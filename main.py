from database_manager.DatabaseManager import DatabaseManager

from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import NumericProperty
from kivy.properties import StringProperty


class MyScreenManager(ScreenManager):
    account_id = NumericProperty(None)
    label_id = NumericProperty(None)

    def label_clicked(self, label_id):
        self.label_id = label_id
        destination_screen = self.current_screen.name
        print(self.current_screen.name)
        if self.current_screen.name == 'expenses_list_screen':
            destination_screen = 'expense_details_screen'
        else:
            pass
        self.change_screen(destination_screen)

    def change_screen(self, destination_screen='login_screen'):
        self.current = destination_screen

    def logout(self):
        self.account_id = None
        self.change_screen()
        print(self.account_id)


class MenuScreen(Screen):
    pass


class LoginScreen(Screen):

    def validate_input(self, username, password):
        return self.validate_password(password) and self.validate_username(username)

    def validate_username(self, username):
        return username != ''

    def validate_password(self, password):
        return len(password) >= 5

    def check_in_database(self, username, password):
        db_manager = App.get_running_app().db_manager
        print('jeah')
        account_id = db_manager.get_account(username, password)
        print(account_id)
        return account_id

    def clear_input_fields(self, *fields):
        for field in fields:
            field.text = ''

    def show_error(self, message):
        pass

    def login(self, username_field, password_field):
        username = username_field.text
        password = password_field.text

        self.clear_input_fields(username_field, password_field)

        if self.validate_input(username, password):
            account_id = self.check_in_database(username, password)
            if account_id != {}:
                print('logged in')
                App.get_running_app().account_id = account_id
                App.get_running_app().root.current = 'menu_screen'


class CreateAccountScreen(Screen):
    pass


class ExpensesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        for i in range(100):
            box.add_widget(SelectableLabel(text='TestItem', label_id=i))


class ExpenseDetailsScreen(Screen):
    def on_pre_enter(self, *args):
        pass


class SelectableLabel(Label):
    label_id = NumericProperty()

    def __init__(self, **kwargs):
        super(SelectableLabel, self).__init__(**kwargs)
        self.label_id = kwargs['label_id']

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            app = App.get_running_app()
            app.root.label_clicked(self.label_id)
            print('label id: ', self.label_id)


class ScrollableLabel(ScrollView):
    text = StringProperty('')


class MyApp(App):
    db_manager = DatabaseManager()

    def build(self):
        self.title = "Menedżer wydatków"
        return MyScreenManager()


if __name__ == "__main__":
    MyApp().run()
