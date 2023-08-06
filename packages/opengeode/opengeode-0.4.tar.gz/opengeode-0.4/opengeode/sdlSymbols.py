#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    This module contains the definition of the SDL symbols,
    including geometry and specific symbol behaviour when needed.

    All symbols inherit the generic Vertical- and Horizontal-
    Symbol classes defined in the "genericSymbols.py" module.

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

__all__ = ['Input', 'Output', 'State', 'Task', 'ProcedureCall', 'Label',
           'Decision', 'DecisionAnswer', 'Join', 'Start', 'TextSymbol']

from genericSymbols import(
        HorizontalSymbol, VerticalSymbol, Connection, Comment)

from PySide.QtCore import Qt, QPoint, QRect
from PySide.QtGui import(QPainterPath, QBrush, QColor, QPolygon,
        QRadialGradient, QGraphicsItemGroup)

import ogParser
import ogAST

inputCompletionList = []
outputCompletionList = []
stateCompletionList = []
typesCompletionList = []
varCompletionList = []
procCompletionList = []


class Input(HorizontalSymbol):
    ''' SDL INPUT Symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Input', 'Join', 'Label', 'Comment', 'State']

    def __init__(self, parent=None, ast=None):
        ''' Create the INPUT symbol '''
        ast = ast or ogAST.Input()
        coord_x, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        self.branchEntryPoint = None
        super(Input, self).__init__(polygon, parent, text=ast.inputString,
                x=coord_x, y=coord_y, hyperlink=ast.hyperlink)
        gradient = QRadialGradient(50, 50, 50, 50, 50)
        gradient.setColorAt(0, QColor(255, 240, 170))
        gradient.setColorAt(1, Qt.white)
        self.setBrush(QBrush(gradient))
        self.terminalSymbol = False
        self.commonName = 'input_part'
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def checkSyntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntaxErrors, __, ___, ____ = self.parser.parseSingleElement(
                self.commonName, self.pr())
        try:
            self.scene().reportErrors(syntaxErrors)
        except:
            print('[SYNTAX ERROR]', '\n'.join(syntaxErrors))

    def insertSymbol(self, parent, x, y):
        ''' Insert Input symbol - propagate branch Entry point '''
        self.branchEntryPoint = parent.branchEntryPoint
        super(Input, self).insertSymbol(parent, x, y)

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        polygon = QPolygon()
        polygon << QPoint(0, 0) \
                << QPoint(width, 0) \
                << QPoint(width - 15, height / 2) \
                << QPoint(width, height) \
                << QPoint(0, height) \
                << QPoint(0, 0)
        return polygon

    def completionList(self):
        ''' Return the list of defined INPUTs for the autocompletion '''
        return inputCompletionList

    def pr(self):
        ''' Return the PR notation of the single INPUT sybol '''
        comment = repr(self.comment) if self.comment else ';'
        return('/* CIF INPUT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'INPUT {i}{comment}'.format(
                    hlink=repr(self.text), i=str(self),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))

    def __repr__(self):
        ''' Return the complete Input branch in PR format '''
        result = [self.pr()]
        # Recursively return the complete branch below the INPUT
        nextSymbol = self.nextAlignedSymbol()
        while nextSymbol:
            result.append(repr(nextSymbol))
            nextSymbol = nextSymbol.nextAlignedSymbol()
        return '\n'.join(result)


class Output(VerticalSymbol):
    ''' SDL OUTPUT Symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Join', 'Label', 'Comment', 'State']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output()
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(Output, self).__init__(polygon=polygon, parent=parent,
                text=ast.inputString, y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminalSymbol = False
        self.commonName = 'output'
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        polygon = QPolygon()
        polygon << QPoint(0, 0) \
                << QPoint(width - 15, 0) \
                << QPoint(width, height / 2) \
                << QPoint(width - 15, height) \
                << QPoint(0, height) \
                << QPoint(0, 0)
        return polygon

    def completionList(self):
        ''' Return the list of defined OUTPUTs for the autocompletion '''
        return outputCompletionList

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        return ('/* CIF OUTPUT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'OUTPUT {o}{comment}'.format(
                    hlink=repr(self.text), o=str(self),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


class Decision(VerticalSymbol):
    ''' SDL DECISION Symbol '''
    allowed_followers = ['DecisionAnswer', 'Task', 'ProcedureCall', 'Output',
                        'Decision', 'Join', 'Label', 'Comment', 'State']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Decision()
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        # Define the point where all branches of the decision can join again
        self.connectionPoint = QPoint(width / 2, height + 30)
        super(Decision, self).__init__(polygon, parent, text=ast.inputString,
                y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QColor(255, 255, 202))
        self.minDistanceToSymbolAbove = 0
        self.terminalSymbol = False
        self.commonName = 'decision'
        self.parser = ogParser
        self.text_alignment = Qt.AlignHCenter
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def checkSyntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntaxErrors, __, ___, ____ = self.parser.parseSingleElement(
                self.commonName, self.pr(recursive=False))
        try:
            self.scene().reportErrors(syntaxErrors)
        except:
            print('[SYNTAX ERROR]', '\n'.join(syntaxErrors))

    def computePolygon(self, width, height):
        ''' Define polygon points to draw the symbol '''
        polygon = QPolygon()
        polygon << QPoint(width / 2, 0) \
                << QPoint(width, height / 2) \
                << QPoint(width / 2, height) \
                << QPoint(0, height / 2) \
                << QPoint(width / 2, 0)
        return polygon

    def resizeItem(self, rect):
        ''' On resize event, make sure connection points are updated '''
        super(Decision, self).resizeItem(rect)
        self.updateConnectionPointPosition()

    def updateConnectionPointPosition(self):
        ''' Compute the joining point of decision branches '''
        if not self.scene():
            # Connection point update is only relevant for rendering
            # (i.e. if symbol is in a scene) - ignore otherwise
            return
        answers = filter(lambda c:
                isinstance(c, DecisionAnswer), self.childSymbols())
        newY = 0
        newX = self.boundingRect().width() / 2
        if answers:
            for branch in answers:
                lastCnx = []
                lastCmt = None
                last = branch.lastBranchItem
                # Coordinates of the last item of a branch
                # in Decision item coordinates:
                lastPosY = self.mapFromScene(0, last.scenePos().y()).y()
                lastCnx = [c for c in last.childItems() if
                        isinstance(c, Connection) and not
                        isinstance(c.child, Comment)]
                # To compute the branch length, we must keep only the symbols,
                # so we must remove the last connection
                if lastCnx:
                    lastCnx[0].setParentItem(None)
                if last.comment:
                    # Disconnect the comment of the last item so that
                    # it's size is not taken into account
                    lastCmt = last.comment
                    last.comment.setParentItem(None)
                    last.comment.connection.setParentItem(None)
                group = QGraphicsItemGroup(last.parentItem())
                group.addToGroup(last)
                groupHeight = group.boundingRect().height()
                self.scene().destroyItemGroup(group)
                branchLen = lastPosY + groupHeight
                if lastCnx:
                    lastCnx[0].setParentItem(last)
                if lastCmt:
                    # Reconnect the comment of the last item
                    lastCmt.setParentItem(last)
                    last.comment.connection.setParentItem(last)
                # If last item was a decision, use its connection point
                # position to get the length of the branch:
                if isinstance(last, Decision):
                    branchLen = lastPosY + last.connectionPoint.y()
                # Rounded with int() -> mandatory when view scale has changed
                newY = int(max(newY, branchLen))
        else:
            newY = int(self.boundingRect().height())
        newY += 15
        delta = newY - self.connectionPoint.y()
        self.connectionPoint.setY(newY)
        self.connectionPoint.setX(newX)
        child = filter(lambda c: not isinstance
                (c, (DecisionAnswer, Comment)), self.childSymbols())
        if child:
            child[0].moveBy(0, delta)

    def pr(self, recursive=True):
        ''' Get PR notation of a decision (possibly recursively) '''
        comment = repr(self.comment) if self.comment else ';'
        result = ['/* CIF DECISION ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'DECISION {d}{comment}'.format(
                    hlink=repr(self.text), d=str(self),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment)]
        if recursive:
            answers = filter(lambda i: isinstance(i, DecisionAnswer),
                self.childSymbols())
            for a in answers:
                if str(a).lower().strip() == 'else':
                    result.append(repr(a))
                else:
                    result.insert(1, repr(a))
        result.append('ENDDECISION;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the PR notation for the decision and all answers '''
        return self.pr(recursive=True)


class DecisionAnswer(HorizontalSymbol):
    ''' If Decision is a "switch", DecisionAnswer is a "case" '''
    allowed_followers = ['DecisionAnswer', 'Task', 'ProcedureCall',
                        'Output', 'Decision', 'Join', 'Label', 'State']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Answer()
        coord_x, coord_y, width, height = ast.coordinates
        self.terminalSymbol = False
        # lastBranchItem is used to compute branch length
        # for the connection point positionning
        self.lastBranchItem = self
        polygon = self.computePolygon(width, height)
        super(DecisionAnswer, self).__init__(polygon, parent,
                text=ast.inputString,
                x=coord_x, y=coord_y, hyperlink=ast.hyperlink)
        self.setPen(QColor(0, 0, 0, 0))
        self.branchEntryPoint = self
        self.commonName = 'alternative_part'
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def checkSyntax(self):
        ''' Redefined function, to check only the symbol, not recursively '''
        _, syntaxErrors, __, ___, ____ = self.parser.parseSingleElement(
                self.commonName, self.pr(recursive=False))
        try:
            self.scene().reportErrors(syntaxErrors)
        except:
            print('[SYNTAX ERROR]', '\n'.join(syntaxErrors))

    def insertSymbol(self, parent, x, y):
        ''' ANSWER-specific insersion behaviour: link to connection point '''
        if not parent:
            return
        super(DecisionAnswer, self).insertSymbol(parent, x, y)
        if not self.nextAlignedSymbol():
            # If inserting a new decision answer, link it
            # to the connection point
            self.connectionBelow = Connection(self, parent,
                    connectionPoint=True)

    def computePolygon(self, width, height):
        ''' ANSWER has round, disjoint sides - does not fit in a polygon '''
        bound = QRect(0, 0, width, height)
        polygon = QPolygon(bound)
        return polygon

    def paint(self, painter, _, __):
        ''' Draw ANSWER shape within a polygon boundaries '''
        rect = self.boundingRect()
        left = QRect(rect.x(), rect.y(), 35, rect.height())
        right = QRect(rect.width() - 35, rect.y(), 35, rect.height())
        painter.drawArc(left, 2000, 1760)
        painter.drawArc(right, -880, 1760)
        HorizontalSymbol.paint(self, painter, _, __)

    def pr(self, recursive=True):
        ''' Return the PR string for the symbol, possibly recursively '''
        ans = str(self)
        if ans.lower().strip() != 'else':
            ans = '({ans})'.format(ans=ans)
        result = ['/* CIF ANSWER ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{a}:'.format(a=ans, hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()))]
        if recursive:
            nextSymbol = self.nextAlignedSymbol()
            while nextSymbol:
                result.append(repr(nextSymbol))
                nextSymbol = nextSymbol.nextAlignedSymbol()
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        return self.pr()


class Join(VerticalSymbol):
    ''' JOIN symbol (GOTO) '''
    allowed_followers = []

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Terminator(defName='Goto', defCoord=[0, 0, 50, 50])
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(Join, self).__init__(polygon, parent, text=ast.inputString,
                y=coord_y, hyperlink=ast.hyperlink)
        self.setPen(QColor(0, 0, 0, 0))
        self.terminalSymbol = True
        self.arrowHead = True
        self.commonName = 'terminator_statement'
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Define the bouding rectangle of the JOIN symbol '''
        circ = min(width, height)
        bound = QRect(0, 0, circ, circ)
        polygon = QPolygon(bound)
        return polygon

    def paint(self, painter, _, __):
        ''' Draw the JOIN symbol - a circle '''
        rect = self.boundingRect()
        painter.setPen(Qt.blue)
        painter.drawEllipse(rect)
        super(Join, self).paint(painter, _, __)

    def __repr__(self):
        ''' Return the PR string for the join '''
        return ('/* CIF JOIN ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'JOIN {label};'.format(label=str(self),
                    hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


class Label(VerticalSymbol):
    ''' LABEL symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Join', 'Label', 'State']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Label()
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(Label, self).__init__(polygon, parent, text=ast.inputString,
                y=coord_y, hyperlink=ast.hyperlink)
        self.setPen(QColor(0, 0, 0, 0))
        self.terminalSymbol = False
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.commonName = 'label'
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Define the boundaries of the LABEL symbol '''
        return QPolygon(QRect(0, 0, width, height))

    def paint(self, painter, _, __):
        ''' Draw the LABEL symbol within its boundaries '''
        rect = self.boundingRect()
        painter.setPen(Qt.blue)
        painter.drawEllipse(0, rect.height() / 2,
                rect.width() / 4, rect.height() / 2)
        painter.drawLine(rect.width() / 4, rect.height() * 3 / 4,
                rect.width() / 2, rect.height() * 3 / 4)
        # Add arrow head
        painter.drawLine(rect.width() / 2 - 5, rect.height() * 3 / 4 - 5,
                rect.width() / 2, rect.height() * 3 / 4)
        painter.drawLine(rect.width() / 2 - 5, rect.height() * 3 / 4 + 5,
                rect.width() / 2, rect.height() * 3 / 4)
        # Add vertical line in the middle of the symbol
        painter.drawLine(rect.width() / 2, 0,
                rect.width() / 2, rect.height())
        super(Label, self).paint(painter, _, __)

    def __repr__(self):
        ''' Return the PR string for the label '''
        return ('/* CIF LABEL ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{label}:'.format(label=str(self), hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


class Condition(VerticalSymbol):
    ''' Condition is below an INPUT - It's not a continuous signal '''
    # NOT SUPPORTED (Makes no sense in code generation) '''
    def __init__(self, parent=None, text='Provided', y=None,
            w=None, h=None, hyperlink=None):
        w = w or 100
        h = h or 50
        polygon = self.computePolygon(w, h)
        super(Condition, self).__init__(polygon, parent, text=text,
                y=y, hyperlink=hyperlink)
        self.setPen(QColor(0, 0, 0, 0))
        self.terminalSymbol = False
        self.allowed_followers = [Task, ProcedureCall, Output, Decision,
                Join, Label, State]
        self.commonName = 'condition'
        self.parser = ogParser

    def __str__(self):
        return str(self.text)

    def computePolygon(self, width, height):
        bound = QRect(0, 0, width, height)
        polygon = QPolygon(bound)
        return polygon

    def paint(self, painter, _, __):
        #font = QFont()
        #font.setPixelSize(40)
        #painter.setFont(font)
        rect = self.boundingRect()
        painter.drawLines([QPoint(10, 0), QPoint(0, rect.height() / 2),
                           QPoint(0, rect.height() / 2),
                           QPoint(10, rect.height())])
        painter.drawLines([QPoint(rect.width() - 10, 0),
                           QPoint(rect.width(), rect.height() / 2),
                           QPoint(rect.width(), rect.height() / 2),
                           QPoint(rect.width() - 10, rect.height())])
        super(Condition, self).paint(self, painter, _, __)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        return ('/* CIF PROVIDED ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'PROVIDED {p}{comment}'.format(p=str(self.text),
                    hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


class Task(VerticalSymbol):
    ''' TASK symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Join', 'Label', 'Comment', 'State']

    def __init__(self, parent=None, ast=None):
        ''' Initializes the TASK symbol '''
        ast = ast or ogAST.Task()
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(Task, self).__init__(polygon, parent, text=ast.inputString,
                y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminalSymbol = False
        self.commonName = 'task'
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        polygon = QPolygon()
        polygon << QPoint(0, 0) \
                << QPoint(width, 0) \
                << QPoint(width, height) \
                << QPoint(0, height) \
                << QPoint(0, 0)
        return polygon

    def completionList(self):
        ''' Return the list of defined INPUTs for the autocompletion '''
        return varCompletionList

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        return ('/* CIF TASK ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'TASK {t}{comment}'.format(t=str(self.text),
                    hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


class ProcedureCall(VerticalSymbol):
    ''' PROCEDURE CALL symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Join', 'Label', 'Comment', 'State']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Output(defName='callMe')
        _, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(ProcedureCall, self).__init__(polygon, parent,
                text=ast.inputString, y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(255, 255, 202)))
        self.terminalSymbol = False
        self.commonName = 'procedure_call'
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        polygon = QPolygon()
        polygon << QPoint(0, 0) \
                << QPoint(width, 0) \
                << QPoint(width, height) \
                << QPoint(0, height) \
                << QPoint(0, 0) \
                << QPoint(width - 7, 0) \
                << QPoint(width - 7, height) \
                << QPoint(7, height) \
                << QPoint(7, 0)
        return polygon

    def completionList(self):
        ''' Return the list of defined procedures for the autocompletion '''
        return procCompletionList

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        return ('/* CIF PROCEDURE ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'CALL {p}{comment}'.format(p=str(self.text),
                    hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))


