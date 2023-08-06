#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module generates Ada code from SDL process models.
    The Ada code is compliant with the TASTE interfaces, and is
    using the ASN.1 "Space-Certified" compiler for data type definition.
    (See TASTE documentation for more information)

    The design is very flexible and can be used as basis for
    generating other backends.

    When the model is parsed, functions are called to generate the code
    of each symbol. The result, that is symbol based, is a tuple containing
    two entries: local declarations, and actual code. This allows the
    backend template to organize easily the layout of the code.
    These functions are suffixed with "Statement" (e.g. output_statement).

    In turn, when a symbol encounters an expression (assignment, field access,
    embedded constructs), recursive functions (prefixed with "decipher")
    analyze the content and return a tuple with 3 values: "code" (statements),
    "string", and "local declarations". The string is the result of the
    evaluation of the expression - it has to be defined in the "code" part,
    and possibly declared in the "local declarations" part.

    At the end of the recursive call, the caller can build the code easily, in
    particular when intermediate variables need to be created.

    For example, take the SDL statement "OUTPUT hello(a+5)"

    This results (in TASTE terminology) in calling the required interface
    called "hello" and passing a parameter of an ASN.1 type (say MyInteger).
    The parameter is always passed by reference.

    It is therefore necessary to build a temporary variable to hold the result
    of the "a+5" expression.

    In this example, the output_statement function will return:
    local_decl = ["tmp01 : MyInteger;"]
    (The template backend can then place it wherever appropriate)

    and code = ["tmp01 := a + 5;", "hello(tmp01);"]
    (The template will then do a '\n'.join(code) - and add indents).

    To know about "tmp01" and generate the code "hello(tmp01);",
    output_statement will call decipher_expression and
    pass a+5 as parameter. decipher_expression will return the tuple:

    local_decl = ["tmp01 : MyInteger;"]
    code = ["tmp01 := a + 5;"]
    string = "tmp01"

    The string is the only thing of practical interest to output_statement.
    Rest is forwarded to its caller, who eventually will produce the
    code by grouping all declarations together, separately from the
    statements.

    This design allows to have any level of complexity in the embedded
    expression in a way that is easy to handle (adding constructs with
    this pattern is straightforward, once the decipher_expression is
    properly implemented).

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


import ogAST

import logging
LOG = logging.getLogger(__name__)

# reference to the ASN.1 Data view and to the process variables
TYPES = None
VARIABLES = None
# List of output signals and procedures
OUT_SIGNALS = None
PROCEDURES = None

# lookup table for mapping SDL operands with the corresponding Ada ones
OPERANDS = {'plus': '+', 'mul': '*', 'minus': '-', 'or': 'or',
        'and': 'and', 'xor': 'CHECKME', 'eq': '=', 'neq': '/=', 'gt': '>',
        'ge': '>=', 'lt': '<', 'le': '<=', 'div': '/', 'mod': 'mod'}


def find_basic_type(a_type):
    ''' Return the ASN.1 basic type of aType '''
    basic_type = a_type
    while basic_type['Kind'] == 'ReferenceType':
        # Find type with proper case in the data view
        for typename in TYPES.viewkeys():
            if typename.lower() == basic_type['ReferencedTypeName'].lower():
                basic_type = TYPES[typename]['type']
                break
    return basic_type


def get_type_of_parent(identifier):
    ''' Return the type of a "parent" construct (a!b!c)=>return type of b '''
    kind = ''
    name = ''
    if len(identifier) > 1:
        if identifier[0] in VARIABLES:
            name = VARIABLES[identifier[0]].replace('_', '-')
            current_type = TYPES[name]['type']
            for index in range(1, len(identifier)):
                # TODO find type...
                LOG.warning('** INCOMPLETE FEATURE ** ')
            kind = current_type['Kind']
    return kind, name


