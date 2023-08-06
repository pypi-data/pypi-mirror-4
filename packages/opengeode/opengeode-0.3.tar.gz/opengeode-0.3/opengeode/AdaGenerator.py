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
                print '** INCOMPLETE FEATURE !ID=', identifier[index]
            kind = current_type['Kind']
    return kind, name


def traceability(symbol):
    ''' Return a string with code-to-model traceability '''
    trace = ['-- {line}'.format(line=l) for l in
        repr(symbol).split('\n')]
    if hasattr(symbol, 'comment') and symbol.comment:
        trace.extend(traceability(symbol.comment))
    return trace


def output_statement(output):
    ''' Generate the code of a set of output or procedure call statement '''
    code = []
    local_decl = []

    # Add the traceability information
    code.extend(traceability(output))

    for o in output.output:
        signal_name = o['outputName']

        if signal_name.lower() in ('write', 'writeln'):
            # special built-in SDL procedure for printing strings
            # TODO = decipherWrite function that prints any ASN.1 value
            for p in o['params']:
                code.append('{put}("{string}");'.format(
                    put='Put' if signal_name.lower() == 'write'
                    else 'Put_Line',
                    string=p.inputString[1:-1]))
            continue
        if output.kind == 'output':
            out_sig = OUT_SIGNALS.get(signal_name.lower())
        else:
            out_sig = PROCEDURES.get(signal_name.lower())
        if not out_sig:
            print '[ERROR] Signal or procedure not defined:', signal_name
            return [], []
        nb_in_params = len(out_sig['paramsInOrdered'])
        listofParams = []
        for idx, p in enumerate(o.get('params') or []):
            # Determine if it is an IN or OUT type
            select = ('paramsOutOrdered', 'out', idx - nb_in_params) if (
                    idx >= nb_in_params) else ('paramsInOrdered', 'in', idx)

            # Get parameter name and type from the Interface view:
            paramName = out_sig[select[0]][select[2]]
            paramType = out_sig[select[1]][paramName]['type']

            # Check the type of the parameter - set it if missing
            # (TODO: do it in the parser)
            if p.exprType.get('Kind') == 'UnknownType':
                p.exprType = {'Kind': 'ReferenceType',
                        'ReferencedTypeName': paramType}

            pCode, pId, pLocal = decipher_expression(p)
            code.extend(pCode)
            local_decl.extend(pLocal)
            # Create a temporary variable for this parameter
            tmpId = o['tmpVars'][idx]
            # print tmpId, paramName, paramType
            local_decl.append('tmp{idx} : aliased asn1Scc{oType};'.format(
                idx=tmpId, oType=paramType))
            code.append('tmp{idx} := {pId};'.format(
                idx=tmpId, pId=pId))
            listofParams.append("tmp{idx}'access".
                    format(idx=o['tmpVars'][idx]))
        if listofParams:
            code.append('{RI}({params});'.format(
                RI=o['outputName'], params=', '.join(listofParams)))
            # Assign back the out parameters to the local variables
            if len(out_sig['paramsOutOrdered']) > 0:
                for (idx, p) in ((idx, p)
                        for idx, p in enumerate(o['params'])
                        if idx >= nb_in_params):
                    _, pId, __ = decipher_expression(p)
                    code.append('{pId} := tmp{idx};'.format(
                        pId=pId, idx=o['tmpVars'][idx]))
        else:
            code.append('{RI};'.format(RI=o['outputName']))
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
        for t in task.informalText:
            code.append('--  ' + t.replace('\n', '\n' + '--  '))
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
            assignStr = left_str + ' := ' + right_str + ';'
            code.extend(left_stmts)
            code.extend(right_stmts)
            local_decl.extend(left_local)
            local_decl.extend(right_local)
            code.append(assignStr)
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
    subId = []
    for pr_id in primaryId:
        if type(pr_id) is not dict:
            if pr_id.lower() == 'length':
                special_op = 'Length'
                continue
            elif pr_id.lower() == 'present':
                special_op = 'ChoiceKind'
                continue
            special_op = ''
            subId.append(pr_id)
            parentKind, parentTypeName = get_type_of_parent(subId)
            if parentKind == 'ChoiceType':
                ada_string = ('asn1Scc{typename}_{pid}_get({ada_string})'
                        .format(typename=parentTypeName, pid=pr_id,
                        ada_string=ada_string))
            else:
                ada_string += sep + pr_id
        else:
            # index is a LIST - only taking 1st elem.
            if 'index' in pr_id:
                if len(pr_id['index']) > 1:
                    print('[WARNING] multiple index not supported')
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
                    minLength = exp_type.get('Min')
                    maxLength = exp_type.get('Max')
                    if minLength is None or maxLength is None:
                        print('[ERROR] Expression {e} is not a SEQUENCE OF'
                                .format(e=exp.inputString))
                        # TODO: raise exception
                        break
                    param_stmts, paramString, local_var = decipher_expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    if minLength == maxLength:
                        ada_string += minLength
                    else:
                        ada_string += ('Interfaces.Integer_64({e}.Length)'
                                .format(e=paramString))
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
                        print('[ERROR] {e} is not a CHOICE'
                                .format(e=exp.inputString))
                        break
                        # TODO raise exception rather than a print
                    param_stmts, paramString, local_var = decipher_expression(
                            exp)
                    stmts.extend(param_stmts)
                    local_decl.extend(local_var)
                    ada_string += ('asn1Scc{t}_Kind({e})'.format(
                        t=exp_typename, e=paramString))
                else:
                    ada_string += '('
                    # Take all params and join them with commas
                    listOfParams = []
                    for p in pr_id['procParams']:
                        param_stmt, paramString, local_var = (
                                decipher_expression(p))
                        listOfParams.append(paramString)
                        stmts.extend(param_stmt)
                        local_decl.extend(local_var)
                    ada_string += ', '.join(listOfParams)
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
            #print 'We set this:', expr.exprType
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
        stmts, ada_string, local_decl = decipherSequence(
                primary.sequence, primary.primType)
    elif primary.kind == 'sequenceOf':
        stmts, ada_string, local_decl = decipherSequenceOf(
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
        stmts, ada_string, local_decl = decipherIfThenElse(
                primary.ifThenElse, primary.primType)
    elif primary.kind == 'expression':
        stmts, ada_string, local_decl = decipher_expression(primary.expr)
    elif primary.kind == 'mantissaBaseExpFloat':
        pass
    else:
        raise ValueError('unsupported primary kind: ' + primary.kind)
    return stmts, ada_string, local_decl


def decipherIfThenElse(ifThenElse, resType):
    ''' Return string and statements for ternary operator '''
    stmts = []
    # FIXME: resType may be wrong if declaration embedded in SEQUENCE
    # TODO: find a non-conflicing naming convention for tmp variable
    local_decl = ['tmp{idx} : asn1Scc{resType};'.format(
        idx=ifThenElse['tmpVar'], resType=resType['ReferencedTypeName'])]
    if_stmts, ifString, ifLocal = decipher_expression(ifThenElse['if'])
    then_stmts, thenString, thenLocal = decipher_expression(ifThenElse['then'])
    else_stmts, elseString, elseLocal = decipher_expression(ifThenElse['else'])
    stmts.extend(if_stmts)
    stmts.extend(then_stmts)
    stmts.extend(else_stmts)
    local_decl.extend(ifLocal)
    local_decl.extend(thenLocal)
    local_decl.extend(elseLocal)
    stmts.append('if {ifString} then'.format(
        ifString=ifString))
    stmts.append('tmp{idx} := {thenString};'.format(
        idx=ifThenElse['tmpVar'], thenString=thenString))
    stmts.append('else')
    stmts.append('tmp{idx} := {elseString};'.format(
        idx=ifThenElse['tmpVar'], elseString=elseString))
    stmts.append('end if;')
    ada_string = 'tmp{idx}'.format(idx=ifThenElse['tmpVar'])
    return stmts, ada_string, local_decl


def decipherSequence(seq, seqType):
    ''' Return Ada string for an ASN.1 SEQUENCE '''
    #print '[DEBUG] Sequence:', seq, seqType
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
        value_stmts, valueStr, local_var = decipher_expression(value)
        ada_string += sep + elem + ' => ' + valueStr
        sep = ', '
        stmts.extend(value_stmts)
        local_decl.extend(local_var)
    ada_string += ')'
    return stmts, ada_string, local_decl


def decipherSequenceOf(seqof, seqofType):
    ''' Return Ada string for an ASN.1 SEQUENCE OF '''
    stmts = []
    local_decl = []
    typename = seqofType.get('ReferencedTypeName')
    #print '[DEBUG] SequenceOf Typename:', typename
    asnType = TYPES[typename]['type']
    minSize = asnType['Min']
    maxSize = asnType['Max']
    ada_string = 'asn1Scc{seqofType}\'('.format(seqofType=typename)
    if minSize == maxSize:
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
        item_stmts, itemStr, local_var = decipher_primary(seqof[i])
        stmts.extend(item_stmts)
        local_decl.extend(local_var)
        ada_string += '{i} => {value}, '.format(i=i + 1, value=itemStr)
    ada_string += 'others => {anyVal}))'.format(anyVal=itemStr)
    return stmts, ada_string, local_decl


def decipher_choice(choice, choiceType):
    ''' Return the Ada code for a CHOICE expression '''
    if choice['value'].exprType['Kind'] == 'UnknownType':
        # To handle non-explicit type definition (e.g CHOICE { a SEQUENCE...)
        choice['value'].exprType = {'Kind': 'ReferenceType',
        'ReferencedTypeName': '{baseType}_{choiceValue}'.format(
            baseType=choiceType.get('ReferencedTypeName'),
            choiceValue=choice['choice'])}

    stmts, choiceStr, local_decl = decipher_expression(choice['value'])

    ada_string = 'asn1Scc{cType}_{opt}_set({expr})'.format(
            cType=choiceType.get('ReferencedTypeName') or choiceType['Kind'],
            opt=choice['choice'],
            expr=choiceStr)
    return stmts, ada_string, local_decl


def decision_statement(dec):
    ''' generate the code for a decision '''
    code = []
    local_decl = []
    questionType = dec.question.exprType
    # Here is how to get properly the type (except when embedded in a sequence)
    # TODO fix the FIXMEs with that pattern:
    actual_type = questionType.get(
            'ReferencedTypeName') or questionType['Kind']
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
    q_stmts, qStr, qDecl = decipher_expression(dec.question)
    # Add code-to-model traceability
    code.extend(traceability(dec))
    local_decl.extend(qDecl)
    code.extend(q_stmts)
    if not basic:
        code.append('tmp{idx} := {q};'.format(idx=dec.tmpVar, q=qStr))
    sep = 'if '
    for a in dec.answers:
        if a.kind == 'constant':
            a.kind = 'open_range'
            a.openRangeOp = 'eq'
        if a.kind == 'open_range' and a.transition:
            ans_stmts, ansStr, ansDecl = decipher_expression(a.constant)
            code.extend(ans_stmts)
            local_decl.extend(ansDecl)
            if not basic:
                if a.openRangeOp in ('eq', 'neq'):
                    exp = 'asn1Scc{actType}_Equal(tmp{idx}, {ans})'.format(
                            actType=actual_type, idx=dec.tmpVar, ans=ansStr)
                    if a.openRangeOp == 'neq':
                        exp = 'not ' + exp
                else:
                    exp = 'tmp{idx} {op} {ans}'.format(idx=dec.tmpVar,
                            op=OPERANDS[a.openRangeOp], ans=ansStr)
            else:
                exp = '{q} {op} {ans}'.format(q=qStr,
                        op=OPERANDS[a.openRangeOp], ans=ansStr)
            code.append(sep + exp + ' then')
            stmt, trDecl = transition(a.transition)
            code.extend(stmt)
            local_decl.extend(trDecl)
            sep = 'elsif '
        elif a.kind == 'close_range' and a.transition:
            sep = 'elsif '
            # TODO support close_range
        elif a.kind == 'informal_text':
            continue
        elif a.kind == 'else' and a.transition:
            # Keep the ELSE statement for the end
            elseCode, elseDecl = transition(a.transition)
            local_decl.extend(elseDecl)
    try:
        if sep != 'if ':
            # If there is at least one 'if' branch
            # elseCode = ['    ' + c for c in elseCode]
            elseCode.insert(0, 'else')
            code.extend(elseCode)
        else:
            code.extend(elseCode)
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
        if tr.terminator.label:
            code.append('<<{label}>>'.format(
                label=tr.terminator.label.inputString))
        if tr.terminator.kind == 'next_state':
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
    processName = process.processName
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
    fileName = processName + ".adb"
    print 'Generating Ada code for process', processName

    # Generate the code to declare process-level variables
    processLevelDecl = []
    for varName, varType in VARIABLES.iteritems():
        processLevelDecl.append('l_{n} : asn1Scc{t};'.format(
            n=varName, t=varType))

    # Add the process states list to the process-level variables
    statesDecl = 'type states is ('
    statesDecl += ', '.join(process.mapping.iterkeys()) + ');'
    processLevelDecl.append(statesDecl)
    processLevelDecl.append('state : states := START;')

    # Add the declaration of the runTransition procedure
    processLevelDecl.append('procedure runTransition(trId: Integer);')

    # Generate the code of the start transition:
    startTransition = ['begin']
    startTransition.append('runTransition(0);')

    mapping = {}
    # Generate the code for the transitions in a mapping input-state
    for inputSignal in process.inputSignals.viewkeys():
        mapping[inputSignal] = {}
        for stateName, inputSymbols in process.mapping.viewitems():
            if stateName != 'START':
                for i in inputSymbols:
                    if inputSignal.lower() in [inp.lower() for
                                               inp in i.inputlist]:
                        mapping[inputSignal][stateName] = i

    # Generate the TASTE template
    asn1Modules = '\n'.join(['with {dv};\nuse {dv};'.format(
        dv=dv.replace('-', '_'))
        for dv in process.asn1Modules])
    taste_template = ['''with System.IO;
use System.IO;

{dataview}

with adaasn1rtl;
use adaasn1rtl;

with Interfaces;
use Interfaces;

package body {processName} is'''.format(processName=processName,
    dataview=asn1Modules)]

    # Generate the code for the process-level variable declarations
    taste_template.extend(processLevelDecl)

    # Generate the code for each input signal (provided interface)
    for sName, sDef in process.inputSignals.viewitems():
        if sName == 'START':
            continue
        pi_header = 'procedure {sName}'.format(sName=sName)
        if sDef['in']:
            paramName = sDef['in'].keys()[0]
            # Add PI parameter (only one is possible in TASTE PI)
            pi_header += '({pName}: access asn1Scc{pType})'.format(
                    pName=paramName, pType=sDef['in'][paramName]['type'])
        pi_header += ' is'
        taste_template.append(pi_header)
        taste_template.append('begin')
        taste_template.append('case state is')
        for state in process.mapping.viewkeys():
            if state == 'START':
                continue
            taste_template.append('when {state} =>'.format(state=state))
            inputDef = mapping[sName].get(state)
            if inputDef:
                for inp in inputDef.parameters:
                    # Assign the (optional and unique) parameter
                    # to the corresponding process variable
                    taste_template.append('l_{inp} := {tInp}.all;'.format(
                        inp=inp, tInp=sDef['in'].keys()[0]))
                # Execute the correponding transition
                if inputDef.transition:
                    taste_template.append('runTransition({t});'.format(
                        t=inputDef.inputlist[sName]))
                else:
                    taste_template.append('null;')
            else:
                taste_template.append('null;')
        taste_template.append('when others =>')
        taste_template.append('null;')
        taste_template.append('end case;')
        taste_template.append('end {sName};'.format(sName=sName))
        taste_template.append('\n')

    taste_template.append('procedure runTransition(trId: Integer) is')

    # Generate the code for all transitions
    codeTransitions = []
    local_declTransitions = []
    for t in process.transitions:
        codeTr, trLocalDecl = transition(t)
        codeTransitions.append(codeTr)
        local_declTransitions.extend(trLocalDecl)

    # Declare the local variables needed by the transitions in the template
    decl = ['{line}'.format(line=l)
            for l in local_declTransitions]
    taste_template.extend(decl)
    taste_template.append('begin')

    # Generate the switch-case on the transition id
    taste_template.append('case trId is')

    for idx, val in enumerate(codeTransitions):
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

    taste_template.extend(startTransition)
    taste_template.append('end {processName};'.format(processName=processName))

    with open(fileName, 'w') as f:
        f.write('\n'.join(format_ada_code(taste_template)))
