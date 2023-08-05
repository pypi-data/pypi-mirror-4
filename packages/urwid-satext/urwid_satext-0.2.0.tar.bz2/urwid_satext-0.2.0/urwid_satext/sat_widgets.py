#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Primitivus: a SAT frontend
Copyright (C) 2009, 2010  Jérôme Poisson (goffi@goffi.org)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import urwid
from logging import debug, info, warning, error
import encodings
utf8decode = lambda s: encodings.codecs.utf_8_decode(s)[0]

from urwid.util import is_mouse_press #XXX: is_mouse_press is not included in urwid in 1.0.0


class AdvancedEdit(urwid.Edit):
    """Edit box with some custom improvments
    new chars:
              - C-a: like 'home'
              - C-e: like 'end'
              - C-k: remove everything on the right of the cursor
              - C-w: remove the word on the back
    new behaviour: emit a 'click' signal when enter is pressed"""
    signals = urwid.Edit.signals + ['click']

    def setCompletionMethod(self, callback):
        """Define method called when completion is asked
        @callback: method with 2 arguments:
                    - the text to complete
                    - if there was already a completion, a dict with
                        - 'completed':last completion
                        - 'completion_pos': cursor position where the completion starts 
                        - 'position': last completion cursor position
                      this dict must be used (and can be filled) to find next completion)
                   and which return the full text completed"""
        self.completion_cb = callback
        self.completion_data = {}

    def keypress(self, size, key):
        #TODO: insert mode is not managed yet
        if key == 'ctrl a':
            key = 'home'
        elif key == 'ctrl e':
            key = 'end'
        elif key == 'ctrl k':
            self._delete_highlighted()
            self.set_edit_text(self.edit_text[:self.edit_pos])
        elif key == 'ctrl w':    
            before = self.edit_text[:self.edit_pos]
            pos = before.rstrip().rfind(" ")+1
            self.set_edit_text(before[:pos] + self.edit_text[self.edit_pos:])
            self.set_edit_pos(pos)
        elif key == 'enter':
            self._emit('click')
        elif key == 'shift tab':
            try:
                before = self.edit_text[:self.edit_pos]
                if self.completion_data:
                    if (not self.completion_data['completed']
                        or self.completion_data['position'] != self.edit_pos
                        or not before.endswith(self.completion_data['completed'])):
                        self.completion_data.clear()
                    else:
                        before = before[:-len(self.completion_data['completed'])]
                complet = self.completion_cb(before, self.completion_data)
                self.completion_data['completed'] = complet[len(before):]
                self.set_edit_text(complet+self.edit_text[self.edit_pos:])
                self.set_edit_pos(len(complet))
                self.completion_data['position'] = self.edit_pos
                return
            except AttributeError:
                #No completion method defined
                pass
        return super(AdvancedEdit, self).keypress(size, key) 

class Password(AdvancedEdit):
    """Edit box which doesn't show what is entered (show '*' or other char instead)"""

    def __init__(self, *args, **kwargs):
        """Same args than Edit.__init__ with an additional keyword arg 'hidden_char'
        @param hidden_char: char to show instead of what is actually entered: default '*'
        """
        self.hidden_char=kwargs['hidden_char'] if kwargs.has_key('hidden_char') else '*'
        self.__real_text=''
        super(Password, self).__init__(*args, **kwargs)

    def set_edit_text(self, text):
        self.__real_text = text
        hidden_txt = len(text)*'*'
        super(Password, self).set_edit_text(hidden_txt)

    def get_edit_text(self):
        return self.__real_text

    def insert_text(self, text):
        self._edit_text = self.__real_text
        super(Password,self).insert_text(text)

    def render(self, size, focus=False):
        return super(Password, self).render(size, focus)
       
