import re

from kivymd.app import MDApp
from kivy.properties import NumericProperty, ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from database_manager.DatabaseManager import DatabaseManager


class MyScreenManager(ScreenManager):
    account_id = NumericProperty(None)
    label_id = NumericProperty(None)

    def label_clicked(self, label_id):
        self.label_id = label_id
        destination_screen = self.current_screen.name
        print(self.current_screen.name)
        if self.current_screen.name == 'expenses_list_screen':
            destination_screen = 'expense_details_screen'
        elif self.current_screen.name == 'incomes_list_screen':
            destination_screen = 'income_details_screen'
        elif self.current_screen.name == 'users_list_screen':
            destination_screen = 'edit_user_screen'
        elif self.current_screen.name == 'payment_methods_list_screen':
            destination_screen = 'edit_payment_method_screen'
        elif self.current_screen.name == 'categories_list_screen':
            destination_screen = 'edit_category_screen'
        elif self.current_screen.name == 'groups_list_screen':
            destination_screen = 'edit_group_screen'
        else:
            pass
        self.change_screen(destination_screen)

    def change_screen(self, destination_screen='login_screen'):
        self.current = destination_screen

    def logout(self):
        self.account_id = 0
        self.change_screen()
        print(self.account_id)


class MenuScreen(Screen):
    pass


class ButtonWithData(Button):
    button_data = ObjectProperty({'text': '', 'id': 0})

    def on_button_data(self, *args):
        self.text = self.button_data['text']


class FloatInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        if '.' in self.text:
            s = re.sub(pat, '', substring)
        else:
            s = '.'.join([re.sub(pat, '', s) for s in substring.split('.', 1)])
        return super(FloatInput, self).insert_text(s, from_undo=from_undo)


class IntegerInput(TextInput):
    pat = re.compile('[^0-9]')

    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(IntegerInput, self).insert_text(s, from_undo=from_undo)


class CustomDropdown(DropDown):
    pass


class SelectableLabel(Label):
    label_id = NumericProperty()

    def __init__(self, **kwargs):
        super(SelectableLabel, self).__init__(**kwargs)
        self.label_id = kwargs['label_id']

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = MDApp.get_running_app()
            app.root.label_clicked(self.label_id)
            print('label id: ', self.label_id)


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class MyApp(MDApp):
    db_manager = DatabaseManager()

    def build(self):
        self.title = "Menedżer wydatków"
        return MyScreenManager()


if __name__ == "__main__":
    MyApp().run()
