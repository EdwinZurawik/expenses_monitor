import re

from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.list import OneLineListItem
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.picker import MDDatePicker
from kivymd.uix.textfield import MDTextField, MDTextFieldRect
from kivymd.uix.toolbar import MDToolbar


class CenteredTextField(MDTextField):
    pass


class CenteredMultilineTextField(MDTextFieldRect):
    pass


class CenteredDateTextField(CenteredTextField):
    selected_date = ObjectProperty("")

    def get_date(self, date):
        self.selected_date = str(date)

    def show_date_picker(self):
        date_dialog = MDDatePicker(callback=self.get_date)
        date_dialog.open()


class CenteredDropdownTextField(CenteredTextField):
    selected_item = ObjectProperty("")
    menu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("hello")
        self.menu = MDDropdownMenu(
            caller=self,
            items=[{"text": "1", "id": 1}, {"text": "2", "id": 2}, {"text": "3", "id": 3}],
            width_mult=4,
        )
        self.menu.bind(on_release=self.menu_callback)

    def menu_callback(self, menu_instance, menu_item):
        print("hello2")
        self.selected_item = menu_item.text
        menu_instance.dismiss()


class CenteredButton(MDRaisedButton):
    pass


class CenteredErrorLabel(MDLabel):
    pass


class CenteredLabel(MDLabel):
    def update(self, text):
        self.text = text


class VerticalBoxLayout(MDBoxLayout):
    pass


class HorizontalBoxLayout(MDBoxLayout):
    pass


class TopToolbar(MDToolbar):
    pass


class ContentNavigationDrawer(BoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class SelectableListItem(OneLineListItem):
    item_id = NumericProperty()

    def __init__(self, **kwargs):
        super(SelectableListItem, self).__init__(**kwargs)
        self.item_id = kwargs['item_id']

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            app.root.label_clicked(self.item_id)
            print('item id: ', self.item_id)


class FloatInput(CenteredTextField):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class IntegerInput(CenteredTextField):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(IntegerInput, self).insert_text(s, from_undo=from_undo)


class ButtonWithData(Button):
    button_data = ObjectProperty({'text': '', 'id': 0})

    def on_button_data(self, *args):
        self.text = self.button_data['text']
