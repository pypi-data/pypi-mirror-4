#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
    OpenGEODE SDL92 parser

    This library builds the SDL AST (described in ogAST.py)
    The AST can then be used to build SDL backends such as the
    diagram editor (placing symbols in a graphical canvas for editition)
    or code generators, etc.

    The AST build is based on the ANTLR-grammar and generated lexer and parser
    (the grammar is in the file sdl92.g and requires antlr 3.1.3 for Python
    to be compiled and used).

    During the build of the AST this library makes a number of semantic
    checks on the SDL input mode.

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__author__ = 'Maxime Perrotin'

import sys
import os
import antlr3
import antlr3.tree
import importlib

from sdl92Lexer import(sdl92Lexer, PLUS, STATE, STATELIST, INT, ID, PARAMS,
        FIELD_NAME, NOT, MINUS, PRIMARY_ID, ASTERISK, DASH, APPEND, IMPLIES,
        OR, XOR, AND, EQ, NEQ, GT, GE, LT, LE, DIV, MOD, REM, IN, PRIMARY,
        SORT, GROUND, CIF, VARIABLES, DCL, START, NUMBER_OF_INSTANCES,
        INPUTLIST, PROVIDED, TRANSITION, INPUT, PROCEDURE_CALL, TASK, OUTPUT,
        OUTPUT_BODY, DECISION, TERMINATOR, VARIABLE, ASSIGN, INFORMAL_TEXT,
        TEXTAREA, TEXTAREA_CONTENT, TASK_BODY, QUESTION, ELSE, ANY, ANSWER,
        CONSTANT, CLOSED_RANGE, OPEN_RANGE, NEXTSTATE, JOIN, STOP, ENDTEXT,
        EXPRESSION, CHOICE, SEQUENCE, SEQOF, EMPTYSTR, FLOAT, FLOAT2, BITSTR,
        OCTSTR, STRING, IFTHENELSE, TRUE, FALSE, COMMENT, StringLiteral,
        HYPERLINK, LABEL)

from sdl92Parser import sdl92Parser

from ogAST import(Expression, Primary, Decision, Answer, Task, Transition,
        Output, Process, State, Input, Terminator, Start, TextArea, Comment,
        Label)

import samnmax

Kind = {PLUS: 'plus', ASTERISK: 'mul', DASH: 'minus', OR: 'or', AND: 'and',
        XOR: 'xor', EQ: 'eq', NEQ: 'neq', GT: 'gt', GE: 'ge', LT: 'lt',
        LE: 'le', DIV: 'div', MOD: 'mod', APPEND: 'append', IN: 'in',
        REM: 'rem', PRIMARY: 'primary'}

# Insert current path in the search list for importing modules
sys.path.insert(0, '.')

errors = []
warnings = []
dataView = None
iv = None
dv = None

# Code generator backends may need some intemediate variables to process
# expressions. For convenience and to avoid multiple pass parsing, the parser
# tries to guess where they may be useful, and adds a hint in the AST.
tmpVar = 0

# Special SDL operators
special_operators = {'length': {'type': {'Kind': 'IntegerType'},
    'paramsInOrdered': ['seqof_ref'], 'paramsOutOrdered': [],
    'in': {'seqof_ref': {'type': '_SEQOF'}}},
    'present': {'type': {'Kind': 'EnumeratedType', 'extraAttr': 'presentKind',
        'EnumValues': {}},
    'paramsInOrdered': ['choice_ref'], 'paramsOutOrdered': [],
    'in': {'choice_ref': {'type': '_CHOICE'}}}}


def getInputString(root):
    ''' Return the input string of a tree node '''
    return tokens.toString(root.getTokenStartIndex(),
            root.getTokenStopIndex())


def getStateList(processRoot):
    ''' Return the list of states of the whole process '''
    # 1) get all STATE statements
    states = (child for child in processRoot.getChildren()
            if child.type == STATE)
    # 2) keep only the ones containing a STATELIST token (i.e. no ASTERISK)
    relevant = (child for state in states for child in state.getChildren()
            if child.type == STATELIST)
    # 3) extract the state list from each of them
    stateList = [s.toString() for r in relevant for s in r.getChildren()]
    stateList.append('START')
    # 4) create a set to remove duplicates
    return set(stateList)


def find_basic_type(aType):
    ''' Return the ASN.1 basic type of aType '''
    basic_type = aType
    try:
        while basic_type['Kind'] == 'ReferenceType':
            # Find type with proper case in the data view
            for t in dataView.viewkeys():
                if t.lower() == basic_type['ReferencedTypeName'].lower():
                    break
            basic_type = dataView[t]['type']
    except:
        print '[ERROR] type', basic_type['ReferencedTypeName'], 'not found'
    return basic_type


def check_and_fix_op_params(op_name, expr_list, process):
    '''
        Verify and/or set the type of a procedure/operator parameters
        Return false if there is a type mismatch
    '''
    # (1) Find the signature of the function
    o = None
    for key, item in process.operators.viewitems():
        if o.lower() == op_name.lower():
            break
    else:
        for key, item in process.procedures.viewitems():
            if key.lower() == op_name.lower():
                break
        else:
            for key, item in special_operators.viewitems():
                if key.lower() == op_name.lower():
                    break
            else:
                print('[ERROR] op not found')
                return False
    # (2) Build a list of all input and output params from the function spec
    in_params = item.get('paramsInOrdered') or []
    out_params= item.get('paramsOutOrdered') or []
    #all_params = in_params.copy().update(out_params)
    # (3) Check that the number of parameters matches
    if len(expr_list) != len(in_params + out_params):
        print('[ERROR] Wrong number of params in op call')
        return False
    # (4) Check each individual parameter type
    for idx, p in enumerate(expr_list):
        select = ('paramsOutOrdered', 'out', idx-len(in_params)) if (
                idx >= len(in_params)) else ('paramsInOrdered', 'in', idx)

        # Get parameter name and type name from the Interface view:
        paramName = item[select[0]][select[2]]
        paramType = item[select[1]][paramName].get('type')

        # Try to set the type if it is missing
        # This is needed because some internal SDL operators (Length, Present)
        # work on a type that is not fixed. In that case we must look in the
        # list of variables to get the type of the expression set by the user
        if p.exprType.get('Kind') == 'UnknownType':
            # Look in the list of variables
            # TODO: we should exclude enumerated types here
            p.exprType = find_variable(p.inputString, process)
        # If type is still unknown, then copy it from the specification:
        # (except for special operators, that have non-fixed types)
        if p.exprType.get('Kind') == 'UnknownType':
            if paramType is not None and key not in special_operators.keys():
                p.exprType = {'Kind': 'ReferenceType',
                        'ReferencedTypeName': paramType}
            else:
                print('[ERROR] Unable to determine op type')
                return False
    return True


