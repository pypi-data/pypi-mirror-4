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
import undoCommands  # NOQA
import sdl92Lexer  # NOQA
import sdl92Parser  # NOQA
import genericSymbols  # NOQA
import sdlSymbols
import PySide.QtXml  # NOQA

from PySide.QtCore import Qt, QSize, QFile, QIODevice, Signal, QRectF
from PySide.QtGui import(QGraphicsScene, QApplication, QToolBar, QIcon,
        QGraphicsView, QKeySequence, QUndoStack, QFileDialog, QBrush,
        QWidget, QDockWidget, QListWidget, QImage, QListWidgetItem,
        QPainter, QAction, QMessageBox, QMainWindow, QPen, QColor, QStyle)

from PySide.QtUiTools import QUiLoader

from genericSymbols import(Symbol, VerticalSymbol, Connection, Comment,
        EditableText)
from sdlSymbols import(Input, Output, Decision, DecisionAnswer, Task,
        ProcedureCall, TextSymbol, State, Start, Join, Label)

from undoCommands import InsertSymbol, DeleteSymbol

# Icons and png files generated from the resource file:
import icons  # NOQA

import AdaGenerator

import ogParser
import ogAST

import signal
import sys
import os
import optparse
import logging

__all__ = ['opengeode']
__version__ = '0.5'

if hasattr(sys, 'frozen'):
    CUR_DIR = os.path.dirname(unicode
            (sys.executable, sys.getfilesystemencoding()))
else:
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))


LOG = logging.getLogger(__name__)


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


class File_toolbar(QToolBar):
    ''' Toolbar with file open, save, etc '''
    def __init__(self, parent):
        ''' Create the toolbar using standard icons '''
        super(File_toolbar, self).__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.new_button = self.addAction(self.style().standardIcon(
            QStyle.SP_FileIcon), 'New model')
        self.open_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogOpenButton), 'Open model')
        self.save_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogSaveButton), 'Save model')
        self.check_button = self.addAction(self.style().standardIcon(
            QStyle.SP_DialogApplyButton), 'Check model')


class Sdl_toolbar(QToolBar):
    ''' Toolbar with SDL symbols '''
    def __init__(self, parent):
        ''' Create the toolbar, get icons and link actions '''
        super(Sdl_toolbar, self).__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        #self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(40, 40))
        # Removed 'Condition' below (not supported by the parser)
        self.actions = {}
        for item in [Start, State, Input, Task, Decision, DecisionAnswer,
                Output, ProcedureCall, TextSymbol, Comment, Label, Join]:
            item_name = item.__name__
            self.actions[item_name] = self.addAction(QIcon(':/{icon}'.format(
                icon=item_name.lower() + '.png')), item_name)
            self.addSeparator()
        # There can be only one START symbol - 'start_is_possible' verifies it.
        self.start_is_possible = True
        self.update_menu()

    def enable_action(self, action):
        ''' Used as a slot to allow a scene to enable a menu action,
            e.g. if the Start symbol is deleted, the Start button
            shall be activated '''
        self.actions[action].setEnabled(True)
        if action == 'Start':
            self.start_is_possible = True

    def disable_action(self, action):
        ''' See description in enable_action '''
        self.actions[action].setEnabled(False)
        if action == 'Start':
            self.start_is_possible = False

    def update_menu(self):
        ''' Context-dependent enabling/disabling of menu buttons '''
        if self.sender():
            selection = self.sender().selectedItems()
        else:
            selection = []
        if len(selection) > 1:
            # When several items are selected, disable all menu entries
            for _, action in self.actions.viewitems():
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
            self.actions['Start'].setEnabled(self.start_is_possible)
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