class ModalEdit(AdvancedEdit):
    """AdvancedEdit with vi-like mode management
    - there is a new 'mode' property wich can be changed with properties
    specified during init
    - completion callback received a new 'mode' argument
    """

    def __init__(self, modes, *args, **kwargs):
        """ first argument is "modes", others are the same paramaters as AdvancedEdit
        @param modes: dictionnary in the form:
                      'key_to_change_mode': ('Mode', caption)
                      e.g.: 'i': ('INSERTION', '> ')
                      There *MUST* be a None key (for NORMAL mode)"""
        assert(isinstance(modes, dict) and None in modes)
        self._modes = modes
        super(ModalEdit, self).__init__(*args, **kwargs)
        self.mode = self._modes[None][0]

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, value):
        mode_key = None
        for key in self._modes:
            if self._modes[key][0] == value:
                mode_key = key
                break
        
        mode, caption = self._modes[mode_key]
        self._mode = mode
        self.set_caption(caption)
        if not mode_key: #we are in NORMAL mode
            self.set_edit_text('')

    def setCompletionMethod(self, callback):
        """ Same as AdvancedEdit.setCompletionMethod, but with a third argument: current mode"""
        super(ModalEdit, self).setCompletionMethod(lambda text,data: callback(text, data, self._mode))

    def keypress(self, size, key):
        if key == 'esc':
            self.mode = "NORMAL"
            return
        if self._mode == 'NORMAL' and key in self._modes:
            self.mode = self._modes[key][0]
            return
        return super(ModalEdit, self).keypress(size, key) 

class SurroundedText(urwid.FlowWidget):
    """Text centered on a repeated character (like a Divider, but with a text in the center)"""

    def __init__(self,text,car=utf8decode('─')):
        self.text=text
        self.car=car

    def rows(self,size,focus=False):
        return self.display_widget(size, focus).rows(size, focus)

    def render(self, size, focus=False):
        return self.display_widget(size, focus).render(size, focus)

    def display_widget(self, size, focus):
        (maxcol,) = size
        middle = (maxcol-len(self.text))/2
        render_text = middle * self.car + self.text + (maxcol - len(self.text) - middle) * self.car
        return urwid.Text(render_text)

class SelectableText(urwid.WidgetWrap):
    """Text which can be selected with space"""
    signals = ['change']
    
    def __init__(self, text, align='left', header='', focus_attr='default_focus', selected_text=None, selected=False, data=None):
        """@param text: same as urwid.Text's text parameter
        @param align: same as urwid.Text's align parameter
        @select_attr: attrbute to use when selected
        @param selected: is the text selected ?"""
        self.focus_attr = focus_attr
        self.__selected = False
        self.__was_focused = False
        self.header = self.__valid_text(header)
        self.default_txt = self.__valid_text(text)
        urwid.WidgetWrap.__init__(self, urwid.Text("",align=align))
        self.setSelectedText(selected_text)
        self.setState(selected)

    def __valid_text(self, text):
        """Tmp method needed until dbus and urwid are more friends"""
        if isinstance(text,basestring):
            return unicode(text)
        elif isinstance(text,tuple):
            return (unicode(text[0]),text[1])
        elif isinstance(text,list):
            for idx in range(len(text)):
                elem = text[idx]
                if isinstance(elem,basestring):
                    text[idx] = unicode(elem)
                if isinstance(elem,tuple):
                    text[idx] = (unicode(elem[0]),elem[1])
        else:
            warning (_('WARNING: unknown text type'))
        return text

    def getValue(self):
        if isinstance(self.default_txt,basestring):
            return self.default_txt
        list_attr = self.default_txt if isinstance(self.default_txt, list) else [self.default_txt]
        txt = ""
        for attr in list_attr:
            if isinstance(attr,tuple):
                txt+=attr[1]
            else:
                txt+=attr
        return txt

    def get_text(self):
        """for compatibility with urwid.Text"""
        return self.getValue()

    def set_text(self, text):
        """/!\ set_text doesn't change self.selected_txt !"""
        self.default_txt = self.__valid_text(text)
        self.setState(self.__selected,invisible=True)

    def setSelectedText(self, text=None):
        """Text to display when selected
        @text: text as in urwid.Text or None for default value"""
        if text == None:
            text = ('selected',self.getValue())
        self.selected_txt = self.__valid_text(text)
        if self.__selected:
            self.setState(self.__selected)


    def __set_txt(self):
        txt_list = [self.header]
        txt = self.selected_txt if self.__selected else self.default_txt
        if isinstance(txt,list):
            txt_list.extend(txt)
        else:
            txt_list.append(txt)
        self._w.base_widget.set_text(txt_list)

    
    def setState(self, selected, invisible=False):
        """Change state
        @param selected: boolean state value
        @param invisible: don't emit change signal if True"""
        assert(type(selected)==bool)
        self.__selected=selected
        self.__set_txt()
        self.__was_focused = False
        self._invalidate()
        if not invisible:
            self._emit("change", self.__selected)
   
    def getState(self):
        return self.__selected

    def selectable(self):
        return True

    def keypress(self, size, key):
        if key==' ' or key=='enter':
            self.setState(not self.__selected)
        else:
            return key

    def mouse_event(self, size, event, button, x, y, focus):
        if is_mouse_press(event) and button == 1:
            self.setState(not self.__selected)
            return True
        
        return False
   
    def render(self, size, focus=False):
        attr_list = self._w.base_widget._attrib
        if not focus:
            if self.__was_focused:
                self.__set_txt()
                self.__was_focused = False
        else:
            if not self.__was_focused:
                if not attr_list:
                    attr_list.append((self.focus_attr,len(self._w.base_widget.text)))
                else:
                    for idx in range(len(attr_list)):
                        attr,attr_len = attr_list[idx]
                        if attr == None:
                            attr = self.focus_attr
                            attr_list[idx] = (attr,attr_len)
                        else:
                            if not attr.endswith('_focus'):
                                attr+="_focus"
                                attr_list[idx] = (attr,attr_len)
                self._w.base_widget._invalidate()
                self.__was_focused = True #bloody ugly hack :)
        return self._w.render(size, focus)

