""" Parameter Guard - Used to verify parameter typing before running the function"""
import functools

def param_guard(func):
    """This decorator guards against invalid parameter typing
        Usage: @param_guard
    """
    notes = func.__annotations__
    if len(notes) == 0 or notes is None:
        raise SyntaxWarning("Cannot use @param_guard on a function with no parameter annotations")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if isinstance(args[0], object):
            args = args[1:]
        type_match = [isinstance(v,c[1]) for c,v in list(zip(notes.items(),args))[:-1]]
        print(list(zip(notes.items(),args)))

        if all(type_match):
            return func(*args, **kwargs)
        raise TypeError("Mismatched types: please review function inputs and documentation")
    return wrapper
