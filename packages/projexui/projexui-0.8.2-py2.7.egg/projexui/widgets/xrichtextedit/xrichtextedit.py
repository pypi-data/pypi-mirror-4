#!/usr/bin python

""" Defines a full rich text edit to handle WYSIWYG editing. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

from projexui.qt import Signal, Slot, Property
from projexui.qt.QtCore import Qt
from projexui.qt.QtGui import QWidget,\
                              QTextCharFormat,\
                              QAction,\
                              QActionGroup,\
                              QKeySequence,\
                              QFont,\
                              QColorDialog,\
                              QColor

import projexui

from projexui.widgets.xpopupwidget import XPopupWidget
from projexui.widgets.xrichtextedit.xfontpickerwidget import XFontPickerWidget


class XRichTextEdit(QWidget):
    """ """
    copyAvailable = Signal(bool)
    currentCharFormatChanged = Signal(QTextCharFormat)
    cursorPositionChanged = Signal()
    redoAvailable = Signal(bool)
    selectionChanged = Signal()
    textChanged = Signal()
    undoAvailable = Signal(bool)
    
    def __init__( self, parent = None ):
        super(XRichTextEdit, self).__init__( parent )
        
        # load the user interface
        projexui.loadUi(__file__, self)
        
        # define custom properties
        
        # set default properties
        self.setFocusProxy(self.uiEditTXT)
        self.uiFindWGT.setTextEdit(self.uiEditTXT)
        self.uiFindWGT.hide()
        
        # create the font picker widget
        self._fontPickerWidget = XFontPickerWidget(self)
        self.uiFontBTN.setDefaultAnchor(XPopupWidget.Anchor.TopLeft)
        self.uiFontBTN.setCentralWidget(self._fontPickerWidget)
        
        popup = self.uiFontBTN.popupWidget()
        popup.setResizable(False)
        popup.setShowTitleBar(False)
        
        self._fontPickerWidget.accepted.connect(popup.accept)
        
        # generate actions for this editor based on the toolbar buttons
        self._actions = {}
        for mapping in (('bold', self.uiBoldBTN, 'Ctrl+B'),
                        ('italic', self.uiItalicBTN, 'Ctrl+I'),
                        ('underline', self.uiUnderlineBTN, 'Ctrl+U'),
                        ('strikeOut', self.uiStrikeoutBTN, ''),
                        ('unordered', self.uiUnorderedBTN, ''),
                        ('ordered', self.uiOrderedBTN, ''),
                        ('table', self.uiTableBTN, ''),
                        ('align_left', self.uiAlignLeftBTN, ''),
                        ('align_right', self.uiAlignRightBTN, ''),
                        ('align_center', self.uiAlignCenterBTN, ''),
                        ('align_justify', self.uiAlignJustifyBTN, ''),
                        ('font_color', self.uiFontColorBTN, ''),
                        ('bg_color', self.uiBackgroundColorBTN, '')):
            
            name, btn, shortcut = mapping
            
            act = QAction(self)
            act.setObjectName(name)
            act.setToolTip(btn.toolTip())
            act.setIcon(btn.icon())
            
            act.setShortcut(QKeySequence(shortcut))
            act.setCheckable(btn.isCheckable())
            act.setChecked(btn.isChecked())
            
            act.setShortcutContext(Qt.WidgetWithChildrenShortcut)
            
            btn.setDefaultAction(act)
            
            self._actions[name] = act
            self.addAction(act)
        
        # create the action groupings
        popup.resetRequested.connect(self.updateFontPicker)
        popup.aboutToShow.connect(self.updateFontPicker)
        popup.accepted.connect(self.assignFont)
        
        align_group = QActionGroup(self)
        align_group.addAction(self._actions['align_left'])
        align_group.addAction(self._actions['align_right'])
        align_group.addAction(self._actions['align_center'])
        align_group.addAction(self._actions['align_justify'])
        
        align_group.triggered.connect(self.assignAlignment)
        
        self._actions['align_left'].setChecked(True)
        
        # create connections
        self._actions['bold'].toggled.connect(self.setFontBold)
        self._actions['italic'].toggled.connect(self.setFontItalic)
        self._actions['underline'].toggled.connect(self.setFontUnderline)
        self._actions['strikeOut'].toggled.connect(self.setFontStrikeOut)
        
        self._actions['ordered'].triggered.connect(self.insertOrdered)
        self._actions['unordered'].triggered.connect(self.insertUnordered)
        self._actions['table'].triggered.connect(self.insertTable)
        
        self._actions['font_color'].triggered.connect(self.pickTextColor)
        self._actions['bg_color'].triggered.connect(self.pickTextBackgroundColor)
        
        # link signals from the editor to the system
        for signal in ('copyAvailable',
                       'currentCharFormatChanged',
                       'cursorPositionChanged',
                       'redoAvailable',
                       'selectionChanged',
                       'textChanged',
                       'undoAvailable'):
                           
            from_ = getattr(self.uiEditTXT, signal)
            to_   = getattr(self, signal)
            
            from_.connect(to_)
        
        self.cursorPositionChanged.connect(self.refreshAlignmentUi)
        self.currentCharFormatChanged.connect(self.refreshUi)
    
    def alignment(self):
        """
        Returns the current alignment for the editor.
        
        :return     <Qt.Alignment>
        """
        return self.editor().alignment()
    
    def assignAlignment(self, action):
        """
        Sets the current alignment for the editor.
        """
        if self._actions['align_left'] == action:
            self.setAlignment(Qt.AlignLeft)
        elif self._actions['align_right'] == action:
            self.setAlignment(Qt.AlignRight)
        elif self._actions['align_center'] == action:
            self.setAlignment(Qt.AlignHCenter)
        else:
            self.setAlignment(Qt.AlignJustify)
    
    def assignFont(self):
        """
        Assigns the font family and point size settings from the font picker
        widget.
        """
        font = self.currentFont()
        font.setFamily(self._fontPickerWidget.currentFamily())
        font.setPointSize(self._fontPickerWidget.pointSize())
        self.setCurrentFont(font)
    
    def blockSignals(self, state):
        """
        Propagates the block signals for this editor down to the text
        editor.
        
        :param      state | <bool>
        """
        super(XRichTextEdit, self).blockSignals(state)
        self.uiEditTXT.blockSignals(state)
    
    def currentFont(self):
        """
        Returns the current font for this editor.
        
        :return     <QFont>
        """
        return self.editor().currentFont()
    
    def document(self):
        """
        Returns the text document assigned to this edit.
        
        :return     <QTextDocument>
        """
        return self.editor().document()
    
    def documentMargin(self):
        """
        Returns the margins used for the document edges.
        
        :return     <int>
        """
        return self.document().documentMargin()
    
    def editor(self):
        """
        Returns the text editor that is linked with this rich text editor.
        
        :return     <QTextEdit>
        """
        return self.uiEditTXT
    
    def fontBold(self):
        """
        Returns whether or not the current text is bold.
        
        :return     <bool>
        """
        return self.editor().fontWeight() == QFont.Bold
    
    def fontFamily(self):
        """
        Returns the family name of the current font for this editor.
        
        :return     <str>
        """
        return self.editor().fontFamily()
    
    def fontItalic(self):
        """
        Returns whether or not the editor is currently in italics.
        
        :return     <bool>
        """
        return self.editor().fontItalic()
    
    def fontPointSize(self, pointSize):
        """
        Returns the current font's point size.
        
        :return     <int>
        """
        return self.editor().fontPointSize()
    
    def fontStrikeOut(self):
        """
        Returns whether or not the current font is in strike out mode.
        
        :return     <bool>
        """
        return self.currentFont().strikeOut()
    
    def fontUnderline(self):
        """
        Returns whether or not the editor is in underline state.
        
        :return     <bool>
        """
        return self.editor().fontUnderline()
    
    def fontWeight(self):
        """
        Returns the current font weight of the editor.
        
        :return     <QFont.Weight>
        """
        return self.editor().fontWeight()
    
    def insertOrdered(self):
        """
        Inserts an ordered list into the editor.
        """
        self.editor().insertHtml('<ol><li>Item #1</li><li>Item #2</li></ol>')
    
    def insertTable(self):
        """
        Inserts a table into the editor.
        """
        html = ['<table>']
        html.append('<tr><td>Row 1, Cell 1</td><td>Row 1, Cell 2</td></tr>')
        html.append('<tr><td>Row 2, Cell 1</td><td>Row 2, Cell 2</td></tr>')
        html.append('</table>')
        
        self.editor().insertHtml(''.join(html))
    
    def insertUnordered(self):
        """
        Inserts an ordered list into the editor.
        """
        self.editor().insertHtml('<ul><li>Item #1</li><li>Item #2</li></ul>')
    
    @Slot()
    def pickTextBackgroundColor(self):
        """
        Prompts the user to select a text color.
        """
        clr = QColorDialog.getColor(self.textBackgroundColor(),
                                    self.window(),
                                    'Pick Background Color')
        
        if clr.isValid():
            self.setTextBackgroundColor(clr)
    
    @Slot()
    def pickTextColor(self):
        """
        Prompts the user to select a text color.
        """
        clr = QColorDialog.getColor(self.textColor(),
                                    self.window(),
                                    'Pick Text Color')
        
        if clr.isValid():
            self.setTextColor(clr)
    
    def refreshUi(self):
        """
        Matches the UI state to the current cursor positioning.
        """
        font = self.currentFont()
        
        for name in ('underline', 'bold', 'italic', 'strikeOut'):
            getter = getattr(font, name)
            act = self._actions[name]
            act.blockSignals(True)
            act.setChecked(getter())
            act.blockSignals(False)
    
    def refreshAlignmentUi(self):
        """
        Refreshes the alignment UI information.
        """
        align = self.alignment()
        for name, value in (('align_left', Qt.AlignLeft),
                            ('align_right', Qt.AlignRight),
                            ('align_center', Qt.AlignHCenter),
                            ('align_justify', Qt.AlignJustify)):
            
            act = self._actions[name]
            act.blockSignals(True)
            act.setChecked(value == align)
            act.blockSignals(False)
    
    def setAlignment(self, align):
        """
        Sets the current alignment for this editor.
        
        :param      align | <Qt.Align>
        """
        self.blockSignals(True)
        self.editor().setAlignment(align)
        self.blockSignals(False)
        self.refreshAlignmentUi()
    
    @Slot(QFont)
    def setCurrentFont(self, font):
        """
        Sets the current font for the editor to the inputed font.
        
        :param      font | <QFont>
        """
        self.blockSignals(True)
        self.editor().setCurrentFont(font)
        self.blockSignals(False)
        self.refreshUi()
    
    @Slot(int)
    def setDocumentMargin(self, margin):
        """
        Sets the document margins for this editor.
        
        :param      margin | <int>
        """
        self.document().setDocumentMargin(margin)
    
    @Slot(bool)
    def setFontBold(self, state):
        """
        Toggles whether or not the text is currently bold.
        
        :param      state | <bool>
        """
        if state:
            weight = QFont.Bold
        else:
            weight = QFont.Normal
        
        self.setFontWeight(weight)
    
    @Slot(str)
    def setFontFamily(self, family):
        """
        Sets the current font family to the inputed family.
        
        :param      family | <str>
        """
        self.blockSignals(True)
        self.editor().setFontFamily(family)
        self.blockSignals(False)
    
    @Slot(bool)
    def setFontItalic(self, state):
        """
        Toggles whehter or not the text is currently italic.
        
        :param      state | <bool>
        """
        font = self.currentFont()
        font.setItalic(state)
        self.setCurrentFont(font)
    
    @Slot(int)
    def setFontPointSize(self, size):
        """
        Sets the point size of the current font to the inputed size.
        
        :param      size | <int>
        """
        self.blockSignals(True)
        self.editor().setFontPointSize(size)
        self.blockSignals(False)
    
    @Slot(bool)
    def setFontStrikeOut(self, strikeOut):
        """
        Sets whether or not this editor is currently striking out the text.
        
        :param      strikeOut | <bool>
        """
        font = self.currentFont()
        font.setStrikeOut(strikeOut)
        self.setCurrentFont(font)
    
    @Slot(bool)
    def setFontUnderline(self, state):
        """
        Sets whether or not this editor is currently in underline state.
        
        :param      state | <bool>
        """
        font = self.currentFont()
        font.setUnderline(state)
        self.setCurrentFont(font)
    
    @Slot(QFont.Weight)
    def setFontWeight(self, weight):
        """
        Sets the font weight for this editor to the inputed weight.
        
        :param      weight | <QFont.Weight>
        """
        font = self.currentFont()
        font.setWeight(weight)
        self.setCurrentFont(font)
    
    @Slot(str)
    def setText(self, text):
        """
        Sets the text for this editor.
        
        :param      text | <str>
        """
        self.editor().setText(text)
    
    @Slot(QColor)
    def setTextBackgroundColor(self, color):
        """
        Sets the text background color for this instance to the inputed color.
        
        :param      color | <QColor>
        """
        self.editor().setTextBackgroundColor(QColor(color))
    
    @Slot(QColor)
    def setTextColor(self, color):
        """
        Sets the text color for this instance to the inputed color.
        
        :param      color | <QColor>
        """
        self.editor().setTextColor(QColor(color))
    
    def textBackgroundColor(self):
        """
        Returns the background color that is current in the document.
        
        :return     <QColor>
        """
        return self.editor().textBackgroundColor()
    
    def textColor(self):
        """
        Returns the text color that is current in the document.
        
        :return     <QColor>
        """
        return self.editor().textColor()
    
    def toDiv(self, style='document'):
        """
        Returns the text as paragaphed HTML vs. a full HTML document page.
        
        :return     <str>
        """
        if not self.editor().toPlainText():
            return ''
        
        html = unicode(self.editor().toHtml())
        start = '<body '
        end = '</body>'
        
        start_i = html.find(start)
        end_i = html.find(end)
        
        stripped = html[start_i+len(start):end_i]
        return '<div class="%s" %s</div>' % (style, stripped)
    
    def toHtml(self):
        """
        Returns the text as HTML.
        
        :return     <str>
        """
        if self.editor().toPlainText():
            return self.editor().toHtml()
        return ''
    
    def toPlainText(self):
        """
        Returns the text as plain text.
        
        :return     <str>
        """
        return self.editor().toPlainText()
    
    def updateFontPicker(self):
        """
        Updates the font picker widget to the current font settings.
        """
        font = self.currentFont()
        self._fontPickerWidget.setPointSize(font.pointSize())
        self._fontPickerWidget.setCurrentFamily(font.family())