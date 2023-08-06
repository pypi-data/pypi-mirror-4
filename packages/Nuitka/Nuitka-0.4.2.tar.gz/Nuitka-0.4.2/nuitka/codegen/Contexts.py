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
""" Code generation contexts.

"""

from .Identifiers import (
    Identifier,
    ConstantIdentifier,
    LocalVariableIdentifier,
    ClosureVariableIdentifier,
    SpecialConstantIdentifier
)

from .Namify import namifyConstant

from nuitka.Constants import HashableConstant

from nuitka.__past__ import iterItems

from nuitka.Utils import python_version

from nuitka import Options

# False alarms about "hashlib.md5" due to its strange way of defining what is
# exported, pylint won't understand it. pylint: disable=E1101

import hashlib

if python_version < 300:
    def calcHash( key ):
        hash_value = hashlib.md5(
            "%s%s%d%s%d%s%s" % key
        )

        return hash_value.hexdigest()
else:
    def calcHash( key ):
        hash_value = hashlib.md5(
            ( "%s%s%d%s%d%s%s" % key ).encode( "utf-8" )
        )

        return hash_value.hexdigest()

# Many methods won't use self, but it's the interface. pylint: disable=R0201

class PythonContextBase:
    def __init__( self ):
        self.try_count = 0

        self.try_finally_counts = []

    def allocateTryNumber( self ):
        self.try_count += 1

        return self.try_count

    def hasLocalsDict( self ):
        return False

    def setTryFinallyCount( self, value ):
        self.try_finally_counts.append( value )

    def removeFinallyCount( self ):
        del self.try_finally_counts[-1]

    def getTryFinallyCount( self ):
        if self.try_finally_counts:
            return self.try_finally_counts[-1]
        else:
            return None


class PythonChildContextBase( PythonContextBase ):
    def __init__( self, parent ):
        PythonContextBase.__init__( self )

        self.parent = parent

    def addEvalOrderUse( self, value ):
        self.parent.addEvalOrderUse( value )

    def addMakeTupleUse( self, value ):
        self.parent.addMakeTupleUse( value )

    def addMakeListUse( self, value ):
        self.parent.addMakeListUse( value )

    def addMakeDictUse( self, value ):
        self.parent.addMakeDictUse( value )

    def getParent( self ):
        return self.parent

    def getConstantHandle( self, constant ):
        return self.parent.getConstantHandle( constant )

    def addFunctionCodes( self, code_name, function_decl, function_code ):
        self.parent.addFunctionCodes( code_name, function_decl, function_code )

    def addGlobalVariableNameUsage( self, var_name ):
        self.parent.addGlobalVariableNameUsage( var_name )

    def addExportDeclarations( self, declarations ):
        self.parent.addExportDeclarations( declarations )

    def getModuleCodeName( self ):
        return self.parent.getModuleCodeName()

    def getModuleName( self ):
        return self.parent.getModuleName()

    def getCodeObjectHandle( self, filename, code_name, line_number, arg_names, kw_only_count,
                             is_generator, is_optimized ):
        return self.parent.getCodeObjectHandle(
            filename      = filename,
            code_name     = code_name,
            line_number   = line_number,
            arg_names     = arg_names,
            kw_only_count = kw_only_count,
            is_generator  = is_generator,
            is_optimized  = is_optimized
        )


