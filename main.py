from kivy.properties import NumericProperty
from kivy.properties import StringProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp

from database_manager.DatabaseManager import DatabaseManager


class MyScreenManager(ScreenManager):
    account_id = NumericProperty(None)
    item_id = NumericProperty(None)

    def label_clicked(self, item_id):
        self.item_id = item_id
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


class CustomDropdown(DropDown):
    pass


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class MyApp(MDApp):
    db_manager = DatabaseManager()

    def build(self):
        self.title = "Menedżer wydatków"
        return MyScreenManager()


if __name__ == "__main__":
    MyApp().run()
