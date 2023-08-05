## Very, very experimental. Do NOT USE.
from .         import fmForm
from .wgwidget import NotEnoughSpaceForWidget
from .         import wgNMenuDisplay


class FormMultiPage(fmForm.FormBaseNew):
    def __init__(self, *args, **keywords):
        super(FormMultiPage, self).__init__(*args, **keywords)
        self.switch_page(0)
    
    def add_widget_intelligent(self, *args, **keywords):
        try:
            return self.add_widget(*args, **keywords)
        except NotEnoughSpaceForWidget:
            self.add_page()
            return self.add_widget(*args, **keywords)
            
    
    def _clear_all_widgets(self,):
        super(FormMultiPage, self)._clear_all_widgets()
        self._pages__     = [ [],]
        self._active_page = 0
        self.switch_page(self._active_page, display=False)
    
    def switch_page(self, page, display=True):
        self._widgets__ = self._pages__[page]
        self._active_page = page
        self.editw = 0
        if display:
            self.display(clear=True)
    
    def add_page(self):
        self._pages__.append([])
        page_number   = len(self._pages__)-1
        self.nextrely = self.DEFAULT_NEXTRELY
        self.nextrelx = self.DEFAULT_X_OFFSET
        self.switch_page(page_number, display=False)
        return page_number
    
    def find_next_editable(self, *args):
        if not self.editw == len(self._widgets__):
            value_changed = False
            if not self.cycle_widgets:
                r = list(range(self.editw+1, len(self._widgets__)))
            else:
                r = list(range(self.editw+1, len(self._widgets__))) + list(range(0, self.editw))
            for n in r:
                if self._widgets__[n].editable and not self._widgets__[n].hidden: 
                    self.editw = n
                    value_changed = True
                    break
            if not value_changed:
                if self._active_page < len(self._pages__)-1:
                    self.switch_page(self._active_page + 1)
        self.display()
    
    
    def find_previous_editable(self, *args):
        if self.editw == 0:
            if self._active_page > 0:
                self.switch_page(self._active_page-1)
        
        if not self.editw == 0:     
            # remember that xrange does not return the 'last' value,
            # so go to -1, not 0! (fence post error in reverse)
            for n in range(self.editw-1, -1, -1 ):
                if self._widgets__[n].editable and not self._widgets__[n].hidden: 
                    self.editw = n
                    break
                    
                    
class FormMultiPageAction(FormMultiPage):
    CANCEL_BUTTON_BR_OFFSET = (2, 12)
    OK_BUTTON_TEXT          = "OK"
    CANCEL_BUTTON_TEXT      = "Cancel"
    
    def on_ok(self):
        pass
    
    def on_cancel(self):
        pass
    
    def pre_edit_loop(self):
        self._page_for_buttons = len(self._pages__)-1
        self.switch_page(self._page_for_buttons)
        
        # Add ok and cancel buttons. Will remove later
        tmp_rely, tmp_relx = self.nextrely, self.nextrelx
        
        c_button_text = self.CANCEL_BUTTON_TEXT
        cmy, cmx = self.curses_pad.getmaxyx()
        cmy -= self.__class__.CANCEL_BUTTON_BR_OFFSET[0]
        cmx -= len(c_button_text)+self.__class__.CANCEL_BUTTON_BR_OFFSET[1]
        self.c_button = self.add_widget(self.__class__.OKBUTTON_TYPE, name=c_button_text, rely=cmy, relx=cmx, use_max_space=True)
        self._c_button_postion = len(self._widgets__)-1
        self.c_button.update()
        
        my, mx = self.curses_pad.getmaxyx()
        ok_button_text = self.OK_BUTTON_TEXT
        my -= self.__class__.OK_BUTTON_BR_OFFSET[0]
        mx -= len(ok_button_text)+self.__class__.OK_BUTTON_BR_OFFSET[1]
        self.ok_button = self.add_widget(self.__class__.OKBUTTON_TYPE, name=ok_button_text, rely=my, relx=mx, use_max_space=True)
        self._ok_button_postion = len(self._widgets__)-1
        # End add buttons
        self.nextrely, self.nextrelx = tmp_rely, tmp_relx
        self.switch_page(0)
        
    def _during_edit_loop(self):
        if self.ok_button.value or self.c_button.value:
            self.editing = False
    
        if self.ok_button.value:
            self.ok_button.value = False
            self.edit_return_value = self.on_ok()
        elif self.c_button.value:
            self.c_button.value = False
            self.edit_return_value = self.on_cancel()
    
    def post_edit_loop(self):
        self.switch_page(self._page_for_buttons)
        self.ok_button.destroy()
        self.c_button.destroy()
        del self._widgets__[self._ok_button_postion]
        del self.ok_button
        del self._widgets__[self._c_button_postion]
        del self.c_button
        #self.nextrely, self.nextrelx = tmp_rely, tmp_relx
        self.display()
        self.editing = False
        
        return self.edit_return_value


class FormMultiPageWithMenus(fmForm.FormBaseNew):
    def __init__(self, *args, **keywords):
        super(FormMultiPageWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()

class FormMultiPageActionWithMenus(FormMultiPageAction, wgNMenuDisplay.HasMenus):
    def __init__(self, *args, **keywords):
        super(FormMultiPageActionWithMenus, self).__init__(*args, **keywords)
        self.initialize_menus()