class ClickableText(SelectableText):
    signals = SelectableText.signals + ['click']
    
    def setState(self, selected, invisible=False):
        super(ClickableText,self).setState(False,True)
        if not invisible:
            self._emit('click')

class CustomButton(ClickableText):

    def __init__(self, label, on_press=None, user_data=None, left_border = "[ ", right_border = " ]"):
        self.label = label
        self.left_border = left_border
        self.right_border = right_border
        super(CustomButton, self).__init__([left_border, label, right_border]) 
        self.size = len(self.get_text())
        if on_press:
            urwid.connect_signal(self, 'click', on_press, user_data)

    def getSize(self):
        """Return representation size of the button"""
        return self.size

    def get_label(self):
        return self.label[1] if isinstance(self.label,tuple) else self.label

    def set_label(self, label):
        self.label = label
        self.set_text([self.left_border, label, self.right_border])

class GenericList(urwid.WidgetWrap):
    signals = ['click','change']

    def __init__(self, options, style=[], align='left', option_type = SelectableText, on_click=None, on_change=None, user_data=None):
        """
        Widget managing list of string and their selection
        @param options: list of strings used for options
        @param style: list of string:
            - 'single' if only one must be selected
            - 'no_first_select' nothing selected when list is first displayed 
            - 'can_select_none' if we can select nothing
        @param align: alignement of text inside the list
        @param on_click: method called when click signal is emited
        @param user_data: data sent to the callback for click signal
        """
        self.single = 'single' in style
        self.no_first_select = 'no_first_select' in style
        self.can_select_none = 'can_select_none' in style
        self.align = align
        self.option_type = option_type
        self.first_display = True
        
        if on_click:
            urwid.connect_signal(self, 'click', on_click, user_data)
        
        if on_change:
            urwid.connect_signal(self, 'change', on_change, user_data)
        
        self.content = urwid.SimpleListWalker([])
        self.list_box = urwid.ListBox(self.content)
        urwid.WidgetWrap.__init__(self, self.list_box)
        self.changeValues(options)

    def __onStateChange(self, widget, selected):
        if self.single:
            if not selected and not self.can_select_none:
                #if in single mode, it's forbidden to unselect a value
                widget.setState(True, invisible=True)
                return
            if selected:
                self.unselectAll(invisible=True)
                widget.setState(True, invisible=True)
        self._emit("change")

    def __onClick(self, widget):
        self._emit("click", widget)

    def unselectAll(self, invisible=False):
        for widget in self.content:
            if widget.getState():
                widget.setState(False, invisible)
                widget._invalidate()

    def deleteValue(self, value):
        """Delete the first value equal to the param given"""
        for widget in self.content:
            if widget.getValue() == value:
                self.content.remove(widget)
                self._emit('change')
                return
        raise ValueError("%s ==> %s" %  (str(value),str(self.content)))

    def getSelectedValue(self):
        """Convenience method to get the value selected as a string in single mode, or None"""
        values = self.getSelectedValues()
        return values[0] if values else None

    def getAllValues(self):
        """Return values of all items"""
        return [widget.getValue() for widget in self.content]

    def getSelectedValues(self):
        """Return values of selected items"""
        result = []
        for widget in self.content:
            if widget.getState():
                result.append(widget.getValue())
        return result

    def getDisplayWidget(self):
        return self.list_box

    def changeValues(self, new_values):
        """Change all value in one shot"""
        if not self.first_display:
            old_selected = self.getSelectedValues()
        widgets = []
        for option in new_values:
            widget = self.option_type(option, self.align)
            if not self.first_display and option in old_selected:
                widget.setState(True)
            widgets.append(widget)
            for signal, callback in (('change', self.__onStateChange), ('click', self.__onClick)):
                try:
                    urwid.connect_signal(widget, signal, callback)
                except NameError:
                    pass #the widget given doesn't support the signal
        self.content[:] = widgets
        if self.first_display and self.single and new_values and not self.no_first_select:
            self.content[0].setState(True)
        display_widget = self.getDisplayWidget()
        self._set_w(display_widget)
        self._emit('change')
        self.first_display = False 

    def selectValue(self, value):
        """Select the first item which has the given value"""
        self.unselectAll()
        idx = 0
        for widget in self.content:
            if widget.getValue() == value:
                widget.setState(True)
                self.list_box.set_focus(idx)
                return
            idx+=1

