#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

    OpenGEODE - A tiny SDL Editor for TASTE

    AST that can be used to write SDL backends (code generators, etc.)
    In all classes the 'inputString' field corresponds to the exact
    text from the PR file; line and charPositionInLine refer to the
    location of the string in the input PR stream.
    The 'coordinates' field corresponds to the CIF information.
    To use the AST, you must import ogAST and ogParser
    Example of code:

    import ogParser
    import ogAST

    process = ogParser.parseProcessDefinition(filename='test.pr')

    -> process is of type Process (see below)

    Design note:
        classes are used here only for the purpose of convenient
        reading of the AST. There is no object-orientation needed or
        used here.

    See AdaGenerator.py for an example of use.

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


class Expression:
    ''' AST Entry for expressions '''
    def __init__(self, inputString, line, charPositionInLine):
        ''' Initialize Expression attributes '''
        self.inputString = inputString
        self.line = line
        self.charPositionInLine = charPositionInLine
        # left and right are of type Expression (absent if kind=='primary')
        self.left = None
        self.right = None
        # exprType is an ASN.1 type (as exported by asn1scc)
        self.exprType = None
        # kind can be 'primary', in that case value is in 'var',
        # or one of 'plus' 'mul' 'minus' 'or' 'and' 'xor' 'eq' 'neq' 'gt' 'ge'
        # 'lt' 'le' 'div' 'mod' 'append' 'in' 'rem', 'assign'
        self.kind = None
        # var is of type Primary
        self.var = None

    def __repr__(self):
        ''' Debug output for an expression '''
        return '{k}: {exp} ({l},{c})'.format(exp=self.inputString,
                k=self.kind.upper(), l=self.line, c=self.charPositionInLine)


class Primary:
    ''' AST entry for a primary construction '''
    def __init__(self, inputString, line, charPositionInLine):
        ''' Initialize primary attributes (see comments below for details) '''
        self.inputString = inputString
        self.line = line
        self.charPositionInLine = charPositionInLine
        self.op_not = False
        self.op_minus = False
        # kind can be 'primaryId', 'enumeratedValue', 'numericalValue',
        # 'booleanValue', 'expression', 'ifThenElse', 'stringLiteral',
        # 'mantissaBaseExpFloat','emptyString' (SEQUENCE OF type value {}),
        # 'choiceItem', 'sequenceOf', 'sequence', 'choiceDeterminant'
        self.kind = None
        # primType is the ASN.1 type of the primary
        self.primType = None
        # primaryId is a list of elements needed to identify a value
        # for example, "i!j!k(5)" is stored as:
        # [ 'i', 'j', 'k', {'index':[Expression list]}]
        #    (in that case, 5 is an index)
        # other example: "hello(world)" ->
        #      ['hello', {'procParams':[Expression list]'}]
        # (in that case, hello is an operator and world is its parameter)
        # primaryId is set only when kind ==
        #'primaryId', 'enumeratedValue' or 'numericalValue', 'booleanValue'
        self.primaryId = []
        # expr is an Expression
        self.expr = None
        # ifThenElse is a dict:
        # { 'if': Expression, 'then': Expression,
        # 'else': Expression, 'tmpVar': integer}
        # tmpVar can be used if the backend needs a temporary variable
        # to process the ifThenElse
        self.ifThenElse = None
        # stringLiteral is a string (in e.g. a := 'Hello',
        #    'Hello' is the string literal)
        self.stringLiteral = None
        # mantissaBaseExpFloat is a dict:
        # {'mantissa': int, 'base': int, 'exponent': int}
        self.mantissaBaseExpFloat = None
        # choiceItem is a dict : {'choice': string, 'value': Expression}
        self.choiceItem = {}
        # sequenceOf is a list of Primary
        self.sequenceOf = []
        # sequence is a dict : { field1: Expression, field2: Expression }
        self.sequence = {}

    def __repr__(self):
        ''' Debug output for a primary '''
        return 'PRIMARY {k}: {exp} ({l},{c})'.format(exp=self.inputString,
                k=self.kind, l=self.line, c=self.charPositionInLine)


