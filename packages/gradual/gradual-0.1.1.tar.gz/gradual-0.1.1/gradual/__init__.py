"""Gradual Typing module."""

import gradual.runtime_func_check
import gradual.runtime_object_check
import gradual.types

## there are the exposed functions
def typed(typed_thing, to_type=None):
    if type(typed_thing) is gradual.types.ClassType:
        return gradual.runtime_object_check.typed_class(typed_thing,
                                                        to_type)
    if type(typed_thing) is gradual.types.FunctionType:
        return gradual.runtime_func_check.typed_func(typed_thing,
                                                     to_type)
    raise TypeError('@typed decorator can only be applied to '
                    'functions and classes')
func = gradual.runtime_func_check.FuncCast
obj =  gradual.runtime_object_check.ObjectCast

## exposed types
dyn = gradual.types.dyn
void = gradual.types.void