class List(urwid.FlowWidget):
    """FlowWidget list, same arguments as GenericList, with an additional one 'max_height'"""
    signals = ['click','change']

    def __init__(self, options, style=[], max_height=5, align='left', option_type = SelectableText, on_click=None, on_change=None, user_data=None):
        self.genericList = GenericList(options, style, align, option_type, on_click, on_change, user_data)
        self.max_height = max_height 

    def selectable(self):
        return True

    def keypress(self, size, key):
        return self.displayWidget(size,True).keypress(size, key)
        
    def unselectAll(self, invisible=False):
        return self.genericList.unselectAll(invisible)
    
    def deleteValue(self, value):
        return self.genericList.deleteValue(value)

    def getSelectedValue(self):
        return self.genericList.getSelectedValue()

    def getAllValues(self):
        return self.genericList.getAllValues()

    def getSelectedValues(self):
        return self.genericList.getSelectedValues()

    def changeValues(self, new_values):
        return self.genericList.changeValues(new_values)

    def selectValue(self, value):
        return self.genericList.selectValue(value)

    def render(self, size, focus=False):
        return self.displayWidget(size, focus).render(size, focus)
    
    def rows(self, size, focus=False):
        return self.displayWidget(size, focus).rows(size, focus)

    def displayWidget(self, size, focus):
        list_size = sum([wid.rows(size, focus) for wid in self.genericList.content])
        height = min(list_size,self.max_height) or 1 
        return urwid.BoxAdapter(self.genericList, height)

## MISC ##

class NotificationBar(urwid.WidgetWrap):
    """Bar used to show misc information to user"""
    signals = ['change']

    def __init__(self):
        self.waitNotifs = urwid.Text('')
        self.message = ClickableText('')
        urwid.connect_signal(self.message, 'click', lambda wid: self.showNext())
        self.progress = ClickableText('')
        self.columns = urwid.Columns([('fixed',6,self.waitNotifs),self.message,('fixed',4,self.progress)])
        urwid.WidgetWrap.__init__(self, urwid.AttrMap(self.columns,'notifs'))
        self.notifs = []
    
    def __modQueue(self):
        """must be called each time the notifications queue is changed"""
        self.waitNotifs.set_text(('notifs',"(%i)" % len(self.notifs) if self.notifs else ''))
        self._emit('change')

    def setProgress(self,percentage):
        """Define the progression to show on the right side of the bar"""
        if percentage == None:
            self.progress.set_text('')
        else:
            self.progress.set_text(('notifs','%02i%%' % percentage))
        self._emit('change')

    def addPopUp(self, pop_up_widget):
        """Add a popup to the waiting queue"""
        self.notifs.append(('popup',pop_up_widget))
        self.__modQueue()

    def addMessage(self, message):
        "Add a message to the notificatio bar"
        if not self.message.get_text():
            self.message.set_text(('notifs',message))
            self._invalidate()
            self._emit('change')
        else:
            self.notifs.append(('message',message))
            self.__modQueue()

    def showNext(self):
        """Show next message if any, else delete current message"""
        found = None
        for notif in self.notifs:
            if notif[0] == "message":
                found = notif
                break
        if found:
            self.notifs.remove(found)
            self.message.set_text(('notifs',found[1]))
            self.__modQueue()
        else:
            self.message.set_text('')
            self._emit('change')

    def getNextPopup(self):
        """Return next pop-up and remove it from the queue
        @return: pop-up or None if there is no more in the queue"""
        ret = None
        for notif in self.notifs:
            if notif[0] == 'popup':
                ret = notif[1]
                break
        if ret:
            self.notifs.remove(notif)
            self.__modQueue()
        return ret

    def isQueueEmpty(self):
        return not bool(self.notifs)

    def canHide(self):
        """Return True if there is now important information to show"""
        return self.isQueueEmpty() and not self.message.get_text() and not self.progress.get_text()


