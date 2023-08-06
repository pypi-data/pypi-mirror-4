#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    OpenGEODE - A tiny SDL Editor for TASTE

    Undo/Redo commands for generic symbols when used in a diagram editor.

    Note when creating a new command:
        the redo() function is *called* when the command is created.
        No need to perform the action before.

    Copyright (c) 2012 European Space Agency

    Designed and implemented by Maxime Perrotin

    Contact: maxime.perrotin@esa.int
"""


from PySide.QtGui import QUndoCommand


class ReplaceText(QUndoCommand):
    ''' Undo/Redo command for updating the text in a symbol '''
    def __init__(self, text_id, old_text, new_text):
        super(ReplaceText, self).__init__()
        self.setText('Replace text')
        self.text = text_id
        self.old_text = old_text
        self.new_text = new_text

    def undo(self):
        self.text.setPlainText(self.old_text)

    def redo(self):
        self.text.setPlainText(self.new_text)


class ResizeSymbol(QUndoCommand):
    ''' Undo/Redo command for resizing a symbol '''
    def __init__(self, symbol_id, old_rect, new_rect):
        super(ResizeSymbol, self).__init__()
        self.setText('Resize symbol')
        self.symbol = symbol_id
        self.old_rect = old_rect
        self.new_rect = new_rect

    def undo(self):
        self.symbol.resizeItem(self.old_rect)

    def redo(self):
        self.symbol.resizeItem(self.new_rect)


class InsertSymbol(QUndoCommand):
    ''' Undo/Redo command for inserting a new item '''
    def __init__(self, item, parent, pos):
        super(InsertSymbol, self).__init__()
        self.item = item
        self.parent = parent
        self.pos_x = pos.x() if pos else None
        self.pos_y = pos.y() if pos else None
        self.scene = item.scene() or parent.scene()

    def undo(self):
        self.pos_x = self.item.x()
        self.pos_y = self.item.y()
        self.item.deleteSymbol()

    def redo(self):
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        self.item.insertSymbol(self.parent, x=self.pos_x, y=self.pos_y)
        self.scene.refresh()


class DeleteSymbol(QUndoCommand):
    ''' Undo/Redo command for a symbol deletion '''
    def __init__(self, item):
        super(DeleteSymbol, self).__init__()
        self.item = item
        self.scene = item.scene()
        self.parent = item.parentItem() if item.hasParent else None
        self.pos_x = 0
        self.pos_y = 0

    def undo(self):
        self.item.insertSymbol(self.parent, self.pos_x, self.pos_y)
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        self.scene.refresh()

    def redo(self):
        self.pos_x = self.item.x()
        self.pos_y = self.item.y()
        self.item.deleteSymbol()
        self.scene.refresh()


class MoveSymbol(QUndoCommand):
    ''' Undo/Redo command for moving symbols '''
    def __init__(self, symbol_id, old_pos, new_pos):
        super(MoveSymbol, self).__init__()
        self.setText('Move symbol')
        self.symbol = symbol_id
        self.old_pos = old_pos
        self.new_pos = new_pos

    def undo(self):
        ''' Undo a symbol move '''
        self.symbol.setPos(self.old_pos)
        if hasattr(self.symbol, 'decisionParent'):
            self.symbol.decisionParent.updateConnectionPointPosition()
        elif hasattr(self.symbol, 'onTheRight'):
            # If comment symbol, correctly flip it depending on its position
            if(self.symbol.x() <
                    self.symbol.parentItem().boundingRect().width() + 5):
                self.symbol.onTheRight = False
            else:
                self.symbol.onTheRight = True

    def redo(self):
        ''' Apply a symbol move '''
        self.symbol.setPos(self.new_pos)
        if hasattr(self.symbol, 'decisionParent'):
            self.symbol.decisionParent.updateConnectionPointPosition()
        elif hasattr(self.symbol, 'onTheRight'):
            # If comment symbol, correctly flip it depending on its position
            if(self.symbol.x() <
                    self.symbol.parentItem().boundingRect().width() + 5):
                self.symbol.onTheRight = False
            else:
                self.symbol.onTheRight = True