def traceability(symbol):
    ''' Return a string with code-to-model traceability '''
    trace = ['-- {line}'.format(line=l) for l in
        repr(symbol).split('\n')]
    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))
    return trace


def write_statement(param, newline):
    ''' Generate the code for the special "write" operator '''
    code = []
    string = ''
    local = []
    basic_type = find_basic_type(param.exprType) or {}
    type_kind = basic_type.get('Kind')
    if type_kind == 'StringType':
        # Raw string
        string = '"' + param.inputString[1:-1] + '"'
    elif type_kind in ('IntegerType', 'RealType', 'BooleanType'):
        code, string, local = decipher_expression(param)
        if type_kind == 'IntegerType':
            cast = "Interfaces.Integer_64"
        elif type_kind == 'RealType':
            cast = 'Long_Float'
        elif type_kind == 'BooleanType':
            cast = 'Boolean'
        string = "{cast}'Image({s})".format(cast=cast, s=string)
    else:
        error = ('Unsupported parameter in write call' +
                param.var.inputString)
        LOG.error(error)
        raise TypeError(error)
    code.append('Put{line}({string});'.format(
        line='_Line' if newline else '',
        string=string))
    return code, string, local


def output_statement(output):
    ''' Generate the code of a set of output or procedure call statement '''
    code = []
    local_decl = []

    # Add the traceability information
    code.extend(traceability(output))

    for out in output.output:
        signal_name = out['outputName']

        if signal_name.lower() in ('write', 'writeln'):
            # special built-in SDL procedure for printing strings
            # supports printing of native types (int, real, bool)
            # but not yet complex ASN.1 structures (sequence/seqof/choice)
            for param in out['params'][:-1]:
                stmts, _, local = write_statement(param, newline=False)
                code.extend(stmts)
                local_decl.extend(local)
            for param in out['params'][-1:]:
                # Last parameter - add newline if necessary
                stmts, _, local = write_statement(param, newline=True if
                        signal_name.lower() == 'writeln' else False)
                code.extend(stmts)
                local_decl.extend(local)
            continue
        if output.kind == 'output':
            out_sig = OUT_SIGNALS.get(signal_name.lower())
        else:
            out_sig = PROCEDURES.get(signal_name.lower())
        if not out_sig:
            error = 'Signal or procedure not defined:' + str(signal_name)
            LOG.error(error)
            raise NameError(error)
        nb_in_params = len(out_sig['paramsInOrdered'])
        list_of_params = []
        for idx, param in enumerate(out.get('params') or []):
            # Determine if it is an IN or OUT type
            select = ('paramsOutOrdered', 'out', idx - nb_in_params) if (
                    idx >= nb_in_params) else ('paramsInOrdered', 'in', idx)

            # Get parameter name and type from the Interface view:
            param_name = out_sig[select[0]][select[2]]
            param_type = out_sig[select[1]][param_name]['type']

            # Check the type of the parameter - set it if missing
            # (TODO: do it in the parser)
            if param.exprType.get('Kind') == 'UnknownType':
                param.exprType = {'Kind': 'ReferenceType',
                        'ReferencedTypeName': param_type}

            p_code, p_id, p_local = decipher_expression(param)
            code.extend(p_code)
            local_decl.extend(p_local)
            # Create a temporary variable for this parameter
            tmp_id = out['tmpVars'][idx]
            local_decl.append('tmp{idx} : aliased asn1Scc{oType};'.format(
                idx=tmp_id, oType=param_type))
            code.append('tmp{idx} := {p_id};'.format(
                idx=tmp_id, p_id=p_id))
            list_of_params.append("tmp{idx}'access".
                    format(idx=out['tmpVars'][idx]))
        if list_of_params:
            code.append('{RI}({params});'.format(
                RI=out['outputName'], params=', '.join(list_of_params)))
            # Assign back the out parameters to the local variables
            if len(out_sig['paramsOutOrdered']) > 0:
                for (idx, parameter) in ((idx, p)
                        for idx, p in enumerate(out['params'])
                        if idx >= nb_in_params):
                    _, p_id, __ = decipher_expression(parameter)
                    code.append('{p_id} := tmp{idx};'.format(
                        p_id=p_id, idx=out['tmpVars'][idx]))
        else:
            code.append('{RI};'.format(RI=out['outputName']))
    return code, local_decl


