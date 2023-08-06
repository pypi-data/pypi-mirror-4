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
""" This module is providing helper functions for complex call re-formulations.

One for each type of call. """

from .FunctionNodes import (
    CPythonExpressionFunctionBody,
    CPythonExpressionFunctionCreation,
    CPythonExpressionFunctionCall,
    CPythonExpressionFunctionRef
)
from .StatementNodes import (
    CPythonStatementsSequence,
    CPythonStatementsFrame
)
from .LoopNodes import (
    CPythonStatementLoop,
    CPythonStatementBreakLoop
)
from .TypeNode import (
    CPythonExpressionBuiltinIsinstance,
    CPythonExpressionBuiltinType1
)
from .BuiltinReferenceNodes import (
    CPythonExpressionBuiltinRef,
    CPythonExpressionBuiltinExceptionRef,
    CPythonExpressionBuiltinAnonymousRef
)
from .ConditionalNodes import CPythonStatementConditional
from .ComparisonNode import CPythonExpressionComparison
from .VariableRefNode import (
    CPythonExpressionVariableRef,
    CPythonExpressionTargetVariableRef,
    CPythonStatementTempBlock,
    CPythonExpressionTempVariableRef
)
from .CallNode import (
    CPythonExpressionCallKeywordsOnly,
    CPythonExpressionCallNoKeywords,
    CPythonExpressionCallEmpty,
    CPythonExpressionCall
)
from .ReturnNode import CPythonStatementReturn
from .TryNodes import (
    CPythonStatementTryExcept,
    CPythonStatementExceptHandler
)
from .AssignNodes import (
    CPythonStatementAssignmentVariable,
    CPythonStatementAssignmentSubscript
)
from .ExceptionNodes import (
    CPythonStatementRaiseException,
    CPythonExpressionBuiltinMakeException
)
from .ConstantRefNode import CPythonExpressionConstantRef
from .AttributeNodes import CPythonExpressionAttributeLookup
from .ContainerMakingNodes import CPythonExpressionMakeTuple
from .BuiltinTypeNodes import CPythonExpressionBuiltinTuple
from .OperatorNodes import (
    CPythonExpressionOperationBinary,
    CPythonExpressionOperationNOT
)
from .BuiltinIteratorNodes import (
    CPythonExpressionBuiltinIter1,
    CPythonExpressionBuiltinNext1
)
from .SubscriptNode import CPythonExpressionSubscriptLookup
from .BuiltinDictNode import CPythonExpressionBuiltinDict

from .ParameterSpec import ParameterSpec

from ..SourceCodeReferences import fromFilename
from .FutureSpec import FutureSpec

source_ref = fromFilename( "internal", FutureSpec() ).atInternal()

from nuitka.Utils import python_version

# Special decorator, we can cache although provider may change.
def once_decorator( func ):
    func.cached_value = None

    def replacement( provider ):
        if func.cached_value is None:
            func.cached_value = func( provider )

        return func.cached_value

    return replacement

