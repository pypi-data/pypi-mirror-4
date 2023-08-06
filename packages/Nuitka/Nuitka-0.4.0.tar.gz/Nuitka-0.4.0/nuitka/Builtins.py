#     Copyright 2013, Kay Hayen, mailto:kay.hayen@gmail.com
#
#     Part of "Nuitka", an optimizing Python compiler that is compatible and
#     integrates with CPython, but also works on its own.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
""" Builtins module. Information about builtins of the currently running Python.

"""

from types import BuiltinFunctionType, FunctionType, GeneratorType

from nuitka import Utils

import sys

def isExceptionName( builtin_name ):
    if builtin_name.endswith( "Error" ) or builtin_name.endswith( "Exception" ):
        return True
    elif builtin_name in ( "StopIteration", "GeneratorExit", "SystemExit", "NotImplemented", "KeyboardInterrupt" ):
        return True
    else:
        return False

# Hide Python3 changes for builtin exception names
try:
    import exceptions

    builtin_exception_names = [
        str( name ) for name in dir( exceptions )
        if isExceptionName( name )
    ]

    builtin_exception_values = {}

    for key in builtin_exception_names:
        builtin_exception_values[ key ] = getattr( exceptions, key )

    for key in dir( sys.modules[ "__builtin__" ] ):
        name = str( key )

        if isExceptionName( name ):
            builtin_exception_names.append( key )
            builtin_exception_values[ name ] = getattr( sys.modules[ "__builtin__" ], key )

    del name, key # Remove names uses in branch, pylint: disable=W0631

except ImportError:
    exceptions = {}

    for x in dir( sys.modules[ "builtins" ] ):
        name = str( x )

        if isExceptionName( name ):
            exceptions[ name ] = x

    builtin_exception_names = [
        key for key, value in exceptions.items()
    ]

    builtin_exception_values = {}

    for key, value in exceptions.items():
        builtin_exception_values[ key ] = value

    del name, key, value, x # Remove names uses in branch, pylint: disable=W0631

assert "ValueError" in builtin_exception_names
assert "StopIteration" in builtin_exception_names
assert "GeneratorExit" in builtin_exception_names
assert "AssertionError" in builtin_exception_names
assert "BaseException" in builtin_exception_names
assert "Exception" in builtin_exception_names
assert "NotImplemented" in builtin_exception_names

builtin_names = [
    str( x )
    for x in __builtins__.keys()
]

for builtin_exception_name in builtin_exception_names:
    if builtin_exception_name in builtin_names:
        builtin_names.remove( builtin_exception_name )

builtin_names.remove( "__doc__" )
builtin_names.remove( "__name__" )
builtin_names.remove( "__package__" )

builtin_warnings = []

for builtin_name in builtin_names:
    if builtin_name.endswith( "Warning" ):
        builtin_warnings.append( builtin_name )


for builtin_name in builtin_warnings:
    builtin_names.remove( builtin_name )

assert "__import__" in builtin_names
assert "int" in builtin_names

assert "__doc__" not in builtin_names
assert "sys" not in builtin_names

builtin_all_names = builtin_names + builtin_exception_names + builtin_warnings

# For PyLint to be happy.
assert exceptions

builtin_anon_names = {
    "NoneType"                   : type( None ), # Strangely not Python3 types module
    "ellipsis"                   : type( Ellipsis ), # see above
    "NotImplementedType"         : type( NotImplemented ),
    "function"                   : FunctionType,
    "builtin_function_or_method" : BuiltinFunctionType,
    "compiled_function"          : BuiltinFunctionType, # Can't really have it any better way.
    "generator"                  : GeneratorType,
    "compiled_generator"         : GeneratorType, # Can't really have it any better way.
}

builtin_anon_codes = {
    "NoneType"                   : "Py_TYPE( Py_None )",
    "ellipsis"                   : "&PyEllipsis_Type",
    "NotImplementedType"         : "Py_TYPE( Py_NotImplemented )",
    "function"                   : "&PyFunction_Type",
    "builtin_function_or_method" : "&PyCFunction_Type",
    "compiled_function"          : "&Nuitka_Function_Type",
    "compiled_generator"         : "&Nuitka_Generator_Type",
}

if Utils.python_version < 300:
    class Temp:
        def method( self ):
            pass

    builtin_anon_names[ "classobj" ] = type( Temp )
    builtin_anon_codes[ "classobj" ] = "&PyClass_Type"

    builtin_anon_names[ "instance" ] = type( Temp() )
    builtin_anon_codes[ "instance" ] = "&PyInstance_Type"

    builtin_anon_names[ "instancemethod" ] = type( Temp().method )
    builtin_anon_codes[ "instancemethod" ] = "&PyMethod_Type"

    del Temp
