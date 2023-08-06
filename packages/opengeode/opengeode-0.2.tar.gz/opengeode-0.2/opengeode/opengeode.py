#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny, free SDL Editor for TASTE

    SDL is the Specification and Description Language (Z100 standard from ITU)

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""

# Added to please py2exe - NOQA makes flake8 ignore the following lines:
import antlr3  # NOQA
import antlr3.tree  # NOQA
import importlib  # NOQA
import PySide  # NOQA
import PySide.QtCore  # NOQA
import PySide.QtGui  # NOQA
import PySide.QtUiTools  # NOQA
#import generatorc  # NOQA
#import generator  # NOQA
import undoCommands  # NOQA
import sdl92Lexer  # NOQA
import sdl92Parser  # NOQA
import genericSymbols  # NOQA
import PySide.QtXml  # NOQA

from PySide.QtCore import Qt, QSize, QFile, QIODevice, Signal, QRectF
from PySide.QtGui import(QGraphicsScene, QApplication, QToolBar, QIcon,
        QGraphicsView, QKeySequence, QUndoStack, QFileDialog, QBrush,
        QWidget, QDockWidget, QListWidget, QImage, QListWidgetItem,
        QPainter, QAction, QMessageBox, QMainWindow, QPen, QColor)

from PySide.QtUiTools import QUiLoader

import sdlSymbols
from genericSymbols import(Symbol, VerticalSymbol, Connection, Comment,
        EditableText)
from sdlSymbols import(Input, Output, Decision, DecisionAnswer, Task,
        ProcedureCall, TextSymbol, State, Start, Join, Label)

from undoCommands import InsertSymbol, DeleteSymbol

# Icons and png files generated from the resource file:
import icons  # NOQA

#from generatorc import Generator
import AdaGenerator

import ogParser
import ogAST

import signal
import sys
import os
import optparse

__all__ = ['opengeode']

if hasattr(sys, 'frozen'):
    CUR_DIR = os.path.dirname(unicode
            (sys.executable, sys.getfilesystemencoding()))
else:
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))

# MAIN_UI_FILE = os.path.join(CUR_DIR, 'opengeode.ui')


# Global handling all top-level elements
# It seems that if we don't keep a global list of these elements
# (START, STATE, and Text symbols)
# they sometimes get destroyed and disappear from the scene.
# As if a GC was deleting these object *even if they belong to the scene*
# (but have no parentItem). This may be a Qt bug - to be investigated
# If this theory proves to be correct, then this list has to be properly
# updated (when user deletes a state, etc.)
G_SYMBOLS = set()

PROCESS_NAME = 'opengeode'

# Copy-Cut-Paste Buffer (a number of elements can be copied)
COPY_PASTE = []


class sdlToolBar(QToolBar):
    ''' Toolbar with SDL symbols '''
    def __init__(self, parent):
        super(sdlToolBar, self).__init__(parent)
        self.setMovable(True)
        self.setFloatable(True)
        #self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(40, 40))
        # Removed 'Condition' below (not supported by the parser)
        self.itemsList = [Start, State, Input, Task, Decision, DecisionAnswer,
                Output, ProcedureCall, TextSymbol, Comment, Label, Join]
        self.actions = {}
        for item in self.itemsList:
            itemStr = item.__name__
            self.actions[itemStr] = self.addAction(QIcon(':/{icon}'.format(
                icon=itemStr.lower()+'.png')), itemStr)
            #self.actions[itemStr] = self.addAction(QIcon(os.path.join(
            #    CUR_DIR, itemStr.lower()+'.png')), itemStr)
            self.addSeparator()
        # There can be only one START symbol - 'startIsPossible' verifies it.
        self.startIsPossible = True
        self.updateMenu()
        #self.setStyleSheet('QToolBar::handle{background: lightgrey;}')

    def enableAction(self, action):
        ''' Used as a slot to allow a scene to enable a menu action,
            e.g. if the Start symbol is deleted, the Start button
            shall be activated '''
        self.actions[action].setEnabled(True)
        if action == 'Start':
            self.startIsPossible = True

    def disableAction(self, action):
        ''' See description in enableAction '''
        self.actions[action].setEnabled(False)
        if action == 'Start':
            self.startIsPossible = False

    def updateMenu(self):
        ''' Context-dependent enabling/disabling of menu buttons '''
        if self.sender():
            selection = self.sender().selectedItems()
        else:
            selection = []
        if len(selection) > 1:
            # When several items are selected, disable all menu entries
            for name, action in self.actions.viewitems():
                action.setEnabled(False)
                return
        elif not selection:
            # When nothing is selected:
            # activate everything, and when user selects an icon,
            # keep the action on hold until he clicks on the scene
            for action in self.actions.viewkeys():
                self.actions[action].setEnabled(True)

            # Check if there is already a Start symbol and if not,
            # enable the menu entry:
            self.actions['Start'].setEnabled(self.startIsPossible)
        else:
            # Only one selected item
            selection, = selection  # [0]
            for action in self.actions.viewkeys():
                self.actions[action].setEnabled(False)
            for action in type(selection).allowed_followers:
                self.actions[action].setEnabled(True)
            # Allow only one comment per symbol
            if selection.comment:
                self.actions['Comment'].setEnabled(False)
            # Disable the 'State' button if any symbol is already
            # following the selected symbol
            if filter(lambda c: isinstance(c, VerticalSymbol),
                    selection.childSymbols()):
                self.actions['State'].setEnabled(False)
                self.actions['Join'].setEnabled(False)


