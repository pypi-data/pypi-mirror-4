import gradual.types
import gradual.runtime_func_check
import functools
import logging

class ObjectType(gradual.types.Type):

    def __init__(self, obj_cast_dict):
        self.object_cast = {}
        for key, value in obj_cast_dict.items():
            value = gradual.types.getType(value)
            self.object_cast[key] = value

        self.fields = obj_cast_dict.keys()

    def merge(self, other):
        if isinstance(other, ObjectType):
            logging.info('object merging: %r and %r' % (self, other))
            merged = ObjectType({})

            for my_name, my_type in self.object_cast.items():
                other_type = (other.object_cast.get(my_name)
                              if other.object_cast.get(my_name) else dyn)
                merged.object_cast[my_name] = my_type.merge(other_type)

            for o_name, o_type in other.object_cast.items():
                if not merged.object_cast.get(o_name):
                    merged.object_cast[o_name] = o_type

            merged.fields = merged.object_cast.keys()
            return merged

        return super().merge(other)

    def __str__(self):
        l = []
        for key, value in self.object_cast.items():
            l.append('%s: %s' % (key, value))
        return '{' + ','.join(l) + '}'


class ObjectCast(gradual.types.RuntimeCast):

    def __init__(self, **kwargs):
        self.to_cast = ObjectType(kwargs)

    def check_object(runtime_obj):
        """Check if the runtime_object is consistent with it's type."""
        assert hasattr(runtime_obj, '__type__')
        type_dict = runtime_obj.__type__.midType.object_cast
        for attr, expected_ty in type_dict.items():
            logging.info('checking type: %s (%s)' % (attr, expected_ty))
            if not getattr(runtime_obj, attr):
                raise TypeError('Object %r does not have field %s' %
                                (runtime_obj, attr))
            runtime_value = getattr(runtime_obj, attr)
            if hasattr(runtime_value, '__func__'):
                runtime_value = runtime_value.__func__

            new_value = expected_ty.typecheck(runtime_value)
            if (type(new_value) is gradual.types.FunctionType):
                logging.info('--------- %s %s' % (attr, expected_ty))
                p_fun = functools.partial(new_value, runtime_obj)
                p_fun.__type__ = expected_ty
                p_fun.__type__.code = new_value.__code__
                setattr(runtime_obj, attr, p_fun)

        # Now set the setattr and delattr special methods
        class_obj = runtime_obj
        if not isinstance(runtime_obj, type):
            class_obj = type(runtime_obj)
        setattr(class_obj, '__setattr__', setattribute)
        setattr(class_obj, '__delattr__', delattribute)

    def __call__(self, runtime_obj):
        if not hasattr(runtime_obj, '__type__'):
            runtime_obj.__type__ = gradual.types.Threesome(
                self.to_cast, fromType=gradual.types.dyn)

        # Now merge the and update the threesome
        from_three = runtime_obj.__type__
        logging.info('=====================')
        logging.info('from_three: %s' % from_three)
        to_three = gradual.types.Threesome(self.to_cast,
                                           fromType=from_three.toType)
        merged_three = from_three.merge(to_three)
        logging.info('got back threesome: %s' % merged_three)
        runtime_obj.__type__ = merged_three
        # check if the incoming object matches the casted type.
        ObjectCast.check_object(runtime_obj)
        return runtime_obj

def typed_class(typed_c, unused=None):
    """Get the type of the incoming class and we are consistent."""
    my_type = {}
    for attr, attr_value in typed_c.__dict__.items():
        if (type(attr_value) is gradual.types.FunctionType and
            hasattr(attr_value, '__annotations__')):
            logging.info('Function name: %s %s' % (attr, attr_value))
            arrow_ty = gradual.runtime_func_check.ArrowType(
                attr_value.__annotations__)
            my_type[attr] = gradual.types.Threesome(arrow_ty, arrow_ty)
    my_type = ObjectType(my_type)
    typed_c.__type__ = gradual.types.Threesome(my_type, my_type)
    ObjectCast.check_object(typed_c)
    return typed_c

def delattribute(self, name):
    return object.__detattr__(self, name)

def setattribute(self, name, value):
    if hasattr(self, '__type__'):
        expected_ty = self.__type__.midType.object_cast.get(name)
        logging.info('setattr called for %s with %s' % (name, value))
        if expected_ty:
            expected_ty.typecheck(value)
    return object.__setattr__(self, name, value)
