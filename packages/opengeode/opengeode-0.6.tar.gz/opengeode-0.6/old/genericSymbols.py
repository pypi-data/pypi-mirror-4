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
import logging

from PySide.QtCore import(Qt, QPoint, QPointF, QRect, Slot, QRegExp, QFile)

from PySide.QtGui import(QGraphicsTextItem, QGraphicsPathItem,
        QGraphicsPolygonItem, QPainterPath, QGraphicsItem,
        QCompleter, QGraphicsProxyWidget, QListWidget,
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

LOG = logging.getLogger(__name__)


class Completer(QGraphicsProxyWidget):
    ''' Class for handling text autocompletion in the SDL scene '''
    def __init__(self, parent):
        ''' Create an autocompletion list popup '''
        widget = QListWidget()
        super(Completer, self).__init__(parent)
        self.setWidget(widget)
        self._completer = QCompleter(parent.parentItem().completion_list)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.parent = parent
        # For some reason the default minimum size is (61,61)
        # Set it to 0 so that the size of the box is not taken
        # into account when it is hidden.
        self.setMinimumSize(0, 0)

    def set_completion_prefix(self, completion_prefix):
        '''
        Set the current completion prefix (user-entered text)
        and set the corresponding list of words in the popup widget
        '''
        self._completer.setCompletionPrefix(completion_prefix)
        self.widget().clear()
        for i in xrange(self._completer.completionCount()):
            self._completer.setCurrentRow(i)
            self.widget().addItem(self._completer.currentCompletion())
        self.resize(self.widget().sizeHintForColumn(0) + 40, 70)
        return self._completer.completionCount()

    def keyPressEvent(self, e):
        super(Completer, self).keyPressEvent(e)
        if e.key() == Qt.Key_Escape:
            self.parent.setFocus()

    def focusOutEvent(self, event):
        ''' When the user leaves the popup, return focus to parent '''
        super(Completer, self).focusOutEvent(event)
        self.hide()
        self.parent.setFocus()


class Highlighter(QSyntaxHighlighter):
    ''' Class for handling syntax highlighting in editable text '''
    def __init__(self, parent=None):
        ''' Define highlighting rules '''
        super(Highlighter, self).__init__(parent)
        self.highlighting_rules = []

        # Black bold items (allowed keywords)
        black_bold_format = QTextCharFormat()
        black_bold_format.setFontWeight(QFont.Bold)
        black_bold_patterns = ('\\b{word}\\b'.format(word=word) for word in (
                'DCL', 'CALL', 'ELSE', 'IF', 'THEN', 'MANTISSA', 'BASE',
                'EXPONENT', 'TRUE', 'FALSE', 'MOD', 'FI', 'WRITE', 'WRITELN',
                'LENGTH', 'PRESENT'))
        self.highlighting_rules = [(QRegExp(pattern, cs=Qt.CaseInsensitive),
            black_bold_format) for pattern in black_bold_patterns]

        # Red bold items (reserved keywords)
        red_bold_format = QTextCharFormat()
        red_bold_format.setFontWeight(QFont.Bold)
        red_bold_format.setForeground(Qt.red)
        red_bold_patterns = ('\\b{word}\\b'.format(word=word) for word in (
                'INPUT', 'OUTPUT', 'STATE', 'DECISION', 'NEXTSTATE',
                'TASK', 'TIMER', 'PROCESS', 'PROCEDURE', 'LABEL', 'JOIN'))
        for p in red_bold_patterns:
            self.highlighting_rules.append(
                    (QRegExp(p, cs=Qt.CaseInsensitive), red_bold_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(Qt.darkBlue)
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((QRegExp('--[^\n]*'), comment_format))

    def highlightBlock(self, text):
        ''' Redefined function to apply the highlighting rules '''
        for expression, formatter in self.highlighting_rules:
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
    default_cursor = Qt.IBeamCursor
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
        # Increase the Z value of the text area so that the autocompleter
        # always appear on top of text's siblings (parents's followers)
        self.setZValue(1)
        # Set cursor when mouse goes over the text
        self.setCursor(self.default_cursor)

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
        parent_rect = self.parentItem().boundingRect()
        rect = self.boundingRect()
        # Use parent symbol alignment requirement
        # Can be extended to support more combinations..
        alignment = self.parentItem().textbox_alignment
        if alignment & Qt.AlignCenter:
            self.setPos(parent_rect.center() - rect.center())
        elif (alignment & Qt.AlignTop) and (alignment & Qt.AlignLeft):
            self.setPos(0, 0)

    def paint(self, painter, _, __):
        ''' Place the textbox in the parent symbol and draw it '''
        self.set_textbox_position()
        super(EditableText, self).paint(painter, _, __)

    def try_resize(self):
        '''
            If needed, request a resizing of the parent item
            (when text size expands)
        '''
        if self.parentItem().auto_expand:
            parent_rect = self.parentItem().boundingRect()
            rect = self.boundingRect()
            if rect.width() + 30 > parent_rect.width():
                parent_rect.setWidth(rect.width() + 30)
            parent_rect.setHeight(max(rect.height(), parent_rect.height()))
            self.parentItem().resizeItem(parent_rect)

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
                pos_x = relative_x + layout_pos.x()
                pos_y = rect.y() + rect.height() + layout_pos.y()

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
                undo_cmd = ResizeSymbol(self.parentItem(), self.oldSize,
                        self.parentItem().boundingRect())
                self.scene().undo_stack.push(undo_cmd)
                self.parentItem().cam(self.parentItem().pos(),
                        self.parentItem().pos())
            if self.oldText != str(self):
                undo_cmd = ReplaceText(self, self.oldText, str(self))
                self.scene().undo_stack.push(undo_cmd)
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
        if not self.editing:
            self.scene().undo_stack.beginMacro('Edit text')
            self.oldText = str(self)
            self.oldSize = self.parentItem().boundingRect()
            self.editing = True

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
    default_cursor = Qt.ArrowCursor

    def __init__(self, parent, child, connectionPoint=False):
        super(Connection, self).__init__(parent)
        self.parent = parent
        self.child = child
        self.childIsAConnectionPoint = connectionPoint
        self.start_point = QPointF(0, 0)
        self.end_point = QPointF(0, 0)
        #self.reshape()
        pen = QPen()
        pen.setColor(Qt.blue)
        pen.setCosmetic(False)
        self.setPen(pen)
        self.parent_rect = parent.sceneBoundingRect()
        self.childRect = child.sceneBoundingRect()

    def __str__(self):
        ''' Print connection information for debug purpose'''
        return 'Connection: parent = {p}, child = {c}'.format(
                p=str(self.parentItem()), c=str(self.child))

    def reshape(self):
        ''' Update the connection or arrow shape '''
        new_shape = QPainterPath()
        if(self.parentItem().terminal_symbol
                and self.childIsAConnectionPoint):
            self.setPath(new_shape)
            return new_shape
        new_shape = QPainterPath()
        parent_rect = self.parentItem().boundingRect()
        # Define connection start point
        if hasattr(self.parentItem(), 'connectionPoint') and not isinstance(
                self.child, (HorizontalSymbol, Comment)):
            self.start_point = self.parentItem().connectionPoint
        elif isinstance(self.child, Comment):
            self.start_point = QPointF(
                    parent_rect.width(), parent_rect.height() / 2)
        else:
            self.start_point = QPointF(
                    parent_rect.width() / 2, parent_rect.height())
        # Defined connection end point
        if self.childIsAConnectionPoint:
            connection_point_scene = self.child.mapToScene(
                    self.child.connectionPoint)
            connection_point_local = self.parentItem().mapFromScene(
                    connection_point_scene)
            self.end_point = connection_point_local
        elif isinstance(self.child, Comment):
            if self.child.on_the_right:
                self.end_point = QPointF(self.child.x(),
                        self.child.y() +
                        self.child.boundingRect().height() / 2)
            else:
                self.end_point = QPointF(self.child.x() +
                        self.child.boundingRect().width(),
                        self.child.y() +
                        self.child.boundingRect().height() / 2)
        else:
            self.end_point = QPointF()
            #self.end_point.setY(self.child.pos().y())
            # FIXME - why is the pos of the child above the connection point when loading?!
            self.end_point.setY(max(self.child.pos().y(), self.start_point.y()))
            #print self.child.pos(), self.start_point, self.end_point
        # Move to start point and draw the connection
        new_shape.moveTo(self.start_point)
        if not self.childIsAConnectionPoint and not isinstance(
                self.child, Comment):
            if isinstance(self.child, HorizontalSymbol):
                self.end_point.setX(self.child.pos().x() +
                        self.child.boundingRect().width() / 2)
                new_shape.lineTo(self.start_point.x(), self.start_point.y() + 10)
                new_shape.lineTo(self.end_point.x(), self.start_point.y() + 10)
            else:
                self.end_point.setX(self.start_point.x())
        elif isinstance(self.child, Comment):
            # Make sure the connection does not overlap the comment item
            if (self.child.on_the_right or
                    (not self.child.on_the_right and
                        self.child.x() + self.child.boundingRect().width()
                        < self.parentItem().boundingRect().width())):
                goToPoint = self.start_point.x() + 5
            else:
                goToPoint = self.end_point.x() + 5
            new_shape.lineTo(goToPoint, self.start_point.y())
            new_shape.lineTo(goToPoint, self.end_point.y())
            new_shape.lineTo(self.end_point.x(), self.end_point.y())
        else:
            new_shape.lineTo(self.start_point.x(), self.end_point.y() - 10)
            new_shape.lineTo(self.end_point.x(), self.end_point.y() - 10)
        new_shape.lineTo(self.end_point)
        # If required draw an arrow head (e.g. in SDL NEXTSTATE and JOIN)
        if self.child.arrow_head:
            new_shape.lineTo(self.end_point.x() - 5, self.end_point.y() - 5)
            new_shape.moveTo(self.end_point)
            new_shape.lineTo(self.end_point.x() + 5, self.end_point.y() - 5)
        self.setPath(new_shape)
        #if self.child.arrow_head:
        #    print self.child, self.parent
        #    print new_shape
        return new_shape

class Symbol(QGraphicsPolygonItem):
    ''' Top-level class used to handle all SDL symbols '''
    # Symbols of a given type share a text-autocompletion list:
    completion_list = []
    # Symbols of a given type can be graphically followed to:
    allowed_followers = []
    # By default symbol size may expand when inner text exceeds border
    auto_expand = True
    # By default connections between symbols are lines, not arrows
    arrow_head = False
    # Default mouse cursor
    default_cursor = Qt.ArrowCursor

    def __init__(self, parent=None):
        '''
            Create top level symbol and propagate important properties
            from parent items
        '''
        super(Symbol, self).__init__()
        self.mode = ''
        self.text = None
        self.comment = None
        self.hyperlink_dialog = None
        self.hlink_field = None
        self.loadHyperlinkDialog()
        # hasParent compensates a Qt (or PySide) bug when calling parentItem()
        # on top-level items
        self.hasParent = False
        self.parent = None
        # Common name is the name of the symbol as used in a parser or backend
        self.common_name = ''
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

    @property
    def terminal_symbol(self):
        ''' Way to determine if a symbol is terminal (useful for branches) '''
        return self._terminal_symbol

    @terminal_symbol.setter
    def terminal_symbol(self, value):
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
            self.common_name, repr(self))
        return ast, terminators

    def checkSyntax(self):
        ''' Check the syntax of the text inside the symbol (if any) '''
        if not self.parser or not hasattr(self.parser, 'parseSingleElement'):
            print('[ERROR] No parser found')
            return
        _, syntax_errors, __, ___, ____ = self.parser.parseSingleElement(
                self.common_name, repr(self))
        try:
            self.scene().raise_syntax_errors(syntax_errors)
        except:
            print('[SYNTAX ERROR] ' + '\n'.join(syntax_errors))

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
        entrypoint_parent = None
        if self.branchEntryPoint:
            # If the item is the last in a branch, make clean connections
            bep = self.branchEntryPoint
            entrypoint_parent = bep.parentItem()
            if bep.lastBranchItem is self:
                # Last item of a branch, remove or reconnect the link
                # to the connection point
                for child in self.childItems():
                    # Find the connection point below
                    if(isinstance(child, Connection) and
                            child.childIsAConnectionPoint):
                        connection_below = child
                        break
                if bep is not self:
                    # Item is not the branch entry point itself
                    bep.lastBranchItem = self.parentItem()
                    connection_below.setParentItem(self.parentItem())
                    self.parentItem().connectionBelow = connection_below
                else:
                    # delete the link to the connection point
                    connection_below.setParentItem(None)
                    self.scene().removeItem(connection_below)
        child_below = self.nextAlignedSymbol()
        if(child_below and self.hasParent and
                self.parentItem().nextAlignedSymbol() is self):
            # Delete the connection to the child below if
            # it is not a full branch to be deleted
            child_below.connection.setParentItem(None)
            self.scene().removeItem(child_below.connection)
        if self.hasParent:
            if (not child_below or not self.parentItem().nextAlignedSymbol() or
                        self.branchEntryPoint is self):
                # If nothing below or item is branch entry point,
                # remove the connection with the parent
                self.connection.setParentItem(None)
                self.scene().removeItem(self.connection)
            else:
                # Otherwise connect the item below with the parent
                child_below.connection = self.connection
                self.connection.child = child_below
                child_below.parent = self.parentItem()
                child_below.setParentItem(child_below.parent)
                # Update position of child - take place of deleted item
                child_below.setY(self.y())
            self.setParentItem(None)
        self.scene().removeItem(self)
        try:
            entrypoint_parent.updateConnectionPointPosition()
            entrypoint_parent.updateConnectionPoints()
        except AttributeError:
            pass

    def connectToParent(self):
        ''' Add a connection (wire) with the parent item '''
        return Connection(self.parent, self)

    def connection_to_parent(self):
        ''' Return the connection above the symbol '''
        try:
            connection, = [cnx for cnx in self.parent.connections()
                    if cnx.child == self]
            return connection
        except ValueError:
            return None

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow - implemented in subclasses '''
        return None

    def connections(self):
        ''' Return all child connections of this symbol '''
        return (c for c in self.childItems() if isinstance(c, Connection))

    def loadHyperlinkDialog(self):
        ''' Load dialog from ui file for defining hyperlink '''
        loader = QUiLoader()
        ui_file = QFile(':/hyperlink.ui')  # UI_DIALOG_FILE)
        ui_file.open(QFile.ReadOnly)
        self.hyperlink_dialog = loader.load(ui_file)
        ui_file.close()
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
        png_action = 'Export branch to PNG'
        hl_action = 'Hyperlink'
        my_menu = QMenu(png_action)
        if not hasattr(self, '_no_hyperlink'):
            my_menu.addAction(hl_action)
        my_menu.addAction(png_action)
        action = my_menu.exec_(event.screenPos())
        if action:
            if action.text() == png_action:
                # Save a PNG of the selected symbol and all its children
                filename = QFileDialog.getSaveFileName(self.window(),
                        'Export picture', '.', 'Picture (*.png)')[0]
                if not filename:
                    return
                if filename.split('.')[-1] != 'png':
                    filename += '.png'
                old_brush = self.scene().backgroundBrush()
                self.scene().setBackgroundBrush(QBrush())
                complete_rect = (self.childrenBoundingRect() |
                                self.boundingRect())
                # Add some margin for the antialiasing (5 pixels on each side)
                complete_rect.adjust(-5, -5, 5, 5)
                rect = self.mapRectToScene(complete_rect)
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
                self.scene().setBackgroundBrush(old_brush)
            elif action.text() == hl_action:
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
        self.update_connections()

    def update_connections(self):
        '''
           When symbol moves or is resized, update the shape of all
           its connections - can be redefined in subclasses
        '''
        for cnx in self.connections():
            cnx.reshape()
        try:
            self.connection_to_parent().reshape()
        except AttributeError:
            pass
        try:
            self.branchEntryPoint.parent.update_connections()
        except AttributeError:
            pass 

    def computePolygon(self, width, height):
        ''' VIRTUAL - to be implemented per symbol in subclasses '''
        pass

    def mousePressEvent(self, event):
        '''
            Handle resizing and moving of items when grabbing
            the lower right corner
        '''
        # super(Symbol, self).mousePressEvent(event)
        # Save current position to be able to revert move
        self.coord = self.pos()
        event_pos = event.pos()
        rect = self.boundingRect()
        self.height = rect.height()
        if(event_pos.x() > rect.width() - 10 and
                event_pos.y() > rect.height() - 10):
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
            try:
                new_y = max(event.pos().y(),
                        self.text.boundingRect().height() + 10)
                new_x = max(event.pos().x(),
                           self.text.boundingRect().width() + 30)
            except AttributeError:
                new_y = max(event.pos().y(), 15)
                new_x = max(event.pos().x(), 30)
            self.resizeItem(QRect(0, 0, new_x, new_y))

    def mouseReleaseEvent(self, event):
        ''' Default action when mouse is released: reset mode '''
        if self.mode == 'Resize':
            self.scene().undo_stack.beginMacro('Resize symbol')
            undo_cmd = ResizeSymbol(self, self.oldRect, self.boundingRect())
            self.scene().undo_stack.push(undo_cmd)
            self.cam(self.coord, self.pos())
            self.updateConnectionPoints()
            self.scene().undo_stack.endMacro()
        elif self.mode == 'Move' and self.coord != self.pos():
            self.scene().undo_stack.beginMacro('Move symbol')
            undo_cmd = MoveSymbol(self, self.coord, self.pos())
            self.scene().undo_stack.push(undo_cmd)
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

    def cam(self, old_pos, new_pos, ignore=None):
        ''' Collision Avoidance Manoeuvre for top level symbols '''
        if not self.scene():
            # Make sure the item is in a scene. For instance, when loading
            # a model from a file, some items may be connected together
            # and CAM called *before* the top-level item has been inserted.
            return
        if self.hasParent:
            # Exectute CAM on top level of this item
            top_level = self
            while top_level.hasParent:
                # The "or top_level.parent" below is due to a Pyside/Qt bug
                # of the parentItem() function. It can happen that even when
                # the parent has explicitely been set with "setParentItem",
                # a subsequent call to parentItem returns None. Seems to happen
                # if the parent has not been added yet to the scene.
                top_level = top_level.parentItem() or top_level.parent
            top_level.cam(top_level.pos(), top_level.pos())
            return

        # In case CAM is called due to object move, go to the new position
        delta = new_pos - old_pos

        # Rectangle of current group of item in scene coordinates
        rect = (self.sceneBoundingRect() |
                self.mapRectToScene(self.childrenBoundingRect()))

        # Move the rectangle to the new position, and move the current item
        if self.pos() != new_pos:
            rect.adjust(delta.x(), delta.y(), delta.x(), delta.y())
            self.setPos(new_pos)
            undo_cmd = MoveSymbol(self, old_pos, new_pos)
            self.scene().undo_stack.push(undo_cmd)

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
        top_level_colliders = set()
        for item in items:
            while item.hasParent:
                item = item.parentItem() or item.parent
            top_level_colliders.add(item)

        # Determine how much we need to move the colliding groups and call
        # their CAM with this delta
        # Save colliders positions in case they are moved by a sub cam call
        col_pos = {i: i.pos() for i in top_level_colliders}
        for col in top_level_colliders:
            collider_rect = (col.sceneBoundingRect() |
                    col.mapRectToScene(col.childrenBoundingRect()))
            if old_pos.y() + rect.height() <= collider_rect.y():
                # Collision from the top: move down the collider
                delta.setX(col.x())
                delta.setY(rect.y() + rect.height() + 10)
            elif old_pos.y() >= collider_rect.y() + collider_rect.height():
                # Collision from below: move up the collider
                delta.setX(col.x())
                delta.setY(rect.y() - collider_rect.height() - 10)
            elif old_pos.x() <= col.x():
                # Collision from the left: move right
                delta.setX(rect.x() + rect.width() + 10 +
                        col.x() - collider_rect.x())
                delta.setY(col.y())
            else:
                delta.setX(col.x() - collider_rect.x() -
                        collider_rect.width() - 10 + rect.x())
                delta.setY(col.y())
            if col.pos() == col_pos[col]:
                col.cam(col.pos(), delta, ignore=self)
        self.update_connections()


class Comment(Symbol):
    '''
        Class used to handle right connected comments
    '''
    allowed_followers = []

    def __init__(self, parent=None, ast=None):
        ast = ast or ogAST.Comment()
        super(Comment, self).__init__(parent)
        self.connection = None
        if parent:
            self.insertSymbol(parent, ast.pos_x, ast.pos_y)
        polygon = self.computePolygon(ast.width, ast.height)
        pen = QPen()
        # Set transparent color (drawing is done in the paint function)
        pen.setColor(QColor(0, 0, 0, 0))
        self.setPen(pen)
        self.setPolygon(polygon)
        self.text = EditableText(parent=self, text=ast.inputString,
                hyperlink=ast.hyperlink)
        self.common_name = 'end'
        self.parser = ogParser

    def __str__(self):
        return 'Comment'

    @property
    def on_the_right(self):
        ''' Determine if the comment symbol needs to be flipped '''
        return self.x() > self.parent.boundingRect().width() + 5

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
            (Comment symbol only resizes in one direction)
        '''
        self.prepareGeometryChange()
        polygon = self.computePolygon(rect.width(), rect.height())
        self.setPolygon(polygon)
        self.update_connections()

    def computePolygon(self, width, height):
        ''' Set a box - actual shape is computed in the paint function '''
        polygon = QPolygon(QRect(0, 0, width, height))
        return polygon

    def paint(self, painter, _, __):
        ''' Draw the comment symbol '''
        rect = self.boundingRect()
        pen = QPen()
        pen.setStyle(Qt.DashLine)
        pen.setColor(Qt.darkGray)
        painter.setPen(pen)
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        if self.on_the_right:
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
            self.setPos(new_x, new_y)
            self.update_connections()

    def mouseReleaseEvent(self, event):
        '''
            Check if the new position is valid (no collision)
            undo otherwise
        '''
        move_accepted = True
        for item in self.collidingItems():
            if not isinstance(item, (Connection, EditableText)):
                move_accepted = False
        if not move_accepted:
            self.setPos(self.coord)
            self.update_connections()
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
        self.connection = None
        if text:
            self.text = EditableText(parent=self, text=text,
                    hyperlink=hyperlink)
        if parent:
            self.insertSymbol(parent, x, y)
        else:
            self.setPos(x or 0, y or 0)

    def insertSymbol(self, parent, pos_x, pos_y):
        ''' Insert the symbol in the scene - Align below the parent '''
        if not parent:
            self.setPos(pos_x, pos_y)
            return
        super(HorizontalSymbol, self).insertSymbol(parent, pos_x, pos_y)
        if pos_x is None or pos_y is None:
            # Usually for first insertion when item is created:
            # compute position and (if relevant) move siblings
            first, last = None, None
            #siblings = [item for item in parent.childItems()
            #        if item is not self and type(item) is type(self)]
            has_siblings = False
            for sibling in self.siblings():
                has_siblings = True
                first = min(first, sibling.x()) if(
                        first is not None) else sibling.x()
                last = max(last, sibling.x() +
                        sibling.boundingRect().width()) if(
                                last is not None) else(sibling.x() +
                                        sibling.boundingRect().width())
            group_width = last - first if first is not None else 0
            for sibling in self.siblings():
                sib_x = sibling.x() - (self.boundingRect().width()) / 2 - 10
                sib_oldpos = sibling.pos()
                sibling.setX(sib_x)
                undo_cmd = MoveSymbol(sibling, sib_oldpos, sibling.pos())
                self.scene().undo_stack.push(undo_cmd)
            most_left = min([sibling.x()
                for sibling in self.siblings()] or [0])
            if has_siblings:
                pos_x = most_left + group_width + 20
            else:
                # Verical alignment (x-axis):
                pos_x = (parent.boundingRect().width() -
                        self.boundingRect().width()) / 2
            pos_y = (parent.boundingRect().height() +
                    self.minDistanceToSymbolAbove)
        self.setPos(pos_x, pos_y)
        self.connection = self.connectToParent()
        self.updateConnectionPoints()
        self.cam(self.pos(), self.pos())
    
    def update_connections(self):
        '''
           Redefined from Symbol class
           Horizontal symbols may have siblings - check their shape.
        '''
        super(HorizontalSymbol, self).update_connections()
        try:
            for sibling in self.siblings():
                for cnx in sibling.lastBranchItem.connections():
                    cnx.reshape()
        except AttributeError:
            pass

    def siblings(self):
        ''' Return all the items's sibling symbols '''
        try:
            return (item for item in self.parent.childItems()
                    if item is not self and type(item) is type(self))
        except:
            return ()

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow '''
        for symbol in self.childSymbols():
            if not isinstance(symbol, (HorizontalSymbol, Comment)):
                return symbol
        return None

    def mouseMoveEvent(self, event):
        ''' Prevent move from being above the parent '''
        if self.mode == 'Move':
            event_pos = event.pos()
            new_y = self.pos().y() + (event_pos.y() - event.lastPos().y())
            new_x = self.pos().x() + (event_pos.x() - event.lastPos().x())
            if self.hasParent:
                new_y = max(new_y, self.parent.boundingRect().height() +
                        self.minDistanceToSymbolAbove)
            self.setPos(new_x, new_y)
            self.update_connections()
        super(HorizontalSymbol, self).mouseMoveEvent(event)

    def cam(self, old_pos, new_pos, ignore=None):
        '''
            Collision avoidance manoeuvre for parallel branches
            (for SDL: input, decision answers)
        '''
        if self.hasParent:
            # Rectangle of current group of item in scene coordinates
            try:
                # Disconnect the connection below the last item
                # (otherwise the rectangle will be too big)
                last_cnx, = (cnx for cnx in self.lastBranchItem.connections()
                        if cnx.child == self.parentItem())
                last_cnx.setParentItem(None)
            except:
                last_cnx = None
            rect = (self.sceneBoundingRect() |
                    self.mapRectToScene(self.childrenBoundingRect()))
            try:
                # Set back the last connection
                last_cnx.setParentItem(self.lastBranchItem)
            except:
                pass
            # Get all siblings (e.g. surrounding inputs/decision answers)
            siblings = (i for i in self.parentItem().childItems() if
                    isinstance(i, HorizontalSymbol) and i is not self)
            for sibling in siblings:
                try:
                    # Disconnect the connection below the last item
                    last_cnx, = (cnx for cnx in
                            sibling.lastBranchItem.connections()
                            if cnx.child == self.parentItem())
                    last_cnx.setParentItem(None)
                except:
                    last_cnx = None
                sib_rect = (sibling.sceneBoundingRect() |
                        sibling.mapRectToScene(sibling.childrenBoundingRect()))
                try:
                    # Set back the last connection
                    last_cnx.setParentItem(sibling.lastBranchItem)
                except:
                    pass
                if rect.intersects(sib_rect):
                    width = (sib_rect & rect).width() + 10
                    old_sib_pos = sibling.pos()
                    sibling.moveBy(width if self.x() <= sibling.x()
                            else -width, 0)
                    undo_cmd = MoveSymbol(sibling, old_sib_pos, sibling.pos())
                    self.scene().undo_stack.push(undo_cmd)
                    sibling.cam(sibling.pos(), sibling.pos())
        super(HorizontalSymbol, self).cam(old_pos, new_pos, ignore)
        # Recursively call the cam of the parent
        if self.hasParent:
            self.parentItem().cam(self.parentItem().pos(),
                    self.parentItem().pos())
        self.update_connections()


class VerticalSymbol(Symbol):
    '''
        Class used to handle vertically-aligned symbols
        In case of SDL: STATE, OUTPUT, PROCEDURE, DECISION, TASK
    '''
    def __init__(self, polygon, parent=None, text='...',
            y=None, hyperlink=None):
        super(VerticalSymbol, self).__init__(parent)
        self.connection = None
        self.setPolygon(polygon)
        self.text = EditableText(parent=self, text=text, hyperlink=hyperlink)
        self.minDistanceToSymbolAbove = 15
        if parent:
            self.insertSymbol(parent=parent, x=None, y=y)

    def nextAlignedSymbol(self):
        ''' Return the next symbol in the flow '''
        for symbol in self.childSymbols():
            if isinstance(symbol, VerticalSymbol):
                return symbol
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
                            child_y_diff = (
                                    child.y() -
                                    self.parentItem().connectionPoint.y() +
                                    self.boundingRect().height() +
                                    self.minDistanceToSymbolAbove)
                            child.setY(child_y_diff)
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
        pos_y = self.pos().y()
        # 'or self.parent' because of pyside/qt bug
        parent = self.parentItem() or self.parent
        pos_x = (self.boundingRect().width() -
             parent.boundingRect().width()) / 2
        # In case of collision with parent item, move down
        try:
            pos_y = max(self.y(), parent.connectionPoint.y())
        except AttributeError:
            pos_y = max(self.y(), parent.boundingRect().height() + 15)
        self.setPos(-pos_x, pos_y)

    def mouseMoveEvent(self, event):
        ''' Click and move: forbid symbol to move on the x axis '''
        super(VerticalSymbol, self).mouseMoveEvent(event)
        if self.mode == 'Move':
            new_y = self.pos().y() + (event.pos().y() - event.lastPos().y())
            if not self.parent:
                self.setX(self.pos().x() +
                        (event.pos().x() - event.lastPos().x()))
            if not self.hasParent or (new_y >=
                    self.connection.start_point.y() +
                    self.parent.minDistanceToSymbolAbove):
                self.setY(new_y)
            self.update_connections()
            self.updateConnectionPoints()

    def cam(self, old_pos, new_pos, ignore=None):
        ''' Collision avoidance manoeuvre for vertical symbols '''
        if self.hasParent:
            branch_entry = self
            while branch_entry.hasParent and isinstance(
                    branch_entry, VerticalSymbol):
                # See cam of symbol for explanation about
                # the 'or branch_entry.parent' (pyside/qt bug)
                branch_entry = branch_entry.parentItem() or branch_entry.parent
            branch_entry.cam(branch_entry.pos(), branch_entry.pos())
        else:
            super(VerticalSymbol, self).cam(old_pos, new_pos)

    def paint(self, painter, _, __):
        '''
            Make sure symbol is V-aligned below its parent
            and that it is not colliding with it
        '''
        if self.hasParent:
            self.updatePosition()
        super(VerticalSymbol, self).paint(painter, _, __)
