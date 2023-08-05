from __future__ import division

import kabuki
import numpy as np
from copy import deepcopy

def _add_noise(params, check_valid_func=None, bounds=None, noise=.1, exclude_params=(), share_noise=()):
    """Add individual noise to each parameter.

        :Arguments:
            params : dict
                Parameters to use for data generation. should look like this
                * {'condition1': {'param1': value, 'param2': value2},
                   'condition2': {'param1': value3, 'param2': value4}}
        :Optional:
            check_valid_func : function <default lambda x: True>
                Function that takes as input the parameters as kwds
                and returns True if param values are admissable.
            bounds : dict <default={}>
                Dict containing parameter names and
                (lower, upper) value for valid parameter
                range.
            noise : float <default=.1>
                Standard deviation of random gaussian
                variable to add to each parameter.
            exclude_params : tuple <default=()>
                Do not add noise to these parameters.
            share_noise : tuple <default=()>
                parameters in share_noise will share the noise across conditions

        :Returns:
            params : dict
                parameters with noise added.

    """

    def normal_rand(mu, sigma):
        if sigma == 0:
            return mu
        else:
            return np.random.normal(loc=mu, scale=sigma)

    def sample_value(param, value):
        if np.isscalar(noise):
            param_noise = noise
        else:
            param_noise = noise.get(param, 0)

        if param in bounds:
            while True:
                sampled_value = normal_rand(value, param_noise)
                if sampled_value >= bounds[param][0] and sampled_value <= bounds[param][1]:
                    return sampled_value
        else:
            return normal_rand(value, param_noise)

    if bounds is None:
        bounds = {}

    if check_valid_func is None:
        check_valid_func = lambda **params: True


    # Sample parameters until accepted
    original_params = deepcopy(params)
    params_noise= deepcopy(params)
    while True:
        params = deepcopy(original_params)

        # sample params only if not excluded and make sure they are shaared across condition if necessary
        for (i_cond, (cond, cond_params)) in enumerate(original_params.iteritems()):
            if i_cond == 0:
                cond0 = cond
            for param, value in cond_params.iteritems():
                if param not in exclude_params:
                    if (i_cond == 0) or (param not in share_noise):
                        new_value = sample_value(param, value)
                        params[cond][param] = new_value
                        params_noise[cond][param] = new_value - value
                    else:
                        params[cond][param] += params_noise[cond0][param]

        # check if params are valid
        valid = True
        for cond_params in params.itervalues():
            valid = check_valid_func(**cond_params)
            if not valid:
                break

        # return params
        if valid:
            return params

def gen_rand_data(Stochastic, params, size=50, subjs=1, subj_noise=.1, exclude_params=(), share_noise=(),
                  column_name='data', check_valid_func=None, bounds=None, seed=None):
    """Generate a random dataset using a user-defined random distribution.

    :Arguments:
        Stochastic : a pymc stochastic class of the target distribution (e.g., pymc.Normal)
        params : dict
            Parameters to use for data generation. Two options possible:
                * {'param1': value, 'param2': value2}
                * {'condition1': {'param1': value, 'param2': value2},
                   'condition2': {'param1': value3, 'param2': value4}}
            In the second case, the dataset is generated with multiple conditions
            named after the key and will be sampled using the corresponding parameters.

    :Optional:
        size : int <default: 50>
            How many values to sample for each condition for each subject.
        subjs : int <default: 1>
            How many subjects to generate data from. Individual subject parameters
            will be normal distributed around the provided parameters with variance
            subj_noise if subjs > 1. If only one subject is simulated no noise is added.
        subj_noise : float or dictionary <default: .1>
            How much to perturb individual subj parameters.
            if float then each parameter will be sampled from a normal distribution with std of subj_noise.
            if dictionary then only parameters that are keys of subj_noise will be sampled, and the std of the sampling
            distribution will be the value associated with them.
        exclude_params : tuple <default ()>
            Do not add noise to these parameters.
        share_noise : tuple <default=()>
            parameters in share_noise will share the noise across conditions
        check_valid_func : function <default lambda x: True>
            Function that takes as input the parameters as kwds
            and returns True if param values are admissable.
        bounds : dict <default={}>
            Dict containing parameter names and
            (lower, upper) value for valid parameter
            range.
        column_name : str <default='data'>
            What to name the data column.

    :Returns:
        data : numpy structured array
            Will contain the columns 'subj_idx', 'condition' and 'data' which contains
            the random samples.
        final_params_set : dict mapping condition to list of individual subject parameters
            Tries to be smart and will return direct values if there is only 1 subject
            and no dict if there is only 1 condition.

    """
    from itertools import product

    # Check if only dict of params was passed, i.e. no conditions
    if not isinstance(params[params.keys()[0]], dict):
        params = {'none': params}


    final_params_set = {}
    for condition in params.iterkeys():
            final_params_set[condition] = []
    dtype = Stochastic('temp', size=2, **(params.values()[0])).dtype
    if seed is not None:
        np.random.seed(seed)

    idx = list(product(range(subjs), params.keys(), range(size)))
    data = np.array(idx, dtype=[('subj_idx', np.int32), ('condition', 'S20'), (column_name, dtype)])





    for subj_idx in range(subjs):
        #if it is a group model add noise to the parameters
        if subjs > 1:
            # Sample subject parameters from a normal around the specified parameters
            subj_params = _add_noise(params, noise=subj_noise, share_noise=share_noise,
                                        check_valid_func=check_valid_func,
                                        bounds=bounds,
                                        exclude_params=exclude_params)
        else:
            subj_params = params.copy()

        #sample for each condition
        for condition, params_cur in subj_params.iteritems():
            final_params_set[condition].append(params_cur)
            samples_from_dist = Stochastic('temp', size=size, **params_cur).value
            idx = (data['subj_idx'] == subj_idx) & (data['condition'] == condition)
            data[column_name][idx] = np.array(samples_from_dist, dtype=dtype)

    # Remove list around final_params_set if there is only 1 subject
    if subjs == 1:
        for key, val in final_params_set.iteritems():
            final_params_set[key] = val[0]

    # Remove dict around final_params_set if there is only 1 condition
    if len(final_params_set) == 1:
        final_params_set = final_params_set[final_params_set.keys()[0]]

    return data, final_params_set

