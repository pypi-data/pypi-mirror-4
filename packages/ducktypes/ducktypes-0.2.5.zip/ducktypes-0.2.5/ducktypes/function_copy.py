import types

def copy_raw_func_only(func):
    """
    copy func without copying func attributes, e.g. __isabstractmethod__,
    nor any annotation.
    """
    new_code = types.CodeType(func.func_code.co_argcount, \
                func.func_code.co_nlocals, \
                func.func_code.co_stacksize, \
                func.func_code.co_flags, \
                func.func_code.co_code, \
                func.func_code.co_consts, \
                func.func_code.co_names, \
                func.func_code.co_varnames, \
                func.func_code.co_filename, \
                func.func_code.co_name, \
                func.func_code.co_firstlineno, \
                func.func_code.co_lnotab)

    return types.FunctionType(new_code, func.func_globals, func.func_name,
                              func.func_defaults, func.func_closure)


def fully_copy_func(func):
    new = copy_raw_func_only(func)

    new.__dict__ = func.__dict__.copy()

    return new