class SDL_Scene(QGraphicsScene):
    ''' Main graphic scene (canvas) where the user can place SDL symbols '''
    enableMenuItem = Signal(str)
    disableMenuItem = Signal(str)

    def __init__(self):
        super(SDL_Scene, self).__init__()
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
        self.undo_stack = QUndoStack(self)
        # buttonSelected is used to set which symbol to draw
        # on next scene click (see mousePressEvent)
        self.buttonSelected = None
        self.setBackgroundBrush(QBrush(QImage(':/texture.png')))
        self.messagesWindow = None
        self.click_coordinates = None

    def refresh(self):
        ''' Call a refresh of the views '''
        for view in self.views():
            view.refresh()

    def set_cursor(self, follower):
        ''' Set the cursor shape depending on the selected menu item '''
        for item in self.items():
            try:
                if follower.__name__ not in item.allowed_followers:
                    item.setCursor(Qt.ForbiddenCursor)
                else:
                    item.setCursor(Qt.PointingHandCursor)
            except AttributeError:
                # if there are items not having allowed_followers
                pass

    def reset_cursor(self):
        ''' Reset the default cursor of an item '''
        for item in self.items():
            try:
                item.setCursor(item.default_cursor)
            except AttributeError:
                pass

    def raise_syntax_errors(self, errors=None):
        ''' Display an syntax error pop-up message '''
        if not errors:
            return
        for view in self.views():
            errs = []
            for e in errors:
                split = e.split()
                if split[0] == 'line' and len(split) > 1:
                    line_col = split[1].split(':')
                    if len(line_col) == 2:
                        # Get line number and column..to locate error (TODO)
                        line_nb, col = line_col
                        errs.append(' '.join(split[2:]))
                    else:
                        errs.append(e)
                else:
                    errs.append(e)
            self.clearFocus()
            msg_box = QMessageBox(view)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle('OpenGEODE - Syntax Error')
            msg_box.setInformativeText('\n'.join(errs))
            msg_box.setText("Syntax error!")
            msg_box.setStandardButtons(QMessageBox.Discard)
            msg_box.setDefaultButton(QMessageBox.Discard)
            msg_box.exec_()

    def show_item(self, item):
        '''
        Select an item and make sure it is visible
        (used when user clicks on a warning or error to locate the symbol)
        '''
        abs_coordinates = item.data(Qt.UserRole)
        if not abs_coordinates:
            return
        else:
            pos_x, pos_y = abs_coordinates
        item = self.itemAt(pos_x, pos_y)
        if item:
            self.clearSelection()
            self.clearFocus()
            item.setSelected(True)
            item.ensureVisible()

    def delete_selected_symbols(self):
        '''
            Remove selected symbols from the scene, with proper re-connections
        '''
        self.undo_stack.beginMacro('Delete items')
        for item in self.selectedItems():
            if not item.scene():
                # Ignore if item has already been deleted
                # (in case of multiple selection)
                continue
            undo_cmd = DeleteSymbol(item)
            self.undo_stack.push(undo_cmd)
            if isinstance(item, Start):
                self.enableMenuItem.emit('Start')
            try:
                item.branchEntryPoint.parent.updateConnectionPointPosition()
                item.branchEntryPoint.parent.updateConnectionPoints()
            except AttributeError:
                pass
        self.undo_stack.endMacro()

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
            self.messagesWindow.addItem('Selection is incompatible with copy')
            return False
        # Then parse/copy the selected branches
        for item in branch_top_level + floating_items:
            try:
                branch_ast, terminators = self.copy_branch(item)
            except AttributeError:
                # CHECKME - what are the cases for this branch?
                self.messagesWindow.addItem('ERROR: cannot copy '
                        'item "' + str(item) + '". Check its syntax (use F7)')
                return False
            else:
                translation = item.scenePos()
                # Translate all top symbols to a 0,0-based coordinates sysyem
                for item in branch_ast:
                    item.pos_x -= translation.x()
                    item.pos_y -= translation.y()
                # Translate all terminators to have consistent coordinates
                for term in terminators:
                    term.pos_x -= translation.x()
                    term.pos_y -= translation.y()
                COPY_PASTE.append((branch_ast, terminators))
        LOG.debug('COPY-PASTE LIST:' + str(COPY_PASTE))
        return True

    def copy_branch(self, top_level_item):
        ''' Copy branches (recursively) '''
        res_terminators = []
        item_ast, terminators = top_level_item.get_ast()
        LOG.debug('Copying ' + str(item_ast))
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
        for term in terminators:
            # Get symbol at terminator coordinates
            symbols = self.items(
                    QRectF(term.pos_x, term.pos_y, term.width, term.height)
                    .center())
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
        new_item = None
        selection = self.selectedItems()
        if len(selection) > 1:
            self.messagesWindow.addItem('[WARNING] '
                    'Cannot paste when several items are selected')
        elif len(selection) == 0:
            self.undo_stack.beginMacro('Paste items')
            for item_list, terminators in COPY_PASTE:
                next_states_coord = self.nextstate_merge_list(terminators)
                states = [i for i in item_list if isinstance(i, ogAST.State)]
                text_areas = [i for i in item_list if
                        isinstance(i, ogAST.TextArea)]
                for i in states:
                    LOG.debug('Pasting state')
                    # First check if state has already been pasted
                    if((i.pos_x, i.pos_y) in next_states_coord.keys() and
                            isinstance(
                                next_states_coord[(i.pos_x, i.pos_y)], State)):
                        continue
                    new_item = State(ast=i)
                    G_SYMBOLS.add(new_item)
                    if new_item not in self.items():
                        self.addItem(new_item)
                    undo_cmd = InsertSymbol(
                            new_item, parent=None, pos=self.click_coordinates
                            or new_item.pos())
                    self.undo_stack.push(undo_cmd)
                    for inp in i.inputs:
                        inp = self.render_input_from_ast(
                                inp, parent=new_item, states=states,
                                next_states_coord=next_states_coord)
                    new_item.cam(new_item.pos(), new_item.pos())
                for i in text_areas:
                    LOG.debug('Pasting text area')
                    new_item = TextSymbol(ast=i)
                    G_SYMBOLS.add(new_item)
                    if new_item not in self.items():
                        self.addItem(new_item)
                    undo_cmd = InsertSymbol(
                            new_item, parent=None, pos=self.click_coordinates
                            or new_item.pos())
                    self.undo_stack.push(undo_cmd)
                    new_item.cam(new_item.pos(), new_item.pos())
            self.undo_stack.endMacro()
        elif len(selection) == 1:
            parent_item = selection[0]
            self.undo_stack.beginMacro('Paste items')
            for item_list, terminators in COPY_PASTE:
                next_states_coord = self.nextstate_merge_list(terminators)
                states = [i for i in item_list if isinstance(i, ogAST.State)]
                for i in [c for c in item_list if not isinstance
                        (c, (ogAST.State, ogAST.TextArea, ogAST.Start))]:
                    LOG.debug('Pasting ' + str(i))
                    # Create the new item from the AST description
                    # If item to paste is an INPUT or a DECISION ANSWER,
                    # and the selected parent is of the same type,
                    # then select one parent above (STATE or DECISION)
                    if isinstance(i, ogAST.Input):
                        if isinstance(parent_item, Input):
                            parent_item = parent_item.parentItem()
                        new_item = self.render_input_from_ast(
                                i, parent=None, states=states,
                                next_states_coord=next_states_coord)
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
                                    next_states_coord=next_states_coord)
                            if new_item.connection in self.items():
                                self.removeItem(new_item.connection)
                                new_item.connection = None
                        else:
                            new_item = self.render_action_from_ast(
                                    i, parent=None, states=states,
                                    next_states_coord=next_states_coord)
                    # Check that item is compatible with parent
                    if (type(new_item).__name__ not in
                            type(parent_item).allowed_followers):
                        self.messagesWindow.addItem('[WARNING] '
                              ' Cannot paste here ({t1} cannot follow {t2}'
                              .format(t1=type(new_item), t2=type(parent_item)))
                        if new_item in self.items():
                            self.removeItem(new_item)
                            new_item.setParentItem(None)
                        break
                    # Create Undo command, actually inserting symbol
                    undo_cmd = InsertSymbol(
                            new_item, parent_item, None)
                    self.undo_stack.push(undo_cmd)
                    self.clearSelection()
                    self.clearFocus()
                    new_item.updateConnectionPointPosition()
                    new_item.updateConnectionPoints()
                    parent_item = new_item
            self.undo_stack.endMacro()
        #self.clearFocus()
        if new_item:
            new_item.setSelected(True)
        self.refresh()

    def getPrData(self):
        ''' Parse the graphical items and returns a PR string '''
        pr_data = ['PROCESS ' + PROCESS_NAME + ';']
        # Separate the text boxes and START symbol from the states
        # (They need to be placed at the top of the .pr file
        top_level_items = [i for i in self.items() if
                isinstance(i, (Start, State, TextSymbol))]
        text_boxes = filter(
                lambda x: isinstance(x, TextSymbol), top_level_items)
        start_state = filter(lambda x: isinstance(x, Start), top_level_items)
        states = filter(lambda x: isinstance(x, State), top_level_items)
        for item in text_boxes:
            pr_data.append(repr(item))
        if not start_state:
            self.messagesWindow.addItem('[WARNING] START Symbol missing - '
                   'Adding dummy state to comply with the SDL syntax')
            pr_data.append('START;')
            pr_data.append('NEXTSTATE Dummy;')
        else:
            pr_data.append(repr(start_state[0]))
        for item in states:
            pr_data.append(item.parseGR())
        pr_data.append('ENDPROCESS ' + PROCESS_NAME + ';')
        return str('\n'.join(pr_data))

    def mousePressEvent(self, event):
        '''
            Handle mouse click on the scene:
            If a symbol was selected in the menu, check if it can be inserted
            Otherwise store the coordinates, in which case if the user does
            a paste action with floating items, they will be placed there.
        '''
        self.reset_cursor()
        if self.buttonSelected:
            parent_item, follower_item = None, None
            items_at_click_point = self.items(event.scenePos())
            symbol_items = [i for i in items_at_click_point if
                    isinstance(i, Symbol)]
            if len(symbol_items) == 1:
                parent_item, = symbol_items
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
                self.messagesWindow.addItem('Cannot insert this symbol here')
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
            super(SDL_Scene, self).mousePressEvent(event)

    def keyPressEvent(self, keyEvent):
        ''' Handle keyboard: Delete, Undo/Redo '''
        super(SDL_Scene, self).keyPressEvent(keyEvent)
        if keyEvent.matches(QKeySequence.Delete) and self.selectedItems():
            self.delete_selected_symbols()
            self.clearSelection()
            self.clearFocus()
        elif keyEvent.matches(QKeySequence.Undo):
            if not isinstance(self.focusItem(), EditableText):
                self.undo_stack.undo()
                self.refresh()
                self.clearFocus()
        elif keyEvent.matches(QKeySequence.Redo):
            if not isinstance(self.focusItem(), EditableText):
                self.undo_stack.redo()
                self.refresh()
                self.clearFocus()
        elif keyEvent.matches(QKeySequence.Copy):
            if not isinstance(self.focusItem(), EditableText):
                self.copy_selected_symbols()
        elif keyEvent.matches(QKeySequence.Cut):
            self.cut_selected_symbols()
        elif keyEvent.matches(QKeySequence.Paste):
            if not isinstance(self.focusItem(), EditableText):
                self.paste_symbols()
                self.refresh()
                self.clearFocus()
        elif (keyEvent.key() == Qt.Key_J and
                keyEvent.modifiers() == Qt.ControlModifier):
            # Debug mode
            for selection in self.selectedItems():
                LOG.info(repr(selection))
                LOG.info('Position: ' + str(selection.pos()))
                LOG.info('BoundingRect: ' + str(selection.boundingRect()))
                LOG.info('ChildrenList: ' + str(selection.childItems()))
                LOG.info('ChildrenBoundingRect: ' +
                        str(selection.childrenBoundingRect()))
                LOG.info(str(selection.__dict__))

    def placeStart(self, pos):
        '''
            Place the Start button on the scene upon user click
            (called by mousePressEvent)
        '''
        self.undo_stack.beginMacro('Place Start Symbol')
        start = Start()
        if start not in self.items():
            self.addItem(start)
        undo_cmd = InsertSymbol(start, parent=None, pos=pos)
        self.undo_stack.push(undo_cmd)
        global G_SYMBOLS
        G_SYMBOLS.add(start)
        self.clearSelection()
        self.clearFocus()
        start.setSelected(True)
        self.disableMenuItem.emit('Start')
        start.cam(pos, pos)
        self.undo_stack.endMacro()

    def addStart(self):
        '''
            User selected the Start icon.
            Symbol will be added on next scene click
        '''
        self.buttonSelected = Start
        self.set_cursor(Start)
        self.messagesWindow.clear()
        self.messagesWindow.addItem(
                'Hint: Click on the diagram to place the START symbol')

    def placeInput(self, parent):
        ''' Place an INPUT symbol on the scene '''
        self.clearSelection()
        self.clearFocus()
        if isinstance(parent, Input):
            local_select = parent
            parent_state = local_select.parentItem()
        else:
            parent_state = parent
        # Add parent state to the list of global symbols
        # This is mandatory for the PR parsing to allow merging
        # STATE and NEXTSTATE symbols
        global G_SYMBOLS
        G_SYMBOLS.add(parent_state)
        parent_state.setSelected(True)
        self.insertConnectedItem(Input)

    def addInput(self):
        ''' Add an INPUT symbol to the scene '''
        selection = self.selectedItems()
        if not selection:
            # Menu item clicked but no symbol selected ->
            # store until user clicks on the scene
            self.buttonSelected = Input
            self.set_cursor(Input)
            return None
        elif len(selection) > 1:
            self.buttonSelected = None
            return None
        else:
            selection, = selection  # [0]
            self.undo_stack.beginMacro('Add Input')
            self.placeInput(parent=selection)
            self.undo_stack.endMacro()

    def placeConnectedItem(self, itemType, parent, pos=None):
        ''' Draw a connected item on the scene '''
        self.undo_stack.beginMacro('Place Item')
        item = itemType()
        # Add the item to the scene
        if item not in self.items():
            self.addItem(item)
        # Create Undo command (makes the call to the insertSymbol function):
        undo_cmd = InsertSymbol(item, parent, pos)
        self.undo_stack.push(undo_cmd)
        self.clearSelection()
        self.clearFocus()
        # If no item is selected (e.g. new STATE), add it to the scene
        if not parent:
            global G_SYMBOLS
            G_SYMBOLS.add(item)
        item.setSelected(True)
        item.cam(item.pos(), item.pos())
        self.undo_stack.endMacro()
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
            self.set_cursor(itemType)
            return None
        elif len(selection) > 1:
            # Ignore the insertion if there is more than one item selected
            self.buttonSelected = None
            self.reset_cursor()
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
            self.set_cursor(Decision)
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
        self.undo_stack.beginMacro('Add Decision')
        item = self.insertConnectedItem(Decision)
        self.addAnswer()
        self.addAnswer()
        self.undo_stack.endMacro()
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
            self.set_cursor(DecisionAnswer)
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
        self.set_cursor(TextSymbol)
        self.messagesWindow.clear()
        self.messagesWindow.addItem(
                'Hint: Click on the diagram to place the text area\n'
                'A text area is used to declare variables or place comments\n'
                'To declare a variable: \'DCL variableName TypeName;\'\n'
                'To add some comments: -- my comment')

    def placeText(self, pos):
        text = TextSymbol()
        self.addItem(text)
        self.undo_stack.beginMacro('Place Text Symbol')
        undo_cmd = InsertSymbol(text, parent=None, pos=pos)
        self.undo_stack.push(undo_cmd)
        global G_SYMBOLS
        G_SYMBOLS.add(text)
        text.setPos(pos.x(), pos.y())
        self.clearSelection()
        self.clearFocus()
        text.setSelected(True)
        text.cam(pos, pos)
        self.undo_stack.endMacro()

    def nextstate_merge_list(self, terminators):
        '''
            Build up a list of nextstate coordinates to merge state
            and nextate symbols when they have the same coordinates
            Note: We are working in scene coordinates here
        '''
        next_states_coord = {}
        for term in terminators:
            if term.pos_y and term.kind == 'next_state':
                next_states_coord[(term.pos_x, term.pos_y)] = term.inputString
        return next_states_coord

    def add_process_from_ast(self, process):
        ''' Render a process from the PR-parsed AST on the graphics scene '''
        global G_SYMBOLS
        for text_area in process.textAreas:
            text = TextSymbol(ast=text_area)
            G_SYMBOLS.add(text)
            if text not in self.items():
                self.addItem(text)

        # Set autocompletion lists for input, output, state, types, variables:
        if process.dataView:
            TextSymbol.completion_list = [
                    t.replace('-', '_') for t in process.dataView]
        State.completion_list = [
                state for state in process.mapping if state != 'START']
        Input.completion_list = process.inputSignals.keys()
        Output.completion_list = process.outputSignals.keys()
        Task.completion_list = process.variables.keys()
        ProcedureCall.completion_list = process.procedures.keys()

        next_states_coord = self.nextstate_merge_list(process.terminators)

        if process.start:
            self.render_start_from_ast(
                    process.start, process.states, next_states_coord)

        for state in process.states:
            #sx, sy, sw, sh = state.coordinates or (0, 0, 100, 50)
            # Create only floating states
            if (state.pos_x, state.pos_y) in next_states_coord:
                continue
            #if (sx, sy) in next_states_coord and isinstance(
            #        next_states_coord[(sx, sy)], State) and (
            #                str(next_states_coord[(sx, sy)].text) ==
            #                    state.inputString):
            #    new_state = next_states_coord[(sx, sy)]
            else:
                # Note: state pos_x and pos_y are in scene coordinates
                new_state = State(parent=None, ast=state)
                # Update next states coord (used by the copy-paste)
                if (state.pos_x, state.pos_y) in next_states_coord and (
                        state.inputString == next_states_coord
                        [(state.pos_x, state.pos_y)]):
                    next_states_coord[(state.pos_x, state.pos_y)] = new_state
                if new_state not in self.items():
                    self.addItem(new_state)

                for i in state.inputs:
                    self.render_input_from_ast(i, new_state,
                            process.states, next_states_coord)
                # Add state to the global list of symbols
                G_SYMBOLS.add(new_state)

    def render_transition_from_ast(self, parent, t, states, next_states_coord):
        ''' Add a transition to the diagram, from the PR-parsed AST '''
        for a in t.actions:
            parent = self.render_action_from_ast(a, parent, states,
                    next_states_coord=next_states_coord)

        if t.terminator:
            self.render_terminator_from_ast(t.terminator, parent, states,
                    next_states_coord)

    def render_terminator_from_ast(self, t, parent, states, next_states_coord):
        '''
            Add a terminator to the scene, from the AST, and in the case of a
            NEXTSTATE, possibly merge it with a defined STATE
        '''
        if t.label:
            parent = self.render_action_from_ast(
                    t.label, parent, states,
                    next_states_coord=next_states_coord)
        if t.kind == 'next_state':
            #tx, ty, tw, th = t.coordinates  # or (None, None, None, None)