class MenuBox(urwid.WidgetWrap):
    """Show menu items of a category in a box"""
    signals = ['click']
    
    def __init__(self,parent,items):
        self.parent = parent
        self.selected = None
        content = urwid.SimpleListWalker([ClickableText(('menuitem',text)) for text in items])
        for wid in content:
            urwid.connect_signal(wid, 'click', self.onClick)

        self.listBox = urwid.ListBox(content)
        menubox = urwid.LineBox(urwid.BoxAdapter(self.listBox,len(items)))
        urwid.WidgetWrap.__init__(self,menubox)

    def getValue(self):
        return self.selected
   
    def keypress(self, size, key):
        if key=='up':
            if self.listBox.get_focus()[1] == 0:
                self.parent.keypress(size, key)
        elif key=='left' or key=='right':
            self.parent.keypress(size,'up')
            self.parent.keypress(size,key)
        return super(MenuBox,self).keypress(size,key)
    
    def mouse_event(self, size, event, button, x, y, focus):
        if button == 3:
            self.parent.keypress(size,'up')
            return True
        return super(MenuBox,self).mouse_event(size, event, button, x, y, focus)

    def onClick(self, wid):
        self.selected = wid.getValue()
        self._emit('click')

class Menu(urwid.WidgetWrap):

    def __init__(self,loop, x_orig=0):
        """Menu widget
        @param loop: main loop of urwid
        @param x_orig: absolute start of the abscissa
        """
        self.loop = loop
        self.menu_keys = []
        self.menu = {}
        self.x_orig = x_orig
        self.shortcuts = {} #keyboard shortcuts
        self.save_bottom = None
        col_rol = ColumnsRoller()
        urwid.WidgetWrap.__init__(self, urwid.AttrMap(col_rol,'menubar'))
    
    def selectable(self):
        return True

    def getMenuSize(self):
        """return the current number of categories in this menu"""
        return len(self.menu_keys)
   
    def setOrigX(self, orig_x):
        self.x_orig = orig_x

    def __buildOverlay(self,menu_key,columns):
        """Build the overlay menu which show menuitems
        @param menu_key: name of the category
        @colums: column number where the menubox must be displayed"""
        max_len = 0
        for item in self.menu[menu_key]:
            if len(item[0]) > max_len:
                max_len = len(item[0])

        self.save_bottom = self.loop.widget
        menu_box = MenuBox(self,[item[0] for item in self.menu[menu_key]])
        urwid.connect_signal(menu_box, 'click', self.onItemClick)
        
        self.loop.widget = urwid.Overlay(urwid.AttrMap(menu_box,'menubar'),self.save_bottom,('fixed left', columns),max_len+2,('fixed top',1),None) 

    def keypress(self, size, key):
        if key == 'down':
            key = 'enter'
        elif key == 'up':
            if  self.save_bottom:
                self.loop.widget = self.save_bottom
                self.save_bottom = None
            
        return self._w.base_widget.keypress(size, key)
    
    def checkShortcuts(self, key):
        for shortcut in self.shortcuts.keys():
            if key == shortcut:
                category, item, callback = self.shortcuts[shortcut]
                callback((category, item))
        return key

    def addMenu(self, category, item, callback, shortcut=None):
        """Add a menu item, create the category if new
        @param category: category of the menu (e.g. File/Edit)
        @param item: menu item (e.g. new/close/about)
        @callback: method to call when item is selected"""
        if not category in self.menu.keys():
            self.menu_keys.append(category)
            self.menu[category] = []
            button = CustomButton(('menubar',category), self.onCategoryClick,
                                   left_border = ('menubar',"[ "),
                                   right_border = ('menubar'," ]"))
            self._w.base_widget.addWidget(button,button.getSize())
        self.menu[category].append((item, callback))
        if shortcut:
            assert(shortcut not in self.shortcuts.keys())
            self.shortcuts[shortcut] = (category, item, callback)

    def onItemClick(self, widget):
        category = self._w.base_widget.getSelected().get_label()
        item = widget.getValue()
        callback = None
        for menu_item in self.menu[category]:
            if item == menu_item[0]:
                callback = menu_item[1]
                break
        if callback:
            self.keypress(None,'up')
            callback((category, item))
    
    def onCategoryClick(self, button):
        self.__buildOverlay(button.get_label(),
                            self.x_orig + self._w.base_widget.getStartCol(button)) 
        

