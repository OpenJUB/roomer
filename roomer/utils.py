import functools
from django.conf import settings

def get_college_code(college_str):
    for college in settings.COLLEGE_CHOICES:
        if college[1] == college_str:
            return college[0]
    return ''


def tail_call(tuple_return=False):
    """
    Decorator for tail calls. Use with @tail_call
    :param tuple_return:
    :return:
    """
    def __wrapper(func):
        def _optimize_partial(*args, **kwargs):
            old_reference = func.func_globals[func.func_name]
            func.func_globals[func.func_name] = functools.partial(functools.partial, func)

            to_execute = functools.partial(func, *args, **kwargs)

            while isinstance(to_execute, functools.partial):
                to_execute = to_execute()

            func.func_globals[func.func_name] = old_reference
            return to_execute

        def _optimize_tuple(*args, **kwargs):
            while args.__class__ is tuple:
                args = func(*args)

            return args

        if tuple_return:
            functools.update_wrapper(_optimize_tuple, func)
            return _optimize_tuple
        else:
            functools.update_wrapper(_optimize_partial, func)
            return _optimize_partial

    return __wrapper