class sdlScene(QGraphicsScene):
    ''' Main graphic scene (canvas) where the user can place SDL symbols '''
    enableMenuItem = Signal(str)
    disableMenuItem = Signal(str)

    def __init__(self):
        super(sdlScene, self).__init__()
        self.state = ''
        # Configure the action menu
        self.actions = {
                'Start': self.addStart,
                'State': lambda: self.insertConnectedItem(State),
                'Join': lambda: self.insertConnectedItem(Join),
                'Label': lambda: self.insertConnectedItem(Label),
                'Input': self.addInput,
                'Task': lambda: self.insertConnectedItem(Task),
                'Decision': self.addDecision,
                'DecisionAnswer': self.addAnswer,
                'Output': lambda: self.insertConnectedItem(Output),
                'ProcedureCall': lambda: self.insertConnectedItem(
                    ProcedureCall),
                'TextSymbol': self.addText,
                'Comment': lambda: self.insertConnectedItem(Comment)
        }
        # Create a stack for handling undo/redo commands
        # (defined in undoCommands.py)
        self.undoStack = QUndoStack(self)
        # buttonSelected is used to set which symbol to draw
        # on next scene click (see mousePressEvent)
        self.buttonSelected = None
        self.setBackgroundBrush(QBrush(QImage(':/texture.png')))
        #self.setBackgroundBrush(QBrush(QImage(os.path.join
        #    (CUR_DIR, 'texture.png'))))
        self.messagesWindow = None
        self.click_coordinates = None

    def reportErrors(self, errors=[]):
        ''' Display an syntax error pop-up message '''
        if not errors:
            return
        for view in self.views():
            errs = []
            for e in errors:
                split = e.split()
                if split[0] == 'line' and len(split)>1:
                    lineCol = split[1].split(':')
                    if len(lineCol) == 2:
                        # Get line number and column..to locate error (TODO)
                        lineNb, col = lineCol
                        errs.append(' '.join(split[2:]))
                    else:
                        errs.append(e)
                else:
                    errs.append(e)
            msgBox = QMessageBox(view)
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.setWindowTitle('OpenGEODE - Syntax Error')
            msgBox.setInformativeText('\n'.join(errs))
            msgBox.setText("Syntax error!")
            msgBox.setStandardButtons(QMessageBox.Discard)
            msgBox.setDefaultButton(QMessageBox.Discard)
            msgBox.exec_()

    def showItem(self, item):
        '''
        Select an item and make sure it is visible
        (used when user clicks on a warning or error to locate the symbol)
        '''
        absCoordinates = item.data(Qt.UserRole)
        if not absCoordinates:
            return
        else:
            x, y = absCoordinates
        item = self.itemAt(x, y)
        if item:
            self.clearSelection()
            self.clearFocus()
            item.setSelected(True)
            item.ensureVisible()

    def delete_selected_symbols(self):
        '''
            Remove selected symbols from the scene, with proper re-connections
        '''
        self.undoStack.beginMacro('Delete items')
        for item in self.selectedItems():
            if not item.scene():
                # Ignore if item has already been deleted
                # (in case of multiple selection)
                continue
            undoCmd = DeleteSymbol(item)
            self.undoStack.push(undoCmd)
            if isinstance(item, Start):
                self.enableMenuItem.emit('Start')
        self.undoStack.endMacro()

    def copy_selected_symbols(self):
        '''
            Create a copy of selected symbols to a buffer (in AST form)
            Called when user presses Ctrl-C
        '''
        global COPY_PASTE
        COPY_PASTE = []
        branch_top_level = []
        floating_items = []
        self.click_coordinates = None
        for item in self.selectedItems():
            # When several items are selected, take the first of each subbranch
            if item.hasParent and not item.parentItem().isSelected():
                branch_top_level.append(item)
            elif not item.hasParent and not isinstance(item, Start):
                # Take also floating items, but not the Start symbol
                # (which cannot be duplicated)
                floating_items.append(item)
        # Check if selected items would allow a paste - reject copy otherwise
        # e.g. floating and non-floating items cannot be pasted together
        if ((branch_top_level == []) == (floating_items == []) or
                len(branch_top_level) > 1):
            print 'Selection is incompatible with copy'
            return False
        # Then parse/copy the selected branches
        for item in branch_top_level+floating_items:
            branch_ast, terminators = self.copy_branch(item)
            translation = item.scenePos()
            # Translate all top symbols to a 0,0-based coordinates sysyem
            for item in branch_ast:
                item.coordinates[0] -= translation.x()
                item.coordinates[1] -= translation.y()
            # Translate all terminators for to have consistent coordinates
            for t in terminators:
                t.coordinates[0] -= translation.x()
                t.coordinates[1] -= translation.y()
            COPY_PASTE.append((branch_ast, terminators))
        # print 'COPY-PASTE LIST:', COPY_PASTE
        return True

    def copy_branch(self, top_level_item):
        ''' Copy branches (recursively) '''
        res_terminators = []
        item_ast, terminators = top_level_item.get_ast()
        # print 'Copying', item_ast
        branch = [item_ast]
        if not isinstance(top_level_item, (Input, DecisionAnswer)):
            next_aligned = top_level_item.nextAlignedSymbol()
            while next_aligned and next_aligned in self.selectedItems():
                next_ast, next_terminators = next_aligned.get_ast()
                terminators.extend(next_terminators)
                branch.append(next_ast)
                next_aligned = next_aligned.nextAlignedSymbol()
        # Parse all terminators (in case they trigger new branches)
        res_terminators = terminators
        for t in terminators:
            # Get symbol at terminator coordinates
            symbols = self.items(QRectF(*t.coordinates).center())
            # Recursive parsing if symbol is a state with actual
            # children (i.e. inputs. not only a comment)
            for symbol in symbols:
                if (isinstance(symbol, State) and [c for c in
                    symbol.childSymbols() if isinstance(c, Input)]):
                    term_branch, term_inators = self.copy_branch(symbol)
                    branch.extend(term_branch)
                    res_terminators.extend(term_inators)
        return branch, res_terminators

    def cut_selected_symbols(self):
        '''
            Create a copy of selected symbols, then delete them
        '''
        if self.copy_selected_symbols():
            self.delete_selected_symbols()

    def paste_symbols(self):
        '''
            Paste previously copied symbols at selection point
        '''
        global G_SYMBOLS
        selection = self.selectedItems()
        if len(selection) > 1:
            print '[WARNING] Cannot paste when several items are selected'
        elif len(selection) == 0:
            print '[INFO] No selection, can only paste states and text areas'
            self.undoStack.beginMacro('Paste items')
            for item_list, terminators in COPY_PASTE:
                nextStatesCoord = self.nextstate_merge_list(terminators)
                states = [i for i in item_list if isinstance(i, ogAST.State)]
                textAreas = [i for i in item_list if
                        isinstance(i, ogAST.TextArea)]
                for i in states:
                    # print '[DEBUG] pasting state'
                    # First check if state has already been pasted
                    i_x, i_y = i.coordinates[0:2]
                    if((i_x, i_y) in nextStatesCoord.keys() and
                            isinstance(nextStatesCoord[(i_x, i_y)], State)):
                        continue
                    new_item = State(ast=i)
                    G_SYMBOLS.add(new_item)
                    if new_item not in self.items():
                        self.addItem(new_item)
                    undoCmd = InsertSymbol(
                            new_item, parent=None, pos=self.click_coordinates
                            or new_item.pos())
                    self.undoStack.push(undoCmd)
                    for inp in i.inputs:
                        inp = self.render_input_from_ast(
                                inp, parent=new_item, states=states,
                                nextStatesCoord=nextStatesCoord)
                    new_item.cam(new_item.pos(), new_item.pos())
                for i in textAreas:
                    # print '[DEBUG] Pasting text area'
                    new_item = TextSymbol(ast=i)
                    G_SYMBOLS.add(new_item)
                    if new_item not in self.items():
                        self.addItem(new_item)
                    undoCmd = InsertSymbol(
                            new_item, parent=None, pos=self.click_coordinates
                            or new_item.pos())
                    self.undoStack.push(undoCmd)
                    new_item.cam(new_item.pos(), new_item.pos())
            self.undoStack.endMacro()
        elif len(selection) == 1:
            parent_item = selection[0]
            self.undoStack.beginMacro('Paste items')
            for item_list, terminators in COPY_PASTE:
                nextStatesCoord = self.nextstate_merge_list(terminators)
                states = [i for i in item_list if isinstance(i, ogAST.State)]
                for i in [c for c in item_list if not isinstance
                        (c, (ogAST.State, ogAST.TextArea, ogAST.Start))]:
                    # print 'pasting', i
                    # Create the new item from the AST description
                    # If item to paste is an INPUT or a DECISION ANSWER,
                    # and the selected parent is of the same type,
                    # then select one parent above (STATE or DECISION)
                    if isinstance(i, ogAST.Input):
                        if isinstance(parent_item, Input):
                            parent_item = parent_item.parentItem()
                        new_item = self.render_input_from_ast(
                                i, parent=None, states=states,
                                nextStatesCoord=nextStatesCoord)
                    else:
                        if(isinstance(i, ogAST.Answer) and isinstance(
                            parent_item, DecisionAnswer)):
                            parent_item = parent_item.parentItem()
                        # special case: decision answers with transition
                        # must have a parent for the connection point to
                        # be properly updated
                        if(isinstance(i, ogAST.Answer) and isinstance(
                            parent_item, Decision) and i.transition):
                            new_item = self.render_action_from_ast(
                                    i, parent=parent_item, states=states,
                                    nextStatesCoord=nextStatesCoord)
                            if new_item.connection in self.items():
                                self.removeItem(new_item.connection)
                                new_item.connection = None
                        else:
                            new_item = self.render_action_from_ast(
                                    i, parent=None, states=states,
                                    nextStatesCoord=nextStatesCoord)
                    # Check that item is compatible with parent
                    if (type(new_item).__name__ not in
                            type(parent_item).allowed_followers):
                        print('[WARNING]'
                              ' Cannot paste here ({t1} cannot follow {t2}'
                              .format(t1=type(new_item), t2=type(parent_item)))
                        if new_item in self.items():
                            self.removeItem(new_item)
                            new_item.setParentItem(None)
                        break
                    # Create Undo command, actually inserting symbol
                    undoCmd = InsertSymbol(
                            new_item, parent_item, None)  # new_item.pos())
                    self.undoStack.push(undoCmd)
                    self.clearSelection()
                    self.clearFocus()
                    new_item.updateConnectionPointPosition()
                    new_item.updateConnectionPoints()
                    parent_item = new_item
            self.undoStack.endMacro()
        for view in self.views():
            view.viewport().update()

    def getPrData(self):
        ''' Parse the graphical items and returns a PR string '''
        pr = ['PROCESS ' + PROCESS_NAME + ';']
        # Separate the text boxes and START symbol from the states
        # (They need to be placed at the top of the .pr file
        topLevelItems = [i for i in self.items() if
                isinstance(i, (Start, State, TextSymbol))]
        textBoxes = filter(lambda x: isinstance(x, TextSymbol), topLevelItems)
        startState = filter(lambda x: isinstance(x, Start), topLevelItems)
        states = filter(lambda x: isinstance(x, State), topLevelItems)
        for item in textBoxes:
            pr.append(repr(item))
        if not startState:
            print ('[WARNING] START Symbol missing - '
                   'Saving dummy state to comply with the SDL syntax')
            pr.append('START;')
            pr.append('NEXTSTATE Dummy;')
        else:
            pr.append(repr(startState[0]))
        for item in states:
            pr.append(item.parseGR())
        pr.append('ENDPROCESS ' + PROCESS_NAME + ';')
        return str('\n'.join(pr))

    def mousePressEvent(self, event):
        '''
            Handle mouse click on the scene:
            If a symbol was selected in the menu, check if it can be inserted
            Otherwise store the coordinates, in which case if the user does
            a paste action with floating items, they will be placed there.
        '''
        if self.buttonSelected:
            parent_item, follower_item = None, None
            items_at_click_point = self.items(event.scenePos())
            symbol_items = [i for i in items_at_click_point if
                    isinstance(i, Symbol)]
            if len(symbol_items) == 1:
                parent_item, = symbol_items  # [0]
                follower_item = parent_item.nextAlignedSymbol()
            try:
                # Check that parent accepts selection as follower
                compatible_insert = (self.buttonSelected.__name__ in
                        type(parent_item).allowed_followers)
                # Comment: allow only one per symbol:
                if(self.buttonSelected == Comment and parent_item.comment):
                    compatible_insert = False
                # Check chat child of newly inserted item is compatible
                if(follower_item and compatible_insert and
                        self.buttonSelected != Comment):
                    compatible_insert = (type(follower_item).__name__ in
                        self.buttonSelected.allowed_followers)
            except:
                if not parent_item and self.buttonSelected in (
                        Start, State, TextSymbol):
                    compatible_insert = True
                else:
                    compatible_insert = False
            if not compatible_insert:
                print '[DEBUG] Incompatible insersion'
                self.buttonSelected = None
                return
            if self.buttonSelected == Start:
                self.placeStart(event.scenePos())
            elif self.buttonSelected == State:
                self.placeConnectedItem(self.buttonSelected,
                        parent_item, event.scenePos()
                        if not parent_item else None)
            elif self.buttonSelected in (Join, Task, Output,
                    ProcedureCall, Label):
                self.placeConnectedItem(self.buttonSelected, parent_item)
            elif self.buttonSelected == Comment:
                if not parent_item.comment:
                    self.placeConnectedItem(self.buttonSelected, parent_item)
            elif self.buttonSelected == Input:
                self.placeInput(parent_item)
            elif self.buttonSelected == Decision:
                self.placeDecision(parent_item)
            elif self.buttonSelected == DecisionAnswer:
                self.placeAnswer(parent_item)
            elif self.buttonSelected == TextSymbol:
                self.placeText(event.scenePos())
            self.buttonSelected = None
        else:
            self.click_coordinates = event.scenePos()
            super(sdlScene, self).mousePressEvent(event)

    def keyPressEvent(self, keyEvent):
        ''' Handle keyboard: Delete, Undo/Redo '''
        if keyEvent.matches(QKeySequence.Delete) and self.selectedItems():
            self.delete_selected_symbols()
            self.clearSelection()
            self.clearFocus()
        elif keyEvent.matches(QKeySequence.Undo):
            if not isinstance(self.focusItem(), EditableText):
                self.undoStack.undo()
        elif keyEvent.matches(QKeySequence.Redo):
            self.undoStack.redo()
        elif keyEvent.matches(QKeySequence.Copy):
            self.copy_selected_symbols()
        elif keyEvent.matches(QKeySequence.Cut):
            self.cut_selected_symbols()
        elif keyEvent.matches(QKeySequence.Paste):
            self.paste_symbols()
        elif (keyEvent.key() == Qt.Key_J and
                keyEvent.modifiers() == Qt.ControlModifier):
            # Debug mode
            for s in self.selectedItems():
                print repr(s)
                print 'Position:', s.pos()
        super(sdlScene, self).keyPressEvent(keyEvent)

    def placeStart(self, pos):
        '''
            Place the Start button on the scene upon user click
            (called by mousePressEvent)
        '''
        self.undoStack.beginMacro('Place Start Symbol')
        start = Start()
        if start not in self.items():
            self.addItem(start)
        undoCmd = InsertSymbol(start, parent=None, pos=pos)
        self.undoStack.push(undoCmd)
        global G_SYMBOLS
        G_SYMBOLS.add(start)
        self.clearSelection()
        self.clearFocus()
        start.setSelected(True)
        self.disableMenuItem.emit('Start')
        start.cam(pos, pos)
        self.undoStack.endMacro()

    def addStart(self):
        '''
            User selected the Start icon.
            Symbol will be added on next scene click
        '''
        self.buttonSelected = Start
        self.messagesWindow.clear()
        self.messagesWindow.addItem(
                'Hint: Click on the diagram to place the START symbol')

    def placeInput(self, parent):
        ''' Place an INPUT symbol on the scene '''
        self.clearSelection()
        self.clearFocus()
        if isinstance(parent, Input):
            local_select = parent
            parentState = local_select.parentItem()
        else:
            parentState = parent
        # Add parent state to the list of global symbols
        # This is mandatory for the PR parsing to allow merging
        # STATE and NEXTSTATE symbols
        global G_SYMBOLS
        G_SYMBOLS.add(parentState)
        parentState.setSelected(True)
        self.insertConnectedItem(Input)

    def addInput(self):
        ''' Add an INPUT symbol to the scene '''
        selection = self.selectedItems()
        if not selection:
            # Menu item clicked but no symbol selected ->
            # store until user clicks on the scene
            self.buttonSelected = Input
            return None
        elif len(selection) > 1:
            self.buttonSelected = None
            return None
        else:
            selection, = selection  # [0]
            self.undoStack.beginMacro('Add Input')
            self.placeInput(parent=selection)
            self.undoStack.endMacro()

    def placeConnectedItem(self, itemType, parent, pos=None):
        ''' Draw a connected item on the scene '''
        self.undoStack.beginMacro('Place Item')
        item = itemType()
        # Add the item to the scene
        if item not in self.items():
            self.addItem(item)
        # Create Undo command (makes the call to the insertSymbol function):
        undoCmd = InsertSymbol(item, parent, pos)
        self.undoStack.push(undoCmd)
        self.clearSelection()
        self.clearFocus()
        # If no item is selected (e.g. new STATE), add it to the scene
        if not parent:
            global G_SYMBOLS
            G_SYMBOLS.add(item)
        item.setSelected(True)
        item.cam(item.pos(), item.pos())
        self.undoStack.endMacro()
        for view in self.views():
            view.viewport().update()
            view.ensureVisible(item)
        return item

    def insertConnectedItem(self, itemType):
        ''' Add or insert a state machine item '''
        selection = self.selectedItems()
        msg = ''
        if not selection:
            # Menu item clicked but no symbol selected
            # -> store until user clicks on the scene
            self.messagesWindow.clear()
            if itemType == State:
                msg = ('Click on the diagram to place the State, or '
                       'click on an existing symbol to attach the state below')
            elif itemType == Task:
                msg = ('Click on the task parent symbol.\n'
                        'A task is used for assignations or informal text\n'
                        'Assignation syntax: variable := value\n'
                        'Use the ASN.1 Value notation for complex types\n'
                        'e.g. a ::= { name "Guybrush Threepwood", age 35 }\n\n'
                        'For informal text, use single quotes: \'Hello\'')
            elif itemType == Output:
                msg = ('Click on the output parent symbol\n'
                        'An output is used to send a sporadic message, '
                        'and can have one parameter')
            elif itemType == ProcedureCall:
                msg = ('Click on the procedure parent symbol\n'
                        'A procedure is a synchronous function call, '
                        'that can take several input and output parameters\n')

            self.messagesWindow.addItem(msg)
            self.buttonSelected = itemType
            return None
        elif len(selection) > 1:
            # Ignore the insertion if there is more than one item selected
            self.buttonSelected = None
            return None
        else:
            selection, = selection
            return self.placeConnectedItem(itemType, parent=selection)

    def addDecision(self):
        ''' User clicked on the DECISION icon '''
        selection = self.selectedItems()
        if not selection:
            # Menu item clicked but no symbol selected
            # -> store until user clicks on the scene
            self.buttonSelected = Decision
            return
        elif len(selection) > 1:
            self.buttonSelected = None
            return
        else:
            selection, = selection  # [0]
            self.placeDecision(parent=selection)

    def placeDecision(self, parent):
        ''' Place a DECISION and two ANSWERS on the scene '''
        self.clearSelection()
        self.clearFocus()
        parent.setSelected(True)
        self.undoStack.beginMacro('Add Decision')
        item = self.insertConnectedItem(Decision)
        self.addAnswer()
        self.addAnswer()
        self.undoStack.endMacro()
        self.clearSelection()
        self.clearFocus()
        item.setSelected(True)

    def addAnswer(self):
        ''' User clicked on the ANSWER icon '''
        selection = self.selectedItems()
        if not selection:
            # Menu item clicked but no symbol selected
            # -> store until user clicks on the scene
            self.buttonSelected = DecisionAnswer
            return None
        elif len(selection) > 1:
            self.buttonSelected = None
            return None
        else:
            selection, = selection
            return self.placeAnswer(parent=selection)

    def placeAnswer(self, parent):
        ''' Place an ANSWER symbol on the scene below a decision '''
        self.clearSelection()
        self.clearFocus()
        if isinstance(parent, DecisionAnswer):
            local_select = parent
            local_select.parentItem().setSelected(True)
        else:
            parent.setSelected(True)
        return self.insertConnectedItem(DecisionAnswer)

    def addText(self):
        ''' User clicked on the TEXT icon '''
        self.buttonSelected = TextSymbol
        self.messagesWindow.clear()
        self.messagesWindow.addItem(
                'Hint: Click on the diagram to place the text area\n'
                'A text area is used to declare variables or place comments\n'
                'To declare a variable: \'DCL variableName TypeName;\'\n'
                'To add some comments: -- my comment')

    def placeText(self, pos):
        text = TextSymbol()
        self.addItem(text)
        self.undoStack.beginMacro('Place Text Symbol')
        undoCmd = InsertSymbol(text, parent=None, pos=pos)
        self.undoStack.push(undoCmd)
        global G_SYMBOLS
        G_SYMBOLS.add(text)
        text.setPos(pos.x(), pos.y())
        self.clearSelection()
        self.clearFocus()
        text.setSelected(True)
        text.cam(pos, pos)
        self.undoStack.endMacro()

    def nextstate_merge_list(self, terminators):
        '''
            Build up a list of nextstate coordinates to merge state
            and nextate symbols when they have the same coordinates
            Note: We are working in scene coordinates here
        '''
        next_states_coord = {}

        for t in terminators:
            if t.coordinates and t.kind == 'next_state':
                next_states_coord[
                        (t.coordinates[0], t.coordinates[1])] = t.inputString
        return next_states_coord

    def add_process_from_ast(self, process):
        ''' Render a process from the PR-parsed AST on the graphics scene '''
        global G_SYMBOLS
        for ta in process.textAreas:
            text = TextSymbol(ast=ta)
            G_SYMBOLS.add(text)
            if text not in self.items():
                self.addItem(text)

        # Set autocompletion lists for input, output, state, types, variables:
        if process.dataView:
            sdlSymbols.typesCompletionList = [
                    t.replace('-', '_') for t in process.dataView]
        sdlSymbols.stateCompletionList = [
                s for s in process.mapping if s != 'START']
        sdlSymbols.inputCompletionList = process.inputSignals.keys()
        sdlSymbols.outputCompletionList = process.outputSignals.keys()
        sdlSymbols.varCompletionList = process.variables.keys()
        sdlSymbols.procCompletionList = process.procedures.keys()

        nextStatesCoord = self.nextstate_merge_list(process.terminators)

        if process.start:
            self.render_start_from_ast(
                    process.start, process.states, nextStatesCoord)

        for s in process.states:
            sx, sy, sw, sh = s.coordinates or (0, 0, 100, 50)
            if (sx, sy) in nextStatesCoord and isinstance(
                    nextStatesCoord[(sx, sy)], State) and str(
                            nextStatesCoord[(sx, sy)].text) == s.inputString:
                state = nextStatesCoord[(sx, sy)]
            else:
                # Here sx and sy are in scene coordinates
                state = State(parent=None, ast=s)
                if (sx, sy) in nextStatesCoord and (
                        s.inputString == nextStatesCoord[(sx, sy)]):
                    nextStatesCoord[(sx, sy)] = state
                if state not in self.items():
                    self.addItem(state)

                for i in s.inputs:
                    self.render_input_from_ast(i, state,
                            process.states, nextStatesCoord)
            # Add state to the global list of symbols
            G_SYMBOLS.add(state)

    def render_transition_from_ast(self, parent, t, states, nextStatesCoord):
        ''' Add a transition to the diagram, from the PR-parsed AST '''
        for a in t.actions:
            parent = self.render_action_from_ast(a, parent, states,
                    nextStatesCoord=nextStatesCoord)

        if t.terminator:
            self.render_terminator_from_ast(t.terminator, parent, states,
                    nextStatesCoord)

    def render_terminator_from_ast(self, t, parent, states, nextStatesCoord):
        '''
            Add a terminator to the scene, from the AST, and in the case of a
            NEXTSTATE, possibly merge it with a defined STATE
        '''
        if t.label:
            parent = self.render_action_from_ast(
                    t.label, parent, states,
                    nextStatesCoord=nextStatesCoord)
        if t.kind == 'next_state':
            tx, ty, tw, th = t.coordinates or (None, None, None, None)
            st = None
            # Check if the nextstate symbol coincides with a state
            # symbol with the same name and merge them if so.
            if (tx, ty) in nextStatesCoord and (
                    isinstance(nextStatesCoord[(tx, ty)], State)
                    and t.inputString == str(nextStatesCoord[(tx, ty)].text)):
                st = nextStatesCoord[(tx, ty)]
                st.setParentItem(parent)
                st.hasParent = True
                st.parent = parent
                st.setPos(parent.mapFromScene(tx, ty))
                st.connection = Connection(parent, st)
            else:
                # State has not been created yet - create it now
                # print 'Creating state', t.inputString
                st = State(parent=parent, ast=t)
                nextStatesCoord[(tx, ty)] = st
                # Check if a corresponding state with inputs exists
                # If so, render the inputs too.
                try:
                    # if no states are defined ignore
                    for s in states:
                        if (s.inputString == t.inputString and
                                s.coordinates == t.coordinates):
                            for i in s.inputs:
                                self.render_input_from_ast(i, st, states,
                                        nextStatesCoord=nextStatesCoord)
                except:
                    pass

        elif t.kind == 'join':
            st = Join(parent=parent, ast=t)
            st.updateConnectionPoints()
        else:
            print '[Load ERROR] Unsupported terminator:', t
            return

    def render_action_from_ast(self, a, parent, states, nextStatesCoord):
        ''' Render a symbol on the scene '''
        if isinstance(a, ogAST.Task):
            task = Task(parent=parent, ast=a)
            task.updateConnectionPoints()
            new_parent = task
        elif isinstance(a, ogAST.Output):
            if a.kind == 'output':
                outCall = Output(parent=parent, ast=a)
            elif a.kind == 'procedure_call':
                outCall = ProcedureCall(parent=parent, ast=a)
            new_parent = outCall
            outCall.updateConnectionPoints()
        elif isinstance(a, ogAST.Decision):
            d = Decision(parent=parent, ast=a)
            if d not in self.items():
                # Add the decision to the scene, so that the connection
                # point can be updated properly
                self.addItem(d)
            d.updateConnectionPoints()
            new_parent = d
            for branch in a.answers:
                self.render_action_from_ast(
                        branch, new_parent, states, nextStatesCoord)
        elif isinstance(a, ogAST.Label):
            l = Label(parent=parent, ast=a)
            l.updateConnectionPoints()
            new_parent = l
        elif isinstance(a, ogAST.Answer):
            ans = DecisionAnswer(parent=parent, ast=a)
            ans.updateConnectionPoints()
            if a.transition:
                self.render_transition_from_ast(parent=ans,
                        t=a.transition,
                        states=states,
                        nextStatesCoord=nextStatesCoord)
            new_parent = ans
        elif isinstance(a, ogAST.Terminator):
            self.render_terminator_from_ast(a, parent, states, nextStatesCoord)
        else:
            print '[ERROR] Unsupported symbol in branch:', a
            return None
        return new_parent

    def render_start_from_ast(self, s, states, nextStatesCoord):
        start = Start(ast=s)
        if start not in self.items():
            self.addItem(start)
        G_SYMBOLS.add(start)
        self.disableMenuItem.emit('Start')
        if s.transition:
            self.render_transition_from_ast(parent=start,
                    t=s.transition,
                    states=states,
                    nextStatesCoord=nextStatesCoord)

    def render_input_from_ast(self, i, parent, states, nextStatesCoord):
        ''' Add input from the AST to the scene '''
        # Note: PROVIDED clause is not supported
        inp = Input(parent=parent, ast=i)
        if inp not in self.items():
            self.addItem(inp)
        if i.transition:
            self.render_transition_from_ast(parent=inp,
                    t=i.transition,
                    states=states,
                    nextStatesCoord=nextStatesCoord)
        return inp