#            st = None
            # Check if the nextstate symbol coincides with a state
            # symbol with the same name and merge them if so.
#            if (tx, ty) in next_states_coord and (
#                    isinstance(next_states_coord[(tx, ty)], State)
#                    and t.inputString == str(next_states_coord[(tx, ty)].text)):
#                st = next_states_coord[(tx, ty)]
#                st.insertSymbol(parent, tx, ty)
#                st.setPos(parent.mapFromScene(tx, ty))
#            else:
            # State has not been created yet - create it now
            terminator = State(parent=parent, ast=t)
            #next_states_coord[(tx, ty)] = terminator
            # Check if a corresponding state with inputs exists
            # If so, render the inputs too.
#            try:
                # if no states are defined ignore
            for state in states:
                if (state.inputString == t.inputString and
                        state.pos_x == t.pos_x and state.pos_y == t.pos_y):
                    for i in state.inputs:
                        self.render_input_from_ast(i, terminator, states,
                                next_states_coord=next_states_coord)
#            except:
#                pass

        elif t.kind == 'join':
            terminator = Join(parent=parent, ast=t)
        else:
            LOG.error('Unsupported terminator: ' + repr(t))
            return

    def render_action_from_ast(self, a, parent, states, next_states_coord):
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
            dec = Decision(parent=parent, ast=a)
            if dec not in self.items():
                # Add the decision to the scene, so that the connection
                # point can be updated properly
                self.addItem(dec)
            dec.updateConnectionPoints()
            new_parent = dec
            for branch in a.answers:
                self.render_action_from_ast(
                        branch, new_parent, states, next_states_coord)
        elif isinstance(a, ogAST.Label):
            label = Label(parent=parent, ast=a)
            label.updateConnectionPoints()
            new_parent = label
        elif isinstance(a, ogAST.Answer):
            ans = DecisionAnswer(parent=parent, ast=a)
            ans.updateConnectionPoints()
            if a.transition:
                self.render_transition_from_ast(parent=ans,
                        t=a.transition,
                        states=states,
                        next_states_coord=next_states_coord)
            new_parent = ans
        elif isinstance(a, ogAST.Terminator):
            self.render_terminator_from_ast(
                    a, parent, states, next_states_coord)
        else:
            LOG.error('Unsupported symbol in branch: ' + repr(a))
            return None
        return new_parent

    def render_start_from_ast(self, s, states, next_states_coord):
        start = Start(ast=s)
        if start not in self.items():
            self.addItem(start)
        G_SYMBOLS.add(start)
        self.disableMenuItem.emit('Start')
        if s.transition:
            self.render_transition_from_ast(parent=start,
                    t=s.transition,
                    states=states,
                    next_states_coord=next_states_coord)

    def render_input_from_ast(self, i, parent, states, next_states_coord):
        ''' Add input from the AST to the scene '''
        # Note: PROVIDED clause is not supported
        inp = Input(parent=parent, ast=i)
        if inp not in self.items():
            self.addItem(inp)
        if i.transition:
            self.render_transition_from_ast(parent=inp,
                    t=i.transition,
                    states=states,
                    next_states_coord=next_states_coord)
        return inp