def task_statement(task):
    ''' generate the code of a task (set of assign) '''
    code = []
    local_decl = []
    if task.comment:
        # Add the (optional) comment symbol text as Ada comment
        code.extend(traceability(task.comment))
    if task.kind == 'informal_text':
        # Generate Ada comments for informal text
        for informal_task in task.informalText:
            code.append('--  ' + informal_task.replace('\n', '\n' + '--  '))
    elif task.kind == 'assign':
        for expr in task.assign:
            # There can be several assignations in one task
            if expr.kind != 'assign':
                raise ValueError('expression not an assign')
            code.extend(traceability(expr))
            dest = expr.left
            val = expr.right
            if dest.kind != 'primary' or dest.var.kind != 'primaryId':
                raise ValueError('destination is not primary:' +
                        dest.inputString)
            # Get the Ada string for the left part of the expression
            left_stmts, left_str, left_local = decipher_expression(dest)
            right_stmts, right_str, right_local = decipher_expression(val)
            assign_str = left_str + ' := ' + right_str + ';'
            code.extend(left_stmts)
            code.extend(right_stmts)
            local_decl.extend(left_local)
            local_decl.extend(right_local)
            code.append(assign_str)
    else:
        raise ValueError('task kind is unknown: ' + task.kind)
    return code, local_decl


def decipher_primary_id(primaryId):
    '''
    Return the Ada string of a PrimaryId element list
    '''
    ada_string = ''
    stmts = []
    local_decl = []
    # cases: a => 'a' (reference to a variable)
    # a!b => a.b (field of a structure)
    # a!b if a is a CHOICE => TypeOfa_b_get(a)
    # a(Expression) => a(ExpressionSolver) (array index)
    # Expression can be complex (if-then-else-fi..)
    sep = 'l_'
    sub_id = []
    for pr_id in primaryId:
        if type(pr_id) is not dict:
            if pr_id.lower() == 'length':
                special_op = 'Length'
                continue
            elif pr_id.lower() == 'present':
                special_op = 'ChoiceKind'
                continue
            special_op = ''
            sub_id.append(pr_id)
            parent_kind, parent_typename = get_type_of_parent(sub_id)
            if parent_kind == 'ChoiceType':
                ada_string = ('asn1Scc{typename}_{p_id}_get({ada_string})'
                        .format(typename=parent_typename, p_id=pr_id,
                        ada_string=ada_string))
            else:
                ada_string += sep + pr_id
        else:
            # index is a LIST - only taking 1st elem.
            if 'index' in pr_id:
                if len(pr_id['index']) > 1:
                    LOG.warning('Multiple index not supported')
                idx_stmts, idx_string, local_var = decipher_expression(
                        pr_id['index'][0])
                if unicode.isnumeric(idx_string):
                    idx_string = eval(idx_string + '+1')
                else:
                    idx_string = '1+({idx})'.format(idx=idx_string)
                ada_string += '.Data({idx})'.format(idx=idx_string)
                stmts.extend(idx_stmts)
                local_decl.extend(local_var)
            elif 'procParams' in pr_id:
                if special_op == 'Length':
                    # Length of sequence of: take only the first parameter
                    exp, = pr_id['procParams']
                    exp_type = find_basic_type(exp.exprType)
                    min_length = exp_type.get('Min')
                    max_length = exp_type.get('Max')
                    if min_length is None or max_length is None:
                        error = '{} is not a SEQUENCE OF'.format(
                                exp.inputString)
                        LOG.error(error)
                        raise TypeError(error)
                    param_stmts, param_str, local_var = decipher_expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    if min_length == max_length:
                        ada_string += min_length
                    else:
                        ada_string += ('Interfaces.Integer_64({e}.Length)'
                                .format(e=param_str))
                elif special_op == 'ChoiceKind':
                    # User wants to know what CHOICE element is present
                    exp, = pr_id['procParams']
                    # Get the basic type to make sure it is a choice
                    exp_type = find_basic_type(exp.exprType)
                    # Also get the ASN.1 type name as it is
                    # needed to build the Ada expression
                    # (Won't work for embedded types - FIXME)
                    exp_typename = (exp.exprType.get('ReferencedTypeName') or
                            exp.exprType['Kind'])
                    if exp_type['Kind'] != 'ChoiceType':
                        error = '{} is not a CHOICE'.format(exp.inputString)
                        LOG.error(error)
                        raise TypeError(error)
                    param_stmts, param_str, local_var = decipher_expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    ada_string += ('asn1Scc{t}_Kind({e})'.format(
                        t=exp_typename, e=param_str))
                else:
                    ada_string += '('
                    # Take all params and join them with commas
                    list_of_params = []
                    for param in pr_id['procParams']:
                        param_stmt, param_str, local_var = (
                                decipher_expression(param))
                        list_of_params.append(param_str)
                        stmts.extend(param_stmt)
                        local_decl.extend(local_var)
                    ada_string += ', '.join(list_of_params)
                    ada_string += ')'
        sep = '.'
    return stmts, ada_string, local_decl


