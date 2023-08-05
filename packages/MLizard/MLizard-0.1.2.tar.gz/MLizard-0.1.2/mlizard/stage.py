#!/usr/bin/python
# coding=utf-8
# This file is part of the MLizard library published under the GPL3 license.
# Copyright (C) 2012  Klaus Greff
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import division, print_function, unicode_literals
import numpy as np
import inspect
import time
from log import StageFunctionLoggerFacade, ResultLogHandler
from report import Report

class StageFunction(object):
    def __init__(self, name, f, cache, options, message_logger, results_logger,
                 seed):
        self.function = f
        self.message_logger = message_logger
        self.results_logger = results_logger
        self.random = np.random.RandomState(seed)
        self.cache = cache
        self.options = options
        # preserve meta_information
        self.__name__ = name
        self.func_name = name
        self.__doc__ = f.__doc__
        # extract extra info
        self.source = str(inspect.getsource(f))
        self.signature = get_signature(f)
        if self.signature['varargs_name'] :
            raise TypeError("*args not supported by StageFunction")
        if self.signature['kw_wildcard_name'] :
            raise TypeError("**kwargs not supported by StageFunction")
        # some configuration
        self.caching_threshold = 2 # seconds
        self.do_cache_results = True
        # internal state
        self.execution_times = []

    def add_random_arg_to(self, arguments):
        if 'rnd' in self.signature['args']  and 'rnd' not in arguments:
            arguments['rnd'] = self.random

    def add_logger_arg_to(self, arguments):
        l = StageFunctionLoggerFacade(self.message_logger, self.results_logger)
        if 'logger' in self.signature['args']:
            arguments['logger'] = l
        return l

    def execute_function(self, args, kwargs, options):
        # Modify Arguments
        assert_no_unexpected_kwargs(self.signature, kwargs)
        assert_no_duplicate_args(self.signature, args, kwargs)
        arguments = apply_options(self.signature, args, kwargs, options)
        self.message_logger.debug("Called with %s", arguments)
        self.add_random_arg_to(arguments)
        # use arguments without logger as cache-key
        key = (self.source, dict(arguments))
        log_facade = self.add_logger_arg_to(arguments)
        assert_no_missing_args(self.signature, arguments)
        # do we want to cache?
        if self.cache and self.do_cache_results:
            # Check for cached version
            try:
                result, result_logs = self.cache[key]
                log_facade.set_result(**result_logs)
                self.message_logger.info("Retrieved results from cache. "
                                         "Skipping Execution")
                return result
            except KeyError:
                pass

        #### Run the function ####
        local_results_handler = ResultLogHandler()
        self.results_logger.addHandler(local_results_handler)
        start_time = time.time()
        result = self.function(**arguments) #<<=====
        self.execution_times.append(time.time() - start_time)
        self.message_logger.info("Completed in %2.2f sec",
                                 self.execution_times[-1])
        result_logs = local_results_handler.results
        self.results_logger.removeHandler(local_results_handler)
        ##########################

        if self.cache and \
           self.do_cache_results and \
           self.execution_times[-1] > self.caching_threshold:
            self.message_logger.info("Execution took more than %2.2f sec so we "
                                     "cache the result."%self.caching_threshold)
            self.cache[key] = result, result_logs
        return result

    def __call__(self, *args, **kwargs):
        return self.execute_function(args, kwargs, self.options)

    def __hash__(self):
        return hash(self.source)


class StageFunctionOptionsView(object):
    def __init__(self, stage_func, options):
        self.options = options
        self.func = stage_func

    def __call__(self, *args, **kwargs):
        return self.func.execute_function(args, kwargs, self.options)


def get_signature(f):
    args, varargs_name, kw_wildcard_name, defaults = inspect.getargspec(f)
    defaults = defaults or []
    pos_args = args[:len(args)-len(defaults)]
    kwargs = dict(zip(args[-len(defaults):], defaults))
    return {'name' : f.func_name,
            'args' : args,
            'positional' : pos_args,
            'kwargs' : kwargs,
            'varargs_name' : varargs_name,
            'kw_wildcard_name' : kw_wildcard_name}

def assert_no_missing_args(signature, arguments):
    # check if after all some arguments are still missing
    missing_arguments = [v for v in signature['args'] if v not in arguments]
    if missing_arguments :
        raise TypeError("{}() is missing value(s) for {}".format(
            signature['name'], missing_arguments))

def assert_no_unexpected_kwargs(signature, kwargs):
    # check for erroneous kwargs
    wrong_kwargs = [v for v in kwargs if v not in signature['args']]
    if wrong_kwargs :
        raise TypeError("{}() got unexpected keyword argument(s): {}".format(
            signature['name'], wrong_kwargs))

def assert_no_duplicate_args(signature, args, kwargs):
    #check for multiple explicit arguments
    positional_arguments = signature['positional'][:len(args)]
    duplicate_arguments = [v for v in positional_arguments if v in kwargs]
    if duplicate_arguments :
        raise TypeError("{}() got multiple values for argument(s) {}".format(
            signature['name'], duplicate_arguments))

def apply_options(signature, args, kwargs, options):
    """
    For a given function f and the *args and **kwargs it was called with,
    construct a new dictionary of arguments such that:
      - the original explicit call arguments are preserved
      - missing arguments are filled in by name using options (if possible)
      - default arguments are overridden by options
      - sensible errors are thrown if:
        * you pass an unexpected keyword argument
        * you provide multiple values for an argument
        * after all the filling an argument is still missing
    """
    arguments = dict()
    arguments.update(signature['kwargs']) # weakest: default arguments:
    arguments.update((v, options[v]) for v in signature['args'] if v in options)
    arguments.update(kwargs) # keyword arguments
    if len(args) > len(signature['args']):
        raise TypeError("{}() takes at most {} arguments ({} given)".format(
                        signature['name'], len(signature['args']), len(args)))
    positional_arguments = dict(zip(signature['args'], args))
    arguments.update(positional_arguments) # strongest: positional arguments
    return arguments