@once_decorator
def getCallableNameDescBody( provider ):
    helper_name = "get_callable_name_desc"

    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    # Equivalent of:
    #
    # Note: The "called_type" is a temporary variable.
    #
    # called_type = type( BuiltinFunctionType )
    #
    # if ininstance( called, ( FunctionType, MethodType, BuiltinFunctionType ) ):
    #     return called.__name__
    # elif python_version < 3 and isinstance( called, ClassType ):
    #     return called_type.__name__ + " constructor"
    # elif python_version < 3 and isinstance( called, InstanceType ):
    #     return called_type.__name__ + " instance"
    # else:
    #     return called_type.__name__ + " object"

    called_variable, = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeNameAttributeLookup( node, attribute_name = "__name__" ):
        return CPythonExpressionAttributeLookup(
            expression     = node,
            attribute_name = attribute_name,
            source_ref     = source_ref
        )

    temp_block = CPythonStatementTempBlock(
        source_ref = source_ref
    )

    functions_case = CPythonStatementsSequence(
        statements = (
            CPythonStatementReturn(
                expression = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    right      = CPythonExpressionConstantRef(
                        constant = "()",
                        source_ref = source_ref
                    ),
                    left       = makeNameAttributeLookup(
                        makeCalledVariableRef()
                    ),
                    source_ref = source_ref

                ),
                source_ref = source_ref
            ),
        ),
        source_ref = source_ref
    )

    no_branch = CPythonStatementsSequence(
        statements = (
            CPythonStatementReturn(
                expression = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    right      = CPythonExpressionConstantRef(
                        constant = " object",
                        source_ref = source_ref
                    ),
                    left       = makeNameAttributeLookup(
                        CPythonExpressionBuiltinType1(
                            value      = makeCalledVariableRef(),
                            source_ref = source_ref
                        )
                    ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
        ),
        source_ref = source_ref
    )

    if python_version < 300:
        instance_case = CPythonStatementsSequence(
            statements = (
                CPythonStatementReturn(
                    expression = CPythonExpressionOperationBinary(
                        operator   = "Add",
                        right      = CPythonExpressionConstantRef(
                            constant = " instance",
                            source_ref = source_ref
                        ),
                        left       = makeNameAttributeLookup(
                            makeNameAttributeLookup(
                                makeCalledVariableRef(),
                                attribute_name = "__class__",
                            )
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        )

        no_branch = CPythonStatementsSequence(
            statements = (
                CPythonStatementConditional(
                    condition  = CPythonExpressionBuiltinIsinstance(
                        instance   = makeCalledVariableRef(),
                        cls        = CPythonExpressionBuiltinAnonymousRef(
                            builtin_name = "instance",
                            source_ref   = source_ref
                        ),
                        source_ref = source_ref
                    ),
                    yes_branch = instance_case,
                    no_branch  = no_branch,
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        )

        class_case = CPythonStatementsSequence(
            statements = (
                CPythonStatementReturn(
                    expression = CPythonExpressionOperationBinary(
                        operator   = "Add",
                        right      = CPythonExpressionConstantRef(
                            constant = " constructor",
                            source_ref = source_ref
                        ),
                        left       = makeNameAttributeLookup(
                            makeCalledVariableRef(),
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        )

        no_branch = CPythonStatementsSequence(
            statements = (
                CPythonStatementConditional(
                    condition  = CPythonExpressionBuiltinIsinstance(
                        instance   = makeCalledVariableRef(),
                        cls        = CPythonExpressionBuiltinAnonymousRef(
                            builtin_name = "classobj",
                            source_ref   = source_ref
                        ),
                        source_ref = source_ref
                    ),
                    yes_branch = class_case,
                    no_branch  = no_branch,
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        )

    if python_version < 300:
        normal_cases = ( "function", "builtin_function_or_method", "instancemethod" )
    else:
        normal_cases = ( "function", "builtin_function_or_method" )

    statements = (
        CPythonStatementConditional(
            condition = CPythonExpressionBuiltinIsinstance(
                instance   = makeCalledVariableRef(),
                cls        = CPythonExpressionMakeTuple(
                    elements   = tuple(
                        CPythonExpressionBuiltinAnonymousRef(
                            builtin_name = builtin_name,
                            source_ref   = source_ref
                        )
                        for builtin_name in
                        normal_cases
                    ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            yes_branch = functions_case,
            no_branch  = no_branch,
            source_ref = source_ref
        ),
    )

    temp_block.setBody(
        CPythonStatementsSequence(
            statements = statements,
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsSequence(
            statements = ( temp_block, ),
            source_ref = source_ref
        )
    )

    return result


def _makeStarListArgumentToTupleStatement( provider, called_variable_ref,
                                           star_list_target_variable_ref,
                                           star_list_variable_ref ):
    raise_statement = CPythonStatementRaiseException(
        exception_type  = CPythonExpressionBuiltinMakeException(
            exception_name = "TypeError",
            args           = (
                CPythonExpressionOperationBinary(
                    operator = "Mod",
                    left     =  CPythonExpressionConstantRef(
                        constant   = "%s argument after * must be a sequence, not %s",
                        source_ref = source_ref
                    ),
                    right = CPythonExpressionMakeTuple(
                        elements = (
                            CPythonExpressionFunctionCall(
                                function   = CPythonExpressionFunctionCreation(
                                    function_ref = CPythonExpressionFunctionRef(
                                        function_body = getCallableNameDescBody( provider = provider ),
                                        source_ref    = source_ref
                                    ),
                                    defaults     = (),
                                    kw_defaults  = None,
                                    annotations  = None,
                                    source_ref   = source_ref
                                ),
                                values     = (
                                    called_variable_ref,
                                ),
                                source_ref = source_ref
                            ),
                            CPythonExpressionAttributeLookup(
                                expression = CPythonExpressionBuiltinType1(
                                    value      = star_list_variable_ref.makeCloneAt( source_ref ),
                                    source_ref = source_ref
                                ),
                                attribute_name = "__name__",
                                source_ref     = source_ref
                            )
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        exception_value = None,
        exception_trace = None,
        exception_cause = None,
        source_ref      = source_ref
    )

    handler = CPythonStatementExceptHandler(
        exception_types = (
            CPythonExpressionBuiltinExceptionRef(
                exception_name = "TypeError",
                source_ref     = source_ref
            ),
        ),
        body           = CPythonStatementsSequence(
            statements = (
                raise_statement,
            ),
            source_ref = source_ref
        ),
        source_ref     = source_ref
    )

    return CPythonStatementConditional(
        condition  = CPythonExpressionBuiltinIsinstance(
            instance   = star_list_variable_ref.makeCloneAt( source_ref ),
            cls        = CPythonExpressionBuiltinRef(
                builtin_name = "tuple",
                source_ref   = source_ref
            ),
            source_ref = source_ref
        ),
        yes_branch = None,
        no_branch  = CPythonStatementsSequence(
            statements = (
                CPythonStatementTryExcept(
                    tried      = CPythonStatementsSequence(
                        statements = (
                            CPythonStatementAssignmentVariable(
                                variable_ref = star_list_target_variable_ref.makeCloneAt( source_ref ),
                                source       = CPythonExpressionBuiltinTuple(
                                    value      = star_list_variable_ref.makeCloneAt( source_ref ),
                                    source_ref = source_ref
                                ),
                                source_ref   = source_ref
                            ),
                        ),
                        source_ref = source_ref
                    ),
                    handlers   = ( handler, ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        source_ref = source_ref
    )


def _makeStarDictArgumentToDictStatement( provider, called_variable_ref,
                                          star_dict_target_variable_ref,
                                          star_dict_variable_ref ):
    raise_statement = CPythonStatementRaiseException(
        exception_type  = CPythonExpressionBuiltinMakeException(
            exception_name = "TypeError",
            args           = (
                CPythonExpressionOperationBinary(
                    operator = "Mod",
                    left     =  CPythonExpressionConstantRef(
                        constant   = "%s argument after ** must be a mapping, not %s",
                        source_ref = source_ref
                    ),
                    right = CPythonExpressionMakeTuple(
                        elements = (
                            CPythonExpressionFunctionCall(
                                function   = CPythonExpressionFunctionCreation(
                                    function_ref = CPythonExpressionFunctionRef(
                                        function_body = getCallableNameDescBody( provider = provider ),
                                        source_ref    = source_ref
                                    ),
                                    defaults     = (),
                                    kw_defaults  = None,
                                    annotations  = None,
                                    source_ref   = source_ref
                                ),
                                values     = (
                                    called_variable_ref,
                                ),
                                source_ref = source_ref
                            ),
                            CPythonExpressionAttributeLookup(
                                expression = CPythonExpressionBuiltinType1(
                                    value      = star_dict_variable_ref.makeCloneAt( source_ref ),
                                    source_ref = source_ref
                                ),
                                attribute_name = "__name__",
                                source_ref     = source_ref
                            )
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        exception_value = None,
        exception_trace = None,
        exception_cause = None,
        source_ref      = source_ref
    )

    temp_block = CPythonStatementTempBlock(
        source_ref = source_ref
    )

    tmp_dict_variable = temp_block.getTempVariable( "dict" )
    tmp_iter_variable = temp_block.getTempVariable( "iter" )
    tmp_keys_variable = temp_block.getTempVariable( "keys" )
    tmp_key_variable = temp_block.getTempVariable( "key" )

    statements = (
        CPythonStatementTryExcept(
            tried      = CPythonStatementsSequence(
                statements = (
                    CPythonStatementAssignmentVariable(
                        variable_ref = CPythonExpressionTempVariableRef(
                            variable   = tmp_key_variable.makeReference( temp_block ),
                            source_ref = source_ref
                        ),
                        source     = CPythonExpressionBuiltinNext1(
                            value      = CPythonExpressionTempVariableRef(
                                variable   = tmp_iter_variable.makeReference( temp_block ),
                                source_ref = source_ref
                            ),
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                ),
                source_ref = source_ref
            ),
            handlers   = (
                CPythonStatementExceptHandler(
                    exception_types = (
                        CPythonExpressionBuiltinExceptionRef(
                            exception_name = "StopIteration",
                            source_ref     = source_ref
                        ),
                    ),
                    body           = CPythonStatementsSequence(
                        statements = (
                            CPythonStatementBreakLoop(
                                source_ref = source_ref
                            ),
                        ),
                        source_ref = source_ref
                    ),
                    source_ref     = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentSubscript(
            expression = CPythonExpressionTempVariableRef(
                variable   = tmp_dict_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            subscript  = CPythonExpressionTempVariableRef(
                variable   = tmp_key_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionSubscriptLookup(
                expression = star_dict_variable_ref.makeCloneAt( source_ref ),
                subscript  = CPythonExpressionTempVariableRef(
                    variable   = tmp_key_variable.makeReference( temp_block ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    loop_body = CPythonStatementsSequence(
        statements = statements,
        source_ref = source_ref
    )

    statements = (
        # Initializing the temp variable outside of try/except, because code generation
        # does not yet detect that case properly. TODO: Can be removed once code
        # generation is apt enough.
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_keys_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionConstantRef(
                constant   = None,
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementTryExcept(
            tried      = CPythonStatementsSequence(
                statements = (
                    CPythonStatementAssignmentVariable(
                        variable_ref = CPythonExpressionTempVariableRef(
                            variable   = tmp_keys_variable.makeReference( temp_block ),
                            source_ref = source_ref
                        ),
                        source     = CPythonExpressionCallEmpty(
                            called = CPythonExpressionAttributeLookup(
                                expression     = star_dict_variable_ref.makeCloneAt( source_ref ),
                                attribute_name = "keys",
                                source_ref     = source_ref
                            ),
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                ),
                source_ref = source_ref
            ),
            handlers   = (
                CPythonStatementExceptHandler(
                    exception_types = (
                        CPythonExpressionBuiltinExceptionRef(
                            exception_name = "AttributeError",
                            source_ref     = source_ref
                        ),
                    ),
                    body           = CPythonStatementsSequence(
                        statements = (
                            raise_statement,
                        ),
                        source_ref = source_ref
                    ),
                    source_ref     = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_iter_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionBuiltinIter1(
                value      = CPythonExpressionTempVariableRef(
                    variable   = tmp_keys_variable.makeReference( temp_block ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_dict_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionConstantRef(
                constant   = {},
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementLoop(
            body       = loop_body,
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = star_dict_target_variable_ref.makeCloneAt( source_ref ),
            source     = CPythonExpressionTempVariableRef(
                variable   = tmp_dict_variable.makeReference( temp_block ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
    )

    mapping_case = CPythonStatementsSequence(
        statements = statements,
        source_ref = source_ref
    )

    temp_block.setBody( mapping_case )

    mapping_case = CPythonStatementsSequence(
        statements = ( temp_block, ),
        source_ref = source_ref
    )

    return CPythonStatementConditional(
            condition  = CPythonExpressionOperationNOT(
                operand    = CPythonExpressionBuiltinIsinstance(
                    instance   = star_dict_variable_ref.makeCloneAt( source_ref ),
                    cls        = CPythonExpressionBuiltinRef(
                        builtin_name = "dict",
                        source_ref   = source_ref
                    ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            yes_branch = mapping_case,
            no_branch  = None,
            source_ref = source_ref
        )


def _makeStarDictArgumentMergeToKwStatement( provider, called_variable_ref,
                                             kw_target_variable_ref, kw_variable_ref,
                                             star_dict_variable_ref ):
    # This is plain terribly complex, pylint: disable=R0914

    raise_statement = CPythonStatementRaiseException(
        exception_type  = CPythonExpressionBuiltinMakeException(
            exception_name = "TypeError",
            args           = (
                CPythonExpressionOperationBinary(
                    operator = "Mod",
                    left     =  CPythonExpressionConstantRef(
                        constant   = "%s argument after ** must be a mapping, not %s",
                        source_ref = source_ref
                    ),
                    right = CPythonExpressionMakeTuple(
                        elements = (
                            CPythonExpressionFunctionCall(
                                function   = CPythonExpressionFunctionCreation(
                                    function_ref = CPythonExpressionFunctionRef(
                                        function_body = getCallableNameDescBody( provider = provider ),
                                        source_ref    = source_ref
                                    ),
                                    defaults     = (),
                                    kw_defaults  = None,
                                    annotations  = None,
                                    source_ref   = source_ref
                                ),
                                values     = (
                                    called_variable_ref.makeCloneAt( source_ref ),
                                ),
                                source_ref = source_ref
                            ),
                            CPythonExpressionAttributeLookup(
                                expression = CPythonExpressionBuiltinType1(
                                    value      = star_dict_variable_ref.makeCloneAt( source_ref ),
                                    source_ref = source_ref
                                ),
                                attribute_name = "__name__",
                                source_ref     = source_ref
                            )
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        exception_value = None,
        exception_trace = None,
        exception_cause = None,
        source_ref      = source_ref
    )

    mapping_case = CPythonStatementTempBlock(
        source_ref = source_ref
    )

    tmp_dict_variable = mapping_case.getTempVariable( "dict" )
    tmp_keys_variable = mapping_case.getTempVariable( "keys" )
    tmp_key_variable = mapping_case.getTempVariable( "key" )
    tmp_iter_variable = mapping_case.getTempVariable( "iter" )

    raise_duplicate = CPythonStatementRaiseException(
        exception_type  = CPythonExpressionBuiltinMakeException(
            exception_name = "TypeError",
            args           = (
                CPythonExpressionOperationBinary(
                    operator = "Mod",
                    left     =  CPythonExpressionConstantRef(
                        constant   = "%s got multiple values for keyword argument '%s'",
                        source_ref = source_ref
                    ),
                    right = CPythonExpressionMakeTuple(
                        elements = (
                            CPythonExpressionFunctionCall(
                                function   = CPythonExpressionFunctionCreation(
                                    function_ref = CPythonExpressionFunctionRef(
                                        function_body = getCallableNameDescBody( provider = provider ),
                                        source_ref    = source_ref
                                    ),
                                    defaults     = (),
                                    kw_defaults  = None,
                                    annotations  = None,
                                    source_ref   = source_ref
                                ),
                                values     = (
                                    called_variable_ref.makeCloneAt( source_ref ),
                                ),
                                source_ref = source_ref
                            ),
                            CPythonExpressionTempVariableRef(
                                variable   = tmp_key_variable.makeReference( mapping_case ),
                                source_ref = source_ref
                            )
                        ),
                        source_ref = source_ref
                    ),
                    source_ref = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        exception_value = None,
        exception_trace = None,
        exception_cause = None,
        source_ref      = source_ref
    )

    statements = (
        CPythonStatementTryExcept(
            tried      = CPythonStatementsSequence(
                statements = (
                    CPythonStatementAssignmentVariable(
                        variable_ref = CPythonExpressionTempVariableRef(
                            variable   = tmp_key_variable.makeReference( mapping_case ),
                            source_ref = source_ref
                        ),
                        source     = CPythonExpressionBuiltinNext1(
                            value      = CPythonExpressionTempVariableRef(
                                variable   = tmp_iter_variable.makeReference( mapping_case ),
                                source_ref = source_ref
                            ),
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                ),
                source_ref = source_ref
            ),
            handlers   = (
                CPythonStatementExceptHandler(
                    exception_types = (
                        CPythonExpressionBuiltinExceptionRef(
                            exception_name = "StopIteration",
                            source_ref     = source_ref
                        ),
                    ),
                    body           = CPythonStatementsSequence(
                        statements = (
                            CPythonStatementBreakLoop(
                                source_ref = source_ref
                            ),
                        ),
                        source_ref = source_ref
                    ),
                    source_ref     = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        CPythonStatementConditional(
            condition = CPythonExpressionComparison(
                comparator = "In",
                left       = CPythonExpressionTempVariableRef(
                    variable   = tmp_key_variable.makeReference( mapping_case ),
                    source_ref = source_ref
                ),
                right      = kw_variable_ref.makeCloneAt( source_ref ),
                source_ref = source_ref
            ),
            yes_branch = CPythonStatementsSequence(
                statements = ( raise_duplicate, ),
                source_ref = source_ref
            ),
            no_branch  = None,
            source_ref = source_ref
        ),
        CPythonStatementAssignmentSubscript(
            expression = kw_variable_ref.makeCloneAt( source_ref ),
            subscript  = CPythonExpressionTempVariableRef(
                variable   = tmp_key_variable.makeReference( mapping_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionSubscriptLookup(
                expression = star_dict_variable_ref.makeCloneAt( source_ref ),
                subscript  = CPythonExpressionTempVariableRef(
                    variable   = tmp_key_variable.makeReference( mapping_case ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    mapping_loop_body = CPythonStatementsSequence(
        statements = statements,
        source_ref = source_ref
    )

    statements = (
        # Initializing the temp variable outside of try/except, because code generation
        # does not yet detect that case properly. TODO: Can be removed once code
        # generation is apt enough.
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_keys_variable.makeReference( mapping_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionConstantRef(
                constant   = None,
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementTryExcept(
            tried      = CPythonStatementsSequence(
                statements = (
                    CPythonStatementAssignmentVariable(
                        variable_ref = CPythonExpressionTempVariableRef(
                            variable   = tmp_keys_variable.makeReference( mapping_case ),
                            source_ref = source_ref
                        ),
                        source     = CPythonExpressionCallEmpty(
                            called = CPythonExpressionAttributeLookup(
                                expression     = star_dict_variable_ref.makeCloneAt( source_ref ),
                                attribute_name = "keys",
                                source_ref     = source_ref
                            ),
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                ),
                source_ref = source_ref
            ),
            handlers   = (
                CPythonStatementExceptHandler(
                    exception_types = (
                        CPythonExpressionBuiltinExceptionRef(
                            exception_name = "AttributeError",
                            source_ref     = source_ref
                        ),
                    ),
                    body           = CPythonStatementsSequence(
                        statements = (
                            raise_statement,
                        ),
                        source_ref = source_ref
                    ),
                    source_ref     = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_iter_variable.makeReference( mapping_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionBuiltinIter1(
                value      = CPythonExpressionTempVariableRef(
                    variable   = tmp_keys_variable.makeReference( mapping_case ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_dict_variable.makeReference( mapping_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionConstantRef(
                constant   = {},
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementLoop(
            body       = mapping_loop_body,
            source_ref = source_ref
        ),
    )

    mapping_case.setBody(
        CPythonStatementsSequence(
            statements = statements,
            source_ref = source_ref
        )
    )

    mapping_case = CPythonStatementsSequence(
        statements = ( mapping_case, ),
        source_ref = source_ref
    )

    dict_case = CPythonStatementTempBlock(
        source_ref = source_ref
    )

    tmp_iter_variable = dict_case.getTempVariable( "iter" )
    tmp_item_variable = dict_case.getTempVariable( "item" )
    tmp_key_variable = dict_case.getTempVariable( "key" )

    statements = (
        CPythonStatementTryExcept(
            tried      = CPythonStatementsSequence(
                statements = (
                    CPythonStatementAssignmentVariable(
                        variable_ref = CPythonExpressionTempVariableRef(
                            variable   = tmp_item_variable.makeReference( dict_case ),
                            source_ref = source_ref
                        ),
                        source     = CPythonExpressionBuiltinNext1(
                            value      = CPythonExpressionTempVariableRef(
                                variable   = tmp_iter_variable.makeReference( dict_case ),
                                source_ref = source_ref
                            ),
                            source_ref = source_ref
                        ),
                        source_ref = source_ref
                    ),
                ),
                source_ref = source_ref
            ),
            handlers   = (
                CPythonStatementExceptHandler(
                    exception_types = (
                        CPythonExpressionBuiltinExceptionRef(
                            exception_name = "StopIteration",
                            source_ref     = source_ref
                        ),
                    ),
                    body           = CPythonStatementsSequence(
                        statements = (
                            CPythonStatementBreakLoop( source_ref ),
                        ),
                        source_ref = source_ref
                    ),
                    source_ref     = source_ref
                ),
            ),
            source_ref = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_key_variable.makeReference( dict_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionSubscriptLookup(
                expression = CPythonExpressionTempVariableRef(
                    variable   = tmp_item_variable.makeReference( dict_case ),
                    source_ref = source_ref
                ),
                subscript  = CPythonExpressionConstantRef(
                    constant    = 0,
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        CPythonStatementConditional(
            condition = CPythonExpressionComparison(
                comparator = "In",
                left       = CPythonExpressionTempVariableRef(
                    variable   = tmp_key_variable.makeReference( dict_case ),
                    source_ref = source_ref
                ),
                right      = kw_variable_ref.makeCloneAt( source_ref ),
                source_ref = source_ref
            ),
            yes_branch = CPythonStatementsSequence(
                statements = ( raise_duplicate, ),
                source_ref = source_ref
            ),
            no_branch  = None,
            source_ref = source_ref
        ),
        CPythonStatementAssignmentSubscript(
            expression = kw_variable_ref.makeCloneAt( source_ref ),
            subscript  = CPythonExpressionTempVariableRef(
                variable   = tmp_key_variable.makeReference( dict_case ),
                source_ref = source_ref
            ),
            source     = CPythonExpressionSubscriptLookup(
                expression = CPythonExpressionTempVariableRef(
                    variable   = tmp_item_variable.makeReference( dict_case ),
                    source_ref = source_ref
                ),
                subscript  = CPythonExpressionConstantRef(
                    constant   = 1,
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    dict_loop_body = CPythonStatementsSequence(
        statements = statements,
        source_ref = source_ref
    )

    statements = (
        CPythonStatementAssignmentVariable(
            variable_ref = kw_target_variable_ref.makeCloneAt( source_ref ),
            source       = CPythonExpressionBuiltinDict(
                pos_arg    = kw_variable_ref.makeCloneAt( source_ref ),
                pairs      = (),
                source_ref = source_ref
            ),
            source_ref   = source_ref
        ),
        CPythonStatementAssignmentVariable(
            variable_ref = CPythonExpressionTempVariableRef(
                variable   = tmp_iter_variable.makeReference( dict_case ),
                source_ref = source_ref
            ),
            source       = CPythonExpressionBuiltinIter1(
                value = CPythonExpressionCallEmpty(
                    called = CPythonExpressionAttributeLookup(
                        expression     = star_dict_variable_ref.makeCloneAt( source_ref ),
                        attribute_name = "iteritems" if python_version < 300 else "items",
                        source_ref     = source_ref
                    ),
                    source_ref     = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref   = source_ref
        ),
        CPythonStatementLoop(
            body       = dict_loop_body,
            source_ref = source_ref
        ),
    )

    dict_case.setBody(
        CPythonStatementsSequence(
            statements = statements,
            source_ref = source_ref
        )
    )

    dict_case = CPythonStatementsSequence(
        statements = ( dict_case, ),
        source_ref = source_ref
    )

    statements = (
        CPythonStatementConditional(
            condition  = star_dict_variable_ref.makeCloneAt( source_ref ),
            yes_branch = dict_case,
            no_branch  = None,
            source_ref = source_ref
        ),
    )

    dict_case = CPythonStatementsSequence(
        statements = statements,
        source_ref = source_ref
    )

    return CPythonStatementConditional(
        condition  = CPythonExpressionOperationNOT(
            operand    = CPythonExpressionBuiltinIsinstance(
                instance   = star_dict_variable_ref.makeCloneAt( source_ref ),
                cls        = CPythonExpressionBuiltinRef(
                    builtin_name = "dict",
                    source_ref   = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        ),
        yes_branch = mapping_case,
        no_branch  = dict_case,
        source_ref = source_ref
    )


@once_decorator
def getFunctionCallHelperStarList( provider ):
    helper_name = "complex_call_helper_star_list"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "star_arg_list" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, star_arg_list_variable = result.getParameters().getAllVariables()

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to PyObject_Call.
    #
    # if not isinstance( star_arg_list, tuple ):
    #     try:
    #         star_arg_list = tuple( star_arg_list )
    #     except TypeError:
    #         raise TypeError, "%s argument after * must be a sequence, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_list ).__name__
    #         )
    #
    # return called( *star_arg_list )

    statements = (
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCallNoKeywords(
                called     = makeCalledVariableRef(),
                args       = makeStarListArgVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    # TODO: Code generation should become capable of not generating actual exceptions for the
    # TypeError caught immediately and then unused, then the frame will be unnecessary.
    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperKeywordsStarList( provider ):
    helper_name = "complex_call_helper_keywords_star_list"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "kw", "star_arg_list" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, kw_variable, star_arg_list_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeKwVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to PyObject_Call.
    #
    # if not isinstance( star_arg_list, tuple ):
    #     try:
    #         star_arg_list = tuple( star_arg_list )
    #     except TypeError:
    #         raise TypeError, "%s argument after * must be a sequence, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_list ).__name__
    #         )
    #
    # return called( *star_arg_list )

    statements = (
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = makeStarListArgVariableRef( assign = False ),
                kw         = makeKwVariableRef(),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    # TODO: Code generation should become capable of not generating actual exceptions for the
    # TypeError caught immediately and then unused, then the frame will be unnecessary.
    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperPosStarList( provider ):
    helper_name = "complex_call_helper_pos_star_list"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "star_arg_list" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, star_arg_list_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to PyObject_Call.
    #
    # if not isinstance( star_arg_list, tuple ):
    #     try:
    #         star_arg_list = tuple( star_arg_list )
    #     except TypeError:
    #         raise TypeError, "%s argument after * must be a sequence, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_list ).__name__
    #         )
    #
    # return called( *star_arg_list )

    statements = (
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCallNoKeywords(
                called     = makeCalledVariableRef(),
                args       = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    left       = makeArgsVariableRef(),
                    right      = makeStarListArgVariableRef( assign = False ),
                    source_ref = source_ref
                ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    # TODO: Code generation should become capable of not generating actual exceptions for the
    # TypeError caught immediately and then unused, then the frame will be unnecessary.
    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

def getFunctionCallHelperPosKeywordsStarList( provider ):
    helper_name = "complex_call_helper_pos_keywords_star_list"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "kw", "star_arg_list" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, kw_variable, star_arg_list_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeKwVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to PyObject_Call.
    #
    # if not isinstance( star_arg_list, tuple ):
    #     try:
    #         star_arg_list = tuple( star_arg_list )
    #     except TypeError:
    #         raise TypeError, "%s argument after * must be a sequence, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_list ).__name__
    #         )
    #
    # return called( *star_arg_list )

    statements = (
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    left       = makeArgsVariableRef(),
                    right      = makeStarListArgVariableRef( assign = False ),
                    source_ref = source_ref
                ),
                kw         = makeKwVariableRef(),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    # TODO: Code generation should become capable of not generating actual exceptions for the
    # TypeError caught immediately and then unused, then the frame will be unnecessary.
    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperStarDict( provider ):
    helper_name = "complex_call_helper_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, star_arg_dict_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeStarDictArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to
    # PyObject_Call.
    #
    # if not isinstance( star_arg_dict, dict ):
    #     try:
    #         tmp_keys =  star_arg_dict.keys()
    #     except AttributeError:
    #         raise TypeError, ""%s argument after ** must be a mapping, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_dict ).__name__
    #         )
    #
    #     tmp_iter = iter( keys )
    #     tmp_dict = {}
    #
    #     while 1:
    #         try:
    #             tmp_key = tmp_iter.next()
    #         except StopIteration:
    #             break
    #
    #         tmp_dict[ tmp_key ] = star_dict_arg[ tmp_key )
    #
    #     star_arg_dict = new
    #
    # return called( **star_arg_dict )

    statements = (
        _makeStarDictArgumentToDictStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_dict_variable_ref        = makeStarDictArgVariableRef( assign = False ),
            star_dict_target_variable_ref = makeStarDictArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCallKeywordsOnly(
                called     = makeCalledVariableRef(),
                kw         = makeStarDictArgVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperPosStarDict( provider ):
    helper_name = "complex_call_helper_pos_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, star_arg_dict_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeStarDictArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to
    # PyObject_Call.
    #
    # if not isinstance( star_arg_dict, dict ):
    #     try:
    #         tmp_keys =  star_arg_dict.keys()
    #     except AttributeError:
    #         raise TypeError, ""%s argument after ** must be a mapping, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_dict ).__name__
    #         )
    #
    #     tmp_iter = iter( keys )
    #     tmp_dict = {}
    #
    #     while 1:
    #         try:
    #             tmp_key = tmp_iter.next()
    #         except StopIteration:
    #             break
    #
    #         tmp_dict[ tmp_key ] = star_dict_arg[ tmp_key )
    #
    #     star_arg_dict = new
    #
    # return called( args, **star_arg_dict )

    statements = (
        _makeStarDictArgumentToDictStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_dict_variable_ref        = makeStarDictArgVariableRef( assign = False ),
            star_dict_target_variable_ref = makeStarDictArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = makeArgsVariableRef(),
                kw         = makeStarDictArgVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result


@once_decorator
def getFunctionCallHelperKeywordsStarDict( provider ):
    helper_name = "complex_call_helper_keywords_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "kw", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, kw_variable, star_arg_dict_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeStarDictArgVariableRef():
        variable_ref_class = CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    def makeKwVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref


    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to
    # PyObject_Call. One goal is to avoid copying "kw" unless really necessary, and
    # to take the slow route only for non-dictionaries.
    #
    # if not isinstance( star_arg_dict, dict ):
    #     try:
    #         tmp_keys =  star_arg_dict.keys()
    #     except AttributeError:
    #         raise TypeError, ""%s argument after ** must be a mapping, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_dict ).__name__
    #         )
    #
    #     if keys:
    #         kw = dict( kw )
    #
    #         tmp_iter = iter( keys )
    #         tmp_dict = {}
    #
    #         while 1:
    #             try:
    #                 tmp_key = tmp_iter.next()
    #             except StopIteration:
    #                  break
    #
    #             if tmp_key in kw:
    #                 raise TypeError, "%s got multiple values for keyword argument '%s'" % (
    #                     get_callable_name_desc( function ),
    #                     tmp_key
    #                 )
    #
    #             kw[ tmp_key ] = star_dict_arg[ tmp_key )
    #
    # elif star_arg_dict:
    #    tmp_iter = star_arg_dict.iteritems()
    #
    #    kw = dict( kw )
    #    while 1:
    #        try:
    #            tmp_key, tmp_value = tmp_iter.next()
    #        except StopIteration:
    #            break
    #
    #        if tmp_key in kw:
    #            raise TypeError, "%s got multiple values for keyword argument '%s'" % (
    #                 get_callable_name_desc( function ),
    #                 tmp_key
    #            )
    #
    #        kw[ tmp_key ] = tmp_value
    #
    # return called( **kw  )

    statements = (
        _makeStarDictArgumentMergeToKwStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            kw_variable_ref               = makeKwVariableRef( assign = False ),
            kw_target_variable_ref        = makeKwVariableRef( assign = True ),
            star_dict_variable_ref        = makeStarDictArgVariableRef()
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCallKeywordsOnly(
                called     = makeCalledVariableRef(),
                kw         = makeKwVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperPosKeywordsStarDict( provider ):
    helper_name = "complex_call_helper_pos_keywords_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "kw", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, kw_variable, star_arg_dict_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeStarDictArgVariableRef():
        variable_ref_class = CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    def makeKwVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref


    # Equivalent of:
    #
    # Note: Call in here is not the same, as it can go without checks directly to
    # PyObject_Call. One goal is to avoid copying "kw" unless really necessary, and
    # to take the slow route only for non-dictionaries.
    #
    # if not isinstance( star_arg_dict, dict ):
    #     try:
    #         tmp_keys =  star_arg_dict.keys()
    #     except AttributeError:
    #         raise TypeError, ""%s argument after ** must be a mapping, not %s" % (
    #             get_callable_name_desc( function ),
    #             type( star_arg_dict ).__name__
    #         )
    #
    #     if keys:
    #         kw = dict( kw )
    #
    #         tmp_iter = iter( keys )
    #         tmp_dict = {}
    #
    #         while 1:
    #             try:
    #                 tmp_key = tmp_iter.next()
    #             except StopIteration:
    #                  break
    #
    #             if tmp_key in kw:
    #                 raise TypeError, "%s got multiple values for keyword argument '%s'" % (
    #                     get_callable_name_desc( function ),
    #                     tmp_key
    #                 )
    #
    #             kw[ tmp_key ] = star_dict_arg[ tmp_key )
    #
    # elif star_arg_dict:
    #    tmp_iter = star_arg_dict.iteritems()
    #
    #    kw = dict( kw )
    #    while 1:
    #        try:
    #            tmp_key, tmp_value = tmp_iter.next()
    #        except StopIteration:
    #            break
    #
    #        if tmp_key in kw:
    #            raise TypeError, "%s got multiple values for keyword argument '%s'" % (
    #                 get_callable_name_desc( function ),
    #                 tmp_key
    #            )
    #
    #        kw[ tmp_key ] = tmp_value
    #
    # return called( **kw  )

    statements = (
        _makeStarDictArgumentMergeToKwStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            kw_variable_ref               = makeKwVariableRef( assign = False ),
            kw_target_variable_ref        = makeKwVariableRef( assign = True ),
            star_dict_variable_ref        = makeStarDictArgVariableRef()
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = makeArgsVariableRef(),
                kw         = makeKwVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result


@once_decorator
def getFunctionCallHelperStarListStarDict( provider ):
    helper_name = "complex_call_helper_star_list_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "star_arg_list", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, star_arg_list_variable, star_arg_dict_variable = result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    def makeStarDictArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    statements = (
        _makeStarDictArgumentToDictStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_dict_variable_ref        = makeStarDictArgVariableRef( assign = False ),
            star_dict_target_variable_ref = makeStarDictArgVariableRef( assign = True )
        ),
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = makeStarListArgVariableRef( assign = False ),
                kw         = makeStarDictArgVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result

@once_decorator
def getFunctionCallHelperPosStarListStarDict( provider ):
    helper_name = "complex_call_helper_pos_star_list_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "star_arg_list", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, star_arg_list_variable, star_arg_dict_variable = \
        result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    def makeStarDictArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    statements = (
        _makeStarDictArgumentToDictStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_dict_variable_ref        = makeStarDictArgVariableRef( assign = False ),
            star_dict_target_variable_ref = makeStarDictArgVariableRef( assign = True )
        ),
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    left       = makeArgsVariableRef(),
                    right      = makeStarListArgVariableRef( assign = False ),
                    source_ref = source_ref
                ),
                kw         = makeStarDictArgVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result


@once_decorator
def getFunctionCallHelperKeywordsStarListStarDict( provider ):
    helper_name = "complex_call_helper_keywords_star_list_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "kw", "star_arg_list", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, kw_variable, star_arg_list_variable, star_arg_dict_variable = \
        result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeKwVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    def makeStarDictArgVariableRef():
        variable_ref_class = CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    statements = (
        _makeStarDictArgumentMergeToKwStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            kw_variable_ref               = makeKwVariableRef( assign = False ),
            kw_target_variable_ref        = makeKwVariableRef( assign = True ),
            star_dict_variable_ref        = makeStarDictArgVariableRef()
        ),
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = makeStarListArgVariableRef( assign = False ),
                kw         = makeKwVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result


@once_decorator
def getFunctionCallHelperPosKeywordsStarListStarDict( provider ):
    helper_name = "complex_call_helper_pos_keywords_star_list_star_dict"

    # Only need to check if the star argument value is a sequence and then convert to tuple.
    result = CPythonExpressionFunctionBody(
        provider   = provider, # We shouldn't need that.
        name       = helper_name,
        doc        = None,
        parameters = ParameterSpec(
            name          = helper_name,
            normal_args   = ( "called", "args", "kw", "star_arg_list", "star_arg_dict" ),
            list_star_arg = None,
            dict_star_arg = None,
            default_count = 0,
            kw_only_args  = ()
        ),
        source_ref = source_ref,
        is_class   = False
    )

    called_variable, args_variable, kw_variable, star_arg_list_variable, star_arg_dict_variable = \
        result.getParameters().getAllVariables()

    def makeCalledVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = called_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( called_variable )

        return variable_ref

    def makeArgsVariableRef():
        variable_ref = CPythonExpressionVariableRef(
            variable_name = args_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( args_variable )

        return variable_ref

    def makeKwVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = kw_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( kw_variable )

        return variable_ref

    def makeStarListArgVariableRef( assign ):
        variable_ref_class = CPythonExpressionTargetVariableRef if assign else CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_list_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_list_variable )

        return variable_ref

    def makeStarDictArgVariableRef():
        variable_ref_class = CPythonExpressionVariableRef

        variable_ref = variable_ref_class(
            variable_name = star_arg_dict_variable.getName(),
            source_ref    = source_ref
        )

        variable_ref.setVariable( star_arg_dict_variable )

        return variable_ref

    statements = (
        _makeStarDictArgumentMergeToKwStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            kw_variable_ref               = makeKwVariableRef( assign = False ),
            kw_target_variable_ref        = makeKwVariableRef( assign = True ),
            star_dict_variable_ref        = makeStarDictArgVariableRef()
        ),
        _makeStarListArgumentToTupleStatement(
            provider = provider,
            called_variable_ref           = makeCalledVariableRef(),
            star_list_variable_ref        = makeStarListArgVariableRef( assign = False ),
            star_list_target_variable_ref = makeStarListArgVariableRef( assign = True )
        ),
        CPythonStatementReturn(
            expression = CPythonExpressionCall(
                called     = makeCalledVariableRef(),
                args       = CPythonExpressionOperationBinary(
                    operator   = "Add",
                    left       = makeArgsVariableRef(),
                    right      = makeStarListArgVariableRef( assign = False ),
                    source_ref = source_ref
                ),
                kw         = makeKwVariableRef( assign = False ),
                source_ref = source_ref
            ),
            source_ref = source_ref
        )
    )

    result.setBody(
        CPythonStatementsFrame(
            code_name     = "unused",
            guard_mode    = "pass_through",
            arg_names     = (),
            kw_only_count = 0,
            statements    = statements,
            source_ref    = source_ref
        )
    )

    return result