class TextSymbol(HorizontalSymbol):
    ''' Text symbol - used to declare variables, etc. '''
    allowed_followers = []

    def __init__(self, ast=None):
        ''' Create a Text Symbol '''
        ast = ast or ogAST.TextArea()
        coord_x, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(TextSymbol, self).__init__(polygon, parent=None,
                text=ast.inputString,
                x=coord_x, y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(249, 249, 249)))
        self.terminalSymbol = False
        self.setPos(coord_x, coord_y)
        # Disable hyperlinks for Text symbols
        self._no_hyperlink = True
        # Text is not centered in the box - change default alignment:
        self.textbox_alignment = Qt.AlignLeft | Qt.AlignTop
        self.commonName = 'text_area'
        self.parser = ogParser

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def computePolygon(self, width, height):
        ''' Define the polygon of the text symbol '''
        polygon = QPolygon()
        polygon << QPoint(width - 10, 0) \
                << QPoint(0, 0) \
                << QPoint(0, height) \
                << QPoint(width, height) \
                << QPoint(width, 10) \
                << QPoint(width - 10, 10) \
                << QPoint(width - 10, 0) \
                << QPoint(width, 10)
        return polygon

    def completionList(self):
        ''' Return the list of defined ASN.1 datatypes for autocompletion '''
        return typesCompletionList

    def resizeItem(self, rect):
        ''' Text Symbol only resizes in one direction '''
        self.prepareGeometryChange()
        polygon = self.computePolygon(rect.width(), rect.height())
        self.setPolygon(polygon)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        return ('/* CIF TEXT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                '{text}\n'
                '/* CIF ENDTEXT */'.format(text=str(self.text),
                    hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height())))


