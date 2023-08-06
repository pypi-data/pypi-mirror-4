# $ANTLR 3.1.3 Mar 17, 2009 19:23:44 sdl92.g 2013-01-21 22:32:31

import sys
from antlr3 import *
from antlr3.compat import set, frozenset

from antlr3.tree import *



# for convenience in actions
HIDDEN = BaseRecognizer.HIDDEN

# token types
NUMBER_OF_INSTANCES=21
INPUTLIST=65
COMMENT2=163
EXPONENT=125
MANTISSA=123
LT=95
TRANSITION=22
MOD=110
RESET=33
GROUND=72
BitStringLiteral=112
NOT=126
SEQOF=10
T__167=167
TEXTAREA_CONTENT=74
T__168=168
EOF=-1
SIGNAL_LIST=27
T__166=166
ACTION=30
ENDTEXT=19
CREATE=98
NEXTSTATE=50
L_PAREN=85
THIS=99
RETURN=53
VIAPATH=45
PROCEDURE_CALL=31
BASE=124
EXPORT=34
EQ=92
COMMENT=6
ENDALTERNATIVE=89
GEODE=131
INFORMAL_TEXT=66
D=137
E=141
F=145
GE=97
G=146
FIELD_NAME=56
A=134
IMPLIES=101
B=156
OCTSTR=15
C=138
L=139
M=155
EMPTYSTR=11
N=135
O=147
TERMINATOR=52
H=148
I=144
NULL=117
J=157
ELSE=41
K=140
ANSWER=37
U=152
T=150
W=154
V=153
STOP=127
Q=164
PRIMARY=57
INT=79
P=142
TASK=75
S=143
R=149
VALUE=7
Y=136
ALPHA=160
X=151
FI=61
Z=165
SEQUENCE=9
MINUS_INFINITY=119
WS=162
PRIORITY=84
VARIABLE=67
SPECIFIC=130
FloatingPointLiteral=120
NONE=83
OR=102
INPUT_NONE=24
OctetStringLiteral=113
CONSTANT=40
GT=94
CALL=88
FALSE=115
OUTPUT=46
IFTHENELSE=5
APPEND=108
L_BRACKET=121
PRIMARY_ID=58
DIGITS=18
HYPERLINK=63
INPUT=28
Exponent=161
FLOAT=12
ENDSTATE=81
PROCEDURE_NAME=54
AND=104
ID=100
ASTERISK=82
FLOAT2=13
IF=59
STR=159
STIMULUS=29
IN=105
THEN=60
ENDDECISION=90
PROVIDED=26
COMMA=87
OPEN_RANGE=39
ALL=42
PLUS=106
DOT=158
EXPRESSION=17
CHOICE=8
TASK_BODY=76
CLOSED_RANGE=38
PARAMS=55
STATE=23
BITSTR=14
XOR=103
STATELIST=64
DASH=107
TO=43
DCL=70
ENDPROCESS=78
ASSIG_OP=133
VIA=44
SORT=69
SAVE=25
SET=32
REM=111
TEXT=49
MINUS=71
SEMI=128
TRUE=114
PROCEDURE=132
R_BRACKET=122
JOIN=51
R_PAREN=86
TEXTAREA=73
StringLiteral=116
T__175=175
OUTPUT_BODY=47
T__174=174
T__173=173
T__172=172
NEQ=93
ANY=91
T__177=177
QUESTION=77
T__176=176
LABEL=4
PLUS_INFINITY=118
T__171=171
KEEP=129
T__170=170
ASSIGN=48
VARIABLES=68
ALTERNATIVE=36
START=80
CIF=62
DECISION=35
DIV=109
PROCESS=20
T__169=169
LE=96
STRING=16

# token names
tokenNames = [
    "<invalid>", "<EOR>", "<DOWN>", "<UP>", 
    "LABEL", "IFTHENELSE", "COMMENT", "VALUE", "CHOICE", "SEQUENCE", "SEQOF", 
    "EMPTYSTR", "FLOAT", "FLOAT2", "BITSTR", "OCTSTR", "STRING", "EXPRESSION", 
    "DIGITS", "ENDTEXT", "PROCESS", "NUMBER_OF_INSTANCES", "TRANSITION", 
    "STATE", "INPUT_NONE", "SAVE", "PROVIDED", "SIGNAL_LIST", "INPUT", "STIMULUS", 
    "ACTION", "PROCEDURE_CALL", "SET", "RESET", "EXPORT", "DECISION", "ALTERNATIVE", 
    "ANSWER", "CLOSED_RANGE", "OPEN_RANGE", "CONSTANT", "ELSE", "ALL", "TO", 
    "VIA", "VIAPATH", "OUTPUT", "OUTPUT_BODY", "ASSIGN", "TEXT", "NEXTSTATE", 
    "JOIN", "TERMINATOR", "RETURN", "PROCEDURE_NAME", "PARAMS", "FIELD_NAME", 
    "PRIMARY", "PRIMARY_ID", "IF", "THEN", "FI", "CIF", "HYPERLINK", "STATELIST", 
    "INPUTLIST", "INFORMAL_TEXT", "VARIABLE", "VARIABLES", "SORT", "DCL", 
    "MINUS", "GROUND", "TEXTAREA", "TEXTAREA_CONTENT", "TASK", "TASK_BODY", 
    "QUESTION", "ENDPROCESS", "INT", "START", "ENDSTATE", "ASTERISK", "NONE", 
    "PRIORITY", "L_PAREN", "R_PAREN", "COMMA", "CALL", "ENDALTERNATIVE", 
    "ENDDECISION", "ANY", "EQ", "NEQ", "GT", "LT", "LE", "GE", "CREATE", 
    "THIS", "ID", "IMPLIES", "OR", "XOR", "AND", "IN", "PLUS", "DASH", "APPEND", 
    "DIV", "MOD", "REM", "BitStringLiteral", "OctetStringLiteral", "TRUE", 
    "FALSE", "StringLiteral", "NULL", "PLUS_INFINITY", "MINUS_INFINITY", 
    "FloatingPointLiteral", "L_BRACKET", "R_BRACKET", "MANTISSA", "BASE", 
    "EXPONENT", "NOT", "STOP", "SEMI", "KEEP", "SPECIFIC", "GEODE", "PROCEDURE", 
    "ASSIG_OP", "A", "N", "Y", "D", "C", "L", "K", "E", "P", "S", "I", "F", 
    "G", "O", "H", "R", "T", "X", "U", "V", "W", "M", "B", "J", "DOT", "STR", 
    "ALPHA", "Exponent", "WS", "COMMENT2", "Q", "Z", "':'", "'ALL'", "'!'", 
    "'(.'", "'.)'", "'ERROR'", "'ACTIVE'", "'ANY'", "'IMPORT'", "'VIEW'", 
    "'/* CIF'", "'*/'"
]




class sdl92Parser(Parser):
    grammarFileName = "sdl92.g"
    antlr_version = version_str_to_tuple("3.1.3 Mar 17, 2009 19:23:44")
    antlr_version_str = "3.1.3 Mar 17, 2009 19:23:44"
    tokenNames = tokenNames

    def __init__(self, input, state=None, *args, **kwargs):
        if state is None:
            state = RecognizerSharedState()

        super(sdl92Parser, self).__init__(input, state, *args, **kwargs)

        self.dfa2 = self.DFA2(
            self, 2,
            eot = self.DFA2_eot,
            eof = self.DFA2_eof,
            min = self.DFA2_min,
            max = self.DFA2_max,
            accept = self.DFA2_accept,
            special = self.DFA2_special,
            transition = self.DFA2_transition
            )

        self.dfa9 = self.DFA9(
            self, 9,
            eot = self.DFA9_eot,
            eof = self.DFA9_eof,
            min = self.DFA9_min,
            max = self.DFA9_max,
            accept = self.DFA9_accept,
            special = self.DFA9_special,
            transition = self.DFA9_transition
            )

        self.dfa21 = self.DFA21(
            self, 21,
            eot = self.DFA21_eot,
            eof = self.DFA21_eof,
            min = self.DFA21_min,
            max = self.DFA21_max,
            accept = self.DFA21_accept,
            special = self.DFA21_special,
            transition = self.DFA21_transition
            )

        self.dfa30 = self.DFA30(
            self, 30,
            eot = self.DFA30_eot,
            eof = self.DFA30_eof,
            min = self.DFA30_min,
            max = self.DFA30_max,
            accept = self.DFA30_accept,
            special = self.DFA30_special,
            transition = self.DFA30_transition
            )

        self.dfa31 = self.DFA31(
            self, 31,
            eot = self.DFA31_eot,
            eof = self.DFA31_eof,
            min = self.DFA31_min,
            max = self.DFA31_max,
            accept = self.DFA31_accept,
            special = self.DFA31_special,
            transition = self.DFA31_transition
            )

        self.dfa38 = self.DFA38(
            self, 38,
            eot = self.DFA38_eot,
            eof = self.DFA38_eof,
            min = self.DFA38_min,
            max = self.DFA38_max,
            accept = self.DFA38_accept,
            special = self.DFA38_special,
            transition = self.DFA38_transition
            )

        self.dfa36 = self.DFA36(
            self, 36,
            eot = self.DFA36_eot,
            eof = self.DFA36_eof,
            min = self.DFA36_min,
            max = self.DFA36_max,
            accept = self.DFA36_accept,
            special = self.DFA36_special,
            transition = self.DFA36_transition
            )

        self.dfa37 = self.DFA37(
            self, 37,
            eot = self.DFA37_eot,
            eof = self.DFA37_eof,
            min = self.DFA37_min,
            max = self.DFA37_max,
            accept = self.DFA37_accept,
            special = self.DFA37_special,
            transition = self.DFA37_transition
            )

        self.dfa39 = self.DFA39(
            self, 39,
            eot = self.DFA39_eot,
            eof = self.DFA39_eof,
            min = self.DFA39_min,
            max = self.DFA39_max,
            accept = self.DFA39_accept,
            special = self.DFA39_special,
            transition = self.DFA39_transition
            )

        self.dfa40 = self.DFA40(
            self, 40,
            eot = self.DFA40_eot,
            eof = self.DFA40_eof,
            min = self.DFA40_min,
            max = self.DFA40_max,
            accept = self.DFA40_accept,
            special = self.DFA40_special,
            transition = self.DFA40_transition
            )

        self.dfa51 = self.DFA51(
            self, 51,
            eot = self.DFA51_eot,
            eof = self.DFA51_eof,
            min = self.DFA51_min,
            max = self.DFA51_max,
            accept = self.DFA51_accept,
            special = self.DFA51_special,
            transition = self.DFA51_transition
            )

        self.dfa49 = self.DFA49(
            self, 49,
            eot = self.DFA49_eot,
            eof = self.DFA49_eof,
            min = self.DFA49_min,
            max = self.DFA49_max,
            accept = self.DFA49_accept,
            special = self.DFA49_special,
            transition = self.DFA49_transition
            )

        self.dfa59 = self.DFA59(
            self, 59,
            eot = self.DFA59_eot,
            eof = self.DFA59_eof,
            min = self.DFA59_min,
            max = self.DFA59_max,
            accept = self.DFA59_accept,
            special = self.DFA59_special,
            transition = self.DFA59_transition
            )

        self.dfa89 = self.DFA89(
            self, 89,
            eot = self.DFA89_eot,
            eof = self.DFA89_eof,
            min = self.DFA89_min,
            max = self.DFA89_max,
            accept = self.DFA89_accept,
            special = self.DFA89_special,
            transition = self.DFA89_transition
            )

        self.dfa99 = self.DFA99(
            self, 99,
            eot = self.DFA99_eot,
            eof = self.DFA99_eof,
            min = self.DFA99_min,
            max = self.DFA99_max,
            accept = self.DFA99_accept,
            special = self.DFA99_special,
            transition = self.DFA99_transition
            )

        self.dfa109 = self.DFA109(
            self, 109,
            eot = self.DFA109_eot,
            eof = self.DFA109_eof,
            min = self.DFA109_min,
            max = self.DFA109_max,
            accept = self.DFA109_accept,
            special = self.DFA109_special,
            transition = self.DFA109_transition
            )






        self._adaptor = None
        self.adaptor = CommonTreeAdaptor()
                


        
    def getTreeAdaptor(self):
        return self._adaptor

    def setTreeAdaptor(self, adaptor):
        self._adaptor = adaptor

    adaptor = property(getTreeAdaptor, setTreeAdaptor)


    class processDefinition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.processDefinition_return, self).__init__()

            self.tree = None




    # $ANTLR start "processDefinition"
    # sdl92.g:91:1: processDefinition : PROCESS process_id ( number_of_instances )? end ( text_area )* processBody ENDPROCESS ( process_id )? end -> ^( PROCESS process_id ( number_of_instances )? ( text_area )* processBody ) ;
    def processDefinition(self, ):

        retval = self.processDefinition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PROCESS1 = None
        ENDPROCESS7 = None
        process_id2 = None

        number_of_instances3 = None

        end4 = None

        text_area5 = None

        processBody6 = None

        process_id8 = None

        end9 = None


        PROCESS1_tree = None
        ENDPROCESS7_tree = None
        stream_PROCESS = RewriteRuleTokenStream(self._adaptor, "token PROCESS")
        stream_ENDPROCESS = RewriteRuleTokenStream(self._adaptor, "token ENDPROCESS")
        stream_process_id = RewriteRuleSubtreeStream(self._adaptor, "rule process_id")
        stream_processBody = RewriteRuleSubtreeStream(self._adaptor, "rule processBody")
        stream_text_area = RewriteRuleSubtreeStream(self._adaptor, "rule text_area")
        stream_number_of_instances = RewriteRuleSubtreeStream(self._adaptor, "rule number_of_instances")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:92:9: ( PROCESS process_id ( number_of_instances )? end ( text_area )* processBody ENDPROCESS ( process_id )? end -> ^( PROCESS process_id ( number_of_instances )? ( text_area )* processBody ) )
                # sdl92.g:92:17: PROCESS process_id ( number_of_instances )? end ( text_area )* processBody ENDPROCESS ( process_id )? end
                pass 
                PROCESS1=self.match(self.input, PROCESS, self.FOLLOW_PROCESS_in_processDefinition880) 
                if self._state.backtracking == 0:
                    stream_PROCESS.add(PROCESS1)
                self._state.following.append(self.FOLLOW_process_id_in_processDefinition882)
                process_id2 = self.process_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_process_id.add(process_id2.tree)
                # sdl92.g:92:36: ( number_of_instances )?
                alt1 = 2
                LA1_0 = self.input.LA(1)

                if (LA1_0 == L_PAREN) :
                    alt1 = 1
                if alt1 == 1:
                    # sdl92.g:0:0: number_of_instances
                    pass 
                    self._state.following.append(self.FOLLOW_number_of_instances_in_processDefinition884)
                    number_of_instances3 = self.number_of_instances()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_number_of_instances.add(number_of_instances3.tree)



                self._state.following.append(self.FOLLOW_end_in_processDefinition887)
                end4 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end4.tree)
                # sdl92.g:93:17: ( text_area )*
                while True: #loop2
                    alt2 = 2
                    alt2 = self.dfa2.predict(self.input)
                    if alt2 == 1:
                        # sdl92.g:0:0: text_area
                        pass 
                        self._state.following.append(self.FOLLOW_text_area_in_processDefinition905)
                        text_area5 = self.text_area()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_text_area.add(text_area5.tree)


                    else:
                        break #loop2
                self._state.following.append(self.FOLLOW_processBody_in_processDefinition924)
                processBody6 = self.processBody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_processBody.add(processBody6.tree)
                ENDPROCESS7=self.match(self.input, ENDPROCESS, self.FOLLOW_ENDPROCESS_in_processDefinition926) 
                if self._state.backtracking == 0:
                    stream_ENDPROCESS.add(ENDPROCESS7)
                # sdl92.g:94:40: ( process_id )?
                alt3 = 2
                LA3_0 = self.input.LA(1)

                if (LA3_0 == ID) :
                    alt3 = 1
                if alt3 == 1:
                    # sdl92.g:0:0: process_id
                    pass 
                    self._state.following.append(self.FOLLOW_process_id_in_processDefinition928)
                    process_id8 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_process_id.add(process_id8.tree)



                self._state.following.append(self.FOLLOW_end_in_processDefinition931)
                end9 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end9.tree)

                # AST Rewrite
                # elements: PROCESS, process_id, number_of_instances, text_area, processBody
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 94:58: -> ^( PROCESS process_id ( number_of_instances )? ( text_area )* processBody )
                    # sdl92.g:94:61: ^( PROCESS process_id ( number_of_instances )? ( text_area )* processBody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROCESS.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_process_id.nextTree())
                    # sdl92.g:94:82: ( number_of_instances )?
                    if stream_number_of_instances.hasNext():
                        self._adaptor.addChild(root_1, stream_number_of_instances.nextTree())


                    stream_number_of_instances.reset();
                    # sdl92.g:94:103: ( text_area )*
                    while stream_text_area.hasNext():
                        self._adaptor.addChild(root_1, stream_text_area.nextTree())


                    stream_text_area.reset();
                    self._adaptor.addChild(root_1, stream_processBody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "processDefinition"

    class text_area_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.text_area_return, self).__init__()

            self.tree = None




    # $ANTLR start "text_area"
    # sdl92.g:99:1: text_area : cif ( content )? cif_end_text -> ^( TEXTAREA cif ( content )? cif_end_text ) ;
    def text_area(self, ):

        retval = self.text_area_return()
        retval.start = self.input.LT(1)

        root_0 = None

        cif10 = None

        content11 = None

        cif_end_text12 = None


        stream_content = RewriteRuleSubtreeStream(self._adaptor, "rule content")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_cif_end_text = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end_text")
        try:
            try:
                # sdl92.g:100:9: ( cif ( content )? cif_end_text -> ^( TEXTAREA cif ( content )? cif_end_text ) )
                # sdl92.g:100:17: cif ( content )? cif_end_text
                pass 
                self._state.following.append(self.FOLLOW_cif_in_text_area991)
                cif10 = self.cif()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif.add(cif10.tree)
                # sdl92.g:101:17: ( content )?
                alt4 = 2
                LA4_0 = self.input.LA(1)

                if (LA4_0 == DCL) :
                    alt4 = 1
                elif (LA4_0 == 176) :
                    LA4_2 = self.input.LA(2)

                    if (self.synpred4_sdl92()) :
                        alt4 = 1
                if alt4 == 1:
                    # sdl92.g:0:0: content
                    pass 
                    self._state.following.append(self.FOLLOW_content_in_text_area1009)
                    content11 = self.content()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_content.add(content11.tree)



                self._state.following.append(self.FOLLOW_cif_end_text_in_text_area1079)
                cif_end_text12 = self.cif_end_text()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end_text.add(cif_end_text12.tree)

                # AST Rewrite
                # elements: cif_end_text, cif, content
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 102:73: -> ^( TEXTAREA cif ( content )? cif_end_text )
                    # sdl92.g:102:76: ^( TEXTAREA cif ( content )? cif_end_text )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TEXTAREA, "TEXTAREA"), root_1)

                    self._adaptor.addChild(root_1, stream_cif.nextTree())
                    # sdl92.g:102:91: ( content )?
                    if stream_content.hasNext():
                        self._adaptor.addChild(root_1, stream_content.nextTree())


                    stream_content.reset();
                    self._adaptor.addChild(root_1, stream_cif_end_text.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "text_area"

    class content_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.content_return, self).__init__()

            self.tree = None




    # $ANTLR start "content"
    # sdl92.g:104:1: content : ( variable_definition )* -> ^( TEXTAREA_CONTENT ( variable_definition )* ) ;
    def content(self, ):

        retval = self.content_return()
        retval.start = self.input.LT(1)

        root_0 = None

        variable_definition13 = None


        stream_variable_definition = RewriteRuleSubtreeStream(self._adaptor, "rule variable_definition")
        try:
            try:
                # sdl92.g:105:9: ( ( variable_definition )* -> ^( TEXTAREA_CONTENT ( variable_definition )* ) )
                # sdl92.g:105:17: ( variable_definition )*
                pass 
                # sdl92.g:105:17: ( variable_definition )*
                while True: #loop5
                    alt5 = 2
                    LA5_0 = self.input.LA(1)

                    if (LA5_0 == DCL) :
                        alt5 = 1


                    if alt5 == 1:
                        # sdl92.g:0:0: variable_definition
                        pass 
                        self._state.following.append(self.FOLLOW_variable_definition_in_content1157)
                        variable_definition13 = self.variable_definition()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_definition.add(variable_definition13.tree)


                    else:
                        break #loop5

                # AST Rewrite
                # elements: variable_definition
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 105:73: -> ^( TEXTAREA_CONTENT ( variable_definition )* )
                    # sdl92.g:105:76: ^( TEXTAREA_CONTENT ( variable_definition )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TEXTAREA_CONTENT, "TEXTAREA_CONTENT"), root_1)

                    # sdl92.g:105:95: ( variable_definition )*
                    while stream_variable_definition.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_definition.nextTree())


                    stream_variable_definition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "content"

    class variable_definition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_definition_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_definition"
    # sdl92.g:107:1: variable_definition : DCL variables_of_sort ( ',' variables_of_sort )* end -> ^( DCL ( variables_of_sort )+ ) ;
    def variable_definition(self, ):

        retval = self.variable_definition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DCL14 = None
        char_literal16 = None
        variables_of_sort15 = None

        variables_of_sort17 = None

        end18 = None


        DCL14_tree = None
        char_literal16_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_DCL = RewriteRuleTokenStream(self._adaptor, "token DCL")
        stream_variables_of_sort = RewriteRuleSubtreeStream(self._adaptor, "rule variables_of_sort")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:108:9: ( DCL variables_of_sort ( ',' variables_of_sort )* end -> ^( DCL ( variables_of_sort )+ ) )
                # sdl92.g:108:17: DCL variables_of_sort ( ',' variables_of_sort )* end
                pass 
                DCL14=self.match(self.input, DCL, self.FOLLOW_DCL_in_variable_definition1224) 
                if self._state.backtracking == 0:
                    stream_DCL.add(DCL14)
                self._state.following.append(self.FOLLOW_variables_of_sort_in_variable_definition1226)
                variables_of_sort15 = self.variables_of_sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variables_of_sort.add(variables_of_sort15.tree)
                # sdl92.g:108:39: ( ',' variables_of_sort )*
                while True: #loop6
                    alt6 = 2
                    LA6_0 = self.input.LA(1)

                    if (LA6_0 == COMMA) :
                        alt6 = 1


                    if alt6 == 1:
                        # sdl92.g:108:40: ',' variables_of_sort
                        pass 
                        char_literal16=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_variable_definition1229) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal16)
                        self._state.following.append(self.FOLLOW_variables_of_sort_in_variable_definition1231)
                        variables_of_sort17 = self.variables_of_sort()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variables_of_sort.add(variables_of_sort17.tree)


                    else:
                        break #loop6
                self._state.following.append(self.FOLLOW_end_in_variable_definition1235)
                end18 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end18.tree)

                # AST Rewrite
                # elements: DCL, variables_of_sort
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 108:73: -> ^( DCL ( variables_of_sort )+ )
                    # sdl92.g:108:76: ^( DCL ( variables_of_sort )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_DCL.nextNode(), root_1)

                    # sdl92.g:108:82: ( variables_of_sort )+
                    if not (stream_variables_of_sort.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variables_of_sort.hasNext():
                        self._adaptor.addChild(root_1, stream_variables_of_sort.nextTree())


                    stream_variables_of_sort.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_definition"

    class variables_of_sort_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variables_of_sort_return, self).__init__()

            self.tree = None




    # $ANTLR start "variables_of_sort"
    # sdl92.g:110:1: variables_of_sort : variable_id ( ',' variable_id )* sort ( ':=' ground_expression )? -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? ) ;
    def variables_of_sort(self, ):

        retval = self.variables_of_sort_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal20 = None
        string_literal23 = None
        variable_id19 = None

        variable_id21 = None

        sort22 = None

        ground_expression24 = None


        char_literal20_tree = None
        string_literal23_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ASSIG_OP = RewriteRuleTokenStream(self._adaptor, "token ASSIG_OP")
        stream_sort = RewriteRuleSubtreeStream(self._adaptor, "rule sort")
        stream_ground_expression = RewriteRuleSubtreeStream(self._adaptor, "rule ground_expression")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        try:
            try:
                # sdl92.g:111:9: ( variable_id ( ',' variable_id )* sort ( ':=' ground_expression )? -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? ) )
                # sdl92.g:111:17: variable_id ( ',' variable_id )* sort ( ':=' ground_expression )?
                pass 
                self._state.following.append(self.FOLLOW_variable_id_in_variables_of_sort1271)
                variable_id19 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id19.tree)
                # sdl92.g:111:29: ( ',' variable_id )*
                while True: #loop7
                    alt7 = 2
                    LA7_0 = self.input.LA(1)

                    if (LA7_0 == COMMA) :
                        alt7 = 1


                    if alt7 == 1:
                        # sdl92.g:111:30: ',' variable_id
                        pass 
                        char_literal20=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_variables_of_sort1274) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal20)
                        self._state.following.append(self.FOLLOW_variable_id_in_variables_of_sort1276)
                        variable_id21 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id21.tree)


                    else:
                        break #loop7
                self._state.following.append(self.FOLLOW_sort_in_variables_of_sort1280)
                sort22 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort.add(sort22.tree)
                # sdl92.g:111:53: ( ':=' ground_expression )?
                alt8 = 2
                LA8_0 = self.input.LA(1)

                if (LA8_0 == ASSIG_OP) :
                    alt8 = 1
                if alt8 == 1:
                    # sdl92.g:111:54: ':=' ground_expression
                    pass 
                    string_literal23=self.match(self.input, ASSIG_OP, self.FOLLOW_ASSIG_OP_in_variables_of_sort1283) 
                    if self._state.backtracking == 0:
                        stream_ASSIG_OP.add(string_literal23)
                    self._state.following.append(self.FOLLOW_ground_expression_in_variables_of_sort1285)
                    ground_expression24 = self.ground_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_ground_expression.add(ground_expression24.tree)




                # AST Rewrite
                # elements: ground_expression, sort, variable_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 111:82: -> ^( VARIABLES ( variable_id )+ sort ( ground_expression )? )
                    # sdl92.g:111:85: ^( VARIABLES ( variable_id )+ sort ( ground_expression )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VARIABLES, "VARIABLES"), root_1)

                    # sdl92.g:111:97: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()
                    self._adaptor.addChild(root_1, stream_sort.nextTree())
                    # sdl92.g:111:115: ( ground_expression )?
                    if stream_ground_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_ground_expression.nextTree())


                    stream_ground_expression.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variables_of_sort"

    class ground_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.ground_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "ground_expression"
    # sdl92.g:113:1: ground_expression : expression -> ^( GROUND expression ) ;
    def ground_expression(self, ):

        retval = self.ground_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression25 = None


        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:114:9: ( expression -> ^( GROUND expression ) )
                # sdl92.g:114:17: expression
                pass 
                self._state.following.append(self.FOLLOW_expression_in_ground_expression1326)
                expression25 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression25.tree)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 114:37: -> ^( GROUND expression )
                    # sdl92.g:114:40: ^( GROUND expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(GROUND, "GROUND"), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "ground_expression"

    class number_of_instances_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.number_of_instances_return, self).__init__()

            self.tree = None




    # $ANTLR start "number_of_instances"
    # sdl92.g:116:1: number_of_instances : '(' initial_number= INT ',' maximum_number= INT ')' -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number) ;
    def number_of_instances(self, ):

        retval = self.number_of_instances_return()
        retval.start = self.input.LT(1)

        root_0 = None

        initial_number = None
        maximum_number = None
        char_literal26 = None
        char_literal27 = None
        char_literal28 = None

        initial_number_tree = None
        maximum_number_tree = None
        char_literal26_tree = None
        char_literal27_tree = None
        char_literal28_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")

        try:
            try:
                # sdl92.g:117:9: ( '(' initial_number= INT ',' maximum_number= INT ')' -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number) )
                # sdl92.g:117:17: '(' initial_number= INT ',' maximum_number= INT ')'
                pass 
                char_literal26=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_number_of_instances1365) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal26)
                initial_number=self.match(self.input, INT, self.FOLLOW_INT_in_number_of_instances1369) 
                if self._state.backtracking == 0:
                    stream_INT.add(initial_number)
                char_literal27=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_number_of_instances1371) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(char_literal27)
                maximum_number=self.match(self.input, INT, self.FOLLOW_INT_in_number_of_instances1375) 
                if self._state.backtracking == 0:
                    stream_INT.add(maximum_number)
                char_literal28=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_number_of_instances1377) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal28)

                # AST Rewrite
                # elements: initial_number, maximum_number
                # token labels: maximum_number, initial_number
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_maximum_number = RewriteRuleTokenStream(self._adaptor, "token maximum_number", maximum_number)
                    stream_initial_number = RewriteRuleTokenStream(self._adaptor, "token initial_number", initial_number)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 117:74: -> ^( NUMBER_OF_INSTANCES $initial_number $maximum_number)
                    # sdl92.g:117:77: ^( NUMBER_OF_INSTANCES $initial_number $maximum_number)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(NUMBER_OF_INSTANCES, "NUMBER_OF_INSTANCES"), root_1)

                    self._adaptor.addChild(root_1, stream_initial_number.nextNode())
                    self._adaptor.addChild(root_1, stream_maximum_number.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "number_of_instances"

    class processBody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.processBody_return, self).__init__()

            self.tree = None




    # $ANTLR start "processBody"
    # sdl92.g:120:1: processBody : ( start )? ( state )* ;
    def processBody(self, ):

        retval = self.processBody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        start29 = None

        state30 = None



        try:
            try:
                # sdl92.g:121:9: ( ( start )? ( state )* )
                # sdl92.g:121:17: ( start )? ( state )*
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:121:17: ( start )?
                alt9 = 2
                alt9 = self.dfa9.predict(self.input)
                if alt9 == 1:
                    # sdl92.g:0:0: start
                    pass 
                    self._state.following.append(self.FOLLOW_start_in_processBody1427)
                    start29 = self.start()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, start29.tree)



                # sdl92.g:121:24: ( state )*
                while True: #loop10
                    alt10 = 2
                    LA10_0 = self.input.LA(1)

                    if (LA10_0 == STATE or LA10_0 == 176) :
                        alt10 = 1


                    if alt10 == 1:
                        # sdl92.g:121:25: state
                        pass 
                        self._state.following.append(self.FOLLOW_state_in_processBody1431)
                        state30 = self.state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, state30.tree)


                    else:
                        break #loop10



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "processBody"

    class start_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.start_return, self).__init__()

            self.tree = None




    # $ANTLR start "start"
    # sdl92.g:123:1: start : ( cif )? ( hyperlink )? START end transition -> ^( START ( cif )? ( hyperlink )? ( end )? transition ) ;
    def start(self, ):

        retval = self.start_return()
        retval.start = self.input.LT(1)

        root_0 = None

        START33 = None
        cif31 = None

        hyperlink32 = None

        end34 = None

        transition35 = None


        START33_tree = None
        stream_START = RewriteRuleTokenStream(self._adaptor, "token START")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:124:9: ( ( cif )? ( hyperlink )? START end transition -> ^( START ( cif )? ( hyperlink )? ( end )? transition ) )
                # sdl92.g:124:17: ( cif )? ( hyperlink )? START end transition
                pass 
                # sdl92.g:124:17: ( cif )?
                alt11 = 2
                LA11_0 = self.input.LA(1)

                if (LA11_0 == 176) :
                    LA11_1 = self.input.LA(2)

                    if (LA11_1 == LABEL or LA11_1 == COMMENT or LA11_1 == STATE or LA11_1 == PROVIDED or LA11_1 == INPUT or LA11_1 == DECISION or LA11_1 == ANSWER or LA11_1 == OUTPUT or (TEXT <= LA11_1 <= JOIN) or LA11_1 == TASK or LA11_1 == START or LA11_1 == PROCEDURE) :
                        alt11 = 1
                if alt11 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_start1466)
                    cif31 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif31.tree)



                # sdl92.g:125:17: ( hyperlink )?
                alt12 = 2
                LA12_0 = self.input.LA(1)

                if (LA12_0 == 176) :
                    alt12 = 1
                if alt12 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_start1485)
                    hyperlink32 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink32.tree)



                START33=self.match(self.input, START, self.FOLLOW_START_in_start1504) 
                if self._state.backtracking == 0:
                    stream_START.add(START33)
                self._state.following.append(self.FOLLOW_end_in_start1506)
                end34 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end34.tree)
                self._state.following.append(self.FOLLOW_transition_in_start1524)
                transition35 = self.transition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_transition.add(transition35.tree)

                # AST Rewrite
                # elements: transition, cif, end, START, hyperlink
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 127:48: -> ^( START ( cif )? ( hyperlink )? ( end )? transition )
                    # sdl92.g:127:51: ^( START ( cif )? ( hyperlink )? ( end )? transition )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_START.nextNode(), root_1)

                    # sdl92.g:127:59: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:127:64: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:127:75: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_transition.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "start"

    class state_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_return, self).__init__()

            self.tree = None




    # $ANTLR start "state"
    # sdl92.g:130:1: state : ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* ) ;
    def state(self, ):

        retval = self.state_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STATE38 = None
        ENDSTATE41 = None
        e = None

        f = None

        cif36 = None

        hyperlink37 = None

        statelist39 = None

        state_part40 = None

        statename42 = None


        STATE38_tree = None
        ENDSTATE41_tree = None
        stream_STATE = RewriteRuleTokenStream(self._adaptor, "token STATE")
        stream_ENDSTATE = RewriteRuleTokenStream(self._adaptor, "token ENDSTATE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_statelist = RewriteRuleSubtreeStream(self._adaptor, "rule statelist")
        stream_state_part = RewriteRuleSubtreeStream(self._adaptor, "rule state_part")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:131:9: ( ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* ) )
                # sdl92.g:131:17: ( cif )? ( hyperlink )? STATE statelist e= end ( state_part )* ENDSTATE ( statename )? f= end
                pass 
                # sdl92.g:131:17: ( cif )?
                alt13 = 2
                LA13_0 = self.input.LA(1)

                if (LA13_0 == 176) :
                    LA13_1 = self.input.LA(2)

                    if (LA13_1 == LABEL or LA13_1 == COMMENT or LA13_1 == STATE or LA13_1 == PROVIDED or LA13_1 == INPUT or LA13_1 == DECISION or LA13_1 == ANSWER or LA13_1 == OUTPUT or (TEXT <= LA13_1 <= JOIN) or LA13_1 == TASK or LA13_1 == START or LA13_1 == PROCEDURE) :
                        alt13 = 1
                if alt13 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_state1587)
                    cif36 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif36.tree)



                # sdl92.g:132:17: ( hyperlink )?
                alt14 = 2
                LA14_0 = self.input.LA(1)

                if (LA14_0 == 176) :
                    alt14 = 1
                if alt14 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_state1607)
                    hyperlink37 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink37.tree)



                STATE38=self.match(self.input, STATE, self.FOLLOW_STATE_in_state1626) 
                if self._state.backtracking == 0:
                    stream_STATE.add(STATE38)
                self._state.following.append(self.FOLLOW_statelist_in_state1628)
                statelist39 = self.statelist()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statelist.add(statelist39.tree)
                self._state.following.append(self.FOLLOW_end_in_state1632)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                # sdl92.g:134:17: ( state_part )*
                while True: #loop15
                    alt15 = 2
                    LA15_0 = self.input.LA(1)

                    if ((SAVE <= LA15_0 <= PROVIDED) or LA15_0 == INPUT or LA15_0 == 176) :
                        alt15 = 1


                    if alt15 == 1:
                        # sdl92.g:134:18: state_part
                        pass 
                        self._state.following.append(self.FOLLOW_state_part_in_state1651)
                        state_part40 = self.state_part()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_state_part.add(state_part40.tree)


                    else:
                        break #loop15
                ENDSTATE41=self.match(self.input, ENDSTATE, self.FOLLOW_ENDSTATE_in_state1671) 
                if self._state.backtracking == 0:
                    stream_ENDSTATE.add(ENDSTATE41)
                # sdl92.g:135:26: ( statename )?
                alt16 = 2
                LA16_0 = self.input.LA(1)

                if (LA16_0 == ID) :
                    alt16 = 1
                if alt16 == 1:
                    # sdl92.g:0:0: statename
                    pass 
                    self._state.following.append(self.FOLLOW_statename_in_state1673)
                    statename42 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_statename.add(statename42.tree)



                self._state.following.append(self.FOLLOW_end_in_state1678)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: hyperlink, cif, STATE, state_part, e, statelist
                # token labels: 
                # rule labels: retval, e
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if e is not None:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "rule e", e.tree)
                    else:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "token e", None)


                    root_0 = self._adaptor.nil()
                    # 135:51: -> ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* )
                    # sdl92.g:135:54: ^( STATE ( cif )? ( hyperlink )? ( $e)? statelist ( state_part )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_STATE.nextNode(), root_1)

                    # sdl92.g:135:62: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:135:67: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:135:78: ( $e)?
                    if stream_e.hasNext():
                        self._adaptor.addChild(root_1, stream_e.nextTree())


                    stream_e.reset();
                    self._adaptor.addChild(root_1, stream_statelist.nextTree())
                    # sdl92.g:135:92: ( state_part )*
                    while stream_state_part.hasNext():
                        self._adaptor.addChild(root_1, stream_state_part.nextTree())


                    stream_state_part.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state"

    class statelist_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.statelist_return, self).__init__()

            self.tree = None




    # $ANTLR start "statelist"
    # sdl92.g:137:1: statelist : ( ( ( statename ) ( ',' statename )* ) -> ^( STATELIST ( statename )+ ) | ASTERISK ( exception_state )? -> ^( ASTERISK ( exception_state )? ) );
    def statelist(self, ):

        retval = self.statelist_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal44 = None
        ASTERISK46 = None
        statename43 = None

        statename45 = None

        exception_state47 = None


        char_literal44_tree = None
        ASTERISK46_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_ASTERISK = RewriteRuleTokenStream(self._adaptor, "token ASTERISK")
        stream_exception_state = RewriteRuleSubtreeStream(self._adaptor, "rule exception_state")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        try:
            try:
                # sdl92.g:138:9: ( ( ( statename ) ( ',' statename )* ) -> ^( STATELIST ( statename )+ ) | ASTERISK ( exception_state )? -> ^( ASTERISK ( exception_state )? ) )
                alt19 = 2
                LA19_0 = self.input.LA(1)

                if (LA19_0 == ID) :
                    alt19 = 1
                elif (LA19_0 == ASTERISK) :
                    alt19 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 19, 0, self.input)

                    raise nvae

                if alt19 == 1:
                    # sdl92.g:138:17: ( ( statename ) ( ',' statename )* )
                    pass 
                    # sdl92.g:138:17: ( ( statename ) ( ',' statename )* )
                    # sdl92.g:138:18: ( statename ) ( ',' statename )*
                    pass 
                    # sdl92.g:138:18: ( statename )
                    # sdl92.g:138:19: statename
                    pass 
                    self._state.following.append(self.FOLLOW_statename_in_statelist1738)
                    statename43 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_statename.add(statename43.tree)



                    # sdl92.g:138:29: ( ',' statename )*
                    while True: #loop17
                        alt17 = 2
                        LA17_0 = self.input.LA(1)

                        if (LA17_0 == COMMA) :
                            alt17 = 1


                        if alt17 == 1:
                            # sdl92.g:138:30: ',' statename
                            pass 
                            char_literal44=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_statelist1741) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal44)
                            self._state.following.append(self.FOLLOW_statename_in_statelist1743)
                            statename45 = self.statename()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_statename.add(statename45.tree)


                        else:
                            break #loop17




                    # AST Rewrite
                    # elements: statename
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 138:49: -> ^( STATELIST ( statename )+ )
                        # sdl92.g:138:52: ^( STATELIST ( statename )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(STATELIST, "STATELIST"), root_1)

                        # sdl92.g:138:64: ( statename )+
                        if not (stream_statename.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_statename.hasNext():
                            self._adaptor.addChild(root_1, stream_statename.nextTree())


                        stream_statename.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt19 == 2:
                    # sdl92.g:139:19: ASTERISK ( exception_state )?
                    pass 
                    ASTERISK46=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_statelist1778) 
                    if self._state.backtracking == 0:
                        stream_ASTERISK.add(ASTERISK46)
                    # sdl92.g:139:28: ( exception_state )?
                    alt18 = 2
                    LA18_0 = self.input.LA(1)

                    if (LA18_0 == L_PAREN) :
                        alt18 = 1
                    if alt18 == 1:
                        # sdl92.g:0:0: exception_state
                        pass 
                        self._state.following.append(self.FOLLOW_exception_state_in_statelist1780)
                        exception_state47 = self.exception_state()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_exception_state.add(exception_state47.tree)




                    # AST Rewrite
                    # elements: exception_state, ASTERISK
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 139:49: -> ^( ASTERISK ( exception_state )? )
                        # sdl92.g:139:52: ^( ASTERISK ( exception_state )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_ASTERISK.nextNode(), root_1)

                        # sdl92.g:139:63: ( exception_state )?
                        if stream_exception_state.hasNext():
                            self._adaptor.addChild(root_1, stream_exception_state.nextTree())


                        stream_exception_state.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "statelist"

    class exception_state_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.exception_state_return, self).__init__()

            self.tree = None




    # $ANTLR start "exception_state"
    # sdl92.g:141:1: exception_state : '(' statename ( ',' statename )* ')' -> ( statename )+ ;
    def exception_state(self, ):

        retval = self.exception_state_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal48 = None
        char_literal50 = None
        char_literal52 = None
        statename49 = None

        statename51 = None


        char_literal48_tree = None
        char_literal50_tree = None
        char_literal52_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_statename = RewriteRuleSubtreeStream(self._adaptor, "rule statename")
        try:
            try:
                # sdl92.g:142:9: ( '(' statename ( ',' statename )* ')' -> ( statename )+ )
                # sdl92.g:143:17: '(' statename ( ',' statename )* ')'
                pass 
                char_literal48=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_exception_state1826) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal48)
                self._state.following.append(self.FOLLOW_statename_in_exception_state1828)
                statename49 = self.statename()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_statename.add(statename49.tree)
                # sdl92.g:143:31: ( ',' statename )*
                while True: #loop20
                    alt20 = 2
                    LA20_0 = self.input.LA(1)

                    if (LA20_0 == COMMA) :
                        alt20 = 1


                    if alt20 == 1:
                        # sdl92.g:143:32: ',' statename
                        pass 
                        char_literal50=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_exception_state1831) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal50)
                        self._state.following.append(self.FOLLOW_statename_in_exception_state1833)
                        statename51 = self.statename()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_statename.add(statename51.tree)


                    else:
                        break #loop20
                char_literal52=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_exception_state1837) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal52)

                # AST Rewrite
                # elements: statename
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 143:56: -> ( statename )+
                    # sdl92.g:143:59: ( statename )+
                    if not (stream_statename.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_statename.hasNext():
                        self._adaptor.addChild(root_0, stream_statename.nextTree())


                    stream_statename.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "exception_state"

    class state_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.state_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "state_part"
    # sdl92.g:146:1: state_part : ( input_part | save_part | spontaneous_transition | continuous_signal );
    def state_part(self, ):

        retval = self.state_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        input_part53 = None

        save_part54 = None

        spontaneous_transition55 = None

        continuous_signal56 = None



        try:
            try:
                # sdl92.g:147:9: ( input_part | save_part | spontaneous_transition | continuous_signal )
                alt21 = 4
                alt21 = self.dfa21.predict(self.input)
                if alt21 == 1:
                    # sdl92.g:147:17: input_part
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_input_part_in_state_part1883)
                    input_part53 = self.input_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, input_part53.tree)


                elif alt21 == 2:
                    # sdl92.g:149:17: save_part
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_save_part_in_state_part1948)
                    save_part54 = self.save_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, save_part54.tree)


                elif alt21 == 3:
                    # sdl92.g:150:17: spontaneous_transition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_spontaneous_transition_in_state_part1996)
                    spontaneous_transition55 = self.spontaneous_transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, spontaneous_transition55.tree)


                elif alt21 == 4:
                    # sdl92.g:151:17: continuous_signal
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_continuous_signal_in_state_part2025)
                    continuous_signal56 = self.continuous_signal()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, continuous_signal56.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "state_part"

    class spontaneous_transition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.spontaneous_transition_return, self).__init__()

            self.tree = None




    # $ANTLR start "spontaneous_transition"
    # sdl92.g:153:1: spontaneous_transition : ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition ) ;
    def spontaneous_transition(self, ):

        retval = self.spontaneous_transition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INPUT59 = None
        NONE60 = None
        cif57 = None

        hyperlink58 = None

        end61 = None

        enabling_condition62 = None

        transition63 = None


        INPUT59_tree = None
        NONE60_tree = None
        stream_INPUT = RewriteRuleTokenStream(self._adaptor, "token INPUT")
        stream_NONE = RewriteRuleTokenStream(self._adaptor, "token NONE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_enabling_condition = RewriteRuleSubtreeStream(self._adaptor, "rule enabling_condition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:154:9: ( ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition ) )
                # sdl92.g:154:17: ( cif )? ( hyperlink )? INPUT NONE end ( enabling_condition )? transition
                pass 
                # sdl92.g:154:17: ( cif )?
                alt22 = 2
                LA22_0 = self.input.LA(1)

                if (LA22_0 == 176) :
                    LA22_1 = self.input.LA(2)

                    if (LA22_1 == LABEL or LA22_1 == COMMENT or LA22_1 == STATE or LA22_1 == PROVIDED or LA22_1 == INPUT or LA22_1 == DECISION or LA22_1 == ANSWER or LA22_1 == OUTPUT or (TEXT <= LA22_1 <= JOIN) or LA22_1 == TASK or LA22_1 == START or LA22_1 == PROCEDURE) :
                        alt22 = 1
                if alt22 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_spontaneous_transition2068)
                    cif57 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif57.tree)



                # sdl92.g:155:17: ( hyperlink )?
                alt23 = 2
                LA23_0 = self.input.LA(1)

                if (LA23_0 == 176) :
                    alt23 = 1
                if alt23 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_spontaneous_transition2087)
                    hyperlink58 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink58.tree)



                INPUT59=self.match(self.input, INPUT, self.FOLLOW_INPUT_in_spontaneous_transition2106) 
                if self._state.backtracking == 0:
                    stream_INPUT.add(INPUT59)
                NONE60=self.match(self.input, NONE, self.FOLLOW_NONE_in_spontaneous_transition2108) 
                if self._state.backtracking == 0:
                    stream_NONE.add(NONE60)
                self._state.following.append(self.FOLLOW_end_in_spontaneous_transition2110)
                end61 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end61.tree)
                # sdl92.g:157:17: ( enabling_condition )?
                alt24 = 2
                LA24_0 = self.input.LA(1)

                if (LA24_0 == PROVIDED) :
                    alt24 = 1
                if alt24 == 1:
                    # sdl92.g:0:0: enabling_condition
                    pass 
                    self._state.following.append(self.FOLLOW_enabling_condition_in_spontaneous_transition2128)
                    enabling_condition62 = self.enabling_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_enabling_condition.add(enabling_condition62.tree)



                self._state.following.append(self.FOLLOW_transition_in_spontaneous_transition2147)
                transition63 = self.transition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_transition.add(transition63.tree)

                # AST Rewrite
                # elements: hyperlink, transition, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 158:49: -> ^( INPUT_NONE ( cif )? ( hyperlink )? transition )
                    # sdl92.g:158:52: ^( INPUT_NONE ( cif )? ( hyperlink )? transition )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INPUT_NONE, "INPUT_NONE"), root_1)

                    # sdl92.g:158:65: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:158:70: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    self._adaptor.addChild(root_1, stream_transition.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "spontaneous_transition"

    class enabling_condition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.enabling_condition_return, self).__init__()

            self.tree = None




    # $ANTLR start "enabling_condition"
    # sdl92.g:160:1: enabling_condition : PROVIDED expression end -> ^( PROVIDED expression ) ;
    def enabling_condition(self, ):

        retval = self.enabling_condition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PROVIDED64 = None
        expression65 = None

        end66 = None


        PROVIDED64_tree = None
        stream_PROVIDED = RewriteRuleTokenStream(self._adaptor, "token PROVIDED")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:161:9: ( PROVIDED expression end -> ^( PROVIDED expression ) )
                # sdl92.g:161:17: PROVIDED expression end
                pass 
                PROVIDED64=self.match(self.input, PROVIDED, self.FOLLOW_PROVIDED_in_enabling_condition2204) 
                if self._state.backtracking == 0:
                    stream_PROVIDED.add(PROVIDED64)
                self._state.following.append(self.FOLLOW_expression_in_enabling_condition2206)
                expression65 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression65.tree)
                self._state.following.append(self.FOLLOW_end_in_enabling_condition2208)
                end66 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end66.tree)

                # AST Rewrite
                # elements: expression, PROVIDED
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 161:49: -> ^( PROVIDED expression )
                    # sdl92.g:161:52: ^( PROVIDED expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROVIDED.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "enabling_condition"

    class continuous_signal_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.continuous_signal_return, self).__init__()

            self.tree = None




    # $ANTLR start "continuous_signal"
    # sdl92.g:163:1: continuous_signal : PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition -> ^( PROVIDED expression ( $integer_literal_name)? transition ) ;
    def continuous_signal(self, ):

        retval = self.continuous_signal_return()
        retval.start = self.input.LT(1)

        root_0 = None

        integer_literal_name = None
        PROVIDED67 = None
        PRIORITY70 = None
        expression68 = None

        end69 = None

        end71 = None

        transition72 = None


        integer_literal_name_tree = None
        PROVIDED67_tree = None
        PRIORITY70_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_PRIORITY = RewriteRuleTokenStream(self._adaptor, "token PRIORITY")
        stream_PROVIDED = RewriteRuleTokenStream(self._adaptor, "token PROVIDED")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:164:9: ( PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition -> ^( PROVIDED expression ( $integer_literal_name)? transition ) )
                # sdl92.g:164:17: PROVIDED expression end ( PRIORITY integer_literal_name= INT end )? transition
                pass 
                PROVIDED67=self.match(self.input, PROVIDED, self.FOLLOW_PROVIDED_in_continuous_signal2246) 
                if self._state.backtracking == 0:
                    stream_PROVIDED.add(PROVIDED67)
                self._state.following.append(self.FOLLOW_expression_in_continuous_signal2248)
                expression68 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression68.tree)
                self._state.following.append(self.FOLLOW_end_in_continuous_signal2250)
                end69 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end69.tree)
                # sdl92.g:165:17: ( PRIORITY integer_literal_name= INT end )?
                alt25 = 2
                LA25_0 = self.input.LA(1)

                if (LA25_0 == PRIORITY) :
                    alt25 = 1
                if alt25 == 1:
                    # sdl92.g:165:18: PRIORITY integer_literal_name= INT end
                    pass 
                    PRIORITY70=self.match(self.input, PRIORITY, self.FOLLOW_PRIORITY_in_continuous_signal2270) 
                    if self._state.backtracking == 0:
                        stream_PRIORITY.add(PRIORITY70)
                    integer_literal_name=self.match(self.input, INT, self.FOLLOW_INT_in_continuous_signal2274) 
                    if self._state.backtracking == 0:
                        stream_INT.add(integer_literal_name)
                    self._state.following.append(self.FOLLOW_end_in_continuous_signal2276)
                    end71 = self.end()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_end.add(end71.tree)



                self._state.following.append(self.FOLLOW_transition_in_continuous_signal2297)
                transition72 = self.transition()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_transition.add(transition72.tree)

                # AST Rewrite
                # elements: PROVIDED, transition, integer_literal_name, expression
                # token labels: integer_literal_name
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_integer_literal_name = RewriteRuleTokenStream(self._adaptor, "token integer_literal_name", integer_literal_name)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 166:49: -> ^( PROVIDED expression ( $integer_literal_name)? transition )
                    # sdl92.g:166:52: ^( PROVIDED expression ( $integer_literal_name)? transition )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_PROVIDED.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())
                    # sdl92.g:166:74: ( $integer_literal_name)?
                    if stream_integer_literal_name.hasNext():
                        self._adaptor.addChild(root_1, stream_integer_literal_name.nextNode())


                    stream_integer_literal_name.reset();
                    self._adaptor.addChild(root_1, stream_transition.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "continuous_signal"

    class save_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.save_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "save_part"
    # sdl92.g:168:1: save_part : SAVE save_list end -> ^( SAVE save_list ) ;
    def save_part(self, ):

        retval = self.save_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SAVE73 = None
        save_list74 = None

        end75 = None


        SAVE73_tree = None
        stream_SAVE = RewriteRuleTokenStream(self._adaptor, "token SAVE")
        stream_save_list = RewriteRuleSubtreeStream(self._adaptor, "rule save_list")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:169:9: ( SAVE save_list end -> ^( SAVE save_list ) )
                # sdl92.g:169:17: SAVE save_list end
                pass 
                SAVE73=self.match(self.input, SAVE, self.FOLLOW_SAVE_in_save_part2359) 
                if self._state.backtracking == 0:
                    stream_SAVE.add(SAVE73)
                self._state.following.append(self.FOLLOW_save_list_in_save_part2361)
                save_list74 = self.save_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_save_list.add(save_list74.tree)
                self._state.following.append(self.FOLLOW_end_in_save_part2363)
                end75 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end75.tree)

                # AST Rewrite
                # elements: SAVE, save_list
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 169:49: -> ^( SAVE save_list )
                    # sdl92.g:169:52: ^( SAVE save_list )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_SAVE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_save_list.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "save_part"

    class save_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.save_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "save_list"
    # sdl92.g:171:1: save_list : ( signal_list | asterisk_save_list );
    def save_list(self, ):

        retval = self.save_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_list76 = None

        asterisk_save_list77 = None



        try:
            try:
                # sdl92.g:172:9: ( signal_list | asterisk_save_list )
                alt26 = 2
                LA26_0 = self.input.LA(1)

                if (LA26_0 == ID) :
                    alt26 = 1
                elif (LA26_0 == ASTERISK) :
                    alt26 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 26, 0, self.input)

                    raise nvae

                if alt26 == 1:
                    # sdl92.g:172:17: signal_list
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_signal_list_in_save_list2406)
                    signal_list76 = self.signal_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, signal_list76.tree)


                elif alt26 == 2:
                    # sdl92.g:172:29: asterisk_save_list
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_asterisk_save_list_in_save_list2408)
                    asterisk_save_list77 = self.asterisk_save_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, asterisk_save_list77.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "save_list"

    class asterisk_save_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.asterisk_save_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "asterisk_save_list"
    # sdl92.g:174:1: asterisk_save_list : ASTERISK ;
    def asterisk_save_list(self, ):

        retval = self.asterisk_save_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK78 = None

        ASTERISK78_tree = None

        try:
            try:
                # sdl92.g:175:9: ( ASTERISK )
                # sdl92.g:175:17: ASTERISK
                pass 
                root_0 = self._adaptor.nil()

                ASTERISK78=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_asterisk_save_list2436)
                if self._state.backtracking == 0:

                    ASTERISK78_tree = self._adaptor.createWithPayload(ASTERISK78)
                    self._adaptor.addChild(root_0, ASTERISK78_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "asterisk_save_list"

    class signal_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_list"
    # sdl92.g:177:1: signal_list : signal_item ( ',' signal_item )* -> ^( SIGNAL_LIST ( signal_item )+ ) ;
    def signal_list(self, ):

        retval = self.signal_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal80 = None
        signal_item79 = None

        signal_item81 = None


        char_literal80_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_signal_item = RewriteRuleSubtreeStream(self._adaptor, "rule signal_item")
        try:
            try:
                # sdl92.g:178:9: ( signal_item ( ',' signal_item )* -> ^( SIGNAL_LIST ( signal_item )+ ) )
                # sdl92.g:178:17: signal_item ( ',' signal_item )*
                pass 
                self._state.following.append(self.FOLLOW_signal_item_in_signal_list2463)
                signal_item79 = self.signal_item()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_signal_item.add(signal_item79.tree)
                # sdl92.g:178:29: ( ',' signal_item )*
                while True: #loop27
                    alt27 = 2
                    LA27_0 = self.input.LA(1)

                    if (LA27_0 == COMMA) :
                        alt27 = 1


                    if alt27 == 1:
                        # sdl92.g:178:30: ',' signal_item
                        pass 
                        char_literal80=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_signal_list2466) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal80)
                        self._state.following.append(self.FOLLOW_signal_item_in_signal_list2468)
                        signal_item81 = self.signal_item()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_signal_item.add(signal_item81.tree)


                    else:
                        break #loop27

                # AST Rewrite
                # elements: signal_item
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 178:49: -> ^( SIGNAL_LIST ( signal_item )+ )
                    # sdl92.g:178:52: ^( SIGNAL_LIST ( signal_item )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SIGNAL_LIST, "SIGNAL_LIST"), root_1)

                    # sdl92.g:178:66: ( signal_item )+
                    if not (stream_signal_item.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_signal_item.hasNext():
                        self._adaptor.addChild(root_1, stream_signal_item.nextTree())


                    stream_signal_item.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_list"

    class signal_item_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_item_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_item"
    # sdl92.g:181:1: signal_item : signal_id ;
    def signal_item(self, ):

        retval = self.signal_item_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_id82 = None



        try:
            try:
                # sdl92.g:182:9: ( signal_id )
                # sdl92.g:182:17: signal_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_signal_id_in_signal_item2503)
                signal_id82 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, signal_id82.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_item"

    class input_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.input_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "input_part"
    # sdl92.g:202:1: input_part : ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )? -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? ) ;
    def input_part(self, ):

        retval = self.input_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        INPUT85 = None
        cif83 = None

        hyperlink84 = None

        inputlist86 = None

        end87 = None

        enabling_condition88 = None

        transition89 = None


        INPUT85_tree = None
        stream_INPUT = RewriteRuleTokenStream(self._adaptor, "token INPUT")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        stream_inputlist = RewriteRuleSubtreeStream(self._adaptor, "rule inputlist")
        stream_enabling_condition = RewriteRuleSubtreeStream(self._adaptor, "rule enabling_condition")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:203:9: ( ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )? -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? ) )
                # sdl92.g:203:17: ( cif )? ( hyperlink )? INPUT inputlist end ( enabling_condition )? ( transition )?
                pass 
                # sdl92.g:203:17: ( cif )?
                alt28 = 2
                LA28_0 = self.input.LA(1)

                if (LA28_0 == 176) :
                    LA28_1 = self.input.LA(2)

                    if (LA28_1 == LABEL or LA28_1 == COMMENT or LA28_1 == STATE or LA28_1 == PROVIDED or LA28_1 == INPUT or LA28_1 == DECISION or LA28_1 == ANSWER or LA28_1 == OUTPUT or (TEXT <= LA28_1 <= JOIN) or LA28_1 == TASK or LA28_1 == START or LA28_1 == PROCEDURE) :
                        alt28 = 1
                if alt28 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_input_part2542)
                    cif83 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif83.tree)



                # sdl92.g:204:17: ( hyperlink )?
                alt29 = 2
                LA29_0 = self.input.LA(1)

                if (LA29_0 == 176) :
                    alt29 = 1
                if alt29 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_input_part2561)
                    hyperlink84 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink84.tree)



                INPUT85=self.match(self.input, INPUT, self.FOLLOW_INPUT_in_input_part2580) 
                if self._state.backtracking == 0:
                    stream_INPUT.add(INPUT85)
                self._state.following.append(self.FOLLOW_inputlist_in_input_part2582)
                inputlist86 = self.inputlist()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_inputlist.add(inputlist86.tree)
                self._state.following.append(self.FOLLOW_end_in_input_part2584)
                end87 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end87.tree)
                # sdl92.g:206:17: ( enabling_condition )?
                alt30 = 2
                alt30 = self.dfa30.predict(self.input)
                if alt30 == 1:
                    # sdl92.g:0:0: enabling_condition
                    pass 
                    self._state.following.append(self.FOLLOW_enabling_condition_in_input_part2603)
                    enabling_condition88 = self.enabling_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_enabling_condition.add(enabling_condition88.tree)



                # sdl92.g:207:17: ( transition )?
                alt31 = 2
                alt31 = self.dfa31.predict(self.input)
                if alt31 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_input_part2623)
                    transition89 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition89.tree)




                # AST Rewrite
                # elements: inputlist, enabling_condition, transition, hyperlink, INPUT, cif, end
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 207:50: -> ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? )
                    # sdl92.g:207:53: ^( INPUT ( cif )? ( hyperlink )? ( end )? inputlist ( enabling_condition )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_INPUT.nextNode(), root_1)

                    # sdl92.g:207:61: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:207:66: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:207:77: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_inputlist.nextTree())
                    # sdl92.g:207:92: ( enabling_condition )?
                    if stream_enabling_condition.hasNext():
                        self._adaptor.addChild(root_1, stream_enabling_condition.nextTree())


                    stream_enabling_condition.reset();
                    # sdl92.g:207:112: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "input_part"

    class inputlist_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.inputlist_return, self).__init__()

            self.tree = None




    # $ANTLR start "inputlist"
    # sdl92.g:212:1: inputlist : ( ASTERISK | ( stimulus ( ',' stimulus )* ) -> ^( INPUTLIST ( stimulus )+ ) );
    def inputlist(self, ):

        retval = self.inputlist_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK90 = None
        char_literal92 = None
        stimulus91 = None

        stimulus93 = None


        ASTERISK90_tree = None
        char_literal92_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_stimulus = RewriteRuleSubtreeStream(self._adaptor, "rule stimulus")
        try:
            try:
                # sdl92.g:213:9: ( ASTERISK | ( stimulus ( ',' stimulus )* ) -> ^( INPUTLIST ( stimulus )+ ) )
                alt33 = 2
                LA33_0 = self.input.LA(1)

                if (LA33_0 == ASTERISK) :
                    alt33 = 1
                elif (LA33_0 == ID) :
                    alt33 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 33, 0, self.input)

                    raise nvae

                if alt33 == 1:
                    # sdl92.g:213:17: ASTERISK
                    pass 
                    root_0 = self._adaptor.nil()

                    ASTERISK90=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_inputlist2694)
                    if self._state.backtracking == 0:

                        ASTERISK90_tree = self._adaptor.createWithPayload(ASTERISK90)
                        self._adaptor.addChild(root_0, ASTERISK90_tree)



                elif alt33 == 2:
                    # sdl92.g:214:19: ( stimulus ( ',' stimulus )* )
                    pass 
                    # sdl92.g:214:19: ( stimulus ( ',' stimulus )* )
                    # sdl92.g:214:20: stimulus ( ',' stimulus )*
                    pass 
                    self._state.following.append(self.FOLLOW_stimulus_in_inputlist2719)
                    stimulus91 = self.stimulus()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_stimulus.add(stimulus91.tree)
                    # sdl92.g:214:29: ( ',' stimulus )*
                    while True: #loop32
                        alt32 = 2
                        LA32_0 = self.input.LA(1)

                        if (LA32_0 == COMMA) :
                            alt32 = 1


                        if alt32 == 1:
                            # sdl92.g:214:30: ',' stimulus
                            pass 
                            char_literal92=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_inputlist2722) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal92)
                            self._state.following.append(self.FOLLOW_stimulus_in_inputlist2724)
                            stimulus93 = self.stimulus()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_stimulus.add(stimulus93.tree)


                        else:
                            break #loop32




                    # AST Rewrite
                    # elements: stimulus
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 214:49: -> ^( INPUTLIST ( stimulus )+ )
                        # sdl92.g:214:52: ^( INPUTLIST ( stimulus )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INPUTLIST, "INPUTLIST"), root_1)

                        # sdl92.g:214:64: ( stimulus )+
                        if not (stream_stimulus.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_stimulus.hasNext():
                            self._adaptor.addChild(root_1, stream_stimulus.nextTree())


                        stream_stimulus.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "inputlist"

    class stimulus_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stimulus_return, self).__init__()

            self.tree = None




    # $ANTLR start "stimulus"
    # sdl92.g:220:1: stimulus : stimulus_id ( input_params )? ;
    def stimulus(self, ):

        retval = self.stimulus_return()
        retval.start = self.input.LT(1)

        root_0 = None

        stimulus_id94 = None

        input_params95 = None



        try:
            try:
                # sdl92.g:221:9: ( stimulus_id ( input_params )? )
                # sdl92.g:221:17: stimulus_id ( input_params )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_stimulus_id_in_stimulus2772)
                stimulus_id94 = self.stimulus_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, stimulus_id94.tree)
                # sdl92.g:221:29: ( input_params )?
                alt34 = 2
                LA34_0 = self.input.LA(1)

                if (LA34_0 == L_PAREN) :
                    alt34 = 1
                if alt34 == 1:
                    # sdl92.g:0:0: input_params
                    pass 
                    self._state.following.append(self.FOLLOW_input_params_in_stimulus2774)
                    input_params95 = self.input_params()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, input_params95.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stimulus"

    class input_params_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.input_params_return, self).__init__()

            self.tree = None




    # $ANTLR start "input_params"
    # sdl92.g:224:1: input_params : L_PAREN variable_id ( ',' variable_id )* R_PAREN -> ^( PARAMS ( variable_id )+ ) ;
    def input_params(self, ):

        retval = self.input_params_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN96 = None
        char_literal98 = None
        R_PAREN100 = None
        variable_id97 = None

        variable_id99 = None


        L_PAREN96_tree = None
        char_literal98_tree = None
        R_PAREN100_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        try:
            try:
                # sdl92.g:225:9: ( L_PAREN variable_id ( ',' variable_id )* R_PAREN -> ^( PARAMS ( variable_id )+ ) )
                # sdl92.g:225:17: L_PAREN variable_id ( ',' variable_id )* R_PAREN
                pass 
                L_PAREN96=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_input_params2815) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN96)
                self._state.following.append(self.FOLLOW_variable_id_in_input_params2817)
                variable_id97 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id97.tree)
                # sdl92.g:225:37: ( ',' variable_id )*
                while True: #loop35
                    alt35 = 2
                    LA35_0 = self.input.LA(1)

                    if (LA35_0 == COMMA) :
                        alt35 = 1


                    if alt35 == 1:
                        # sdl92.g:225:38: ',' variable_id
                        pass 
                        char_literal98=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_input_params2820) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal98)
                        self._state.following.append(self.FOLLOW_variable_id_in_input_params2822)
                        variable_id99 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id99.tree)


                    else:
                        break #loop35
                R_PAREN100=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_input_params2826) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN100)

                # AST Rewrite
                # elements: variable_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 225:72: -> ^( PARAMS ( variable_id )+ )
                    # sdl92.g:225:75: ^( PARAMS ( variable_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                    # sdl92.g:225:84: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "input_params"

    class transition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.transition_return, self).__init__()

            self.tree = None




    # $ANTLR start "transition"
    # sdl92.g:228:1: transition : ( ( action )+ ( terminator_statement )? -> ^( TRANSITION ( action )+ ( terminator_statement )? ) | terminator_statement -> ^( TRANSITION terminator_statement ) );
    def transition(self, ):

        retval = self.transition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        action101 = None

        terminator_statement102 = None

        terminator_statement103 = None


        stream_terminator_statement = RewriteRuleSubtreeStream(self._adaptor, "rule terminator_statement")
        stream_action = RewriteRuleSubtreeStream(self._adaptor, "rule action")
        try:
            try:
                # sdl92.g:229:9: ( ( action )+ ( terminator_statement )? -> ^( TRANSITION ( action )+ ( terminator_statement )? ) | terminator_statement -> ^( TRANSITION terminator_statement ) )
                alt38 = 2
                alt38 = self.dfa38.predict(self.input)
                if alt38 == 1:
                    # sdl92.g:229:17: ( action )+ ( terminator_statement )?
                    pass 
                    # sdl92.g:229:17: ( action )+
                    cnt36 = 0
                    while True: #loop36
                        alt36 = 2
                        alt36 = self.dfa36.predict(self.input)
                        if alt36 == 1:
                            # sdl92.g:0:0: action
                            pass 
                            self._state.following.append(self.FOLLOW_action_in_transition2869)
                            action101 = self.action()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_action.add(action101.tree)


                        else:
                            if cnt36 >= 1:
                                break #loop36

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(36, self.input)
                            raise eee

                        cnt36 += 1
                    # sdl92.g:229:25: ( terminator_statement )?
                    alt37 = 2
                    alt37 = self.dfa37.predict(self.input)
                    if alt37 == 1:
                        # sdl92.g:0:0: terminator_statement
                        pass 
                        self._state.following.append(self.FOLLOW_terminator_statement_in_transition2872)
                        terminator_statement102 = self.terminator_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_terminator_statement.add(terminator_statement102.tree)




                    # AST Rewrite
                    # elements: terminator_statement, action
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 229:51: -> ^( TRANSITION ( action )+ ( terminator_statement )? )
                        # sdl92.g:229:54: ^( TRANSITION ( action )+ ( terminator_statement )? )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TRANSITION, "TRANSITION"), root_1)

                        # sdl92.g:229:67: ( action )+
                        if not (stream_action.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_action.hasNext():
                            self._adaptor.addChild(root_1, stream_action.nextTree())


                        stream_action.reset()
                        # sdl92.g:229:75: ( terminator_statement )?
                        if stream_terminator_statement.hasNext():
                            self._adaptor.addChild(root_1, stream_terminator_statement.nextTree())


                        stream_terminator_statement.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt38 == 2:
                    # sdl92.g:230:19: terminator_statement
                    pass 
                    self._state.following.append(self.FOLLOW_terminator_statement_in_transition2910)
                    terminator_statement103 = self.terminator_statement()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_terminator_statement.add(terminator_statement103.tree)

                    # AST Rewrite
                    # elements: terminator_statement
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 230:57: -> ^( TRANSITION terminator_statement )
                        # sdl92.g:230:60: ^( TRANSITION terminator_statement )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TRANSITION, "TRANSITION"), root_1)

                        self._adaptor.addChild(root_1, stream_terminator_statement.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "transition"

    class action_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.action_return, self).__init__()

            self.tree = None




    # $ANTLR start "action"
    # sdl92.g:232:1: action : ( label )? ( task | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call ) ;
    def action(self, ):

        retval = self.action_return()
        retval.start = self.input.LT(1)

        root_0 = None

        label104 = None

        task105 = None

        output106 = None

        create_request107 = None

        decision108 = None

        transition_option109 = None

        set_timer110 = None

        reset_timer111 = None

        export112 = None

        procedure_call113 = None



        try:
            try:
                # sdl92.g:233:9: ( ( label )? ( task | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call ) )
                # sdl92.g:233:17: ( label )? ( task | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:233:17: ( label )?
                alt39 = 2
                alt39 = self.dfa39.predict(self.input)
                if alt39 == 1:
                    # sdl92.g:0:0: label
                    pass 
                    self._state.following.append(self.FOLLOW_label_in_action2960)
                    label104 = self.label()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, label104.tree)



                # sdl92.g:234:17: ( task | output | create_request | decision | transition_option | set_timer | reset_timer | export | procedure_call )
                alt40 = 9
                alt40 = self.dfa40.predict(self.input)
                if alt40 == 1:
                    # sdl92.g:234:18: task
                    pass 
                    self._state.following.append(self.FOLLOW_task_in_action2980)
                    task105 = self.task()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, task105.tree)


                elif alt40 == 2:
                    # sdl92.g:235:19: output
                    pass 
                    self._state.following.append(self.FOLLOW_output_in_action3020)
                    output106 = self.output()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, output106.tree)


                elif alt40 == 3:
                    # sdl92.g:236:19: create_request
                    pass 
                    self._state.following.append(self.FOLLOW_create_request_in_action3059)
                    create_request107 = self.create_request()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, create_request107.tree)


                elif alt40 == 4:
                    # sdl92.g:237:19: decision
                    pass 
                    self._state.following.append(self.FOLLOW_decision_in_action3090)
                    decision108 = self.decision()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, decision108.tree)


                elif alt40 == 5:
                    # sdl92.g:238:19: transition_option
                    pass 
                    self._state.following.append(self.FOLLOW_transition_option_in_action3135)
                    transition_option109 = self.transition_option()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, transition_option109.tree)


                elif alt40 == 6:
                    # sdl92.g:239:19: set_timer
                    pass 
                    self._state.following.append(self.FOLLOW_set_timer_in_action3171)
                    set_timer110 = self.set_timer()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, set_timer110.tree)


                elif alt40 == 7:
                    # sdl92.g:240:19: reset_timer
                    pass 
                    self._state.following.append(self.FOLLOW_reset_timer_in_action3215)
                    reset_timer111 = self.reset_timer()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, reset_timer111.tree)


                elif alt40 == 8:
                    # sdl92.g:241:19: export
                    pass 
                    self._state.following.append(self.FOLLOW_export_in_action3256)
                    export112 = self.export()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, export112.tree)


                elif alt40 == 9:
                    # sdl92.g:242:19: procedure_call
                    pass 
                    self._state.following.append(self.FOLLOW_procedure_call_in_action3297)
                    procedure_call113 = self.procedure_call()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, procedure_call113.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "action"

    class export_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.export_return, self).__init__()

            self.tree = None




    # $ANTLR start "export"
    # sdl92.g:246:1: export : EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end -> ^( EXPORT ( variable_id )+ ) ;
    def export(self, ):

        retval = self.export_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EXPORT114 = None
        L_PAREN115 = None
        COMMA117 = None
        R_PAREN119 = None
        variable_id116 = None

        variable_id118 = None

        end120 = None


        EXPORT114_tree = None
        L_PAREN115_tree = None
        COMMA117_tree = None
        R_PAREN119_tree = None
        stream_EXPORT = RewriteRuleTokenStream(self._adaptor, "token EXPORT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:247:9: ( EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end -> ^( EXPORT ( variable_id )+ ) )
                # sdl92.g:247:17: EXPORT L_PAREN variable_id ( COMMA variable_id )* R_PAREN end
                pass 
                EXPORT114=self.match(self.input, EXPORT, self.FOLLOW_EXPORT_in_export3340) 
                if self._state.backtracking == 0:
                    stream_EXPORT.add(EXPORT114)
                L_PAREN115=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_export3358) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN115)
                self._state.following.append(self.FOLLOW_variable_id_in_export3360)
                variable_id116 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id116.tree)
                # sdl92.g:248:37: ( COMMA variable_id )*
                while True: #loop41
                    alt41 = 2
                    LA41_0 = self.input.LA(1)

                    if (LA41_0 == COMMA) :
                        alt41 = 1


                    if alt41 == 1:
                        # sdl92.g:248:38: COMMA variable_id
                        pass 
                        COMMA117=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_export3363) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(COMMA117)
                        self._state.following.append(self.FOLLOW_variable_id_in_export3365)
                        variable_id118 = self.variable_id()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_variable_id.add(variable_id118.tree)


                    else:
                        break #loop41
                R_PAREN119=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_export3369) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN119)
                self._state.following.append(self.FOLLOW_end_in_export3371)
                end120 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end120.tree)

                # AST Rewrite
                # elements: variable_id, EXPORT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 248:70: -> ^( EXPORT ( variable_id )+ )
                    # sdl92.g:248:73: ^( EXPORT ( variable_id )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_EXPORT.nextNode(), root_1)

                    # sdl92.g:248:82: ( variable_id )+
                    if not (stream_variable_id.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_variable_id.hasNext():
                        self._adaptor.addChild(root_1, stream_variable_id.nextTree())


                    stream_variable_id.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "export"

    class procedure_call_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_call_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_call"
    # sdl92.g:256:1: procedure_call : ( cif )? ( hyperlink )? CALL procedure_call_body end -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body ) ;
    def procedure_call(self, ):

        retval = self.procedure_call_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CALL123 = None
        cif121 = None

        hyperlink122 = None

        procedure_call_body124 = None

        end125 = None


        CALL123_tree = None
        stream_CALL = RewriteRuleTokenStream(self._adaptor, "token CALL")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_procedure_call_body = RewriteRuleSubtreeStream(self._adaptor, "rule procedure_call_body")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:257:9: ( ( cif )? ( hyperlink )? CALL procedure_call_body end -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body ) )
                # sdl92.g:257:17: ( cif )? ( hyperlink )? CALL procedure_call_body end
                pass 
                # sdl92.g:257:17: ( cif )?
                alt42 = 2
                LA42_0 = self.input.LA(1)

                if (LA42_0 == 176) :
                    LA42_1 = self.input.LA(2)

                    if (LA42_1 == LABEL or LA42_1 == COMMENT or LA42_1 == STATE or LA42_1 == PROVIDED or LA42_1 == INPUT or LA42_1 == DECISION or LA42_1 == ANSWER or LA42_1 == OUTPUT or (TEXT <= LA42_1 <= JOIN) or LA42_1 == TASK or LA42_1 == START or LA42_1 == PROCEDURE) :
                        alt42 = 1
                if alt42 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_procedure_call3403)
                    cif121 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif121.tree)



                # sdl92.g:258:17: ( hyperlink )?
                alt43 = 2
                LA43_0 = self.input.LA(1)

                if (LA43_0 == 176) :
                    alt43 = 1
                if alt43 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_procedure_call3422)
                    hyperlink122 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink122.tree)



                CALL123=self.match(self.input, CALL, self.FOLLOW_CALL_in_procedure_call3441) 
                if self._state.backtracking == 0:
                    stream_CALL.add(CALL123)
                self._state.following.append(self.FOLLOW_procedure_call_body_in_procedure_call3443)
                procedure_call_body124 = self.procedure_call_body()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_procedure_call_body.add(procedure_call_body124.tree)
                self._state.following.append(self.FOLLOW_end_in_procedure_call3445)
                end125 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end125.tree)

                # AST Rewrite
                # elements: end, procedure_call_body, hyperlink, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 259:58: -> ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body )
                    # sdl92.g:259:61: ^( PROCEDURE_CALL ( cif )? ( hyperlink )? ( end )? procedure_call_body )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PROCEDURE_CALL, "PROCEDURE_CALL"), root_1)

                    # sdl92.g:259:78: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:259:83: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:259:94: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_procedure_call_body.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_call"

    class procedure_call_body_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_call_body_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_call_body"
    # sdl92.g:261:1: procedure_call_body : procedure_id ( actual_parameters )? -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? ) ;
    def procedure_call_body(self, ):

        retval = self.procedure_call_body_return()
        retval.start = self.input.LT(1)

        root_0 = None

        procedure_id126 = None

        actual_parameters127 = None


        stream_procedure_id = RewriteRuleSubtreeStream(self._adaptor, "rule procedure_id")
        stream_actual_parameters = RewriteRuleSubtreeStream(self._adaptor, "rule actual_parameters")
        try:
            try:
                # sdl92.g:262:9: ( procedure_id ( actual_parameters )? -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? ) )
                # sdl92.g:262:17: procedure_id ( actual_parameters )?
                pass 
                self._state.following.append(self.FOLLOW_procedure_id_in_procedure_call_body3504)
                procedure_id126 = self.procedure_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_procedure_id.add(procedure_id126.tree)
                # sdl92.g:262:30: ( actual_parameters )?
                alt44 = 2
                LA44_0 = self.input.LA(1)

                if (LA44_0 == L_PAREN) :
                    alt44 = 1
                if alt44 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_procedure_call_body3506)
                    actual_parameters127 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_actual_parameters.add(actual_parameters127.tree)




                # AST Rewrite
                # elements: actual_parameters, procedure_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 262:51: -> ^( OUTPUT_BODY procedure_id ( actual_parameters )? )
                    # sdl92.g:262:54: ^( OUTPUT_BODY procedure_id ( actual_parameters )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OUTPUT_BODY, "OUTPUT_BODY"), root_1)

                    self._adaptor.addChild(root_1, stream_procedure_id.nextTree())
                    # sdl92.g:262:81: ( actual_parameters )?
                    if stream_actual_parameters.hasNext():
                        self._adaptor.addChild(root_1, stream_actual_parameters.nextTree())


                    stream_actual_parameters.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_call_body"

    class set_timer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.set_timer_return, self).__init__()

            self.tree = None




    # $ANTLR start "set_timer"
    # sdl92.g:264:1: set_timer : SET set_statement ( COMMA set_statement )* end -> ( set_statement )+ ;
    def set_timer(self, ):

        retval = self.set_timer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        SET128 = None
        COMMA130 = None
        set_statement129 = None

        set_statement131 = None

        end132 = None


        SET128_tree = None
        COMMA130_tree = None
        stream_SET = RewriteRuleTokenStream(self._adaptor, "token SET")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_set_statement = RewriteRuleSubtreeStream(self._adaptor, "rule set_statement")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:265:9: ( SET set_statement ( COMMA set_statement )* end -> ( set_statement )+ )
                # sdl92.g:265:17: SET set_statement ( COMMA set_statement )* end
                pass 
                SET128=self.match(self.input, SET, self.FOLLOW_SET_in_set_timer3549) 
                if self._state.backtracking == 0:
                    stream_SET.add(SET128)
                self._state.following.append(self.FOLLOW_set_statement_in_set_timer3551)
                set_statement129 = self.set_statement()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_set_statement.add(set_statement129.tree)
                # sdl92.g:265:35: ( COMMA set_statement )*
                while True: #loop45
                    alt45 = 2
                    LA45_0 = self.input.LA(1)

                    if (LA45_0 == COMMA) :
                        alt45 = 1


                    if alt45 == 1:
                        # sdl92.g:265:36: COMMA set_statement
                        pass 
                        COMMA130=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_set_timer3554) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(COMMA130)
                        self._state.following.append(self.FOLLOW_set_statement_in_set_timer3556)
                        set_statement131 = self.set_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_set_statement.add(set_statement131.tree)


                    else:
                        break #loop45
                self._state.following.append(self.FOLLOW_end_in_set_timer3560)
                end132 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end132.tree)

                # AST Rewrite
                # elements: set_statement
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 265:70: -> ( set_statement )+
                    # sdl92.g:265:73: ( set_statement )+
                    if not (stream_set_statement.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_set_statement.hasNext():
                        self._adaptor.addChild(root_0, stream_set_statement.nextTree())


                    stream_set_statement.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "set_timer"

    class set_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.set_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "set_statement"
    # sdl92.g:267:1: set_statement : L_PAREN ( expression COMMA )? timer_id R_PAREN -> ^( SET ( expression )? timer_id ) ;
    def set_statement(self, ):

        retval = self.set_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN133 = None
        COMMA135 = None
        R_PAREN137 = None
        expression134 = None

        timer_id136 = None


        L_PAREN133_tree = None
        COMMA135_tree = None
        R_PAREN137_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_timer_id = RewriteRuleSubtreeStream(self._adaptor, "rule timer_id")
        try:
            try:
                # sdl92.g:268:9: ( L_PAREN ( expression COMMA )? timer_id R_PAREN -> ^( SET ( expression )? timer_id ) )
                # sdl92.g:268:17: L_PAREN ( expression COMMA )? timer_id R_PAREN
                pass 
                L_PAREN133=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_set_statement3595) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN133)
                # sdl92.g:268:25: ( expression COMMA )?
                alt46 = 2
                LA46_0 = self.input.LA(1)

                if (LA46_0 == IF or LA46_0 == INT or LA46_0 == L_PAREN or LA46_0 == DASH or (BitStringLiteral <= LA46_0 <= L_BRACKET) or LA46_0 == NOT) :
                    alt46 = 1
                elif (LA46_0 == ID) :
                    LA46_2 = self.input.LA(2)

                    if (LA46_2 == ASTERISK or LA46_2 == L_PAREN or LA46_2 == COMMA or (EQ <= LA46_2 <= GE) or (IMPLIES <= LA46_2 <= REM) or LA46_2 == 166 or LA46_2 == 168) :
                        alt46 = 1
                if alt46 == 1:
                    # sdl92.g:268:26: expression COMMA
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_set_statement3598)
                    expression134 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression134.tree)
                    COMMA135=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_set_statement3600) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA135)



                self._state.following.append(self.FOLLOW_timer_id_in_set_statement3604)
                timer_id136 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_timer_id.add(timer_id136.tree)
                R_PAREN137=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_set_statement3606) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN137)

                # AST Rewrite
                # elements: expression, timer_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 268:75: -> ^( SET ( expression )? timer_id )
                    # sdl92.g:268:78: ^( SET ( expression )? timer_id )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SET, "SET"), root_1)

                    # sdl92.g:268:84: ( expression )?
                    if stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset();
                    self._adaptor.addChild(root_1, stream_timer_id.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "set_statement"

    class reset_timer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.reset_timer_return, self).__init__()

            self.tree = None




    # $ANTLR start "reset_timer"
    # sdl92.g:271:1: reset_timer : RESET reset_statement ( ',' reset_statement )* end -> ( reset_statement )+ ;
    def reset_timer(self, ):

        retval = self.reset_timer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        RESET138 = None
        char_literal140 = None
        reset_statement139 = None

        reset_statement141 = None

        end142 = None


        RESET138_tree = None
        char_literal140_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_RESET = RewriteRuleTokenStream(self._adaptor, "token RESET")
        stream_reset_statement = RewriteRuleSubtreeStream(self._adaptor, "rule reset_statement")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:272:9: ( RESET reset_statement ( ',' reset_statement )* end -> ( reset_statement )+ )
                # sdl92.g:272:17: RESET reset_statement ( ',' reset_statement )* end
                pass 
                RESET138=self.match(self.input, RESET, self.FOLLOW_RESET_in_reset_timer3676) 
                if self._state.backtracking == 0:
                    stream_RESET.add(RESET138)
                self._state.following.append(self.FOLLOW_reset_statement_in_reset_timer3678)
                reset_statement139 = self.reset_statement()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_reset_statement.add(reset_statement139.tree)
                # sdl92.g:272:39: ( ',' reset_statement )*
                while True: #loop47
                    alt47 = 2
                    LA47_0 = self.input.LA(1)

                    if (LA47_0 == COMMA) :
                        alt47 = 1


                    if alt47 == 1:
                        # sdl92.g:272:40: ',' reset_statement
                        pass 
                        char_literal140=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_reset_timer3681) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal140)
                        self._state.following.append(self.FOLLOW_reset_statement_in_reset_timer3683)
                        reset_statement141 = self.reset_statement()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_reset_statement.add(reset_statement141.tree)


                    else:
                        break #loop47
                self._state.following.append(self.FOLLOW_end_in_reset_timer3687)
                end142 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end142.tree)

                # AST Rewrite
                # elements: reset_statement
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 272:69: -> ( reset_statement )+
                    # sdl92.g:272:72: ( reset_statement )+
                    if not (stream_reset_statement.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_reset_statement.hasNext():
                        self._adaptor.addChild(root_0, stream_reset_statement.nextTree())


                    stream_reset_statement.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "reset_timer"

    class reset_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.reset_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "reset_statement"
    # sdl92.g:274:1: reset_statement : timer_id ( '(' expression_list ')' )? -> ^( RESET timer_id ( expression_list )? ) ;
    def reset_statement(self, ):

        retval = self.reset_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal144 = None
        char_literal146 = None
        timer_id143 = None

        expression_list145 = None


        char_literal144_tree = None
        char_literal146_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression_list = RewriteRuleSubtreeStream(self._adaptor, "rule expression_list")
        stream_timer_id = RewriteRuleSubtreeStream(self._adaptor, "rule timer_id")
        try:
            try:
                # sdl92.g:275:9: ( timer_id ( '(' expression_list ')' )? -> ^( RESET timer_id ( expression_list )? ) )
                # sdl92.g:275:17: timer_id ( '(' expression_list ')' )?
                pass 
                self._state.following.append(self.FOLLOW_timer_id_in_reset_statement3717)
                timer_id143 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_timer_id.add(timer_id143.tree)
                # sdl92.g:275:26: ( '(' expression_list ')' )?
                alt48 = 2
                LA48_0 = self.input.LA(1)

                if (LA48_0 == L_PAREN) :
                    alt48 = 1
                if alt48 == 1:
                    # sdl92.g:275:27: '(' expression_list ')'
                    pass 
                    char_literal144=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_reset_statement3720) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(char_literal144)
                    self._state.following.append(self.FOLLOW_expression_list_in_reset_statement3722)
                    expression_list145 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression_list.add(expression_list145.tree)
                    char_literal146=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_reset_statement3724) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(char_literal146)




                # AST Rewrite
                # elements: timer_id, expression_list
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 275:65: -> ^( RESET timer_id ( expression_list )? )
                    # sdl92.g:275:68: ^( RESET timer_id ( expression_list )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(RESET, "RESET"), root_1)

                    self._adaptor.addChild(root_1, stream_timer_id.nextTree())
                    # sdl92.g:275:85: ( expression_list )?
                    if stream_expression_list.hasNext():
                        self._adaptor.addChild(root_1, stream_expression_list.nextTree())


                    stream_expression_list.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "reset_statement"

    class transition_option_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.transition_option_return, self).__init__()

            self.tree = None




    # $ANTLR start "transition_option"
    # sdl92.g:277:1: transition_option : ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end -> ^( ALTERNATIVE answer_part alternative_part ) ;
    def transition_option(self, ):

        retval = self.transition_option_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ALTERNATIVE147 = None
        ENDALTERNATIVE151 = None
        e = None

        f = None

        alternative_question148 = None

        answer_part149 = None

        alternative_part150 = None


        ALTERNATIVE147_tree = None
        ENDALTERNATIVE151_tree = None
        stream_ALTERNATIVE = RewriteRuleTokenStream(self._adaptor, "token ALTERNATIVE")
        stream_ENDALTERNATIVE = RewriteRuleTokenStream(self._adaptor, "token ENDALTERNATIVE")
        stream_alternative_question = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_question")
        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_alternative_part = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_part")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:278:9: ( ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end -> ^( ALTERNATIVE answer_part alternative_part ) )
                # sdl92.g:278:17: ALTERNATIVE alternative_question e= end answer_part alternative_part ENDALTERNATIVE f= end
                pass 
                ALTERNATIVE147=self.match(self.input, ALTERNATIVE, self.FOLLOW_ALTERNATIVE_in_transition_option3771) 
                if self._state.backtracking == 0:
                    stream_ALTERNATIVE.add(ALTERNATIVE147)
                self._state.following.append(self.FOLLOW_alternative_question_in_transition_option3773)
                alternative_question148 = self.alternative_question()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_alternative_question.add(alternative_question148.tree)
                self._state.following.append(self.FOLLOW_end_in_transition_option3777)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                self._state.following.append(self.FOLLOW_answer_part_in_transition_option3795)
                answer_part149 = self.answer_part()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_answer_part.add(answer_part149.tree)
                self._state.following.append(self.FOLLOW_alternative_part_in_transition_option3813)
                alternative_part150 = self.alternative_part()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_alternative_part.add(alternative_part150.tree)
                ENDALTERNATIVE151=self.match(self.input, ENDALTERNATIVE, self.FOLLOW_ENDALTERNATIVE_in_transition_option3831) 
                if self._state.backtracking == 0:
                    stream_ENDALTERNATIVE.add(ENDALTERNATIVE151)
                self._state.following.append(self.FOLLOW_end_in_transition_option3835)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: alternative_part, ALTERNATIVE, answer_part
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 281:54: -> ^( ALTERNATIVE answer_part alternative_part )
                    # sdl92.g:281:57: ^( ALTERNATIVE answer_part alternative_part )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ALTERNATIVE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_answer_part.nextTree())
                    self._adaptor.addChild(root_1, stream_alternative_part.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "transition_option"

    class alternative_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.alternative_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "alternative_part"
    # sdl92.g:283:1: alternative_part : ( ( ( answer_part )+ ( else_part )? ) -> ( answer_part )+ ( else_part )? | else_part -> else_part );
    def alternative_part(self, ):

        retval = self.alternative_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        answer_part152 = None

        else_part153 = None

        else_part154 = None


        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_else_part = RewriteRuleSubtreeStream(self._adaptor, "rule else_part")
        try:
            try:
                # sdl92.g:284:9: ( ( ( answer_part )+ ( else_part )? ) -> ( answer_part )+ ( else_part )? | else_part -> else_part )
                alt51 = 2
                alt51 = self.dfa51.predict(self.input)
                if alt51 == 1:
                    # sdl92.g:284:17: ( ( answer_part )+ ( else_part )? )
                    pass 
                    # sdl92.g:284:17: ( ( answer_part )+ ( else_part )? )
                    # sdl92.g:284:18: ( answer_part )+ ( else_part )?
                    pass 
                    # sdl92.g:284:18: ( answer_part )+
                    cnt49 = 0
                    while True: #loop49
                        alt49 = 2
                        alt49 = self.dfa49.predict(self.input)
                        if alt49 == 1:
                            # sdl92.g:0:0: answer_part
                            pass 
                            self._state.following.append(self.FOLLOW_answer_part_in_alternative_part3900)
                            answer_part152 = self.answer_part()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_answer_part.add(answer_part152.tree)


                        else:
                            if cnt49 >= 1:
                                break #loop49

                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            eee = EarlyExitException(49, self.input)
                            raise eee

                        cnt49 += 1
                    # sdl92.g:284:31: ( else_part )?
                    alt50 = 2
                    LA50_0 = self.input.LA(1)

                    if (LA50_0 == ELSE or LA50_0 == 176) :
                        alt50 = 1
                    if alt50 == 1:
                        # sdl92.g:0:0: else_part
                        pass 
                        self._state.following.append(self.FOLLOW_else_part_in_alternative_part3903)
                        else_part153 = self.else_part()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_else_part.add(else_part153.tree)







                    # AST Rewrite
                    # elements: else_part, answer_part
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 284:57: -> ( answer_part )+ ( else_part )?
                        # sdl92.g:284:60: ( answer_part )+
                        if not (stream_answer_part.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_answer_part.hasNext():
                            self._adaptor.addChild(root_0, stream_answer_part.nextTree())


                        stream_answer_part.reset()
                        # sdl92.g:284:73: ( else_part )?
                        if stream_else_part.hasNext():
                            self._adaptor.addChild(root_0, stream_else_part.nextTree())


                        stream_else_part.reset();



                        retval.tree = root_0


                elif alt51 == 2:
                    # sdl92.g:285:19: else_part
                    pass 
                    self._state.following.append(self.FOLLOW_else_part_in_alternative_part3947)
                    else_part154 = self.else_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_else_part.add(else_part154.tree)

                    # AST Rewrite
                    # elements: else_part
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 285:57: -> else_part
                        self._adaptor.addChild(root_0, stream_else_part.nextTree())



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "alternative_part"

    class alternative_question_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.alternative_question_return, self).__init__()

            self.tree = None




    # $ANTLR start "alternative_question"
    # sdl92.g:288:1: alternative_question : ( expression | informal_text );
    def alternative_question(self, ):

        retval = self.alternative_question_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression155 = None

        informal_text156 = None



        try:
            try:
                # sdl92.g:289:9: ( expression | informal_text )
                alt52 = 2
                LA52_0 = self.input.LA(1)

                if (LA52_0 == IF or LA52_0 == INT or LA52_0 == L_PAREN or LA52_0 == ID or LA52_0 == DASH or (BitStringLiteral <= LA52_0 <= FALSE) or (NULL <= LA52_0 <= L_BRACKET) or LA52_0 == NOT) :
                    alt52 = 1
                elif (LA52_0 == StringLiteral) :
                    LA52_2 = self.input.LA(2)

                    if (self.synpred61_sdl92()) :
                        alt52 = 1
                    elif (True) :
                        alt52 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 52, 2, self.input)

                        raise nvae

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 52, 0, self.input)

                    raise nvae

                if alt52 == 1:
                    # sdl92.g:289:17: expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_expression_in_alternative_question4003)
                    expression155 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression155.tree)


                elif alt52 == 2:
                    # sdl92.g:289:30: informal_text
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_informal_text_in_alternative_question4007)
                    informal_text156 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, informal_text156.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "alternative_question"

    class decision_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.decision_return, self).__init__()

            self.tree = None




    # $ANTLR start "decision"
    # sdl92.g:292:1: decision : ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? ) ;
    def decision(self, ):

        retval = self.decision_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DECISION159 = None
        ENDDECISION163 = None
        e = None

        f = None

        cif157 = None

        hyperlink158 = None

        question160 = None

        answer_part161 = None

        alternative_part162 = None


        DECISION159_tree = None
        ENDDECISION163_tree = None
        stream_DECISION = RewriteRuleTokenStream(self._adaptor, "token DECISION")
        stream_ENDDECISION = RewriteRuleTokenStream(self._adaptor, "token ENDDECISION")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_answer_part = RewriteRuleSubtreeStream(self._adaptor, "rule answer_part")
        stream_question = RewriteRuleSubtreeStream(self._adaptor, "rule question")
        stream_alternative_part = RewriteRuleSubtreeStream(self._adaptor, "rule alternative_part")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:293:9: ( ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? ) )
                # sdl92.g:293:17: ( cif )? ( hyperlink )? DECISION question e= end ( answer_part )? ( alternative_part )? ENDDECISION f= end
                pass 
                # sdl92.g:293:17: ( cif )?
                alt53 = 2
                LA53_0 = self.input.LA(1)

                if (LA53_0 == 176) :
                    LA53_1 = self.input.LA(2)

                    if (LA53_1 == LABEL or LA53_1 == COMMENT or LA53_1 == STATE or LA53_1 == PROVIDED or LA53_1 == INPUT or LA53_1 == DECISION or LA53_1 == ANSWER or LA53_1 == OUTPUT or (TEXT <= LA53_1 <= JOIN) or LA53_1 == TASK or LA53_1 == START or LA53_1 == PROCEDURE) :
                        alt53 = 1
                if alt53 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_decision4038)
                    cif157 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif157.tree)



                # sdl92.g:294:17: ( hyperlink )?
                alt54 = 2
                LA54_0 = self.input.LA(1)

                if (LA54_0 == 176) :
                    alt54 = 1
                if alt54 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_decision4057)
                    hyperlink158 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink158.tree)



                DECISION159=self.match(self.input, DECISION, self.FOLLOW_DECISION_in_decision4076) 
                if self._state.backtracking == 0:
                    stream_DECISION.add(DECISION159)
                self._state.following.append(self.FOLLOW_question_in_decision4078)
                question160 = self.question()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_question.add(question160.tree)
                self._state.following.append(self.FOLLOW_end_in_decision4082)
                e = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(e.tree)
                # sdl92.g:296:17: ( answer_part )?
                alt55 = 2
                LA55_0 = self.input.LA(1)

                if (LA55_0 == 176) :
                    LA55_1 = self.input.LA(2)

                    if (self.synpred64_sdl92()) :
                        alt55 = 1
                elif (LA55_0 == L_PAREN) :
                    LA55_2 = self.input.LA(2)

                    if (self.synpred64_sdl92()) :
                        alt55 = 1
                if alt55 == 1:
                    # sdl92.g:0:0: answer_part
                    pass 
                    self._state.following.append(self.FOLLOW_answer_part_in_decision4111)
                    answer_part161 = self.answer_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_answer_part.add(answer_part161.tree)



                # sdl92.g:297:17: ( alternative_part )?
                alt56 = 2
                LA56_0 = self.input.LA(1)

                if (LA56_0 == ELSE or LA56_0 == L_PAREN or LA56_0 == 176) :
                    alt56 = 1
                if alt56 == 1:
                    # sdl92.g:0:0: alternative_part
                    pass 
                    self._state.following.append(self.FOLLOW_alternative_part_in_decision4130)
                    alternative_part162 = self.alternative_part()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_alternative_part.add(alternative_part162.tree)



                ENDDECISION163=self.match(self.input, ENDDECISION, self.FOLLOW_ENDDECISION_in_decision4149) 
                if self._state.backtracking == 0:
                    stream_ENDDECISION.add(ENDDECISION163)
                self._state.following.append(self.FOLLOW_end_in_decision4153)
                f = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(f.tree)

                # AST Rewrite
                # elements: alternative_part, answer_part, hyperlink, question, DECISION, cif, e
                # token labels: 
                # rule labels: retval, e
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if e is not None:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "rule e", e.tree)
                    else:
                        stream_e = RewriteRuleSubtreeStream(self._adaptor, "token e", None)


                    root_0 = self._adaptor.nil()
                    # 298:55: -> ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? )
                    # sdl92.g:298:58: ^( DECISION ( cif )? ( hyperlink )? ( $e)? question ( answer_part )? ( alternative_part )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_DECISION.nextNode(), root_1)

                    # sdl92.g:298:69: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:298:74: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:298:85: ( $e)?
                    if stream_e.hasNext():
                        self._adaptor.addChild(root_1, stream_e.nextTree())


                    stream_e.reset();
                    self._adaptor.addChild(root_1, stream_question.nextTree())
                    # sdl92.g:298:98: ( answer_part )?
                    if stream_answer_part.hasNext():
                        self._adaptor.addChild(root_1, stream_answer_part.nextTree())


                    stream_answer_part.reset();
                    # sdl92.g:298:111: ( alternative_part )?
                    if stream_alternative_part.hasNext():
                        self._adaptor.addChild(root_1, stream_alternative_part.nextTree())


                    stream_alternative_part.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "decision"

    class answer_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.answer_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "answer_part"
    # sdl92.g:300:1: answer_part : ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )? -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? ) ;
    def answer_part(self, ):

        retval = self.answer_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN166 = None
        R_PAREN168 = None
        char_literal169 = None
        cif164 = None

        hyperlink165 = None

        answer167 = None

        transition170 = None


        L_PAREN166_tree = None
        R_PAREN168_tree = None
        char_literal169_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_166 = RewriteRuleTokenStream(self._adaptor, "token 166")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_answer = RewriteRuleSubtreeStream(self._adaptor, "rule answer")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        try:
            try:
                # sdl92.g:301:9: ( ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )? -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? ) )
                # sdl92.g:301:17: ( cif )? ( hyperlink )? L_PAREN answer R_PAREN ':' ( transition )?
                pass 
                # sdl92.g:301:17: ( cif )?
                alt57 = 2
                LA57_0 = self.input.LA(1)

                if (LA57_0 == 176) :
                    LA57_1 = self.input.LA(2)

                    if (LA57_1 == LABEL or LA57_1 == COMMENT or LA57_1 == STATE or LA57_1 == PROVIDED or LA57_1 == INPUT or LA57_1 == DECISION or LA57_1 == ANSWER or LA57_1 == OUTPUT or (TEXT <= LA57_1 <= JOIN) or LA57_1 == TASK or LA57_1 == START or LA57_1 == PROCEDURE) :
                        alt57 = 1
                if alt57 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_answer_part4235)
                    cif164 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif164.tree)



                # sdl92.g:302:17: ( hyperlink )?
                alt58 = 2
                LA58_0 = self.input.LA(1)

                if (LA58_0 == 176) :
                    alt58 = 1
                if alt58 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_answer_part4254)
                    hyperlink165 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink165.tree)



                L_PAREN166=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_answer_part4273) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN166)
                self._state.following.append(self.FOLLOW_answer_in_answer_part4275)
                answer167 = self.answer()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_answer.add(answer167.tree)
                R_PAREN168=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_answer_part4277) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN168)
                char_literal169=self.match(self.input, 166, self.FOLLOW_166_in_answer_part4279) 
                if self._state.backtracking == 0:
                    stream_166.add(char_literal169)
                # sdl92.g:303:44: ( transition )?
                alt59 = 2
                alt59 = self.dfa59.predict(self.input)
                if alt59 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_answer_part4281)
                    transition170 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition170.tree)




                # AST Rewrite
                # elements: transition, cif, answer, hyperlink
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 303:65: -> ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? )
                    # sdl92.g:303:68: ^( ANSWER ( cif )? ( hyperlink )? answer ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ANSWER, "ANSWER"), root_1)

                    # sdl92.g:303:77: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:303:82: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    self._adaptor.addChild(root_1, stream_answer.nextTree())
                    # sdl92.g:303:100: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "answer_part"

    class answer_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.answer_return, self).__init__()

            self.tree = None




    # $ANTLR start "answer"
    # sdl92.g:305:1: answer : ( range_condition | informal_text );
    def answer(self, ):

        retval = self.answer_return()
        retval.start = self.input.LT(1)

        root_0 = None

        range_condition171 = None

        informal_text172 = None



        try:
            try:
                # sdl92.g:306:9: ( range_condition | informal_text )
                alt60 = 2
                LA60_0 = self.input.LA(1)

                if (LA60_0 == IF or LA60_0 == INT or LA60_0 == L_PAREN or (EQ <= LA60_0 <= GE) or LA60_0 == ID or LA60_0 == DASH or (BitStringLiteral <= LA60_0 <= FALSE) or (NULL <= LA60_0 <= L_BRACKET) or LA60_0 == NOT) :
                    alt60 = 1
                elif (LA60_0 == StringLiteral) :
                    LA60_2 = self.input.LA(2)

                    if (self.synpred69_sdl92()) :
                        alt60 = 1
                    elif (True) :
                        alt60 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 60, 2, self.input)

                        raise nvae

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 60, 0, self.input)

                    raise nvae

                if alt60 == 1:
                    # sdl92.g:306:17: range_condition
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_range_condition_in_answer4341)
                    range_condition171 = self.range_condition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, range_condition171.tree)


                elif alt60 == 2:
                    # sdl92.g:307:19: informal_text
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_informal_text_in_answer4361)
                    informal_text172 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, informal_text172.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "answer"

    class else_part_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.else_part_return, self).__init__()

            self.tree = None




    # $ANTLR start "else_part"
    # sdl92.g:309:1: else_part : ( cif )? ( hyperlink )? ELSE ':' ( transition )? -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? ) ;
    def else_part(self, ):

        retval = self.else_part_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ELSE175 = None
        char_literal176 = None
        cif173 = None

        hyperlink174 = None

        transition177 = None


        ELSE175_tree = None
        char_literal176_tree = None
        stream_166 = RewriteRuleTokenStream(self._adaptor, "token 166")
        stream_ELSE = RewriteRuleTokenStream(self._adaptor, "token ELSE")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_transition = RewriteRuleSubtreeStream(self._adaptor, "rule transition")
        try:
            try:
                # sdl92.g:310:9: ( ( cif )? ( hyperlink )? ELSE ':' ( transition )? -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? ) )
                # sdl92.g:310:17: ( cif )? ( hyperlink )? ELSE ':' ( transition )?
                pass 
                # sdl92.g:310:17: ( cif )?
                alt61 = 2
                LA61_0 = self.input.LA(1)

                if (LA61_0 == 176) :
                    LA61_1 = self.input.LA(2)

                    if (LA61_1 == LABEL or LA61_1 == COMMENT or LA61_1 == STATE or LA61_1 == PROVIDED or LA61_1 == INPUT or LA61_1 == DECISION or LA61_1 == ANSWER or LA61_1 == OUTPUT or (TEXT <= LA61_1 <= JOIN) or LA61_1 == TASK or LA61_1 == START or LA61_1 == PROCEDURE) :
                        alt61 = 1
                if alt61 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_else_part4390)
                    cif173 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif173.tree)



                # sdl92.g:311:17: ( hyperlink )?
                alt62 = 2
                LA62_0 = self.input.LA(1)

                if (LA62_0 == 176) :
                    alt62 = 1
                if alt62 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_else_part4409)
                    hyperlink174 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink174.tree)



                ELSE175=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_else_part4428) 
                if self._state.backtracking == 0:
                    stream_ELSE.add(ELSE175)
                char_literal176=self.match(self.input, 166, self.FOLLOW_166_in_else_part4430) 
                if self._state.backtracking == 0:
                    stream_166.add(char_literal176)
                # sdl92.g:312:26: ( transition )?
                alt63 = 2
                LA63_0 = self.input.LA(1)

                if ((SET <= LA63_0 <= ALTERNATIVE) or LA63_0 == OUTPUT or (NEXTSTATE <= LA63_0 <= JOIN) or LA63_0 == RETURN or LA63_0 == TASK or LA63_0 == CALL or LA63_0 == CREATE or LA63_0 == ID or LA63_0 == STOP or LA63_0 == 176) :
                    alt63 = 1
                if alt63 == 1:
                    # sdl92.g:0:0: transition
                    pass 
                    self._state.following.append(self.FOLLOW_transition_in_else_part4432)
                    transition177 = self.transition()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_transition.add(transition177.tree)




                # AST Rewrite
                # elements: cif, transition, hyperlink, ELSE
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 312:61: -> ^( ELSE ( cif )? ( hyperlink )? ( transition )? )
                    # sdl92.g:312:64: ^( ELSE ( cif )? ( hyperlink )? ( transition )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ELSE.nextNode(), root_1)

                    # sdl92.g:312:71: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:312:76: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:312:87: ( transition )?
                    if stream_transition.hasNext():
                        self._adaptor.addChild(root_1, stream_transition.nextTree())


                    stream_transition.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "else_part"

    class question_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.question_return, self).__init__()

            self.tree = None




    # $ANTLR start "question"
    # sdl92.g:314:1: question : ( expression -> ^( QUESTION expression ) | informal_text -> informal_text | ANY -> ^( ANY ) );
    def question(self, ):

        retval = self.question_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ANY180 = None
        expression178 = None

        informal_text179 = None


        ANY180_tree = None
        stream_ANY = RewriteRuleTokenStream(self._adaptor, "token ANY")
        stream_informal_text = RewriteRuleSubtreeStream(self._adaptor, "rule informal_text")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:315:9: ( expression -> ^( QUESTION expression ) | informal_text -> informal_text | ANY -> ^( ANY ) )
                alt64 = 3
                LA64 = self.input.LA(1)
                if LA64 == IF or LA64 == INT or LA64 == L_PAREN or LA64 == ID or LA64 == DASH or LA64 == BitStringLiteral or LA64 == OctetStringLiteral or LA64 == TRUE or LA64 == FALSE or LA64 == NULL or LA64 == PLUS_INFINITY or LA64 == MINUS_INFINITY or LA64 == FloatingPointLiteral or LA64 == L_BRACKET or LA64 == NOT:
                    alt64 = 1
                elif LA64 == StringLiteral:
                    LA64_2 = self.input.LA(2)

                    if (self.synpred73_sdl92()) :
                        alt64 = 1
                    elif (self.synpred74_sdl92()) :
                        alt64 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 64, 2, self.input)

                        raise nvae

                elif LA64 == ANY:
                    alt64 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 64, 0, self.input)

                    raise nvae

                if alt64 == 1:
                    # sdl92.g:315:17: expression
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_question4509)
                    expression178 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression178.tree)

                    # AST Rewrite
                    # elements: expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 315:61: -> ^( QUESTION expression )
                        # sdl92.g:315:64: ^( QUESTION expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(QUESTION, "QUESTION"), root_1)

                        self._adaptor.addChild(root_1, stream_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt64 == 2:
                    # sdl92.g:316:19: informal_text
                    pass 
                    self._state.following.append(self.FOLLOW_informal_text_in_question4571)
                    informal_text179 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_informal_text.add(informal_text179.tree)

                    # AST Rewrite
                    # elements: informal_text
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 316:61: -> informal_text
                        self._adaptor.addChild(root_0, stream_informal_text.nextTree())



                        retval.tree = root_0


                elif alt64 == 3:
                    # sdl92.g:317:19: ANY
                    pass 
                    ANY180=self.match(self.input, ANY, self.FOLLOW_ANY_in_question4623) 
                    if self._state.backtracking == 0:
                        stream_ANY.add(ANY180)

                    # AST Rewrite
                    # elements: ANY
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 317:61: -> ^( ANY )
                        # sdl92.g:317:64: ^( ANY )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_ANY.nextNode(), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "question"

    class range_condition_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.range_condition_return, self).__init__()

            self.tree = None




    # $ANTLR start "range_condition"
    # sdl92.g:319:1: range_condition : ( closed_range | open_range ) ;
    def range_condition(self, ):

        retval = self.range_condition_return()
        retval.start = self.input.LT(1)

        root_0 = None

        closed_range181 = None

        open_range182 = None



        try:
            try:
                # sdl92.g:320:9: ( ( closed_range | open_range ) )
                # sdl92.g:320:17: ( closed_range | open_range )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:320:17: ( closed_range | open_range )
                alt65 = 2
                LA65_0 = self.input.LA(1)

                if (LA65_0 == INT) :
                    LA65_1 = self.input.LA(2)

                    if (LA65_1 == 166) :
                        alt65 = 1
                    elif (LA65_1 == EOF or LA65_1 == ASTERISK or (L_PAREN <= LA65_1 <= R_PAREN) or (EQ <= LA65_1 <= GE) or (IMPLIES <= LA65_1 <= REM) or LA65_1 == 168) :
                        alt65 = 2
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 65, 1, self.input)

                        raise nvae

                elif (LA65_0 == IF or LA65_0 == L_PAREN or (EQ <= LA65_0 <= GE) or LA65_0 == ID or LA65_0 == DASH or (BitStringLiteral <= LA65_0 <= L_BRACKET) or LA65_0 == NOT) :
                    alt65 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 65, 0, self.input)

                    raise nvae

                if alt65 == 1:
                    # sdl92.g:320:18: closed_range
                    pass 
                    self._state.following.append(self.FOLLOW_closed_range_in_range_condition4690)
                    closed_range181 = self.closed_range()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, closed_range181.tree)


                elif alt65 == 2:
                    # sdl92.g:320:33: open_range
                    pass 
                    self._state.following.append(self.FOLLOW_open_range_in_range_condition4694)
                    open_range182 = self.open_range()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, open_range182.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "range_condition"

    class closed_range_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.closed_range_return, self).__init__()

            self.tree = None




    # $ANTLR start "closed_range"
    # sdl92.g:323:1: closed_range : a= INT ':' b= INT -> ^( CLOSED_RANGE $a $b) ;
    def closed_range(self, ):

        retval = self.closed_range_return()
        retval.start = self.input.LT(1)

        root_0 = None

        a = None
        b = None
        char_literal183 = None

        a_tree = None
        b_tree = None
        char_literal183_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_166 = RewriteRuleTokenStream(self._adaptor, "token 166")

        try:
            try:
                # sdl92.g:324:9: (a= INT ':' b= INT -> ^( CLOSED_RANGE $a $b) )
                # sdl92.g:324:17: a= INT ':' b= INT
                pass 
                a=self.match(self.input, INT, self.FOLLOW_INT_in_closed_range4744) 
                if self._state.backtracking == 0:
                    stream_INT.add(a)
                char_literal183=self.match(self.input, 166, self.FOLLOW_166_in_closed_range4746) 
                if self._state.backtracking == 0:
                    stream_166.add(char_literal183)
                b=self.match(self.input, INT, self.FOLLOW_INT_in_closed_range4750) 
                if self._state.backtracking == 0:
                    stream_INT.add(b)

                # AST Rewrite
                # elements: b, a
                # token labels: b, a
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_b = RewriteRuleTokenStream(self._adaptor, "token b", b)
                    stream_a = RewriteRuleTokenStream(self._adaptor, "token a", a)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 324:51: -> ^( CLOSED_RANGE $a $b)
                    # sdl92.g:324:54: ^( CLOSED_RANGE $a $b)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CLOSED_RANGE, "CLOSED_RANGE"), root_1)

                    self._adaptor.addChild(root_1, stream_a.nextNode())
                    self._adaptor.addChild(root_1, stream_b.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "closed_range"

    class open_range_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.open_range_return, self).__init__()

            self.tree = None




    # $ANTLR start "open_range"
    # sdl92.g:326:1: open_range : ( constant -> constant | ( ( EQ | NEQ | GT | LT | LE | GE ) constant ) -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant ) );
    def open_range(self, ):

        retval = self.open_range_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EQ185 = None
        NEQ186 = None
        GT187 = None
        LT188 = None
        LE189 = None
        GE190 = None
        constant184 = None

        constant191 = None


        EQ185_tree = None
        NEQ186_tree = None
        GT187_tree = None
        LT188_tree = None
        LE189_tree = None
        GE190_tree = None
        stream_GT = RewriteRuleTokenStream(self._adaptor, "token GT")
        stream_GE = RewriteRuleTokenStream(self._adaptor, "token GE")
        stream_LT = RewriteRuleTokenStream(self._adaptor, "token LT")
        stream_NEQ = RewriteRuleTokenStream(self._adaptor, "token NEQ")
        stream_EQ = RewriteRuleTokenStream(self._adaptor, "token EQ")
        stream_LE = RewriteRuleTokenStream(self._adaptor, "token LE")
        stream_constant = RewriteRuleSubtreeStream(self._adaptor, "rule constant")
        try:
            try:
                # sdl92.g:327:9: ( constant -> constant | ( ( EQ | NEQ | GT | LT | LE | GE ) constant ) -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant ) )
                alt67 = 2
                LA67_0 = self.input.LA(1)

                if (LA67_0 == IF or LA67_0 == INT or LA67_0 == L_PAREN or LA67_0 == ID or LA67_0 == DASH or (BitStringLiteral <= LA67_0 <= L_BRACKET) or LA67_0 == NOT) :
                    alt67 = 1
                elif ((EQ <= LA67_0 <= GE)) :
                    alt67 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 67, 0, self.input)

                    raise nvae

                if alt67 == 1:
                    # sdl92.g:327:17: constant
                    pass 
                    self._state.following.append(self.FOLLOW_constant_in_open_range4810)
                    constant184 = self.constant()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_constant.add(constant184.tree)

                    # AST Rewrite
                    # elements: constant
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 327:57: -> constant
                        self._adaptor.addChild(root_0, stream_constant.nextTree())



                        retval.tree = root_0


                elif alt67 == 2:
                    # sdl92.g:328:19: ( ( EQ | NEQ | GT | LT | LE | GE ) constant )
                    pass 
                    # sdl92.g:328:19: ( ( EQ | NEQ | GT | LT | LE | GE ) constant )
                    # sdl92.g:328:21: ( EQ | NEQ | GT | LT | LE | GE ) constant
                    pass 
                    # sdl92.g:328:21: ( EQ | NEQ | GT | LT | LE | GE )
                    alt66 = 6
                    LA66 = self.input.LA(1)
                    if LA66 == EQ:
                        alt66 = 1
                    elif LA66 == NEQ:
                        alt66 = 2
                    elif LA66 == GT:
                        alt66 = 3
                    elif LA66 == LT:
                        alt66 = 4
                    elif LA66 == LE:
                        alt66 = 5
                    elif LA66 == GE:
                        alt66 = 6
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 66, 0, self.input)

                        raise nvae

                    if alt66 == 1:
                        # sdl92.g:328:22: EQ
                        pass 
                        EQ185=self.match(self.input, EQ, self.FOLLOW_EQ_in_open_range4868) 
                        if self._state.backtracking == 0:
                            stream_EQ.add(EQ185)


                    elif alt66 == 2:
                        # sdl92.g:328:25: NEQ
                        pass 
                        NEQ186=self.match(self.input, NEQ, self.FOLLOW_NEQ_in_open_range4870) 
                        if self._state.backtracking == 0:
                            stream_NEQ.add(NEQ186)


                    elif alt66 == 3:
                        # sdl92.g:328:29: GT
                        pass 
                        GT187=self.match(self.input, GT, self.FOLLOW_GT_in_open_range4872) 
                        if self._state.backtracking == 0:
                            stream_GT.add(GT187)


                    elif alt66 == 4:
                        # sdl92.g:328:32: LT
                        pass 
                        LT188=self.match(self.input, LT, self.FOLLOW_LT_in_open_range4874) 
                        if self._state.backtracking == 0:
                            stream_LT.add(LT188)


                    elif alt66 == 5:
                        # sdl92.g:328:35: LE
                        pass 
                        LE189=self.match(self.input, LE, self.FOLLOW_LE_in_open_range4876) 
                        if self._state.backtracking == 0:
                            stream_LE.add(LE189)


                    elif alt66 == 6:
                        # sdl92.g:328:38: GE
                        pass 
                        GE190=self.match(self.input, GE, self.FOLLOW_GE_in_open_range4878) 
                        if self._state.backtracking == 0:
                            stream_GE.add(GE190)



                    self._state.following.append(self.FOLLOW_constant_in_open_range4881)
                    constant191 = self.constant()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_constant.add(constant191.tree)




                    # AST Rewrite
                    # elements: LE, constant, EQ, GT, LT, NEQ, GE
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 328:57: -> ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant )
                        # sdl92.g:328:60: ^( OPEN_RANGE ( EQ )? ( NEQ )? ( GT )? ( LT )? ( LE )? ( GE )? constant )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OPEN_RANGE, "OPEN_RANGE"), root_1)

                        # sdl92.g:328:73: ( EQ )?
                        if stream_EQ.hasNext():
                            self._adaptor.addChild(root_1, stream_EQ.nextNode())


                        stream_EQ.reset();
                        # sdl92.g:328:77: ( NEQ )?
                        if stream_NEQ.hasNext():
                            self._adaptor.addChild(root_1, stream_NEQ.nextNode())


                        stream_NEQ.reset();
                        # sdl92.g:328:82: ( GT )?
                        if stream_GT.hasNext():
                            self._adaptor.addChild(root_1, stream_GT.nextNode())


                        stream_GT.reset();
                        # sdl92.g:328:86: ( LT )?
                        if stream_LT.hasNext():
                            self._adaptor.addChild(root_1, stream_LT.nextNode())


                        stream_LT.reset();
                        # sdl92.g:328:90: ( LE )?
                        if stream_LE.hasNext():
                            self._adaptor.addChild(root_1, stream_LE.nextNode())


                        stream_LE.reset();
                        # sdl92.g:328:94: ( GE )?
                        if stream_GE.hasNext():
                            self._adaptor.addChild(root_1, stream_GE.nextNode())


                        stream_GE.reset();
                        self._adaptor.addChild(root_1, stream_constant.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "open_range"

    class constant_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.constant_return, self).__init__()

            self.tree = None




    # $ANTLR start "constant"
    # sdl92.g:330:1: constant : expression -> ^( CONSTANT expression ) ;
    def constant(self, ):

        retval = self.constant_return()
        retval.start = self.input.LT(1)

        root_0 = None

        expression192 = None


        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:331:9: ( expression -> ^( CONSTANT expression ) )
                # sdl92.g:331:17: expression
                pass 
                self._state.following.append(self.FOLLOW_expression_in_constant4951)
                expression192 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression192.tree)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 331:57: -> ^( CONSTANT expression )
                    # sdl92.g:331:60: ^( CONSTANT expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CONSTANT, "CONSTANT"), root_1)

                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "constant"

    class create_request_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.create_request_return, self).__init__()

            self.tree = None




    # $ANTLR start "create_request"
    # sdl92.g:333:1: create_request : CREATE createbody ( actual_parameters )? end -> ^( CREATE createbody ( actual_parameters )? ) ;
    def create_request(self, ):

        retval = self.create_request_return()
        retval.start = self.input.LT(1)

        root_0 = None

        CREATE193 = None
        createbody194 = None

        actual_parameters195 = None

        end196 = None


        CREATE193_tree = None
        stream_CREATE = RewriteRuleTokenStream(self._adaptor, "token CREATE")
        stream_createbody = RewriteRuleSubtreeStream(self._adaptor, "rule createbody")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        stream_actual_parameters = RewriteRuleSubtreeStream(self._adaptor, "rule actual_parameters")
        try:
            try:
                # sdl92.g:334:9: ( CREATE createbody ( actual_parameters )? end -> ^( CREATE createbody ( actual_parameters )? ) )
                # sdl92.g:334:17: CREATE createbody ( actual_parameters )? end
                pass 
                CREATE193=self.match(self.input, CREATE, self.FOLLOW_CREATE_in_create_request5010) 
                if self._state.backtracking == 0:
                    stream_CREATE.add(CREATE193)
                self._state.following.append(self.FOLLOW_createbody_in_create_request5029)
                createbody194 = self.createbody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_createbody.add(createbody194.tree)
                # sdl92.g:336:17: ( actual_parameters )?
                alt68 = 2
                LA68_0 = self.input.LA(1)

                if (LA68_0 == L_PAREN) :
                    alt68 = 1
                if alt68 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_create_request5047)
                    actual_parameters195 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_actual_parameters.add(actual_parameters195.tree)



                self._state.following.append(self.FOLLOW_end_in_create_request5050)
                end196 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end196.tree)

                # AST Rewrite
                # elements: actual_parameters, CREATE, createbody
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 336:57: -> ^( CREATE createbody ( actual_parameters )? )
                    # sdl92.g:336:60: ^( CREATE createbody ( actual_parameters )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_CREATE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_createbody.nextTree())
                    # sdl92.g:336:80: ( actual_parameters )?
                    if stream_actual_parameters.hasNext():
                        self._adaptor.addChild(root_1, stream_actual_parameters.nextTree())


                    stream_actual_parameters.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "create_request"

    class createbody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.createbody_return, self).__init__()

            self.tree = None




    # $ANTLR start "createbody"
    # sdl92.g:338:1: createbody : ( process_id | THIS );
    def createbody(self, ):

        retval = self.createbody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        THIS198 = None
        process_id197 = None


        THIS198_tree = None

        try:
            try:
                # sdl92.g:339:9: ( process_id | THIS )
                alt69 = 2
                LA69_0 = self.input.LA(1)

                if (LA69_0 == ID) :
                    alt69 = 1
                elif (LA69_0 == THIS) :
                    alt69 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 69, 0, self.input)

                    raise nvae

                if alt69 == 1:
                    # sdl92.g:339:17: process_id
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_process_id_in_createbody5106)
                    process_id197 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, process_id197.tree)


                elif alt69 == 2:
                    # sdl92.g:340:19: THIS
                    pass 
                    root_0 = self._adaptor.nil()

                    THIS198=self.match(self.input, THIS, self.FOLLOW_THIS_in_createbody5126)
                    if self._state.backtracking == 0:

                        THIS198_tree = self._adaptor.createWithPayload(THIS198)
                        self._adaptor.addChild(root_0, THIS198_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "createbody"

    class output_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.output_return, self).__init__()

            self.tree = None




    # $ANTLR start "output"
    # sdl92.g:342:1: output : ( cif )? ( hyperlink )? OUTPUT outputbody end -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody ) ;
    def output(self, ):

        retval = self.output_return()
        retval.start = self.input.LT(1)

        root_0 = None

        OUTPUT201 = None
        cif199 = None

        hyperlink200 = None

        outputbody202 = None

        end203 = None


        OUTPUT201_tree = None
        stream_OUTPUT = RewriteRuleTokenStream(self._adaptor, "token OUTPUT")
        stream_outputbody = RewriteRuleSubtreeStream(self._adaptor, "rule outputbody")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:343:9: ( ( cif )? ( hyperlink )? OUTPUT outputbody end -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody ) )
                # sdl92.g:343:17: ( cif )? ( hyperlink )? OUTPUT outputbody end
                pass 
                # sdl92.g:343:17: ( cif )?
                alt70 = 2
                LA70_0 = self.input.LA(1)

                if (LA70_0 == 176) :
                    LA70_1 = self.input.LA(2)

                    if (LA70_1 == LABEL or LA70_1 == COMMENT or LA70_1 == STATE or LA70_1 == PROVIDED or LA70_1 == INPUT or LA70_1 == DECISION or LA70_1 == ANSWER or LA70_1 == OUTPUT or (TEXT <= LA70_1 <= JOIN) or LA70_1 == TASK or LA70_1 == START or LA70_1 == PROCEDURE) :
                        alt70 = 1
                if alt70 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_output5150)
                    cif199 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif199.tree)



                # sdl92.g:344:17: ( hyperlink )?
                alt71 = 2
                LA71_0 = self.input.LA(1)

                if (LA71_0 == 176) :
                    alt71 = 1
                if alt71 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_output5169)
                    hyperlink200 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink200.tree)



                OUTPUT201=self.match(self.input, OUTPUT, self.FOLLOW_OUTPUT_in_output5188) 
                if self._state.backtracking == 0:
                    stream_OUTPUT.add(OUTPUT201)
                self._state.following.append(self.FOLLOW_outputbody_in_output5190)
                outputbody202 = self.outputbody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_outputbody.add(outputbody202.tree)
                self._state.following.append(self.FOLLOW_end_in_output5192)
                end203 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end203.tree)

                # AST Rewrite
                # elements: end, cif, OUTPUT, outputbody, hyperlink
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 345:58: -> ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody )
                    # sdl92.g:345:61: ^( OUTPUT ( cif )? ( hyperlink )? ( end )? outputbody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_OUTPUT.nextNode(), root_1)

                    # sdl92.g:345:70: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:345:75: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:345:86: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_outputbody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "output"

    class outputbody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.outputbody_return, self).__init__()

            self.tree = None




    # $ANTLR start "outputbody"
    # sdl92.g:347:1: outputbody : outputstmt ( ',' outputstmt )* -> ^( OUTPUT_BODY ( outputstmt )+ ) ;
    def outputbody(self, ):

        retval = self.outputbody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal205 = None
        outputstmt204 = None

        outputstmt206 = None


        char_literal205_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_outputstmt = RewriteRuleSubtreeStream(self._adaptor, "rule outputstmt")
        try:
            try:
                # sdl92.g:348:9: ( outputstmt ( ',' outputstmt )* -> ^( OUTPUT_BODY ( outputstmt )+ ) )
                # sdl92.g:348:17: outputstmt ( ',' outputstmt )*
                pass 
                self._state.following.append(self.FOLLOW_outputstmt_in_outputbody5256)
                outputstmt204 = self.outputstmt()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_outputstmt.add(outputstmt204.tree)
                # sdl92.g:348:28: ( ',' outputstmt )*
                while True: #loop72
                    alt72 = 2
                    LA72_0 = self.input.LA(1)

                    if (LA72_0 == COMMA) :
                        alt72 = 1


                    if alt72 == 1:
                        # sdl92.g:348:29: ',' outputstmt
                        pass 
                        char_literal205=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_outputbody5259) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal205)
                        self._state.following.append(self.FOLLOW_outputstmt_in_outputbody5261)
                        outputstmt206 = self.outputstmt()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_outputstmt.add(outputstmt206.tree)


                    else:
                        break #loop72

                # AST Rewrite
                # elements: outputstmt
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 348:47: -> ^( OUTPUT_BODY ( outputstmt )+ )
                    # sdl92.g:348:50: ^( OUTPUT_BODY ( outputstmt )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OUTPUT_BODY, "OUTPUT_BODY"), root_1)

                    # sdl92.g:348:64: ( outputstmt )+
                    if not (stream_outputstmt.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_outputstmt.hasNext():
                        self._adaptor.addChild(root_1, stream_outputstmt.nextTree())


                    stream_outputstmt.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "outputbody"

    class outputstmt_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.outputstmt_return, self).__init__()

            self.tree = None




    # $ANTLR start "outputstmt"
    # sdl92.g:352:1: outputstmt : signal_id ( actual_parameters )? ;
    def outputstmt(self, ):

        retval = self.outputstmt_return()
        retval.start = self.input.LT(1)

        root_0 = None

        signal_id207 = None

        actual_parameters208 = None



        try:
            try:
                # sdl92.g:353:9: ( signal_id ( actual_parameters )? )
                # sdl92.g:353:17: signal_id ( actual_parameters )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_signal_id_in_outputstmt5313)
                signal_id207 = self.signal_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, signal_id207.tree)
                # sdl92.g:354:17: ( actual_parameters )?
                alt73 = 2
                LA73_0 = self.input.LA(1)

                if (LA73_0 == L_PAREN) :
                    alt73 = 1
                if alt73 == 1:
                    # sdl92.g:0:0: actual_parameters
                    pass 
                    self._state.following.append(self.FOLLOW_actual_parameters_in_outputstmt5332)
                    actual_parameters208 = self.actual_parameters()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, actual_parameters208.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "outputstmt"

    class viabody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.viabody_return, self).__init__()

            self.tree = None




    # $ANTLR start "viabody"
    # sdl92.g:363:1: viabody : ( 'ALL' -> ^( ALL ) | via_path -> ^( VIAPATH via_path ) );
    def viabody(self, ):

        retval = self.viabody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal209 = None
        via_path210 = None


        string_literal209_tree = None
        stream_167 = RewriteRuleTokenStream(self._adaptor, "token 167")
        stream_via_path = RewriteRuleSubtreeStream(self._adaptor, "rule via_path")
        try:
            try:
                # sdl92.g:363:9: ( 'ALL' -> ^( ALL ) | via_path -> ^( VIAPATH via_path ) )
                alt74 = 2
                LA74_0 = self.input.LA(1)

                if (LA74_0 == 167) :
                    alt74 = 1
                elif (LA74_0 == ID) :
                    alt74 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 74, 0, self.input)

                    raise nvae

                if alt74 == 1:
                    # sdl92.g:363:17: 'ALL'
                    pass 
                    string_literal209=self.match(self.input, 167, self.FOLLOW_167_in_viabody5370) 
                    if self._state.backtracking == 0:
                        stream_167.add(string_literal209)

                    # AST Rewrite
                    # elements: 
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 363:49: -> ^( ALL )
                        # sdl92.g:363:52: ^( ALL )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ALL, "ALL"), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt74 == 2:
                    # sdl92.g:364:19: via_path
                    pass 
                    self._state.following.append(self.FOLLOW_via_path_in_viabody5422)
                    via_path210 = self.via_path()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_via_path.add(via_path210.tree)

                    # AST Rewrite
                    # elements: via_path
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 364:49: -> ^( VIAPATH via_path )
                        # sdl92.g:364:52: ^( VIAPATH via_path )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VIAPATH, "VIAPATH"), root_1)

                        self._adaptor.addChild(root_1, stream_via_path.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "viabody"

    class destination_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.destination_return, self).__init__()

            self.tree = None




    # $ANTLR start "destination"
    # sdl92.g:366:1: destination : ( pid_expression | process_id | THIS );
    def destination(self, ):

        retval = self.destination_return()
        retval.start = self.input.LT(1)

        root_0 = None

        THIS213 = None
        pid_expression211 = None

        process_id212 = None


        THIS213_tree = None

        try:
            try:
                # sdl92.g:367:9: ( pid_expression | process_id | THIS )
                alt75 = 3
                LA75 = self.input.LA(1)
                if LA75 == P or LA75 == S or LA75 == O:
                    alt75 = 1
                elif LA75 == ID:
                    alt75 = 2
                elif LA75 == THIS:
                    alt75 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 75, 0, self.input)

                    raise nvae

                if alt75 == 1:
                    # sdl92.g:367:17: pid_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_pid_expression_in_destination5478)
                    pid_expression211 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression211.tree)


                elif alt75 == 2:
                    # sdl92.g:368:19: process_id
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_process_id_in_destination5499)
                    process_id212 = self.process_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, process_id212.tree)


                elif alt75 == 3:
                    # sdl92.g:369:19: THIS
                    pass 
                    root_0 = self._adaptor.nil()

                    THIS213=self.match(self.input, THIS, self.FOLLOW_THIS_in_destination5519)
                    if self._state.backtracking == 0:

                        THIS213_tree = self._adaptor.createWithPayload(THIS213)
                        self._adaptor.addChild(root_0, THIS213_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "destination"

    class via_path_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_path_return, self).__init__()

            self.tree = None




    # $ANTLR start "via_path"
    # sdl92.g:371:1: via_path : via_path_element ( ',' via_path_element )* -> ( via_path_element )+ ;
    def via_path(self, ):

        retval = self.via_path_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal215 = None
        via_path_element214 = None

        via_path_element216 = None


        char_literal215_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_via_path_element = RewriteRuleSubtreeStream(self._adaptor, "rule via_path_element")
        try:
            try:
                # sdl92.g:372:9: ( via_path_element ( ',' via_path_element )* -> ( via_path_element )+ )
                # sdl92.g:372:17: via_path_element ( ',' via_path_element )*
                pass 
                self._state.following.append(self.FOLLOW_via_path_element_in_via_path5557)
                via_path_element214 = self.via_path_element()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_via_path_element.add(via_path_element214.tree)
                # sdl92.g:372:34: ( ',' via_path_element )*
                while True: #loop76
                    alt76 = 2
                    LA76_0 = self.input.LA(1)

                    if (LA76_0 == COMMA) :
                        alt76 = 1


                    if alt76 == 1:
                        # sdl92.g:372:35: ',' via_path_element
                        pass 
                        char_literal215=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_via_path5560) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal215)
                        self._state.following.append(self.FOLLOW_via_path_element_in_via_path5562)
                        via_path_element216 = self.via_path_element()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_via_path_element.add(via_path_element216.tree)


                    else:
                        break #loop76

                # AST Rewrite
                # elements: via_path_element
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 372:65: -> ( via_path_element )+
                    # sdl92.g:372:68: ( via_path_element )+
                    if not (stream_via_path_element.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_via_path_element.hasNext():
                        self._adaptor.addChild(root_0, stream_via_path_element.nextTree())


                    stream_via_path_element.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via_path"

    class via_path_element_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.via_path_element_return, self).__init__()

            self.tree = None




    # $ANTLR start "via_path_element"
    # sdl92.g:374:1: via_path_element : ID ;
    def via_path_element(self, ):

        retval = self.via_path_element_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID217 = None

        ID217_tree = None

        try:
            try:
                # sdl92.g:375:9: ( ID )
                # sdl92.g:375:17: ID
                pass 
                root_0 = self._adaptor.nil()

                ID217=self.match(self.input, ID, self.FOLLOW_ID_in_via_path_element5606)
                if self._state.backtracking == 0:

                    ID217_tree = self._adaptor.createWithPayload(ID217)
                    self._adaptor.addChild(root_0, ID217_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "via_path_element"

    class actual_parameters_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.actual_parameters_return, self).__init__()

            self.tree = None




    # $ANTLR start "actual_parameters"
    # sdl92.g:377:1: actual_parameters : '(' expression ( ',' expression )* ')' -> ^( PARAMS ( expression )+ ) ;
    def actual_parameters(self, ):

        retval = self.actual_parameters_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal218 = None
        char_literal220 = None
        char_literal222 = None
        expression219 = None

        expression221 = None


        char_literal218_tree = None
        char_literal220_tree = None
        char_literal222_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:378:9: ( '(' expression ( ',' expression )* ')' -> ^( PARAMS ( expression )+ ) )
                # sdl92.g:378:16: '(' expression ( ',' expression )* ')'
                pass 
                char_literal218=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_actual_parameters5636) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(char_literal218)
                self._state.following.append(self.FOLLOW_expression_in_actual_parameters5638)
                expression219 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression219.tree)
                # sdl92.g:378:31: ( ',' expression )*
                while True: #loop77
                    alt77 = 2
                    LA77_0 = self.input.LA(1)

                    if (LA77_0 == COMMA) :
                        alt77 = 1


                    if alt77 == 1:
                        # sdl92.g:378:32: ',' expression
                        pass 
                        char_literal220=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_actual_parameters5641) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal220)
                        self._state.following.append(self.FOLLOW_expression_in_actual_parameters5643)
                        expression221 = self.expression()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_expression.add(expression221.tree)


                    else:
                        break #loop77
                char_literal222=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_actual_parameters5647) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(char_literal222)

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 378:64: -> ^( PARAMS ( expression )+ )
                    # sdl92.g:378:67: ^( PARAMS ( expression )+ )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                    # sdl92.g:378:76: ( expression )+
                    if not (stream_expression.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset()

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "actual_parameters"

    class task_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.task_return, self).__init__()

            self.tree = None




    # $ANTLR start "task"
    # sdl92.g:380:1: task : ( cif )? ( hyperlink )? TASK task_body end -> ^( TASK ( cif )? ( hyperlink )? ( end )? task_body ) ;
    def task(self, ):

        retval = self.task_return()
        retval.start = self.input.LT(1)

        root_0 = None

        TASK225 = None
        cif223 = None

        hyperlink224 = None

        task_body226 = None

        end227 = None


        TASK225_tree = None
        stream_TASK = RewriteRuleTokenStream(self._adaptor, "token TASK")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_task_body = RewriteRuleSubtreeStream(self._adaptor, "rule task_body")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:381:9: ( ( cif )? ( hyperlink )? TASK task_body end -> ^( TASK ( cif )? ( hyperlink )? ( end )? task_body ) )
                # sdl92.g:381:17: ( cif )? ( hyperlink )? TASK task_body end
                pass 
                # sdl92.g:381:17: ( cif )?
                alt78 = 2
                LA78_0 = self.input.LA(1)

                if (LA78_0 == 176) :
                    LA78_1 = self.input.LA(2)

                    if (LA78_1 == LABEL or LA78_1 == COMMENT or LA78_1 == STATE or LA78_1 == PROVIDED or LA78_1 == INPUT or LA78_1 == DECISION or LA78_1 == ANSWER or LA78_1 == OUTPUT or (TEXT <= LA78_1 <= JOIN) or LA78_1 == TASK or LA78_1 == START or LA78_1 == PROCEDURE) :
                        alt78 = 1
                if alt78 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_task5701)
                    cif223 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif223.tree)



                # sdl92.g:382:17: ( hyperlink )?
                alt79 = 2
                LA79_0 = self.input.LA(1)

                if (LA79_0 == 176) :
                    alt79 = 1
                if alt79 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_task5720)
                    hyperlink224 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink224.tree)



                TASK225=self.match(self.input, TASK, self.FOLLOW_TASK_in_task5739) 
                if self._state.backtracking == 0:
                    stream_TASK.add(TASK225)
                self._state.following.append(self.FOLLOW_task_body_in_task5741)
                task_body226 = self.task_body()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_task_body.add(task_body226.tree)
                self._state.following.append(self.FOLLOW_end_in_task5743)
                end227 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end227.tree)

                # AST Rewrite
                # elements: cif, task_body, TASK, hyperlink, end
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 383:52: -> ^( TASK ( cif )? ( hyperlink )? ( end )? task_body )
                    # sdl92.g:383:55: ^( TASK ( cif )? ( hyperlink )? ( end )? task_body )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_TASK.nextNode(), root_1)

                    # sdl92.g:383:62: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:383:67: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:383:78: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_task_body.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "task"

    class task_body_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.task_body_return, self).__init__()

            self.tree = None




    # $ANTLR start "task_body"
    # sdl92.g:385:1: task_body : ( ( assignement_statement ( ',' assignement_statement )* ) -> ^( TASK_BODY ( assignement_statement )+ ) | ( informal_text ( ',' informal_text )* ) -> ^( TASK_BODY ( informal_text )+ ) );
    def task_body(self, ):

        retval = self.task_body_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal229 = None
        char_literal232 = None
        assignement_statement228 = None

        assignement_statement230 = None

        informal_text231 = None

        informal_text233 = None


        char_literal229_tree = None
        char_literal232_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_informal_text = RewriteRuleSubtreeStream(self._adaptor, "rule informal_text")
        stream_assignement_statement = RewriteRuleSubtreeStream(self._adaptor, "rule assignement_statement")
        try:
            try:
                # sdl92.g:386:9: ( ( assignement_statement ( ',' assignement_statement )* ) -> ^( TASK_BODY ( assignement_statement )+ ) | ( informal_text ( ',' informal_text )* ) -> ^( TASK_BODY ( informal_text )+ ) )
                alt82 = 2
                LA82_0 = self.input.LA(1)

                if (LA82_0 == ID) :
                    alt82 = 1
                elif (LA82_0 == StringLiteral) :
                    alt82 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 82, 0, self.input)

                    raise nvae

                if alt82 == 1:
                    # sdl92.g:386:17: ( assignement_statement ( ',' assignement_statement )* )
                    pass 
                    # sdl92.g:386:17: ( assignement_statement ( ',' assignement_statement )* )
                    # sdl92.g:386:18: assignement_statement ( ',' assignement_statement )*
                    pass 
                    self._state.following.append(self.FOLLOW_assignement_statement_in_task_body5806)
                    assignement_statement228 = self.assignement_statement()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_assignement_statement.add(assignement_statement228.tree)
                    # sdl92.g:386:40: ( ',' assignement_statement )*
                    while True: #loop80
                        alt80 = 2
                        LA80_0 = self.input.LA(1)

                        if (LA80_0 == COMMA) :
                            alt80 = 1


                        if alt80 == 1:
                            # sdl92.g:386:41: ',' assignement_statement
                            pass 
                            char_literal229=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_task_body5809) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal229)
                            self._state.following.append(self.FOLLOW_assignement_statement_in_task_body5811)
                            assignement_statement230 = self.assignement_statement()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_assignement_statement.add(assignement_statement230.tree)


                        else:
                            break #loop80




                    # AST Rewrite
                    # elements: assignement_statement
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 386:73: -> ^( TASK_BODY ( assignement_statement )+ )
                        # sdl92.g:386:76: ^( TASK_BODY ( assignement_statement )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TASK_BODY, "TASK_BODY"), root_1)

                        # sdl92.g:386:88: ( assignement_statement )+
                        if not (stream_assignement_statement.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_assignement_statement.hasNext():
                            self._adaptor.addChild(root_1, stream_assignement_statement.nextTree())


                        stream_assignement_statement.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt82 == 2:
                    # sdl92.g:387:19: ( informal_text ( ',' informal_text )* )
                    pass 
                    # sdl92.g:387:19: ( informal_text ( ',' informal_text )* )
                    # sdl92.g:387:20: informal_text ( ',' informal_text )*
                    pass 
                    self._state.following.append(self.FOLLOW_informal_text_in_task_body5847)
                    informal_text231 = self.informal_text()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_informal_text.add(informal_text231.tree)
                    # sdl92.g:387:34: ( ',' informal_text )*
                    while True: #loop81
                        alt81 = 2
                        LA81_0 = self.input.LA(1)

                        if (LA81_0 == COMMA) :
                            alt81 = 1


                        if alt81 == 1:
                            # sdl92.g:387:35: ',' informal_text
                            pass 
                            char_literal232=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_task_body5850) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(char_literal232)
                            self._state.following.append(self.FOLLOW_informal_text_in_task_body5852)
                            informal_text233 = self.informal_text()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_informal_text.add(informal_text233.tree)


                        else:
                            break #loop81




                    # AST Rewrite
                    # elements: informal_text
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 387:73: -> ^( TASK_BODY ( informal_text )+ )
                        # sdl92.g:387:76: ^( TASK_BODY ( informal_text )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TASK_BODY, "TASK_BODY"), root_1)

                        # sdl92.g:387:88: ( informal_text )+
                        if not (stream_informal_text.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_informal_text.hasNext():
                            self._adaptor.addChild(root_1, stream_informal_text.nextTree())


                        stream_informal_text.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "task_body"

    class assignement_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.assignement_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "assignement_statement"
    # sdl92.g:389:1: assignement_statement : variable ':=' expression -> ^( ASSIGN variable expression ) ;
    def assignement_statement(self, ):

        retval = self.assignement_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal235 = None
        variable234 = None

        expression236 = None


        string_literal235_tree = None
        stream_ASSIG_OP = RewriteRuleTokenStream(self._adaptor, "token ASSIG_OP")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_variable = RewriteRuleSubtreeStream(self._adaptor, "rule variable")
        try:
            try:
                # sdl92.g:390:9: ( variable ':=' expression -> ^( ASSIGN variable expression ) )
                # sdl92.g:390:17: variable ':=' expression
                pass 
                self._state.following.append(self.FOLLOW_variable_in_assignement_statement5911)
                variable234 = self.variable()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable.add(variable234.tree)
                string_literal235=self.match(self.input, ASSIG_OP, self.FOLLOW_ASSIG_OP_in_assignement_statement5913) 
                if self._state.backtracking == 0:
                    stream_ASSIG_OP.add(string_literal235)
                self._state.following.append(self.FOLLOW_expression_in_assignement_statement5915)
                expression236 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression236.tree)

                # AST Rewrite
                # elements: expression, variable
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 390:61: -> ^( ASSIGN variable expression )
                    # sdl92.g:390:64: ^( ASSIGN variable expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(ASSIGN, "ASSIGN"), root_1)

                    self._adaptor.addChild(root_1, stream_variable.nextTree())
                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "assignement_statement"

    class variable_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable"
    # sdl92.g:405:1: variable : variable_id ( primary_params )* -> ^( VARIABLE variable_id ( primary_params )* ) ;
    def variable(self, ):

        retval = self.variable_return()
        retval.start = self.input.LT(1)

        root_0 = None

        variable_id237 = None

        primary_params238 = None


        stream_variable_id = RewriteRuleSubtreeStream(self._adaptor, "rule variable_id")
        stream_primary_params = RewriteRuleSubtreeStream(self._adaptor, "rule primary_params")
        try:
            try:
                # sdl92.g:406:9: ( variable_id ( primary_params )* -> ^( VARIABLE variable_id ( primary_params )* ) )
                # sdl92.g:406:17: variable_id ( primary_params )*
                pass 
                self._state.following.append(self.FOLLOW_variable_id_in_variable5970)
                variable_id237 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_variable_id.add(variable_id237.tree)
                # sdl92.g:406:29: ( primary_params )*
                while True: #loop83
                    alt83 = 2
                    LA83_0 = self.input.LA(1)

                    if (LA83_0 == L_PAREN or LA83_0 == 168) :
                        alt83 = 1


                    if alt83 == 1:
                        # sdl92.g:0:0: primary_params
                        pass 
                        self._state.following.append(self.FOLLOW_primary_params_in_variable5972)
                        primary_params238 = self.primary_params()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_primary_params.add(primary_params238.tree)


                    else:
                        break #loop83

                # AST Rewrite
                # elements: variable_id, primary_params
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 406:53: -> ^( VARIABLE variable_id ( primary_params )* )
                    # sdl92.g:406:56: ^( VARIABLE variable_id ( primary_params )* )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(VARIABLE, "VARIABLE"), root_1)

                    self._adaptor.addChild(root_1, stream_variable_id.nextTree())
                    # sdl92.g:406:79: ( primary_params )*
                    while stream_primary_params.hasNext():
                        self._adaptor.addChild(root_1, stream_primary_params.nextTree())


                    stream_primary_params.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable"

    class field_selection_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_selection_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_selection"
    # sdl92.g:410:1: field_selection : ( '!' field_name ) ;
    def field_selection(self, ):

        retval = self.field_selection_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal239 = None
        field_name240 = None


        char_literal239_tree = None

        try:
            try:
                # sdl92.g:411:9: ( ( '!' field_name ) )
                # sdl92.g:411:17: ( '!' field_name )
                pass 
                root_0 = self._adaptor.nil()

                # sdl92.g:411:17: ( '!' field_name )
                # sdl92.g:411:18: '!' field_name
                pass 
                char_literal239=self.match(self.input, 168, self.FOLLOW_168_in_field_selection6052)
                if self._state.backtracking == 0:

                    char_literal239_tree = self._adaptor.createWithPayload(char_literal239)
                    self._adaptor.addChild(root_0, char_literal239_tree)

                self._state.following.append(self.FOLLOW_field_name_in_field_selection6054)
                field_name240 = self.field_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, field_name240.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_selection"

    class expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "expression"
    # sdl92.g:416:1: expression : operand0 ( IMPLIES operand0 )* ;
    def expression(self, ):

        retval = self.expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IMPLIES242 = None
        operand0241 = None

        operand0243 = None


        IMPLIES242_tree = None

        try:
            try:
                # sdl92.g:416:17: ( operand0 ( IMPLIES operand0 )* )
                # sdl92.g:416:25: operand0 ( IMPLIES operand0 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand0_in_expression6093)
                operand0241 = self.operand0()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand0241.tree)
                # sdl92.g:416:34: ( IMPLIES operand0 )*
                while True: #loop84
                    alt84 = 2
                    LA84_0 = self.input.LA(1)

                    if (LA84_0 == IMPLIES) :
                        LA84_2 = self.input.LA(2)

                        if (self.synpred99_sdl92()) :
                            alt84 = 1




                    if alt84 == 1:
                        # sdl92.g:416:36: IMPLIES operand0
                        pass 
                        IMPLIES242=self.match(self.input, IMPLIES, self.FOLLOW_IMPLIES_in_expression6097)
                        if self._state.backtracking == 0:

                            IMPLIES242_tree = self._adaptor.createWithPayload(IMPLIES242)
                            root_0 = self._adaptor.becomeRoot(IMPLIES242_tree, root_0)

                        self._state.following.append(self.FOLLOW_operand0_in_expression6100)
                        operand0243 = self.operand0()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand0243.tree)


                    else:
                        break #loop84



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "expression"

    class operand0_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand0_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand0"
    # sdl92.g:417:1: operand0 : operand1 ( ( OR | XOR ) operand1 )* ;
    def operand0(self, ):

        retval = self.operand0_return()
        retval.start = self.input.LT(1)

        root_0 = None

        OR245 = None
        XOR246 = None
        operand1244 = None

        operand1247 = None


        OR245_tree = None
        XOR246_tree = None

        try:
            try:
                # sdl92.g:417:17: ( operand1 ( ( OR | XOR ) operand1 )* )
                # sdl92.g:417:25: operand1 ( ( OR | XOR ) operand1 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand1_in_operand06123)
                operand1244 = self.operand1()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand1244.tree)
                # sdl92.g:417:34: ( ( OR | XOR ) operand1 )*
                while True: #loop86
                    alt86 = 2
                    LA86_0 = self.input.LA(1)

                    if (LA86_0 == OR) :
                        LA86_2 = self.input.LA(2)

                        if (self.synpred101_sdl92()) :
                            alt86 = 1


                    elif (LA86_0 == XOR) :
                        LA86_3 = self.input.LA(2)

                        if (self.synpred101_sdl92()) :
                            alt86 = 1




                    if alt86 == 1:
                        # sdl92.g:417:35: ( OR | XOR ) operand1
                        pass 
                        # sdl92.g:417:35: ( OR | XOR )
                        alt85 = 2
                        LA85_0 = self.input.LA(1)

                        if (LA85_0 == OR) :
                            alt85 = 1
                        elif (LA85_0 == XOR) :
                            alt85 = 2
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 85, 0, self.input)

                            raise nvae

                        if alt85 == 1:
                            # sdl92.g:417:37: OR
                            pass 
                            OR245=self.match(self.input, OR, self.FOLLOW_OR_in_operand06128)
                            if self._state.backtracking == 0:

                                OR245_tree = self._adaptor.createWithPayload(OR245)
                                root_0 = self._adaptor.becomeRoot(OR245_tree, root_0)



                        elif alt85 == 2:
                            # sdl92.g:417:43: XOR
                            pass 
                            XOR246=self.match(self.input, XOR, self.FOLLOW_XOR_in_operand06133)
                            if self._state.backtracking == 0:

                                XOR246_tree = self._adaptor.createWithPayload(XOR246)
                                root_0 = self._adaptor.becomeRoot(XOR246_tree, root_0)




                        self._state.following.append(self.FOLLOW_operand1_in_operand06138)
                        operand1247 = self.operand1()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand1247.tree)


                    else:
                        break #loop86



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand0"

    class operand1_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand1_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand1"
    # sdl92.g:418:1: operand1 : operand2 ( AND operand2 )* ;
    def operand1(self, ):

        retval = self.operand1_return()
        retval.start = self.input.LT(1)

        root_0 = None

        AND249 = None
        operand2248 = None

        operand2250 = None


        AND249_tree = None

        try:
            try:
                # sdl92.g:418:17: ( operand2 ( AND operand2 )* )
                # sdl92.g:418:25: operand2 ( AND operand2 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand2_in_operand16160)
                operand2248 = self.operand2()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand2248.tree)
                # sdl92.g:418:34: ( AND operand2 )*
                while True: #loop87
                    alt87 = 2
                    LA87_0 = self.input.LA(1)

                    if (LA87_0 == AND) :
                        LA87_2 = self.input.LA(2)

                        if (self.synpred102_sdl92()) :
                            alt87 = 1




                    if alt87 == 1:
                        # sdl92.g:418:36: AND operand2
                        pass 
                        AND249=self.match(self.input, AND, self.FOLLOW_AND_in_operand16164)
                        if self._state.backtracking == 0:

                            AND249_tree = self._adaptor.createWithPayload(AND249)
                            root_0 = self._adaptor.becomeRoot(AND249_tree, root_0)

                        self._state.following.append(self.FOLLOW_operand2_in_operand16167)
                        operand2250 = self.operand2()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand2250.tree)


                    else:
                        break #loop87



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand1"

    class operand2_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand2_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand2"
    # sdl92.g:419:1: operand2 : operand3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3 )* ;
    def operand2(self, ):

        retval = self.operand2_return()
        retval.start = self.input.LT(1)

        root_0 = None

        EQ252 = None
        NEQ253 = None
        GT254 = None
        GE255 = None
        LT256 = None
        LE257 = None
        IN258 = None
        operand3251 = None

        operand3259 = None


        EQ252_tree = None
        NEQ253_tree = None
        GT254_tree = None
        GE255_tree = None
        LT256_tree = None
        LE257_tree = None
        IN258_tree = None

        try:
            try:
                # sdl92.g:419:17: ( operand3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3 )* )
                # sdl92.g:419:25: operand3 ( ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand3_in_operand26189)
                operand3251 = self.operand3()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand3251.tree)
                # sdl92.g:419:34: ( ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3 )*
                while True: #loop89
                    alt89 = 2
                    alt89 = self.dfa89.predict(self.input)
                    if alt89 == 1:
                        # sdl92.g:419:35: ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3
                        pass 
                        # sdl92.g:419:35: ( EQ | NEQ | GT | GE | LT | LE | IN )
                        alt88 = 7
                        LA88 = self.input.LA(1)
                        if LA88 == EQ:
                            alt88 = 1
                        elif LA88 == NEQ:
                            alt88 = 2
                        elif LA88 == GT:
                            alt88 = 3
                        elif LA88 == GE:
                            alt88 = 4
                        elif LA88 == LT:
                            alt88 = 5
                        elif LA88 == LE:
                            alt88 = 6
                        elif LA88 == IN:
                            alt88 = 7
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 88, 0, self.input)

                            raise nvae

                        if alt88 == 1:
                            # sdl92.g:419:37: EQ
                            pass 
                            EQ252=self.match(self.input, EQ, self.FOLLOW_EQ_in_operand26194)
                            if self._state.backtracking == 0:

                                EQ252_tree = self._adaptor.createWithPayload(EQ252)
                                root_0 = self._adaptor.becomeRoot(EQ252_tree, root_0)



                        elif alt88 == 2:
                            # sdl92.g:419:43: NEQ
                            pass 
                            NEQ253=self.match(self.input, NEQ, self.FOLLOW_NEQ_in_operand26199)
                            if self._state.backtracking == 0:

                                NEQ253_tree = self._adaptor.createWithPayload(NEQ253)
                                root_0 = self._adaptor.becomeRoot(NEQ253_tree, root_0)



                        elif alt88 == 3:
                            # sdl92.g:419:50: GT
                            pass 
                            GT254=self.match(self.input, GT, self.FOLLOW_GT_in_operand26204)
                            if self._state.backtracking == 0:

                                GT254_tree = self._adaptor.createWithPayload(GT254)
                                root_0 = self._adaptor.becomeRoot(GT254_tree, root_0)



                        elif alt88 == 4:
                            # sdl92.g:419:56: GE
                            pass 
                            GE255=self.match(self.input, GE, self.FOLLOW_GE_in_operand26209)
                            if self._state.backtracking == 0:

                                GE255_tree = self._adaptor.createWithPayload(GE255)
                                root_0 = self._adaptor.becomeRoot(GE255_tree, root_0)



                        elif alt88 == 5:
                            # sdl92.g:419:62: LT
                            pass 
                            LT256=self.match(self.input, LT, self.FOLLOW_LT_in_operand26214)
                            if self._state.backtracking == 0:

                                LT256_tree = self._adaptor.createWithPayload(LT256)
                                root_0 = self._adaptor.becomeRoot(LT256_tree, root_0)



                        elif alt88 == 6:
                            # sdl92.g:419:68: LE
                            pass 
                            LE257=self.match(self.input, LE, self.FOLLOW_LE_in_operand26219)
                            if self._state.backtracking == 0:

                                LE257_tree = self._adaptor.createWithPayload(LE257)
                                root_0 = self._adaptor.becomeRoot(LE257_tree, root_0)



                        elif alt88 == 7:
                            # sdl92.g:419:74: IN
                            pass 
                            IN258=self.match(self.input, IN, self.FOLLOW_IN_in_operand26224)
                            if self._state.backtracking == 0:

                                IN258_tree = self._adaptor.createWithPayload(IN258)
                                root_0 = self._adaptor.becomeRoot(IN258_tree, root_0)




                        self._state.following.append(self.FOLLOW_operand3_in_operand26229)
                        operand3259 = self.operand3()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand3259.tree)


                    else:
                        break #loop89



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand2"

    class operand3_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand3_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand3"
    # sdl92.g:420:1: operand3 : operand4 ( ( PLUS | DASH | APPEND ) operand4 )* ;
    def operand3(self, ):

        retval = self.operand3_return()
        retval.start = self.input.LT(1)

        root_0 = None

        PLUS261 = None
        DASH262 = None
        APPEND263 = None
        operand4260 = None

        operand4264 = None


        PLUS261_tree = None
        DASH262_tree = None
        APPEND263_tree = None

        try:
            try:
                # sdl92.g:420:17: ( operand4 ( ( PLUS | DASH | APPEND ) operand4 )* )
                # sdl92.g:420:25: operand4 ( ( PLUS | DASH | APPEND ) operand4 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand4_in_operand36251)
                operand4260 = self.operand4()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand4260.tree)
                # sdl92.g:420:34: ( ( PLUS | DASH | APPEND ) operand4 )*
                while True: #loop91
                    alt91 = 2
                    LA91 = self.input.LA(1)
                    if LA91 == PLUS:
                        LA91_2 = self.input.LA(2)

                        if (self.synpred112_sdl92()) :
                            alt91 = 1


                    elif LA91 == DASH:
                        LA91_3 = self.input.LA(2)

                        if (self.synpred112_sdl92()) :
                            alt91 = 1


                    elif LA91 == APPEND:
                        LA91_4 = self.input.LA(2)

                        if (self.synpred112_sdl92()) :
                            alt91 = 1



                    if alt91 == 1:
                        # sdl92.g:420:35: ( PLUS | DASH | APPEND ) operand4
                        pass 
                        # sdl92.g:420:35: ( PLUS | DASH | APPEND )
                        alt90 = 3
                        LA90 = self.input.LA(1)
                        if LA90 == PLUS:
                            alt90 = 1
                        elif LA90 == DASH:
                            alt90 = 2
                        elif LA90 == APPEND:
                            alt90 = 3
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 90, 0, self.input)

                            raise nvae

                        if alt90 == 1:
                            # sdl92.g:420:37: PLUS
                            pass 
                            PLUS261=self.match(self.input, PLUS, self.FOLLOW_PLUS_in_operand36256)
                            if self._state.backtracking == 0:

                                PLUS261_tree = self._adaptor.createWithPayload(PLUS261)
                                root_0 = self._adaptor.becomeRoot(PLUS261_tree, root_0)



                        elif alt90 == 2:
                            # sdl92.g:420:45: DASH
                            pass 
                            DASH262=self.match(self.input, DASH, self.FOLLOW_DASH_in_operand36261)
                            if self._state.backtracking == 0:

                                DASH262_tree = self._adaptor.createWithPayload(DASH262)
                                root_0 = self._adaptor.becomeRoot(DASH262_tree, root_0)



                        elif alt90 == 3:
                            # sdl92.g:420:53: APPEND
                            pass 
                            APPEND263=self.match(self.input, APPEND, self.FOLLOW_APPEND_in_operand36266)
                            if self._state.backtracking == 0:

                                APPEND263_tree = self._adaptor.createWithPayload(APPEND263)
                                root_0 = self._adaptor.becomeRoot(APPEND263_tree, root_0)




                        self._state.following.append(self.FOLLOW_operand4_in_operand36271)
                        operand4264 = self.operand4()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand4264.tree)


                    else:
                        break #loop91



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand3"

    class operand4_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand4_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand4"
    # sdl92.g:421:1: operand4 : operand5 ( ( ASTERISK | DIV | MOD | REM ) operand5 )* ;
    def operand4(self, ):

        retval = self.operand4_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ASTERISK266 = None
        DIV267 = None
        MOD268 = None
        REM269 = None
        operand5265 = None

        operand5270 = None


        ASTERISK266_tree = None
        DIV267_tree = None
        MOD268_tree = None
        REM269_tree = None

        try:
            try:
                # sdl92.g:421:17: ( operand5 ( ( ASTERISK | DIV | MOD | REM ) operand5 )* )
                # sdl92.g:421:25: operand5 ( ( ASTERISK | DIV | MOD | REM ) operand5 )*
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operand5_in_operand46293)
                operand5265 = self.operand5()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operand5265.tree)
                # sdl92.g:421:34: ( ( ASTERISK | DIV | MOD | REM ) operand5 )*
                while True: #loop93
                    alt93 = 2
                    LA93 = self.input.LA(1)
                    if LA93 == ASTERISK:
                        LA93_2 = self.input.LA(2)

                        if (self.synpred116_sdl92()) :
                            alt93 = 1


                    elif LA93 == DIV:
                        LA93_3 = self.input.LA(2)

                        if (self.synpred116_sdl92()) :
                            alt93 = 1


                    elif LA93 == MOD:
                        LA93_4 = self.input.LA(2)

                        if (self.synpred116_sdl92()) :
                            alt93 = 1


                    elif LA93 == REM:
                        LA93_5 = self.input.LA(2)

                        if (self.synpred116_sdl92()) :
                            alt93 = 1



                    if alt93 == 1:
                        # sdl92.g:421:35: ( ASTERISK | DIV | MOD | REM ) operand5
                        pass 
                        # sdl92.g:421:35: ( ASTERISK | DIV | MOD | REM )
                        alt92 = 4
                        LA92 = self.input.LA(1)
                        if LA92 == ASTERISK:
                            alt92 = 1
                        elif LA92 == DIV:
                            alt92 = 2
                        elif LA92 == MOD:
                            alt92 = 3
                        elif LA92 == REM:
                            alt92 = 4
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 92, 0, self.input)

                            raise nvae

                        if alt92 == 1:
                            # sdl92.g:421:37: ASTERISK
                            pass 
                            ASTERISK266=self.match(self.input, ASTERISK, self.FOLLOW_ASTERISK_in_operand46298)
                            if self._state.backtracking == 0:

                                ASTERISK266_tree = self._adaptor.createWithPayload(ASTERISK266)
                                root_0 = self._adaptor.becomeRoot(ASTERISK266_tree, root_0)



                        elif alt92 == 2:
                            # sdl92.g:421:49: DIV
                            pass 
                            DIV267=self.match(self.input, DIV, self.FOLLOW_DIV_in_operand46303)
                            if self._state.backtracking == 0:

                                DIV267_tree = self._adaptor.createWithPayload(DIV267)
                                root_0 = self._adaptor.becomeRoot(DIV267_tree, root_0)



                        elif alt92 == 3:
                            # sdl92.g:421:56: MOD
                            pass 
                            MOD268=self.match(self.input, MOD, self.FOLLOW_MOD_in_operand46308)
                            if self._state.backtracking == 0:

                                MOD268_tree = self._adaptor.createWithPayload(MOD268)
                                root_0 = self._adaptor.becomeRoot(MOD268_tree, root_0)



                        elif alt92 == 4:
                            # sdl92.g:421:63: REM
                            pass 
                            REM269=self.match(self.input, REM, self.FOLLOW_REM_in_operand46313)
                            if self._state.backtracking == 0:

                                REM269_tree = self._adaptor.createWithPayload(REM269)
                                root_0 = self._adaptor.becomeRoot(REM269_tree, root_0)




                        self._state.following.append(self.FOLLOW_operand5_in_operand46318)
                        operand5270 = self.operand5()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            self._adaptor.addChild(root_0, operand5270.tree)


                    else:
                        break #loop93



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand4"

    class operand5_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operand5_return, self).__init__()

            self.tree = None




    # $ANTLR start "operand5"
    # sdl92.g:422:1: operand5 : ( primary_qualifier )? primary -> ^( PRIMARY ( primary_qualifier )? primary ) ;
    def operand5(self, ):

        retval = self.operand5_return()
        retval.start = self.input.LT(1)

        root_0 = None

        primary_qualifier271 = None

        primary272 = None


        stream_primary_qualifier = RewriteRuleSubtreeStream(self._adaptor, "rule primary_qualifier")
        stream_primary = RewriteRuleSubtreeStream(self._adaptor, "rule primary")
        try:
            try:
                # sdl92.g:422:17: ( ( primary_qualifier )? primary -> ^( PRIMARY ( primary_qualifier )? primary ) )
                # sdl92.g:422:25: ( primary_qualifier )? primary
                pass 
                # sdl92.g:422:25: ( primary_qualifier )?
                alt94 = 2
                LA94_0 = self.input.LA(1)

                if (LA94_0 == DASH or LA94_0 == NOT) :
                    alt94 = 1
                if alt94 == 1:
                    # sdl92.g:0:0: primary_qualifier
                    pass 
                    self._state.following.append(self.FOLLOW_primary_qualifier_in_operand56340)
                    primary_qualifier271 = self.primary_qualifier()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_primary_qualifier.add(primary_qualifier271.tree)



                self._state.following.append(self.FOLLOW_primary_in_operand56343)
                primary272 = self.primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_primary.add(primary272.tree)

                # AST Rewrite
                # elements: primary, primary_qualifier
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 422:57: -> ^( PRIMARY ( primary_qualifier )? primary )
                    # sdl92.g:422:60: ^( PRIMARY ( primary_qualifier )? primary )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PRIMARY, "PRIMARY"), root_1)

                    # sdl92.g:422:70: ( primary_qualifier )?
                    if stream_primary_qualifier.hasNext():
                        self._adaptor.addChild(root_1, stream_primary_qualifier.nextTree())


                    stream_primary_qualifier.reset();
                    self._adaptor.addChild(root_1, stream_primary.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operand5"

    class primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary"
    # sdl92.g:425:1: primary : (a= asn1Value ( primary_params )* -> ^( PRIMARY_ID asn1Value ( primary_params )* ) | L_PAREN expression R_PAREN -> ^( EXPRESSION expression ) | conditional_ground_expression );
    def primary(self, ):

        retval = self.primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        L_PAREN274 = None
        R_PAREN276 = None
        a = None

        primary_params273 = None

        expression275 = None

        conditional_ground_expression277 = None


        L_PAREN274_tree = None
        R_PAREN276_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        stream_primary_params = RewriteRuleSubtreeStream(self._adaptor, "rule primary_params")
        stream_asn1Value = RewriteRuleSubtreeStream(self._adaptor, "rule asn1Value")
        try:
            try:
                # sdl92.g:426:9: (a= asn1Value ( primary_params )* -> ^( PRIMARY_ID asn1Value ( primary_params )* ) | L_PAREN expression R_PAREN -> ^( EXPRESSION expression ) | conditional_ground_expression )
                alt96 = 3
                LA96 = self.input.LA(1)
                if LA96 == INT or LA96 == ID or LA96 == BitStringLiteral or LA96 == OctetStringLiteral or LA96 == TRUE or LA96 == FALSE or LA96 == StringLiteral or LA96 == NULL or LA96 == PLUS_INFINITY or LA96 == MINUS_INFINITY or LA96 == FloatingPointLiteral or LA96 == L_BRACKET:
                    alt96 = 1
                elif LA96 == L_PAREN:
                    alt96 = 2
                elif LA96 == IF:
                    alt96 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 96, 0, self.input)

                    raise nvae

                if alt96 == 1:
                    # sdl92.g:426:17: a= asn1Value ( primary_params )*
                    pass 
                    self._state.following.append(self.FOLLOW_asn1Value_in_primary6386)
                    a = self.asn1Value()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_asn1Value.add(a.tree)
                    # sdl92.g:426:29: ( primary_params )*
                    while True: #loop95
                        alt95 = 2
                        LA95_0 = self.input.LA(1)

                        if (LA95_0 == L_PAREN) :
                            LA95_2 = self.input.LA(2)

                            if (self.synpred118_sdl92()) :
                                alt95 = 1


                        elif (LA95_0 == 168) :
                            LA95_3 = self.input.LA(2)

                            if (self.synpred118_sdl92()) :
                                alt95 = 1




                        if alt95 == 1:
                            # sdl92.g:0:0: primary_params
                            pass 
                            self._state.following.append(self.FOLLOW_primary_params_in_primary6388)
                            primary_params273 = self.primary_params()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_primary_params.add(primary_params273.tree)


                        else:
                            break #loop95

                    # AST Rewrite
                    # elements: asn1Value, primary_params
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 426:61: -> ^( PRIMARY_ID asn1Value ( primary_params )* )
                        # sdl92.g:426:64: ^( PRIMARY_ID asn1Value ( primary_params )* )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PRIMARY_ID, "PRIMARY_ID"), root_1)

                        self._adaptor.addChild(root_1, stream_asn1Value.nextTree())
                        # sdl92.g:426:87: ( primary_params )*
                        while stream_primary_params.hasNext():
                            self._adaptor.addChild(root_1, stream_primary_params.nextTree())


                        stream_primary_params.reset();

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt96 == 2:
                    # sdl92.g:427:19: L_PAREN expression R_PAREN
                    pass 
                    L_PAREN274=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_primary6436) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(L_PAREN274)
                    self._state.following.append(self.FOLLOW_expression_in_primary6438)
                    expression275 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression275.tree)
                    R_PAREN276=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_primary6440) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(R_PAREN276)

                    # AST Rewrite
                    # elements: expression
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 427:61: -> ^( EXPRESSION expression )
                        # sdl92.g:427:64: ^( EXPRESSION expression )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(EXPRESSION, "EXPRESSION"), root_1)

                        self._adaptor.addChild(root_1, stream_expression.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt96 == 3:
                    # sdl92.g:428:19: conditional_ground_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_conditional_ground_expression_in_primary6498)
                    conditional_ground_expression277 = self.conditional_ground_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, conditional_ground_expression277.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary"

    class asn1Value_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.asn1Value_return, self).__init__()

            self.tree = None




    # $ANTLR start "asn1Value"
    # sdl92.g:431:1: asn1Value : ( BitStringLiteral -> ^( BITSTR BitStringLiteral ) | OctetStringLiteral -> ^( OCTSTR OctetStringLiteral ) | TRUE | FALSE | StringLiteral -> ^( STRING StringLiteral ) | NULL | PLUS_INFINITY | MINUS_INFINITY | ID | INT | FloatingPointLiteral -> ^( FLOAT FloatingPointLiteral ) | L_BRACKET R_BRACKET -> ^( EMPTYSTR ) | L_BRACKET MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT R_BRACKET -> ^( FLOAT2 $mant $bas $exp) | choiceValue | L_BRACKET namedValue ( COMMA namedValue )* R_BRACKET -> ^( SEQUENCE ( namedValue )+ ) | L_BRACKET asn1Value ( COMMA asn1Value )* R_BRACKET -> ^( SEQOF ( ^( SEQOF asn1Value ) )+ ) );
    def asn1Value(self, ):

        retval = self.asn1Value_return()
        retval.start = self.input.LT(1)

        root_0 = None

        mant = None
        bas = None
        exp = None
        BitStringLiteral278 = None
        OctetStringLiteral279 = None
        TRUE280 = None
        FALSE281 = None
        StringLiteral282 = None
        NULL283 = None
        PLUS_INFINITY284 = None
        MINUS_INFINITY285 = None
        ID286 = None
        INT287 = None
        FloatingPointLiteral288 = None
        L_BRACKET289 = None
        R_BRACKET290 = None
        L_BRACKET291 = None
        MANTISSA292 = None
        COMMA293 = None
        BASE294 = None
        COMMA295 = None
        EXPONENT296 = None
        R_BRACKET297 = None
        L_BRACKET299 = None
        COMMA301 = None
        R_BRACKET303 = None
        L_BRACKET304 = None
        COMMA306 = None
        R_BRACKET308 = None
        choiceValue298 = None

        namedValue300 = None

        namedValue302 = None

        asn1Value305 = None

        asn1Value307 = None


        mant_tree = None
        bas_tree = None
        exp_tree = None
        BitStringLiteral278_tree = None
        OctetStringLiteral279_tree = None
        TRUE280_tree = None
        FALSE281_tree = None
        StringLiteral282_tree = None
        NULL283_tree = None
        PLUS_INFINITY284_tree = None
        MINUS_INFINITY285_tree = None
        ID286_tree = None
        INT287_tree = None
        FloatingPointLiteral288_tree = None
        L_BRACKET289_tree = None
        R_BRACKET290_tree = None
        L_BRACKET291_tree = None
        MANTISSA292_tree = None
        COMMA293_tree = None
        BASE294_tree = None
        COMMA295_tree = None
        EXPONENT296_tree = None
        R_BRACKET297_tree = None
        L_BRACKET299_tree = None
        COMMA301_tree = None
        R_BRACKET303_tree = None
        L_BRACKET304_tree = None
        COMMA306_tree = None
        R_BRACKET308_tree = None
        stream_StringLiteral = RewriteRuleTokenStream(self._adaptor, "token StringLiteral")
        stream_OctetStringLiteral = RewriteRuleTokenStream(self._adaptor, "token OctetStringLiteral")
        stream_BASE = RewriteRuleTokenStream(self._adaptor, "token BASE")
        stream_MANTISSA = RewriteRuleTokenStream(self._adaptor, "token MANTISSA")
        stream_EXPONENT = RewriteRuleTokenStream(self._adaptor, "token EXPONENT")
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_L_BRACKET = RewriteRuleTokenStream(self._adaptor, "token L_BRACKET")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_BRACKET = RewriteRuleTokenStream(self._adaptor, "token R_BRACKET")
        stream_FloatingPointLiteral = RewriteRuleTokenStream(self._adaptor, "token FloatingPointLiteral")
        stream_BitStringLiteral = RewriteRuleTokenStream(self._adaptor, "token BitStringLiteral")
        stream_namedValue = RewriteRuleSubtreeStream(self._adaptor, "rule namedValue")
        stream_asn1Value = RewriteRuleSubtreeStream(self._adaptor, "rule asn1Value")
        try:
            try:
                # sdl92.g:432:9: ( BitStringLiteral -> ^( BITSTR BitStringLiteral ) | OctetStringLiteral -> ^( OCTSTR OctetStringLiteral ) | TRUE | FALSE | StringLiteral -> ^( STRING StringLiteral ) | NULL | PLUS_INFINITY | MINUS_INFINITY | ID | INT | FloatingPointLiteral -> ^( FLOAT FloatingPointLiteral ) | L_BRACKET R_BRACKET -> ^( EMPTYSTR ) | L_BRACKET MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT R_BRACKET -> ^( FLOAT2 $mant $bas $exp) | choiceValue | L_BRACKET namedValue ( COMMA namedValue )* R_BRACKET -> ^( SEQUENCE ( namedValue )+ ) | L_BRACKET asn1Value ( COMMA asn1Value )* R_BRACKET -> ^( SEQOF ( ^( SEQOF asn1Value ) )+ ) )
                alt99 = 16
                alt99 = self.dfa99.predict(self.input)
                if alt99 == 1:
                    # sdl92.g:432:17: BitStringLiteral
                    pass 
                    BitStringLiteral278=self.match(self.input, BitStringLiteral, self.FOLLOW_BitStringLiteral_in_asn1Value6521) 
                    if self._state.backtracking == 0:
                        stream_BitStringLiteral.add(BitStringLiteral278)

                    # AST Rewrite
                    # elements: BitStringLiteral
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 432:45: -> ^( BITSTR BitStringLiteral )
                        # sdl92.g:432:48: ^( BITSTR BitStringLiteral )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(BITSTR, "BITSTR"), root_1)

                        self._adaptor.addChild(root_1, stream_BitStringLiteral.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 2:
                    # sdl92.g:433:17: OctetStringLiteral
                    pass 
                    OctetStringLiteral279=self.match(self.input, OctetStringLiteral, self.FOLLOW_OctetStringLiteral_in_asn1Value6558) 
                    if self._state.backtracking == 0:
                        stream_OctetStringLiteral.add(OctetStringLiteral279)

                    # AST Rewrite
                    # elements: OctetStringLiteral
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 433:45: -> ^( OCTSTR OctetStringLiteral )
                        # sdl92.g:433:48: ^( OCTSTR OctetStringLiteral )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(OCTSTR, "OCTSTR"), root_1)

                        self._adaptor.addChild(root_1, stream_OctetStringLiteral.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 3:
                    # sdl92.g:434:17: TRUE
                    pass 
                    root_0 = self._adaptor.nil()

                    TRUE280=self.match(self.input, TRUE, self.FOLLOW_TRUE_in_asn1Value6593)
                    if self._state.backtracking == 0:

                        TRUE280_tree = self._adaptor.createWithPayload(TRUE280)
                        root_0 = self._adaptor.becomeRoot(TRUE280_tree, root_0)



                elif alt99 == 4:
                    # sdl92.g:435:17: FALSE
                    pass 
                    root_0 = self._adaptor.nil()

                    FALSE281=self.match(self.input, FALSE, self.FOLLOW_FALSE_in_asn1Value6612)
                    if self._state.backtracking == 0:

                        FALSE281_tree = self._adaptor.createWithPayload(FALSE281)
                        root_0 = self._adaptor.becomeRoot(FALSE281_tree, root_0)



                elif alt99 == 5:
                    # sdl92.g:436:17: StringLiteral
                    pass 
                    StringLiteral282=self.match(self.input, StringLiteral, self.FOLLOW_StringLiteral_in_asn1Value6631) 
                    if self._state.backtracking == 0:
                        stream_StringLiteral.add(StringLiteral282)

                    # AST Rewrite
                    # elements: StringLiteral
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 436:45: -> ^( STRING StringLiteral )
                        # sdl92.g:436:48: ^( STRING StringLiteral )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(STRING, "STRING"), root_1)

                        self._adaptor.addChild(root_1, stream_StringLiteral.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 6:
                    # sdl92.g:437:17: NULL
                    pass 
                    root_0 = self._adaptor.nil()

                    NULL283=self.match(self.input, NULL, self.FOLLOW_NULL_in_asn1Value6671)
                    if self._state.backtracking == 0:

                        NULL283_tree = self._adaptor.createWithPayload(NULL283)
                        root_0 = self._adaptor.becomeRoot(NULL283_tree, root_0)



                elif alt99 == 7:
                    # sdl92.g:438:17: PLUS_INFINITY
                    pass 
                    root_0 = self._adaptor.nil()

                    PLUS_INFINITY284=self.match(self.input, PLUS_INFINITY, self.FOLLOW_PLUS_INFINITY_in_asn1Value6690)
                    if self._state.backtracking == 0:

                        PLUS_INFINITY284_tree = self._adaptor.createWithPayload(PLUS_INFINITY284)
                        root_0 = self._adaptor.becomeRoot(PLUS_INFINITY284_tree, root_0)



                elif alt99 == 8:
                    # sdl92.g:439:17: MINUS_INFINITY
                    pass 
                    root_0 = self._adaptor.nil()

                    MINUS_INFINITY285=self.match(self.input, MINUS_INFINITY, self.FOLLOW_MINUS_INFINITY_in_asn1Value6709)
                    if self._state.backtracking == 0:

                        MINUS_INFINITY285_tree = self._adaptor.createWithPayload(MINUS_INFINITY285)
                        root_0 = self._adaptor.becomeRoot(MINUS_INFINITY285_tree, root_0)



                elif alt99 == 9:
                    # sdl92.g:440:17: ID
                    pass 
                    root_0 = self._adaptor.nil()

                    ID286=self.match(self.input, ID, self.FOLLOW_ID_in_asn1Value6728)
                    if self._state.backtracking == 0:

                        ID286_tree = self._adaptor.createWithPayload(ID286)
                        self._adaptor.addChild(root_0, ID286_tree)



                elif alt99 == 10:
                    # sdl92.g:441:17: INT
                    pass 
                    root_0 = self._adaptor.nil()

                    INT287=self.match(self.input, INT, self.FOLLOW_INT_in_asn1Value6746)
                    if self._state.backtracking == 0:

                        INT287_tree = self._adaptor.createWithPayload(INT287)
                        self._adaptor.addChild(root_0, INT287_tree)



                elif alt99 == 11:
                    # sdl92.g:442:17: FloatingPointLiteral
                    pass 
                    FloatingPointLiteral288=self.match(self.input, FloatingPointLiteral, self.FOLLOW_FloatingPointLiteral_in_asn1Value6764) 
                    if self._state.backtracking == 0:
                        stream_FloatingPointLiteral.add(FloatingPointLiteral288)

                    # AST Rewrite
                    # elements: FloatingPointLiteral
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 442:45: -> ^( FLOAT FloatingPointLiteral )
                        # sdl92.g:442:48: ^( FLOAT FloatingPointLiteral )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FLOAT, "FLOAT"), root_1)

                        self._adaptor.addChild(root_1, stream_FloatingPointLiteral.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 12:
                    # sdl92.g:443:17: L_BRACKET R_BRACKET
                    pass 
                    L_BRACKET289=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_asn1Value6797) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(L_BRACKET289)
                    R_BRACKET290=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_asn1Value6799) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(R_BRACKET290)

                    # AST Rewrite
                    # elements: 
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 443:45: -> ^( EMPTYSTR )
                        # sdl92.g:443:48: ^( EMPTYSTR )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(EMPTYSTR, "EMPTYSTR"), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 13:
                    # sdl92.g:444:17: L_BRACKET MANTISSA mant= INT COMMA BASE bas= INT COMMA EXPONENT exp= INT R_BRACKET
                    pass 
                    L_BRACKET291=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_asn1Value6831) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(L_BRACKET291)
                    MANTISSA292=self.match(self.input, MANTISSA, self.FOLLOW_MANTISSA_in_asn1Value6850) 
                    if self._state.backtracking == 0:
                        stream_MANTISSA.add(MANTISSA292)
                    mant=self.match(self.input, INT, self.FOLLOW_INT_in_asn1Value6854) 
                    if self._state.backtracking == 0:
                        stream_INT.add(mant)
                    COMMA293=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_asn1Value6856) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA293)
                    BASE294=self.match(self.input, BASE, self.FOLLOW_BASE_in_asn1Value6875) 
                    if self._state.backtracking == 0:
                        stream_BASE.add(BASE294)
                    bas=self.match(self.input, INT, self.FOLLOW_INT_in_asn1Value6879) 
                    if self._state.backtracking == 0:
                        stream_INT.add(bas)
                    COMMA295=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_asn1Value6881) 
                    if self._state.backtracking == 0:
                        stream_COMMA.add(COMMA295)
                    EXPONENT296=self.match(self.input, EXPONENT, self.FOLLOW_EXPONENT_in_asn1Value6900) 
                    if self._state.backtracking == 0:
                        stream_EXPONENT.add(EXPONENT296)
                    exp=self.match(self.input, INT, self.FOLLOW_INT_in_asn1Value6904) 
                    if self._state.backtracking == 0:
                        stream_INT.add(exp)
                    R_BRACKET297=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_asn1Value6923) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(R_BRACKET297)

                    # AST Rewrite
                    # elements: mant, exp, bas
                    # token labels: exp, mant, bas
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0
                        stream_exp = RewriteRuleTokenStream(self._adaptor, "token exp", exp)
                        stream_mant = RewriteRuleTokenStream(self._adaptor, "token mant", mant)
                        stream_bas = RewriteRuleTokenStream(self._adaptor, "token bas", bas)

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 448:45: -> ^( FLOAT2 $mant $bas $exp)
                        # sdl92.g:448:48: ^( FLOAT2 $mant $bas $exp)
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FLOAT2, "FLOAT2"), root_1)

                        self._adaptor.addChild(root_1, stream_mant.nextNode())
                        self._adaptor.addChild(root_1, stream_bas.nextNode())
                        self._adaptor.addChild(root_1, stream_exp.nextNode())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 14:
                    # sdl92.g:449:17: choiceValue
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_choiceValue_in_asn1Value6974)
                    choiceValue298 = self.choiceValue()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, choiceValue298.tree)


                elif alt99 == 15:
                    # sdl92.g:450:17: L_BRACKET namedValue ( COMMA namedValue )* R_BRACKET
                    pass 
                    L_BRACKET299=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_asn1Value6992) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(L_BRACKET299)
                    self._state.following.append(self.FOLLOW_namedValue_in_asn1Value7010)
                    namedValue300 = self.namedValue()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_namedValue.add(namedValue300.tree)
                    # sdl92.g:451:28: ( COMMA namedValue )*
                    while True: #loop97
                        alt97 = 2
                        LA97_0 = self.input.LA(1)

                        if (LA97_0 == COMMA) :
                            alt97 = 1


                        if alt97 == 1:
                            # sdl92.g:451:29: COMMA namedValue
                            pass 
                            COMMA301=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_asn1Value7013) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(COMMA301)
                            self._state.following.append(self.FOLLOW_namedValue_in_asn1Value7015)
                            namedValue302 = self.namedValue()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_namedValue.add(namedValue302.tree)


                        else:
                            break #loop97
                    R_BRACKET303=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_asn1Value7035) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(R_BRACKET303)

                    # AST Rewrite
                    # elements: namedValue
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 452:45: -> ^( SEQUENCE ( namedValue )+ )
                        # sdl92.g:452:48: ^( SEQUENCE ( namedValue )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SEQUENCE, "SEQUENCE"), root_1)

                        # sdl92.g:452:59: ( namedValue )+
                        if not (stream_namedValue.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_namedValue.hasNext():
                            self._adaptor.addChild(root_1, stream_namedValue.nextTree())


                        stream_namedValue.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt99 == 16:
                    # sdl92.g:453:17: L_BRACKET asn1Value ( COMMA asn1Value )* R_BRACKET
                    pass 
                    L_BRACKET304=self.match(self.input, L_BRACKET, self.FOLLOW_L_BRACKET_in_asn1Value7080) 
                    if self._state.backtracking == 0:
                        stream_L_BRACKET.add(L_BRACKET304)
                    self._state.following.append(self.FOLLOW_asn1Value_in_asn1Value7099)
                    asn1Value305 = self.asn1Value()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_asn1Value.add(asn1Value305.tree)
                    # sdl92.g:454:27: ( COMMA asn1Value )*
                    while True: #loop98
                        alt98 = 2
                        LA98_0 = self.input.LA(1)

                        if (LA98_0 == COMMA) :
                            alt98 = 1


                        if alt98 == 1:
                            # sdl92.g:454:28: COMMA asn1Value
                            pass 
                            COMMA306=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_asn1Value7102) 
                            if self._state.backtracking == 0:
                                stream_COMMA.add(COMMA306)
                            self._state.following.append(self.FOLLOW_asn1Value_in_asn1Value7104)
                            asn1Value307 = self.asn1Value()

                            self._state.following.pop()
                            if self._state.backtracking == 0:
                                stream_asn1Value.add(asn1Value307.tree)


                        else:
                            break #loop98
                    R_BRACKET308=self.match(self.input, R_BRACKET, self.FOLLOW_R_BRACKET_in_asn1Value7125) 
                    if self._state.backtracking == 0:
                        stream_R_BRACKET.add(R_BRACKET308)

                    # AST Rewrite
                    # elements: asn1Value
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 455:45: -> ^( SEQOF ( ^( SEQOF asn1Value ) )+ )
                        # sdl92.g:455:48: ^( SEQOF ( ^( SEQOF asn1Value ) )+ )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SEQOF, "SEQOF"), root_1)

                        # sdl92.g:455:56: ( ^( SEQOF asn1Value ) )+
                        if not (stream_asn1Value.hasNext()):
                            raise RewriteEarlyExitException()

                        while stream_asn1Value.hasNext():
                            # sdl92.g:455:56: ^( SEQOF asn1Value )
                            root_2 = self._adaptor.nil()
                            root_2 = self._adaptor.becomeRoot(self._adaptor.createFromType(SEQOF, "SEQOF"), root_2)

                            self._adaptor.addChild(root_2, stream_asn1Value.nextTree())

                            self._adaptor.addChild(root_1, root_2)


                        stream_asn1Value.reset()

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "asn1Value"

    class informal_text_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.informal_text_return, self).__init__()

            self.tree = None




    # $ANTLR start "informal_text"
    # sdl92.g:467:1: informal_text : StringLiteral -> ^( INFORMAL_TEXT StringLiteral ) ;
    def informal_text(self, ):

        retval = self.informal_text_return()
        retval.start = self.input.LT(1)

        root_0 = None

        StringLiteral309 = None

        StringLiteral309_tree = None
        stream_StringLiteral = RewriteRuleTokenStream(self._adaptor, "token StringLiteral")

        try:
            try:
                # sdl92.g:467:14: ( StringLiteral -> ^( INFORMAL_TEXT StringLiteral ) )
                # sdl92.g:467:17: StringLiteral
                pass 
                StringLiteral309=self.match(self.input, StringLiteral, self.FOLLOW_StringLiteral_in_informal_text7265) 
                if self._state.backtracking == 0:
                    stream_StringLiteral.add(StringLiteral309)

                # AST Rewrite
                # elements: StringLiteral
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 467:41: -> ^( INFORMAL_TEXT StringLiteral )
                    # sdl92.g:467:44: ^( INFORMAL_TEXT StringLiteral )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(INFORMAL_TEXT, "INFORMAL_TEXT"), root_1)

                    self._adaptor.addChild(root_1, stream_StringLiteral.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "informal_text"

    class choiceValue_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.choiceValue_return, self).__init__()

            self.tree = None




    # $ANTLR start "choiceValue"
    # sdl92.g:470:1: choiceValue : choice= ID ':' expression -> ^( CHOICE $choice expression ) ;
    def choiceValue(self, ):

        retval = self.choiceValue_return()
        retval.start = self.input.LT(1)

        root_0 = None

        choice = None
        char_literal310 = None
        expression311 = None


        choice_tree = None
        char_literal310_tree = None
        stream_ID = RewriteRuleTokenStream(self._adaptor, "token ID")
        stream_166 = RewriteRuleTokenStream(self._adaptor, "token 166")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:471:9: (choice= ID ':' expression -> ^( CHOICE $choice expression ) )
                # sdl92.g:471:11: choice= ID ':' expression
                pass 
                choice=self.match(self.input, ID, self.FOLLOW_ID_in_choiceValue7307) 
                if self._state.backtracking == 0:
                    stream_ID.add(choice)
                char_literal310=self.match(self.input, 166, self.FOLLOW_166_in_choiceValue7309) 
                if self._state.backtracking == 0:
                    stream_166.add(char_literal310)
                self._state.following.append(self.FOLLOW_expression_in_choiceValue7311)
                expression311 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression311.tree)

                # AST Rewrite
                # elements: choice, expression
                # token labels: choice
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_choice = RewriteRuleTokenStream(self._adaptor, "token choice", choice)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 471:42: -> ^( CHOICE $choice expression )
                    # sdl92.g:471:45: ^( CHOICE $choice expression )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CHOICE, "CHOICE"), root_1)

                    self._adaptor.addChild(root_1, stream_choice.nextNode())
                    self._adaptor.addChild(root_1, stream_expression.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "choiceValue"

    class namedValue_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.namedValue_return, self).__init__()

            self.tree = None




    # $ANTLR start "namedValue"
    # sdl92.g:475:1: namedValue : ID expression ;
    def namedValue(self, ):

        retval = self.namedValue_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID312 = None
        expression313 = None


        ID312_tree = None

        try:
            try:
                # sdl92.g:476:9: ( ID expression )
                # sdl92.g:476:11: ID expression
                pass 
                root_0 = self._adaptor.nil()

                ID312=self.match(self.input, ID, self.FOLLOW_ID_in_namedValue7350)
                if self._state.backtracking == 0:

                    ID312_tree = self._adaptor.createWithPayload(ID312)
                    self._adaptor.addChild(root_0, ID312_tree)

                self._state.following.append(self.FOLLOW_expression_in_namedValue7352)
                expression313 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression313.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "namedValue"

    class primary_qualifier_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_qualifier_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary_qualifier"
    # sdl92.g:480:1: primary_qualifier : ( DASH -> ^( MINUS ) | NOT );
    def primary_qualifier(self, ):

        retval = self.primary_qualifier_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DASH314 = None
        NOT315 = None

        DASH314_tree = None
        NOT315_tree = None
        stream_DASH = RewriteRuleTokenStream(self._adaptor, "token DASH")

        try:
            try:
                # sdl92.g:481:9: ( DASH -> ^( MINUS ) | NOT )
                alt100 = 2
                LA100_0 = self.input.LA(1)

                if (LA100_0 == DASH) :
                    alt100 = 1
                elif (LA100_0 == NOT) :
                    alt100 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 100, 0, self.input)

                    raise nvae

                if alt100 == 1:
                    # sdl92.g:481:17: DASH
                    pass 
                    DASH314=self.match(self.input, DASH, self.FOLLOW_DASH_in_primary_qualifier7378) 
                    if self._state.backtracking == 0:
                        stream_DASH.add(DASH314)

                    # AST Rewrite
                    # elements: 
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 481:33: -> ^( MINUS )
                        # sdl92.g:481:36: ^( MINUS )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(MINUS, "MINUS"), root_1)

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt100 == 2:
                    # sdl92.g:482:19: NOT
                    pass 
                    root_0 = self._adaptor.nil()

                    NOT315=self.match(self.input, NOT, self.FOLLOW_NOT_in_primary_qualifier7416)
                    if self._state.backtracking == 0:

                        NOT315_tree = self._adaptor.createWithPayload(NOT315)
                        self._adaptor.addChild(root_0, NOT315_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary_qualifier"

    class primary_params_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.primary_params_return, self).__init__()

            self.tree = None




    # $ANTLR start "primary_params"
    # sdl92.g:484:1: primary_params : ( '(' expression_list ')' -> ^( PARAMS expression_list ) | '!' literal_id -> ^( FIELD_NAME literal_id ) );
    def primary_params(self, ):

        retval = self.primary_params_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal316 = None
        char_literal318 = None
        char_literal319 = None
        expression_list317 = None

        literal_id320 = None


        char_literal316_tree = None
        char_literal318_tree = None
        char_literal319_tree = None
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_168 = RewriteRuleTokenStream(self._adaptor, "token 168")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_expression_list = RewriteRuleSubtreeStream(self._adaptor, "rule expression_list")
        stream_literal_id = RewriteRuleSubtreeStream(self._adaptor, "rule literal_id")
        try:
            try:
                # sdl92.g:485:9: ( '(' expression_list ')' -> ^( PARAMS expression_list ) | '!' literal_id -> ^( FIELD_NAME literal_id ) )
                alt101 = 2
                LA101_0 = self.input.LA(1)

                if (LA101_0 == L_PAREN) :
                    alt101 = 1
                elif (LA101_0 == 168) :
                    alt101 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 101, 0, self.input)

                    raise nvae

                if alt101 == 1:
                    # sdl92.g:485:16: '(' expression_list ')'
                    pass 
                    char_literal316=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_primary_params7437) 
                    if self._state.backtracking == 0:
                        stream_L_PAREN.add(char_literal316)
                    self._state.following.append(self.FOLLOW_expression_list_in_primary_params7439)
                    expression_list317 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression_list.add(expression_list317.tree)
                    char_literal318=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_primary_params7441) 
                    if self._state.backtracking == 0:
                        stream_R_PAREN.add(char_literal318)

                    # AST Rewrite
                    # elements: expression_list
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 485:47: -> ^( PARAMS expression_list )
                        # sdl92.g:485:50: ^( PARAMS expression_list )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(PARAMS, "PARAMS"), root_1)

                        self._adaptor.addChild(root_1, stream_expression_list.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                elif alt101 == 2:
                    # sdl92.g:486:18: '!' literal_id
                    pass 
                    char_literal319=self.match(self.input, 168, self.FOLLOW_168_in_primary_params7475) 
                    if self._state.backtracking == 0:
                        stream_168.add(char_literal319)
                    self._state.following.append(self.FOLLOW_literal_id_in_primary_params7477)
                    literal_id320 = self.literal_id()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_literal_id.add(literal_id320.tree)

                    # AST Rewrite
                    # elements: literal_id
                    # token labels: 
                    # rule labels: retval
                    # token list labels: 
                    # rule list labels: 
                    # wildcard labels: 
                    if self._state.backtracking == 0:

                        retval.tree = root_0

                        if retval is not None:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                        else:
                            stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                        root_0 = self._adaptor.nil()
                        # 486:47: -> ^( FIELD_NAME literal_id )
                        # sdl92.g:486:50: ^( FIELD_NAME literal_id )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(FIELD_NAME, "FIELD_NAME"), root_1)

                        self._adaptor.addChild(root_1, stream_literal_id.nextTree())

                        self._adaptor.addChild(root_0, root_1)



                        retval.tree = root_0


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "primary_params"

    class indexed_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.indexed_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "indexed_primary"
    # sdl92.g:497:1: indexed_primary : primary '(' expression_list ')' ;
    def indexed_primary(self, ):

        retval = self.indexed_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal322 = None
        char_literal324 = None
        primary321 = None

        expression_list323 = None


        char_literal322_tree = None
        char_literal324_tree = None

        try:
            try:
                # sdl92.g:498:9: ( primary '(' expression_list ')' )
                # sdl92.g:498:17: primary '(' expression_list ')'
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_primary_in_indexed_primary7524)
                primary321 = self.primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, primary321.tree)
                char_literal322=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_indexed_primary7526)
                if self._state.backtracking == 0:

                    char_literal322_tree = self._adaptor.createWithPayload(char_literal322)
                    self._adaptor.addChild(root_0, char_literal322_tree)

                self._state.following.append(self.FOLLOW_expression_list_in_indexed_primary7528)
                expression_list323 = self.expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression_list323.tree)
                char_literal324=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_indexed_primary7530)
                if self._state.backtracking == 0:

                    char_literal324_tree = self._adaptor.createWithPayload(char_literal324)
                    self._adaptor.addChild(root_0, char_literal324_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "indexed_primary"

    class field_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_primary"
    # sdl92.g:500:1: field_primary : primary field_selection ;
    def field_primary(self, ):

        retval = self.field_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        primary325 = None

        field_selection326 = None



        try:
            try:
                # sdl92.g:501:9: ( primary field_selection )
                # sdl92.g:501:17: primary field_selection
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_primary_in_field_primary7560)
                primary325 = self.primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, primary325.tree)
                self._state.following.append(self.FOLLOW_field_selection_in_field_primary7562)
                field_selection326 = self.field_selection()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, field_selection326.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_primary"

    class structure_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.structure_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "structure_primary"
    # sdl92.g:503:1: structure_primary : '(.' expression_list '.)' ;
    def structure_primary(self, ):

        retval = self.structure_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal327 = None
        string_literal329 = None
        expression_list328 = None


        string_literal327_tree = None
        string_literal329_tree = None

        try:
            try:
                # sdl92.g:504:9: ( '(.' expression_list '.)' )
                # sdl92.g:504:17: '(.' expression_list '.)'
                pass 
                root_0 = self._adaptor.nil()

                string_literal327=self.match(self.input, 169, self.FOLLOW_169_in_structure_primary7592)
                if self._state.backtracking == 0:

                    string_literal327_tree = self._adaptor.createWithPayload(string_literal327)
                    self._adaptor.addChild(root_0, string_literal327_tree)

                self._state.following.append(self.FOLLOW_expression_list_in_structure_primary7594)
                expression_list328 = self.expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression_list328.tree)
                string_literal329=self.match(self.input, 170, self.FOLLOW_170_in_structure_primary7596)
                if self._state.backtracking == 0:

                    string_literal329_tree = self._adaptor.createWithPayload(string_literal329)
                    self._adaptor.addChild(root_0, string_literal329_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "structure_primary"

    class active_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_expression"
    # sdl92.g:506:1: active_expression : active_primary ;
    def active_expression(self, ):

        retval = self.active_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        active_primary330 = None



        try:
            try:
                # sdl92.g:507:9: ( active_primary )
                # sdl92.g:507:17: active_primary
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_active_primary_in_active_expression7627)
                active_primary330 = self.active_primary()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_primary330.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_expression"

    class active_primary_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_primary_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_primary"
    # sdl92.g:509:1: active_primary : ( variable_access | operator_application | conditional_expression | imperative_operator | '(' active_expression ')' | 'ERROR' );
    def active_primary(self, ):

        retval = self.active_primary_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal335 = None
        char_literal337 = None
        string_literal338 = None
        variable_access331 = None

        operator_application332 = None

        conditional_expression333 = None

        imperative_operator334 = None

        active_expression336 = None


        char_literal335_tree = None
        char_literal337_tree = None
        string_literal338_tree = None

        try:
            try:
                # sdl92.g:510:9: ( variable_access | operator_application | conditional_expression | imperative_operator | '(' active_expression ')' | 'ERROR' )
                alt102 = 6
                LA102 = self.input.LA(1)
                if LA102 == ID:
                    LA102_1 = self.input.LA(2)

                    if (LA102_1 == L_PAREN) :
                        alt102 = 2
                    elif ((R_PAREN <= LA102_1 <= COMMA)) :
                        alt102 = 1
                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 102, 1, self.input)

                        raise nvae

                elif LA102 == IF:
                    alt102 = 3
                elif LA102 == N or LA102 == P or LA102 == S or LA102 == O or LA102 == 172 or LA102 == 173 or LA102 == 174 or LA102 == 175:
                    alt102 = 4
                elif LA102 == L_PAREN:
                    alt102 = 5
                elif LA102 == 171:
                    alt102 = 6
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 102, 0, self.input)

                    raise nvae

                if alt102 == 1:
                    # sdl92.g:510:17: variable_access
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_variable_access_in_active_primary7657)
                    variable_access331 = self.variable_access()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, variable_access331.tree)


                elif alt102 == 2:
                    # sdl92.g:511:17: operator_application
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_operator_application_in_active_primary7693)
                    operator_application332 = self.operator_application()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, operator_application332.tree)


                elif alt102 == 3:
                    # sdl92.g:512:17: conditional_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_conditional_expression_in_active_primary7724)
                    conditional_expression333 = self.conditional_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, conditional_expression333.tree)


                elif alt102 == 4:
                    # sdl92.g:513:17: imperative_operator
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_imperative_operator_in_active_primary7753)
                    imperative_operator334 = self.imperative_operator()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, imperative_operator334.tree)


                elif alt102 == 5:
                    # sdl92.g:514:17: '(' active_expression ')'
                    pass 
                    root_0 = self._adaptor.nil()

                    char_literal335=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_active_primary7785)
                    if self._state.backtracking == 0:

                        char_literal335_tree = self._adaptor.createWithPayload(char_literal335)
                        self._adaptor.addChild(root_0, char_literal335_tree)

                    self._state.following.append(self.FOLLOW_active_expression_in_active_primary7787)
                    active_expression336 = self.active_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, active_expression336.tree)
                    char_literal337=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_active_primary7789)
                    if self._state.backtracking == 0:

                        char_literal337_tree = self._adaptor.createWithPayload(char_literal337)
                        self._adaptor.addChild(root_0, char_literal337_tree)



                elif alt102 == 6:
                    # sdl92.g:515:17: 'ERROR'
                    pass 
                    root_0 = self._adaptor.nil()

                    string_literal338=self.match(self.input, 171, self.FOLLOW_171_in_active_primary7815)
                    if self._state.backtracking == 0:

                        string_literal338_tree = self._adaptor.createWithPayload(string_literal338)
                        self._adaptor.addChild(root_0, string_literal338_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_primary"

    class imperative_operator_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.imperative_operator_return, self).__init__()

            self.tree = None




    # $ANTLR start "imperative_operator"
    # sdl92.g:518:1: imperative_operator : ( now_expression | import_expression | pid_expression | view_expression | timer_active_expression | anyvalue_expression );
    def imperative_operator(self, ):

        retval = self.imperative_operator_return()
        retval.start = self.input.LT(1)

        root_0 = None

        now_expression339 = None

        import_expression340 = None

        pid_expression341 = None

        view_expression342 = None

        timer_active_expression343 = None

        anyvalue_expression344 = None



        try:
            try:
                # sdl92.g:519:9: ( now_expression | import_expression | pid_expression | view_expression | timer_active_expression | anyvalue_expression )
                alt103 = 6
                LA103 = self.input.LA(1)
                if LA103 == N:
                    alt103 = 1
                elif LA103 == 174:
                    alt103 = 2
                elif LA103 == P or LA103 == S or LA103 == O:
                    alt103 = 3
                elif LA103 == 175:
                    alt103 = 4
                elif LA103 == 172:
                    alt103 = 5
                elif LA103 == 173:
                    alt103 = 6
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 103, 0, self.input)

                    raise nvae

                if alt103 == 1:
                    # sdl92.g:519:17: now_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_now_expression_in_imperative_operator7855)
                    now_expression339 = self.now_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, now_expression339.tree)


                elif alt103 == 2:
                    # sdl92.g:520:17: import_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_import_expression_in_imperative_operator7884)
                    import_expression340 = self.import_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, import_expression340.tree)


                elif alt103 == 3:
                    # sdl92.g:521:17: pid_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_pid_expression_in_imperative_operator7918)
                    pid_expression341 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression341.tree)


                elif alt103 == 4:
                    # sdl92.g:522:17: view_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_view_expression_in_imperative_operator7947)
                    view_expression342 = self.view_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, view_expression342.tree)


                elif alt103 == 5:
                    # sdl92.g:523:17: timer_active_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_timer_active_expression_in_imperative_operator7975)
                    timer_active_expression343 = self.timer_active_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, timer_active_expression343.tree)


                elif alt103 == 6:
                    # sdl92.g:524:17: anyvalue_expression
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_anyvalue_expression_in_imperative_operator8003)
                    anyvalue_expression344 = self.anyvalue_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, anyvalue_expression344.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "imperative_operator"

    class timer_active_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.timer_active_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "timer_active_expression"
    # sdl92.g:526:1: timer_active_expression : 'ACTIVE' '(' timer_id ( '(' expression_list ')' )? ')' ;
    def timer_active_expression(self, ):

        retval = self.timer_active_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal345 = None
        char_literal346 = None
        char_literal348 = None
        char_literal350 = None
        char_literal351 = None
        timer_id347 = None

        expression_list349 = None


        string_literal345_tree = None
        char_literal346_tree = None
        char_literal348_tree = None
        char_literal350_tree = None
        char_literal351_tree = None

        try:
            try:
                # sdl92.g:527:9: ( 'ACTIVE' '(' timer_id ( '(' expression_list ')' )? ')' )
                # sdl92.g:527:17: 'ACTIVE' '(' timer_id ( '(' expression_list ')' )? ')'
                pass 
                root_0 = self._adaptor.nil()

                string_literal345=self.match(self.input, 172, self.FOLLOW_172_in_timer_active_expression8025)
                if self._state.backtracking == 0:

                    string_literal345_tree = self._adaptor.createWithPayload(string_literal345)
                    self._adaptor.addChild(root_0, string_literal345_tree)

                char_literal346=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_timer_active_expression8027)
                if self._state.backtracking == 0:

                    char_literal346_tree = self._adaptor.createWithPayload(char_literal346)
                    self._adaptor.addChild(root_0, char_literal346_tree)

                self._state.following.append(self.FOLLOW_timer_id_in_timer_active_expression8029)
                timer_id347 = self.timer_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, timer_id347.tree)
                # sdl92.g:527:39: ( '(' expression_list ')' )?
                alt104 = 2
                LA104_0 = self.input.LA(1)

                if (LA104_0 == L_PAREN) :
                    alt104 = 1
                if alt104 == 1:
                    # sdl92.g:527:40: '(' expression_list ')'
                    pass 
                    char_literal348=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_timer_active_expression8032)
                    if self._state.backtracking == 0:

                        char_literal348_tree = self._adaptor.createWithPayload(char_literal348)
                        self._adaptor.addChild(root_0, char_literal348_tree)

                    self._state.following.append(self.FOLLOW_expression_list_in_timer_active_expression8034)
                    expression_list349 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression_list349.tree)
                    char_literal350=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_timer_active_expression8036)
                    if self._state.backtracking == 0:

                        char_literal350_tree = self._adaptor.createWithPayload(char_literal350)
                        self._adaptor.addChild(root_0, char_literal350_tree)




                char_literal351=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_timer_active_expression8040)
                if self._state.backtracking == 0:

                    char_literal351_tree = self._adaptor.createWithPayload(char_literal351)
                    self._adaptor.addChild(root_0, char_literal351_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "timer_active_expression"

    class anyvalue_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.anyvalue_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "anyvalue_expression"
    # sdl92.g:529:1: anyvalue_expression : 'ANY' '(' sort ')' ;
    def anyvalue_expression(self, ):

        retval = self.anyvalue_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal352 = None
        char_literal353 = None
        char_literal355 = None
        sort354 = None


        string_literal352_tree = None
        char_literal353_tree = None
        char_literal355_tree = None

        try:
            try:
                # sdl92.g:530:9: ( 'ANY' '(' sort ')' )
                # sdl92.g:530:17: 'ANY' '(' sort ')'
                pass 
                root_0 = self._adaptor.nil()

                string_literal352=self.match(self.input, 173, self.FOLLOW_173_in_anyvalue_expression8070)
                if self._state.backtracking == 0:

                    string_literal352_tree = self._adaptor.createWithPayload(string_literal352)
                    self._adaptor.addChild(root_0, string_literal352_tree)

                char_literal353=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_anyvalue_expression8072)
                if self._state.backtracking == 0:

                    char_literal353_tree = self._adaptor.createWithPayload(char_literal353)
                    self._adaptor.addChild(root_0, char_literal353_tree)

                self._state.following.append(self.FOLLOW_sort_in_anyvalue_expression8074)
                sort354 = self.sort()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, sort354.tree)
                char_literal355=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_anyvalue_expression8076)
                if self._state.backtracking == 0:

                    char_literal355_tree = self._adaptor.createWithPayload(char_literal355)
                    self._adaptor.addChild(root_0, char_literal355_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "anyvalue_expression"

    class sort_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.sort_return, self).__init__()

            self.tree = None




    # $ANTLR start "sort"
    # sdl92.g:532:1: sort : sort_id -> ^( SORT sort_id ) ;
    def sort(self, ):

        retval = self.sort_return()
        retval.start = self.input.LT(1)

        root_0 = None

        sort_id356 = None


        stream_sort_id = RewriteRuleSubtreeStream(self._adaptor, "rule sort_id")
        try:
            try:
                # sdl92.g:532:9: ( sort_id -> ^( SORT sort_id ) )
                # sdl92.g:532:17: sort_id
                pass 
                self._state.following.append(self.FOLLOW_sort_id_in_sort8101)
                sort_id356 = self.sort_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_sort_id.add(sort_id356.tree)

                # AST Rewrite
                # elements: sort_id
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 532:39: -> ^( SORT sort_id )
                    # sdl92.g:532:42: ^( SORT sort_id )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(SORT, "SORT"), root_1)

                    self._adaptor.addChild(root_1, stream_sort_id.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "sort"

    class syntype_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype"
    # sdl92.g:534:1: syntype : syntype_id ;
    def syntype(self, ):

        retval = self.syntype_return()
        retval.start = self.input.LT(1)

        root_0 = None

        syntype_id357 = None



        try:
            try:
                # sdl92.g:534:9: ( syntype_id )
                # sdl92.g:534:17: syntype_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_syntype_id_in_syntype8137)
                syntype_id357 = self.syntype_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, syntype_id357.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype"

    class import_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.import_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "import_expression"
    # sdl92.g:536:1: import_expression : 'IMPORT' '(' remote_variable_id ( ',' destination )? ')' ;
    def import_expression(self, ):

        retval = self.import_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal358 = None
        char_literal359 = None
        char_literal361 = None
        char_literal363 = None
        remote_variable_id360 = None

        destination362 = None


        string_literal358_tree = None
        char_literal359_tree = None
        char_literal361_tree = None
        char_literal363_tree = None

        try:
            try:
                # sdl92.g:537:9: ( 'IMPORT' '(' remote_variable_id ( ',' destination )? ')' )
                # sdl92.g:537:17: 'IMPORT' '(' remote_variable_id ( ',' destination )? ')'
                pass 
                root_0 = self._adaptor.nil()

                string_literal358=self.match(self.input, 174, self.FOLLOW_174_in_import_expression8159)
                if self._state.backtracking == 0:

                    string_literal358_tree = self._adaptor.createWithPayload(string_literal358)
                    self._adaptor.addChild(root_0, string_literal358_tree)

                char_literal359=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_import_expression8161)
                if self._state.backtracking == 0:

                    char_literal359_tree = self._adaptor.createWithPayload(char_literal359)
                    self._adaptor.addChild(root_0, char_literal359_tree)

                self._state.following.append(self.FOLLOW_remote_variable_id_in_import_expression8163)
                remote_variable_id360 = self.remote_variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, remote_variable_id360.tree)
                # sdl92.g:537:49: ( ',' destination )?
                alt105 = 2
                LA105_0 = self.input.LA(1)

                if (LA105_0 == COMMA) :
                    alt105 = 1
                if alt105 == 1:
                    # sdl92.g:537:50: ',' destination
                    pass 
                    char_literal361=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_import_expression8166)
                    if self._state.backtracking == 0:

                        char_literal361_tree = self._adaptor.createWithPayload(char_literal361)
                        self._adaptor.addChild(root_0, char_literal361_tree)

                    self._state.following.append(self.FOLLOW_destination_in_import_expression8168)
                    destination362 = self.destination()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, destination362.tree)



                char_literal363=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_import_expression8172)
                if self._state.backtracking == 0:

                    char_literal363_tree = self._adaptor.createWithPayload(char_literal363)
                    self._adaptor.addChild(root_0, char_literal363_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "import_expression"

    class view_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.view_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "view_expression"
    # sdl92.g:539:1: view_expression : 'VIEW' '(' view_id ( ',' pid_expression )? ')' ;
    def view_expression(self, ):

        retval = self.view_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal364 = None
        char_literal365 = None
        char_literal367 = None
        char_literal369 = None
        view_id366 = None

        pid_expression368 = None


        string_literal364_tree = None
        char_literal365_tree = None
        char_literal367_tree = None
        char_literal369_tree = None

        try:
            try:
                # sdl92.g:540:9: ( 'VIEW' '(' view_id ( ',' pid_expression )? ')' )
                # sdl92.g:540:17: 'VIEW' '(' view_id ( ',' pid_expression )? ')'
                pass 
                root_0 = self._adaptor.nil()

                string_literal364=self.match(self.input, 175, self.FOLLOW_175_in_view_expression8194)
                if self._state.backtracking == 0:

                    string_literal364_tree = self._adaptor.createWithPayload(string_literal364)
                    self._adaptor.addChild(root_0, string_literal364_tree)

                char_literal365=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_view_expression8196)
                if self._state.backtracking == 0:

                    char_literal365_tree = self._adaptor.createWithPayload(char_literal365)
                    self._adaptor.addChild(root_0, char_literal365_tree)

                self._state.following.append(self.FOLLOW_view_id_in_view_expression8198)
                view_id366 = self.view_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, view_id366.tree)
                # sdl92.g:540:36: ( ',' pid_expression )?
                alt106 = 2
                LA106_0 = self.input.LA(1)

                if (LA106_0 == COMMA) :
                    alt106 = 1
                if alt106 == 1:
                    # sdl92.g:540:37: ',' pid_expression
                    pass 
                    char_literal367=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_view_expression8201)
                    if self._state.backtracking == 0:

                        char_literal367_tree = self._adaptor.createWithPayload(char_literal367)
                        self._adaptor.addChild(root_0, char_literal367_tree)

                    self._state.following.append(self.FOLLOW_pid_expression_in_view_expression8203)
                    pid_expression368 = self.pid_expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, pid_expression368.tree)



                char_literal369=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_view_expression8207)
                if self._state.backtracking == 0:

                    char_literal369_tree = self._adaptor.createWithPayload(char_literal369)
                    self._adaptor.addChild(root_0, char_literal369_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "view_expression"

    class variable_access_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_access_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_access"
    # sdl92.g:542:1: variable_access : variable_id ;
    def variable_access(self, ):

        retval = self.variable_access_return()
        retval.start = self.input.LT(1)

        root_0 = None

        variable_id370 = None



        try:
            try:
                # sdl92.g:543:9: ( variable_id )
                # sdl92.g:543:17: variable_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_variable_id_in_variable_access8229)
                variable_id370 = self.variable_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, variable_id370.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_access"

    class operator_application_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operator_application_return, self).__init__()

            self.tree = None




    # $ANTLR start "operator_application"
    # sdl92.g:545:1: operator_application : operator_id '(' active_expression_list ')' ;
    def operator_application(self, ):

        retval = self.operator_application_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal372 = None
        char_literal374 = None
        operator_id371 = None

        active_expression_list373 = None


        char_literal372_tree = None
        char_literal374_tree = None

        try:
            try:
                # sdl92.g:546:9: ( operator_id '(' active_expression_list ')' )
                # sdl92.g:546:17: operator_id '(' active_expression_list ')'
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_operator_id_in_operator_application8259)
                operator_id371 = self.operator_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, operator_id371.tree)
                char_literal372=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_operator_application8261)
                if self._state.backtracking == 0:

                    char_literal372_tree = self._adaptor.createWithPayload(char_literal372)
                    self._adaptor.addChild(root_0, char_literal372_tree)

                self._state.following.append(self.FOLLOW_active_expression_list_in_operator_application8262)
                active_expression_list373 = self.active_expression_list()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_expression_list373.tree)
                char_literal374=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_operator_application8264)
                if self._state.backtracking == 0:

                    char_literal374_tree = self._adaptor.createWithPayload(char_literal374)
                    self._adaptor.addChild(root_0, char_literal374_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operator_application"

    class active_expression_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.active_expression_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "active_expression_list"
    # sdl92.g:548:1: active_expression_list : active_expression ( ',' expression_list )? ;
    def active_expression_list(self, ):

        retval = self.active_expression_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal376 = None
        active_expression375 = None

        expression_list377 = None


        char_literal376_tree = None

        try:
            try:
                # sdl92.g:549:9: ( active_expression ( ',' expression_list )? )
                # sdl92.g:549:17: active_expression ( ',' expression_list )?
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_active_expression_in_active_expression_list8295)
                active_expression375 = self.active_expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, active_expression375.tree)
                # sdl92.g:549:35: ( ',' expression_list )?
                alt107 = 2
                LA107_0 = self.input.LA(1)

                if (LA107_0 == COMMA) :
                    alt107 = 1
                if alt107 == 1:
                    # sdl92.g:549:36: ',' expression_list
                    pass 
                    char_literal376=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_active_expression_list8298)
                    if self._state.backtracking == 0:

                        char_literal376_tree = self._adaptor.createWithPayload(char_literal376)
                        self._adaptor.addChild(root_0, char_literal376_tree)

                    self._state.following.append(self.FOLLOW_expression_list_in_active_expression_list8300)
                    expression_list377 = self.expression_list()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, expression_list377.tree)






                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "active_expression_list"

    class conditional_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.conditional_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "conditional_expression"
    # sdl92.g:558:1: conditional_expression : IF expression THEN expression ELSE expression FI ;
    def conditional_expression(self, ):

        retval = self.conditional_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IF378 = None
        THEN380 = None
        ELSE382 = None
        FI384 = None
        expression379 = None

        expression381 = None

        expression383 = None


        IF378_tree = None
        THEN380_tree = None
        ELSE382_tree = None
        FI384_tree = None

        try:
            try:
                # sdl92.g:559:9: ( IF expression THEN expression ELSE expression FI )
                # sdl92.g:559:17: IF expression THEN expression ELSE expression FI
                pass 
                root_0 = self._adaptor.nil()

                IF378=self.match(self.input, IF, self.FOLLOW_IF_in_conditional_expression8336)
                if self._state.backtracking == 0:

                    IF378_tree = self._adaptor.createWithPayload(IF378)
                    self._adaptor.addChild(root_0, IF378_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression8338)
                expression379 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression379.tree)
                THEN380=self.match(self.input, THEN, self.FOLLOW_THEN_in_conditional_expression8340)
                if self._state.backtracking == 0:

                    THEN380_tree = self._adaptor.createWithPayload(THEN380)
                    self._adaptor.addChild(root_0, THEN380_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression8342)
                expression381 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression381.tree)
                ELSE382=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_conditional_expression8344)
                if self._state.backtracking == 0:

                    ELSE382_tree = self._adaptor.createWithPayload(ELSE382)
                    self._adaptor.addChild(root_0, ELSE382_tree)

                self._state.following.append(self.FOLLOW_expression_in_conditional_expression8346)
                expression383 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, expression383.tree)
                FI384=self.match(self.input, FI, self.FOLLOW_FI_in_conditional_expression8348)
                if self._state.backtracking == 0:

                    FI384_tree = self._adaptor.createWithPayload(FI384)
                    self._adaptor.addChild(root_0, FI384_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "conditional_expression"

    class synonym_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.synonym_return, self).__init__()

            self.tree = None




    # $ANTLR start "synonym"
    # sdl92.g:563:1: synonym : ID ;
    def synonym(self, ):

        retval = self.synonym_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID385 = None

        ID385_tree = None

        try:
            try:
                # sdl92.g:563:9: ( ID )
                # sdl92.g:563:17: ID
                pass 
                root_0 = self._adaptor.nil()

                ID385=self.match(self.input, ID, self.FOLLOW_ID_in_synonym8388)
                if self._state.backtracking == 0:

                    ID385_tree = self._adaptor.createWithPayload(ID385)
                    self._adaptor.addChild(root_0, ID385_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "synonym"

    class external_synonym_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.external_synonym_return, self).__init__()

            self.tree = None




    # $ANTLR start "external_synonym"
    # sdl92.g:565:1: external_synonym : external_synonym_id ;
    def external_synonym(self, ):

        retval = self.external_synonym_return()
        retval.start = self.input.LT(1)

        root_0 = None

        external_synonym_id386 = None



        try:
            try:
                # sdl92.g:566:9: ( external_synonym_id )
                # sdl92.g:566:17: external_synonym_id
                pass 
                root_0 = self._adaptor.nil()

                self._state.following.append(self.FOLLOW_external_synonym_id_in_external_synonym8411)
                external_synonym_id386 = self.external_synonym_id()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    self._adaptor.addChild(root_0, external_synonym_id386.tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "external_synonym"

    class conditional_ground_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.conditional_ground_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "conditional_ground_expression"
    # sdl92.g:569:1: conditional_ground_expression : IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr) ;
    def conditional_ground_expression(self, ):

        retval = self.conditional_ground_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        IF387 = None
        THEN388 = None
        ELSE389 = None
        FI390 = None
        ifexpr = None

        thenexpr = None

        elseexpr = None


        IF387_tree = None
        THEN388_tree = None
        ELSE389_tree = None
        FI390_tree = None
        stream_THEN = RewriteRuleTokenStream(self._adaptor, "token THEN")
        stream_IF = RewriteRuleTokenStream(self._adaptor, "token IF")
        stream_ELSE = RewriteRuleTokenStream(self._adaptor, "token ELSE")
        stream_FI = RewriteRuleTokenStream(self._adaptor, "token FI")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:570:9: ( IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr) )
                # sdl92.g:570:17: IF ifexpr= expression THEN thenexpr= expression ELSE elseexpr= expression FI
                pass 
                IF387=self.match(self.input, IF, self.FOLLOW_IF_in_conditional_ground_expression8434) 
                if self._state.backtracking == 0:
                    stream_IF.add(IF387)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression8438)
                ifexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(ifexpr.tree)
                THEN388=self.match(self.input, THEN, self.FOLLOW_THEN_in_conditional_ground_expression8440) 
                if self._state.backtracking == 0:
                    stream_THEN.add(THEN388)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression8444)
                thenexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(thenexpr.tree)
                ELSE389=self.match(self.input, ELSE, self.FOLLOW_ELSE_in_conditional_ground_expression8446) 
                if self._state.backtracking == 0:
                    stream_ELSE.add(ELSE389)
                self._state.following.append(self.FOLLOW_expression_in_conditional_ground_expression8450)
                elseexpr = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(elseexpr.tree)
                FI390=self.match(self.input, FI, self.FOLLOW_FI_in_conditional_ground_expression8452) 
                if self._state.backtracking == 0:
                    stream_FI.add(FI390)

                # AST Rewrite
                # elements: ifexpr, thenexpr, elseexpr
                # token labels: 
                # rule labels: elseexpr, retval, ifexpr, thenexpr
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if elseexpr is not None:
                        stream_elseexpr = RewriteRuleSubtreeStream(self._adaptor, "rule elseexpr", elseexpr.tree)
                    else:
                        stream_elseexpr = RewriteRuleSubtreeStream(self._adaptor, "token elseexpr", None)


                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    if ifexpr is not None:
                        stream_ifexpr = RewriteRuleSubtreeStream(self._adaptor, "rule ifexpr", ifexpr.tree)
                    else:
                        stream_ifexpr = RewriteRuleSubtreeStream(self._adaptor, "token ifexpr", None)


                    if thenexpr is not None:
                        stream_thenexpr = RewriteRuleSubtreeStream(self._adaptor, "rule thenexpr", thenexpr.tree)
                    else:
                        stream_thenexpr = RewriteRuleSubtreeStream(self._adaptor, "token thenexpr", None)


                    root_0 = self._adaptor.nil()
                    # 570:97: -> ^( IFTHENELSE $ifexpr $thenexpr $elseexpr)
                    # sdl92.g:570:100: ^( IFTHENELSE $ifexpr $thenexpr $elseexpr)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(IFTHENELSE, "IFTHENELSE"), root_1)

                    self._adaptor.addChild(root_1, stream_ifexpr.nextTree())
                    self._adaptor.addChild(root_1, stream_thenexpr.nextTree())
                    self._adaptor.addChild(root_1, stream_elseexpr.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "conditional_ground_expression"

    class expression_list_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.expression_list_return, self).__init__()

            self.tree = None




    # $ANTLR start "expression_list"
    # sdl92.g:573:1: expression_list : expression ( ',' expression )* -> ( expression )+ ;
    def expression_list(self, ):

        retval = self.expression_list_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal392 = None
        expression391 = None

        expression393 = None


        char_literal392_tree = None
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:574:9: ( expression ( ',' expression )* -> ( expression )+ )
                # sdl92.g:574:17: expression ( ',' expression )*
                pass 
                self._state.following.append(self.FOLLOW_expression_in_expression_list8497)
                expression391 = self.expression()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_expression.add(expression391.tree)
                # sdl92.g:574:28: ( ',' expression )*
                while True: #loop108
                    alt108 = 2
                    LA108_0 = self.input.LA(1)

                    if (LA108_0 == COMMA) :
                        alt108 = 1


                    if alt108 == 1:
                        # sdl92.g:574:29: ',' expression
                        pass 
                        char_literal392=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_expression_list8500) 
                        if self._state.backtracking == 0:
                            stream_COMMA.add(char_literal392)
                        self._state.following.append(self.FOLLOW_expression_in_expression_list8502)
                        expression393 = self.expression()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_expression.add(expression393.tree)


                    else:
                        break #loop108

                # AST Rewrite
                # elements: expression
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 574:57: -> ( expression )+
                    # sdl92.g:574:60: ( expression )+
                    if not (stream_expression.hasNext()):
                        raise RewriteEarlyExitException()

                    while stream_expression.hasNext():
                        self._adaptor.addChild(root_0, stream_expression.nextTree())


                    stream_expression.reset()



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "expression_list"

    class terminator_statement_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.terminator_statement_return, self).__init__()

            self.tree = None




    # $ANTLR start "terminator_statement"
    # sdl92.g:576:1: terminator_statement : ( label )? ( cif )? ( hyperlink )? terminator end -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator ) ;
    def terminator_statement(self, ):

        retval = self.terminator_statement_return()
        retval.start = self.input.LT(1)

        root_0 = None

        label394 = None

        cif395 = None

        hyperlink396 = None

        terminator397 = None

        end398 = None


        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_terminator = RewriteRuleSubtreeStream(self._adaptor, "rule terminator")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        stream_label = RewriteRuleSubtreeStream(self._adaptor, "rule label")
        stream_end = RewriteRuleSubtreeStream(self._adaptor, "rule end")
        try:
            try:
                # sdl92.g:577:9: ( ( label )? ( cif )? ( hyperlink )? terminator end -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator ) )
                # sdl92.g:577:17: ( label )? ( cif )? ( hyperlink )? terminator end
                pass 
                # sdl92.g:577:17: ( label )?
                alt109 = 2
                alt109 = self.dfa109.predict(self.input)
                if alt109 == 1:
                    # sdl92.g:0:0: label
                    pass 
                    self._state.following.append(self.FOLLOW_label_in_terminator_statement8542)
                    label394 = self.label()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_label.add(label394.tree)



                # sdl92.g:578:17: ( cif )?
                alt110 = 2
                LA110_0 = self.input.LA(1)

                if (LA110_0 == 176) :
                    LA110_1 = self.input.LA(2)

                    if (LA110_1 == LABEL or LA110_1 == COMMENT or LA110_1 == STATE or LA110_1 == PROVIDED or LA110_1 == INPUT or LA110_1 == DECISION or LA110_1 == ANSWER or LA110_1 == OUTPUT or (TEXT <= LA110_1 <= JOIN) or LA110_1 == TASK or LA110_1 == START or LA110_1 == PROCEDURE) :
                        alt110 = 1
                if alt110 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_terminator_statement8561)
                    cif395 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif395.tree)



                # sdl92.g:579:17: ( hyperlink )?
                alt111 = 2
                LA111_0 = self.input.LA(1)

                if (LA111_0 == 176) :
                    alt111 = 1
                if alt111 == 1:
                    # sdl92.g:0:0: hyperlink
                    pass 
                    self._state.following.append(self.FOLLOW_hyperlink_in_terminator_statement8580)
                    hyperlink396 = self.hyperlink()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_hyperlink.add(hyperlink396.tree)



                self._state.following.append(self.FOLLOW_terminator_in_terminator_statement8599)
                terminator397 = self.terminator()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_terminator.add(terminator397.tree)
                self._state.following.append(self.FOLLOW_end_in_terminator_statement8618)
                end398 = self.end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_end.add(end398.tree)

                # AST Rewrite
                # elements: cif, hyperlink, label, end, terminator
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 581:39: -> ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator )
                    # sdl92.g:581:42: ^( TERMINATOR ( label )? ( cif )? ( hyperlink )? ( end )? terminator )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(TERMINATOR, "TERMINATOR"), root_1)

                    # sdl92.g:581:55: ( label )?
                    if stream_label.hasNext():
                        self._adaptor.addChild(root_1, stream_label.nextTree())


                    stream_label.reset();
                    # sdl92.g:581:62: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    # sdl92.g:581:67: ( hyperlink )?
                    if stream_hyperlink.hasNext():
                        self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                    stream_hyperlink.reset();
                    # sdl92.g:581:78: ( end )?
                    if stream_end.hasNext():
                        self._adaptor.addChild(root_1, stream_end.nextTree())


                    stream_end.reset();
                    self._adaptor.addChild(root_1, stream_terminator.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "terminator_statement"

    class label_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.label_return, self).__init__()

            self.tree = None




    # $ANTLR start "label"
    # sdl92.g:583:1: label : ( cif )? connector_name ':' -> ^( LABEL ( cif )? connector_name ) ;
    def label(self, ):

        retval = self.label_return()
        retval.start = self.input.LT(1)

        root_0 = None

        char_literal401 = None
        cif399 = None

        connector_name400 = None


        char_literal401_tree = None
        stream_166 = RewriteRuleTokenStream(self._adaptor, "token 166")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_connector_name = RewriteRuleSubtreeStream(self._adaptor, "rule connector_name")
        try:
            try:
                # sdl92.g:583:9: ( ( cif )? connector_name ':' -> ^( LABEL ( cif )? connector_name ) )
                # sdl92.g:583:17: ( cif )? connector_name ':'
                pass 
                # sdl92.g:583:17: ( cif )?
                alt112 = 2
                LA112_0 = self.input.LA(1)

                if (LA112_0 == 176) :
                    alt112 = 1
                if alt112 == 1:
                    # sdl92.g:0:0: cif
                    pass 
                    self._state.following.append(self.FOLLOW_cif_in_label8680)
                    cif399 = self.cif()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_cif.add(cif399.tree)



                self._state.following.append(self.FOLLOW_connector_name_in_label8683)
                connector_name400 = self.connector_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_connector_name.add(connector_name400.tree)
                char_literal401=self.match(self.input, 166, self.FOLLOW_166_in_label8685) 
                if self._state.backtracking == 0:
                    stream_166.add(char_literal401)

                # AST Rewrite
                # elements: cif, connector_name
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 583:43: -> ^( LABEL ( cif )? connector_name )
                    # sdl92.g:583:46: ^( LABEL ( cif )? connector_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(LABEL, "LABEL"), root_1)

                    # sdl92.g:583:54: ( cif )?
                    if stream_cif.hasNext():
                        self._adaptor.addChild(root_1, stream_cif.nextTree())


                    stream_cif.reset();
                    self._adaptor.addChild(root_1, stream_connector_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "label"

    class terminator_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.terminator_return, self).__init__()

            self.tree = None




    # $ANTLR start "terminator"
    # sdl92.g:586:1: terminator : ( nextstate | join | stop | return_stmt );
    def terminator(self, ):

        retval = self.terminator_return()
        retval.start = self.input.LT(1)

        root_0 = None

        nextstate402 = None

        join403 = None

        stop404 = None

        return_stmt405 = None



        try:
            try:
                # sdl92.g:587:9: ( nextstate | join | stop | return_stmt )
                alt113 = 4
                LA113 = self.input.LA(1)
                if LA113 == NEXTSTATE:
                    alt113 = 1
                elif LA113 == JOIN:
                    alt113 = 2
                elif LA113 == STOP:
                    alt113 = 3
                elif LA113 == RETURN:
                    alt113 = 4
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 113, 0, self.input)

                    raise nvae

                if alt113 == 1:
                    # sdl92.g:587:17: nextstate
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_nextstate_in_terminator8729)
                    nextstate402 = self.nextstate()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, nextstate402.tree)


                elif alt113 == 2:
                    # sdl92.g:587:29: join
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_join_in_terminator8733)
                    join403 = self.join()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, join403.tree)


                elif alt113 == 3:
                    # sdl92.g:587:36: stop
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_stop_in_terminator8737)
                    stop404 = self.stop()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, stop404.tree)


                elif alt113 == 4:
                    # sdl92.g:587:43: return_stmt
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_return_stmt_in_terminator8741)
                    return_stmt405 = self.return_stmt()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, return_stmt405.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "terminator"

    class join_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.join_return, self).__init__()

            self.tree = None




    # $ANTLR start "join"
    # sdl92.g:589:1: join : JOIN connector_name -> ^( JOIN connector_name ) ;
    def join(self, ):

        retval = self.join_return()
        retval.start = self.input.LT(1)

        root_0 = None

        JOIN406 = None
        connector_name407 = None


        JOIN406_tree = None
        stream_JOIN = RewriteRuleTokenStream(self._adaptor, "token JOIN")
        stream_connector_name = RewriteRuleSubtreeStream(self._adaptor, "rule connector_name")
        try:
            try:
                # sdl92.g:589:9: ( JOIN connector_name -> ^( JOIN connector_name ) )
                # sdl92.g:589:18: JOIN connector_name
                pass 
                JOIN406=self.match(self.input, JOIN, self.FOLLOW_JOIN_in_join8768) 
                if self._state.backtracking == 0:
                    stream_JOIN.add(JOIN406)
                self._state.following.append(self.FOLLOW_connector_name_in_join8770)
                connector_name407 = self.connector_name()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_connector_name.add(connector_name407.tree)

                # AST Rewrite
                # elements: connector_name, JOIN
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 589:57: -> ^( JOIN connector_name )
                    # sdl92.g:589:60: ^( JOIN connector_name )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_JOIN.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_connector_name.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "join"

    class stop_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stop_return, self).__init__()

            self.tree = None




    # $ANTLR start "stop"
    # sdl92.g:591:1: stop : STOP ;
    def stop(self, ):

        retval = self.stop_return()
        retval.start = self.input.LT(1)

        root_0 = None

        STOP408 = None

        STOP408_tree = None

        try:
            try:
                # sdl92.g:591:9: ( STOP )
                # sdl92.g:591:17: STOP
                pass 
                root_0 = self._adaptor.nil()

                STOP408=self.match(self.input, STOP, self.FOLLOW_STOP_in_stop8814)
                if self._state.backtracking == 0:

                    STOP408_tree = self._adaptor.createWithPayload(STOP408)
                    self._adaptor.addChild(root_0, STOP408_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stop"

    class return_stmt_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.return_stmt_return, self).__init__()

            self.tree = None




    # $ANTLR start "return_stmt"
    # sdl92.g:593:1: return_stmt : RETURN ( expression )? -> ^( RETURN ( expression )? ) ;
    def return_stmt(self, ):

        retval = self.return_stmt_return()
        retval.start = self.input.LT(1)

        root_0 = None

        RETURN409 = None
        expression410 = None


        RETURN409_tree = None
        stream_RETURN = RewriteRuleTokenStream(self._adaptor, "token RETURN")
        stream_expression = RewriteRuleSubtreeStream(self._adaptor, "rule expression")
        try:
            try:
                # sdl92.g:593:17: ( RETURN ( expression )? -> ^( RETURN ( expression )? ) )
                # sdl92.g:593:25: RETURN ( expression )?
                pass 
                RETURN409=self.match(self.input, RETURN, self.FOLLOW_RETURN_in_return_stmt8832) 
                if self._state.backtracking == 0:
                    stream_RETURN.add(RETURN409)
                # sdl92.g:593:32: ( expression )?
                alt114 = 2
                LA114_0 = self.input.LA(1)

                if (LA114_0 == IF or LA114_0 == INT or LA114_0 == L_PAREN or LA114_0 == ID or LA114_0 == DASH or (BitStringLiteral <= LA114_0 <= L_BRACKET) or LA114_0 == NOT) :
                    alt114 = 1
                if alt114 == 1:
                    # sdl92.g:0:0: expression
                    pass 
                    self._state.following.append(self.FOLLOW_expression_in_return_stmt8834)
                    expression410 = self.expression()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        stream_expression.add(expression410.tree)




                # AST Rewrite
                # elements: expression, RETURN
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 593:57: -> ^( RETURN ( expression )? )
                    # sdl92.g:593:60: ^( RETURN ( expression )? )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_RETURN.nextNode(), root_1)

                    # sdl92.g:593:69: ( expression )?
                    if stream_expression.hasNext():
                        self._adaptor.addChild(root_1, stream_expression.nextTree())


                    stream_expression.reset();

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "return_stmt"

    class nextstate_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.nextstate_return, self).__init__()

            self.tree = None




    # $ANTLR start "nextstate"
    # sdl92.g:596:1: nextstate : NEXTSTATE nextstatebody -> ^( NEXTSTATE nextstatebody ) ;
    def nextstate(self, ):

        retval = self.nextstate_return()
        retval.start = self.input.LT(1)

        root_0 = None

        NEXTSTATE411 = None
        nextstatebody412 = None


        NEXTSTATE411_tree = None
        stream_NEXTSTATE = RewriteRuleTokenStream(self._adaptor, "token NEXTSTATE")
        stream_nextstatebody = RewriteRuleSubtreeStream(self._adaptor, "rule nextstatebody")
        try:
            try:
                # sdl92.g:596:17: ( NEXTSTATE nextstatebody -> ^( NEXTSTATE nextstatebody ) )
                # sdl92.g:596:25: NEXTSTATE nextstatebody
                pass 
                NEXTSTATE411=self.match(self.input, NEXTSTATE, self.FOLLOW_NEXTSTATE_in_nextstate8903) 
                if self._state.backtracking == 0:
                    stream_NEXTSTATE.add(NEXTSTATE411)
                self._state.following.append(self.FOLLOW_nextstatebody_in_nextstate8905)
                nextstatebody412 = self.nextstatebody()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_nextstatebody.add(nextstatebody412.tree)

                # AST Rewrite
                # elements: nextstatebody, NEXTSTATE
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 596:57: -> ^( NEXTSTATE nextstatebody )
                    # sdl92.g:596:60: ^( NEXTSTATE nextstatebody )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_NEXTSTATE.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_nextstatebody.nextTree())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "nextstate"

    class nextstatebody_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.nextstatebody_return, self).__init__()

            self.tree = None




    # $ANTLR start "nextstatebody"
    # sdl92.g:599:1: nextstatebody : ( statename | dash_nextstate );
    def nextstatebody(self, ):

        retval = self.nextstatebody_return()
        retval.start = self.input.LT(1)

        root_0 = None

        statename413 = None

        dash_nextstate414 = None



        try:
            try:
                # sdl92.g:599:14: ( statename | dash_nextstate )
                alt115 = 2
                LA115_0 = self.input.LA(1)

                if (LA115_0 == ID) :
                    alt115 = 1
                elif (LA115_0 == DASH) :
                    alt115 = 2
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 115, 0, self.input)

                    raise nvae

                if alt115 == 1:
                    # sdl92.g:599:17: statename
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_statename_in_nextstatebody8948)
                    statename413 = self.statename()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, statename413.tree)


                elif alt115 == 2:
                    # sdl92.g:600:17: dash_nextstate
                    pass 
                    root_0 = self._adaptor.nil()

                    self._state.following.append(self.FOLLOW_dash_nextstate_in_nextstatebody8967)
                    dash_nextstate414 = self.dash_nextstate()

                    self._state.following.pop()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, dash_nextstate414.tree)


                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "nextstatebody"

    class end_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.end_return, self).__init__()

            self.tree = None




    # $ANTLR start "end"
    # sdl92.g:602:1: end : ( ( cif )? ( hyperlink )? COMMENT StringLiteral )? SEMI -> ( ^( COMMENT ( cif )? ( hyperlink )? StringLiteral ) )? ;
    def end(self, ):

        retval = self.end_return()
        retval.start = self.input.LT(1)

        root_0 = None

        COMMENT417 = None
        StringLiteral418 = None
        SEMI419 = None
        cif415 = None

        hyperlink416 = None


        COMMENT417_tree = None
        StringLiteral418_tree = None
        SEMI419_tree = None
        stream_StringLiteral = RewriteRuleTokenStream(self._adaptor, "token StringLiteral")
        stream_COMMENT = RewriteRuleTokenStream(self._adaptor, "token COMMENT")
        stream_SEMI = RewriteRuleTokenStream(self._adaptor, "token SEMI")
        stream_cif = RewriteRuleSubtreeStream(self._adaptor, "rule cif")
        stream_hyperlink = RewriteRuleSubtreeStream(self._adaptor, "rule hyperlink")
        try:
            try:
                # sdl92.g:603:9: ( ( ( cif )? ( hyperlink )? COMMENT StringLiteral )? SEMI -> ( ^( COMMENT ( cif )? ( hyperlink )? StringLiteral ) )? )
                # sdl92.g:603:13: ( ( cif )? ( hyperlink )? COMMENT StringLiteral )? SEMI
                pass 
                # sdl92.g:603:13: ( ( cif )? ( hyperlink )? COMMENT StringLiteral )?
                alt118 = 2
                LA118_0 = self.input.LA(1)

                if (LA118_0 == COMMENT or LA118_0 == 176) :
                    alt118 = 1
                if alt118 == 1:
                    # sdl92.g:603:14: ( cif )? ( hyperlink )? COMMENT StringLiteral
                    pass 
                    # sdl92.g:603:14: ( cif )?
                    alt116 = 2
                    LA116_0 = self.input.LA(1)

                    if (LA116_0 == 176) :
                        LA116_1 = self.input.LA(2)

                        if (LA116_1 == LABEL or LA116_1 == COMMENT or LA116_1 == STATE or LA116_1 == PROVIDED or LA116_1 == INPUT or LA116_1 == DECISION or LA116_1 == ANSWER or LA116_1 == OUTPUT or (TEXT <= LA116_1 <= JOIN) or LA116_1 == TASK or LA116_1 == START or LA116_1 == PROCEDURE) :
                            alt116 = 1
                    if alt116 == 1:
                        # sdl92.g:0:0: cif
                        pass 
                        self._state.following.append(self.FOLLOW_cif_in_end8988)
                        cif415 = self.cif()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_cif.add(cif415.tree)



                    # sdl92.g:603:19: ( hyperlink )?
                    alt117 = 2
                    LA117_0 = self.input.LA(1)

                    if (LA117_0 == 176) :
                        alt117 = 1
                    if alt117 == 1:
                        # sdl92.g:0:0: hyperlink
                        pass 
                        self._state.following.append(self.FOLLOW_hyperlink_in_end8991)
                        hyperlink416 = self.hyperlink()

                        self._state.following.pop()
                        if self._state.backtracking == 0:
                            stream_hyperlink.add(hyperlink416.tree)



                    COMMENT417=self.match(self.input, COMMENT, self.FOLLOW_COMMENT_in_end8994) 
                    if self._state.backtracking == 0:
                        stream_COMMENT.add(COMMENT417)
                    StringLiteral418=self.match(self.input, StringLiteral, self.FOLLOW_StringLiteral_in_end8996) 
                    if self._state.backtracking == 0:
                        stream_StringLiteral.add(StringLiteral418)



                SEMI419=self.match(self.input, SEMI, self.FOLLOW_SEMI_in_end9000) 
                if self._state.backtracking == 0:
                    stream_SEMI.add(SEMI419)

                # AST Rewrite
                # elements: StringLiteral, hyperlink, COMMENT, cif
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 603:68: -> ( ^( COMMENT ( cif )? ( hyperlink )? StringLiteral ) )?
                    # sdl92.g:603:71: ( ^( COMMENT ( cif )? ( hyperlink )? StringLiteral ) )?
                    if stream_StringLiteral.hasNext() or stream_hyperlink.hasNext() or stream_COMMENT.hasNext() or stream_cif.hasNext():
                        # sdl92.g:603:71: ^( COMMENT ( cif )? ( hyperlink )? StringLiteral )
                        root_1 = self._adaptor.nil()
                        root_1 = self._adaptor.becomeRoot(stream_COMMENT.nextNode(), root_1)

                        # sdl92.g:603:81: ( cif )?
                        if stream_cif.hasNext():
                            self._adaptor.addChild(root_1, stream_cif.nextTree())


                        stream_cif.reset();
                        # sdl92.g:603:86: ( hyperlink )?
                        if stream_hyperlink.hasNext():
                            self._adaptor.addChild(root_1, stream_hyperlink.nextTree())


                        stream_hyperlink.reset();
                        self._adaptor.addChild(root_1, stream_StringLiteral.nextNode())

                        self._adaptor.addChild(root_0, root_1)


                    stream_StringLiteral.reset();
                    stream_hyperlink.reset();
                    stream_COMMENT.reset();
                    stream_cif.reset();



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "end"

    class cif_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif"
    # sdl92.g:606:1: cif : cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end -> ^( CIF $x $y $width $height) ;
    def cif(self, ):

        retval = self.cif_return()
        retval.start = self.input.LT(1)

        root_0 = None

        x = None
        y = None
        width = None
        height = None
        L_PAREN422 = None
        COMMA423 = None
        R_PAREN424 = None
        COMMA425 = None
        L_PAREN426 = None
        COMMA427 = None
        R_PAREN428 = None
        cif_decl420 = None

        symbolname421 = None

        cif_end429 = None


        x_tree = None
        y_tree = None
        width_tree = None
        height_tree = None
        L_PAREN422_tree = None
        COMMA423_tree = None
        R_PAREN424_tree = None
        COMMA425_tree = None
        L_PAREN426_tree = None
        COMMA427_tree = None
        R_PAREN428_tree = None
        stream_INT = RewriteRuleTokenStream(self._adaptor, "token INT")
        stream_COMMA = RewriteRuleTokenStream(self._adaptor, "token COMMA")
        stream_R_PAREN = RewriteRuleTokenStream(self._adaptor, "token R_PAREN")
        stream_L_PAREN = RewriteRuleTokenStream(self._adaptor, "token L_PAREN")
        stream_symbolname = RewriteRuleSubtreeStream(self._adaptor, "rule symbolname")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:607:5: ( cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end -> ^( CIF $x $y $width $height) )
                # sdl92.g:607:9: cif_decl symbolname L_PAREN x= INT COMMA y= INT R_PAREN COMMA L_PAREN width= INT COMMA height= INT R_PAREN cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_cif9047)
                cif_decl420 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl420.tree)
                self._state.following.append(self.FOLLOW_symbolname_in_cif9049)
                symbolname421 = self.symbolname()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_symbolname.add(symbolname421.tree)
                L_PAREN422=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_cif9059) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN422)
                x=self.match(self.input, INT, self.FOLLOW_INT_in_cif9063) 
                if self._state.backtracking == 0:
                    stream_INT.add(x)
                COMMA423=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif9065) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA423)
                y=self.match(self.input, INT, self.FOLLOW_INT_in_cif9069) 
                if self._state.backtracking == 0:
                    stream_INT.add(y)
                R_PAREN424=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_cif9071) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN424)
                COMMA425=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif9082) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA425)
                L_PAREN426=self.match(self.input, L_PAREN, self.FOLLOW_L_PAREN_in_cif9092) 
                if self._state.backtracking == 0:
                    stream_L_PAREN.add(L_PAREN426)
                width=self.match(self.input, INT, self.FOLLOW_INT_in_cif9096) 
                if self._state.backtracking == 0:
                    stream_INT.add(width)
                COMMA427=self.match(self.input, COMMA, self.FOLLOW_COMMA_in_cif9098) 
                if self._state.backtracking == 0:
                    stream_COMMA.add(COMMA427)
                height=self.match(self.input, INT, self.FOLLOW_INT_in_cif9102) 
                if self._state.backtracking == 0:
                    stream_INT.add(height)
                R_PAREN428=self.match(self.input, R_PAREN, self.FOLLOW_R_PAREN_in_cif9104) 
                if self._state.backtracking == 0:
                    stream_R_PAREN.add(R_PAREN428)
                self._state.following.append(self.FOLLOW_cif_end_in_cif9115)
                cif_end429 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end429.tree)

                # AST Rewrite
                # elements: width, x, height, y
                # token labels: height, width, y, x
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0
                    stream_height = RewriteRuleTokenStream(self._adaptor, "token height", height)
                    stream_width = RewriteRuleTokenStream(self._adaptor, "token width", width)
                    stream_y = RewriteRuleTokenStream(self._adaptor, "token y", y)
                    stream_x = RewriteRuleTokenStream(self._adaptor, "token x", x)

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 611:61: -> ^( CIF $x $y $width $height)
                    # sdl92.g:611:64: ^( CIF $x $y $width $height)
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(self._adaptor.createFromType(CIF, "CIF"), root_1)

                    self._adaptor.addChild(root_1, stream_x.nextNode())
                    self._adaptor.addChild(root_1, stream_y.nextNode())
                    self._adaptor.addChild(root_1, stream_width.nextNode())
                    self._adaptor.addChild(root_1, stream_height.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif"

    class hyperlink_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.hyperlink_return, self).__init__()

            self.tree = None




    # $ANTLR start "hyperlink"
    # sdl92.g:613:1: hyperlink : cif_decl KEEP SPECIFIC GEODE HYPERLINK StringLiteral cif_end -> ^( HYPERLINK StringLiteral ) ;
    def hyperlink(self, ):

        retval = self.hyperlink_return()
        retval.start = self.input.LT(1)

        root_0 = None

        KEEP431 = None
        SPECIFIC432 = None
        GEODE433 = None
        HYPERLINK434 = None
        StringLiteral435 = None
        cif_decl430 = None

        cif_end436 = None


        KEEP431_tree = None
        SPECIFIC432_tree = None
        GEODE433_tree = None
        HYPERLINK434_tree = None
        StringLiteral435_tree = None
        stream_StringLiteral = RewriteRuleTokenStream(self._adaptor, "token StringLiteral")
        stream_SPECIFIC = RewriteRuleTokenStream(self._adaptor, "token SPECIFIC")
        stream_KEEP = RewriteRuleTokenStream(self._adaptor, "token KEEP")
        stream_HYPERLINK = RewriteRuleTokenStream(self._adaptor, "token HYPERLINK")
        stream_GEODE = RewriteRuleTokenStream(self._adaptor, "token GEODE")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:614:5: ( cif_decl KEEP SPECIFIC GEODE HYPERLINK StringLiteral cif_end -> ^( HYPERLINK StringLiteral ) )
                # sdl92.g:614:9: cif_decl KEEP SPECIFIC GEODE HYPERLINK StringLiteral cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_hyperlink9191)
                cif_decl430 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl430.tree)
                KEEP431=self.match(self.input, KEEP, self.FOLLOW_KEEP_in_hyperlink9193) 
                if self._state.backtracking == 0:
                    stream_KEEP.add(KEEP431)
                SPECIFIC432=self.match(self.input, SPECIFIC, self.FOLLOW_SPECIFIC_in_hyperlink9195) 
                if self._state.backtracking == 0:
                    stream_SPECIFIC.add(SPECIFIC432)
                GEODE433=self.match(self.input, GEODE, self.FOLLOW_GEODE_in_hyperlink9197) 
                if self._state.backtracking == 0:
                    stream_GEODE.add(GEODE433)
                HYPERLINK434=self.match(self.input, HYPERLINK, self.FOLLOW_HYPERLINK_in_hyperlink9199) 
                if self._state.backtracking == 0:
                    stream_HYPERLINK.add(HYPERLINK434)
                StringLiteral435=self.match(self.input, StringLiteral, self.FOLLOW_StringLiteral_in_hyperlink9201) 
                if self._state.backtracking == 0:
                    stream_StringLiteral.add(StringLiteral435)
                self._state.following.append(self.FOLLOW_cif_end_in_hyperlink9211)
                cif_end436 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end436.tree)

                # AST Rewrite
                # elements: HYPERLINK, StringLiteral
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 615:61: -> ^( HYPERLINK StringLiteral )
                    # sdl92.g:615:64: ^( HYPERLINK StringLiteral )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_HYPERLINK.nextNode(), root_1)

                    self._adaptor.addChild(root_1, stream_StringLiteral.nextNode())

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "hyperlink"

    class symbolname_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.symbolname_return, self).__init__()

            self.tree = None




    # $ANTLR start "symbolname"
    # sdl92.g:618:1: symbolname : ( START | INPUT | OUTPUT | STATE | PROCEDURE | DECISION | TEXT | TASK | NEXTSTATE | ANSWER | PROVIDED | COMMENT | LABEL | JOIN );
    def symbolname(self, ):

        retval = self.symbolname_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set437 = None

        set437_tree = None

        try:
            try:
                # sdl92.g:619:5: ( START | INPUT | OUTPUT | STATE | PROCEDURE | DECISION | TEXT | TASK | NEXTSTATE | ANSWER | PROVIDED | COMMENT | LABEL | JOIN )
                # sdl92.g:
                pass 
                root_0 = self._adaptor.nil()

                set437 = self.input.LT(1)
                if self.input.LA(1) == LABEL or self.input.LA(1) == COMMENT or self.input.LA(1) == STATE or self.input.LA(1) == PROVIDED or self.input.LA(1) == INPUT or self.input.LA(1) == DECISION or self.input.LA(1) == ANSWER or self.input.LA(1) == OUTPUT or (TEXT <= self.input.LA(1) <= JOIN) or self.input.LA(1) == TASK or self.input.LA(1) == START or self.input.LA(1) == PROCEDURE:
                    self.input.consume()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, self._adaptor.createWithPayload(set437))
                    self._state.errorRecovery = False

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    mse = MismatchedSetException(None, self.input)
                    raise mse





                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "symbolname"

    class cif_decl_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_decl_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_decl"
    # sdl92.g:621:1: cif_decl : '/* CIF' ;
    def cif_decl(self, ):

        retval = self.cif_decl_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal438 = None

        string_literal438_tree = None

        try:
            try:
                # sdl92.g:621:17: ( '/* CIF' )
                # sdl92.g:621:25: '/* CIF'
                pass 
                root_0 = self._adaptor.nil()

                string_literal438=self.match(self.input, 176, self.FOLLOW_176_in_cif_decl9353)
                if self._state.backtracking == 0:

                    string_literal438_tree = self._adaptor.createWithPayload(string_literal438)
                    self._adaptor.addChild(root_0, string_literal438_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_decl"

    class cif_end_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_end_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_end"
    # sdl92.g:622:1: cif_end : '*/' ;
    def cif_end(self, ):

        retval = self.cif_end_return()
        retval.start = self.input.LT(1)

        root_0 = None

        string_literal439 = None

        string_literal439_tree = None

        try:
            try:
                # sdl92.g:622:17: ( '*/' )
                # sdl92.g:622:25: '*/'
                pass 
                root_0 = self._adaptor.nil()

                string_literal439=self.match(self.input, 177, self.FOLLOW_177_in_cif_end9374)
                if self._state.backtracking == 0:

                    string_literal439_tree = self._adaptor.createWithPayload(string_literal439)
                    self._adaptor.addChild(root_0, string_literal439_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_end"

    class cif_end_text_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.cif_end_text_return, self).__init__()

            self.tree = None




    # $ANTLR start "cif_end_text"
    # sdl92.g:623:1: cif_end_text : cif_decl ENDTEXT cif_end -> ^( ENDTEXT ) ;
    def cif_end_text(self, ):

        retval = self.cif_end_text_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ENDTEXT441 = None
        cif_decl440 = None

        cif_end442 = None


        ENDTEXT441_tree = None
        stream_ENDTEXT = RewriteRuleTokenStream(self._adaptor, "token ENDTEXT")
        stream_cif_end = RewriteRuleSubtreeStream(self._adaptor, "rule cif_end")
        stream_cif_decl = RewriteRuleSubtreeStream(self._adaptor, "rule cif_decl")
        try:
            try:
                # sdl92.g:623:17: ( cif_decl ENDTEXT cif_end -> ^( ENDTEXT ) )
                # sdl92.g:623:25: cif_decl ENDTEXT cif_end
                pass 
                self._state.following.append(self.FOLLOW_cif_decl_in_cif_end_text9390)
                cif_decl440 = self.cif_decl()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_decl.add(cif_decl440.tree)
                ENDTEXT441=self.match(self.input, ENDTEXT, self.FOLLOW_ENDTEXT_in_cif_end_text9392) 
                if self._state.backtracking == 0:
                    stream_ENDTEXT.add(ENDTEXT441)
                self._state.following.append(self.FOLLOW_cif_end_in_cif_end_text9394)
                cif_end442 = self.cif_end()

                self._state.following.pop()
                if self._state.backtracking == 0:
                    stream_cif_end.add(cif_end442.tree)

                # AST Rewrite
                # elements: ENDTEXT
                # token labels: 
                # rule labels: retval
                # token list labels: 
                # rule list labels: 
                # wildcard labels: 
                if self._state.backtracking == 0:

                    retval.tree = root_0

                    if retval is not None:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "rule retval", retval.tree)
                    else:
                        stream_retval = RewriteRuleSubtreeStream(self._adaptor, "token retval", None)


                    root_0 = self._adaptor.nil()
                    # 623:52: -> ^( ENDTEXT )
                    # sdl92.g:623:55: ^( ENDTEXT )
                    root_1 = self._adaptor.nil()
                    root_1 = self._adaptor.becomeRoot(stream_ENDTEXT.nextNode(), root_1)

                    self._adaptor.addChild(root_0, root_1)



                    retval.tree = root_0



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "cif_end_text"

    class dash_nextstate_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.dash_nextstate_return, self).__init__()

            self.tree = None




    # $ANTLR start "dash_nextstate"
    # sdl92.g:624:1: dash_nextstate : DASH ;
    def dash_nextstate(self, ):

        retval = self.dash_nextstate_return()
        retval.start = self.input.LT(1)

        root_0 = None

        DASH443 = None

        DASH443_tree = None

        try:
            try:
                # sdl92.g:624:17: ( DASH )
                # sdl92.g:624:25: DASH
                pass 
                root_0 = self._adaptor.nil()

                DASH443=self.match(self.input, DASH, self.FOLLOW_DASH_in_dash_nextstate9416)
                if self._state.backtracking == 0:

                    DASH443_tree = self._adaptor.createWithPayload(DASH443)
                    self._adaptor.addChild(root_0, DASH443_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "dash_nextstate"

    class connector_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.connector_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "connector_name"
    # sdl92.g:625:1: connector_name : ID ;
    def connector_name(self, ):

        retval = self.connector_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID444 = None

        ID444_tree = None

        try:
            try:
                # sdl92.g:625:17: ( ID )
                # sdl92.g:625:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID444=self.match(self.input, ID, self.FOLLOW_ID_in_connector_name9430)
                if self._state.backtracking == 0:

                    ID444_tree = self._adaptor.createWithPayload(ID444)
                    self._adaptor.addChild(root_0, ID444_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "connector_name"

    class signal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_id"
    # sdl92.g:626:1: signal_id : ID ;
    def signal_id(self, ):

        retval = self.signal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID445 = None

        ID445_tree = None

        try:
            try:
                # sdl92.g:626:17: ( ID )
                # sdl92.g:626:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID445=self.match(self.input, ID, self.FOLLOW_ID_in_signal_id9449)
                if self._state.backtracking == 0:

                    ID445_tree = self._adaptor.createWithPayload(ID445)
                    self._adaptor.addChild(root_0, ID445_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_id"

    class statename_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.statename_return, self).__init__()

            self.tree = None




    # $ANTLR start "statename"
    # sdl92.g:627:1: statename : ID ;
    def statename(self, ):

        retval = self.statename_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID446 = None

        ID446_tree = None

        try:
            try:
                # sdl92.g:627:17: ( ID )
                # sdl92.g:627:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID446=self.match(self.input, ID, self.FOLLOW_ID_in_statename9468)
                if self._state.backtracking == 0:

                    ID446_tree = self._adaptor.createWithPayload(ID446)
                    self._adaptor.addChild(root_0, ID446_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "statename"

    class variable_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.variable_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "variable_id"
    # sdl92.g:628:1: variable_id : ID ;
    def variable_id(self, ):

        retval = self.variable_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID447 = None

        ID447_tree = None

        try:
            try:
                # sdl92.g:628:17: ( ID )
                # sdl92.g:628:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID447=self.match(self.input, ID, self.FOLLOW_ID_in_variable_id9485)
                if self._state.backtracking == 0:

                    ID447_tree = self._adaptor.createWithPayload(ID447)
                    self._adaptor.addChild(root_0, ID447_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "variable_id"

    class literal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.literal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "literal_id"
    # sdl92.g:629:1: literal_id : ( ID | INT );
    def literal_id(self, ):

        retval = self.literal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        set448 = None

        set448_tree = None

        try:
            try:
                # sdl92.g:629:17: ( ID | INT )
                # sdl92.g:
                pass 
                root_0 = self._adaptor.nil()

                set448 = self.input.LT(1)
                if self.input.LA(1) == INT or self.input.LA(1) == ID:
                    self.input.consume()
                    if self._state.backtracking == 0:
                        self._adaptor.addChild(root_0, self._adaptor.createWithPayload(set448))
                    self._state.errorRecovery = False

                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    mse = MismatchedSetException(None, self.input)
                    raise mse





                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "literal_id"

    class process_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.process_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "process_id"
    # sdl92.g:630:1: process_id : ID ;
    def process_id(self, ):

        retval = self.process_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID449 = None

        ID449_tree = None

        try:
            try:
                # sdl92.g:630:17: ( ID )
                # sdl92.g:630:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID449=self.match(self.input, ID, self.FOLLOW_ID_in_process_id9526)
                if self._state.backtracking == 0:

                    ID449_tree = self._adaptor.createWithPayload(ID449)
                    self._adaptor.addChild(root_0, ID449_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "process_id"

    class process_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.process_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "process_name"
    # sdl92.g:631:1: process_name : ID ;
    def process_name(self, ):

        retval = self.process_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID450 = None

        ID450_tree = None

        try:
            try:
                # sdl92.g:631:17: ( ID )
                # sdl92.g:631:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID450=self.match(self.input, ID, self.FOLLOW_ID_in_process_name9544)
                if self._state.backtracking == 0:

                    ID450_tree = self._adaptor.createWithPayload(ID450)
                    self._adaptor.addChild(root_0, ID450_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "process_name"

    class priority_signal_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.priority_signal_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "priority_signal_id"
    # sdl92.g:632:1: priority_signal_id : ID ;
    def priority_signal_id(self, ):

        retval = self.priority_signal_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID451 = None

        ID451_tree = None

        try:
            try:
                # sdl92.g:633:17: ( ID )
                # sdl92.g:633:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID451=self.match(self.input, ID, self.FOLLOW_ID_in_priority_signal_id9575)
                if self._state.backtracking == 0:

                    ID451_tree = self._adaptor.createWithPayload(ID451)
                    self._adaptor.addChild(root_0, ID451_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "priority_signal_id"

    class signal_list_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_list_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_list_id"
    # sdl92.g:634:1: signal_list_id : ID ;
    def signal_list_id(self, ):

        retval = self.signal_list_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID452 = None

        ID452_tree = None

        try:
            try:
                # sdl92.g:634:17: ( ID )
                # sdl92.g:634:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID452=self.match(self.input, ID, self.FOLLOW_ID_in_signal_list_id9589)
                if self._state.backtracking == 0:

                    ID452_tree = self._adaptor.createWithPayload(ID452)
                    self._adaptor.addChild(root_0, ID452_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_list_id"

    class timer_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.timer_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "timer_id"
    # sdl92.g:635:1: timer_id : ID ;
    def timer_id(self, ):

        retval = self.timer_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID453 = None

        ID453_tree = None

        try:
            try:
                # sdl92.g:635:17: ( ID )
                # sdl92.g:635:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID453=self.match(self.input, ID, self.FOLLOW_ID_in_timer_id9609)
                if self._state.backtracking == 0:

                    ID453_tree = self._adaptor.createWithPayload(ID453)
                    self._adaptor.addChild(root_0, ID453_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "timer_id"

    class field_name_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.field_name_return, self).__init__()

            self.tree = None




    # $ANTLR start "field_name"
    # sdl92.g:636:1: field_name : ID ;
    def field_name(self, ):

        retval = self.field_name_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID454 = None

        ID454_tree = None

        try:
            try:
                # sdl92.g:636:17: ( ID )
                # sdl92.g:636:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID454=self.match(self.input, ID, self.FOLLOW_ID_in_field_name9627)
                if self._state.backtracking == 0:

                    ID454_tree = self._adaptor.createWithPayload(ID454)
                    self._adaptor.addChild(root_0, ID454_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "field_name"

    class signal_route_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.signal_route_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "signal_route_id"
    # sdl92.g:637:1: signal_route_id : ID ;
    def signal_route_id(self, ):

        retval = self.signal_route_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID455 = None

        ID455_tree = None

        try:
            try:
                # sdl92.g:637:17: ( ID )
                # sdl92.g:637:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID455=self.match(self.input, ID, self.FOLLOW_ID_in_signal_route_id9640)
                if self._state.backtracking == 0:

                    ID455_tree = self._adaptor.createWithPayload(ID455)
                    self._adaptor.addChild(root_0, ID455_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "signal_route_id"

    class channel_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.channel_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "channel_id"
    # sdl92.g:638:1: channel_id : ID ;
    def channel_id(self, ):

        retval = self.channel_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID456 = None

        ID456_tree = None

        try:
            try:
                # sdl92.g:638:17: ( ID )
                # sdl92.g:638:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID456=self.match(self.input, ID, self.FOLLOW_ID_in_channel_id9658)
                if self._state.backtracking == 0:

                    ID456_tree = self._adaptor.createWithPayload(ID456)
                    self._adaptor.addChild(root_0, ID456_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "channel_id"

    class gate_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.gate_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "gate_id"
    # sdl92.g:639:1: gate_id : ID ;
    def gate_id(self, ):

        retval = self.gate_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID457 = None

        ID457_tree = None

        try:
            try:
                # sdl92.g:639:17: ( ID )
                # sdl92.g:639:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID457=self.match(self.input, ID, self.FOLLOW_ID_in_gate_id9679)
                if self._state.backtracking == 0:

                    ID457_tree = self._adaptor.createWithPayload(ID457)
                    self._adaptor.addChild(root_0, ID457_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "gate_id"

    class procedure_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.procedure_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "procedure_id"
    # sdl92.g:640:1: procedure_id : ID ;
    def procedure_id(self, ):

        retval = self.procedure_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID458 = None

        ID458_tree = None

        try:
            try:
                # sdl92.g:640:17: ( ID )
                # sdl92.g:640:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID458=self.match(self.input, ID, self.FOLLOW_ID_in_procedure_id9695)
                if self._state.backtracking == 0:

                    ID458_tree = self._adaptor.createWithPayload(ID458)
                    self._adaptor.addChild(root_0, ID458_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "procedure_id"

    class remote_procedure_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.remote_procedure_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "remote_procedure_id"
    # sdl92.g:641:1: remote_procedure_id : ID ;
    def remote_procedure_id(self, ):

        retval = self.remote_procedure_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID459 = None

        ID459_tree = None

        try:
            try:
                # sdl92.g:642:17: ( ID )
                # sdl92.g:642:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID459=self.match(self.input, ID, self.FOLLOW_ID_in_remote_procedure_id9724)
                if self._state.backtracking == 0:

                    ID459_tree = self._adaptor.createWithPayload(ID459)
                    self._adaptor.addChild(root_0, ID459_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "remote_procedure_id"

    class operator_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.operator_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "operator_id"
    # sdl92.g:643:1: operator_id : ID ;
    def operator_id(self, ):

        retval = self.operator_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID460 = None

        ID460_tree = None

        try:
            try:
                # sdl92.g:643:17: ( ID )
                # sdl92.g:643:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID460=self.match(self.input, ID, self.FOLLOW_ID_in_operator_id9741)
                if self._state.backtracking == 0:

                    ID460_tree = self._adaptor.createWithPayload(ID460)
                    self._adaptor.addChild(root_0, ID460_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "operator_id"

    class synonym_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.synonym_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "synonym_id"
    # sdl92.g:644:1: synonym_id : ID ;
    def synonym_id(self, ):

        retval = self.synonym_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID461 = None

        ID461_tree = None

        try:
            try:
                # sdl92.g:644:17: ( ID )
                # sdl92.g:644:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID461=self.match(self.input, ID, self.FOLLOW_ID_in_synonym_id9759)
                if self._state.backtracking == 0:

                    ID461_tree = self._adaptor.createWithPayload(ID461)
                    self._adaptor.addChild(root_0, ID461_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "synonym_id"

    class external_synonym_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.external_synonym_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "external_synonym_id"
    # sdl92.g:645:1: external_synonym_id : ID ;
    def external_synonym_id(self, ):

        retval = self.external_synonym_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID462 = None

        ID462_tree = None

        try:
            try:
                # sdl92.g:646:17: ( ID )
                # sdl92.g:646:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID462=self.match(self.input, ID, self.FOLLOW_ID_in_external_synonym_id9788)
                if self._state.backtracking == 0:

                    ID462_tree = self._adaptor.createWithPayload(ID462)
                    self._adaptor.addChild(root_0, ID462_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "external_synonym_id"

    class remote_variable_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.remote_variable_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "remote_variable_id"
    # sdl92.g:647:1: remote_variable_id : ID ;
    def remote_variable_id(self, ):

        retval = self.remote_variable_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID463 = None

        ID463_tree = None

        try:
            try:
                # sdl92.g:648:17: ( ID )
                # sdl92.g:648:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID463=self.match(self.input, ID, self.FOLLOW_ID_in_remote_variable_id9817)
                if self._state.backtracking == 0:

                    ID463_tree = self._adaptor.createWithPayload(ID463)
                    self._adaptor.addChild(root_0, ID463_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "remote_variable_id"

    class view_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.view_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "view_id"
    # sdl92.g:649:1: view_id : ID ;
    def view_id(self, ):

        retval = self.view_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID464 = None

        ID464_tree = None

        try:
            try:
                # sdl92.g:649:17: ( ID )
                # sdl92.g:649:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID464=self.match(self.input, ID, self.FOLLOW_ID_in_view_id9838)
                if self._state.backtracking == 0:

                    ID464_tree = self._adaptor.createWithPayload(ID464)
                    self._adaptor.addChild(root_0, ID464_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "view_id"

    class sort_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.sort_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "sort_id"
    # sdl92.g:650:1: sort_id : ID ;
    def sort_id(self, ):

        retval = self.sort_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID465 = None

        ID465_tree = None

        try:
            try:
                # sdl92.g:650:17: ( ID )
                # sdl92.g:650:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID465=self.match(self.input, ID, self.FOLLOW_ID_in_sort_id9859)
                if self._state.backtracking == 0:

                    ID465_tree = self._adaptor.createWithPayload(ID465)
                    self._adaptor.addChild(root_0, ID465_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "sort_id"

    class syntype_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.syntype_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "syntype_id"
    # sdl92.g:651:1: syntype_id : ID ;
    def syntype_id(self, ):

        retval = self.syntype_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID466 = None

        ID466_tree = None

        try:
            try:
                # sdl92.g:651:17: ( ID )
                # sdl92.g:651:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID466=self.match(self.input, ID, self.FOLLOW_ID_in_syntype_id9877)
                if self._state.backtracking == 0:

                    ID466_tree = self._adaptor.createWithPayload(ID466)
                    self._adaptor.addChild(root_0, ID466_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "syntype_id"

    class stimulus_id_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.stimulus_id_return, self).__init__()

            self.tree = None




    # $ANTLR start "stimulus_id"
    # sdl92.g:652:1: stimulus_id : ID ;
    def stimulus_id(self, ):

        retval = self.stimulus_id_return()
        retval.start = self.input.LT(1)

        root_0 = None

        ID467 = None

        ID467_tree = None

        try:
            try:
                # sdl92.g:652:17: ( ID )
                # sdl92.g:652:25: ID
                pass 
                root_0 = self._adaptor.nil()

                ID467=self.match(self.input, ID, self.FOLLOW_ID_in_stimulus_id9894)
                if self._state.backtracking == 0:

                    ID467_tree = self._adaptor.createWithPayload(ID467)
                    self._adaptor.addChild(root_0, ID467_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "stimulus_id"

    class pid_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.pid_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "pid_expression"
    # sdl92.g:682:1: pid_expression : ( S E L F | P A R E N T | O F F S P R I N G | S E N D E R );
    def pid_expression(self, ):

        retval = self.pid_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        S468 = None
        E469 = None
        L470 = None
        F471 = None
        P472 = None
        A473 = None
        R474 = None
        E475 = None
        N476 = None
        T477 = None
        O478 = None
        F479 = None
        F480 = None
        S481 = None
        P482 = None
        R483 = None
        I484 = None
        N485 = None
        G486 = None
        S487 = None
        E488 = None
        N489 = None
        D490 = None
        E491 = None
        R492 = None

        S468_tree = None
        E469_tree = None
        L470_tree = None
        F471_tree = None
        P472_tree = None
        A473_tree = None
        R474_tree = None
        E475_tree = None
        N476_tree = None
        T477_tree = None
        O478_tree = None
        F479_tree = None
        F480_tree = None
        S481_tree = None
        P482_tree = None
        R483_tree = None
        I484_tree = None
        N485_tree = None
        G486_tree = None
        S487_tree = None
        E488_tree = None
        N489_tree = None
        D490_tree = None
        E491_tree = None
        R492_tree = None

        try:
            try:
                # sdl92.g:682:17: ( S E L F | P A R E N T | O F F S P R I N G | S E N D E R )
                alt119 = 4
                LA119 = self.input.LA(1)
                if LA119 == S:
                    LA119_1 = self.input.LA(2)

                    if (LA119_1 == E) :
                        LA119_4 = self.input.LA(3)

                        if (LA119_4 == L) :
                            alt119 = 1
                        elif (LA119_4 == N) :
                            alt119 = 4
                        else:
                            if self._state.backtracking > 0:
                                raise BacktrackingFailed

                            nvae = NoViableAltException("", 119, 4, self.input)

                            raise nvae

                    else:
                        if self._state.backtracking > 0:
                            raise BacktrackingFailed

                        nvae = NoViableAltException("", 119, 1, self.input)

                        raise nvae

                elif LA119 == P:
                    alt119 = 2
                elif LA119 == O:
                    alt119 = 3
                else:
                    if self._state.backtracking > 0:
                        raise BacktrackingFailed

                    nvae = NoViableAltException("", 119, 0, self.input)

                    raise nvae

                if alt119 == 1:
                    # sdl92.g:682:25: S E L F
                    pass 
                    root_0 = self._adaptor.nil()

                    S468=self.match(self.input, S, self.FOLLOW_S_in_pid_expression10750)
                    if self._state.backtracking == 0:

                        S468_tree = self._adaptor.createWithPayload(S468)
                        self._adaptor.addChild(root_0, S468_tree)

                    E469=self.match(self.input, E, self.FOLLOW_E_in_pid_expression10752)
                    if self._state.backtracking == 0:

                        E469_tree = self._adaptor.createWithPayload(E469)
                        self._adaptor.addChild(root_0, E469_tree)

                    L470=self.match(self.input, L, self.FOLLOW_L_in_pid_expression10754)
                    if self._state.backtracking == 0:

                        L470_tree = self._adaptor.createWithPayload(L470)
                        self._adaptor.addChild(root_0, L470_tree)

                    F471=self.match(self.input, F, self.FOLLOW_F_in_pid_expression10756)
                    if self._state.backtracking == 0:

                        F471_tree = self._adaptor.createWithPayload(F471)
                        self._adaptor.addChild(root_0, F471_tree)



                elif alt119 == 2:
                    # sdl92.g:682:35: P A R E N T
                    pass 
                    root_0 = self._adaptor.nil()

                    P472=self.match(self.input, P, self.FOLLOW_P_in_pid_expression10760)
                    if self._state.backtracking == 0:

                        P472_tree = self._adaptor.createWithPayload(P472)
                        self._adaptor.addChild(root_0, P472_tree)

                    A473=self.match(self.input, A, self.FOLLOW_A_in_pid_expression10762)
                    if self._state.backtracking == 0:

                        A473_tree = self._adaptor.createWithPayload(A473)
                        self._adaptor.addChild(root_0, A473_tree)

                    R474=self.match(self.input, R, self.FOLLOW_R_in_pid_expression10764)
                    if self._state.backtracking == 0:

                        R474_tree = self._adaptor.createWithPayload(R474)
                        self._adaptor.addChild(root_0, R474_tree)

                    E475=self.match(self.input, E, self.FOLLOW_E_in_pid_expression10766)
                    if self._state.backtracking == 0:

                        E475_tree = self._adaptor.createWithPayload(E475)
                        self._adaptor.addChild(root_0, E475_tree)

                    N476=self.match(self.input, N, self.FOLLOW_N_in_pid_expression10768)
                    if self._state.backtracking == 0:

                        N476_tree = self._adaptor.createWithPayload(N476)
                        self._adaptor.addChild(root_0, N476_tree)

                    T477=self.match(self.input, T, self.FOLLOW_T_in_pid_expression10770)
                    if self._state.backtracking == 0:

                        T477_tree = self._adaptor.createWithPayload(T477)
                        self._adaptor.addChild(root_0, T477_tree)



                elif alt119 == 3:
                    # sdl92.g:682:49: O F F S P R I N G
                    pass 
                    root_0 = self._adaptor.nil()

                    O478=self.match(self.input, O, self.FOLLOW_O_in_pid_expression10774)
                    if self._state.backtracking == 0:

                        O478_tree = self._adaptor.createWithPayload(O478)
                        self._adaptor.addChild(root_0, O478_tree)

                    F479=self.match(self.input, F, self.FOLLOW_F_in_pid_expression10776)
                    if self._state.backtracking == 0:

                        F479_tree = self._adaptor.createWithPayload(F479)
                        self._adaptor.addChild(root_0, F479_tree)

                    F480=self.match(self.input, F, self.FOLLOW_F_in_pid_expression10778)
                    if self._state.backtracking == 0:

                        F480_tree = self._adaptor.createWithPayload(F480)
                        self._adaptor.addChild(root_0, F480_tree)

                    S481=self.match(self.input, S, self.FOLLOW_S_in_pid_expression10780)
                    if self._state.backtracking == 0:

                        S481_tree = self._adaptor.createWithPayload(S481)
                        self._adaptor.addChild(root_0, S481_tree)

                    P482=self.match(self.input, P, self.FOLLOW_P_in_pid_expression10782)
                    if self._state.backtracking == 0:

                        P482_tree = self._adaptor.createWithPayload(P482)
                        self._adaptor.addChild(root_0, P482_tree)

                    R483=self.match(self.input, R, self.FOLLOW_R_in_pid_expression10784)
                    if self._state.backtracking == 0:

                        R483_tree = self._adaptor.createWithPayload(R483)
                        self._adaptor.addChild(root_0, R483_tree)

                    I484=self.match(self.input, I, self.FOLLOW_I_in_pid_expression10786)
                    if self._state.backtracking == 0:

                        I484_tree = self._adaptor.createWithPayload(I484)
                        self._adaptor.addChild(root_0, I484_tree)

                    N485=self.match(self.input, N, self.FOLLOW_N_in_pid_expression10788)
                    if self._state.backtracking == 0:

                        N485_tree = self._adaptor.createWithPayload(N485)
                        self._adaptor.addChild(root_0, N485_tree)

                    G486=self.match(self.input, G, self.FOLLOW_G_in_pid_expression10790)
                    if self._state.backtracking == 0:

                        G486_tree = self._adaptor.createWithPayload(G486)
                        self._adaptor.addChild(root_0, G486_tree)



                elif alt119 == 4:
                    # sdl92.g:682:69: S E N D E R
                    pass 
                    root_0 = self._adaptor.nil()

                    S487=self.match(self.input, S, self.FOLLOW_S_in_pid_expression10794)
                    if self._state.backtracking == 0:

                        S487_tree = self._adaptor.createWithPayload(S487)
                        self._adaptor.addChild(root_0, S487_tree)

                    E488=self.match(self.input, E, self.FOLLOW_E_in_pid_expression10796)
                    if self._state.backtracking == 0:

                        E488_tree = self._adaptor.createWithPayload(E488)
                        self._adaptor.addChild(root_0, E488_tree)

                    N489=self.match(self.input, N, self.FOLLOW_N_in_pid_expression10798)
                    if self._state.backtracking == 0:

                        N489_tree = self._adaptor.createWithPayload(N489)
                        self._adaptor.addChild(root_0, N489_tree)

                    D490=self.match(self.input, D, self.FOLLOW_D_in_pid_expression10800)
                    if self._state.backtracking == 0:

                        D490_tree = self._adaptor.createWithPayload(D490)
                        self._adaptor.addChild(root_0, D490_tree)

                    E491=self.match(self.input, E, self.FOLLOW_E_in_pid_expression10802)
                    if self._state.backtracking == 0:

                        E491_tree = self._adaptor.createWithPayload(E491)
                        self._adaptor.addChild(root_0, E491_tree)

                    R492=self.match(self.input, R, self.FOLLOW_R_in_pid_expression10804)
                    if self._state.backtracking == 0:

                        R492_tree = self._adaptor.createWithPayload(R492)
                        self._adaptor.addChild(root_0, R492_tree)



                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "pid_expression"

    class now_expression_return(ParserRuleReturnScope):
        def __init__(self):
            super(sdl92Parser.now_expression_return, self).__init__()

            self.tree = None




    # $ANTLR start "now_expression"
    # sdl92.g:683:1: now_expression : N O W ;
    def now_expression(self, ):

        retval = self.now_expression_return()
        retval.start = self.input.LT(1)

        root_0 = None

        N493 = None
        O494 = None
        W495 = None

        N493_tree = None
        O494_tree = None
        W495_tree = None

        try:
            try:
                # sdl92.g:683:17: ( N O W )
                # sdl92.g:683:25: N O W
                pass 
                root_0 = self._adaptor.nil()

                N493=self.match(self.input, N, self.FOLLOW_N_in_now_expression10819)
                if self._state.backtracking == 0:

                    N493_tree = self._adaptor.createWithPayload(N493)
                    self._adaptor.addChild(root_0, N493_tree)

                O494=self.match(self.input, O, self.FOLLOW_O_in_now_expression10821)
                if self._state.backtracking == 0:

                    O494_tree = self._adaptor.createWithPayload(O494)
                    self._adaptor.addChild(root_0, O494_tree)

                W495=self.match(self.input, W, self.FOLLOW_W_in_now_expression10823)
                if self._state.backtracking == 0:

                    W495_tree = self._adaptor.createWithPayload(W495)
                    self._adaptor.addChild(root_0, W495_tree)




                retval.stop = self.input.LT(-1)

                if self._state.backtracking == 0:

                    retval.tree = self._adaptor.rulePostProcessing(root_0)
                    self._adaptor.setTokenBoundaries(retval.tree, retval.start, retval.stop)


            except RecognitionException, re:
                self.reportError(re)
                self.recover(self.input, re)
                retval.tree = self._adaptor.errorNode(self.input, retval.start, self.input.LT(-1), re)
        finally:

            pass
        return retval

    # $ANTLR end "now_expression"

    # $ANTLR start "synpred4_sdl92"
    def synpred4_sdl92_fragment(self, ):
        # sdl92.g:101:17: ( content )
        # sdl92.g:101:17: content
        pass 
        self._state.following.append(self.FOLLOW_content_in_synpred4_sdl921009)
        self.content()

        self._state.following.pop()


    # $ANTLR end "synpred4_sdl92"



    # $ANTLR start "synpred32_sdl92"
    def synpred32_sdl92_fragment(self, ):
        # sdl92.g:206:17: ( enabling_condition )
        # sdl92.g:206:17: enabling_condition
        pass 
        self._state.following.append(self.FOLLOW_enabling_condition_in_synpred32_sdl922603)
        self.enabling_condition()

        self._state.following.pop()


    # $ANTLR end "synpred32_sdl92"



    # $ANTLR start "synpred61_sdl92"
    def synpred61_sdl92_fragment(self, ):
        # sdl92.g:289:17: ( expression )
        # sdl92.g:289:17: expression
        pass 
        self._state.following.append(self.FOLLOW_expression_in_synpred61_sdl924003)
        self.expression()

        self._state.following.pop()


    # $ANTLR end "synpred61_sdl92"



    # $ANTLR start "synpred64_sdl92"
    def synpred64_sdl92_fragment(self, ):
        # sdl92.g:296:17: ( answer_part )
        # sdl92.g:296:17: answer_part
        pass 
        self._state.following.append(self.FOLLOW_answer_part_in_synpred64_sdl924111)
        self.answer_part()

        self._state.following.pop()


    # $ANTLR end "synpred64_sdl92"



    # $ANTLR start "synpred69_sdl92"
    def synpred69_sdl92_fragment(self, ):
        # sdl92.g:306:17: ( range_condition )
        # sdl92.g:306:17: range_condition
        pass 
        self._state.following.append(self.FOLLOW_range_condition_in_synpred69_sdl924341)
        self.range_condition()

        self._state.following.pop()


    # $ANTLR end "synpred69_sdl92"



    # $ANTLR start "synpred73_sdl92"
    def synpred73_sdl92_fragment(self, ):
        # sdl92.g:315:17: ( expression )
        # sdl92.g:315:17: expression
        pass 
        self._state.following.append(self.FOLLOW_expression_in_synpred73_sdl924509)
        self.expression()

        self._state.following.pop()


    # $ANTLR end "synpred73_sdl92"



    # $ANTLR start "synpred74_sdl92"
    def synpred74_sdl92_fragment(self, ):
        # sdl92.g:316:19: ( informal_text )
        # sdl92.g:316:19: informal_text
        pass 
        self._state.following.append(self.FOLLOW_informal_text_in_synpred74_sdl924571)
        self.informal_text()

        self._state.following.pop()


    # $ANTLR end "synpred74_sdl92"



    # $ANTLR start "synpred99_sdl92"
    def synpred99_sdl92_fragment(self, ):
        # sdl92.g:416:36: ( IMPLIES operand0 )
        # sdl92.g:416:36: IMPLIES operand0
        pass 
        self.match(self.input, IMPLIES, self.FOLLOW_IMPLIES_in_synpred99_sdl926097)
        self._state.following.append(self.FOLLOW_operand0_in_synpred99_sdl926100)
        self.operand0()

        self._state.following.pop()


    # $ANTLR end "synpred99_sdl92"



    # $ANTLR start "synpred101_sdl92"
    def synpred101_sdl92_fragment(self, ):
        # sdl92.g:417:35: ( ( OR | XOR ) operand1 )
        # sdl92.g:417:35: ( OR | XOR ) operand1
        pass 
        if (OR <= self.input.LA(1) <= XOR):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_operand1_in_synpred101_sdl926138)
        self.operand1()

        self._state.following.pop()


    # $ANTLR end "synpred101_sdl92"



    # $ANTLR start "synpred102_sdl92"
    def synpred102_sdl92_fragment(self, ):
        # sdl92.g:418:36: ( AND operand2 )
        # sdl92.g:418:36: AND operand2
        pass 
        self.match(self.input, AND, self.FOLLOW_AND_in_synpred102_sdl926164)
        self._state.following.append(self.FOLLOW_operand2_in_synpred102_sdl926167)
        self.operand2()

        self._state.following.pop()


    # $ANTLR end "synpred102_sdl92"



    # $ANTLR start "synpred109_sdl92"
    def synpred109_sdl92_fragment(self, ):
        # sdl92.g:419:35: ( ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3 )
        # sdl92.g:419:35: ( EQ | NEQ | GT | GE | LT | LE | IN ) operand3
        pass 
        if (EQ <= self.input.LA(1) <= GE) or self.input.LA(1) == IN:
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_operand3_in_synpred109_sdl926229)
        self.operand3()

        self._state.following.pop()


    # $ANTLR end "synpred109_sdl92"



    # $ANTLR start "synpred112_sdl92"
    def synpred112_sdl92_fragment(self, ):
        # sdl92.g:420:35: ( ( PLUS | DASH | APPEND ) operand4 )
        # sdl92.g:420:35: ( PLUS | DASH | APPEND ) operand4
        pass 
        if (PLUS <= self.input.LA(1) <= APPEND):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_operand4_in_synpred112_sdl926271)
        self.operand4()

        self._state.following.pop()


    # $ANTLR end "synpred112_sdl92"



    # $ANTLR start "synpred116_sdl92"
    def synpred116_sdl92_fragment(self, ):
        # sdl92.g:421:35: ( ( ASTERISK | DIV | MOD | REM ) operand5 )
        # sdl92.g:421:35: ( ASTERISK | DIV | MOD | REM ) operand5
        pass 
        if self.input.LA(1) == ASTERISK or (DIV <= self.input.LA(1) <= REM):
            self.input.consume()
            self._state.errorRecovery = False

        else:
            if self._state.backtracking > 0:
                raise BacktrackingFailed

            mse = MismatchedSetException(None, self.input)
            raise mse


        self._state.following.append(self.FOLLOW_operand5_in_synpred116_sdl926318)
        self.operand5()

        self._state.following.pop()


    # $ANTLR end "synpred116_sdl92"



    # $ANTLR start "synpred118_sdl92"
    def synpred118_sdl92_fragment(self, ):
        # sdl92.g:426:29: ( primary_params )
        # sdl92.g:426:29: primary_params
        pass 
        self._state.following.append(self.FOLLOW_primary_params_in_synpred118_sdl926388)
        self.primary_params()

        self._state.following.pop()


    # $ANTLR end "synpred118_sdl92"




    # Delegated rules

    def synpred116_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred116_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred109_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred109_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred61_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred61_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred102_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred102_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred4_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred4_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred32_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred32_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred99_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred99_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred64_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred64_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred69_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred69_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred118_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred118_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred73_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred73_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred101_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred101_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred74_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred74_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success

    def synpred112_sdl92(self):
        self._state.backtracking += 1
        start = self.input.mark()
        try:
            self.synpred112_sdl92_fragment()
        except BacktrackingFailed:
            success = False
        else:
            success = True
        self.input.rewind(start)
        self._state.backtracking -= 1
        return success



    # lookup tables for DFA #2

    DFA2_eot = DFA.unpack(
        u"\22\uffff"
        )

    DFA2_eof = DFA.unpack(
        u"\22\uffff"
        )

    DFA2_min = DFA.unpack(
        u"\1\27\1\4\1\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1\125\1\117"
        u"\1\127\1\117\1\126\1\u00b1\1\27\1\uffff\1\23"
        )

    DFA2_max = DFA.unpack(
        u"\1\u00b0\1\u0084\1\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1"
        u"\125\1\117\1\127\1\117\1\126\1\u00b1\1\u00b0\1\uffff\1\u0081"
        )

    DFA2_accept = DFA.unpack(
        u"\2\uffff\1\2\15\uffff\1\1\1\uffff"
        )

    DFA2_special = DFA.unpack(
        u"\22\uffff"
        )

            
    DFA2_transition = [
        DFA.unpack(u"\1\2\66\uffff\1\2\1\uffff\1\2\137\uffff\1\1"),
        DFA.unpack(u"\1\3\1\uffff\1\3\20\uffff\1\3\2\uffff\1\3\1\uffff\1"
        u"\3\6\uffff\1\3\1\uffff\1\3\10\uffff\1\3\2\uffff\3\3\27\uffff\1"
        u"\3\4\uffff\1\3\60\uffff\1\2\2\uffff\1\3"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\4"),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\56\uffff\1\20\11\uffff\1\2\137\uffff\1\21"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\20\155\uffff\1\2")
    ]

    # class definition for DFA #2

    class DFA2(DFA):
        pass


    # lookup tables for DFA #9

    DFA9_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA9_eof = DFA.unpack(
        u"\30\uffff"
        )

    DFA9_min = DFA.unpack(
        u"\1\27\1\4\2\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77\1\117"
        u"\1\164\1\126\1\u00b1\1\127\1\27\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\27\1\u0081"
        )

    DFA9_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77"
        u"\1\117\1\164\1\126\1\u00b1\1\127\1\120\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA9_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA9_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA9_transition = [
        DFA.unpack(u"\1\3\66\uffff\1\3\1\uffff\1\2\137\uffff\1\1"),
        DFA.unpack(u"\1\4\1\uffff\1\4\20\uffff\1\4\2\uffff\1\4\1\uffff\1"
        u"\4\6\uffff\1\4\1\uffff\1\4\10\uffff\1\4\2\uffff\3\4\27\uffff\1"
        u"\4\4\uffff\1\4\60\uffff\1\5\2\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\3\70\uffff\1\2"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\70\uffff\1\2\137\uffff\1\27"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #9

    class DFA9(DFA):
        pass


    # lookup tables for DFA #21

    DFA21_eot = DFA.unpack(
        u"\33\uffff"
        )

    DFA21_eof = DFA.unpack(
        u"\33\uffff"
        )

    DFA21_min = DFA.unpack(
        u"\1\31\1\4\1\122\2\uffff\1\u0082\1\125\2\uffff\1\u0083\1\117\1\77"
        u"\1\127\1\164\1\117\1\u00b1\1\126\1\34\1\127\1\125\1\117\1\127\1"
        u"\117\1\126\1\u00b1\1\34\1\u0081"
        )

    DFA21_max = DFA.unpack(
        u"\1\u00b0\1\u0084\1\144\2\uffff\1\u0082\1\125\2\uffff\1\u0083\1"
        u"\117\1\77\1\127\1\164\1\117\1\u00b1\1\126\1\34\1\127\1\125\1\117"
        u"\1\127\1\117\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA21_accept = DFA.unpack(
        u"\3\uffff\1\2\1\4\2\uffff\1\3\1\1\22\uffff"
        )

    DFA21_special = DFA.unpack(
        u"\33\uffff"
        )

            
    DFA21_transition = [
        DFA.unpack(u"\1\3\1\4\1\uffff\1\2\u0093\uffff\1\1"),
        DFA.unpack(u"\1\6\1\uffff\1\6\20\uffff\1\6\2\uffff\1\6\1\uffff\1"
        u"\6\6\uffff\1\6\1\uffff\1\6\10\uffff\1\6\2\uffff\3\6\27\uffff\1"
        u"\6\4\uffff\1\6\60\uffff\1\5\2\uffff\1\6"),
        DFA.unpack(u"\1\10\1\7\20\uffff\1\10"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\2"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\2\u0093\uffff\1\32"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #21

    class DFA21(DFA):
        pass


    # lookup tables for DFA #30

    DFA30_eot = DFA.unpack(
        u"\26\uffff"
        )

    DFA30_eof = DFA.unpack(
        u"\1\2\25\uffff"
        )

    DFA30_min = DFA.unpack(
        u"\1\31\1\0\24\uffff"
        )

    DFA30_max = DFA.unpack(
        u"\1\u00b0\1\0\24\uffff"
        )

    DFA30_accept = DFA.unpack(
        u"\2\uffff\1\2\22\uffff\1\1"
        )

    DFA30_special = DFA.unpack(
        u"\1\uffff\1\0\24\uffff"
        )

            
    DFA30_transition = [
        DFA.unpack(u"\1\2\1\1\1\uffff\1\2\3\uffff\5\2\11\uffff\1\2\3\uffff"
        u"\2\2\1\uffff\1\2\25\uffff\1\2\5\uffff\1\2\6\uffff\1\2\11\uffff"
        u"\1\2\1\uffff\1\2\32\uffff\1\2\60\uffff\1\2"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #30

    class DFA30(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA30_1 = input.LA(1)

                 
                index30_1 = input.index()
                input.rewind()
                s = -1
                if (self.synpred32_sdl92()):
                    s = 21

                elif (True):
                    s = 2

                 
                input.seek(index30_1)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 30, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #31

    DFA31_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA31_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA31_min = DFA.unpack(
        u"\1\31\1\4\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127\1\164"
        u"\1\117\1\u00b1\1\126\1\34\1\127\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\34\1\u0081"
        )

    DFA31_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127"
        u"\1\164\1\117\1\u00b1\1\126\1\177\1\127\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA31_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA31_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA31_transition = [
        DFA.unpack(u"\2\3\1\uffff\1\3\3\uffff\5\2\11\uffff\1\2\3\uffff\2"
        u"\2\1\uffff\1\2\25\uffff\1\2\5\uffff\1\3\6\uffff\1\2\11\uffff\1"
        u"\2\1\uffff\1\2\32\uffff\1\2\60\uffff\1\1"),
        DFA.unpack(u"\1\5\1\uffff\1\5\20\uffff\1\5\2\uffff\1\5\1\uffff\1"
        u"\5\6\uffff\1\5\1\uffff\1\5\10\uffff\1\5\2\uffff\3\5\27\uffff\1"
        u"\5\4\uffff\1\5\60\uffff\1\4\2\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\6\uffff\1\2\12\uffff\1\2\3\uffff\2\2\1\uffff\1"
        u"\2\25\uffff\1\2\14\uffff\1\2\46\uffff\1\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\6\uffff\1\2\12\uffff\1\2\3\uffff\2\2\1\uffff\1"
        u"\2\25\uffff\1\2\14\uffff\1\2\13\uffff\1\2\32\uffff\1\2\60\uffff"
        u"\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #31

    class DFA31(DFA):
        pass


    # lookup tables for DFA #38

    DFA38_eot = DFA.unpack(
        u"\50\uffff"
        )

    DFA38_eof = DFA.unpack(
        u"\50\uffff"
        )

    DFA38_min = DFA.unpack(
        u"\1\40\1\4\1\u00a6\2\uffff\1\125\1\u0082\1\40\1\117\1\u0083\1\4"
        u"\1\127\1\77\1\125\1\117\1\164\1\117\1\126\1\u00b1\2\127\1\43\1"
        u"\117\1\125\1\126\1\117\2\127\1\125\2\117\1\126\1\127\1\u00b1\1"
        u"\117\1\43\1\126\1\u0081\1\u00b1\1\43"
        )

    DFA38_max = DFA.unpack(
        u"\1\u00b0\1\u0084\1\u00a6\2\uffff\1\125\1\u0082\1\u00b0\1\117\1"
        u"\u0083\1\u0084\1\127\1\77\1\125\1\117\1\164\1\117\1\126\1\u00b1"
        u"\2\127\1\177\1\117\1\125\1\126\1\117\2\127\1\125\2\117\1\126\1"
        u"\127\1\u00b1\1\117\1\u00b0\1\126\1\u0081\1\u00b1\1\u00b0"
        )

    DFA38_accept = DFA.unpack(
        u"\3\uffff\1\1\1\2\43\uffff"
        )

    DFA38_special = DFA.unpack(
        u"\50\uffff"
        )

            
    DFA38_transition = [
        DFA.unpack(u"\5\3\11\uffff\1\3\3\uffff\2\4\1\uffff\1\4\25\uffff\1"
        u"\3\14\uffff\1\3\11\uffff\1\3\1\uffff\1\2\32\uffff\1\4\60\uffff"
        u"\1\1"),
        DFA.unpack(u"\1\5\1\uffff\1\5\20\uffff\1\5\2\uffff\1\5\1\uffff\1"
        u"\5\6\uffff\1\5\1\uffff\1\5\10\uffff\1\5\2\uffff\3\5\27\uffff\1"
        u"\5\4\uffff\1\5\60\uffff\1\6\2\uffff\1\5"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\5\3\11\uffff\1\3\3\uffff\2\4\1\uffff\1\4\25\uffff"
        u"\1\3\14\uffff\1\3\11\uffff\1\3\34\uffff\1\4\60\uffff\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15\1\uffff\1\15\20\uffff\1\15\2\uffff\1\15\1\uffff"
        u"\1\15\6\uffff\1\15\1\uffff\1\15\10\uffff\1\15\2\uffff\3\15\27\uffff"
        u"\1\15\4\uffff\1\15\60\uffff\1\6\2\uffff\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\3\12\uffff\1\3\3\uffff\2\4\1\uffff\1\4\25\uffff"
        u"\1\3\14\uffff\1\3\46\uffff\1\4"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\37"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u"\1\43"),
        DFA.unpack(u"\1\44"),
        DFA.unpack(u"\1\3\12\uffff\1\3\3\uffff\2\4\1\uffff\1\4\25\uffff"
        u"\1\3\14\uffff\1\3\13\uffff\1\2\32\uffff\1\4\60\uffff\1\45"),
        DFA.unpack(u"\1\46"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\47"),
        DFA.unpack(u"\1\3\12\uffff\1\3\3\uffff\2\4\1\uffff\1\4\25\uffff"
        u"\1\3\14\uffff\1\3\46\uffff\1\4\60\uffff\1\45")
    ]

    # class definition for DFA #38

    class DFA38(DFA):
        pass


    # lookup tables for DFA #36

    DFA36_eot = DFA.unpack(
        u"\57\uffff"
        )

    DFA36_eof = DFA.unpack(
        u"\1\3\56\uffff"
        )

    DFA36_min = DFA.unpack(
        u"\1\27\1\4\1\u00a6\2\uffff\1\u0082\1\125\1\40\1\u0083\1\117\1\4"
        u"\1\77\1\127\1\125\1\u0082\1\164\2\117\1\u0083\1\u00b1\1\126\1\127"
        u"\1\77\1\27\1\127\1\117\1\164\1\125\1\126\1\u00b1\1\117\1\127\1"
        u"\43\1\127\1\125\2\117\1\126\1\127\1\u00b1\1\117\1\27\1\126\1\u0081"
        u"\1\u00b1\1\43\1\u0081"
        )

    DFA36_max = DFA.unpack(
        u"\1\u00b0\1\u0084\1\u00a6\2\uffff\1\u0082\1\125\1\u00b0\1\u0083"
        u"\1\117\1\u0084\1\77\1\127\1\125\1\u0082\1\164\2\117\1\u0083\1\u00b1"
        u"\1\126\1\127\1\77\1\177\1\127\1\117\1\164\1\125\1\126\1\u00b1\1"
        u"\117\1\127\1\177\1\127\1\125\2\117\1\126\1\127\1\u00b1\1\117\1"
        u"\u00b0\1\126\1\u0081\1\u00b1\1\u00b0\1\u0081"
        )

    DFA36_accept = DFA.unpack(
        u"\3\uffff\1\2\1\1\52\uffff"
        )

    DFA36_special = DFA.unpack(
        u"\57\uffff"
        )

            
    DFA36_transition = [
        DFA.unpack(u"\1\3\1\uffff\2\3\1\uffff\1\3\3\uffff\5\4\4\uffff\1\3"
        u"\4\uffff\1\4\3\uffff\2\3\1\uffff\1\3\25\uffff\1\4\2\uffff\1\3\2"
        u"\uffff\1\3\3\uffff\1\3\2\uffff\1\4\2\3\7\uffff\1\4\1\uffff\1\2"
        u"\32\uffff\1\3\60\uffff\1\1"),
        DFA.unpack(u"\1\6\1\uffff\1\6\20\uffff\1\6\2\uffff\1\6\1\uffff\1"
        u"\6\6\uffff\1\6\1\uffff\1\6\10\uffff\1\6\2\uffff\3\6\27\uffff\1"
        u"\6\4\uffff\1\6\60\uffff\1\5\2\uffff\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\5\4\11\uffff\1\4\3\uffff\2\3\1\uffff\1\3\25\uffff"
        u"\1\4\14\uffff\1\4\11\uffff\1\4\34\uffff\1\3\60\uffff\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15\1\uffff\1\15\20\uffff\1\15\2\uffff\1\15\1\uffff"
        u"\1\15\6\uffff\1\15\1\uffff\1\15\10\uffff\1\15\2\uffff\3\15\27\uffff"
        u"\1\15\4\uffff\1\15\60\uffff\1\16\2\uffff\1\15"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\3\4\uffff\1\3\6\uffff\1\4\5\uffff\1\3\4\uffff\1"
        u"\4\3\uffff\2\3\1\uffff\1\3\25\uffff\1\4\11\uffff\1\3\2\uffff\1"
        u"\4\46\uffff\1\3"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\36"),
        DFA.unpack(u"\1\37"),
        DFA.unpack(u"\1\40"),
        DFA.unpack(u"\1\41"),
        DFA.unpack(u"\1\42"),
        DFA.unpack(u"\1\4\12\uffff\1\4\3\uffff\2\3\1\uffff\1\3\25\uffff"
        u"\1\4\14\uffff\1\4\46\uffff\1\3"),
        DFA.unpack(u"\1\43"),
        DFA.unpack(u"\1\44"),
        DFA.unpack(u"\1\45"),
        DFA.unpack(u"\1\46"),
        DFA.unpack(u"\1\47"),
        DFA.unpack(u"\1\50"),
        DFA.unpack(u"\1\51"),
        DFA.unpack(u"\1\52"),
        DFA.unpack(u"\1\3\4\uffff\1\3\6\uffff\1\4\5\uffff\1\3\4\uffff\1"
        u"\4\3\uffff\2\3\1\uffff\1\3\25\uffff\1\4\11\uffff\1\3\2\uffff\1"
        u"\4\13\uffff\1\2\32\uffff\1\3\60\uffff\1\53"),
        DFA.unpack(u"\1\54"),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u"\1\55"),
        DFA.unpack(u"\1\4\12\uffff\1\4\3\uffff\2\3\1\uffff\1\3\25\uffff"
        u"\1\4\14\uffff\1\4\46\uffff\1\3\60\uffff\1\56"),
        DFA.unpack(u"\1\16")
    ]

    # class definition for DFA #36

    class DFA36(DFA):
        pass


    # lookup tables for DFA #37

    DFA37_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA37_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA37_min = DFA.unpack(
        u"\1\27\1\4\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127\1\164"
        u"\1\117\1\u00b1\1\126\1\27\1\127\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\27\1\u0081"
        )

    DFA37_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127"
        u"\1\164\1\117\1\u00b1\1\126\1\177\1\127\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA37_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA37_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA37_transition = [
        DFA.unpack(u"\1\3\1\uffff\2\3\1\uffff\1\3\14\uffff\1\3\10\uffff\2"
        u"\2\1\uffff\1\2\30\uffff\1\3\2\uffff\1\3\3\uffff\1\3\3\uffff\2\3"
        u"\11\uffff\1\2\32\uffff\1\2\60\uffff\1\1"),
        DFA.unpack(u"\1\5\1\uffff\1\5\20\uffff\1\5\2\uffff\1\5\1\uffff\1"
        u"\5\6\uffff\1\5\1\uffff\1\5\10\uffff\1\5\2\uffff\3\5\27\uffff\1"
        u"\5\4\uffff\1\5\60\uffff\1\4\2\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\3\4\uffff\1\3\14\uffff\1\3\10\uffff\2\2\1\uffff"
        u"\1\2\37\uffff\1\3\51\uffff\1\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\4\uffff\1\3\14\uffff\1\3\10\uffff\2\2\1\uffff"
        u"\1\2\37\uffff\1\3\16\uffff\1\2\32\uffff\1\2\60\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #37

    class DFA37(DFA):
        pass


    # lookup tables for DFA #39

    DFA39_eot = DFA.unpack(
        u"\21\uffff"
        )

    DFA39_eof = DFA.unpack(
        u"\21\uffff"
        )

    DFA39_min = DFA.unpack(
        u"\1\40\1\4\2\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1\125\1\117"
        u"\1\127\1\117\1\126\1\u00b1\1\43"
        )

    DFA39_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1"
        u"\125\1\117\1\127\1\117\1\126\1\u00b1\1\u00b0"
        )

    DFA39_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\15\uffff"
        )

    DFA39_special = DFA.unpack(
        u"\21\uffff"
        )

            
    DFA39_transition = [
        DFA.unpack(u"\5\3\11\uffff\1\3\34\uffff\1\3\14\uffff\1\3\11\uffff"
        u"\1\3\1\uffff\1\2\113\uffff\1\1"),
        DFA.unpack(u"\1\4\1\uffff\1\4\20\uffff\1\4\2\uffff\1\4\1\uffff\1"
        u"\4\6\uffff\1\4\1\uffff\1\4\10\uffff\1\4\2\uffff\3\4\27\uffff\1"
        u"\4\4\uffff\1\4\60\uffff\1\3\2\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\3\12\uffff\1\3\34\uffff\1\3\14\uffff\1\3\13\uffff"
        u"\1\2\113\uffff\1\3")
    ]

    # class definition for DFA #39

    class DFA39(DFA):
        pass


    # lookup tables for DFA #40

    DFA40_eot = DFA.unpack(
        u"\37\uffff"
        )

    DFA40_eof = DFA.unpack(
        u"\37\uffff"
        )

    DFA40_min = DFA.unpack(
        u"\1\40\1\4\11\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77\1\117"
        u"\1\164\1\126\1\u00b1\1\127\1\43\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\43\1\u0081"
        )

    DFA40_max = DFA.unpack(
        u"\1\u00b0\1\u0084\11\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77"
        u"\1\117\1\164\1\126\1\u00b1\1\127\1\130\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA40_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\1\3\1\4\1\5\1\6\1\7\1\10\1\11\24\uffff"
        )

    DFA40_special = DFA.unpack(
        u"\37\uffff"
        )

            
    DFA40_transition = [
        DFA.unpack(u"\1\7\1\10\1\11\1\5\1\6\11\uffff\1\3\34\uffff\1\2\14"
        u"\uffff\1\12\11\uffff\1\4\115\uffff\1\1"),
        DFA.unpack(u"\1\13\1\uffff\1\13\20\uffff\1\13\2\uffff\1\13\1\uffff"
        u"\1\13\6\uffff\1\13\1\uffff\1\13\10\uffff\1\13\2\uffff\3\13\27\uffff"
        u"\1\13\4\uffff\1\13\60\uffff\1\14\2\uffff\1\13"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\27"),
        DFA.unpack(u"\1\5\12\uffff\1\3\34\uffff\1\2\14\uffff\1\12"),
        DFA.unpack(u"\1\30"),
        DFA.unpack(u"\1\31"),
        DFA.unpack(u"\1\32"),
        DFA.unpack(u"\1\33"),
        DFA.unpack(u"\1\34"),
        DFA.unpack(u"\1\35"),
        DFA.unpack(u"\1\5\12\uffff\1\3\34\uffff\1\2\14\uffff\1\12\127\uffff"
        u"\1\36"),
        DFA.unpack(u"\1\14")
    ]

    # class definition for DFA #40

    class DFA40(DFA):
        pass


    # lookup tables for DFA #51

    DFA51_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA51_eof = DFA.unpack(
        u"\30\uffff"
        )

    DFA51_min = DFA.unpack(
        u"\1\51\1\4\2\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77\1\117"
        u"\1\164\1\126\1\u00b1\1\127\1\51\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\51\1\u0081"
        )

    DFA51_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\125\1\u0082\1\117\1\u0083\1\127\1\77"
        u"\1\117\1\164\1\126\1\u00b1\1\127\2\125\1\117\1\127\1\117\1\126"
        u"\1\u00b1\1\u00b0\1\u0081"
        )

    DFA51_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA51_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA51_transition = [
        DFA.unpack(u"\1\3\53\uffff\1\2\132\uffff\1\1"),
        DFA.unpack(u"\1\4\1\uffff\1\4\20\uffff\1\4\2\uffff\1\4\1\uffff\1"
        u"\4\6\uffff\1\4\1\uffff\1\4\10\uffff\1\4\2\uffff\3\4\27\uffff\1"
        u"\4\4\uffff\1\4\60\uffff\1\5\2\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\3\53\uffff\1\2"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\3\53\uffff\1\2\132\uffff\1\27"),
        DFA.unpack(u"\1\5")
    ]

    # class definition for DFA #51

    class DFA51(DFA):
        pass


    # lookup tables for DFA #49

    DFA49_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA49_eof = DFA.unpack(
        u"\1\2\27\uffff"
        )

    DFA49_min = DFA.unpack(
        u"\1\51\1\4\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127\1\164"
        u"\1\117\1\u00b1\1\126\1\51\1\127\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\51\1\u0081"
        )

    DFA49_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127"
        u"\1\164\1\117\1\u00b1\1\126\1\125\1\127\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA49_accept = DFA.unpack(
        u"\2\uffff\1\2\1\1\24\uffff"
        )

    DFA49_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA49_transition = [
        DFA.unpack(u"\1\2\53\uffff\1\3\3\uffff\2\2\125\uffff\1\1"),
        DFA.unpack(u"\1\5\1\uffff\1\5\20\uffff\1\5\2\uffff\1\5\1\uffff\1"
        u"\5\6\uffff\1\5\1\uffff\1\5\10\uffff\1\5\2\uffff\3\5\27\uffff\1"
        u"\5\4\uffff\1\5\60\uffff\1\4\2\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\53\uffff\1\3"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\2\53\uffff\1\3\132\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #49

    class DFA49(DFA):
        pass


    # lookup tables for DFA #59

    DFA59_eot = DFA.unpack(
        u"\30\uffff"
        )

    DFA59_eof = DFA.unpack(
        u"\1\3\27\uffff"
        )

    DFA59_min = DFA.unpack(
        u"\1\40\1\4\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127\1\164"
        u"\1\117\1\u00b1\1\126\1\43\1\127\1\125\1\117\1\127\1\117\1\126\1"
        u"\u00b1\1\43\1\u0081"
        )

    DFA59_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\u0082\1\125\1\u0083\1\117\1\77\1\127"
        u"\1\164\1\117\1\u00b1\1\126\1\177\1\127\1\125\1\117\1\127\1\117"
        u"\1\126\1\u00b1\1\u00b0\1\u0081"
        )

    DFA59_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\24\uffff"
        )

    DFA59_special = DFA.unpack(
        u"\30\uffff"
        )

            
    DFA59_transition = [
        DFA.unpack(u"\5\2\4\uffff\1\3\4\uffff\1\2\3\uffff\2\2\1\uffff\1\2"
        u"\25\uffff\1\2\11\uffff\1\3\2\uffff\1\2\2\3\7\uffff\1\2\1\uffff"
        u"\1\2\32\uffff\1\2\60\uffff\1\1"),
        DFA.unpack(u"\1\5\1\uffff\1\5\20\uffff\1\5\2\uffff\1\5\1\uffff\1"
        u"\5\6\uffff\1\5\1\uffff\1\5\10\uffff\1\5\2\uffff\3\5\27\uffff\1"
        u"\5\4\uffff\1\5\60\uffff\1\4\2\uffff\1\5"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\2\5\uffff\1\3\4\uffff\1\2\3\uffff\2\2\1\uffff\1"
        u"\2\25\uffff\1\2\11\uffff\1\3\2\uffff\1\2\46\uffff\1\2"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\1\21"),
        DFA.unpack(u"\1\22"),
        DFA.unpack(u"\1\23"),
        DFA.unpack(u"\1\24"),
        DFA.unpack(u"\1\25"),
        DFA.unpack(u"\1\26"),
        DFA.unpack(u"\1\2\5\uffff\1\3\4\uffff\1\2\3\uffff\2\2\1\uffff\1"
        u"\2\25\uffff\1\2\11\uffff\1\3\2\uffff\1\2\13\uffff\1\2\32\uffff"
        u"\1\2\60\uffff\1\27"),
        DFA.unpack(u"\1\4")
    ]

    # class definition for DFA #59

    class DFA59(DFA):
        pass


    # lookup tables for DFA #89

    DFA89_eot = DFA.unpack(
        u"\12\uffff"
        )

    DFA89_eof = DFA.unpack(
        u"\1\1\11\uffff"
        )

    DFA89_min = DFA.unpack(
        u"\1\6\1\uffff\7\0\1\uffff"
        )

    DFA89_max = DFA.unpack(
        u"\1\u00b0\1\uffff\7\0\1\uffff"
        )

    DFA89_accept = DFA.unpack(
        u"\1\uffff\1\2\7\uffff\1\1"
        )

    DFA89_special = DFA.unpack(
        u"\2\uffff\1\4\1\1\1\5\1\2\1\6\1\0\1\3\1\uffff"
        )

            
    DFA89_transition = [
        DFA.unpack(u"\1\1\42\uffff\1\1\22\uffff\2\1\24\uffff\1\1\2\uffff"
        u"\3\1\4\uffff\1\2\1\3\1\4\1\6\1\7\1\5\3\uffff\4\1\1\10\6\1\12\uffff"
        u"\1\1\5\uffff\1\1\47\uffff\1\1\1\uffff\1\1\5\uffff\1\1"),
        DFA.unpack(u""),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"\1\uffff"),
        DFA.unpack(u"")
    ]

    # class definition for DFA #89

    class DFA89(DFA):
        pass


        def specialStateTransition(self_, s, input):
            # convince pylint that my self_ magic is ok ;)
            # pylint: disable-msg=E0213

            # pretend we are a member of the recognizer
            # thus semantic predicates can be evaluated
            self = self_.recognizer

            _s = s

            if s == 0: 
                LA89_7 = input.LA(1)

                 
                index89_7 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_7)
                if s >= 0:
                    return s
            elif s == 1: 
                LA89_3 = input.LA(1)

                 
                index89_3 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_3)
                if s >= 0:
                    return s
            elif s == 2: 
                LA89_5 = input.LA(1)

                 
                index89_5 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_5)
                if s >= 0:
                    return s
            elif s == 3: 
                LA89_8 = input.LA(1)

                 
                index89_8 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_8)
                if s >= 0:
                    return s
            elif s == 4: 
                LA89_2 = input.LA(1)

                 
                index89_2 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_2)
                if s >= 0:
                    return s
            elif s == 5: 
                LA89_4 = input.LA(1)

                 
                index89_4 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_4)
                if s >= 0:
                    return s
            elif s == 6: 
                LA89_6 = input.LA(1)

                 
                index89_6 = input.index()
                input.rewind()
                s = -1
                if (self.synpred109_sdl92()):
                    s = 9

                elif (True):
                    s = 1

                 
                input.seek(index89_6)
                if s >= 0:
                    return s

            if self._state.backtracking >0:
                raise BacktrackingFailed
            nvae = NoViableAltException(self_.getDescription(), 89, _s, input)
            self_.error(nvae)
            raise nvae
    # lookup tables for DFA #99

    DFA99_eot = DFA.unpack(
        u"\24\uffff"
        )

    DFA99_eof = DFA.unpack(
        u"\11\uffff\1\16\12\uffff"
        )

    DFA99_min = DFA.unpack(
        u"\1\117\10\uffff\1\6\2\uffff\1\117\4\uffff\1\73\2\uffff"
        )

    DFA99_max = DFA.unpack(
        u"\1\171\10\uffff\1\u00b0\2\uffff\1\173\4\uffff\1\u00a6\2\uffff"
        )

    DFA99_accept = DFA.unpack(
        u"\1\uffff\1\1\1\2\1\3\1\4\1\5\1\6\1\7\1\10\1\uffff\1\12\1\13\1\uffff"
        u"\1\16\1\11\1\14\1\15\1\uffff\1\20\1\17"
        )

    DFA99_special = DFA.unpack(
        u"\24\uffff"
        )

            
    DFA99_transition = [
        DFA.unpack(u"\1\12\24\uffff\1\11\13\uffff\1\1\1\2\1\3\1\4\1\5\1\6"
        u"\1\7\1\10\1\13\1\14"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\16\42\uffff\1\16\22\uffff\2\16\24\uffff\1\16\2\uffff"
        u"\3\16\4\uffff\6\16\3\uffff\13\16\12\uffff\1\16\5\uffff\1\16\45"
        u"\uffff\1\15\1\uffff\1\16\1\uffff\1\16\5\uffff\1\16"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\22\24\uffff\1\21\13\uffff\12\22\1\17\1\20"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\23\23\uffff\1\23\5\uffff\1\23\1\uffff\1\22\14\uffff"
        u"\1\23\6\uffff\1\23\4\uffff\12\23\1\22\3\uffff\1\23\47\uffff\1\22"),
        DFA.unpack(u""),
        DFA.unpack(u"")
    ]

    # class definition for DFA #99

    class DFA99(DFA):
        pass


    # lookup tables for DFA #109

    DFA109_eot = DFA.unpack(
        u"\21\uffff"
        )

    DFA109_eof = DFA.unpack(
        u"\21\uffff"
        )

    DFA109_min = DFA.unpack(
        u"\1\62\1\4\2\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1\125\1\117"
        u"\1\127\1\117\1\126\1\u00b1\1\62"
        )

    DFA109_max = DFA.unpack(
        u"\1\u00b0\1\u0084\2\uffff\1\125\1\117\1\127\1\117\1\126\1\127\1"
        u"\125\1\117\1\127\1\117\1\126\1\u00b1\1\u00b0"
        )

    DFA109_accept = DFA.unpack(
        u"\2\uffff\1\1\1\2\15\uffff"
        )

    DFA109_special = DFA.unpack(
        u"\21\uffff"
        )

            
    DFA109_transition = [
        DFA.unpack(u"\2\3\1\uffff\1\3\56\uffff\1\2\32\uffff\1\3\60\uffff"
        u"\1\1"),
        DFA.unpack(u"\1\4\1\uffff\1\4\20\uffff\1\4\2\uffff\1\4\1\uffff\1"
        u"\4\6\uffff\1\4\1\uffff\1\4\10\uffff\1\4\2\uffff\3\4\27\uffff\1"
        u"\4\4\uffff\1\4\60\uffff\1\3\2\uffff\1\4"),
        DFA.unpack(u""),
        DFA.unpack(u""),
        DFA.unpack(u"\1\5"),
        DFA.unpack(u"\1\6"),
        DFA.unpack(u"\1\7"),
        DFA.unpack(u"\1\10"),
        DFA.unpack(u"\1\11"),
        DFA.unpack(u"\1\12"),
        DFA.unpack(u"\1\13"),
        DFA.unpack(u"\1\14"),
        DFA.unpack(u"\1\15"),
        DFA.unpack(u"\1\16"),
        DFA.unpack(u"\1\17"),
        DFA.unpack(u"\1\20"),
        DFA.unpack(u"\2\3\1\uffff\1\3\56\uffff\1\2\32\uffff\1\3\60\uffff"
        u"\1\3")
    ]

    # class definition for DFA #109

    class DFA109(DFA):
        pass


 

    FOLLOW_PROCESS_in_processDefinition880 = frozenset([100])
    FOLLOW_process_id_in_processDefinition882 = frozenset([6, 85, 128, 176])
    FOLLOW_number_of_instances_in_processDefinition884 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_processDefinition887 = frozenset([23, 78, 80, 176])
    FOLLOW_text_area_in_processDefinition905 = frozenset([23, 78, 80, 176])
    FOLLOW_processBody_in_processDefinition924 = frozenset([78])
    FOLLOW_ENDPROCESS_in_processDefinition926 = frozenset([6, 85, 100, 128, 176])
    FOLLOW_process_id_in_processDefinition928 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_processDefinition931 = frozenset([1])
    FOLLOW_cif_in_text_area991 = frozenset([70, 176])
    FOLLOW_content_in_text_area1009 = frozenset([70, 176])
    FOLLOW_cif_end_text_in_text_area1079 = frozenset([1])
    FOLLOW_variable_definition_in_content1157 = frozenset([1, 70])
    FOLLOW_DCL_in_variable_definition1224 = frozenset([100])
    FOLLOW_variables_of_sort_in_variable_definition1226 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_COMMA_in_variable_definition1229 = frozenset([100])
    FOLLOW_variables_of_sort_in_variable_definition1231 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_end_in_variable_definition1235 = frozenset([1])
    FOLLOW_variable_id_in_variables_of_sort1271 = frozenset([87, 100])
    FOLLOW_COMMA_in_variables_of_sort1274 = frozenset([100])
    FOLLOW_variable_id_in_variables_of_sort1276 = frozenset([87, 100])
    FOLLOW_sort_in_variables_of_sort1280 = frozenset([1, 133])
    FOLLOW_ASSIG_OP_in_variables_of_sort1283 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_ground_expression_in_variables_of_sort1285 = frozenset([1])
    FOLLOW_expression_in_ground_expression1326 = frozenset([1])
    FOLLOW_L_PAREN_in_number_of_instances1365 = frozenset([79])
    FOLLOW_INT_in_number_of_instances1369 = frozenset([87])
    FOLLOW_COMMA_in_number_of_instances1371 = frozenset([79])
    FOLLOW_INT_in_number_of_instances1375 = frozenset([86])
    FOLLOW_R_PAREN_in_number_of_instances1377 = frozenset([1])
    FOLLOW_start_in_processBody1427 = frozenset([1, 23, 176])
    FOLLOW_state_in_processBody1431 = frozenset([1, 23, 176])
    FOLLOW_cif_in_start1466 = frozenset([80, 176])
    FOLLOW_hyperlink_in_start1485 = frozenset([80])
    FOLLOW_START_in_start1504 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_start1506 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_start1524 = frozenset([1])
    FOLLOW_cif_in_state1587 = frozenset([23, 176])
    FOLLOW_hyperlink_in_state1607 = frozenset([23])
    FOLLOW_STATE_in_state1626 = frozenset([82, 100])
    FOLLOW_statelist_in_state1628 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_state1632 = frozenset([25, 26, 28, 81, 176])
    FOLLOW_state_part_in_state1651 = frozenset([25, 26, 28, 81, 176])
    FOLLOW_ENDSTATE_in_state1671 = frozenset([6, 85, 100, 128, 176])
    FOLLOW_statename_in_state1673 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_state1678 = frozenset([1])
    FOLLOW_statename_in_statelist1738 = frozenset([1, 87])
    FOLLOW_COMMA_in_statelist1741 = frozenset([100])
    FOLLOW_statename_in_statelist1743 = frozenset([1, 87])
    FOLLOW_ASTERISK_in_statelist1778 = frozenset([1, 85])
    FOLLOW_exception_state_in_statelist1780 = frozenset([1])
    FOLLOW_L_PAREN_in_exception_state1826 = frozenset([100])
    FOLLOW_statename_in_exception_state1828 = frozenset([86, 87])
    FOLLOW_COMMA_in_exception_state1831 = frozenset([100])
    FOLLOW_statename_in_exception_state1833 = frozenset([86, 87])
    FOLLOW_R_PAREN_in_exception_state1837 = frozenset([1])
    FOLLOW_input_part_in_state_part1883 = frozenset([1])
    FOLLOW_save_part_in_state_part1948 = frozenset([1])
    FOLLOW_spontaneous_transition_in_state_part1996 = frozenset([1])
    FOLLOW_continuous_signal_in_state_part2025 = frozenset([1])
    FOLLOW_cif_in_spontaneous_transition2068 = frozenset([28, 176])
    FOLLOW_hyperlink_in_spontaneous_transition2087 = frozenset([28])
    FOLLOW_INPUT_in_spontaneous_transition2106 = frozenset([83])
    FOLLOW_NONE_in_spontaneous_transition2108 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_spontaneous_transition2110 = frozenset([26, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_enabling_condition_in_spontaneous_transition2128 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_spontaneous_transition2147 = frozenset([1])
    FOLLOW_PROVIDED_in_enabling_condition2204 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_enabling_condition2206 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_enabling_condition2208 = frozenset([1])
    FOLLOW_PROVIDED_in_continuous_signal2246 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_continuous_signal2248 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_continuous_signal2250 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 84, 88, 98, 100, 127, 176])
    FOLLOW_PRIORITY_in_continuous_signal2270 = frozenset([79])
    FOLLOW_INT_in_continuous_signal2274 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_continuous_signal2276 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_continuous_signal2297 = frozenset([1])
    FOLLOW_SAVE_in_save_part2359 = frozenset([82, 100])
    FOLLOW_save_list_in_save_part2361 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_save_part2363 = frozenset([1])
    FOLLOW_signal_list_in_save_list2406 = frozenset([1])
    FOLLOW_asterisk_save_list_in_save_list2408 = frozenset([1])
    FOLLOW_ASTERISK_in_asterisk_save_list2436 = frozenset([1])
    FOLLOW_signal_item_in_signal_list2463 = frozenset([1, 87])
    FOLLOW_COMMA_in_signal_list2466 = frozenset([100])
    FOLLOW_signal_item_in_signal_list2468 = frozenset([1, 87])
    FOLLOW_signal_id_in_signal_item2503 = frozenset([1])
    FOLLOW_cif_in_input_part2542 = frozenset([28, 176])
    FOLLOW_hyperlink_in_input_part2561 = frozenset([28])
    FOLLOW_INPUT_in_input_part2580 = frozenset([82, 100])
    FOLLOW_inputlist_in_input_part2582 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_input_part2584 = frozenset([1, 26, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_enabling_condition_in_input_part2603 = frozenset([1, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_input_part2623 = frozenset([1])
    FOLLOW_ASTERISK_in_inputlist2694 = frozenset([1])
    FOLLOW_stimulus_in_inputlist2719 = frozenset([1, 87])
    FOLLOW_COMMA_in_inputlist2722 = frozenset([82, 100])
    FOLLOW_stimulus_in_inputlist2724 = frozenset([1, 87])
    FOLLOW_stimulus_id_in_stimulus2772 = frozenset([1, 85])
    FOLLOW_input_params_in_stimulus2774 = frozenset([1])
    FOLLOW_L_PAREN_in_input_params2815 = frozenset([100])
    FOLLOW_variable_id_in_input_params2817 = frozenset([86, 87])
    FOLLOW_COMMA_in_input_params2820 = frozenset([100])
    FOLLOW_variable_id_in_input_params2822 = frozenset([86, 87])
    FOLLOW_R_PAREN_in_input_params2826 = frozenset([1])
    FOLLOW_action_in_transition2869 = frozenset([1, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_terminator_statement_in_transition2872 = frozenset([1])
    FOLLOW_terminator_statement_in_transition2910 = frozenset([1])
    FOLLOW_label_in_action2960 = frozenset([32, 33, 34, 35, 36, 46, 75, 88, 98, 100, 176])
    FOLLOW_task_in_action2980 = frozenset([1])
    FOLLOW_output_in_action3020 = frozenset([1])
    FOLLOW_create_request_in_action3059 = frozenset([1])
    FOLLOW_decision_in_action3090 = frozenset([1])
    FOLLOW_transition_option_in_action3135 = frozenset([1])
    FOLLOW_set_timer_in_action3171 = frozenset([1])
    FOLLOW_reset_timer_in_action3215 = frozenset([1])
    FOLLOW_export_in_action3256 = frozenset([1])
    FOLLOW_procedure_call_in_action3297 = frozenset([1])
    FOLLOW_EXPORT_in_export3340 = frozenset([85])
    FOLLOW_L_PAREN_in_export3358 = frozenset([100])
    FOLLOW_variable_id_in_export3360 = frozenset([86, 87])
    FOLLOW_COMMA_in_export3363 = frozenset([100])
    FOLLOW_variable_id_in_export3365 = frozenset([86, 87])
    FOLLOW_R_PAREN_in_export3369 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_export3371 = frozenset([1])
    FOLLOW_cif_in_procedure_call3403 = frozenset([88, 176])
    FOLLOW_hyperlink_in_procedure_call3422 = frozenset([88])
    FOLLOW_CALL_in_procedure_call3441 = frozenset([100])
    FOLLOW_procedure_call_body_in_procedure_call3443 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_procedure_call3445 = frozenset([1])
    FOLLOW_procedure_id_in_procedure_call_body3504 = frozenset([1, 85])
    FOLLOW_actual_parameters_in_procedure_call_body3506 = frozenset([1])
    FOLLOW_SET_in_set_timer3549 = frozenset([85])
    FOLLOW_set_statement_in_set_timer3551 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_COMMA_in_set_timer3554 = frozenset([85])
    FOLLOW_set_statement_in_set_timer3556 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_end_in_set_timer3560 = frozenset([1])
    FOLLOW_L_PAREN_in_set_statement3595 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_set_statement3598 = frozenset([87])
    FOLLOW_COMMA_in_set_statement3600 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_timer_id_in_set_statement3604 = frozenset([86])
    FOLLOW_R_PAREN_in_set_statement3606 = frozenset([1])
    FOLLOW_RESET_in_reset_timer3676 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_reset_statement_in_reset_timer3678 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_COMMA_in_reset_timer3681 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_reset_statement_in_reset_timer3683 = frozenset([6, 85, 87, 128, 176])
    FOLLOW_end_in_reset_timer3687 = frozenset([1])
    FOLLOW_timer_id_in_reset_statement3717 = frozenset([1, 85])
    FOLLOW_L_PAREN_in_reset_statement3720 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_reset_statement3722 = frozenset([86])
    FOLLOW_R_PAREN_in_reset_statement3724 = frozenset([1])
    FOLLOW_ALTERNATIVE_in_transition_option3771 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_alternative_question_in_transition_option3773 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_transition_option3777 = frozenset([85, 176])
    FOLLOW_answer_part_in_transition_option3795 = frozenset([41, 85, 176])
    FOLLOW_alternative_part_in_transition_option3813 = frozenset([89])
    FOLLOW_ENDALTERNATIVE_in_transition_option3831 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_transition_option3835 = frozenset([1])
    FOLLOW_answer_part_in_alternative_part3900 = frozenset([1, 41, 85, 176])
    FOLLOW_else_part_in_alternative_part3903 = frozenset([1])
    FOLLOW_else_part_in_alternative_part3947 = frozenset([1])
    FOLLOW_expression_in_alternative_question4003 = frozenset([1])
    FOLLOW_informal_text_in_alternative_question4007 = frozenset([1])
    FOLLOW_cif_in_decision4038 = frozenset([35, 176])
    FOLLOW_hyperlink_in_decision4057 = frozenset([35])
    FOLLOW_DECISION_in_decision4076 = frozenset([59, 79, 85, 91, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_question_in_decision4078 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_decision4082 = frozenset([41, 85, 90, 176])
    FOLLOW_answer_part_in_decision4111 = frozenset([41, 85, 90, 176])
    FOLLOW_alternative_part_in_decision4130 = frozenset([90])
    FOLLOW_ENDDECISION_in_decision4149 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_decision4153 = frozenset([1])
    FOLLOW_cif_in_answer_part4235 = frozenset([85, 176])
    FOLLOW_hyperlink_in_answer_part4254 = frozenset([85])
    FOLLOW_L_PAREN_in_answer_part4273 = frozenset([59, 79, 85, 92, 93, 94, 95, 96, 97, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_answer_in_answer_part4275 = frozenset([86])
    FOLLOW_R_PAREN_in_answer_part4277 = frozenset([166])
    FOLLOW_166_in_answer_part4279 = frozenset([1, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_answer_part4281 = frozenset([1])
    FOLLOW_range_condition_in_answer4341 = frozenset([1])
    FOLLOW_informal_text_in_answer4361 = frozenset([1])
    FOLLOW_cif_in_else_part4390 = frozenset([41, 176])
    FOLLOW_hyperlink_in_else_part4409 = frozenset([41])
    FOLLOW_ELSE_in_else_part4428 = frozenset([166])
    FOLLOW_166_in_else_part4430 = frozenset([1, 32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_transition_in_else_part4432 = frozenset([1])
    FOLLOW_expression_in_question4509 = frozenset([1])
    FOLLOW_informal_text_in_question4571 = frozenset([1])
    FOLLOW_ANY_in_question4623 = frozenset([1])
    FOLLOW_closed_range_in_range_condition4690 = frozenset([1])
    FOLLOW_open_range_in_range_condition4694 = frozenset([1])
    FOLLOW_INT_in_closed_range4744 = frozenset([166])
    FOLLOW_166_in_closed_range4746 = frozenset([79])
    FOLLOW_INT_in_closed_range4750 = frozenset([1])
    FOLLOW_constant_in_open_range4810 = frozenset([1])
    FOLLOW_EQ_in_open_range4868 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_NEQ_in_open_range4870 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_GT_in_open_range4872 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_LT_in_open_range4874 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_LE_in_open_range4876 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_GE_in_open_range4878 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_constant_in_open_range4881 = frozenset([1])
    FOLLOW_expression_in_constant4951 = frozenset([1])
    FOLLOW_CREATE_in_create_request5010 = frozenset([99, 100])
    FOLLOW_createbody_in_create_request5029 = frozenset([6, 85, 128, 176])
    FOLLOW_actual_parameters_in_create_request5047 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_create_request5050 = frozenset([1])
    FOLLOW_process_id_in_createbody5106 = frozenset([1])
    FOLLOW_THIS_in_createbody5126 = frozenset([1])
    FOLLOW_cif_in_output5150 = frozenset([46, 176])
    FOLLOW_hyperlink_in_output5169 = frozenset([46])
    FOLLOW_OUTPUT_in_output5188 = frozenset([100])
    FOLLOW_outputbody_in_output5190 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_output5192 = frozenset([1])
    FOLLOW_outputstmt_in_outputbody5256 = frozenset([1, 87])
    FOLLOW_COMMA_in_outputbody5259 = frozenset([100])
    FOLLOW_outputstmt_in_outputbody5261 = frozenset([1, 87])
    FOLLOW_signal_id_in_outputstmt5313 = frozenset([1, 85])
    FOLLOW_actual_parameters_in_outputstmt5332 = frozenset([1])
    FOLLOW_167_in_viabody5370 = frozenset([1])
    FOLLOW_via_path_in_viabody5422 = frozenset([1])
    FOLLOW_pid_expression_in_destination5478 = frozenset([1])
    FOLLOW_process_id_in_destination5499 = frozenset([1])
    FOLLOW_THIS_in_destination5519 = frozenset([1])
    FOLLOW_via_path_element_in_via_path5557 = frozenset([1, 87])
    FOLLOW_COMMA_in_via_path5560 = frozenset([100])
    FOLLOW_via_path_element_in_via_path5562 = frozenset([1, 87])
    FOLLOW_ID_in_via_path_element5606 = frozenset([1])
    FOLLOW_L_PAREN_in_actual_parameters5636 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_actual_parameters5638 = frozenset([86, 87])
    FOLLOW_COMMA_in_actual_parameters5641 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_actual_parameters5643 = frozenset([86, 87])
    FOLLOW_R_PAREN_in_actual_parameters5647 = frozenset([1])
    FOLLOW_cif_in_task5701 = frozenset([75, 176])
    FOLLOW_hyperlink_in_task5720 = frozenset([75])
    FOLLOW_TASK_in_task5739 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_task_body_in_task5741 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_task5743 = frozenset([1])
    FOLLOW_assignement_statement_in_task_body5806 = frozenset([1, 87])
    FOLLOW_COMMA_in_task_body5809 = frozenset([100])
    FOLLOW_assignement_statement_in_task_body5811 = frozenset([1, 87])
    FOLLOW_informal_text_in_task_body5847 = frozenset([1, 87])
    FOLLOW_COMMA_in_task_body5850 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_informal_text_in_task_body5852 = frozenset([1, 87])
    FOLLOW_variable_in_assignement_statement5911 = frozenset([133])
    FOLLOW_ASSIG_OP_in_assignement_statement5913 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_assignement_statement5915 = frozenset([1])
    FOLLOW_variable_id_in_variable5970 = frozenset([1, 85, 168])
    FOLLOW_primary_params_in_variable5972 = frozenset([1, 85, 168])
    FOLLOW_168_in_field_selection6052 = frozenset([100])
    FOLLOW_field_name_in_field_selection6054 = frozenset([1])
    FOLLOW_operand0_in_expression6093 = frozenset([1, 101])
    FOLLOW_IMPLIES_in_expression6097 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand0_in_expression6100 = frozenset([1, 101])
    FOLLOW_operand1_in_operand06123 = frozenset([1, 102, 103])
    FOLLOW_OR_in_operand06128 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_XOR_in_operand06133 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand1_in_operand06138 = frozenset([1, 102, 103])
    FOLLOW_operand2_in_operand16160 = frozenset([1, 104])
    FOLLOW_AND_in_operand16164 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand2_in_operand16167 = frozenset([1, 104])
    FOLLOW_operand3_in_operand26189 = frozenset([1, 92, 93, 94, 95, 96, 97, 105])
    FOLLOW_EQ_in_operand26194 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_NEQ_in_operand26199 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_GT_in_operand26204 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_GE_in_operand26209 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_LT_in_operand26214 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_LE_in_operand26219 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_IN_in_operand26224 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand3_in_operand26229 = frozenset([1, 92, 93, 94, 95, 96, 97, 105])
    FOLLOW_operand4_in_operand36251 = frozenset([1, 106, 107, 108])
    FOLLOW_PLUS_in_operand36256 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_DASH_in_operand36261 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_APPEND_in_operand36266 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand4_in_operand36271 = frozenset([1, 106, 107, 108])
    FOLLOW_operand5_in_operand46293 = frozenset([1, 82, 109, 110, 111])
    FOLLOW_ASTERISK_in_operand46298 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_DIV_in_operand46303 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_MOD_in_operand46308 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_REM_in_operand46313 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand5_in_operand46318 = frozenset([1, 82, 109, 110, 111])
    FOLLOW_primary_qualifier_in_operand56340 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_primary_in_operand56343 = frozenset([1])
    FOLLOW_asn1Value_in_primary6386 = frozenset([1, 85, 168])
    FOLLOW_primary_params_in_primary6388 = frozenset([1, 85, 168])
    FOLLOW_L_PAREN_in_primary6436 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_primary6438 = frozenset([86])
    FOLLOW_R_PAREN_in_primary6440 = frozenset([1])
    FOLLOW_conditional_ground_expression_in_primary6498 = frozenset([1])
    FOLLOW_BitStringLiteral_in_asn1Value6521 = frozenset([1])
    FOLLOW_OctetStringLiteral_in_asn1Value6558 = frozenset([1])
    FOLLOW_TRUE_in_asn1Value6593 = frozenset([1])
    FOLLOW_FALSE_in_asn1Value6612 = frozenset([1])
    FOLLOW_StringLiteral_in_asn1Value6631 = frozenset([1])
    FOLLOW_NULL_in_asn1Value6671 = frozenset([1])
    FOLLOW_PLUS_INFINITY_in_asn1Value6690 = frozenset([1])
    FOLLOW_MINUS_INFINITY_in_asn1Value6709 = frozenset([1])
    FOLLOW_ID_in_asn1Value6728 = frozenset([1])
    FOLLOW_INT_in_asn1Value6746 = frozenset([1])
    FOLLOW_FloatingPointLiteral_in_asn1Value6764 = frozenset([1])
    FOLLOW_L_BRACKET_in_asn1Value6797 = frozenset([122])
    FOLLOW_R_BRACKET_in_asn1Value6799 = frozenset([1])
    FOLLOW_L_BRACKET_in_asn1Value6831 = frozenset([123])
    FOLLOW_MANTISSA_in_asn1Value6850 = frozenset([79])
    FOLLOW_INT_in_asn1Value6854 = frozenset([87])
    FOLLOW_COMMA_in_asn1Value6856 = frozenset([124])
    FOLLOW_BASE_in_asn1Value6875 = frozenset([79])
    FOLLOW_INT_in_asn1Value6879 = frozenset([87])
    FOLLOW_COMMA_in_asn1Value6881 = frozenset([125])
    FOLLOW_EXPONENT_in_asn1Value6900 = frozenset([79])
    FOLLOW_INT_in_asn1Value6904 = frozenset([122])
    FOLLOW_R_BRACKET_in_asn1Value6923 = frozenset([1])
    FOLLOW_choiceValue_in_asn1Value6974 = frozenset([1])
    FOLLOW_L_BRACKET_in_asn1Value6992 = frozenset([100])
    FOLLOW_namedValue_in_asn1Value7010 = frozenset([87, 122])
    FOLLOW_COMMA_in_asn1Value7013 = frozenset([100])
    FOLLOW_namedValue_in_asn1Value7015 = frozenset([87, 122])
    FOLLOW_R_BRACKET_in_asn1Value7035 = frozenset([1])
    FOLLOW_L_BRACKET_in_asn1Value7080 = frozenset([79, 100, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121])
    FOLLOW_asn1Value_in_asn1Value7099 = frozenset([87, 122])
    FOLLOW_COMMA_in_asn1Value7102 = frozenset([79, 100, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121])
    FOLLOW_asn1Value_in_asn1Value7104 = frozenset([87, 122])
    FOLLOW_R_BRACKET_in_asn1Value7125 = frozenset([1])
    FOLLOW_StringLiteral_in_informal_text7265 = frozenset([1])
    FOLLOW_ID_in_choiceValue7307 = frozenset([166])
    FOLLOW_166_in_choiceValue7309 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_choiceValue7311 = frozenset([1])
    FOLLOW_ID_in_namedValue7350 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_namedValue7352 = frozenset([1])
    FOLLOW_DASH_in_primary_qualifier7378 = frozenset([1])
    FOLLOW_NOT_in_primary_qualifier7416 = frozenset([1])
    FOLLOW_L_PAREN_in_primary_params7437 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_primary_params7439 = frozenset([86])
    FOLLOW_R_PAREN_in_primary_params7441 = frozenset([1])
    FOLLOW_168_in_primary_params7475 = frozenset([79, 100])
    FOLLOW_literal_id_in_primary_params7477 = frozenset([1])
    FOLLOW_primary_in_indexed_primary7524 = frozenset([85])
    FOLLOW_L_PAREN_in_indexed_primary7526 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_indexed_primary7528 = frozenset([86])
    FOLLOW_R_PAREN_in_indexed_primary7530 = frozenset([1])
    FOLLOW_primary_in_field_primary7560 = frozenset([168])
    FOLLOW_field_selection_in_field_primary7562 = frozenset([1])
    FOLLOW_169_in_structure_primary7592 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_structure_primary7594 = frozenset([170])
    FOLLOW_170_in_structure_primary7596 = frozenset([1])
    FOLLOW_active_primary_in_active_expression7627 = frozenset([1])
    FOLLOW_variable_access_in_active_primary7657 = frozenset([1])
    FOLLOW_operator_application_in_active_primary7693 = frozenset([1])
    FOLLOW_conditional_expression_in_active_primary7724 = frozenset([1])
    FOLLOW_imperative_operator_in_active_primary7753 = frozenset([1])
    FOLLOW_L_PAREN_in_active_primary7785 = frozenset([59, 85, 100, 135, 142, 143, 147, 171, 172, 173, 174, 175])
    FOLLOW_active_expression_in_active_primary7787 = frozenset([86])
    FOLLOW_R_PAREN_in_active_primary7789 = frozenset([1])
    FOLLOW_171_in_active_primary7815 = frozenset([1])
    FOLLOW_now_expression_in_imperative_operator7855 = frozenset([1])
    FOLLOW_import_expression_in_imperative_operator7884 = frozenset([1])
    FOLLOW_pid_expression_in_imperative_operator7918 = frozenset([1])
    FOLLOW_view_expression_in_imperative_operator7947 = frozenset([1])
    FOLLOW_timer_active_expression_in_imperative_operator7975 = frozenset([1])
    FOLLOW_anyvalue_expression_in_imperative_operator8003 = frozenset([1])
    FOLLOW_172_in_timer_active_expression8025 = frozenset([85])
    FOLLOW_L_PAREN_in_timer_active_expression8027 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_timer_id_in_timer_active_expression8029 = frozenset([85, 86])
    FOLLOW_L_PAREN_in_timer_active_expression8032 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_timer_active_expression8034 = frozenset([86])
    FOLLOW_R_PAREN_in_timer_active_expression8036 = frozenset([86])
    FOLLOW_R_PAREN_in_timer_active_expression8040 = frozenset([1])
    FOLLOW_173_in_anyvalue_expression8070 = frozenset([85])
    FOLLOW_L_PAREN_in_anyvalue_expression8072 = frozenset([87, 100])
    FOLLOW_sort_in_anyvalue_expression8074 = frozenset([86])
    FOLLOW_R_PAREN_in_anyvalue_expression8076 = frozenset([1])
    FOLLOW_sort_id_in_sort8101 = frozenset([1])
    FOLLOW_syntype_id_in_syntype8137 = frozenset([1])
    FOLLOW_174_in_import_expression8159 = frozenset([85])
    FOLLOW_L_PAREN_in_import_expression8161 = frozenset([100])
    FOLLOW_remote_variable_id_in_import_expression8163 = frozenset([86, 87])
    FOLLOW_COMMA_in_import_expression8166 = frozenset([99, 100, 142, 143, 147])
    FOLLOW_destination_in_import_expression8168 = frozenset([86])
    FOLLOW_R_PAREN_in_import_expression8172 = frozenset([1])
    FOLLOW_175_in_view_expression8194 = frozenset([85])
    FOLLOW_L_PAREN_in_view_expression8196 = frozenset([100])
    FOLLOW_view_id_in_view_expression8198 = frozenset([86, 87])
    FOLLOW_COMMA_in_view_expression8201 = frozenset([142, 143, 147])
    FOLLOW_pid_expression_in_view_expression8203 = frozenset([86])
    FOLLOW_R_PAREN_in_view_expression8207 = frozenset([1])
    FOLLOW_variable_id_in_variable_access8229 = frozenset([1])
    FOLLOW_operator_id_in_operator_application8259 = frozenset([85])
    FOLLOW_L_PAREN_in_operator_application8261 = frozenset([59, 85, 100, 135, 142, 143, 147, 171, 172, 173, 174, 175])
    FOLLOW_active_expression_list_in_operator_application8262 = frozenset([86])
    FOLLOW_R_PAREN_in_operator_application8264 = frozenset([1])
    FOLLOW_active_expression_in_active_expression_list8295 = frozenset([1, 87])
    FOLLOW_COMMA_in_active_expression_list8298 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_list_in_active_expression_list8300 = frozenset([1])
    FOLLOW_IF_in_conditional_expression8336 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_expression8338 = frozenset([60])
    FOLLOW_THEN_in_conditional_expression8340 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_expression8342 = frozenset([41])
    FOLLOW_ELSE_in_conditional_expression8344 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_expression8346 = frozenset([61])
    FOLLOW_FI_in_conditional_expression8348 = frozenset([1])
    FOLLOW_ID_in_synonym8388 = frozenset([1])
    FOLLOW_external_synonym_id_in_external_synonym8411 = frozenset([1])
    FOLLOW_IF_in_conditional_ground_expression8434 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_ground_expression8438 = frozenset([60])
    FOLLOW_THEN_in_conditional_ground_expression8440 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_ground_expression8444 = frozenset([41])
    FOLLOW_ELSE_in_conditional_ground_expression8446 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_conditional_ground_expression8450 = frozenset([61])
    FOLLOW_FI_in_conditional_ground_expression8452 = frozenset([1])
    FOLLOW_expression_in_expression_list8497 = frozenset([1, 87])
    FOLLOW_COMMA_in_expression_list8500 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_expression_list8502 = frozenset([1, 87])
    FOLLOW_label_in_terminator_statement8542 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_cif_in_terminator_statement8561 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_hyperlink_in_terminator_statement8580 = frozenset([32, 33, 34, 35, 36, 46, 50, 51, 53, 75, 88, 98, 100, 127, 176])
    FOLLOW_terminator_in_terminator_statement8599 = frozenset([6, 85, 128, 176])
    FOLLOW_end_in_terminator_statement8618 = frozenset([1])
    FOLLOW_cif_in_label8680 = frozenset([100, 176])
    FOLLOW_connector_name_in_label8683 = frozenset([166])
    FOLLOW_166_in_label8685 = frozenset([1])
    FOLLOW_nextstate_in_terminator8729 = frozenset([1])
    FOLLOW_join_in_terminator8733 = frozenset([1])
    FOLLOW_stop_in_terminator8737 = frozenset([1])
    FOLLOW_return_stmt_in_terminator8741 = frozenset([1])
    FOLLOW_JOIN_in_join8768 = frozenset([100, 176])
    FOLLOW_connector_name_in_join8770 = frozenset([1])
    FOLLOW_STOP_in_stop8814 = frozenset([1])
    FOLLOW_RETURN_in_return_stmt8832 = frozenset([1, 59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_expression_in_return_stmt8834 = frozenset([1])
    FOLLOW_NEXTSTATE_in_nextstate8903 = frozenset([100, 107])
    FOLLOW_nextstatebody_in_nextstate8905 = frozenset([1])
    FOLLOW_statename_in_nextstatebody8948 = frozenset([1])
    FOLLOW_dash_nextstate_in_nextstatebody8967 = frozenset([1])
    FOLLOW_cif_in_end8988 = frozenset([6, 176])
    FOLLOW_hyperlink_in_end8991 = frozenset([6])
    FOLLOW_COMMENT_in_end8994 = frozenset([116])
    FOLLOW_StringLiteral_in_end8996 = frozenset([128])
    FOLLOW_SEMI_in_end9000 = frozenset([1])
    FOLLOW_cif_decl_in_cif9047 = frozenset([4, 6, 23, 26, 28, 35, 37, 46, 49, 50, 51, 75, 80, 132])
    FOLLOW_symbolname_in_cif9049 = frozenset([85])
    FOLLOW_L_PAREN_in_cif9059 = frozenset([79])
    FOLLOW_INT_in_cif9063 = frozenset([87])
    FOLLOW_COMMA_in_cif9065 = frozenset([79])
    FOLLOW_INT_in_cif9069 = frozenset([86])
    FOLLOW_R_PAREN_in_cif9071 = frozenset([87])
    FOLLOW_COMMA_in_cif9082 = frozenset([85])
    FOLLOW_L_PAREN_in_cif9092 = frozenset([79])
    FOLLOW_INT_in_cif9096 = frozenset([87])
    FOLLOW_COMMA_in_cif9098 = frozenset([79])
    FOLLOW_INT_in_cif9102 = frozenset([86])
    FOLLOW_R_PAREN_in_cif9104 = frozenset([177])
    FOLLOW_cif_end_in_cif9115 = frozenset([1])
    FOLLOW_cif_decl_in_hyperlink9191 = frozenset([129])
    FOLLOW_KEEP_in_hyperlink9193 = frozenset([130])
    FOLLOW_SPECIFIC_in_hyperlink9195 = frozenset([131])
    FOLLOW_GEODE_in_hyperlink9197 = frozenset([63])
    FOLLOW_HYPERLINK_in_hyperlink9199 = frozenset([116])
    FOLLOW_StringLiteral_in_hyperlink9201 = frozenset([177])
    FOLLOW_cif_end_in_hyperlink9211 = frozenset([1])
    FOLLOW_set_in_symbolname0 = frozenset([1])
    FOLLOW_176_in_cif_decl9353 = frozenset([1])
    FOLLOW_177_in_cif_end9374 = frozenset([1])
    FOLLOW_cif_decl_in_cif_end_text9390 = frozenset([19])
    FOLLOW_ENDTEXT_in_cif_end_text9392 = frozenset([177])
    FOLLOW_cif_end_in_cif_end_text9394 = frozenset([1])
    FOLLOW_DASH_in_dash_nextstate9416 = frozenset([1])
    FOLLOW_ID_in_connector_name9430 = frozenset([1])
    FOLLOW_ID_in_signal_id9449 = frozenset([1])
    FOLLOW_ID_in_statename9468 = frozenset([1])
    FOLLOW_ID_in_variable_id9485 = frozenset([1])
    FOLLOW_set_in_literal_id0 = frozenset([1])
    FOLLOW_ID_in_process_id9526 = frozenset([1])
    FOLLOW_ID_in_process_name9544 = frozenset([1])
    FOLLOW_ID_in_priority_signal_id9575 = frozenset([1])
    FOLLOW_ID_in_signal_list_id9589 = frozenset([1])
    FOLLOW_ID_in_timer_id9609 = frozenset([1])
    FOLLOW_ID_in_field_name9627 = frozenset([1])
    FOLLOW_ID_in_signal_route_id9640 = frozenset([1])
    FOLLOW_ID_in_channel_id9658 = frozenset([1])
    FOLLOW_ID_in_gate_id9679 = frozenset([1])
    FOLLOW_ID_in_procedure_id9695 = frozenset([1])
    FOLLOW_ID_in_remote_procedure_id9724 = frozenset([1])
    FOLLOW_ID_in_operator_id9741 = frozenset([1])
    FOLLOW_ID_in_synonym_id9759 = frozenset([1])
    FOLLOW_ID_in_external_synonym_id9788 = frozenset([1])
    FOLLOW_ID_in_remote_variable_id9817 = frozenset([1])
    FOLLOW_ID_in_view_id9838 = frozenset([1])
    FOLLOW_ID_in_sort_id9859 = frozenset([1])
    FOLLOW_ID_in_syntype_id9877 = frozenset([1])
    FOLLOW_ID_in_stimulus_id9894 = frozenset([1])
    FOLLOW_S_in_pid_expression10750 = frozenset([141])
    FOLLOW_E_in_pid_expression10752 = frozenset([139])
    FOLLOW_L_in_pid_expression10754 = frozenset([145])
    FOLLOW_F_in_pid_expression10756 = frozenset([1])
    FOLLOW_P_in_pid_expression10760 = frozenset([134])
    FOLLOW_A_in_pid_expression10762 = frozenset([149])
    FOLLOW_R_in_pid_expression10764 = frozenset([141])
    FOLLOW_E_in_pid_expression10766 = frozenset([135])
    FOLLOW_N_in_pid_expression10768 = frozenset([150])
    FOLLOW_T_in_pid_expression10770 = frozenset([1])
    FOLLOW_O_in_pid_expression10774 = frozenset([145])
    FOLLOW_F_in_pid_expression10776 = frozenset([145])
    FOLLOW_F_in_pid_expression10778 = frozenset([143])
    FOLLOW_S_in_pid_expression10780 = frozenset([142])
    FOLLOW_P_in_pid_expression10782 = frozenset([149])
    FOLLOW_R_in_pid_expression10784 = frozenset([144])
    FOLLOW_I_in_pid_expression10786 = frozenset([135])
    FOLLOW_N_in_pid_expression10788 = frozenset([146])
    FOLLOW_G_in_pid_expression10790 = frozenset([1])
    FOLLOW_S_in_pid_expression10794 = frozenset([141])
    FOLLOW_E_in_pid_expression10796 = frozenset([135])
    FOLLOW_N_in_pid_expression10798 = frozenset([137])
    FOLLOW_D_in_pid_expression10800 = frozenset([141])
    FOLLOW_E_in_pid_expression10802 = frozenset([149])
    FOLLOW_R_in_pid_expression10804 = frozenset([1])
    FOLLOW_N_in_now_expression10819 = frozenset([147])
    FOLLOW_O_in_now_expression10821 = frozenset([154])
    FOLLOW_W_in_now_expression10823 = frozenset([1])
    FOLLOW_content_in_synpred4_sdl921009 = frozenset([1])
    FOLLOW_enabling_condition_in_synpred32_sdl922603 = frozenset([1])
    FOLLOW_expression_in_synpred61_sdl924003 = frozenset([1])
    FOLLOW_answer_part_in_synpred64_sdl924111 = frozenset([1])
    FOLLOW_range_condition_in_synpred69_sdl924341 = frozenset([1])
    FOLLOW_expression_in_synpred73_sdl924509 = frozenset([1])
    FOLLOW_informal_text_in_synpred74_sdl924571 = frozenset([1])
    FOLLOW_IMPLIES_in_synpred99_sdl926097 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand0_in_synpred99_sdl926100 = frozenset([1])
    FOLLOW_set_in_synpred101_sdl926126 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand1_in_synpred101_sdl926138 = frozenset([1])
    FOLLOW_AND_in_synpred102_sdl926164 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand2_in_synpred102_sdl926167 = frozenset([1])
    FOLLOW_set_in_synpred109_sdl926192 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand3_in_synpred109_sdl926229 = frozenset([1])
    FOLLOW_set_in_synpred112_sdl926254 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand4_in_synpred112_sdl926271 = frozenset([1])
    FOLLOW_set_in_synpred116_sdl926296 = frozenset([59, 79, 85, 100, 107, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 126])
    FOLLOW_operand5_in_synpred116_sdl926318 = frozenset([1])
    FOLLOW_primary_params_in_synpred118_sdl926388 = frozenset([1])



def main(argv, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    from antlr3.main import ParserMain
    main = ParserMain("sdl92Lexer", sdl92Parser)
    main.stdin = stdin
    main.stdout = stdout
    main.stderr = stderr
    main.execute(argv)


if __name__ == '__main__':
    main(sys.argv)
