#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Generic library containing the definition of top-level symbols
    that can be used to create diagrams.

    The Symbol class contains common behaviour shared by inherited
    symobols - in particular the VerticalSymbol is a class of symbols
    that can only be vertically aligned ; Horizontal symbols, on the
    other hand, can be move in both directions.

    The "Comment" class of symbols is a floating symbol that is
    connected to a parent symbol on the right.

    This library also contains the defintition of connections
    (the Connection class).

    Symbols can have an editable text area, which behaviour is
    defined in the EditableText class. This class uses the Completer
    and Highlighter class for text auto-completion and syntax
    highlighting.


    Major functionalities offered by the generic Symbol classes are
    the insersion and deletion of items (possibly recursively if there
    are child symbols), the moving and resizing, the collision
    avoidance manoeuvres (when moving a group of symbols on top
    of another group, it has the effect of "pushing" the colliders
    so that symbols never "touch" each others - keeping the diagram
    clean.

    In order to create a specific diagram editor, the user of this
    library shall create his own symbols, that inherit either from
    Horizontal- or VerticalSymbol classes. The geometry of the symbol
    has to be defined in these subclass by defining the polygon
    and other properties (colours, filling, etc.). Some methods can
    be redefined if a particular behaviour is required (e.g. resizing
    differently, holding different connections points, etc).

    For a complete example, look at the "sdlSymbols.py" module, that
    provide symbol definitions that correspond to an SDL editor.

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin for the TASTE project

    Contact: maxime.perrotin@esa.int
"""

import os
import sys

from PySide.QtCore import(Qt, QPoint, QPointF, QRect, Slot, QRegExp, QFile)

from PySide.QtGui import(QGraphicsTextItem, QGraphicsPathItem,
        QGraphicsPolygonItem, QPainterPath, QGraphicsItem,
        QGraphicsItemGroup, QCompleter, QGraphicsProxyWidget, QListWidget,
        QListWidgetItem, QTextCursor, QSyntaxHighlighter, QTextCharFormat,
        QFont, QPolygon, QPen, QColor, QMenu, QFileDialog, QImage, QPainter,
        QLineEdit, QBrush, QTextBlockFormat)

from PySide.QtUiTools import QUiLoader

from undoCommands import ReplaceText, ResizeSymbol, MoveSymbol

# Remove the following line when the Comment symbol is moved to sdlSymbols.py
import ogAST
import ogParser

if hasattr(sys, 'frozen'):
    # Detect py2exe distribution (that does not support the __file__ construct)
    CUR_DIR = os.path.dirname(unicode
            (sys.executable, sys.getfilesystemencoding()))
else:
    CUR_DIR = os.path.dirname(os.path.realpath(__file__))

# UI_DIALOG_FILE = os.path.join(CUR_DIR, 'hyperlink.ui')


class Completer(QGraphicsProxyWidget):
    ''' Class for handling text autocompletion in the SDL scene '''
    def __init__(self, parent):
        ''' Create an autocompletion list popup '''
        widget = QListWidget()
        super(Completer, self).__init__(parent.parentItem())
        self.setWidget(widget)
        self.c = QCompleter(parent.parentItem().completion_list)
        self.c.setCaseSensitivity(Qt.CaseInsensitive)
        self.parent = parent

    def set_completion_prefix(self, completion_prefix):
        '''
        Set the current completion prefix (user-entered text)
        and set the corresponding list of words in the popup widget
        '''
        if not hasattr(self, 'c'):
            return 0
        self.c.setCompletionPrefix(completion_prefix)
        self.widget().clear()
        for i in xrange(self.c.completionCount()):
            self.c.setCurrentRow(i)
            self.widget().addItem(self.c.currentCompletion())
        self.resize(self.widget().sizeHintForColumn(0) + 40, 70)
        return self.c.completionCount()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hide()
            self.parent.setFocus()
        super(Completer, self).keyPressEvent(e)

    def focusOutEvent(self, event):
        ''' When the user leaves the popup, return focus to parent '''
        self.hide()
        self.parent.setFocus()
        super(Completer, self).focusOutEvent(event)


class Highlighter(QSyntaxHighlighter):
    ''' Class for handling syntax highlighting in editable text '''
    def __init__(self, parent=None):
        ''' Define highlighting rules '''
        super(Highlighter, self).__init__(parent)
        self.highlightingRules = []

        # Black bold items (allowed keywords)
        blackBoldFormat = QTextCharFormat()
        blackBoldFormat.setFontWeight(QFont.Bold)
        blackBoldPatterns = ['\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT')]
        self.highlightingRules = [(QRegExp(pattern, cs=Qt.CaseInsensitive),
            blackBoldFormat) for pattern in blackBoldPatterns]

        # Red bold items (reserved keywords)
        redBoldFormat = QTextCharFormat()
        redBoldFormat.setFontWeight(QFont.Bold)
        redBoldFormat.setForeground(Qt.red)
        redBoldPatterns = ['\\b{word}\\b'.format(word=word) for word in (
                'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE',
                'TASK', 'TIMER', 'PROCESS', 'PROCEDURE', 'LABEL', 'JOIN')]
        for p in redBoldPatterns:
            self.highlightingRules.append(
                    (QRegExp(p, cs=Qt.CaseInsensitive), redBoldFormat))

        # Comments
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(Qt.darkBlue)
        commentFormat.setFontItalic(True)
        self.highlightingRules.append((QRegExp('--[^\n]*'), commentFormat))

    def highlightBlock(self, text):
        ''' Redefined function to apply the highlighting rules '''
        for expression, formatter in self.highlightingRules:
            index = expression.indexIn(text)
            while (index >= 0):
                length = expression.matchedLength()
                self.setFormat(index, length, formatter)
                index = expression.indexIn(text, index + length)


class EditableText(QGraphicsTextItem):
    '''
        Editable text area inside symbols
        Includes autocompletion when parent item needs it
    '''
    def __init__(self, parent, text='...', hyperlink=None):
        super(EditableText, self).__init__(parent)
        self.completer = None
        self.hyperlink = hyperlink
        self.setOpenExternalLinks(True)
        if hyperlink:
            self.setHtml('<a href="{hlink}">{text}</a>'.format
                    (hlink=hyperlink, text=text.replace('\n', '<br>')))
        else:
            self.setPlainText(text)
        self.setTextInteractionFlags(
                Qt.TextEditorInteraction
                | Qt.LinksAccessibleByMouse
                | Qt.LinksAccessibleByKeyboard)
        self.completer_has_focus = False
        self.editing = False
        self.try_resize()
        self.highlighter = Highlighter(self.document())
        self.completion_prefix = ''
        self.set_textbox_position()
        self.set_text_alignment()

    def __str__(self):
        ''' Print the text inside the symbol '''
        return self.toPlainText()

    def set_text_alignment(self):
        ''' Apply the required text alignment within the text box '''
        alignment = self.parentItem().text_alignment
        self.setTextWidth(self.boundingRect().width())
        fmt = QTextBlockFormat()
        fmt.setAlignment(alignment)
        cursor = self.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.mergeBlockFormat(fmt)
        cursor.clearSelection()
        self.setTextCursor(cursor)

    def set_textbox_position(self):
        ''' Compute the textbox position '''
        parentRect = self.parentItem().boundingRect()
        rect = self.boundingRect()
        # Use parent symbol alignment requirement
        # Can be extended to support more combinations..
        alignment = self.parentItem().textbox_alignment
        if alignment & Qt.AlignCenter:
            self.setPos(parentRect.center() - rect.center())
        elif (alignment & Qt.AlignTop) and (alignment & Qt.AlignLeft):
            self.setPos(0, 0)

    def paint(self, painter, _, __):
        ''' Place the text properly in the middle of the parent symbol '''
        self.set_textbox_position()
        super(EditableText, self).paint(painter, _, __)

    def try_resize(self):
        '''
            If needed, request a resizing of the parent item
            (when text size expands)
        '''
        parentRect = self.parentItem().boundingRect()
        rect = self.boundingRect()
        if rect.width() + 30 > parentRect.width():
            parentRect.setWidth(rect.width() + 30)
        parentRect.setHeight(max(rect.height(), parentRect.height()))
        self.parentItem().resizeItem(parentRect)

    @Slot(QListWidgetItem)
    def completion_selected(self, item):
        '''
            Slot connected to the autocompletion popup,
            invoked when selection is made
        '''
        tc = self.textCursor()
        extra = len(item.text()) - len(self.completion_prefix)
        if extra > 0:
            tc.movePosition(QTextCursor.Left)
            tc.movePosition(QTextCursor.EndOfWord)
            tc.insertText(item.text()[-extra:])
            self.setTextCursor(tc)
        self.completer_has_focus = False
        self.completer.hide()

    def keyPressEvent(self, event):
        '''
            Activate the autocompletion window if relevant
        '''
        super(EditableText, self).keyPressEvent(event)
        self.try_resize()
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        self.completion_prefix = tc.selectedText()
        #if(hasattr(self.parentItem(), 'completion_list') and not
        #        self.completer):
        if not self.completer:
            self.completer = Completer(self)
            self.completer.widget().itemActivated.connect(
                    self.completion_selected)
        if self.completer:
            completion_count = self.completer.set_completion_prefix(
                    self.completion_prefix)
            if completion_count > 0 and (len(self.completion_prefix) > 1 or
                    event.key() == Qt.Key_F8):
                # Computing the position of the completer
                # No direct Qt function for that.. doing it the hard way
                pos = self.textCursor().positionInBlock()
                block = self.textCursor().block()
                layout = block.layout()
                line = layout.lineForTextPosition(pos)
                rect = line.rect()
                relative_x, _ = line.cursorToX(pos)
                layout_pos = layout.position()
                pos_x = self.x() + relative_x + layout_pos.x()
                pos_y = self.y() + rect.y() + rect.height() + layout_pos.y()

                self.completer.setPos(pos_x, pos_y)
                self.completer.show()
                self.completer.setFocusProxy(self)
                self.setTabChangesFocus(True)
            else:
                self.completer.setFocusProxy(None)
                self.completer.hide()
                self.setFocus()
            self.completer_has_focus = False
            if self.completer.isVisible() and event.key() == Qt.Key_Down:
                self.completer_has_focus = True
                self.completer.setFocusProxy(None)
                self.completer.widget().setFocus()

    def focusOutEvent(self, event):
        '''
            When the user stops editing, this function is called
            In that case, hide the completer if it is not the item
            that got the focus.
        '''
        if not self.editing:
            return super(EditableText, self).focusOutEvent(event)
        if self.completer and not self.completer_has_focus:
            self.completer.hide()
            self.completer.resize(0, 0)
        if not self.completer or not self.completer.isVisible():
            if self.oldSize != self.parentItem().boundingRect():
                undoCmd = ResizeSymbol(self.parentItem(), self.oldSize,
                        self.parentItem().boundingRect())
                self.scene().undo_stack.push(undoCmd)
                self.parentItem().cam(self.parentItem().pos(),
                        self.parentItem().pos())
            if self.oldText != str(self):
                undoCmd = ReplaceText(self, self.oldText, str(self))
                self.scene().undo_stack.push(undoCmd)
                self.scene().undo_stack.endMacro()
            else:
                self.scene().undo_stack.endMacro()
            self.editing = False
            tc = self.textCursor()
            if tc.hasSelection():
                tc.clearSelection()
                self.setTextCursor(tc)
            # Call syntax checker from item containing the text (if any)
            self.parentItem().checkSyntax()
        self.setSelected(False)
        self.set_text_alignment()
        super(EditableText, self).focusOutEvent(event)

    def focusInEvent(self, event):
        ''' When user starts editing text, save previous state for Undo '''
        super(EditableText, self).focusInEvent(event)
        # Clear selection otherwise the "Delete" key may delete other items
        self.scene().clearSelection()
        # Set width to auto-expand, and disables alignment, while editing:
        self.setTextWidth(-1)
        if self.completer:
            self.completer.resize(0, 0)
        if not self.editing:
            self.scene().undo_stack.beginMacro('Edit text')
            self.oldText = str(self)
            self.oldSize = self.parentItem().boundingRect()
            self.editing = True
        # super(EditableText, self).focusInEvent(event)

#    def mousePressEvent(self, event):
#        '''
#            When the user clicks on the text symbol (to edit),
#            the list of selected objects on the diagram must be cleared
#            to prevent the the "Delete" key from removing the selected objects
#        '''
#        self.scene().clearSelection()
#        super(EditableText, self).mousePressEvent(event)

    def __repr__(self):
        '''
            Return the PR notation for the hyperlink
            TODO: remove from here, put in SDL symbols
        '''
        if self.hyperlink:
            return(
                "/* CIF Keep Specific Geode HyperLink '{hlink}' */\n".format(
                    hlink=self.hyperlink))
        else:
            return ''


class Connection(QGraphicsPathItem):
    ''' Connection between two symbols (arrow) '''
    def __init__(self, parent, child, connectionPoint=False):
        super(Connection, self).__init__(parent)
        self.parent = parent
        self.child = child
        self.childIsAConnectionPoint = connectionPoint
        self.startPoint = QPointF(0, 0)
        self.endPoint = QPointF(0, 0)
        self.update_lines()
        pen = QPen()
        pen.setColor(Qt.blue)
        pen.setCosmetic(False)
        self.setPen(pen)
        self.parentRect = parent.sceneBoundingRect()
        self.childRect = child.sceneBoundingRect()

    def __str__(self):
        ''' Print connection information for debug purpose'''
        return 'Connection: parent = {p}, child = {c}'.format(
                p=str(self.parentItem()), c=str(self.child))

    def update_lines(self):
        ''' Update the connection line '''
        if(self.parentItem().terminalSymbol
                and self.childIsAConnectionPoint):
            self.setPath(QPainterPath())
            return
        arrowPath = QPainterPath()
        parentRect = self.parentItem().boundingRect()
        # Define connection start point
        if hasattr(self.parentItem(), 'connectionPoint') and not isinstance(
                self.child, (HorizontalSymbol, Comment)):
            self.startPoint = self.parentItem().connectionPoint
        elif isinstance(self.child, Comment):
            self.startPoint = QPointF(
                    parentRect.width(), parentRect.height() / 2)
        else:
            self.startPoint = QPointF(
                    parentRect.width() / 2, parentRect.height())
        # Defined connection end point
        if self.childIsAConnectionPoint:
            connectionPointScene = self.child.mapToScene(
                    self.child.connectionPoint)
            connectionPointLocal = self.parentItem().mapFromScene(
                    connectionPointScene)
            self.endPoint = connectionPointLocal
        elif isinstance(self.child, Comment):
            if self.child.onTheRight:
                self.endPoint = QPointF(self.child.x(),
                        self.child.y() +
                        self.child.boundingRect().height() / 2)
            else:
                self.endPoint = QPointF(self.child.x() +
                        self.child.boundingRect().width(),
                        self.child.y() +
                        self.child.boundingRect().height() / 2)
        else:
            self.endPoint = QPointF()
            self.endPoint.setY(self.child.pos().y())
        # Move to start point and draw the connection
        arrowPath.moveTo(self.startPoint)
        if not self.childIsAConnectionPoint and not isinstance(
                self.child, Comment):
            if isinstance(self.child, HorizontalSymbol):
                self.endPoint.setX(self.child.pos().x() +
                        self.child.boundingRect().width() / 2)
                arrowPath.lineTo(self.startPoint.x(), self.startPoint.y() + 10)
                arrowPath.lineTo(self.endPoint.x(), self.startPoint.y() + 10)
            else:
                self.endPoint.setX(self.startPoint.x())
        elif isinstance(self.child, Comment):
            # Make sure the connection does not overlap the comment item
            if (self.child.onTheRight or
                    (not self.child.onTheRight and
                        self.child.x() + self.child.boundingRect().width()
                        < self.parentItem().boundingRect().width())):
                goToPoint = self.startPoint.x() + 5
            else:
                goToPoint = self.endPoint.x() + 5
            arrowPath.lineTo(goToPoint, self.startPoint.y())
            arrowPath.lineTo(goToPoint, self.endPoint.y())
            arrowPath.lineTo(self.endPoint.x(), self.endPoint.y())
        else:
            arrowPath.lineTo(self.startPoint.x(), self.endPoint.y() - 10)
            arrowPath.lineTo(self.endPoint.x(), self.endPoint.y() - 10)
        arrowPath.lineTo(self.endPoint)
        # If required draw an arrow head (e.g. in SDL NEXTSTATE and GOTO)
        if hasattr(self.child, 'arrowHead'):
            arrowPath.lineTo(self.endPoint.x() - 5, self.endPoint.y() - 5)
            arrowPath.moveTo(self.endPoint)
            arrowPath.lineTo(self.endPoint.x() + 5, self.endPoint.y() - 5)
        self.setPath(arrowPath)

# Notes on performance: boundingRect() is called by Qt to know if the item
# has to be painted. Therefore the call is very frequent, so it is better
# not to re-implement this function. It is called more often than paint
# Paint is also called often - whenever anything changes on the scene,
# all the paint methods of all the visible items are called - frequently,
# but a bit less than boundingRect. The problem anyway is that boundingRect
# has to return a proper rectangle for Qt to know if paint must be called.
# This means that the shape of the drawing cannot not be defined in paint.
# It is now done in the "update_lines" method, which is called whenever
# something changes on a symbol (see changeItem function on class Symbol).
#    def boundingRect(self):
#        ''' Compute the line shape and return the bounding rect '''
#        if(self.parentRect != self.parent.sceneBoundingRect() or
#                self.childRect != self.child.sceneBoundingRect()):
#            self.update_lines()
#            self.parentRect = self.parent.sceneBoundingRect()
#            self.childRect = self.child.sceneBoundingRect()
#        return super(Connection, self).boundingRect()

    def paint(self, painter, _, __):
        ''' Draw the connection '''
        self.update_lines()
        super(Connection, self).paint(painter, _, __)


class Symbol(QGraphicsPolygonItem):
    ''' Top-level class used to handle all SDL symbols '''
    # Symbols of a given type share a text-autocompletion list:
    completion_list = []
    # Symbols of a given type can be graphically followed to:
    allowed_followers = []

    def __init__(self, parent=None):
        '''
            Create top level symbol and propagate important properties
            from parent items
        '''
        super(Symbol, self).__init__()
        self.mode = ''
        self.text = ''
        self.comment = None
        self.loadHyperlinkDialog()
        # hasParent compensates a Qt (or PySide) bug when calling parentItem()
        # on top-level items
        self.hasParent = False
        self.parent = None
        # allowedFollowers property defines the allowed child set of symbols
        self.allowedFollowers = []
        # Common name is the name of the symbol as used in a parser or backend
        self.commonName = ''
        # Optional parser for the symbol textual representation
        self.parser = None
        # branch entry point allows working with aligned symbols
        self.branchEntryPoint = None
        # Terminal symbol can be used to identify last items of a branch
        self._terminal_symbol = False
        # default textbox alignment: centered in the symbol
        # can differ on specific symbols (e.g. TextArea or label)
        self.textbox_alignment = Qt.AlignCenter
        # and default text alignment within a textbox
        self.text_alignment = Qt.AlignLeft
        self.setFlags(
                QGraphicsItem.ItemIsMovable
                | QGraphicsItem.ItemIsSelectable)
#                | QGraphicsItem.ItemSendsGeometryChanges)
#                | QGraphicsItem.ItemSendsScenePositionChanges)

# Performance of itemChange is not good enough - commented out
#    def itemChange(self, change, value):
#        '''
#            Function called by Qt when anything happens to the symbol
#            Used to detect when connection lines need to be re-computed
#        '''
#        if change in (QGraphicsItem.GraphicsItemChange.ItemPositionChange,
#                      QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged,
#                      QGraphicsItem.GraphicsItemChange.ItemChildAddedChange):
#            for cnx in self.connections():
#                cnx.update_lines()
#            if self.hasParent:
#                for cnx in self.parentItem().connections():
#                    cnx.update_lines()
#        return super(Symbol, self).itemChange(change, value)

    @property
    def terminalSymbol(self):
        ''' Way to determine if a symbol is terminal (useful for branches) '''
        return self._terminal_symbol

    @terminalSymbol.setter
    def terminalSymbol(self, value):
        ''' Attribute is set per symbol '''
        self._terminal_symbol = value

    def __str__(self):
        ''' Print the text inside the symbol '''
        return str(self.text)

    def parseGR(self, recursive=True):
        ''' Parse the graphical representation '''
        return repr(self)

    def get_ast(self):
        ''' Return the symbol in the AST form, as returned by the parser '''
        if not self.parser or not hasattr(self.parser, 'parseSingleElement'):
            print('[ERROR] No parser found')
            return
        ast, _, __, ___, terminators = self.parser.parseSingleElement(
            self.commonName, repr(self))
        return ast, terminators

    def checkSyntax(self):
        ''' Check the syntax of the text inside the symbol (if any) '''
        if not self.parser or not hasattr(self.parser, 'parseSingleElement'):
            print('[ERROR] No parser found')
            return
        _, syntaxErrors, __, ___, ____ = self.parser.parseSingleElement(
                self.commonName, repr(self))
        try:
            self.scene().reportErrors(syntaxErrors)
        except:
            print('[SYNTAX ERROR]', '\n'.join(syntaxErrors))

    def paint(self, painter, _, __):
        ''' Apply anti-aliasing only for Symbols - not for Connections '''
        painter.setRenderHint(QPainter.Antialiasing, True)
        super(Symbol, self).paint(painter, _, __)

    def insertSymbol(self, parent, x, y):
        '''
            Set attributes related to the parent item when inserting the symbol
            in the scene. This method is redefined in subclasses
        '''
        if parent:
            self.hasParent = True
            self.parent = parent
            self.setParentItem(parent)

    def deleteSymbol(self):
        '''
            Remove the symbol: pass ownership from parent to caller
            (undo command)
        '''
        entryPointParent = None
        if self.branchEntryPoint:
            # If the item is the last in a branch, make clean connections
            bep = self.branchEntryPoint
            entryPointParent = bep.parentItem()
            if bep.lastBranchItem is self:
                # Last item of a branch, remove or reconnect the link
                # to the connection point
                for child in self.childItems():
                    # Find the connection point below
                    if(isinstance(child, Connection) and
                            child.childIsAConnectionPoint):
                        connectionBelow = child
                        break
                if bep is not self:
                    # Item is not the branch entry point itself
                    bep.lastBranchItem = self.parentItem()
                    connectionBelow.setParentItem(self.parentItem())
                    self.parentItem().connectionBelow = connectionBelow
                else:
                    # delete the link to the connection point
                    connectionBelow.setParentItem(None)
                    self.scene().removeItem(connectionBelow)
        childBelow = self.nextAlignedSymbol()
        if(childBelow and self.hasParent and
                self.parentItem().nextAlignedSymbol() is self):
            # Delete the connection to the child below if
            # it is not a full branch to be deleted
            childBelow.connection.setParentItem(None)
            self.scene().removeItem(childBelow.connection)
        if self.hasParent:
            if (not childBelow or not self.parentItem().nextAlignedSymbol() or
                        self.branchEntryPoint is self):
                # If nothing below or item is branch entry point,
                # remove the connection with the parent
                self.connection.setParentItem(None)
                self.scene().removeItem(self.connection)
            else:
                # Otherwise connect the item below with the parent
                childBelow.connection = self.connection
                self.connection.child = childBelow
                childBelow.parent = self.parentItem()
                childBelow.setParentItem(childBelow.parent)
            self.setParentItem(None)
        self.scene().removeItem(self)
        if entryPointParent:
            entryPointParent.updateConnectionPointPosition()
            entryPointParent.updateConnectionPoints()

    def connectToParent(self):
        ''' Add a connection (wire) with the parent item '''
        return Connection(self.parent, self)

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow - implemented in subclasses '''
        return None

    def connections(self):
        ''' Return all child connections of this symbol '''
        return (c for c in self.childItems() if isinstance(c, Connection))

    def loadHyperlinkDialog(self):
        ''' Load dialog from ui file for defining hyperlink '''
        loader = QUiLoader()
        uiFile = QFile(':/hyperlink.ui')  # UI_DIALOG_FILE)
        uiFile.open(QFile.ReadOnly)
        self.hyperlink_dialog = loader.load(uiFile)
        uiFile.close()
        self.hyperlink_dialog.accepted.connect(self.hyperlinkChanged)
        self.hlink_field = self.hyperlink_dialog.findChild(QLineEdit, 'hlink')

    def hyperlinkChanged(self):
        ''' Update hyperlink field '''
        if not self.text:
            return
        hlink = self.hlink_field.text()
        if hlink:
            self.text.setHtml('<a href="{hlink}">{text}</a>'.format
                    (hlink=hlink, text=str(self.text).replace('\n', '<br>')))
            self.text.hyperlink = hlink
        else:
            self.text.hyperlink = None
            self.text.setPlainText(str(self.text))

    def contextMenuEvent(self, event):
        ''' When user right-clicks: display context menu '''
        pngAction = 'Export branch to PNG'
        hlAction = 'Hyperlink'
        myMenu = QMenu(pngAction)
        if not hasattr(self, '_no_hyperlink'):
            myMenu.addAction(hlAction)
        myMenu.addAction(pngAction)
        action = myMenu.exec_(event.screenPos())
        if action:
            if action.text() == pngAction:
                # Save a PNG of the selected symbol and all its children
                filename = QFileDialog.getSaveFileName(self.window(),
                        'Export picture', '.', 'Picture (*.png)')[0]
                if not filename:
                    return
                if filename.split('.')[-1] != 'png':
                    filename += '.png'
                oldBrush = self.scene().backgroundBrush()
                self.scene().setBackgroundBrush(QBrush())
                completeRect = (self.childrenBoundingRect() |
                                self.boundingRect())
                # Add some margin for the antialiasing (5 pixels on each side)
                completeRect.adjust(-5, -5, 5, 5)
                rect = self.mapRectToScene(completeRect)
                image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
                image.fill(Qt.transparent)
                painter = QPainter(image)
                painter.setRenderHint(QPainter.Antialiasing)
                self.setSelected(False)
                self.scene().render(painter, source=rect)
                image.save(filename)
                if painter.isActive():
                    painter.end()
                self.setSelected(True)
                self.scene().setBackgroundBrush(oldBrush)
            elif action.text() == hlAction:
                if self.text:
                    self.hyperlink_dialog.setParent(
                            self.scene().views()[0], Qt.Dialog)
                    self.hlink_field.setText(self.text.hyperlink)
                    self.hyperlink_dialog.show()

    def childSymbols(self):
        ''' Return the list of child symbols, excluding text/connections '''
        return (item for item in self.childItems() if isinstance(item, Symbol))

    def resizeItem(self, rect):
        ''' resize item, e.g. when editing text - move children accordingly '''
        deltaX = (self.boundingRect().width() - rect.width()) / 2
        deltaY = self.boundingRect().height() - rect.height()
        self.prepareGeometryChange()
        polygon = self.computePolygon(rect.width(), rect.height())
        self.setPolygon(polygon)
        # Align children properly when resizing
        for child in (c for c in self.childItems()
                if not isinstance(c, Connection)):
            # includes position of the text inside the box
            child.moveBy(-deltaX, 0)
        for child in self.childSymbols():
            child.moveBy(0, -deltaY)
        self.moveBy(deltaX, 0)

    def computePolygon(self, width, height):
        ''' To be implemented per symbol in subclasses '''
        pass

    def mousePressEvent(self, event):
        '''
            Handle resizing and moving of items when grabbing
            the lower right corner
        '''
        # super(Symbol, self).mousePressEvent(event)
        # Save current position to be able to revert move
        self.coord = self.pos()
        eventPos = event.pos()
        rect = self.boundingRect()
        self.height = rect.height()
        if(eventPos.x() > rect.width() - 10 and
                eventPos.y() > rect.height() - 10):
            self.mode = 'Resize'
            self.oldRect = self.boundingRect()
        else:
            self.mode = 'Move'
            super(Symbol, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        ''' Handle resizing of items - moving is handled in subclass '''
        self.updateConnectionPoints()
        if self.mode == 'Resize':
            # Minimum size is the size of the text inside the symbol
            if self.text:
                newY = max(event.pos().y(),
                        self.text.boundingRect().height() + 10)
                newX = max(event.pos().x(),
                           self.text.boundingRect().width() + 30)
            else:
                newY = max(event.pos().y(), 15)
                newX = max(event.pos().x(), 30)
            self.resizeItem(QRect(0, 0, newX, newY))

    def mouseReleaseEvent(self, event):
        ''' Default action when mouse is released: reset mode '''
        if self.mode == 'Resize':
            pass
            self.scene().undo_stack.beginMacro('Resize symbol')
            undoCmd = ResizeSymbol(self, self.oldRect, self.boundingRect())
            self.scene().undo_stack.push(undoCmd)
            self.cam(self.coord, self.pos())
            self.updateConnectionPoints()
            self.scene().undo_stack.endMacro()
        elif self.mode == 'Move':
            self.scene().undo_stack.beginMacro('Move symbol')
            undoCmd = MoveSymbol(self, self.coord, self.pos())
            self.scene().undo_stack.push(undoCmd)
            self.cam(self.coord, self.pos())
            self.scene().undo_stack.endMacro()
        self.mode = ''

    def updateConnectionPoints(self):
        ''' Recursively update connection points (decision branch lengths) '''
        if(self.branchEntryPoint and self.branchEntryPoint.hasParent):
            self.branchEntryPoint.parentItem().updateConnectionPointPosition()
            self.branchEntryPoint.parentItem().updateConnectionPoints()

    def updateConnectionPointPosition(self):
        ''' Implemented in the relevant subclass '''
        pass

    def cam(self, oldPos, newPos, ignore=None):
        ''' Collision Avoidance Manoeuvre for top level symbols '''
        if not self.scene():
            # Make sure the item is in a scene. For instance, when loading
            # a model from a file, some items may be connected together
            # and CAM called *before* the top-level item has been inserted.
            return
        if self.hasParent:
            # Exectute CAM on top level of this item
            selfTopLevel = self
            while selfTopLevel.hasParent:
                # The "or selfTopLevel.parent" below is due to a Pyside/Qt bug
                # of the parentItem() function. It can happen that even when
                # the parent has explicitely been set with "setParentItem",
                # a subsequent call to parentItem returns None. Seems to happen
                # if the parent has not been added yet to the scene.
                selfTopLevel = selfTopLevel.parentItem() or selfTopLevel.parent
            selfTopLevel.cam(selfTopLevel.pos(), selfTopLevel.pos())
            return

        # In case CAM is called due to object move, go to the new position
        delta = newPos - oldPos

        # Rectangle of current group of item in scene coordinates
        rect = (self.sceneBoundingRect() |
                self.mapRectToScene(self.childrenBoundingRect()))

        # Move the rectangle to the new position, and move the current item
        if self.pos() != newPos:
            rect.adjust(delta.x(), delta.y(), delta.x(), delta.y())
            self.setPos(newPos)
            undoCmd = MoveSymbol(self, oldPos, newPos)
            self.scene().undo_stack.push(undoCmd)

        # Get all items in the rectangle when placed at the new position
        items = self.scene().items(rect)

        # Filters: we keep only items that collide with the group
        # at the new position

        # (a) Filter out items from the current group
        items = [i for i in items
                if (not self.isAncestorOf(i) and i is not self)
                and isinstance(i, Symbol)]

        # (b) Filter out items that are in the rectangle but that do not
        #     actually collide with the current group
        items = [i for i in items if [j for j in i.collidingItems() if
            self.isAncestorOf(j) or j is self]]

        # (c) Filter out the potentially colliding items
        #     if they belong in the cam caller
        items = [i for i in items if not ignore or not
                i.commonAncestorItem(ignore)]

        # Get the top level item of each collider
        topLevelColliders = set()
        for item in items:
            while item.hasParent:
                item = item.parentItem() or item.parent
            topLevelColliders.add(item)

        # Determine how much we need to move the colliding groups and call
        # their CAM with this delta
        # Save colliders positions in case they are moved by a sub cam call
        colPos = {i: i.pos() for i in topLevelColliders}
        for col in topLevelColliders:
            colliderRect = (col.sceneBoundingRect() |
                    col.mapRectToScene(col.childrenBoundingRect()))
            if oldPos.y() + rect.height() <= colliderRect.y():
                # Collision from the top: move down the collider
                delta.setX(col.x())
                delta.setY(rect.y() + rect.height() + 10)
            elif oldPos.y() >= colliderRect.y() + colliderRect.height():
                # Collision from below: move up the collider
                delta.setX(col.x())
                delta.setY(rect.y() - colliderRect.height() - 10)
            elif oldPos.x() <= col.x():
                # Collision from the left: move right
                delta.setX(rect.x() + rect.width() + 10 +
                        col.x() - colliderRect.x())
                delta.setY(col.y())
            else:
                delta.setX(col.x() - colliderRect.x() -
                        colliderRect.width() - 10 + rect.x())
                delta.setY(col.y())
            if col.pos() == colPos[col]:
                col.cam(col.pos(), delta, ignore=self)


class Comment(Symbol):
    '''
        Class used to handle right connected comments
        TODO: move to sdlSymbols.pr
    '''
    allowed_followers = []

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Comment()
        coord_x, coord_y, width, height = ast.coordinates
        super(Comment, self).__init__(parent)
        # onTheRight determines if the comment symbol needs to be flipped
        self.onTheRight = True
        self.connection = None
        if parent:
            self.insertSymbol(parent, coord_x, coord_y)
        polygon = self.computePolygon(width, height)
        pen = QPen()
        # Set transparent color (drawing is done in the paint function)
        pen.setColor(QColor(0, 0, 0, 0))
        self.setPen(pen)
        self.setPolygon(polygon)
        self.text = EditableText(parent=self, text=ast.inputString,
                hyperlink=ast.hyperlink)
        self.commonName = 'end'
        self.parser = ogParser

    def __str__(self):
        return 'Comment'

    def insertSymbol(self, parent, x, y):
        ''' Align the symbol on the right of the parent '''
        if not parent:
            return
        parent.comment = self
        super(Comment, self).insertSymbol(parent, x, y)
        if x is not None:
            self.setX(x)
        else:
            self.setX(parent.boundingRect().width() + 20)
        if y is not None:
            self.setY(y)
        else:
            self.setY((parent.boundingRect().height() -
                self.boundingRect().height()) / 2)
        self.connection = self.connectToParent()
        if self.x() < parent.boundingRect().width() + 5:
            self.onTheRight = False
        parent.cam(parent.pos(), parent.pos())

    def deleteSymbol(self):
        '''
            Specific delete actions for Comment:
            reset comment field in parent
        '''
        self.parentItem().comment = None
        super(Comment, self).deleteSymbol()

    def resizeItem(self, rect):
        '''
            Redefinition of the Resize function
            (textSymbol only resize in one direction)
        '''
        self.prepareGeometryChange()
        polygon = self.computePolygon(rect.width(), rect.height())
        self.setPolygon(polygon)
        #for cnx in self.connections():
        #    cnx.update_lines()
        #if self.hasParent:
        #    for cnx in self.parent.connections():
        #        cnx.update_lines()

    def computePolygon(self, width, height):
        polygon = QPolygon(QRect(0, 0, width, height))
        return polygon

    def paint(self, painter, _, __):
        rect = self.boundingRect()
        pen = QPen()
        pen.setStyle(Qt.DashLine)
        pen.setColor(Qt.darkGray)
        painter.setPen(pen)
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        if self.onTheRight:
            painter.drawLines([QPoint(w, y), QPoint(x, y),
                               QPoint(x, y), QPoint(x, h),
                               QPoint(x, h), QPoint(w, h)])
        else:
            painter.drawLines([QPoint(x, y), QPoint(w, y),
                               QPoint(w, y), QPoint(w, h),
                               QPoint(w, h), QPoint(x, h)])
        # Call parent paint function to have the drawing of the selection box
        # (when item is selected it will draw a dashed line around it)
        super(Comment, self).paint(painter, _, __)

    def mouseMoveEvent(self, event):
        ''' Handle item move '''
        super(Comment, self).mouseMoveEvent(event)
        if self.mode == 'Move':
            new_y = self.pos().y() + (event.pos().y() - event.lastPos().y())
            new_x = self.pos().x() + (event.pos().x() - event.lastPos().x())
            if new_x < self.parentItem().boundingRect().width() + 5:
                self.onTheRight = False
            else:
                self.onTheRight = True
            self.setPos(new_x, new_y)

    def mouseReleaseEvent(self, event):
        '''
            Check if the new position is valid (no collision)
            undo otherwise
        '''
        moveAccepted = True
        for item in self.collidingItems():
            if not isinstance(item, (Connection, EditableText)):
                moveAccepted = False
        if not moveAccepted:
            self.setPos(self.coord)
        return super(Comment, self).mouseReleaseEvent(event)

    def updateConnectionPoints(self):
        '''
            Disable the update of connection points
            (comments do not influence them)
        '''
        pass

    def __repr__(self):
        ''' Return the text corresponding to the SDL PR notation '''
        return ('\n/* CIF COMMENT ({x}, {y}), ({w}, {h}) */\n'
                '{hlink}'
                'COMMENT \'{comment}\';'.format(hlink=repr(self.text),
                    x=int(self.x()), y=int(self.y()),
                    w=int(self.boundingRect().width()),
                    h=int(self.boundingRect().height()),
                    comment=str(self.text)))


class HorizontalSymbol(Symbol):
    '''
        Class used to handle horizontal symbols
        In case of SDL: INPUT, DECISION answers, Text Symbol, Start
    '''
    def __init__(self, polygon, parent=None, text='...',
            x=None, y=None, hyperlink=None):
        super(HorizontalSymbol, self).__init__(parent)
        self.setPolygon(polygon)
        self.minDistanceToSymbolAbove = 20
        if text:
            self.text = EditableText(parent=self, text=text,
                    hyperlink=hyperlink)
        if parent:
            self.insertSymbol(parent, x, y)
        else:
            self.setPos(x or 0, y or 0)

    def insertSymbol(self, parent, x, y):
        ''' Insert the symbol in the scene - Align below the parent '''
        if not parent:
            return
        super(HorizontalSymbol, self).insertSymbol(parent, x, y)
        if x is None or y is None:
            # Usually for first insertion when item is create:
            # compute position and (if relevant) move siblings
            siblings = [item for item in parent.childItems()
                    if item is not self and type(item) is type(self)]
            group = QGraphicsItemGroup(parent)
            map(group.addToGroup, siblings)
            groupW = group.boundingRect().width()
            self.scene().destroyItemGroup(group)
            for s in siblings:
                sX = s.x() - (self.boundingRect().width()) / 2 - 10
                sOldPos = s.pos()
                s.setX(sX)
                undoCmd = MoveSymbol(s, sOldPos, s.pos())
                self.scene().undo_stack.push(undoCmd)
            mostLeft = min([s.x() for s in siblings]) if siblings else 0
            if siblings:
                posX = mostLeft + groupW + 20
            else:
                # Verical alignment (x-axis):
                posX = (parent.boundingRect().width() -
                        self.boundingRect().width()) / 2
            posY = (parent.boundingRect().height() +
                    self.minDistanceToSymbolAbove)
            self.setPos(posX, posY)
        else:
            self.setPos(x, y)
        self.connection = self.connectToParent()
        self.updateConnectionPoints()
        self.cam(self.pos(), self.pos())

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow '''
        for s in self.childSymbols():
            if not isinstance(s, (HorizontalSymbol, Comment)):
                return s
        return None

    def mouseMoveEvent(self, event):
        ''' Prevent move from being above the parent '''
        if self.mode == 'Move':
            eventPos = event.pos()
            newY = self.pos().y() + (eventPos.y() - event.lastPos().y())
            newX = self.pos().x() + (eventPos.x() - event.lastPos().x())
            if self.hasParent:
                newY = max(newY, self.parent.boundingRect().height() +
                        self.minDistanceToSymbolAbove)
            self.setPos(newX, newY)
        super(HorizontalSymbol, self).mouseMoveEvent(event)

    def cam(self, oldPos, newPos, ignore=None):
        '''
            Collision avoidance manoeuvre for parallel branches
            (input, decision answers)
        '''
        if self.hasParent:
            # Rectangle of current group of item in scene coordinates
            lastCnx = None
            if hasattr(self, 'lastBranchItem'):
                # Disconnect the connection below the last item
                # (otherwise the rectangle will be too big)
                lastCnx = [c for c in self.lastBranchItem.childItems()
                        if isinstance(c, Connection) and not
                        isinstance(c.child, Comment)]
                if lastCnx:
                    lastCnx[0].setParentItem(None)
            rect = (self.sceneBoundingRect() |
                    self.mapRectToScene(self.childrenBoundingRect()))
            if lastCnx:
                lastCnx[0].setParentItem(self.lastBranchItem)
                lastCnx = None
            # Get all siblings (surrounding inputs/decision answers)
            siblings = (
                    i for i in self.parentItem().childItems()
                    if isinstance(i, HorizontalSymbol) and i is not self)
            for sibling in siblings:
                if hasattr(sibling, 'lastBranchItem'):
                    # Disconnect the connection below
                    # the last item of the sibling
                    lastCnx = [c for c in sibling.lastBranchItem.childItems()
                            if isinstance(c, Connection) and not
                            isinstance(c.child, Comment)]
                    if lastCnx:
                        lastCnx[0].setParentItem(None)
                sibRect = (sibling.sceneBoundingRect() |
                        sibling.mapRectToScene(sibling.childrenBoundingRect()))
                if lastCnx:
                    # Enable back the last connection
                    lastCnx[0].setParentItem(sibling.lastBranchItem)
                if rect.intersects(sibRect):
                    width = (sibRect & rect).width() + 10
                    oldSibPos = sibling.pos()
                    sibling.moveBy(width if self.x() <= sibling.x()
                            else -width, 0)
                    undoCmd = MoveSymbol(sibling, oldSibPos, sibling.pos())
                    self.scene().undo_stack.push(undoCmd)
                    sibling.cam(sibling.pos(), sibling.pos())
        super(HorizontalSymbol, self).cam(oldPos, newPos, ignore)
        # Recursively call the cam of the parent
        if self.hasParent:
            self.parentItem().cam(self.parentItem().pos(),
                    self.parentItem().pos())


class VerticalSymbol(Symbol):
    '''
        Class used to handle vertically-aligned symbols
        In case of SDL: STATE, OUTPUT, PROCEDURE, DECISION, TASK
    '''
    def __init__(self, polygon, parent=None, text='...',
            y=None, hyperlink=None):
        super(VerticalSymbol, self).__init__(parent)
        self.setPolygon(polygon)
        self.text = EditableText(parent=self, text=text, hyperlink=hyperlink)
        self.minDistanceToSymbolAbove = 15
        if parent:
            self.insertSymbol(parent=parent, x=None, y=y)

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow '''
        for s in self.childSymbols():
            if isinstance(s, VerticalSymbol):
                return s
        return None

    def insertSymbol(self, parent, x, y):
        '''
            Place the symbol in the scene.
            Determine the coordinates based on the position
            and size of the parent item, and make proper connections
        '''
        if not parent:
            # Place standalone item on the scene at given coordinates
            # (e.g. floating state)
            if x is not None and y is not None:
                self.setPos(x, y)
            return
        super(VerticalSymbol, self).insertSymbol(parent, x, y)
        # in a branch (e.g. DECISION) all items must know the first element
        # (used for computing the branch size and the connection point)
        self.branchEntryPoint = parent.branchEntryPoint
        # If inserting an symbol at the end of a branch (e.g. DECISION),
        # inform the branch entry point
        for child in parent.childItems():
            if isinstance(child, Connection) and child.childIsAConnectionPoint:
                self.branchEntryPoint.lastBranchItem = self
        # Check if parent has a connection point (e.g. DECISION)
        if hasattr(parent, 'connectionPoint'):
            # Move the new symbol below the connection point:
            # First, check if the parent was the last item of another branch
            for child in parent.childItems():
                if child not in (self, parent.text) and not isinstance(
                        child, HorizontalSymbol):
                    # Insertion: change parent and position of previous child:
                    if (isinstance(child, Connection) and
                            isinstance(child.child, Comment) or
                            isinstance(child, Comment)):
                        continue
                    if not isinstance(child, Connection) or not isinstance(
                            child.child, HorizontalSymbol):
                        child.setParentItem(self)
                        child.parent = self
                        if isinstance(child, Symbol):
                            childYDiff = (
                                    child.y() -
                                    self.parentItem().connectionPoint.y() +
                                    self.boundingRect().height() +
                                    self.minDistanceToSymbolAbove)
                            child.setY(childYDiff)
                            if not isinstance(child, Comment):
                                child.updatePosition()
        else:
            # If parent already had children,
            # change their parent to the inserted symbol
            for child in parent.childItems():
                if child not in (self, parent.text, parent.comment):
                    if (isinstance(child, Connection) and
                            isinstance(child.child, Comment)):
                        # Don't change the parent of a comment
                        continue
                    child.parent = self
                    child.setParentItem(self)
                    # move child position down when inserting
                    if isinstance(child, Symbol):
                        child.setY(0)
                        child.updatePosition()
        # Create the connection with the parent symbol
        self.connection = self.connectToParent()
        self.updatePosition()
        self.updateConnectionPoints()
        if y is not None:
            self.setY(y)
        #else:
        #    self.updatePosition()
        self.cam(self.pos(), self.pos())

    def updatePosition(self):
        '''
            Update the symbol position -
            always below its parent (check collisions, etc.)
        '''
        y = self.pos().y()
        # 'or self.parent' because of pyside/qt bug
        parent = self.parentItem() or self.parent
        x = (self.boundingRect().width() -
             parent.boundingRect().width()) / 2
        # In case of collision with parent item, move down
        for item in self.collidingItems():
            if hasattr(self.parentItem(), 'connectionPoint'):
                y = max(self.y(), parent.connectionPoint.y())
            else:
                y = max(self.y(),
                        parent.boundingRect().height() + 15)
        self.setPos(-x, y)

    def mouseMoveEvent(self, event):
        ''' Click and move: forbid symbol to move on the x axis '''
        if self.mode == 'Move':
            newY = self.pos().y() + (event.pos().y() - event.lastPos().y())
            if not self.parent:
                self.setX(self.pos().x() +
                        (event.pos().x() - event.lastPos().x()))
            if not self.hasParent or (newY >= self.connection.startPoint.y() +
                    self.parent.minDistanceToSymbolAbove):
                self.setY(newY)
        super(VerticalSymbol, self).mouseMoveEvent(event)

    def cam(self, oldPos, newPos, ignore=None):
        ''' Collision avoidance manoeuvre for vertical symbols '''
        if self.hasParent:
            branchEntry = self
            while branchEntry.hasParent and isinstance(
                    branchEntry, VerticalSymbol):
                # See cam of symbol for explanation about
                # the 'or branchEntry.parent' (pyside/qt bug)
                branchEntry = branchEntry.parentItem() or branchEntry.parent
            branchEntry.cam(branchEntry.pos(), branchEntry.pos())
        else:
            super(VerticalSymbol, self).cam(oldPos, newPos)

    def paint(self, painter, _, __):
        '''
            Make sure symbol is V-aligned below its parent
            and that it is not colliding with it
        '''
        if self.hasParent:
            self.updatePosition()
        super(VerticalSymbol, self).paint(painter, _, __)