class Decision:
    ''' AST Entry for a decision '''
    def __init__(self):
        ''' A DECISION statement '''
        self.inputString = 'Switch'
        self.line = None
        self.charPositionInLine = None
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 70]
        self.absCoordinates = []
        # kind can be 'any', 'informal_text', or 'question'
        self.kind = None
        # question is an Expression
        self.question = None
        # informalText is a string (when kind == 'informal_text')
        self.informalText = None
        # list of type Answer
        self.answers = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # hint for backends needing a temporary variable to hold the question
        self.tmpVar = -1

    def __repr__(self):
        ''' Debug output for a decision '''
        return 'DECISION {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Answer:
    ''' AST Entry for a decision answer '''
    def __init__(self):
        ''' One ANSWER of a DECISION '''
        self.inputString = 'case'
        self.line = None
        self.charPositionInLine = None
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 35]
        self.absCoordinates = []
        # one of 'closed_range' 'constant' 'open_range' 'else' 'informal_text'
        self.kind = None
        # informalText is a string, when kind == 'informal_text'
        self.informalText = None
        # closedRange is a set of two numbers
        self.closedRange = []
        # constant is an Expression
        #    (contains 'open_range' and 'constant' kinds corresponding value)
        self.constant = None
        # one of 'eq' 'neq' 'gt' 'ge 'lt' 'le'
        self.openRangeOp = None
        # transition is of type Transition
        self.transition = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for an answer '''
        return 'ANSWER {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Task:
    ''' AST Entry for TASKS '''
    def __init__(self):
        ''' Initialize TASK attributes (set of ASSIGN statements) '''
        self.inputString = 'foo := 42'
        self.line = None
        self.charPositionInLine = None
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        # one of 'informal_text', 'assign'
        self.kind = None
        # list of 'assign'-kind Expression
        self.assign = []
        # list of strings
        self.informalText = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a task '''
        return 'TASK {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Output:
    ''' AST Entry for OUTPUT statements '''
    def __init__(self, defName='msgOut'):
        ''' Set of OUTPUT statements '''
        self.inputString = defName
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        self.line = None
        self.charPositionInLine = None
        # one of 'procedure_call', 'output'
        self.kind = None
        # list of {'outputName':ID, 'params':list of Expression, 'tmpVars':[]}
        self.output = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for an Output symbol '''
        return '{kind} {exp} ({l},{c})'.format(exp=self.inputString,
                kind=self.kind.upper(), l=self.line, c=self.charPositionInLine)


class Terminator:
    ''' Terminator elements (join, nextstate, stop) '''
    def __init__(self, defName='Wait', defCoord=[0, 0, 100, 50]):
        ''' Initialize terminator attributes '''
        self.inputString = defName
        # x y w h (relative and absolute)
        self.coordinates = defCoord
        self.absCoordinates = []
        self.line = None
        self.charPositionInLine = None
        # one of 'next_state' 'join' 'stop'
        self.kind = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None
        # optional Label instance (to be placed just before the terminator)
        self.label = None

    def __repr__(self):
        ''' Debug output for terminators '''
        return '{kind} {exp} ({l},{c}) at {x}, {y}'.format(
                exp=self.inputString,
                kind=self.kind.upper(), l=self.line, c=self.charPositionInLine,
                x=self.coordinates[0], y=self.coordinates[1])


class Label:
    ''' AST Entry for a Label '''
    def __init__(self):
        ''' Initialize the label attributes '''
        # inputString holds the label name
        self.inputString = 'Here'
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        self.line = None
        self.charPositionInLine = None
        # optional hyperlink
        self.hyperlink = None
        # No comment for labels - keep to None
        self.comment = None

    def __repr__(self):
        ''' Debug output for a label '''
        return 'LABEL {label} ({l},{c})'.format(label=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Transition:
    ''' AST Entry for a complete transition '''
    def __init__(self):
        ''' Initialize the transition attributes '''
        # list of either Label, Output, Task, Decision
        self.actions = []
        # terminator is of type Terminator (it is optional)
        self.terminator = None


class Input:
    ''' AST Entry for the INPUT symbol '''
    def __init__(self):
        ''' Initialize the Input attributes '''
        self.inputString = 'msgName'
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        self.line = None
        self.charPositionInLine = None
        # provided clause (not supported yet)
        self.provided = None
        # transition is of type Transition
        self.transition = None
        # List of input parameters (strings: each param is a variable)
        # (If there are several inputs in the symbol, there are no parameters)
        self.parameters = []
        # list of inputs and corresponding transitions
        # dictionnary: {'inputName': transitionRef, ... }
        # transitionRef is an index of the process.transitions list
        self.inputlist = {}
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for an INPUT symbol '''
        return 'INPUT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Start:
    ''' AST Entry for the START symbol '''
    def __init__(self):
        ''' Initialize the Start symbol attributes '''
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        # start transition is of type Transition
        self.transition = None
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a START symbol '''
        return 'START'


class Comment:
    ''' AST Entry for COMMENT symbols '''
    def __init__(self):
        ''' Comment symbol '''
        # inputString is the comment value itself
        self.inputString = 'Comment'
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        self.line = None
        self.charPositionInLine = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a COMMENT symbol '''
        return 'COMMENT {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class State:
    ''' AST Entry for STATE symbols '''
    def __init__(self, defName='Wait'):
        ''' Used only for rendering backends - not for code generation '''
        # inputString contains possibly several states (and asterisk)
        self.inputString = defName
        self.line = None
        self.charPositionInLine = None
        # x y w h (relative and absolute)
        self.coordinates = [0, 0, 100, 50]
        self.absCoordinates = []
        # list of type Input
        self.inputs = []
        # optional comment symbol
        self.comment = None
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a STATE symbol '''
        return 'STATE {exp} ({l},{c}) at {x},{y}'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine,
                x=self.coordinates[0], y=self.coordinates[1])


class TextArea:
    ''' AST Entry for text areas (containing declarations/comments) '''
    def __init__(self):
        ''' Text area (raw content for rendering only) '''
        self.inputString = '-- Declare your variables\n\nDCL foo MyInteger;'
        self.line = None
        self.charPositionInLine = None
        # Set default coordinates and width/height
        self.coordinates = [0, 0, 170, 140]
        self.absCoordinates = []
        # optional hyperlink
        self.hyperlink = None

    def __repr__(self):
        ''' Debug output for a text area '''
        return 'TEXTAREA {exp} ({l},{c})'.format(exp=self.inputString,
                l=self.line, c=self.charPositionInLine)


class Process:
    ''' SDL Process entry point '''
    def __init__(self):
        ''' Initializes the AST for a complete SDL process '''
        self.processName = None
        # variables: dictionnary: {variable1Name:asn1SccType, ...}
        # WARNING default value is not supported yet
        self.variables = {}

        # dataView: complete AST of the ASN.1 types
        self.asn1Modules = None
        self.dataView = None

        # input and output signal lists: {'signal': definition from iv.py, ...}
        self.inputSignals = {}
        self.outputSignals = {}

        # start, states, and terminators are useful for rendering backends
        self.start = None
        self.states = []
        self.terminators = []

        # list of operators (not supported) and procedures
        self.operators = {}
        # procedures: same form as outputlist:
        #     {'procedureName': definition from iv.py, ...}
        # only supports procedures as sync RI specified in the
        # TASTE interface view
        # use operators for other purposes
        self.procedures = {}

        # list of type TextArea. Useful for rendering only
        # use 'variables', 'operators' and 'procedures' to get useful content
        self.textAreas = []

        # The Mapping structure should be used for code generation backends
        # dictionnary: {'stateName': [class Input1, Input2,...], ...}
        # then class Input contains the inputs list and corresponding transition
        self.mapping = {}

        # list of type Transition - use 'mapping' to map index to inputs/states
        self.transitions = []
