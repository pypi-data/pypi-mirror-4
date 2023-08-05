import itertools
import logging
import types

logging.basicConfig(level=logging.ERROR)

TYPE = '__type__'


class Type(object):

    def merge(self, other):
        """Merge the self and other types.

        Merge the from (self) and to (other) types to find the maximum
        of the structure of the two types. This means that we find the
        most restrictive type of these two types (Greatest Lower
        Bound) from the 'Threesomes with and without blame'
        paper. This version is without blame tracking.

        The base case returns the 'self' type if the two types are
        equal. If one of the types is dynamic, then it returns the
        other one. If both these cases fail, then it throws a
        TypeError.
        """
        if self == other or other == dyn:
            return self
        elif self == dyn:
            return other
        raise TypeError('Unable to merge: incompatible types %s and %s' %
                        (self, other))


class DynType(Type):

    def __str__(self):
        return '?'

    def typecheck(self, runtime_value):
        """All values are dynamic, so nothing to do here."""
        return runtime_value


class GroundType(Type):

    def __init__(self):
        pass

    def typeCheckError(self, value):
        raise TypeError('Expected %s, got: %r of type %s' %
                        (self, value, type(value).__name__))


class IntType(GroundType):

    def typecheck(self, runtime_value):
        if not isinstance(runtime_value, int):
            self.typeCheckError(runtime_value)
        return runtime_value

    def __str__(self):
        return 'int'


class StrType(GroundType):

    def typecheck(self, runtime_value):
        if not isinstance(runtime_value, str):
            self.typeCheckError(runtime_value)
        return runtime_value

    def __str__(self):
        return 'str'


class BoolType(GroundType):

    def typecheck(self, runtime_value):
        if not isinstance(runtime_value, bool):
            self.typeCheckError(runtime_value)
        return runtime_value

    def __str__(self):
        return 'bool'


class VoidType(GroundType):

    def typecheck(self, runtime_value):
        if not (runtime_value is None):
            self.typeCheckError(runtime_value)
        return runtime_value

    def __str__(self):
        return 'void'


intType = IntType()
strType = StrType()
boolType = BoolType()
dyn = DynType()
void = VoidType()


def getType(runtime_value):
    if isinstance(runtime_value, Type):
        return runtime_value
    if isinstance(runtime_value, RuntimeCast):
        return runtime_value.get_type()
    if hasattr(runtime_value, '__type__'):
        return runtime_value.__type__
    # Special-case the types that are also used in user-code
    if runtime_value == dyn or runtime_value == void:
        return runtime_value
    if runtime_value == int:
        return intType
    if runtime_value == str:
        return strType
    if runtime_value == bool:
        return boolType
    if runtime_value == type(None):  # XXX: use isinstance here
        return void
    raise NotImplementedError('type unknown for: %s' % runtime_value)


class Threesome(Type):

    def __init__(self, midType, fromType=None, toType=None):
        self.midType = midType
        self.fromType = fromType
        self.toType = toType
        if fromType is None and toType is None:
            logging.error('one of fromType and toType should not be None')
        if fromType is None:
            self.fromType = self.midType
        if toType is None:
            self.toType = self.midType

    def merge(self, other):
        """Return a new threesome by merging self with the other type.

        If the other object is a Threesome, we require that the toType
        of the current object and the fromType of the other object be
        the same.

        It is also possible to merge a threesome with other types such
        as ArrowType, ObjectType or dyn. In such case the midType of
        this threesome is merged with the other object.
        """
        if isinstance(other, Threesome):
            assert self.toType == other.fromType
            mergedMidType = self.midType.merge(other.midType)
            return Threesome(mergedMidType, fromType=self.fromType,
                             toType=other.toType)
        else:
            mergedMidType = self.midType.merge(other)
            return Threesome(mergedMidType, fromType=self.fromType,
                             toType=other)

    def typecheck(self, runtime_value):
        return runtime_value

    def __str__(self):
        return '%s == %s ==> %s' % (
            self.fromType, self.midType, self.toType)


class RuntimeCast(object):
    """An interface meant to be implemented by Object and Func Casts."""
    def get_type(self):
        pass


# some definitions needed
def _f():
    pass

FunctionType = type(_f)

class _C:
    def _m(self): pass
ClassType = type(_C)
UnboundMethodType = type(_C._m)
_x = _C()
InstanceType = type(_x)
MethodType = type(_x._m)
del _C, _x, _f
