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
    def __init__(self, textId, oldText, newText):
        super(ReplaceText, self).__init__()
        self.setText('Replace text')
        self.text = textId
        self.oldText = oldText
        self.newText = newText

    def undo(self):
        self.text.setPlainText(self.oldText)

    def redo(self):
        self.text.setPlainText(self.newText)


class ResizeSymbol(QUndoCommand):
    ''' Undo/Redo command for resizing a symbol '''
    def __init__(self, symbolId, oldRect, newRect):
        super(ResizeSymbol, self).__init__()
        self.setText('Resize symbol')
        self.symbol = symbolId
        self.oldRect = oldRect
        self.newRect = newRect

    def undo(self):
        self.symbol.resizeItem(self.oldRect)

    def redo(self):
        self.symbol.resizeItem(self.newRect)


class InsertSymbol(QUndoCommand):
    ''' Undo/Redo command for inserting a new item '''
    def __init__(self, item, parent, pos):
        super(InsertSymbol, self).__init__()
        self.item = item
        self.parent = parent
        self.x = pos.x() if pos else None
        self.y = pos.y() if pos else None
        self.scene = item.scene() or parent.scene()

    def undo(self):
        self.x = self.item.x()
        self.y = self.item.y()
        self.item.deleteSymbol()

    def redo(self):
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)
        self.item.insertSymbol(self.parent, x=self.x, y=self.y)
        #if self.parent:
        #    for cnx in self.parent.connections():
        #        cnx.update_lines()
        #for cnx in self.item.connections():
        #    cnx.update_lines()


class DeleteSymbol(QUndoCommand):
    ''' Undo/Redo command for a symbol deletion '''
    def __init__(self, item):
        super(DeleteSymbol, self).__init__()
        self.item = item
        self.scene = item.scene()
        self.parent = item.parentItem() if item.hasParent else None

    def undo(self):
        self.item.insertSymbol(self.parent, self.x, self.y)
        if self.item not in self.scene.items():
            self.scene.addItem(self.item)

    def redo(self):
        self.x = self.item.x()
        self.y = self.item.y()
        self.item.deleteSymbol()


class MoveSymbol(QUndoCommand):
    ''' Undo/Redo command for moving symbols '''
    def __init__(self, symbolId, oldPos, newPos):
        super(MoveSymbol, self).__init__()
        self.setText('Move symbol')
        self.symbol = symbolId
        self.oldPos = oldPos
        self.newPos = newPos

    def undo(self):
        ''' Undo a symbol move '''
        self.symbol.setPos(self.oldPos)
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
        self.symbol.setPos(self.newPos)
        if hasattr(self.symbol, 'decisionParent'):
            self.symbol.decisionParent.updateConnectionPointPosition()
        elif hasattr(self.symbol, 'onTheRight'):
            # If comment symbol, correctly flip it depending on its position
            if(self.symbol.x() <
                    self.symbol.parentItem().boundingRect().width() + 5):
                self.symbol.onTheRight = False
            else:
                self.symbol.onTheRight = True
