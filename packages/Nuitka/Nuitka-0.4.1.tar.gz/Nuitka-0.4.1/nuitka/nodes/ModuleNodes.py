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
""" Module/Package nodes

The top of the tree. Packages are also modules. Modules are what hold a program together
and cross-module optimizations are the most difficult to tackle.
"""

from .NodeBases import (
    ClosureGiverNodeBase,
    ChildrenHavingMixin
)

from .IndicatorMixins import MarkContainsTryExceptIndicator

from nuitka import (
    Variables,
    Utils
)

from nuitka.oset import OrderedSet

class PythonModule( ChildrenHavingMixin, ClosureGiverNodeBase,
                    MarkContainsTryExceptIndicator ):
    """ Module

        The module is the only possible root of a tree. When there are many modules
        they form a forrest.
    """

    kind = "PYTHON_MODULE"

    named_children = ( "body", )

    def __init__( self, name, package, is_main, source_ref ):
        assert type(name) is str, type(name)
        assert "." not in name, name
        assert package is None or ( type( package ) is str and package != "" )

        ClosureGiverNodeBase.__init__(
            self,
            name        = name,
            code_prefix = "module",
            source_ref  = source_ref
        )

        ChildrenHavingMixin.__init__(
            self,
            values = {}
        )

        MarkContainsTryExceptIndicator.__init__( self )

        self.package = package

        # Indicator, if this is the top level module.
        self.is_main = is_main

        self.variables = set()

        # The list functions contained in that module.
        self.functions = OrderedSet()

    def getDetails( self ):
        return {
            "filename" : self.source_ref.getFilename(),
            "package"  : self.package,
            "name"     : self.name
        }

    def asXml( self ):
        # The class is new style, false alarm: pylint: disable=E1002
        result = super( PythonModule, self ).asXml()

        for function_body in self.functions:
            result.append( function_body.asXml() )

        return result

    getBody = ChildrenHavingMixin.childGetter( "body" )
    setBody = ChildrenHavingMixin.childSetter( "body" )

    def isPythonModule( self ):
        return True

    def getParent( self ):
        assert False

    def getParentVariableProvider( self ):
        return None

    def getVariables( self ):
        return self.variables

    def getFilename( self ):
        return self.source_ref.getFilename()

    def getPackage( self ):
        return self.package

    def getFullName( self ):
        if self.package:
            return self.package + "." + self.getName()
        else:
            return self.getName()

    def getVariableForAssignment( self, variable_name ):
        result = self.getProvidedVariable( variable_name )

        return result.makeReference( self )

    def getVariableForReference( self, variable_name ):
        result = self.getProvidedVariable( variable_name )

        return result.makeReference( self )

    def getVariableForClosure( self, variable_name ):
        return self.getProvidedVariable(
            variable_name = variable_name
        )

    def createProvidedVariable( self, variable_name ):
        result = Variables.ModuleVariable(
            module        = self,
            variable_name = variable_name
        )

        assert result not in self.variables
        self.variables.add( result )

        return result

    def isEarlyClosure( self ):
        # Modules should immediately closure variables on use, pylint: disable=R0201
        return True

    def isMainModule( self ):
        return self.is_main

    def getCodeName( self ):
        return "module_" + self.getFullName().replace( ".", "__" ).replace( "-", "_" )

    def addFunction( self, function_body ):
        assert function_body not in self.functions

        self.functions.add( function_body )

    def getFunctions( self ):
        return self.functions


class PythonPackage( PythonModule ):
    kind = "PYTHON_PACKAGE"

    def __init__( self, name, package, source_ref ):
        assert name

        PythonModule.__init__(
            self,
            name       = name,
            package    = package,
            is_main    = False,
            source_ref = source_ref
        )