class PythonGlobalContext:
    def __init__( self ):
        self.constants = {}
        self.contained_constants = {}

        # Basic values that the code uses all the times.
        self.getConstantHandle( () )
        self.getConstantHandle( {} )
        self.getConstantHandle( "" )
        self.getConstantHandle( True )
        self.getConstantHandle( False )
        self.getConstantHandle( 0 )
        # For Python3 empty bytes, no effect for Python2, same as ""
        self.getConstantHandle( b"" )

        # Python mechanics.
        self.getConstantHandle( "__module__" )
        self.getConstantHandle( "__class__" )
        self.getConstantHandle( "__name__" )
        self.getConstantHandle( "__metaclass__" )
        self.getConstantHandle( "__dict__" )
        self.getConstantHandle( "__doc__" )
        self.getConstantHandle( "__file__" )
        self.getConstantHandle( "__enter__" )
        self.getConstantHandle( "__exit__" )
        self.getConstantHandle( "__builtins__" )
        self.getConstantHandle( "__all__" )

        # For Python3 modules
        if python_version >= 300:
            self.getConstantHandle( "__cached__" )

        if python_version >= 330:
            self.getConstantHandle( "__loader__" )

        # For patching Python2 internal class type
        if python_version < 300:
            self.getConstantHandle( "__getattr__" )
            self.getConstantHandle( "__setattr__" )
            self.getConstantHandle( "__delattr__" )

        # Patched module name.
        self.getConstantHandle( "inspect" )

        # Names of builtins used in helper code.
        self.getConstantHandle( "compile" )
        self.getConstantHandle( "range" )
        self.getConstantHandle( "open" )
        self.getConstantHandle( "print" )
        self.getConstantHandle( "__import__" )

        # Names of builtins replace, maybe used by helpers
        if Options.isDebug and not Options.shallMakeModule():
            self.getConstantHandle( "type" )
            self.getConstantHandle( "len" )
            self.getConstantHandle( "range" )
            self.getConstantHandle( "repr" )
            self.getConstantHandle( "int" )
            self.getConstantHandle( "iter" )
            self.getConstantHandle( "long" )

        # The print builtin needs some argument names.
        self.getConstantHandle( "end" )
        self.getConstantHandle( "file" )

        # COMPILE_CODE uses read/strip method lookups.
        self.getConstantHandle( "read" )
        self.getConstantHandle( "strip" )

        # Executables only
        self.getConstantHandle( "__main__" )

        # sys exception attributes
        self.getConstantHandle( "exc_type" )
        self.getConstantHandle( "exc_value" )
        self.getConstantHandle( "exc_traceback" )

        # Have EVAL_ORDER for 1..6 in any case, so we can use it in the C++ code freely
        # without concern.
        self.make_tuples_used = set( range( 1, 6 ) )
        self.make_lists_used = set( range( 0, 1 ) )
        self.make_dicts_used = set( range( 0, 3 ) )

        # Include 0, so list and tuple making can use it without being special.
        self.eval_orders_used = set( range( 0, 6 ) )

        # Code objects needed.
        self.code_objects = {}

    def getConstantHandle( self, constant ):
        if constant is None:
            return SpecialConstantIdentifier( None )
        elif constant is True:
            return SpecialConstantIdentifier( True )
        elif constant is False:
            return SpecialConstantIdentifier( False )
        elif constant is Ellipsis:
            return SpecialConstantIdentifier( Ellipsis )
        else:
            key = ( type( constant ), HashableConstant( constant ) )

            if key not in self.constants:
                self.constants[ key ] = "_python_" + namifyConstant( constant )

            return ConstantIdentifier( self.constants[ key ], constant )

    def getConstantCodeName( self, constant ):
        if constant is None:
            return SpecialConstantIdentifier( None ).getCode()
        elif constant is True:
            return SpecialConstantIdentifier( True ).getCode()
        elif constant is False:
            return SpecialConstantIdentifier( False ).getCode()
        elif constant is Ellipsis:
            return SpecialConstantIdentifier( Ellipsis ).getCode()
        else:
            return "_python_" + namifyConstant( constant )


    def getConstants( self ):
        return self.constants

    def setContainedConstants( self, contained_constants ):
        self.contained_constants = contained_constants

    def getContainedConstants( self ):
        return self.contained_constants

    def getCodeObjectHandle( self, filename, code_name, line_number, arg_names, kw_only_count,
                             is_generator, is_optimized ):
        key = ( filename, code_name, line_number, arg_names, kw_only_count, is_generator, is_optimized )

        if key not in self.code_objects:
            self.code_objects[ key ] = Identifier(
                "_codeobj_%s" % calcHash( key ),
                0
            )

            self.getConstantHandle( filename )
            self.getConstantHandle( code_name )
            self.getConstantHandle( arg_names )

        return self.code_objects[ key ]

    def getCodeObjects( self ):
        return sorted( iterItems( self.code_objects ) )

    def addEvalOrderUse( self, value ):
        assert type( value ) is int

        self.eval_orders_used.add( value )

    def getEvalOrdersUsed( self ):
        return sorted( self.eval_orders_used )

    def addMakeTupleUse( self, value ):
        assert type( value ) is int

        self.addEvalOrderUse( value ) # generated code uses it
        self.make_tuples_used.add( value )

    def addMakeListUse( self, value ):
        assert type( value ) is int

        self.addEvalOrderUse( value ) # generated code uses it
        self.make_lists_used.add( value )

    def addMakeDictUse( self, value ):
        assert type( value ) is int

        self.addEvalOrderUse( value * 2 ) # generated code uses it
        self.make_dicts_used.add( value )

    def getMakeTuplesUsed( self ):
        return sorted( self.make_tuples_used )

    def getMakeListsUsed( self ):
        return sorted( self.make_lists_used )

    def getMakeDictsUsed( self ):
        return sorted( self.make_dicts_used )