def decipher_expression(expr):
    ''' Return a set of statements and an Ada string for an expression '''
    stmts = []
    ada_string = ''
    local_decl = []
    if expr.kind == 'primary':
        if (expr.var.primType == None
                or expr.var.primType['Kind'] != 'ReferenceType'):
            # Populate the expression type to the field if it was not set
            # It can be the case if the type definition is embedded
            # in a SEQUENCE - in that case the ASN.1 compiler creates an
            # intermediate type by concatenating field names.
            expr.var.primType = expr.exprType
        prim_stmts, ada_string, local_var = decipher_primary(expr.var)
        stmts.extend(prim_stmts)
        local_decl.extend(local_var)
    elif expr.kind in ('plus', 'mul', 'minus', 'or', 'and', 'xor', 'eq',
            'neq', 'gt', 'ge', 'lt', 'le', 'div', 'mod'):
        left_stmts, left_str, left_local = decipher_expression(expr.left)
        right_stmts, right_str, right_local = decipher_expression(expr.right)
        ada_string = '({left} {op} {right})'.format(
                left=left_str, op=OPERANDS[expr.kind], right=right_str)
        stmts.extend(left_stmts)
        stmts.extend(right_stmts)
        local_decl.extend(left_local)
        local_decl.extend(right_local)
    elif expr.kind == 'append':
        # TODO (Append item to a list)
        pass
    elif expr.kind == 'in':
        # TODO (Check if item is in a list/set)
        pass
    elif expr.kind == 'rem':
        # TODO (Remove item from a set?)
        pass
    else:
        raise ValueError('unsupported expression kind: ' + expr.kind)
    return stmts, ada_string, local_decl