class SDL_View(QGraphicsView):
    enableMenuItem = Signal(str)
    ''' Main graphic view used to display the SDL scene and handle zoom '''
    def __init__(self, scene):
        super(SDL_View, self).__init__(scene)
        self.wrappingWindow = None
        self.messagesWindow = None
        self.mode = ''
        self.phantom_rect = None
        self.filename = ''
        self.orig_pos = None
        self.select_rect = None
        self.mouse_pos = None

    def keyPressEvent(self, keyEvent):
        ''' Handle keyboard: Zoom, open/save diagram, etc. '''
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
            # Refresh
            self.refresh()
        elif keyEvent.matches(QKeySequence.Open):
            self.open_diagram()
        elif keyEvent.matches(QKeySequence.New):
            self.new_diagram()
        super(SDL_View, self).keyPressEvent(keyEvent)

    def refresh(self):
        ''' Refresh the complete view '''
        for symbol in self.scene().items():
            try:
                # Update connection points recursively
                symbol.updateConnectionPointPosition()
                symbol.updateConnectionPoints()
            except AttributeError:
                pass
            try:
                # EditableText refreshing - design explanation:
                # The first one is tricky: at symbol initialization,
                # the bounding rect of the text is computed from the raw
                # text value, without any formatting. However, it can
                # happen that text (especially when a model is loaded)
                # contains highlighted data (bold), which has the effect
                # of making the width of the text in fact wider than
                # the bounding rect. The set_text_alignment function,
                # that is applying the aligment of the text within its
                # bounding rect, can work only if the text width is fixed.
                # It has to set it according to the bounding rect, which,
                # therefore can be too small, and this has the effect of
                # pushing the exceeding character to the next line.
                # The only way to avoid this is to call setTextWidth
                # with the value -1 before the aligment is computed.
                # This has the effect of re-computing the bounding rect
                # and fixing the width issue.
                symbol.setTextWidth(-1)
                symbol.set_textbox_position()
                symbol.set_text_alignment()
                symbol.try_resize()
            except AttributeError:
                pass
        self.setSceneRect(self.scene().sceneRect())
        self.viewport().update()

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
        scene_rect = self.scene().itemsBoundingRect()
        view_size = self.size()
        scene_rect.setWidth(max(scene_rect.width(), view_size.width()))
        scene_rect.setHeight(max(scene_rect.height(), view_size.height()))
        if self.phantom_rect and self.phantom_rect in self.scene().items():
            self.scene().removeItem(self.phantom_rect)
        self.phantom_rect = self.scene().addRect(scene_rect,
                pen=QPen(QColor(0, 0, 0, 0)))
        # Hide the rectangle so that it does not collide with the symbols
        self.phantom_rect.hide()
        super(SDL_View, self).resizeEvent(e)

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
            return(super(SDL_View, self).wheelEvent(wheelEvent))

    def mousePressEvent(self, evt):
        '''
            Catch mouse press event to move (when middle button is clicked)
            or to select multiple items
        '''
        super(SDL_View, self).mousePressEvent(evt)
        self.mouse_pos = evt.pos()
        if evt.button() == Qt.MidButton:
            self.mode = 'moveScreen'
        elif evt.button() == Qt.LeftButton:
            item = self.itemAt(evt.pos())
            if not item:
                self.mode = 'selectItems'
                self.orig_pos = self.mouse_pos
                self.select_rect = self.scene().addRect(
                        QRectF(self.mapToScene(self.mouse_pos),
                            self.mapToScene(self.mouse_pos)))

    def mouseMoveEvent(self, evt):
        ''' Handle the screen move when user clicks '''
        if evt.buttons() == Qt.NoButton:
            return super(SDL_View, self).mouseMoveEvent(evt) 
        new_pos = evt.pos()
        if self.mode == 'moveScreen':
            diff_x = self.mouse_pos.x() - new_pos.x()
            diff_y = self.mouse_pos.y() - new_pos.y()
            h_scroll = self.horizontalScrollBar()
            v_scroll = self.verticalScrollBar()
            h_scroll.setValue(h_scroll.value() + diff_x)
            v_scroll.setValue(v_scroll.value() + diff_y)
            self.mouse_pos = new_pos
        elif self.mode == 'selectItems':
            rect = QRectF(self.mapToScene(self.orig_pos),
                    self.mapToScene(new_pos))
            self.select_rect.setRect(rect.normalized())
        else:
            return super(SDL_View, self).mouseMoveEvent(evt)

    def mouseReleaseEvent(self, evt):
        if self.mode == 'selectItems':
            for item in self.scene().items(self.select_rect.rect().toRect(),
                    mode=Qt.ContainsItemBoundingRect):
                if isinstance(item, Symbol):
                    item.setSelected(True)
            self.scene().removeItem(self.select_rect)
            #self.refresh()  # removed - CHECKME
        self.mode = ''
        super(SDL_View, self).mouseReleaseEvent(evt)

    def save_as(self):
        ''' Save As function '''
        self.save_diagram(save_as=True)

    def save_diagram(self, save_as=False):
        ''' Save the diagram to a .pr file '''
        # First update the global symbols list
        for symbol in [s for s in G_SYMBOLS
                if s not in self.scene().items() or
                (s.parentItem() is not None and not s.childSymbols())]:
            G_SYMBOLS.remove(symbol)
        if not self.filename or save_as:
            self.filename = QFileDialog.getSaveFileName(self, "Save model",
                    ".", "SDL Model (*.pr)")[0]
        if not self.filename:
            return False
        else:
            if self.filename.split('.')[-1] != 'pr':
                self.filename += ".pr"
            pr_file = QFile(self.filename)
            pr_file.open(QIODevice.WriteOnly | QIODevice.Text)
            global PROCESS_NAME
            PROCESS_NAME = ''.join(self.filename
                    .split(os.path.extsep)[0:-1]).split(os.path.sep)[-1]
            self.wrappingWindow.setWindowTitle(
                    'process ' + PROCESS_NAME + '[*]')
        pr_data = self.scene().getPrData()
        LOG.debug(str(pr_data))
        try:
            pr_file.write(pr_data)
            pr_file.close()
            self.scene().undo_stack.setClean()
            return True
        except:
            LOG.error('Impossible to save the file')
            return False

    def save_png(self):
        ''' Save the whole diagram as a PNG image '''
        filename = QFileDialog.getSaveFileName(self, "Save picture",
                ".", "Image (*.png)")[0]
        if not filename:
            return
        else:
            if filename.split('.')[-1] != 'png':
                filename += ".png"
        self.scene().clearSelection()
        self.scene().clearFocus()
        old_brush = self.scene().backgroundBrush()
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
        self.scene().setBackgroundBrush(old_brush)

    def load_file(self, filename):
        ''' Parse a PR file and render it on the scene '''
        self.filename = filename
        process, warnings, errors = ogParser.parseProcessDefinition(
                fileName=self.filename)
        LOG.debug('Parsing complete. Summary, found ' + str(len(warnings)) +
                ' warnings and ' + str(len(errors)) + ' errors')
        self.log_errors(errors, warnings)
        global PROCESS_NAME
        PROCESS_NAME = process.processName or 'opengeode'
        self.wrappingWindow.setWindowTitle('process ' + PROCESS_NAME + '[*]')
        self.scene().add_process_from_ast(process)
        self.refresh()
        self.centerOn(self.sceneRect().topLeft())
        self.scene().undo_stack.clear()

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
        if not self.scene().undo_stack.isClean():
            # If changes occured since last save, pop up a window
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle('OpenGEODE')
            msg_box.setText("The model has been modified.")
            msg_box.setInformativeText("Do you want to save your changes?")
            msg_box.setStandardButtons(QMessageBox.Save |
                    QMessageBox.Discard |
                    QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Save)
            ret = msg_box.exec_()
            if ret == QMessageBox.Save:
                if not self.save_diagram():
                    return False
            elif ret == QMessageBox.Discard:
                pass
            elif ret == QMessageBox.Cancel:
                return False
        self.scene().undo_stack.clear()
        self.scene().clear()
        G_SYMBOLS.clear()
        global PROCESS_NAME
        PROCESS_NAME = ''
        self.filename = None
        self.wrappingWindow.setWindowTitle('process[*]')
        self.enableMenuItem.emit('Start')
        return True

    def log_errors(self, errors, warnings):
        ''' Report Error and Warnings on the console and in the log window '''
        if self.messagesWindow:
            self.messagesWindow.clear()
        for error in errors:
            LOG.error(error[0])
            if type(error[0]) == list:
                # FIXME
                continue
            item = QListWidgetItem(u'[ERROR] ' + error[0])
            if len(error) == 2:
                item.setData(Qt.UserRole, error[1])
            if self.messagesWindow:
                self.messagesWindow.addItem(item)
        for warning in warnings:
            LOG.warning(warning[0])
            item = QListWidgetItem(u'[WARNING] ' + warning[0])
            if len(warning) == 2:
                item.setData(Qt.UserRole, warning[1])
            if self.messagesWindow:
                self.messagesWindow.addItem(item)
        if not errors and not warnings and self.messagesWindow:
            self.messagesWindow.addItem('No errors, no warnings!')

    def check_model(self):
        ''' Parse the model and check for warnings and errors '''
        pr_data = self.scene().getPrData()
        if pr_data:
            _, warnings, errors = ogParser.parseProcessDefinition(
                    string=pr_data)
            self.log_errors(errors, warnings)

    def generate_ada(self):
        ''' Generate Ada code '''
        pr_data = self.scene().getPrData()
        if pr_data:
            process, warnings, errors = ogParser.parseProcessDefinition(
                    string=pr_data)
            self.log_errors(errors, warnings)
            if len(errors) > 0:
                self.messagesWindow.addItem(
                        'Aborting: too many errors to generate code')
            else:
                self.messagesWindow.addItem('Generating Ada code')
                try:
                    AdaGenerator.generate(process)
                    self.messagesWindow.addItem('Done')
                except (TypeError, ValueError, NameError):
                    self.messagesWindow.addItem('Code generation failed')


