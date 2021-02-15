from kivy.app import App
from kivy.uix.screenmanager import Screen


class LoginScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, username, password):
        return self.validate_username(username) and self.validate_password(password)

    def validate_username(self, username):
        valid = False
        if len(username) < 3:
            self.show_message('Nazwa konta powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_password(self, password):
        valid = False
        if len(password) < 5:
            self.show_message('Hasło powinno składać się z co najmniej 5 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, username, password):
        db_manager = App.get_running_app().db_manager
        print('jeah')
        account = db_manager.get_account(username, password)
        print(account)
        if account == {}:
            account_id = account
        else:
            account_id = account['account_id']
        return account_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.username.text = ''
        self.ids.password.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def login(self, username_field, password_field):
        username = username_field.text
        password = password_field.text

        if self.validate_input(username, password):
            account_id = self.check_in_database(username, password)
            if account_id != {}:
                print('logged in')
                App.get_running_app().root.account_id = account_id
                App.get_running_app().root.current = 'menu_screen'
            else:
                self.show_message('Nieprawidłowa nazwa użytkownika lub hasło.')