def decipher_primary(primary):
    ''' Return Ada string for a Primary '''
    stmts = []
    ada_string = ''
    local_decl = []
    if primary.kind == 'primaryId':
        stmts, ada_string, local_decl = decipher_primary_id(primary.primaryId)
    elif primary.kind == 'enumeratedValue':
        # (note: in C we would need to read EnumID in the type definition)
        ada_string = 'asn1Scc{enumVal}'.format(enumVal=primary.primaryId[0])
    elif primary.kind == 'choiceDeterminant':
        ada_string = '{choice}_PRESENT'.format(choice=primary.primaryId[0])
    elif primary.kind in ('numericalValue', 'booleanValue'):
        ada_string = primary.primaryId[0]
    elif primary.kind == 'sequence':
        stmts, ada_string, local_decl = decipher_sequence(
                primary.sequence, primary.primType)
    elif primary.kind == 'sequenceOf':
        stmts, ada_string, local_decl = decipher_sequence_of(
                primary.sequenceOf, primary.primType)
    elif primary.kind == 'choiceItem':
        stmts, ada_string, local_decl = decipher_choice(
                primary.choiceItem, primary.primType)
    elif primary.kind == 'emptyString':
        ada_string = 'asn1Scc{typeRef}_Init'.format(
                typeRef=primary.primType['ReferencedTypeName'])
    elif primary.kind == 'stringLiteral':
        pass
    elif primary.kind == 'ifThenElse':
        stmts, ada_string, local_decl = decipher_if_then_else(
                primary.ifThenElse, primary.primType)
    elif primary.kind == 'expression':
        stmts, ada_string, local_decl = decipher_expression(primary.expr)
    elif primary.kind == 'mantissaBaseExpFloat':
        pass
    else:
        raise ValueError('unsupported primary kind: ' + primary.kind)
    return stmts, ada_string, local_decl


def decipher_if_then_else(ifThenElse, resType):
    ''' Return string and statements for ternary operator '''
    stmts = []
    # FIXME: resType may be wrong if declaration embedded in SEQUENCE
    # TODO: find a non-conflicing naming convention for tmp variable
    local_decl = ['tmp{idx} : asn1Scc{resType};'.format(
        idx=ifThenElse['tmpVar'], resType=resType.get('ReferencedTypeName') or
        'ERROR!')]
    if_stmts, if_str, if_local = decipher_expression(ifThenElse['if'])
    then_stmts, then_str, then_local = decipher_expression(ifThenElse['then'])
    else_stmts, else_str, else_local = decipher_expression(ifThenElse['else'])
    stmts.extend(if_stmts)
    stmts.extend(then_stmts)
    stmts.extend(else_stmts)
    local_decl.extend(if_local)
    local_decl.extend(then_local)
    local_decl.extend(else_local)
    stmts.append('if {if_str} then'.format(
        if_str=if_str))
    stmts.append('tmp{idx} := {then_str};'.format(
        idx=ifThenElse['tmpVar'], then_str=then_str))
    stmts.append('else')
    stmts.append('tmp{idx} := {else_str};'.format(
        idx=ifThenElse['tmpVar'], else_str=else_str))
    stmts.append('end if;')
    ada_string = 'tmp{idx}'.format(idx=ifThenElse['tmpVar'])
    return stmts, ada_string, local_decl


def decipher_sequence(seq, seqType):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    LOG.debug('Sequence: ' + str(seq) + str(seqType))
    ada_string = 'asn1Scc{seqType}\'('.format(
            seqType=seqType['ReferencedTypeName'])
    stmts = []
    local_decl = []
    sep = ''
    for elem, value in seq.viewitems():
        if value.exprType['Kind'] == 'UnknownType':
            # Type may be unknown if it is an unnamed embedded type
            # In that case, build up the type name by appending
            # the last known type with the field name
            value.exprType['Kind'] = 'ReferenceType'
            value.exprType['ReferencedTypeName'] = '{thisType}_{elem}'.format(
                    thisType=seqType['ReferencedTypeName'], elem=elem)
        value_stmts, value_str, local_var = decipher_expression(value)
        ada_string += sep + elem + ' => ' + value_str
        sep = ', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    ada_string += ')'
    return stmts, ada_string, local_decl


