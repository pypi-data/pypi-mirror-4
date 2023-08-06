#!/usr/bin python

""" Defines a dock toolbar for generating expanding toolbar icons. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt import Signal
from projexui.qt.QtCore import QRect,\
                               Qt,\
                               QSize,\
                               QPoint,\
                               QParallelAnimationGroup

from projexui.qt.QtGui import QWidget,\
                              QPainter,\
                              QBoxLayout,\
                              QLabel,\
                              QGraphicsDropShadowEffect,\
                              QAction

from projexui.xanimation import XObjectAnimation
from projexui import resources
from projex.enum import enum

class XDockActionLabel(QLabel):
    entered = Signal()
    exited = Signal()
    
    def __init__(self, action, pixmapSize, parent=None):
        super(XDockActionLabel, self).__init__(parent)
        
        # define custom properties
        self._action = action
        self._pixmapSize = pixmapSize
        self._position = XDockToolbar.Position.South
        
        # setup default properties
        self.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        self.setPixmapSize(pixmapSize)
        self.setMouseTracking(True)
        self.setToolTip(action.toolTip())
    
    def action(self):
        """
        Returns the action linked with this label.
        
        :return     <QAction>
        """
        return self._action
    
    def mousePressEvent(self, event):
        """
        Handles when the user presses this label.
        
        :param      event | <QEvent>
        """
        if event.button() == Qt.LeftButton:
            self.parent().actionTriggered.emit(self.action())
        elif event.button() == Qt.MidButton:
            self.parent().actionMiddleTriggered.emit(self.action())
        elif event.button() == Qt.RightButton:
            self.parent().actionMenuRequested.emit(self.action(),
                                                   self.mapToParent(event.pos()))
        
        event.accept()
    
    def pixmapSize(self):
        """
        Returns the size of the pixmap for this widget.
        
        :return     <QSize>
        """
        return self._pixmapSize
    
    def position(self):
        """
        Returns the position associated with this label.
        
        :return     <XDockToolbar.Position>
        """
        return self._position
    
    def setPixmapSize(self, size):
        """
        Sets the pixmap size for this label.
        
        :param      size | <QSize>
        """
        self._pixmapSize = size
        self.setPixmap(self.action().icon().pixmap(size))
        
        max_size = self.parent().maximumPixmapSize()
        
        if self.position() in (XDockToolbar.Position.North,
                               XDockToolbar.Position.South):
            self.setFixedWidth(size.width())
            self.setFixedHeight(max_size.height())
        else:
            self.setFixedWidth(max_size.width())
            self.setFixedHeight(size.height())
    
    def setPosition(self, position):
        """
        Adjusts this label to match the given position.
        
        :param      <XDockToolbar.Position>
        """
        self._position = position
        
        if position == XDockToolbar.Position.North:
            self.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        elif position == XDockToolbar.Position.East:
            self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        elif position == XDockToolbar.Position.South:
            self.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        elif position == XDockToolbar.Position.West:
            self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

#----------------------------------------------------------------------

class XDockToolbar(QWidget):
    Position = enum('North', 'South', 'East', 'West')
    
    actionTriggered = Signal(QAction)
    actionMiddleTriggered = Signal(QAction)
    actionMenuRequested = Signal(QAction, QPoint)
    currentActionChanged = Signal(QAction)
    
    def __init__(self, parent=None):
        super(XDockToolbar, self).__init__(parent)
        
        # defines the position for this widget
        self._currentAction = -1
        self._position = XDockToolbar.Position.South
        self._minimumPixmapSize = QSize(16, 16)
        self._maximumPixmapSize = QSize(48, 48)
        
        # install an event filter to update the location for this toolbar
        layout = QBoxLayout(QBoxLayout.LeftToRight)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)
        layout.addStretch(1)
        layout.addStretch(1)
        
        self.setLayout(layout)
        self.setContentsMargins(2, 2, 2, 2)
        self.setMouseTracking(True)
        parent.window().installEventFilter(self)
        parent.window().statusBar().installEventFilter(self)
    
    def addAction(self, action):
        """
        Adds the inputed action to this toolbar.
        
        :param      action | <QAction>
        """
        super(XDockToolbar, self).addAction(action)
        
        label = XDockActionLabel(action, self.minimumPixmapSize(), self)
        label.setPosition(self.position())
        
        layout = self.layout()
        layout.insertWidget(layout.count() - 1, label)
    
    def actionAt(self, pos):
        """
        Returns the action at the given position.
        
        :param      pos | <QPoint>
        
        :return     <QAction> || None
        """
        child = self.childAt(pos)
        if child:
            return child.action()
        return None
        
    def actionLabels(self):
        """
        Returns the labels for this widget.
        
        :return     <XDockActionLabel>
        """
        l = self.layout()
        return [l.itemAt(i).widget() for i in range(1, l.count() - 1)]
    
    def clear(self):
        """
        Clears out all the actions and items from this toolbar.
        """
        for act in self.actions():
            act.setParent(None)
            act.deleteLater()
    
    def currentAction(self):
        """
        Returns the currently hovered/active action.
        
        :return     <QAction> || None
        """
        return self._action
    
    def eventFilter(self, object, event):
        """
        Filters the parent objects events to rebuild this toolbar when
        the widget resizes.
        
        :param      object | <QObject>
                    event | <QEvent>
        """
        if event.type() in (event.Move, event.Resize):
            if self.isVisible():
                self.rebuild()
            elif object.isVisible():
                self.setVisible(True)
        
        return False
    
    def labelForAction(self, action):
        """
        Returns the label that contains the inputed action.
        
        :return     <XDockActionLabel> || None
        """
        for label in self.actionLabels():
            if label.action() == action:
                return label
        return None
    
    def leaveEvent(self, event):
        """
        Clears the current action for this widget.
        
        :param      event | <QEvent>
        """
        super(XDockToolbar, self).leaveEvent(event)
        
        self.setCurrentAction(None)
    
    def maximumPixmapSize(self):
        """
        Returns the maximum pixmap size for this toolbar.
        
        :return     <int>
        """
        return self._maximumPixmapSize
    
    def minimumPixmapSize(self):
        """
        Returns the minimum pixmap size that will be displayed to the user
        for the dock widget.
        
        :return     <int>
        """
        return self._minimumPixmapSize
    
    def mouseMoveEvent(self, event):
        """
        Updates the labels for this dock toolbar.
        
        :param      event | <XDockToolbar>
        """
        # update the current label
        self.setCurrentAction(self.actionAt(event.pos()))
    
    def position(self):
        """
        Returns the position for this docktoolbar.
        
        :return     <XDockToolbar.Position>
        """
        return self._position
    
    def rebuild(self):
        """
        Rebuilds the widget based on the position and current size/location
        of its parent.
        """
        if not self.isVisible():
            return
        
        self.raise_()
        
        max_size = self.maximumPixmapSize()
        min_size = self.minimumPixmapSize()
        widget   = self.window()
        rect     = widget.rect()
        rect.setBottom(rect.bottom() - widget.statusBar().height())
        rect.setTop(widget.menuBar().height())
        offset   = 8
        
        # align this widget to the north
        if self.position() == XDockToolbar.Position.North:
            self.move(rect.left(), rect.top())
            self.resize(rect.width(), min_size.height() + offset)
        
        # align this widget to the east
        elif self.position() == XDockToolbar.Position.East:
            self.move(rect.left(), rect.top())
            self.resize(min_size.width() + offset, rect.height())
        
        # align this widget to the south
        elif self.position() == XDockToolbar.Position.South:
            self.move(rect.left(), rect.top() - min_size.height() - offset)
            self.resize(rect.width(), min_size.height() + offset)
        
        # align this widget to the west
        else:
            self.move(rect.right() - min_size.width() - offset, rect.top())
            self.resize(min_size.width() + offset, rect.height())
    
    def setCurrentAction(self, action):
        """
        Sets the current action for this widget that highlights the size
        for this toolbar.
        
        :param      action | <QAction>
        """
        
        if action == self._currentAction:
            return
        
        self._currentAction = action
        self.currentActionChanged.emit(action)
        
        labels   = self.actionLabels()
        anim_grp = QParallelAnimationGroup(self)
        max_size = self.maximumPixmapSize()
        min_size = self.minimumPixmapSize()
        
        if action:
            label = self.labelForAction(action)
            index = labels.index(label)
            
            # create the highlight effect
            palette = self.palette()
            effect = QGraphicsDropShadowEffect(label)
            effect.setXOffset(0)
            effect.setYOffset(0)
            effect.setBlurRadius(20)
            effect.setColor(palette.color(palette.Highlight))
            label.setGraphicsEffect(effect)
            
            offset = 8
            if self.position() in (XDockToolbar.Position.East,
                                   XDockToolbar.Position.West):
                self.resize(max_size.width() + offset, self.height())
            
            elif self.position() in (XDockToolbar.Position.North,
                                     XDockToolbar.Position.South):
                self.resize(self.width(), max_size.height() + offset)
            
            w  = max_size.width()
            h  = max_size.height()
            dw = (max_size.width() - min_size.width()) / 3
            dh = (max_size.height() - min_size.height()) / 3
            
            for i in range(4):
                before = index - i
                after  = index + i
                
                if 0 <= before and before < len(labels):
                    anim = XObjectAnimation(labels[before],
                                            'setPixmapSize',
                                            anim_grp)
                    
                    anim.setStartValue(labels[before].pixmapSize())
                    anim.setEndValue(QSize(w, h))
                    anim.setDuration(150)
                    anim_grp.addAnimation(anim)
                    
                    if i:
                        labels[before].setGraphicsEffect(None)
                
                if after != before and 0 <= after and after < len(labels):
                    anim = XObjectAnimation(labels[after],
                                            'setPixmapSize',
                                            anim_grp)
                    
                    anim.setStartValue(labels[after].pixmapSize())
                    anim.setEndValue(QSize(w, h))
                    anim.setDuration(150)
                    anim_grp.addAnimation(anim)
                    
                    if i:
                        labels[after].setGraphicsEffect(None)
            
                w -= dw
                h -= dh
        else:
            offset = 8
            if self.position() in (XDockToolbar.Position.East,
                                   XDockToolbar.Position.West):
                self.resize(min_size.width() + offset, self.height())
            
            elif self.position() in (XDockToolbar.Position.North,
                                     XDockToolbar.Position.South):
                self.resize(self.width(), min_size.height() + offset)
            
            for label in self.actionLabels():
                # clear the graphics effect 
                label.setGraphicsEffect(None)
                
                # create the animation
                anim = XObjectAnimation(label, 'setPixmapSize', self)
                anim.setStartValue(label.pixmapSize())
                anim.setEndValue(min_size)
                anim.setDuration(150)
                anim_grp.addAnimation(anim)
        
        anim_grp.start()
        anim_grp.finished.connect(anim_grp.deleteLater)
    
    def setVisible(self, state):
        """
        Sets whether or not this toolbar is visible.  If shown, it will rebuild.
        
        :param      state | <bool>
        """
        super(XDockToolbar, self).setVisible(state)
        
        if state:
            self.rebuild()
            self.setCurrentAction(None)
    
    def setMaximumPixmapSize(self, size):
        """
        Sets the maximum pixmap size for this toolbar.
        
        :param     size | <int>
        """
        self._maximumPixmapSize = size
        position = self.position()
        self._position = None
        self.setPosition(position)
    
    def setMinimumPixmapSize(self, size):
        """
        Sets the minimum pixmap size that will be displayed to the user
        for the dock widget.
        
        :param     size | <int>
        """
        self._minimumPixmapSize = size
        position = self.position()
        self._position = None
        self.setPosition(position)
    
    def setPosition(self, position):
        """
        Sets the position for this widget and its parent.
        
        :param      position | <XDockToolbar.Position>
        """
        if position == self._position:
            return
        
        self._position = position
        
        widget   = self.window()
        layout   = self.layout()
        offset   = 8
        min_size = self.minimumPixmapSize()
        
        # set the layout to north
        if position == XDockToolbar.Position.North:
            self.move(0, 0)
            widget.setContentsMargins(0, min_size.height() + offset, 0, 0)
            layout.setDirection(QBoxLayout.LeftToRight)
        
        # set the layout to east
        elif position == XDockToolbar.Position.East:
            self.move(0, 0)
            widget.setContentsMargins(min_size.width() + offset, 0, 0, 0)
            layout.setDirection(QBoxLayout.TopToBottom)
        
        # set the layout to the south
        elif position == XDockToolbar.Position.South:
            widget.setContentsMargins(0, 0, 0, min_size.height() + offset)
            layout.setDirection(QBoxLayout.LeftToRight)
        
        # set the layout to the west
        else:
            widget.setContentsMargins(0, 0, min_size.width() + offset, 0)
            layout.setDirection(QBoxLayout.TopToBottom)
        
        # update the label alignments
        for label in self.actionLabels():
            label.setPosition(position)
        
        # rebuilds the widget
        self.rebuild()
        self.update()
