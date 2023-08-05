"""Runtime type checking for functions."""

import gradual.types
import functools
import logging

RETURNS = ['return_', 'return']


class ArrowType(gradual.types.Type):
    """Represents a function type.

    Important fields:
      retType: return type of the function.
      paramNames: a list containing the names of the parameters
      paramTypes: a list containing the type of each of the parameter.
          It is essential that the size of the lists paramNames and
          paramTypes are equal.

    TODO(shashank): Add support for varargs, kwargs and optional args
    """

    def __init__(self, types_dict):
        self.retType = gradual.types.dyn
        for ret in RETURNS:
            if types_dict.get(ret):
                self.retType = gradual.types.getType(types_dict.get(ret))
        self.paramNames = []
        self.paramTypes = []
        self.params = {}
        for key, type_ in types_dict.items():
            if key in RETURNS:
                continue
            self.paramNames.append(key)
            self.paramTypes.append(gradual.types.getType(type_))
            self.params[key] = gradual.types.getType(type_)
        assert len(self.paramNames) == len(self.paramTypes)

    def merge(self, other):
        if isinstance(other, ArrowType):
            logging.info('merging: %s and %s' % (self, other))
            merged = ArrowType({})
            merged.retType = self.retType.merge(other.retType)
            for my_name, my_type in self.params.items():
                other_type = (other.params.get(my_name)
                              if other.params.get(my_name) else
                              gradual.types.dyn)
                merged.params[my_name] = my_type.merge(other_type)

            for o_name, o_type in other.params.items():
                if not merged.params.get(o_name):
                    merged.params[o_name] = o_type

            merged.paramNames = merged.params.keys()
            merged.paramTypes = merged.params.values()

            return merged
        return super().merge(other)

    def __str__(self):
        l = []
        for name, type_ in zip(self.paramNames, self.paramTypes):
            if name in RETURNS:
                continue
            l.append('%s: %s' % (name, type_))

        return '(' + ', '.join(l) + ') -> ' + str(self.retType)

    def typecheck(self, runtime_value):
        """Check if we can merge the threesome and self."""
        make_sure_func_has_type(runtime_value)
        logging.info('%s has type %s' % (runtime_value,
                                         runtime_value.__type__))
        return cast_func_to_new_type(runtime_value, self)


dynArrow = ArrowType({})


class FuncCast(gradual.types.RuntimeCast):
    """A class representing the runtime cast object.

    When a new object is created, the user passes in the cast
    parameters.  The newly created object is callable, and is called
    with the actual function being casted.

    Here is an example of a function h being cast to g:
        g = FuncCast(int, str, key=FuncCast(int), return_=void)(h)
    """

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.to_arrow = ArrowType(self.kwargs)

    def __call__(self, fun):
        logging.info('input type: %s' % fun)
        if not hasattr(fun, '__type__'):
            fun.__type__ = gradual.types.Threesome(
                dynArrow, fromType=dynArrow)
            fun.__type__.code = fun.__code__

        from_ = fun.__type__

        # Add the positional parameters into the type dictionary
        for varname, arg_type in zip(from_.code.co_varnames, self.args):
            logging.info('adding %s of type %s' % (varname, arg_type))
            self.kwargs[varname] = arg_type

        self.to_arrow = ArrowType(self.kwargs)

        # TODO: merge the prev and kwargs, 'return' contains the
        # return type.

        logging.info('=====from: %s' % from_)
        to_ = gradual.types.Threesome(self.to_arrow,
                                      fromType=from_.toType)
        return cast_func_to_new_type(fun, to_)

    def get_type(self):
        """Return the ArrowType corresponding to this cast."""
        return self.to_arrow

def cast_func_to_new_type(func, to_type):
    from_ = func.__type__
    merged_type = from_.merge(to_type)
    newfun = functools.partial(func)
    newfun.__type__ = merged_type
    newfun.__type__.code = from_.code

    logging.info('%s: has type: %s' % (newfun, newfun.__type__))
    return typed_func(newfun)


def make_sure_func_has_type(func):
    if not hasattr(func, '__type__'):
        midType = ArrowType(func.__annotations__)
        func.__type__ = gradual.types.Threesome(
            midType, fromType=dynArrow)
        func.__type__.code = func.__code__


def typed_func(typed_func, to_type=None):
    make_sure_func_has_type(typed_func)

    @functools.wraps(typed_func)
    def wrapper(*args, **kwds):
        logging.info('calling decorated fun: %s kw: %s, function: %s' %
                     (args, kwds, typed_func.__type__))
        # TODO: handle kwargs
        argcount = typed_func.__type__.code.co_argcount
        assert len(args) == argcount, (
            'number of arguments passed %s is different from the number of '
            'arguments expected: %s' % (len(args), argcount))
        ftype = typed_func.__type__.midType

        new_args = []

        for i, arg in enumerate(args):
            param_name = typed_func.__type__.code.co_varnames[i]
            param_type = ftype.params.get(param_name)
            if param_type:
                arg = param_type.typecheck(arg)

            new_args.append(arg)

        ret = typed_func(*new_args, **kwds)
        ftype.retType.typecheck(ret)
        return ret

    return wrapper