def decipher_sequence_of(seqof, seqofType):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    stmts = []
    local_decl = []
    typename = seqofType.get('ReferencedTypeName')
    LOG.debug('SequenceOf Typename:' + str(typename))
    asn_type = TYPES[typename]['type']
    min_size = asn_type['Min']
    max_size = asn_type['Max']
    ada_string = 'asn1Scc{seqofType}\'('.format(seqofType=typename)
    if min_size == max_size:
        # Fixed-length array - no need to set the Length field
        ada_string += 'Data => asn1Scc{seqofType}_array\'('.format(
                seqofType=typename)
    else:
        # Variable-length array
        ada_string += (
                'Length => {length}, Data => asn1Scc{seqofType}_array\'('
                .format(seqofType=typename, length=len(seqof)))
    for i in xrange(len(seqof)):
        if seqof[i].primType is None:
            # Embedded type (e.g. SEQUENCE OF SEQUENCE {...}):
            # asn1Scc creates an intermediate type suffixed with _elm:
            seqof[i].primType = {'Kind': 'ReferenceType',
                    'ReferencedTypeName': '{baseType}_elm'.
                    format(baseType=typename)}
        item_stmts, item_str, local_var = decipher_primary(seqof[i])
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        ada_string += '{i} => {value}, '.format(i=i + 1, value=item_str)
    ada_string += 'others => {anyVal}))'.format(anyVal=item_str)
    return stmts, ada_string, local_decl


def decipher_choice(choice, choiceType):
    ''' Return the Ada code for a CHOICE expression '''
    if choice['value'].exprType['Kind'] == 'UnknownType':
        # To handle non-explicit type definition (e.g CHOICE { a SEQUENCE...)
        choice['value'].exprType = {'Kind': 'ReferenceType',
                'ReferencedTypeName': '{baseType}_{choiceValue}'.format(
                    baseType=choiceType.get('ReferencedTypeName'),
                    choiceValue=choice['choice'])}

    stmts, choice_str, local_decl = decipher_expression(choice['value'])

    ada_string = 'asn1Scc{cType}_{opt}_set({expr})'.format(
            cType=choiceType.get('ReferencedTypeName') or choiceType['Kind'],
            opt=choice['choice'],
            expr=choice_str)
    return stmts, ada_string, local_decl


def decision_statement(dec):
    ''' generate the code for a decision '''
    code = []
    local_decl = []
    question_type = dec.question.exprType
    # Here is how to get properly the type (except when embedded in a sequence)
    # TODO fix the FIXMEs with that pattern:
    actual_type = question_type.get(
            'ReferencedTypeName') or question_type['Kind']
    actual_type = actual_type.replace('-', '_')
    basic = False
    if actual_type in ('IntegerType', 'BooleanType',
            'RealType', 'EnumeratedType'):
        basic = True
    # for ASN.1 types, declare a local variable
    # to hold the evaluation of the question
    if not basic:
        local_decl.append('tmp{idx} : asn1Scc{actType};'.format(
            idx=dec.tmpVar, actType=actual_type))
    q_stmts, q_str, q_decl = decipher_expression(dec.question)
    # Add code-to-model traceability
    code.extend(traceability(dec))
    local_decl.extend(q_decl)
    code.extend(q_stmts)
    if not basic:
        code.append('tmp{idx} := {q};'.format(idx=dec.tmpVar, q=q_str))
    sep = 'if '
    for a in dec.answers:
        if a.kind == 'constant':
            a.kind = 'open_range'
            a.openRangeOp = 'eq'
        if a.kind == 'open_range' and a.transition:
            ans_stmts, ans_str, ans_decl = decipher_expression(a.constant)
            code.extend(ans_stmts)
            local_decl.extend(ans_decl)
            if not basic:
                if a.openRangeOp in ('eq', 'neq'):
                    exp = 'asn1Scc{actType}_Equal(tmp{idx}, {ans})'.format(
                            actType=actual_type, idx=dec.tmpVar, ans=ans_str)
                    if a.openRangeOp == 'neq':
                        exp = 'not ' + exp
                else:
                    exp = 'tmp{idx} {op} {ans}'.format(idx=dec.tmpVar,
                            op=OPERANDS[a.openRangeOp], ans=ans_str)
            else:
                exp = '{q} {op} {ans}'.format(q=q_str,
                        op=OPERANDS[a.openRangeOp], ans=ans_str)
            code.append(sep + exp + ' then')
            stmt, tr_decl = transition(a.transition)
            code.extend(stmt)
            local_decl.extend(tr_decl)
            sep = 'elsif '
        elif a.kind == 'close_range' and a.transition:
            sep = 'elsif '
            # TODO support close_range
        elif a.kind == 'informal_text':
            continue
        elif a.kind == 'else' and a.transition:
            # Keep the ELSE statement for the end
            else_code, else_decl = transition(a.transition)
            local_decl.extend(else_decl)
    try:
        if sep != 'if ':
            # If there is at least one 'if' branch
            else_code.insert(0, 'else')
            code.extend(else_code)
        else:
            code.extend(else_code)
    except:
        pass
    if sep != 'if ':
        # If there is at least one 'if' branch
        code.append('end if;')
    return code, local_decl