class MenuRoller(urwid.WidgetWrap):

    def __init__(self,menus_list):
        """Create a MenuRoller
        @param menus_list: list of tuple with (name, Menu_instance), name can be None
        """
        assert (menus_list)
        self.selected = 0
        self.name_list = []
        self.menus = {}
             
        self.columns = urwid.Columns([urwid.Text(''),urwid.Text('')]) 
        urwid.WidgetWrap.__init__(self, self.columns)
        
        for menu_tuple in menus_list:
            name,menu = menu_tuple
            self.addMenu(name, menu)

    def __showSelected(self):
        """show menu selected"""
        name_txt = u'\u21c9 '+self.name_list[self.selected]+u' \u21c7 '
        current_name = ClickableText(name_txt) 
        name_len = len(name_txt)
        current_menu = self.menus[self.name_list[self.selected]]
        current_menu.setOrigX(name_len)
        self.columns.widget_list[0] = current_name
        self.columns.column_types[0]=('fixed', name_len)
        self.columns.widget_list[1] = current_menu

    def keypress(self, size, key):
        if key=='up':
            if self.columns.get_focus_column()==0 and self.selected > 0:
                self.selected -= 1
                self.__showSelected()
        elif key=='down':
            if self.columns.get_focus_column()==0 and self.selected < len(self.name_list)-1:
                self.selected += 1
                self.__showSelected()
        elif key=='right':
            if self.columns.get_focus_column()==0 and \
                (isinstance(self.columns.widget_list[1], urwid.Text) or \
                self.menus[self.name_list[self.selected]].getMenuSize()==0):
                return #if we have no menu or the menu is empty, we don't go the right column

        return super(MenuRoller, self).keypress(size, key)

    def addMenu(self, name_param, menu):
        name = name_param or ''
        if name not in self.name_list:
            self.name_list.append(name)
        self.menus[name] = menu
        if self.name_list[self.selected] == name:
            self.__showSelected() #if we are on the menu, we update it

    def removeMenu(self, name):
        if name in self.name_list:
            self.name_list.remove(name)
        if name in self.menus.keys():
            del self.menus[name]
        self.selected = 0
        self.__showSelected()

    def checkShortcuts(self, key):
        for menu in self.name_list:
            key = self.menus[menu].checkShortcuts(key)
        return key
        

## DIALOGS ##

class GenericDialog(urwid.WidgetWrap):

    def __init__(self, widgets_lst, title, style=[], **kwargs):
        frame_header = urwid.AttrMap(urwid.Text(title,'center'),'title')
       
        buttons = None

        if "OK/CANCEL" in style:
            cancel_arg = [kwargs['cancel_value']] if kwargs.has_key('cancel_value') else []
            ok_arg = [kwargs['ok_value']] if kwargs.has_key('ok_value') else []
            buttons = [urwid.Button(_("Cancel"), kwargs['cancel_cb'], *cancel_arg),
                      urwid.Button(_("Ok"), kwargs['ok_cb'], *ok_arg)]
        elif "YES/NO" in style:
            yes_arg = [kwargs['yes_value']] if kwargs.has_key('yes_value') else []
            no_arg = [kwargs['no_value']] if kwargs.has_key('no_value') else []
            buttons = [urwid.Button(_("Yes"), kwargs['yes_cb'], *yes_arg),
                      urwid.Button(_("No"), kwargs['no_cb'], *no_arg)]
        if "OK" in style:
            ok_arg = [kwargs['ok_value']] if kwargs.has_key('ok_value') else []
            buttons = [urwid.Button(_("Ok"), kwargs['ok_cb'], *ok_arg)]
        if buttons:
            buttons_flow = urwid.GridFlow(buttons, max([len(button.get_label()) for button in buttons])+4, 1, 1, 'center')
        body_content = urwid.SimpleListWalker(widgets_lst)
        frame_body = urwid.ListBox(body_content)
        frame = FocusFrame(frame_body, frame_header, buttons_flow if buttons else None, 'footer' if buttons else 'body')
        decorated_frame = urwid.LineBox(frame)
        urwid.WidgetWrap.__init__(self, decorated_frame)



