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
""" Code generation for tuples.

Right now only the creation is done here. But more should be added later on.
"""

from .Identifiers import getCodeTemporaryRefs, CallIdentifier, ConstantIdentifier

def getTupleCreationCode( context, element_identifiers ):
    if len( element_identifiers ) == 0:
        return ConstantIdentifier( "_python_tuple_empty", () )

    arg_codes = getCodeTemporaryRefs( element_identifiers )
    args_length = len( element_identifiers )

    context.addMakeTupleUse( args_length )

    return CallIdentifier(
        called  = "MAKE_TUPLE%d" % args_length,
        args    = arg_codes
    )