class OG_MainWindow(QMainWindow):
    ''' Main GUI window '''
    def __init__(self, parent=None):
        ''' Create the main window '''
        super(OG_MainWindow, self).__init__(parent)
        self.view = None
        self.scene = None

    def start(self, file_name):
        ''' Initializes all objects to start the application '''
        # Create a graphic scene: the main canvas
        self.scene = SDL_Scene()
        # Find SDL_View widget
        self.view = self.findChild(SDL_View, 'graphicsView')
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

        # Add a toolbar widget (not in .ui file due to pyside bugs)
        toolbar = Sdl_toolbar(self)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)

        # Add a toolbar with New/Open/Save/Check buttons
        filebar = File_toolbar(self)
        filebar.open_button.activated.connect(self.view.open_diagram)
        filebar.new_button.activated.connect(self.view.new_diagram)
        filebar.check_button.activated.connect(self.view.check_model)
        filebar.save_button.activated.connect(self.view.save_diagram)
        self.addToolBar(Qt.TopToolBarArea, filebar)

        # Connect toolbar actions
        self.scene.selectionChanged.connect(toolbar.update_menu)
        self.scene.disableMenuItem.connect(toolbar.disable_action)
        self.scene.enableMenuItem.connect(toolbar.enable_action)
        self.view.enableMenuItem.connect(toolbar.enable_action)
        for item in toolbar.actions.viewkeys():
            toolbar.actions[item].triggered.connect(self.scene.actions[item])

        self.scene.clearSelection()
        self.scene.clearFocus()

        # widget wrapping the view. We have to maximize it
        process_widget = self.findChild(QWidget, 'process')
        process_widget.showMaximized()
        self.view.wrappingWindow = process_widget
        self.scene.undo_stack.cleanChanged.connect(
                lambda x: process_widget.setWindowModified(not x))

        # get the messages list window (to display errors and warnings)
        # it is a QListWidget
        msg_dock = self.findChild(QDockWidget, 'msgDock')
        msg_dock.setWindowTitle('Use F7 to check the model')
        msg_dock.setStyleSheet('QDockWidget::title {background: lightgrey;}')
        messages = self.findChild(QListWidget, 'messages')
        messages.addItem('Welcome to OpenGEODE.')
        self.view.messagesWindow = messages
        self.scene.messagesWindow = messages
        messages.itemClicked.connect(self.scene.show_item)

        if file_name:
            self.view.load_file(file_name)
        self.show()

    def closeEvent(self, event):
        ''' Close main application '''
        if self.view.new_diagram():
            super(OG_MainWindow, self).closeEvent(event)
        else:
            event.ignore()