def transition(tr):
    ''' generate the code for a transition '''
    code = []
    local_decl = []
    for action in tr.actions:
        if isinstance(action, ogAST.Output):
            stmt, local_var = output_statement(action)
        elif isinstance(action, ogAST.Task):
            stmt, local_var = task_statement(action)
        elif isinstance(action, ogAST.Decision):
            stmt, local_var = decision_statement(action)
        elif isinstance(action, ogAST.Label):
            stmt = ['<<{label}>>'.format(
                label=action.inputString)]
            local_var = []
        code.extend(stmt)
        local_decl.extend(local_var)
    if tr.terminator:
        code.extend(traceability(tr.terminator))
        if tr.terminator.label:
            code.append('<<{label}>>'.format(
                label=tr.terminator.label.inputString))
        if(tr.terminator.kind == 'next_state' and
                tr.terminator.inputString.strip() != '-'):
            # discard the "-" state (remain in the same state)
            code.append('state := {nextState};'.format(
                nextState=tr.terminator.inputString))
            code.append('return;')
        elif tr.terminator.kind == 'join':
            code.append('goto {label};'.format(
                label=tr.terminator.inputString))
        elif tr.terminator.kind == 'stop':
            pass
            # TODO
    return code, local_decl


def format_ada_code(stmts):
    ''' Indent properly the Ada code '''
    indent = 0
    indent_pattern = '    '
    for line in stmts[:-1]:
        elems = line.strip().split()
        if elems and elems[0] in ('when', 'end', 'elsif', 'else'):
            indent = max(indent - 1, 0)
        if elems and elems[-1] == 'case;':
            indent = max(indent - 1, 0)
        yield indent_pattern * indent + line
        if elems and elems[-1] in ('is', 'then'):
            indent += 1
        if elems and elems[0] in ('begin', 'case', 'else', 'when'):
            indent += 1
        if not elems:
            indent -= 1
    yield stmts[-1]