class InputDialog(GenericDialog):
    """Dialog with an edit box"""

    def __init__(self, title, instrucions, style=['OK/CANCEL'], default_txt = '', **kwargs):
        instr_wid = urwid.Text(instrucions+':')
        edit_box = AdvancedEdit(edit_text=default_txt)
        GenericDialog.__init__(self, [instr_wid,edit_box], title, style, ok_value=edit_box, **kwargs)
        self._w.base_widget.set_focus('body')

class ConfirmDialog(GenericDialog):
    """Dialog with buttons for confirm or cancel an action"""

    def __init__(self, title, style=['YES/NO'], **kwargs):
        GenericDialog.__init__(self, [], title, style, **kwargs)

class Alert(GenericDialog):
    """Dialog with just a message and a OK button"""

    def __init__(self, title, message, style=['OK'], **kwargs):
        GenericDialog.__init__(self, [urwid.Text(message, 'center')], title, style, ok_value=None, **kwargs)

## CONTAINERS ##

class ColumnsRoller(urwid.FlowWidget):
    
    def __init__(self, widget_list = None, focus_column=0):
        self.widget_list = widget_list or []
        self.focus_column = focus_column
        self.__start = 0
        self.__next = False

    def addWidget(self, widget, width):
        self.widget_list.append((width,widget))
        if len(self.widget_list) == 1:
            self.set_focus(0)

    def getStartCol(self, widget):
        """Return the column of the left corner of the widget"""
        start_col = 0
        for wid in self.widget_list[self.__start:]:
            if wid[1] == widget:
                return start_col
            start_col+=wid[0]
        return None

    def selectable(self):
        try:
            return self.widget_list[self.focus_column][1].selectable()
        except IndexError:
            return False
    
    def keypress(self, size, key):
        if key=='left':
            if self.focus_column>0:
                self.focus_column-=1
                self._invalidate()
                return
        if key=='right':
            if self.focus_column<len(self.widget_list)-1:
                self.focus_column+=1
                self._invalidate()
                return
        if self.focus_column<len(self.widget_list):
            return self.widget_list[self.focus_column][1].keypress(size,key)
        return key

    def getSelected(self):
        """Return selected widget"""
        return self.widget_list[self.focus_column][1]

    def set_focus(self, idx):
        if idx>len(self.widget_list)-1:
            idx = len(self.widget_list)-1
        self.focus_column = idx

    def rows(self,size,focus=False):
        return 1

    def __calculate_limits(self, size):
        (maxcol,) = size
        _prev = _next = False
        start_wid = 0
        end_wid = len(self.widget_list)-1
        
        total_wid = sum([w[0] for w in self.widget_list])
        while total_wid > maxcol:
            if self.focus_column == end_wid:
                if not _prev:
                    total_wid+=1
                    _prev = True
                total_wid-=self.widget_list[start_wid][0]
                start_wid+=1
            else:
                if not _next:
                    total_wid+=1
                    _next = True
                total_wid-=self.widget_list[end_wid][0]
                end_wid-=1
        
        cols_left = maxcol - total_wid
        self.__start = start_wid #we need to keep it for getStartCol
        return _prev,_next,start_wid,end_wid,cols_left
        

    def mouse_event(self, size, event, button, x, y, focus):
        (maxcol,)=size

        if is_mouse_press(event) and button == 1:
            _prev,_next,start_wid,end_wid,cols_left = self.__calculate_limits(size)
            if x==0 and _prev:
                self.keypress(size,'left')
                return True
            if x==maxcol-1 and _next:
                self.keypress(size,'right')
                return True
            
            current_pos = 1 if _prev else 0
            idx = 0
            while current_pos<x and idx<len(self.widget_list):
                width,widget = self.widget_list[idx]
                if x<=current_pos+width:
                    self.focus_column = idx
                    self._invalidate()
                    if not hasattr(widget,'mouse_event'):
                        return False
                    return widget.mouse_event((width,0), event, button, 
                        x-current_pos, 0, focus)

                current_pos+=self.widget_list[idx][0]
                idx+=1
        
        return False
    
    def render(self, size, focus=False):
        if not self.widget_list:
            return SolidCanvas(" ", size[0], 1)

        _prev,_next,start_wid,end_wid,cols_left = self.__calculate_limits(size)
        
        idx=start_wid
        render = []

        for width,widget in self.widget_list[start_wid:end_wid+1]:
            _focus = idx == self.focus_column and focus
            render.append((widget.render((width,),_focus),False,_focus,width))
            idx+=1
        if _prev:
            render.insert(0,(urwid.Text([u"◀"]).render((1,),False),False,False,1))
        if _next:
            render.append((urwid.Text([u"▶"],align='right').render((1+cols_left,),False),False,False,1+cols_left))
        else:
            render.append((urwid.SolidCanvas(" "*cols_left, size[0], 1),False,False,cols_left))

        return urwid.CanvasJoin(render)