class sdlView(QGraphicsView):
    ''' Main graphic view used to display the SDL scene and handle zoom '''
    def __init__(self, scene):
        super(sdlView, self).__init__(scene)
        self.wrappingWindow = None
        self.messagesWindow = None
        self.mode = ''
        self.phantomRect = None
        self.filename = ''

    def keyPressEvent(self, keyEvent):
        ''' Handle keyboard: Zoom, open/save diagram '''

        if keyEvent.matches(QKeySequence.ZoomOut):
            self.scale(0.8, 0.8)
        elif keyEvent.matches(QKeySequence.ZoomIn):
            self.scale(1.2, 1.2)
        elif keyEvent.matches(QKeySequence.Save):
            self.save_diagram()
        elif (keyEvent.key() == Qt.Key_G and
                keyEvent.modifiers() == Qt.ControlModifier):
            self.generate_ada()
        elif keyEvent.key() == Qt.Key_F7:
            self.check_model()
        elif keyEvent.key() == Qt.Key_F5:
            # Refresh (in principle not needed)
            self.viewport().update()
        elif keyEvent.matches(QKeySequence.Open):
            self.open_diagram()
        elif keyEvent.matches(QKeySequence.New):
            self.new_diagram()
        super(sdlView, self).keyPressEvent(keyEvent)

    def resizeEvent(self, e):
        '''
           Called by Qt when window is resized
           Make sure that the scene that is displayed is at least
           of the size of the view, by drawing a transparent rectangle
           Otherwise, the scene is centered on the view, with the size
           of its bounding rect. This is nice in theory, except when
           the user wants to place a symbol at an exact position - in
           that case, the automatic centering is not appropriate.
        '''
        sceneRect = self.scene().itemsBoundingRect()
        viewSize = self.size()
        sceneRect.setWidth(max(sceneRect.width(), viewSize.width()))
        sceneRect.setHeight(max(sceneRect.height(), viewSize.height()))
        if self.phantomRect and self.phantomRect in self.scene().items():
            self.scene().removeItem(self.phantomRect)
        self.phantomRect = self.scene().addRect(sceneRect,
                pen=QPen(QColor(0, 0, 0, 0)))
        # Hide the rectangle so that it does not collide with the symbols
        self.phantomRect.hide()
        super(sdlView, self).resizeEvent(e)

    def about_og(self):
        ''' Display the About dialog '''
        QMessageBox.about(self, 'About OpenGEODE',
                'OpenGEODE - a tiny SDL editor for TASTE\n\n'
                'Author: \nMaxime Perrotin'
                '\n\nContact: maxime.perrotin@esa.int\n\n'
                'Coded with Pyside (Python + Qt)\n'
                'and ANTLR 3.1.3 for Python (parser)')

    def wheelEvent(self, wheelEvent):
        '''
            Catch the mouse Wheel event
        '''
        if wheelEvent.modifiers() == Qt.ControlModifier:
            #pos = self.mapToScene(wheelEvent.pos())
            # Google-Earth zoom mode (Zoom with center on the mouse position)
            self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
            if wheelEvent.delta() < 0:
                self.scale(0.9, 0.9)
            else:
                self.scale(1.1, 1.1)
            #self.centerOn(pos)
            self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        else:
            return(super(sdlView, self).wheelEvent(wheelEvent))

    def mousePressEvent(self, evt):
        '''
            Catch mouse press event to move (when middle button is clicked)
            or to select multiple items
        '''
        self.mousePos = evt.pos()
        if evt.button() == Qt.MidButton:
            self.mode = 'moveScreen'
        elif evt.button() == Qt.LeftButton:
            item = self.itemAt(evt.pos())
            if not item:  # or not isinstance(item, Symbol):
                self.mode = 'selectItems'
                self.origPos = self.mousePos
                self.selectRect = self.scene().addRect(
                        QRectF(self.mapToScene(self.mousePos),
                            self.mapToScene(self.mousePos)))
        super(sdlView, self).mousePressEvent(evt)

    def mouseMoveEvent(self, evt):
        ''' Handle the screen move when user middle-clicks '''
        newPos = evt.pos()
        if self.mode == 'moveScreen':
            diffX = self.mousePos.x() - newPos.x()
            diffY = self.mousePos.y() - newPos.y()
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() + diffX)
            v_scroll.setValue(v_scroll.value() + diffY)
            self.mousePos = newPos
        elif self.mode == 'selectItems':
            rect = QRectF(self.mapToScene(self.origPos),
                    self.mapToScene(newPos))
            self.selectRect.setRect(rect.normalized())
        else:
            super(sdlView, self).mouseMoveEvent(evt)

    def mouseReleaseEvent(self, evt):
        if self.mode == 'selectItems':
            for item in self.scene().items(self.selectRect.rect().toRect(),
                    mode=Qt.ContainsItemBoundingRect):
                if isinstance(item, Symbol):
                    item.setSelected(True)
            self.scene().removeItem(self.selectRect)
            self.viewport().update()
        self.mode = ''
        super(sdlView, self).mouseReleaseEvent(evt)

    def save_as(self):
        ''' Save As function '''
        self.save_diagram(saveAs=True)

    def save_diagram(self, saveAs=False):
        ''' Save the diagram to a .pr file '''
        # First update the global symbols list
        # (in case items were deleted, etc)
        global G_SYMBOLS
        toBeDeleted = [s for s in G_SYMBOLS
                if s not in self.scene().items() or
                (s.parentItem() is not None and not s.childSymbols())]
        map(G_SYMBOLS.remove, toBeDeleted)
        if not self.filename or saveAs:
            self.filename = QFileDialog.getSaveFileName(self, "Save model",
                    ".", "SDL Model (*.pr)")[0]
        if not self.filename:
            return False
        else:
            if self.filename.split('.')[-1] != 'pr':
                self.filename += ".pr"
            prFile = QFile(self.filename)
            prFile.open(QIODevice.WriteOnly | QIODevice.Text)
            # FIXME: ProcessName is a temporary solution -
            # the second split won't work on Windows
            global PROCESS_NAME
            PROCESS_NAME = ''.join(self.filename
                    .split('.')[0:-1]).split('/')[-1]
            self.wrappingWindow.setWindowTitle('process ' + PROCESS_NAME)
        pr = self.scene().getPrData()
        # print pr
        try:
            prFile.write(pr)
            prFile.close()
            self.scene().undoStack.setClean()
            return True
        except:
            print 'ERROR - impossible to save the file'
            return False

    def save_png(self):
        ''' Save the whole diagram as a PNG image '''
        filename = QFileDialog.getSaveFileName(self, "Save picture",
                ".", "Inmage (*.png)")[0]
        if not filename:
            return
        else:
            if filename.split('.')[-1] != 'png':
                filename += ".png"
        self.scene().clearSelection()
        self.scene().clearFocus()
        oldBrush = self.scene().backgroundBrush()
        self.scene().setBackgroundBrush(QBrush())
        self.scene().setSceneRect(self.scene().itemsBoundingRect())
        image = QImage(self.scene().sceneRect().size().toSize(),
                QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        #painter.setRenderHint(QPainter.Antialiasing)
        self.scene().render(painter)
        image.save(filename)
        if painter.isActive():
            painter.end()
        self.scene().setBackgroundBrush(oldBrush)

    def load_file(self, filename):
        ''' Parse a PR file and render it on the scene '''
        self.filename = filename
        process, warnings, errors = ogParser.parseProcessDefinition(
                fileName=self.filename)
        print('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        self.reportErrors(errors, warnings)
        global PROCESS_NAME
        PROCESS_NAME = process.processName or 'opengeode'
        self.wrappingWindow.setWindowTitle('process ' + PROCESS_NAME)
        self.scene().add_process_from_ast(process)
        self.centerOn(self.sceneRect().topLeft())
        self.viewport().update()

    def open_diagram(self):
        ''' Load a .pr file and display the state machine '''
        if self.new_diagram():
            filename, _ = QFileDialog.getOpenFileName(self,
                    "Open model", ".", "SDL model (*.pr)")
            if not filename:
                return
            else:
                self.load_file(filename)
                self.filename = filename

    def new_diagram(self):
        ''' If model state is clean, reset current diagram '''
        if not self.scene().undoStack.isClean():
            # If changes occured since last save, pop up a window
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle('OpenGEODE')
            msgBox.setText("The model has been modified.")
            msgBox.setInformativeText("Do you want to save your changes?")
            msgBox.setStandardButtons(QMessageBox.Save |
                    QMessageBox.Discard |
                    QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)
            ret = msgBox.exec_()
            if ret == QMessageBox.Save:
                if not self.save_diagram():
                    return False
            elif ret == QMessageBox.Discard:
                pass
            elif ret == QMessageBox.Cancel:
                return False
        self.scene().undoStack.clear()
        self.scene().clear()
        global G_SYMBOLS
        G_SYMBOLS.clear()
        return True

    def reportErrors(self, errors, warnings):
        ''' Report Error and Warnings on the console and in the log window '''
        if self.messagesWindow:
            self.messagesWindow.clear()
        for e in errors:
            print u'[ERROR]', e[0]
            if type(e[0]) == list:
                # FIXME
                continue
            item = QListWidgetItem(u'[ERROR] ' + e[0])
            if len(e) == 2:
                item.setData(Qt.UserRole, e[1])
            if self.messagesWindow:
                self.messagesWindow.addItem(item)
        for w in warnings:
            print u'[WARNING]', w[0]
            item = QListWidgetItem(u'[WARNING] ' + w[0])
            if len(w) == 2:
                item.setData(Qt.UserRole, w[1])
            if self.messagesWindow:
                self.messagesWindow.addItem(item)
        if not errors and not warnings and self.messagesWindow:
            self.messagesWindow.addItem('No errors, no warnings!')

    def check_model(self):
        ''' Parse the model and check for warnings and errors '''
        pr = self.scene().getPrData()
        if pr:
            process, warnings, errors = ogParser.parseProcessDefinition(
                    string=pr)
            self.reportErrors(errors, warnings)

    def generate_ada(self):
        ''' Generate Ada code '''
        pr = self.scene().getPrData()
        if pr:
            print 'Generate Ada code'
            process, warnings, errors = ogParser.parseProcessDefinition(
                    string=pr)
            self.reportErrors(errors, warnings)
            if len(errors)>0:
                self.messagesWindow.addItem(
                        'Aborting: too many errors to generate code')
            else:
                AdaGenerator.generate(process)


class ogMainWindow(QMainWindow):
    ''' Main GUI window '''
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

    def go(self, fileName):
        ''' Initializes all objects to start the application '''
        # Create a graphic scene: the main canvas
        self.scene = sdlScene()
        # Find sdlView widget
        self.view = self.findChild(sdlView, 'graphicsView')
        self.view.setScene(self.scene)

        # Find Menu Actions
        open_action = self.findChild(QAction, 'actionOpen')
        new_action = self.findChild(QAction, 'actionNew')
        save_action = self.findChild(QAction, 'actionSave')
        save_as_action = self.findChild(QAction, 'actionSaveAs')
        quit_action = self.findChild(QAction, 'actionQuit')
        check_action = self.findChild(QAction, 'actionCheck_model')
        about_action = self.findChild(QAction, 'actionAbout')
        ada_action = self.findChild(QAction, 'actionGenerate_Ada_code')
        png_action = self.findChild(QAction, 'actionExport_to_PNG')

        # Connect menu actions
        open_action.activated.connect(self.view.open_diagram)
        save_action.activated.connect(self.view.save_diagram)
        save_as_action.activated.connect(self.view.save_as)
        quit_action.activated.connect(self.close)
        new_action.activated.connect(self.view.new_diagram)
        check_action.activated.connect(self.view.check_model)
        about_action.activated.connect(self.view.about_og)
        ada_action.activated.connect(self.view.generate_ada)
        png_action.activated.connect(self.view.save_png)

        # Add a sdlToolBar widget (not in .ui file due to pyside bugs)
        toolbar = sdlToolBar(self)
        self.addToolBar(toolbar)

        # Connect toolbar actions
        self.scene.selectionChanged.connect(toolbar.updateMenu)
        self.scene.disableMenuItem.connect(toolbar.disableAction)
        self.scene.enableMenuItem.connect(toolbar.enableAction)
        for item in toolbar.actions.viewkeys():
            toolbar.actions[item].triggered.connect(self.scene.actions[item])

        self.scene.clearSelection()
        self.scene.clearFocus()

        # processWidget is the widget wrapping the view. We have to maximize it
        processWidget = self.findChild(QWidget, 'process')
        processWidget.showMaximized()
        self.view.wrappingWindow = processWidget

        # get the messages list window (to display errors and warnings)
        # it is a QListWidget
        msgDock = self.findChild(QDockWidget, 'msgDock')
        msgDock.setWindowTitle('Use F7 to check the model')
        msgDock.setStyleSheet('QDockWidget::title {background: lightgrey;}')
        messages = self.findChild(QListWidget, 'messages')
        messages.addItem('Welcome to OpenGEODE.')
        self.view.messagesWindow = messages
        self.scene.messagesWindow = messages
        messages.itemClicked.connect(self.scene.showItem)

        # get the mdiArea to set the background image
        #mdiArea = self.findChild(QMdiArea, 'mdiArea')
        #mdiArea.setBackground(QBrush(QImage(os.path.join(CUR_DIR,
        #   'opengeode.png'))))
        if fileName:
            self.view.load_file(fileName)
        self.show()

    def closeEvent(self, event):
        ''' Close main application '''
        if self.view.new_diagram():
            super(ogMainWindow, self).closeEvent(event)
        else:
            event.ignore()


def opengeode():
    ''' Tool entry point '''
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    # app.setWindowIcon(QIcon(os.path.join(CUR_DIR, 'input.png')))
    app.setWindowIcon(QIcon(':/output.png'))  # os.path.join(CUR_DIR, 'input.png')))
    # currentSymbolItem = None

    # Parse the command line
    usage = ('usage: opengeode.py [--verbose] [--open | --check | '
             '--toAda file.pr]')
    version = '0.2'
    parser = optparse.OptionParser(usage=usage, version=version)
    parser.add_option('-v', '--verbose', action='store_true', default=False,
            help='Display debug information')
    parser.add_option('--check', metavar='file.pr', dest='check',
            help='Check a .pr file for syntax and semantics')
    parser.add_option('-o', '--open', metavar='file.pr', dest='loadGR',
            help='Load a .pr file in the graphical editor')
    parser.add_option('--toAda', dest='toAda', metavar='file.pr',
            help='Generate Ada code for the .pr file')
    options, args = parser.parse_args()
    ret = 0
    if options.verbose:
        pass
        #log.setLevel(logging.DEBUG)
    else:
        pass
        #log.setLevel(logging.INFO)
    if options.check:
        print 'Checking', options.check
        _, warnings, errors = ogParser.parseProcessDefinition(
                fileName=options.check)
        print('Parsing complete. Summary, found ' +
                str(len(warnings)) +
                ' warnings and ' +
                str(len(errors)) +
                ' errors')
        for w in warnings:
            print '[WARNING]', w[0]
        for e in errors:
            print '[ERROR]', e[0]
        if len(errors) > 0:
            ret = -1
    elif options.toAda:
        print 'Generating Ada code for', options.toAda
        process, warnings, errors = ogParser.parseProcessDefinition(
                fileName=options.toAda)
        print('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        for w in warnings:
            print '[WARNING]', w[0]
        for e in errors:
            print '[ERROR]', e[0]
        if len(errors) > 0:
            print 'Too many errors, cannot generate Ada code'
            ret = -1
        else:
            AdaGenerator.generate(process)
    else:
        # Load the application layout from the .ui file
        loader = QUiLoader()
        loader.registerCustomWidget(ogMainWindow)
        loader.registerCustomWidget(sdlView)
        loader.registerCustomWidget(sdlToolBar)
        uiFile = QFile(':/opengeode.ui')  # MAIN_UI_FILE)
        uiFile.open(QFile.ReadOnly)
        myWidget = loader.load(uiFile)
        uiFile.close()
        myWidget.go(options.loadGR)
        ret = app.exec_()
    sys.exit(ret)

if __name__ == '__main__':
    ''' Call opengeode entry point '''
    opengeode()