def generate(process):
    ''' Generate Ada code '''
    process_name = process.processName
    global VARIABLES
    VARIABLES = process.variables
    global TYPES
    TYPES = process.dataView
    global OUT_SIGNALS
    global PROCEDURES
    # Ada is case insensitive => lower cases
    OUT_SIGNALS = {sig.lower(): defn for sig, defn in
            process.outputSignals.viewitems()}
    PROCEDURES = {p.lower(): defn for p, defn in
            process.procedures.viewitems()}
    filename = process_name + ".adb"
    LOG.info('Generating Ada code for process' + str(process_name))

    # Generate the code to declare process-level variables
    process_level_decl = []
    for var_name, var_type in VARIABLES.iteritems():
        process_level_decl.append('l_{n} : asn1Scc{t};'.format(
            n=var_name, t=var_type))

    # Add the process states list to the process-level variables
    states_decl = 'type states is ('
    states_decl += ', '.join(process.mapping.iterkeys()) + ');'
    process_level_decl.append(states_decl)
    process_level_decl.append('state : states := START;')

    # Add the declaration of the runTransition procedure
    process_level_decl.append('procedure runTransition(trId: Integer);')

    # Generate the code of the start transition:
    start_transition = ['begin']
    start_transition.append('runTransition(0);')

    mapping = {}
    # Generate the code for the transitions in a mapping input-state
    for input_signal in process.inputSignals.viewkeys():
        mapping[input_signal] = {}
        for state_name, input_symbols in process.mapping.viewitems():
            if state_name != 'START':
                for i in input_symbols:
                    if input_signal.lower() in (inp.lower() for
                                               inp in i.inputlist):
                        mapping[input_signal][state_name] = i

    # Generate the TASTE template
    asn1_modules = '\n'.join(['with {dv};\nuse {dv};'.format(
        dv=dv.replace('-', '_'))
        for dv in process.asn1Modules])
    taste_template = ['''with System.IO;
use System.IO;

{dataview}

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body {process_name} is'''.format(process_name=process_name,
    dataview=asn1_modules)]

    # Generate the code for the process-level variable declarations
    taste_template.extend(process_level_decl)

    # Generate the code for each input signal (provided interface)
    for sig_name, sig_def in process.inputSignals.viewitems():
        if sig_name == 'START':
            continue
        pi_header = 'procedure {sig_name}'.format(sig_name=sig_name)
        if sig_def['in']:
            param_name = sig_def['in'].keys()[0]
            # Add PI parameter (only one is possible in TASTE PI)
            pi_header += '({pName}: access asn1Scc{pType})'.format(
                    pName=param_name, pType=sig_def['in'][param_name]['type'])
        pi_header += ' is'
        taste_template.append(pi_header)
        taste_template.append('begin')
        taste_template.append('case state is')
        for state in process.mapping.viewkeys():
            if state == 'START':
                continue
            taste_template.append('when {state} =>'.format(state=state))
            input_def = mapping[sig_name].get(state)
            if input_def:
                for inp in input_def.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    taste_template.append('l_{inp} := {tInp}.all;'.format(
                        inp=inp, tInp=sig_def['in'].keys()[0]))
                # Execute the correponding transition
                if input_def.transition:
                    taste_template.append('runTransition({t});'.format(
                        t=input_def.inputlist[sig_name]))
                else:
                    taste_template.append('null;')
            else:
                taste_template.append('null;')
        taste_template.append('when others =>')
        taste_template.append('null;')
        taste_template.append('end case;')
        taste_template.append('end {sig_name};'.format(sig_name=sig_name))
        taste_template.append('\n')

    taste_template.append('procedure runTransition(trId: Integer) is')

    # Generate the code for all transitions
    code_transitions = []
    local_decl_transitions = []
    for proc_tr in process.transitions:
        code_tr, tr_local_decl = transition(proc_tr)
        code_transitions.append(code_tr)
        local_decl_transitions.extend(tr_local_decl)

    # Declare the local variables needed by the transitions in the template
    decl = ['{line}'.format(line=l)
            for l in local_decl_transitions]
    taste_template.extend(decl)
    taste_template.append('begin')

    # Generate the switch-case on the transition id
    taste_template.append('case trId is')

    for idx, val in enumerate(code_transitions):
        taste_template.append('when {idx} =>'.format(idx=idx))
        val = ['{line}'.format(line=l) for l in val]
        if val:
            taste_template.extend(val)
        else:
            taste_template.append('null;')

    taste_template.append('when others =>')
    taste_template.append('null;')

    taste_template.append('end case;')
    taste_template.append('end runTransition;')
    taste_template.append('\n')

    taste_template.extend(start_transition)
    taste_template.append('end {process_name};'
            .format(process_name=process_name))

    with open(filename, 'w') as ada_file:
        ada_file.write('\n'.join(format_ada_code(taste_template)))