def isOfCompatibleType(primary, typeRef, process):
    '''
        Check if a primary (raw value, enumerated, ASN.1 Value...)
        is compatible with a given type
    '''
    actualType = find_basic_type(typeRef)
    print "[DEBUG] checking if {value} is of type {typeref}".format(
            value=primary.inputString, typeref=actualType['Kind'])

    if (primary.kind == 'primaryId'
            and actualType['Kind'] == 'EnumeratedType'):
        # If type ref is an enumeration, check that the value is valid
        if (primary.primaryId[0].replace('_', '-')
                in actualType['EnumValues'].keys()):
            # enumeratedValue kind can only be set here'
            if actualType.get('extraAttr'):
                primary.kind = 'choiceDeterminant'
            else:
                primary.kind = 'enumeratedValue'
            print('... It is!')
            return True
        else:
            print('... It is not. value "', primary.primaryId[0],
                    '"not in this enumeration:',
                    actualType['EnumValues'].keys())
            return False
    elif(primary.kind == 'primaryId' and len(primary.primaryId) == 1 and
            primary.primType['Kind'] == 'UnknownType'):
        primary.primType = find_variable(primary.primaryId[0], process)
        return compare_types(primary.primType, typeRef)
    elif (actualType['Kind'] in ('IntegerType', 'RealType') and
            (primary.kind == 'numericalValue' or primary.primType.get('Kind')
            == actualType['Kind'])):
        print '... It is!'
        return True
    elif (actualType['Kind'] == 'BooleanType' and
            primary.kind == 'booleanValue'):
        print '... It is!'
        return True
    elif (primary.kind == 'emptyString' and
            actualType['Kind'] == 'SequenceOfType'):
        if int(actualType['Min']) == 0:
            print '...It is!'
            return True
        else:
            print ('... It is not (SEQUENCE OF has a minimum size == '
                    + actualType['Min'] + ')')
            return False
    elif (primary.kind == 'sequenceOf' and
            actualType['Kind'] == 'SequenceOfType'):
        if (len(primary.sequenceOf) < int(actualType['Min']) or
                len(primary.sequenceOf) > int(actualType['Max'])):
            print ('... It is not (', len(primary.sequenceOf),
                    'elems, while constraint is [',
                    actualType['Min'], '..', actualType['Max'], '])')
            return False
        for elem in primary.sequenceOf:
            if not isOfCompatibleType(elem, actualType['type'], process):
                print '...It is not!'
                return False
        print '...SEQUENCE OF Check OK'
        return True
    elif primary.kind == 'sequence' and actualType['Kind'] == 'SequenceType':
        userNbElem = len(primary.sequence.keys())
        typeNbElem = len(actualType['Children'].keys())
        if userNbElem != typeNbElem:
            print ('... It is not '
                   '(not the right number of fields in the sequence)')
            return False
        else:
            for field, fieldData in actualType['Children'].viewitems():
                if field not in primary.sequence:
                    print '... It is not (missing field ' + field + ')'
                    return False
                else:
                    # If the user field is a raw value
                    if (primary.sequence[field].kind == 'primary'
                            and primary.sequence[field].var.kind != 'expression'
                            and primary.sequence[field].exprType['Kind'] in
                            ('UnknownType', 'IntegerType', 'RealType',
                                'BooleanType', 'EnumeratedType')):
                        if not isOfCompatibleType(
                                primary.sequence[field].var, fieldData['type'],
                                process):
                            print ('...it is not (field ' + field +
                                    ' is not of the proper type, i.e. ' + (
                                fieldData['type'].get('ReferencedTypeName') or
                                fieldData['type']['Kind']) + ')')
                            return False
                    # Compare the types for semantic equivalence
                    elif not compare_types(
                        primary.sequence[field].exprType, fieldData['type']):
                        print ('...it is not (field ' + field +
                            ' is not of the proper type, i.e. ' + (
                            fieldData['type'].get('ReferencedTypeName') or
                            fieldData['type']['Kind']) + ')')
                        return False
            print '...It is!'
            return True
    elif primary.kind == 'choiceItem' and actualType['Kind'] == 'ChoiceType':
        if primary.choiceItem['choice'] not in actualType['Children'].keys():
            print '...It is not (inexistent choice)'
            return False
        else:
            # compare primary.choiceItem['value']
            # with actualType['Children'][primary.choiceItem['choice']]
            value = primary.choiceItem['value']
            typeOfChoiceField = actualType['Children'][
                    primary.choiceItem['choice']]['type']
            # if the user field is a raw value:
            if (value.kind == 'primary'
                    and value.var.kind != 'expression'
                    and value.exprType['Kind'] in
                    ('UnknownType', 'IntegerType', 'RealType', 'BooleanType')):
                if not isOfCompatibleType(value.var, typeOfChoiceField,
                        process):
                    print('...it is not (field ' +
                            primary.choiceItem['choice'] +
                            ' is not of the proper type, i.e. ' +
                            (typeOfChoiceField.get('ReferencedTypeName') or
                                typeOfChoiceField['Kind']) + ')')
                    return False
            # Compare the types for semantic equivalence:
            elif not compare_types(primary.choiceItem['value'].exprType,
                    typeOfChoiceField):
                print('...it is not (field ' +
                        primary.choiceItem['choice'] +
                        ' is not of the proper type, i.e. ' +
                        (typeOfChoiceField.get('ReferencedTypeName') or
                            typeOfChoiceField['Kind']) + ')')
                return False
            if value.kind == 'primary':
                # Set the type of the choice field
                value.var.primType = typeOfChoiceField
        print '...It is!'
        return True
    elif primary.kind == 'stringLiteral':
        print 'OCTET STRING NOT SUPPORTED YET'
        return True  # Unsupported OCTET STRING
    elif primary.kind == 'ifThenElse':
        # check that IF expr returns BOOL, and that Then and Else expressions
        # are compatible with actualType
        ifExpr = primary.ifThenElse['if']
        thenExpr = primary.ifThenElse['then']
        elseExpr = primary.ifThenElse['else']
        if ifExpr.exprType['Kind'] != 'BooleanType':
            print '...No: IF expression does not return a boolean'
            return False
        else:
            for expr in (thenExpr, elseExpr):
                if (expr.kind == 'primary'
                        and expr.var.kind != 'expression'
                        and expr.exprType['Kind'] in
                        ('UnknownType', 'IntegerType',
                            'RealType', 'BooleanType')):
                    if not isOfCompatibleType(expr.var, typeRef, process):
                        print('...it is not! (' +
                            expr.var.inputString +
                            ' is not of the proper type, i.e. ' +
                            (typeRef.get('ReferencedTypeName') or
                                typeRef['Kind']) + ')')
                        return False
                    else:
                        expr.var.primType = typeRef
                        expr.exprType = typeRef
                # compare the types for semantic equivalence:
                elif not compare_types(expr.exprType, typeRef):
                    print('...it is not (' + expr.inputString +
                        ' is not of the proper type, i.e. ' +
                        (typeRef.get('ReferencedTypeName') or
                            typeRef['Kind']) + ')')
                    return False
        print '...It is!'
        return True
    elif (primary.kind == 'mantissaBaseExpFloat' and
        actualType['Kind'] == 'RealType'):
        print ('..probably (it is a float but I did not check'
               'if values are compatible)')
        return True
    else:
        print '...Cannot conclude. Assuming not.'
        return False


def compare_types(typeA, typeB):
    ''' Compare two types, return True if they are semantically equivalent '''
    # Build the set of References for each type and look for an intersection
    print '[DEBUG] compare_types', typeA, typeB
    if typeA == typeB:
        return True
    A = typeA
    B = typeB
    refsetA = []
    refsetB = []
    while A['Kind'] == 'ReferenceType':
            refsetA.append(A['ReferencedTypeName'])
            try:
                A = dataView[A['ReferencedTypeName']]['type']
            except:
                # Type not in dataview is checked at DCL level
                # no need to raise another error
                pass
    while B['Kind'] == 'ReferenceType':
            refsetB.append(B['ReferencedTypeName'])
            try:
                B = dataView[B['ReferencedTypeName']]['type']
            except:
                pass
    if set(refsetA).intersection(refsetB):
        # Types share a common name: they are identical
        # This cover structured types and enumerations
        # (that cannot be compared at basic type level)
        return True
    # Check if both types have basic compatibility (INTEGER, REAL, BOOLEAN)
    simpleType = filter(lambda x: x['Kind'] in
            ('IntegerType', 'BooleanType', 'RealType'), [A, B])
    if len(simpleType) < 2:
        # Either A or B is not a basic type - cannot be compatible
        return False
    elif A['Kind'] == B['Kind']:
        return True
    elif not(A['Kind'] in ('IntegerType', 'RealType') and
            B['Kind'] in ('IntegerType', 'RealType')):
        return False
    else:
        return True


def find_variable(var, process):
    ''' Look for a variable name in the process and return its type '''
    result = {'Kind': 'UnknownType'}
    for v in process.variables.viewkeys():
        # Case insensitive comparison with variables
        if var.lower() == v.lower():
            result = {'Kind': 'ReferenceType',
                'ReferencedTypeName': process.variables[v]
                .replace('_', '-')}
            break
    return result