class FocusFrame(urwid.Frame):
    """Frame which manage 'tab' key"""

    def keypress(self, size, key):
        ret = urwid.Frame.keypress(self, size, key)
        if not ret:
            return
        
        if key == 'tab':
            focus_list = ('header','body','footer')
            focus_idx = focus_list.index(self.focus_part)
            for i in range(2):
                focus_idx = (focus_idx + 1) % len(focus_list)
                focus_name = focus_list[focus_idx]
                widget = getattr(self,'_'+focus_name)
                if widget!=None and widget.selectable():
                    self.set_focus(focus_name)

        return ret 

class TabsContainer(urwid.WidgetWrap):
    signals = ['click']

    def __init__(self):
        self._current_tab = None
        self._buttons_cont = ColumnsRoller()
        self.tabs = []
        self.__frame = FocusFrame(urwid.Filler(urwid.Text('')),urwid.Pile([self._buttons_cont,urwid.Divider(u"─")]))
        urwid.WidgetWrap.__init__(self, self.__frame)

    def keypress(self, size, key):
        if key=='tab':
            self._w.keypress(size,key)
            return
        return self._w.keypress(size,key)

    def __buttonClicked(self, button, invisible=False):
        """Called when a button on the tab is changed,
        change the page
        @param button: button clicked
        @param invisible: emit signal only if False"""
        tab_name = button.get_label()
        for tab in self.tabs:
            if tab[0] == tab_name:
                break
        if tab[0] != tab_name:
            error(_("INTERNAL ERROR: Tab not found"))
            assert(False)
        self.__frame.body = tab[1]
        button.set_label(('title',button.get_label()))
        if self._current_tab:
            self._current_tab.set_label(self._current_tab.get_label())
        self._current_tab = button
        if not invisible:
            self._emit('click')

    def __appendButton(self, name):
        """Append a button to the frame header,
        and link it to the page change method"""
        button = CustomButton(name, self.__buttonClicked, left_border = '', right_border=' | ')
        self._buttons_cont.addWidget(button, button.getSize())
        if len(self._buttons_cont.widget_list) == 1:
            #first button: we set the focus and the body
            self._buttons_cont.set_focus(0)
            self.__buttonClicked(button,True)

    def addTab(self,name,content=[]):
        """Add a page to the container
        @param name: name of the page (what appear on the tab)
        @param content: content of the page
        @return: ListBox (content of the page)"""
        listbox = urwid.ListBox(urwid.SimpleListWalker(content))
        self.tabs.append([name,listbox])
        self.__appendButton(name)
        return listbox

    def addFooter(self, widget):
        """Add a widget on the bottom of the tab (will be displayed on all pages)
        @param widget: FlowWidget"""
        self._w.footer = widget
    

## DECORATORS ##
class LabelLine(urwid.LineBox):
    """Like LineBox, but with a Label centered in the top line"""

    def __init__(self, original_widget, label_widget):
        urwid.LineBox.__init__(self, original_widget)
        top_columns = self._w.widget_list[0]
        top_columns.widget_list[1] = label_widget

class VerticalSeparator(urwid.WidgetDecoration, urwid.WidgetWrap):
    def __init__(self, original_widget, left_char = u"│", right_char = ''):
        """Draw a separator on left and/or right of original_widget."""
        
        widgets = [original_widget]
        if left_char:
            widgets.insert(0, ('fixed', 1, urwid.SolidFill(left_char)))
        if right_char:
            widgets.append(('fixed', 1, urwid.SolidFill(right_char)))
        columns = urwid.Columns(widgets, box_columns = [0,2], focus_column = 1)
        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, columns)

        