class State(VerticalSymbol):
    ''' SDL STATE Symbol '''
    allowed_followers = ['Input', 'Comment']

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.State()
        # Note: ast coordinates are in scene coordinates
        coord_x, coord_y, width, height = ast.coordinates
        polygon = self.computePolygon(width, height)
        super(State, self).__init__(polygon=polygon, parent=parent,
                text=ast.inputString, y=coord_y, hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        self.arrowHead = True
        self.terminalSymbol = True
        if parent:
            # Change to parent coordinates
            self.setPos(parent.mapFromScene(coord_x, coord_y))
            self.setPos(self.mapFromScene(coord_x, coord_y))
            #print 'Set nextState pos to', self.pos()
            #print coord_x, coord_y, self.mapFromScene(coord_x, coord_y)
        else:
            # Use scene coordinates to position
            self.setPos(coord_x, coord_y)
        self.parser = ogParser
        self.commonName = 'terminator_statement'
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' Return the text string as entered by the user '''
        return str(self.text)

    def checkSyntax(self):
        ''' Redefined function, to distinguish STATE and NEXTSTATE '''
        if self.hasParent:
            super(State, self).checkSyntax()
        else:
            _, syntaxErrors, __, ___, ____ = self.parser.parseSingleElement(
                    'state', self.parseGR(recursive=False))
            try:
                self.scene().reportErrors(syntaxErrors)
            except:
                print('[SYNTAX ERROR]', '\n'.join(syntaxErrors))

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        statePath = QPainterPath()
        statePath.addRoundedRect(0, 0, width, height, 15, 50)
        return statePath.toFillPolygon()

    def completionList(self):
        ''' Return the list of defined STATEs for the autocompletion '''
        return stateCompletionList

    def get_ast(self):
        ''' Redefinition of the get_ast function for the state '''
        if self.hasParent and not [c for c in self.childSymbols()
                if not isinstance(c, Comment)]:
            # Terminator case
            return super(State, self).get_ast()
        else:
            # State case
            ast, _, __, ___, terminators = self.parser.parseSingleElement(
                'state', self.parseGR(recursive=True))
            return ast, terminators

    def parseGR(self, recursive=True):
        ''' Parse state '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        if self.hasParent and not [s for s in self.childSymbols() if
                                   not isinstance(s, Comment)]:
            # Do not generate a new STATE when there is no need
            # FIXME: check if childSymbol is a commment
            return ''
        result = ['/* CIF STATE ({x}, {y}), ({w}, {h}) */\n'
                    '{hlink}'
                    'STATE {state}{comment}'.format(
                        state=str(self),
                        hlink=repr(self.text),
                        x=int(self.scenePos().x()), y=int(self.scenePos().y()),
                        w=int(self.boundingRect().width()),
                        h=int(self.boundingRect().height()), comment=comment)]
        if recursive:
            for i in self.childSymbols():
                # Recursively return next symbols (inputs)
                if isinstance(i, Input):
                    result.append(repr(i))
        result.append('ENDSTATE;')
        return '\n'.join(result)

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        result = ['/* CIF NEXTSTATE ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'NEXTSTATE {state}{comment}'.format(
                    state=str(self),
                    hlink=repr(self.text),
                    x=int(self.scenePos().x()), y=int(self.scenePos().y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment)]
        return '\n'.join(result)


class Start(HorizontalSymbol):
    ''' SDL START Symbol '''
    allowed_followers = ['Task', 'ProcedureCall', 'Output', 'Decision',
                        'Join', 'Label', 'Comment', 'State']

    def __init__(self, ast=None):
        ast = ast or ogAST.Start()
        coord_x, coord_y, width, height = ast.coordinates
        self.terminalSymbol = False
        polygon = self.computePolygon(width, height)
        super(Start, self).__init__(polygon, parent=None, text='',
                x=coord_x, y=coord_y,
                hyperlink=ast.hyperlink)
        self.setBrush(QBrush(QColor(255, 228, 213)))
        # No hyperlink for START symbol because it has no text
        self._no_hyperlink = True
        self.commonName = 'start'
        self.parser = ogParser
        if ast.comment:
            Comment(parent=self, ast=ast.comment)

    def __str__(self):
        ''' User cannot enter text in the START symbol - Return dummy text '''
        return 'START'

    def computePolygon(self, width, height):
        ''' Compute the polygon to fit in width, height '''
        path = QPainterPath()
        path.addRoundedRect(0, 0, width, height, 25, 25)
        return path.toFillPolygon()

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        result = []
        comment = ';'
        if self.comment:
            comment = repr(self.comment)
        result.append('/* CIF START ({x}, {y}), ({w}, {h}) */\n'
                'START{comment}'.format(x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()), comment=comment))
        # Recursively return the complete branch below the start symbol
        nextSymbol = self.nextAlignedSymbol()
        while nextSymbol:
            result.append(repr(nextSymbol))
            nextSymbol = nextSymbol.nextAlignedSymbol()
        return '\n'.join(result)