def findType(path, process):
    '''
        Determine the type of an element using the data model,
        and the list of variables, operators and procedures
    '''
    errors = []
    warnings = []
    result = {'Kind': 'UnknownType'}
    if not dataView:
        errors.append('Dataview is required to process types')
        return result, errors, warnings
    #print '[DEBUG] Determining type of', path, '...',
    if path:
        # First, find the type of the main element
        # (variable, operator/procedure return type)
        main = path[0]
        if unicode.isnumeric(main):
            result = {'Kind': 'IntegerType', 'Min': main, 'Max': main}
        else:
            try:
                float(main)
                result = {'Kind': 'RealType', 'Min': main, 'Max': main}
            except ValueError:
                v, o = None, None
                # Try to find the name in the variables list
                # Guard (len(path)>1) is used to skip the type
                # detection when the value is a single field.
                for v in process.variables.viewkeys():
                    # Case insensitive comparison with variables
                    if main.lower() == v.lower() and len(path) > 1:
                        result = {'Kind': 'ReferenceType',
                            'ReferencedTypeName': process.variables[v]
                            .replace('_', '-')}
                        break
                else:
                    for o in process.operators.viewkeys():
                        # Case insensitive comparison with operators
                        if main.lower() == o.lower() and len(path) > 1:
                            result = {'Kind': 'ReferenceType',
                                    'ReferencedTypeName': process.operators[o]
                                    .replace('_', '-')}
                            break
                    else:
                        if main.lower() in ('true', 'false'):
                            result = {'Kind': 'BooleanType'}
                        elif(main.lower() in special_operators
                                and len(path) > 1):
                            result = special_operators[main.lower()]['type']
                            # Special operators require type elaboration
                            if main.lower() == 'present':
                                # present(choiceType): must return an enumerated
                                # with elements being the choice options
                                param, = path[1].get('procParams') or [None]
                                if not param:
                                    errors.append('Missing parameter'
                                            ' in PRESENT clause')
                                else:
                                    param_type = find_basic_type(param.exprType)
                                    if param_type.get('Kind') != 'ChoiceType':
                                        errors.append('PRESENT clause parameter'
                                                ' must be a CHOICE type')
                                    else:
                                        result['EnumValues'] = (param_type.
                                                get('Children') or {})
                        else:
                            pass
                #elif main in process.procedures:
                # Incorrect: process.procedures does not have this form.
                # FIXME (or not: if procedures are only sync RI they wont ever
                # have a return parameter - use operators if this is needed,
                # or IN/OUT params in procedures)
                #    result = {'Kind': 'ReferenceType',
                # 'ReferencedTypeName':
                # process.procedures[main].replace('_', '-')}
                #print 'type of ' + main,
    if result['Kind'] not in ('UnknownType', 'IntegerType', 'RealType',
            'BooleanType', 'EnumeratedType') and len(path) > 1:
        resultAsn1 = result['ReferencedTypeName'].replace('_', '-').lower()
        currentIdx = [c for c in dataView if c.lower() == resultAsn1]
        if currentIdx:
            current = dataView[currentIdx[0]]['type']
        else:
            # This check could be done at variable declaration rather than here
            errors.append('Type of variable ' + main + ' : ' +
                    resultAsn1.upper() + ' is not defined')
            return result, errors, warnings
        for elem in path[1:]:
            if 'procParams' in elem:
                # Discard operator parameters: they do not change the type
                continue
            # Sequence, Choice (case insentive)
            if current['Kind'] in ('SequenceType', 'ChoiceType'):
                elemAsn1 = elem.replace('_', '-').lower()
                typeIdx = [c for c in current['Children']
                        if c.lower() == elemAsn1]
                if typeIdx:
                    current = current['Children'][typeIdx[0]]['type']
                    if current['Kind'] == 'ReferenceType':
                        # Jump to the referenced type
                        current = dataView[current
                                ['ReferencedTypeName']]['type']
            # Sequence of
            elif current['Kind'] == 'SequenceOfType':
                #print '[DEBUG] This should be an index:', elem
                current = current['type']
                if current['Kind'] == 'ReferenceType':
                    # Jump to the type of the Sequence of
                    current = dataView[current['ReferencedTypeName']]['type']
            elif current['Kind'] == 'EnumeratedType':
                pass
            else:
                errors.append('Expression ' + '.'.join(path) +
                        ' does not resolve')
        result = current
    return result, errors, warnings


