import re

from kivy.app import App
from kivy.uix.screenmanager import Screen


class CreateAccountScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def print_confirmation(self):
        self.show_message('Konto zostało utworzone')

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, username, password, email):
        return self.validate_username(username) \
               and self.validate_password(password) \
               and self.validate_email(email)

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

    def validate_email(self, email):
        valid = False
        email_regex = re.compile(r'([a-zA-Z0-9_]+@[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+)')
        email_match = re.search(email_regex, email)
        if len(email) == 0:
            self.show_message('Pole "Adres e-mail" nie może być puste.')
        elif email_match is None or email_match.group(1) != email:
            self.show_message('Nieprawidłowy adres e-mail.')
        else:
            valid = True
        return valid

    def check_in_database(self, username, password, email):
        db_manager = App.get_running_app().db_manager
        print('jeah')
        account_id = db_manager.create_account(username, password, email)
        print(account_id)
        return account_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.username.text = ''
        self.ids.password.text = ''
        self.ids.email.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def create_account(self, username_field, password_field, email_field):
        username = username_field.text
        password = password_field.text
        email = email_field.text

        if self.validate_input(username, password, email):
            account_id = self.check_in_database(username, password, email)
            if account_id != {}:
                self.clear_input_fields()
                self.print_confirmation()
                print('account created')