def opengeode():
    ''' Tool entry point '''
    # Catch Ctrl-C to stop the app from the console
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    # Initialize logging
    terminal_formatter = logging.Formatter(
            fmt="[%(levelname)s] %(message)s")
    handler_console = logging.StreamHandler()
    handler_console.setFormatter(terminal_formatter)
    LOG.addHandler(handler_console)

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/input.png'))

    # Parse the command line
    usage = ('usage: opengeode.py [--verbose] [--open | --check | '
             '--toAda file.pr]')
    parser = optparse.OptionParser(usage=usage, version=__version__)
    parser.add_option('-v', '--verbose', action='store_true', default=False,
            help='Display debug information')
    parser.add_option('--check', metavar='file.pr', dest='check',
            help='Check a .pr file for syntax and semantics')
    parser.add_option('-o', '--open', metavar='file.pr', dest='loadGR',
            help='Load a .pr file in the graphical editor')
    parser.add_option('--toAda', dest='toAda', metavar='file.pr',
            help='Generate Ada code for the .pr file')
    options, _ = parser.parse_args()
    ret = 0
    if options.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    # Set log level for all libraries
    LOG.setLevel(level)
    for module in (sdlSymbols, genericSymbols, ogAST, ogParser,
            AdaGenerator, undoCommands):
        module.LOG.addHandler(handler_console)
        module.LOG.setLevel(level)

    LOG.debug('Starting OpenGEODE version ' + __version__)

    file_name = options.check or options.toAda
    if file_name:
        LOG.info('Checking ' + str(file_name))
        process, warnings, errors = ogParser.parseProcessDefinition(
                fileName=file_name)
        LOG.info('Parsing complete. Summary, found ' +
                str(len(warnings)) +
                ' warnings and ' +
                str(len(errors)) +
                ' errors')
        for warning in warnings:
            LOG.warning(warning[0])
        for error in errors:
            LOG.error(error[0])
        if len(errors) > 0:
            ret = -1
        if options.toAda:
            if len(errors) > 0:
                LOG.error('Too many errors, cannot generate Ada code')
            else:
                LOG.info('Generating Ada code')
                try:
                    AdaGenerator.generate(process)
                except (TypeError, ValueError, NameError):
                    LOG.error('Code generation did not succeed')
    else:
        LOG.debug('Running the GUI')
        # Load the application layout from the .ui file
        loader = QUiLoader()
        loader.registerCustomWidget(OG_MainWindow)
        loader.registerCustomWidget(SDL_View)
        #loader.registerCustomWidget(Sdl_toolbar)
        ui_file = QFile(':/opengeode.ui')
        ui_file.open(QFile.ReadOnly)
        my_widget = loader.load(ui_file)
        ui_file.close()
        my_widget.start(options.loadGR)
        ret = app.exec_()
    return(ret)

if __name__ == '__main__':
    sys.exit(opengeode())