class sdlScc_AST:
    ''' Clean AST backend '''
    def __init__(self, states=[]):
        ''' Initialize the code generator '''
        self.process = Process()
        self.process.inputSignals = {}
        self.process.outputSignals = {}
        self.process.procedures = {}
        self.process.dataView = dataView
        if dv:
            self.process.asn1Modules = dv.asn1Modules
        for state in states:
            # map a list of transitions to each state
            self.process.mapping[state] = []

    def expression_list(self, root):
        ''' Parse a list of expression parameters '''
        errors = []
        warnings = []
        result = []
        params = root.getChildren()
        for p in params:
            exp, err, warn = self.expression(p)
            errors.extend(err)
            warnings.extend(warn)
            result.append(exp)
        return result, errors, warnings

    def primaryValue(self, root, prim=None):
        '''
            Process a primary expression such as a!b(4)!c(hello)
            or { x 1, y a:2 } (ASN.1 Value Notation)
        '''
        warnings = []
        errors = []
        prim.kind = 'primaryId'
        firstId = ''
        for child in root.getChildren():
            if child.type == ID:
                firstId = unicode(child.toString())
                prim.primaryId = [firstId]
            elif child.type == INT:
                prim.kind = 'numericalValue'
                prim.primaryId = [unicode(child.toString().lower())]
            elif child.type in (TRUE, FALSE):
                prim.kind = 'booleanValue'
                prim.primaryId = [unicode(child.toString().lower())]
            elif child.type == FLOAT:
                prim.kind = 'numericalValue'
                prim.primaryId = [unicode(child.getChild(0).toString())]
            elif child.type == STRING:
                prim.kind = 'stringLiteral'
                prim.stringLiteral = unicode(child.getChild(0).toString())
            elif child.type == FLOAT2:
                prim.kind = 'mantissaBaseExpFloat'
                mant = int(child.getChild(0).toString())
                base = int(child.getChild(1).toString())
                exp = int(child.getChild(2).toString())
                prim.mantissaBaseExpFloat = {'mantissa': mant, 'base': base,
                        'exponent': exp}
                prim.primType = {'Kind': 'RealType'}
            elif child.type == EMPTYSTR:
                # Empty SEQUENCE OF (i.e. "{}")
                prim.kind = 'emptyString'
            elif child.type == CHOICE:
                prim.kind = 'choiceItem'
                choice = child.getChild(0).toString()
                expr, err, warn = self.expression(child.getChild(1))
                errors.extend(err)
                warnings.extend(warn)
                prim.choiceItem = {'choice': choice, 'value': expr}
            elif child.type == SEQUENCE:
                prim.kind = 'sequence'
                for elem in child.getChildren():
                    if elem.type == ID:
                        fieldName = elem.toString()
                    else:
                        prim.sequence[fieldName], err, warn = (
                                self.expression(elem))
                        map(errors.append, err)
                        map(warnings.append, warn)
            elif child.type == SEQOF:
                prim.kind = 'sequenceOf'
                for elem in child.getChildren():
                    primElem = Primary(getInputString(elem), elem.getLine(),
                            elem.getCharPositionInLine())
                    primElem, err, warn = self.primaryValue(elem, primElem)
                    map(errors.append, err)
                    map(warnings.append, warn)
                    prim.sequenceOf.append(primElem)
            elif child.type == BITSTR:
                prim.kind = 'bitString'
                warnings.append('Bit string literal not supported yet')
            elif child.type == OCTSTR:
                prim.kind = 'octetString'
                warnings.append('Octet string literal not supported yet')
            elif child.type == PARAMS:
                if not firstId:
                    errors.append(
                            'Ground expression cannot have index or params: ' +
                            getInputString(root))
                    return [], errors, warnings
                exprList, err, warn = self.expression_list(child)
                errors.extend(err)
                warnings.extend(warn)
                case_insensitive_ops = ([o.lower() for o in
                        self.process.operators] + [p.lower() for p in
                            self.process.procedures])
                if(firstId.lower() in special_operators or
                        firstId.lower() in case_insensitive_ops):
                    print '[DEBUG] calling check_and_fix_op_params'
                    # here we must check/set the type of each param
                    if not check_and_fix_op_params(
                            firstId.lower(), exprList, self.process):
                        errors.append('Wrong parameter(s) in operation call'
                                + getInputString(root))
                    prim.primaryId.append({'procParams': exprList})
                else:
                    # Must be an index (only one param)
                    if len(exprList) != 1:
                        errors.append('Wrong number of parameters')
                    else:
                        prim.primaryId.append({'index': exprList})
            elif child.type == FIELD_NAME:
                if not firstId:
                    errors.append(
                            'Ground expression cannot have index or params: ' +
                            getInputString(root))
                    return [], errors, warnings
                prim.primaryId.append(child.getChild(0).toString())
            else:
                warnings.append('Unsupported primary construct, type:' +
                        str(child.type) +
                        ' (line ' + str(child.getLine()) + ')')
        if prim.primaryId and not prim.primType:
            prim.primType, err, warn = findType(prim.primaryId, self.process)
            errors.extend(err)
            warnings.extend(warn)
        return prim, errors, warnings

    def primary(self, root):
        ''' Process a primary (-/NOT value) '''
        warnings = []
        errors = []
        prim = Primary(
                getInputString(root),
                root.getLine(),
                root.getCharPositionInLine())
        for child in root.getChildren():
            if child.type == NOT:
                prim.op_not = True
            elif child.type == MINUS:
                prim.op_minus = True
            elif child.type == PRIMARY_ID:
                # Covers variable reference, indexed values,
                # and ASN.1 value notation
                prim, err, warn = self.primaryValue(child, prim)
                errors.extend(err)
                warnings.extend(warn)
            elif child.type == EXPRESSION:
                prim.kind = 'expression'
                prim.expr, err, warn = self.expression(child.getChild(0))
                errors.extend(err)
                warnings.extend(warn)
                prim.primType = prim.expr.exprType
            elif child.type == IFTHENELSE:
                prim.kind = 'ifThenElse'
                ifPart = child.getChild(0)
                thenPart = child.getChild(1)
                elsePart = child.getChild(2)
                ifExpr, err, warn = self.expression(ifPart)
                errors.extend(err)
                warnings.extend(warn)
                thenExpr, err, warn = self.expression(thenPart)
                errors.extend(err)
                warnings.extend(warn)
                elseExpr, err, warn = self.expression(elsePart)
                errors.extend(err)
                warnings.extend(warn)
                global tmpVar
                prim.ifThenElse = {'if': ifExpr,
                        'then': thenExpr,
                        'else': elseExpr,
                        'tmpVar': tmpVar}
                #prim.primType = thenExpr.exprType
                prim.primType = {'Kind': 'UnknownType'}
                tmpVar += 1
                # Check if thenExpr is of same type as elseExpr:
                # REMOVED : not needed! there is already a test
                # in the isCompatibleTypes function
                #if not compare_types(thenExpr.exprType, elseExpr.exprType):
                #    thenExprTypeName = (
                #            thenExpr.exprType.get('ReferencedTypeName') or
                #            thenExpr.exprType['Kind']).replace('-', '_')
                #    elseExprTypeName = (
                #            elseExpr.exprType.get('ReferencedTypeName') or
                #            elseExpr.exprType['Kind']).replace('-', '_')
                #    errors.append('If-then-else expression: return values not'
                #            ' of the same type: THEN (' +
                #            thenExpr.inputString + ', type= ' +
                #            thenExprTypeName +
                #            '), ELSE ('+
                #            elseExpr.inputString +
                #            ', type= ' +
                #            elseExprTypeName +
                #            ') (line ' + str(ifExpr.line)+ ')')
            else:
                warnings.append('Unsupported primary child type:' +
                        str(child.type) + ' (line ' +
                        str(child.getLine()) + ')')
        return prim, errors, warnings

    def expression(self, root):
        ''' Expression analysis (e.g. 5+5*hello(world)!foo) '''
        errors = []
        warnings = []
        expr = Expression(getInputString(root), root.getLine(),
                root.getCharPositionInLine())
        expr.exprType = {'Kind': 'UnknownType'}

        if root.type in (PLUS, ASTERISK, DASH, APPEND, IMPLIES, OR, XOR, AND,
                EQ, NEQ, GT, GE, LT, LE, IN, DIV, MOD, REM):
            left, right = root.getChildren()

            expr.left, eLeft, wLeft = self.expression(left)
            expr.right, eRight, wRight = self.expression(right)
            errors.extend(eLeft)
            warnings.extend(wLeft)
            errors.extend(eRight)
            warnings.extend(wRight)

            # Compare the type of both sides of the expression
            leftExprTypeName = (expr.left.exprType.get('ReferencedTypeName') or
                    expr.left.exprType['Kind']).replace('-', '_')
            rightExprTypeName = (expr.right.exprType.get
                    ('ReferencedTypeName') or
                    expr.right.exprType['Kind']).replace('-', '_')

            # If type of a the left part of the expression is still unknown
            # then look in the list of DCL variables for it
            # left expr only must be resolved because right part could
            # be an enumerated, which value name could conflict with a
            # variable name. left part cannot be an enumerated name.
            if expr.left.exprType['Kind'] == 'UnknownType':
                expr.left.exprType = find_variable(expr.left.inputString,
                        self.process)

            # If only one of the operands is a raw value,
            # check for type compatibility with the other operand
            rightIsRaw = (expr.right.kind == 'primary' and
                    expr.right.exprType['Kind'] in
                    ('UnknownType', 'IntegerType', 'RealType', 'BooleanType')
                    and len(expr.right.var.primaryId) == 1)
            leftIsRaw = (expr.left.kind == 'primary' and
                    expr.left.exprType['Kind'] in
                    ('UnknownType', 'IntegerType', 'RealType', 'BooleanType')
                    and len(expr.left.var.primaryId) == 1)

            if (rightIsRaw and expr.right.exprType['Kind'] in
                    ('IntegerType', 'RealType')):
                expr.right.var.kind = 'numericalValue'

            if expr.left.kind == 'primary':
                print expr.left, expr.left.var.kind

            if (leftIsRaw and expr.left.exprType['Kind'] in
                    ('IntegerType', 'RealType')):
                expr.left.var.kind = 'numericalValue'

            if rightIsRaw != leftIsRaw:
                check = ((rightIsRaw and
                    isOfCompatibleType(expr.right.var, expr.left.exprType,
                        self.process))
                    or (leftIsRaw and
                        isOfCompatibleType(
                            expr.left.var, expr.right.exprType, self.process)))
                if not check:
                    errors.append('Incompatible types in expression: left (' +
                            expr.left.inputString + ', type= '+
                            leftExprTypeName + '), right (' +
                            expr.right.inputString +
                            ', type= ' +
                            rightExprTypeName + ') (line ' +
                            str(expr.line)+ ')')
                else:
                    if rightIsRaw:
                        expr.right.exprType = expr.left.exprType
                    else:
                        expr.left.exprType = expr.right.exprType
            elif not compare_types(expr.left.exprType, expr.right.exprType):
                errors.append('!Incompatible types in expression: left (' +
                        expr.left.inputString + ', type= ' +
                        leftExprTypeName + '), right ('+
                        expr.right.inputString +
                        ', type= ' +
                        rightExprTypeName +
                        ') (line ' + str(expr.line)+ ')')
        if root.type in (IN, AND, EQ, NEQ, GT, GE, LT, LE, OR, XOR, AND, IN):
            expr.exprType = {'Kind': 'BooleanType'}
        elif root.type in (PLUS, ASTERISK, DASH, APPEND, REM, MOD):
            expr.exprType = expr.left.exprType
        try:
            expr.kind = Kind[root.type]
        except:
            warnings.append('Unsupported expression construct, type: ' +
                    str(root.type))
        if root.type == PRIMARY:
            expr.var, err, warn = self.primary(root)
            errors.extend(err)
            warnings.extend(warn)
            # Type of expression is the type of the primary
            # (if set - otherwise keep Unknown)
            if expr.var.primType:
                expr.exprType = expr.var.primType
        return expr, errors, warnings

    def variables(self, root):
        ''' Process declarations of variables (dcl a,b Type := 5) '''
        var = []
        errors = []
        warnings = []
        for child in root.getChildren():
            if child.type == ID:
                var.append(child.toString())
            elif child.type == SORT:
                sort = child.getChild(0).toString()
                # Case insensitive check
                if (dataView is None or sort.replace('_', '-').lower() not in
                        [t.lower() for t in dataView.viewkeys()]):
                    errors.append('Datatype "' + sort +
                            '" is not defined in the data view (line ' +
                            str(child.getLine()) + ')')
            elif child.type == GROUND:
                pass
                # TODO Expression - make a default value assignment
                # self.expression(child)
            else:
                warnings.append('Unsupported variables construct type: ' +
                        str(child.type))
        for v in var:
            self.process.variables[v] = sort
        if not dataView:
            errors.append('Cannot do semantic checks on variable declarations')
        return errors, warnings

    def dcl(self, root):
        ''' Process a set of variable declarations '''
        errors = []
        warnings = []
        for child in root.getChildren():
            if child.type == VARIABLES:
                err, warn = self.variables(child)
                map(errors.append, err)
                map(warnings.append, warn)
            else:
                warnings.append(
                        'Unsupported dcl construct, type: ' + str(child.type))
        return errors, warnings

    def textAreaContent(self, root):
        ''' Content of a text area: DCL, operators, procedures  '''
        errors = []
        warnings = []
        for child in root.getChildren():
            if child.type == DCL:
                err, warn = self.dcl(child)
                errors.extend(err)
                warnings.extend(warn)
            else:
                warnings.append(
                        'Unsupported construct in text area content, type: ' +
                        str(child.type))
        return errors, warnings

    def text_area(self, root, parent=None):
        ''' Process a text area (DCL, procedure, operators declarations '''
        errors = []
        warnings = []
        ta = TextArea()
        for child in root.getChildren():
            if child.type == CIF:
                userTextStartIndex = child.getTokenStopIndex() + 1
                x, y, w, h = self.cif(child)
                ta.coordinates = [x, y, w, h]
                ta.absCoordinates = [x, y]
            elif child.type == TEXTAREA_CONTENT:
                ta.line = child.getLine()
                ta.charPositionInLine = child.getCharPositionInLine()
                # Go update the process-level list of variables
                # (TODO: also ops and procedures)
                err, warn = self.textAreaContent(child)
                map(errors.append, err)
                map(warnings.append, warn)
            elif child.type == ENDTEXT:
                userTextStopIndex = child.getTokenStartIndex() - 1
                ta.inputString = tokens.toString(userTextStartIndex,
                        userTextStopIndex).strip()
            elif child.type == HYPERLINK:
                ta.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported construct in text area, type: ' +
                        str(child.type))
        # Report errors with symbol coordinates
        err = [[e, ta.absCoordinates] for e in errors]
        warn = [[w, ta.absCoordinates] for w in warnings]
        return ta, err, warn

    def processDefinition(self, child):
        ''' Process definition analysis '''
        errors = []
        warnings = []
        if child.type == ID:
            # Get process (taste function) name
            self.process.processName = child.text
            try:
                fv = iv.functions[self.process.processName]
                self.process.inputSignals = {i: fv['interfaces'][i] for i in
                        fv['interfaces'] if
                        fv['interfaces'][i]['direction'] == iv.PI}
                self.process.outputSignals = {o: fv['interfaces'][o] for o in
                        fv['interfaces'] if
                        (fv['interfaces'][o]['direction'] == iv.RI and
                            fv['interfaces'][o]['synchronism'] == iv.asynch)}
                self.process.procedures = {o: fv['interfaces'][o] for o in
                        fv['interfaces'] if
                        (fv['interfaces'][o]['direction'] == iv.RI and
                            fv['interfaces'][o]['synchronism'] == iv.synch)}
            except:
                errors.append(
                        'Could not find signal list in the interface view')
        elif child.type == TEXTAREA:
            # Text zone where variables and operators are declared
            ta, err, warn = self.text_area(child)
            map(errors.append, err)
            map(warnings.append, warn)
            self.process.textAreas.append(ta)
        elif child.type == START:
            # START transition (fills the mapping structure)
            #self.process.states.append(self.start(child))
            self.process.start, err, warn = self.start(child)
            map(errors.append, err)
            map(warnings.append, warn)
        elif child.type == STATE:
            # STATE - fills up the 'mapping' structure.
            s, err, warn = self.state(child, parent=None)
            map(errors.append, err)
            map(warnings.append, warn)
            self.process.states.append(s)
        elif child.type == NUMBER_OF_INSTANCES:
            # Number of instances - discarded when working on a single process
            pass
        else:
            warnings.append('Unsupported process definition child type: ' +
                    str(child.type))
        return errors, warnings

    def input_part(self, root, parent):
        ''' Parse an INPUT - set of TASTE provided interfaces '''
        i = Input()
        warnings = []
        errors = []
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                i.coordinates = [x, y, w, h]
                if parent:
                    i.absCoordinates = [a+b for a, b in
                            zip(i.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif child.type == INPUTLIST:
                i.inputString = getInputString(child)
                i.line = child.getLine()
                i.charPositionInLine = child.getCharPositionInLine()
                # get input name and parameters
                for inputname in [c for c in child.getChildren() if
                        c.toString() != 'PARAMS']:
                    for inpSig in self.process.inputSignals.viewkeys():
                        if inpSig.lower() == inputname.toString().lower():
                            i.inputlist[inpSig] = -1
                            break
                    else:
                        warnings.append('Input signal not declared: '
                                + inputname.toString() +
                                ' (line ' + str(i.line) + ')')
                for inputparam in [c.getChildren() for c in
                        child.getChildren() if c.toString() == 'PARAMS']:
                    i.parameters = [p.toString() for p in inputparam]
                    for p in i.parameters:
                        if p not in self.process.variables:
                            errors.append('Input parameter ' +
                                    p +
                                    ' is not declared (add "DCL ' +
                                    p +
                                    ' WhateverType;" in a text area')
                # Report errors with symbol coordinates
                errors = [[e, i.absCoordinates] for e in errors]
                warnings = [[w, i.absCoordinates] for w in warnings]
            elif child.type == ASTERISK:
                # Asterisk means: all inputs not processed explicitely
                # -> FIXME, below is incorrect
                i.inputString = getInputString(child)
                i.line = child.getLine()
                i.charPositionInLine = child.getCharPositionInLine()
                for inp in self.process.inputSignals:
                    i.inputlist[inp] = -1
            elif child.type == PROVIDED:
                warnings.append('"PROVIDED" expressions not supported')
                i.provided = 'Provided'
            elif child.type == TRANSITION:
                transition, err, warn = self.transition(child, parent=i)
                map(errors.append, err)
                map(warnings.append, warn)
                i.transition = transition
                # Associate a reference to the transition to the list of inputs
                # The reference is an index to process.transitions table
                self.process.transitions.append(transition)
                for inp in i.inputlist:
                    i.inputlist[inp]=len(self.process.transitions) - 1
            elif child.type == COMMENT:
                i.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                i.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported INPUT child type: ' +
                        str(child.type))
        return i, errors, warnings

    def state(self, root, parent):
        ''' Parse a STATE '''
        errors = []
        warnings = []
        current_states = []
        s = State()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                s.coordinates = [x, y, w, h]
                if parent:
                    s.absCoordinates = [a+b for a, b in
                            zip(s.coordinates[0:2],
                                parent.absCoordinates[0:2])]
                else:
                    s.absCoordinates = s.coordinates
            elif child.type == STATELIST:
                # State name(s)
                s.inputString = getInputString(child)
                s.line = child.getLine()
                s.charPositionInLine = child.getCharPositionInLine()
                for statename in child.getChildren():
                    current_states.append(statename.toString())
            elif child.type == ASTERISK:
                s.inputString = getInputString(child)
                s.line = child.getLine()
                s.charPositionInLine = child.getCharPositionInLine()
                exceptions = [c.toString() for c in child.getChildren()]
                for st in self.process.mapping:
                    if st not in (exceptions, 'START'):
                        current_states.append(st)
            elif child.type == INPUT:
                # A transition triggered by an INPUT
                i, err, warn = self.input_part(child, parent=s)
                map(errors.append, err)
                map(warnings.append, warn)
                for state in current_states:
                    # Now put the Input class directly -
                    # it contains the input list and the parameters
                    try:
                        self.process.mapping[state].append(i)
                    except:
                        pass
                    #self.process.mapping[state].append(i.inputlist)
                s.inputs.append(i)
            elif child.type == COMMENT:
                s.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                s.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append(['Unsupported STATE definition child type: ' +
                    str(child.type)])
        return s, errors, warnings

    def cif(self, root):
        ''' Return the CIF coordinates '''
        result=[]
        for child in root.getChildren():
            if child.type == DASH:
                val = -int(child.getChild(0).toString())
            else:
                val = int(child.toString())
            result.append(val)
        return result

    def start(self, root, parent=None):
        ''' Parse the START transition '''
        errors = []
        warnings = []
        s = Start()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                s.coordinates = [x, y, w, h]
                s.absCoordinates = [x, y]
            elif child.type == TRANSITION:
                s.transition, err, warn = self.transition(child, parent=s)
                map(errors.append, err)
                map(warnings.append, warn)
                self.process.transitions.append(s.transition)
                self.process.mapping['START'] = len(self.process.transitions)-1
            elif child.type == COMMENT:
                s.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                s.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('START unsupported child type: ' +
                        str(child.type))
        # Report errors with symbol coordinates
        # (removed: start symbol cannot have errors)
        #err = [[e, s.absCoordinates] for e in errors]
        #warn = [[w, s.absCoordinates] for w in warnings]
        return s, errors, warnings

    def end(self, root, parent=None):
        ''' Parse a comment symbol '''
        c = Comment()
        c.line = root.getLine()
        c.charPositionInLine = root.getCharPositionInLine()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                c.coordinates = [x, y, w, h]
                c.absCoordinates = [x, y]
            elif child.type == StringLiteral:
                c.inputString = child.toString()[1:-1]
            elif child.type == HYPERLINK:
                c.hyperlink = child.getChild(0).toString()[1:-1]
        return c, [], []

    def procedure_call(self, root, parent):
        ''' Parse a PROCEDURE CALL (synchronous required interface) '''
        # Same as OUTPUT for external procedures
        o, err, warn = self.output(root, parent)
        o.kind = 'procedure_call'
        return o, err, warn

    def outputbody(self, root):
        ''' Parse an output body (the content excluding the CIF statement) '''
        errors = []
        warnings = []
        body = {}
        for child in root.getChildren():
            if child.type == ID:
                body['outputName'] = child.toString()
            elif child.type == PARAMS:
                body['params'], err, warn = self.expression_list(child)
                errors.extend(err)
                warnings.extend(warn)
            else:
                warnings.append('Unsupported output body type:' + str(child.type))
        if body.get('params'):
            body['tmpVars'] = []
            global tmpVar
            for idx in range(len(body['params'])):
                body['tmpVars'].append(tmpVar)
                tmpVar += 1
        return body, errors, warnings

    def output(self, root, parent):
        ''' Parse an OUTPUT :  set of asynchronous required interface(s) '''
        errors = []
        warnings = []
        o = Output()
        o.kind = 'output'
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                o.coordinates = [x, y, w, h]
                if parent:
                    o.absCoordinates = [a+b for a, b in
                            zip(o.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif child.type == OUTPUT_BODY:
                o.inputString = getInputString(child)
                o.line = child.getLine()
                o.charPositionInLine = child.getCharPositionInLine()
                body, err, warn = self.outputbody(child)
                map(errors.append, err)
                map(warnings.append, warn)
                o.output.append(body)
            elif child.type == COMMENT:
                o.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                o.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported output child type: ' +
                        str(child.type))
        # Report errors with symbol coordinates
        err = [[e, o.absCoordinates] for e in errors]
        warn = [[w, o.absCoordinates] for w in warnings]
        return o, err, warn

    def alternative_part(self, root, parent):
        ''' Parse a decision answer '''
        errors = []
        warnings = []
        ans = Answer()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                ans.coordinates = [x, y, w, h]
                if parent:
                    ans.absCoordinates = [a+b for a, b in
                            zip(ans.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif child.type == CLOSED_RANGE:
                ans.kind = 'closed_range'
                ans.closedRange = [float(child.getChild(0).toString()),
                                  float(child.getChild(1).toString())]
            elif child.type == CONSTANT:
                ans.kind = 'constant'
                ans.constant, err, warn = self.expression(child.getChild(0))
                map(errors.append, err)
                map(warnings.append, warn)
            elif child.type == OPEN_RANGE:
                ans.kind = 'open_range'
                for c in child.getChildren():
                    if c.type == CONSTANT:
                        ans.constant, err, warn = self.expression(
                                c.getChild(0))
                        map(errors.append, err)
                        map(warnings.append, warn)
                    else:
                        ans.openRangeOp = Kind[c.type]
            elif child.type == INFORMAL_TEXT:
                ans.kind = 'informal_text'
                ans.informalText = child.getChild(0).toString()[1:-1]
            elif child.type == TRANSITION:
                ans.transition, err, warn = self.transition(child, parent=ans)
                errors.extend(err)
                warnings.extend(warn)
            elif child.type == HYPERLINK:
                ans.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported answer type: ' + str(child.type))
            if child.type in (CLOSED_RANGE, CONSTANT,
                    OPEN_RANGE, INFORMAL_TEXT):
                ans.inputString = getInputString(child)
                ans.line = child.getLine()
                ans.charPositionInLine = child.getCharPositionInLine()
                # Report errors with symbol coordinates
                errors = [[e, ans.absCoordinates] for e in errors]
                warnings = [[w, ans.absCoordinates] for w in warnings]
        return ans, errors, warnings

    def decision(self, root, parent):
        ''' Parse a DECISION '''
        errors = []
        warnings = []
        dec = Decision()
        global tmpVar
        dec.tmpVar = tmpVar
        tmpVar += 1
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                dec.coordinates = [x, y, w, h]
                if parent:
                    dec.absCoordinates = [a+b for a, b in
                            zip(dec.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif child.type == QUESTION:
                dec.kind = 'question'
                decisionExpr, err, warn = self.expression(child.getChild(0))
                for e in err:
                    errors.append([e, dec.absCoordinates])
                for w in warn:
                    warnings.append([w, dec.absCoordinates])
                dec.question = decisionExpr
                dec.inputString = dec.question.inputString
                dec.line = dec.question.line
                dec.charPositionInLine = dec.question.charPositionInLine
                if dec.question.exprType['Kind'] == 'UnknownType':
                    dec.question.exprType = find_variable(
                            dec.question.inputString, self.process)
            elif child.type == INFORMAL_TEXT:
                dec.kind = 'informal_text'
                dec.inputString = getInputString(child)
                dec.informalText = child.getChild(0).toString()[1:-1]
                dec.line = child.getLine()
                dec.charPositionInLine = child.getCharPositionInLine()
            elif child.type == ANY:
                dec.kind = 'any'
            elif child.type == COMMENT:
                dec.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                dec.hyperlink = child.getChild(0).toString()[1:-1]
            elif child.type == ANSWER:
                ans, err, warn = self.alternative_part(child, parent)
                map(errors.append, err)
                map(warnings.append, warn)
                dec.answers.append(ans)
                # Check that expression and answer types are compatible
                # TODO To be completed: constant that are not enum/int/bool
                # are not checked for existence)
                if (ans.kind in ('constant', 'open_range')
                        and ans.constant.kind == 'primary'
                        and ans.constant.var.kind != 'expression'
                        and ans.constant.exprType['Kind'] in (
                            'UnknownType', 'IntegerType',
                            'RealType', 'BooleanType')):
                    if not isOfCompatibleType(ans.constant.var,
                            dec.question.exprType, self.process):
                        errors.append(ans.inputString +
                                ' is not type-compatible with ' +
                                dec.question.inputString)
                    else:
                        ans.constant.var.primType = dec.question.exprType
                        print '[DEBUG] ANSWER Kind:', ans.constant.var.kind
                elif (ans.kind in ('constant', 'open_range')
                        and not compare_types(ans.constant.exprType,
                            dec.question.exprType)):
                    errors.append(ans.inputString +
                            ' is not of a type compatible with ' +
                            dec.question.inputString)
                else:
                    pass  # TODO: closed-range
            elif child.type == ELSE:
                dec.kind = child.toString()
                a = Answer()
                a.inputString = 'ELSE'
                for c in child.getChildren():
                    if c.type == CIF:
                        x, y, w, h = self.cif(c)
                        a.coordinates = [x, y, w, h]
                        a.absCoordinates = [u+v for u, v in
                                zip(a.coordinates[0:2],
                                    dec.absCoordinates[0:2])]
                    elif c.type == TRANSITION:
                        a.transition, err, warn = self.transition(c, parent=a)
                        for e in err:
                            errors.append([e, a.absCoordinates])
                        for w in warn:
                            warnings.append([w, a.absCoordinates])
                    elif child.type == HYPERLINK:
                        a.hyperlink = child.getChild(0).toString()[1:-1]
                a.kind = 'else'
                dec.answers.append(a)
            else:
                warnings.append(['Unsupported DECISION child type: ' +
                    str(child.type), dec.absCoordinates])
        return dec, errors, warnings

    def terminator_statement(self, root, parent):
        ''' Parse a terminator (NEXTSTATE, JOIN, STOP) '''
        errors = []
        warnings = []
        t = Terminator()
        for term in root.getChildren():
            if term.type == CIF:
                x, y, w, h = self.cif(term)
                t.coordinates = [x, y, w, h]
                if parent:
                    t.absCoordinates = [a+b for a, b in
                            zip(t.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif term.type == LABEL:
                label, err, warn = self.label(term, parent=parent)
                errors.extend(err)
                warnings.extend(warn)
                t.label = label
            elif term.type == NEXTSTATE:
                t.kind = 'next_state'
                t.inputString = term.getChild(0).toString()
                t.line = term.getChild(0).getLine()
                t.charPositionInLine = term.getChild(0).getCharPositionInLine()
                # Add next state infos at process level
                # Used in rendering backends to merge a NEXTSTATE with a STATE
                self.process.terminators.append(t)
            elif term.type == JOIN:
                t.kind = 'join'
                t.inputString = term.getChild(0).toString()
                t.line = term.getChild(0).getLine()
                t.charPositionInLine = term.getChild(0).getCharPositionInLine()
            elif term.type == STOP:
                t.kind = 'stop'
            elif term.type == COMMENT:
                t.comment, _, __ = self.end(term)
            elif term.type == HYPERLINK:
                t.hyperlink = term.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported terminator type: ' +
                        str(term.type))
        # Report errors with symbol coordinates
        err = [[e, t.absCoordinates] for e in errors]
        warn = [[w, t.absCoordinates] for w in warnings]
        return t, err, warn

    def transition(self, root, parent):
        ''' Parse a transition '''
        errors = []
        warnings = []
        t = Transition()
        for child in root.getChildren():
            if child.type == PROCEDURE_CALL:
                pc, err, warn = self.procedure_call(child, parent=parent)
                map(errors.append, err)
                map(warnings.append, warn)
                t.actions.append(pc)
                parent = pc
            elif child.type == LABEL:
                label, err, warn = self.label(child, parent=parent)
                errors.extend(err)
                warnings.extend(warn)
                t.actions.append(label)
                parent = label
            elif child.type == TASK:
                tas, err, warn = self.task(child, parent=parent)
                map(errors.append, err)
                map(warnings.append, warn)
                t.actions.append(tas)
                parent = tas
            elif child.type == OUTPUT:
                outp, err, warn = self.output(child, parent=parent)
                map(errors.append, err)
                map(warnings.append, warn)
                t.actions.append(outp)
                parent = outp
            elif child.type == DECISION:
                dec, err, warn = self.decision(child, parent=parent)
                map(errors.append, err)
                map(warnings.append, warn)
                t.actions.append(dec)
                parent = dec
            elif child.type == TERMINATOR:
                term, err, warn = self.terminator_statement(child,
                        parent=parent)
                map(errors.append, err)
                map(warnings.append, warn)
                t.terminator = term
            else:
                warnings.append('Unsupported symbol in transition, type: ' +
                        str(child.type))
        return t, errors, warnings

    def assign(self, root):
        ''' Parse an assignation (a := b) in a task symbol '''
        errors = []
        warnings = []
        expr = Expression(
                getInputString(root), root.getLine(),
                root.getCharPositionInLine())
        expr.kind = 'assign'
        for child in root.getChildren():
            if child.type == VARIABLE:
                # Left part of the assignation
                prim = Primary(getInputString(child), child.getLine(),
                        child.getCharPositionInLine())
                prim, err, warn = self.primaryValue(child, prim)
                errors.extend(err)
                warnings.extend(warn)
                #leftPart = prim.primaryId
                #leftExprType, err, warn = findType(leftPart, self.process)
                errors.extend(err)
                warnings.extend(warn)
                expr.left = Expression(
                        getInputString(child), child.getLine(),
                        child.getCharPositionInLine())
                expr.left.kind = 'primary'
                expr.left.var = prim  # Primary(
                        #getInputString(child), child.getLine(),
                        #child.getCharPositionInLine())
                #expr.left.var.kind = 'primaryId'
                #expr.left.var.primaryId = leftPart
                #expr.left.var.primType = leftExprType
                expr.left.exprType = expr.left.var.primType
            else:
                # Right part of the assignation
                expr.right, err, warn = self.expression(child)
                errors.extend(err)
                warnings.extend(warn)
        #if leftExprType['Kind'] == 'UnknownType':
        if expr.left.exprType['Kind'] == 'UnknownType':
            # Try to find the variable in the DCL list:
            expr.left.exprType = find_variable(expr.left.var.primaryId[0],
                    self.process)
            expr.left.var.primType = expr.left.exprType
        if expr.left.exprType['Kind'] == 'UnknownType':
            errors.append('Variable ' + expr.left.inputString +
                    ' is undefined (line '
                    + str(root.getLine()) + ', position ' +
                    str(root.getCharPositionInLine()) + ')')
            return expr, errors, warnings
        # If the right part is a value (not an identifier),
        # check if the value is compatible with the type
        if (expr.right.kind == 'primary'
                and expr.right.var.kind != 'expression'
                and expr.right.exprType['Kind'] in
                ('UnknownType', 'IntegerType', 'RealType', 'BooleanType')):
            if isOfCompatibleType(expr.right.var,
                    expr.left.exprType, self.process):
                expr.right.exprType = expr.left.exprType
            else:
                errors.append(expr.right.inputString +
                        ' does not have a type compatible with ' +
                        expr.left.inputString)
                return expr, errors, warnings
        # Compare the types for semantic equivalence
        if not compare_types(expr.left.exprType, expr.right.exprType):
            #print 'Comparing', expr.left.exprType, 'and ', expr.right.exprType
            errors.append(expr.right.inputString +
                    ' has a type that is incompatible with ' +
                    expr.left.inputString)
        else:
            if expr.right.kind == 'primary':
                # Propagate the type of the right expression
                # to its inner primary
                expr.right.var.primType = expr.left.var.primType
        return expr, errors, warnings

    def taskBody(self, root, t):
        ''' Parse the body of a task (excluding CIF and TASK tokens) '''
        errors = []
        warnings = []
        for child in root.getChildren():
            if child.type == ASSIGN:
                a, err, warn = self.assign(child)
                map(errors.append, err)
                map(warnings.append, warn)
                t.kind = 'assign'
                t.assign.append(a)
            elif child.type == INFORMAL_TEXT:
                t.kind = 'informal_text'
                t.informalText.append(child.getChild(0).toString()[1:-1])
            else:
                warnings.append('Unsupported child type in task body: ' +
                        str(child.type))
        return t, errors, warnings

    def task(self, root, parent=None):
        ''' Parse a TASK symbol (assignation or informal text) '''
        errors = []
        warnings = []
        t = Task()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                t.coordinates = [x, y, w, h]
                if parent:
                    t.absCoordinates = [a+b for a, b in
                            zip(t.coordinates[0:2],
                                parent.absCoordinates[0:2])]
            elif child.type == TASK_BODY:
                t.inputString = getInputString(child)
                t.line = child.getLine()
                t.charPositionInLine = child.getCharPositionInLine()
                t, err, warn = self.taskBody(child, t)
                map(errors.append, err)
                map(warnings.append, warn)
            elif child.type == COMMENT:
                t.comment, _, __ = self.end(child)
            elif child.type == HYPERLINK:
                t.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append('Unsupported child type in task definition: ' +
                        str(child.type))
        # Report errors with symbol coordinates
        err = [[e, t.absCoordinates] for e in errors]
        warn = [[w, t.absCoordinates] for w in warnings]
        return t, err, warn

    def label(self, root, parent):
        ''' Parse a LABEL symbol '''
        errors = []
        warnings = []
        t = Label()
        for child in root.getChildren():
            if child.type == CIF:
                # Get symbol coordinates
                x, y, w, h = self.cif(child)
                t.coordinates = [x, y, w, h]
                if parent:
                    t.absCoordinates = [a+b for a, b in
                            zip(t.coordinates[0:2], parent.absCoordinates[0:2])]
            elif child.type == ID:
                t.inputString = getInputString(child)
                t.line = child.getLine()
                t.charPositionInLine = child.getCharPositionInLine()
            elif child.type == HYPERLINK:
                t.hyperlink = child.getChild(0).toString()[1:-1]
            else:
                warnings.append(
                        'Unsupported child type in label definition: ' +
                        str(child.type))
        # Report errors with symbol coordinates
        err = [[e, t.absCoordinates] for e in errors]
        warn = [[w, t.absCoordinates] for w in warnings]
        return t, err, warn


def parseProcessDefinition(fileName=None, string=None):
    ''' Parse a complete SDL process '''
    warnings = []
    errors = []
    if fileName:
        sys.path.insert(0, os.path.dirname(fileName))
    try:
        global dataView
        global dv
        if not dv:
            dv = importlib.import_module('DataView')
        else:
            reload(dv)
        dataView = dv.types
    except ImportError:
        warnings.append(['No dataview. Missing data types declarations!'])
    try:
        global iv
        if not iv:
            iv = importlib.import_module('iv')
        else:
            reload(iv)
    except ImportError:
        warnings.append(
                ['No Interface view! Use buildsupport to generate iv.py'])
    parser = parserInitialize(fileName=fileName, string=string)
    if parser:
        # Use Sam & Max output capturer to get errors from ANTLR parser
        with samnmax.capture_ouput() as (stdout, stderr):
            r = parser.processDefinition()
        for e in stderr:
            errors.append([e.strip()])
        for w in stdout:
            warnings.append([w.strip()])
        # Get the root of the AST (type is antlr3.tree.CommonTree)
        root = r.tree
        states = getStateList(root)
        backend = sdlScc_AST(states)
        for c in root.getChildren():
            err, warn = backend.processDefinition(c)
            for e in err:
                errors.append([e] if type(e) is not list else e)
            for w in warn:
                warnings.append([w] if type(w) is not list else w)
        # Post-parsing: additional semantic checks
        # check that all NEXTSTATEs have a correspondingly defined STATE
        # (except the '-' state, which means "stay in the same state')
        for ns in [t.inputString.lower() for t in backend.process.terminators
                if t.kind == 'next_state']:
            if not ns in [s.lower() for s in
                    backend.process.mapping.viewkeys()] + ['-']:
                errors.append(['State definition missing: ' + ns.upper()])
        # TODO: do the same with JOIN/LABEL
        return backend.process, warnings, errors


def parseSingleElement(elem='', string=''):
    '''
        Parse any symbol andreturn syntax error and AST entry
        Used for on-the-fly checks when user edits text
        and for copy/cut to create a new object
    '''
    assert(elem in ('input_part', 'output', 'decision', 'alternative_part',
            'terminator_statement', 'label', 'task', 'procedure_call',
            'text_area', 'state', 'start', 'end'))
    parser = parserInitialize(string=string)
    parserPtr = getattr(parser, elem)
    assert(parserPtr is not None)
    syntaxErrors = []
    semanticErrors = []
    warnings = []
    t = None
    if parser:
        with samnmax.capture_ouput() as (stdout, stderr):
            r = parserPtr()
        for e in stderr:
            syntaxErrors.append(e.strip())
        for w in stdout:
            syntaxErrors.append(w.strip())
        # Get the root of the Antlr-AST to build our own AST entry
        root = r.tree
        backend = sdlScc_AST()
        backendPtr = getattr(backend, elem)
        t, semanticErrors, warnings = backendPtr(root=root, parent=None)
    return(t, syntaxErrors, semanticErrors, warnings,
            backend.process.terminators)


def parserInitialize(fileName=None, string=None):
    ''' Initialize the parser (to be called first) '''
    try:
        char_stream = antlr3.ANTLRFileStream(fileName)
    except:
        try:
            char_stream = antlr3.ANTLRStringStream(string)
        except:
            print '[ERROR] Impossible to initialize the parser'
            return
    lexer = sdl92Lexer(char_stream)
    global tokens
    tokens = antlr3.CommonTokenStream(lexer)
    parser = sdl92Parser(tokens)
    return parser


if __name__ == '__main__':
    if len(sys.argv) > 1:
        print 'Loading file and parsing SDL process'
        fileName = sys.argv[1]
        process, warnings, error = parseProcessDefinition(fileName=fileName)
        print('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        for w in warnings:
            print w
        for e in errors:
            print w
    else:
        print 'Type an expression and Ctrl-D to finish'
        char_stream = antlr3.ANTLRInputStream(sys.stdin)
        lexer = sdl92Lexer(char_stream)
        tokens = antlr3.CommonTokenStream(lexer)
        parser = sdl92Parser(tokens)
        r = parser.expression()
        # Get the root of the AST (type is antlr3.tree.CommonTree)
        root = r.tree
        backend = sdlScc_AST()
        expr, exprType = backend.expression(root)
        print 'Expression type:', exprType

    # root.getToken() returns CommonToken
    #print root.toStringTree()
    #children = root.getChildren()
    #print root.getType(), children
    #nodes = antlr3.tree.CommonTreeNodeStream(root)
    #nodes.setTokenStream(tokens)