class PythonModuleContext( PythonContextBase ):
    # Plent of attributes, because it's storing so many different things.
    # pylint: disable=R0902

    def __init__( self, module_name, code_name, filename, global_context ):
        PythonContextBase.__init__( self )

        self.name = module_name
        self.code_name = code_name
        self.filename = filename

        self.global_context = global_context

        self.function_codes = {}

        self.global_var_names = set()

        self.temp_keepers = {}

        self.export_declarations = []

    def __repr__( self ):
        return "<PythonModuleContext instance for module %s>" % self.filename

    def getFrameHandle( self ):
        return Identifier( "frame_guard.getFrame()", 1 )

    def getFrameGuardClass( self ):
        return "FrameGuard"

    def getParent( self ):
        return None

    def getConstantHandle( self, constant ):
        return self.global_context.getConstantHandle( constant )

    def getCodeObjectHandle( self, filename, code_name, line_number, arg_names, kw_only_count,
                             is_generator, is_optimized ):
        return self.global_context.getCodeObjectHandle(
            filename      = filename,
            code_name     = code_name,
            line_number   = line_number,
            arg_names     = arg_names,
            kw_only_count = kw_only_count,
            is_generator  = is_generator,
            is_optimized  = is_optimized
        )

    def addFunctionCodes( self, code_name, function_decl, function_code ):
        assert code_name not in self.function_codes, code_name

        self.function_codes[ code_name ] = ( function_decl, function_code )

    def getFunctionsCodes( self ):
        return self.function_codes

    def getName( self ):
        return self.name

    getModuleName = getName

    def getModuleCodeName( self ):
        return self.code_name

    # There cannot ne local variable in modules no need to consider the name.
    # pylint: disable=W0613
    def hasLocalVariable( self, var_name ):
        return False

    def hasClosureVariable( self, var_name ):
        return False
    # pylint: enable=W0613

    def addGlobalVariableNameUsage( self, var_name ):
        self.global_var_names.add( var_name )

    def getGlobalVariableNames( self ):
        return sorted( self.global_var_names )

    def addEvalOrderUse( self, value ):
        self.global_context.addEvalOrderUse( value )

    def addMakeTupleUse( self, value ):
        self.global_context.addMakeTupleUse( value )

    def addMakeListUse( self, value ):
        self.global_context.addMakeListUse( value )

    def addMakeDictUse( self, value ):
        self.global_context.addMakeDictUse( value )

    def addExportDeclarations( self, declarations ):
        self.export_declarations.append( declarations )

    def addTempKeeperUsage( self, variable_name, ref_count ):
        self.temp_keepers[ variable_name ] = ref_count

    def getTempKeeperRefCount( self, variable_name ):
        return self.temp_keepers[ variable_name ]

    def getTempKeeperUsages( self ):
        return self.temp_keepers

    def getExportDeclarations( self ):
        return "\n".join( self.export_declarations )

    def setFrameGuardMode( self, guard_mode ):
        assert guard_mode == "once"

    def getReturnCode( self ):
        return "return MOD_RETURN_VALUE( _module_%s );" % self.getModuleCodeName()


class PythonFunctionContext( PythonChildContextBase ):
    def __init__( self, parent, function ):
        PythonChildContextBase.__init__( self, parent = parent )

        self.function = function

        self.needs_creation = function.needsCreation()

        # Make sure the local names are available as constants
        for local_name in function.getLocalVariableNames():
            self.getConstantHandle( constant = local_name )

        self.temp_keepers = {}

        self.guard_mode = None

    def __repr__( self ):
        return "<PythonFunctionContext for %s '%s'>" % (
            "function" if not self.function.isClassDictCreation() else "class",
            self.function.getName()
        )

    def hasLocalsDict( self ):
        return self.function.hasLocalsDict()

    def hasLocalVariable( self, var_name ):
        return var_name in self.function.getLocalVariableNames()

    def hasClosureVariable( self, var_name ):
        return var_name in self.function.getClosureVariableNames()

    def getFrameHandle( self ):
        if self.function.isGenerator():
            return Identifier( "generator->m_frame", 0 )
        else:
            return Identifier( "frame_guard.getFrame()", 1 )

    def getFrameGuardMode( self ):
        return self.guard_mode

    def setFrameGuardMode( self, guard_mode ):
        self.guard_mode = guard_mode

    def getFrameGuardClass( self ):
        if self.guard_mode == "generator":
            return "FrameGuardLight"
        elif self.guard_mode == "full":
            return "FrameGuard"
        elif self.guard_mode == "pass_through":
            return "FrameGuardVeryLight"
        else:
            assert False, (self, self.guard_mode)

    def getLocalHandle( self, var_name ):
        return LocalVariableIdentifier( var_name, from_context = self.function.isGenerator() )

    def getClosureHandle( self, var_name ):
        if self.needs_creation:
            if self.function.isGenerator():
                return ClosureVariableIdentifier( var_name, from_context = "_python_context->common_context->" )
            else:
                return ClosureVariableIdentifier( var_name, from_context = "_python_context->" )
        else:
            if self.function.isGenerator():
                return ClosureVariableIdentifier( var_name, from_context = "_python_context->" )
            else:
                return ClosureVariableIdentifier( var_name, from_context = "" )

    def addTempKeeperUsage( self, variable_name, ref_count ):
        self.temp_keepers[ variable_name ] = ref_count

    def getTempKeeperRefCount( self, variable_name ):
        return self.temp_keepers[ variable_name ]

    def getTempKeeperUsages( self ):
        return self.temp_keepers


class PythonFunctionDirectContext( PythonFunctionContext ):
    def isForDirectCall( self ):
        return True

    def getExportScope( self ):
        return "NUITKA_CROSS_MODULE" if self.function.isCrossModuleUsed() else "NUITKA_LOCAL_MODULE"

    def isForCrossModuleUsage( self ):
        return self.function.isCrossModuleUsed()

    def isForCreatedFunction( self ):
        return False


class PythonFunctionCreatedContext( PythonFunctionContext ):
    def isForDirectCall( self ):
        return False

    def isForCreatedFunction( self ):
        return True
