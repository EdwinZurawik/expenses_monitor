import re

from kivy.uix.dropdown import DropDown

from database_manager.DatabaseManager import DatabaseManager
from configuration_data import ConfigurationData
import mysql.connector

from kivy.app import App

from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.button import Button


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
        self.account_id = 0
        self.change_screen()
        print(self.account_id)


class MenuScreen(Screen):
    pass


class ButtonWithId(Button):
    button_data = ObjectProperty(None)


class CreateExpenseScreen(Screen):
    payer_id = NumericProperty(None)

    def on_enter(self, *args):
        pass

    def add_payers_dropdown(self):
        payers_dropdown = DropDown()
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()

        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithId(text=user['username'],
                               size_hint_y=None,
                               height='30',
                               button_data=user)
            btn.bind(on_release=lambda btn: payers_dropdown.select(btn.button_data))
            payers_dropdown.add_widget(btn)
        payers_btn = self.ids.payers_btn
        payers_btn.bind(on_release=payers_dropdown.open)
        payers_dropdown.bind(on_select=lambda instance, x: setattr(payers_btn, 'text', x['username']))

    def populate_dropdown(self):
        self.add_payers_dropdown()

    def set_payer_id(self, button_id): # jak przekazać id płacącego?
        self.payer_id = button_id
        print(self.payer_id)


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


class CustomDropdown(DropDown):
    pass


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


class ExpensesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        for i in range(100):
            box.add_widget(SelectableLabel(text='TestItem', label_id=i))


class ExpenseDetailsScreen(Screen):
    def on_pre_enter(self, *args):
        pass


class CreateCategoryScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, description, expense_category, income_category):
        return self.validate_name(name) \
               and self.validate_description(description) \
               and self.validate_type(expense_category, income_category)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa kategorii powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def validate_description(self, description):
        valid = False
        if len(description) > 255:
            self.show_message('Opis nie powinien przekroczyć 255 znaków.')
        else:
            valid = True
        return valid

    def validate_type(self, expense_category, income_category):
        valid = False
        if expense_category.state == 'normal' and income_category.state == 'normal':
            self.show_message('Wybierz typ kategorii.')
        elif expense_category.state == 'down' and income_category.state == 'down':
            self.show_message('Można wybrać tylko jeden typ kategorii.')
        else:
            valid = True
        return valid

    def check_in_database(self, name, description, expense_category):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        category_type_id = 1 if expense_category.state == 'down' else 2
        print('Próbuję dodać kategorię')
        category_id = db_manager.create_category(app.root.account_id, name, description, category_type_id)
        print(app.root.account_id, name, description, category_type_id)
        print(category_id)
        return category_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.expense_category.state = 'down'
        self.ids.income_category.state = 'normal'

    def show_message(self, message):
        self.ids.message.text = message

    def add_category(self, name_field, description_field, expense_category, income_category):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, expense_category, income_category):
            category_id = self.check_in_database(name, description, expense_category)
            if category_id != {}:
                print('category succesfully added')
                self.clear_input_fields()
                self.show_message(f'Kategoria {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class CreateUserScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name):
        return self.validate_name(name)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa użytkownika powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję dodać użytkownika')
        user_id = db_manager.create_user(app.root.account_id, name)
        print(app.root.account_id, name)
        print(user_id)
        return user_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def add_user(self, name_field):
        name = name_field.text

        if self.validate_input(name):
            user_id = self.check_in_database(name)
            if user_id != {}:
                print('user succesfully added')
                self.clear_input_fields()
                self.show_message(f'Użytkownik {name} został dodany.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class CreatePaymentMethodScreen(Screen):

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name):
        return self.validate_name(name)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa metody płatności powinna składać się z co najmniej 3 znaków.')
        else:
            valid = True
        return valid

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję dodać metodę płatności')
        payment_method_id = db_manager.create_payment_method(app.root.account_id, name)
        print(app.root.account_id, name)
        print(payment_method_id)
        return payment_method_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def add_payment_method(self, name_field):
        name = name_field.text

        if self.validate_input(name):
            payment_method_id = self.check_in_database(name)
            if payment_method_id != {}:
                print('payment method succesfully added')
                self.clear_input_fields()
                self.show_message(f'Metoda płatności {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class IpAddressScreen(Screen):
    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, address):
        return self.validate_address(address)

    def validate_address(self, address):
        valid = False
        address_regex = re.compile(r'([0-9]+.[0-9]+.[0-9]+.[0-9]+)')
        address_match = re.search(address_regex, address)
        if address != 'localhost' and (address_match is None or address_match.group(1) != address):
            self.show_message('Błędny format adresu ip (przykładowy adres: 192.168.1.1).')
        else:
            valid = True
        return valid

    def check_in_database(self, address):
        db_manager = App.get_running_app().db_manager

        print(address)
        print('Próbuję dodać połączyć się z bazą')
        ConfigurationData.db_config['host'] = address
        connected = False
        try:
            connection_check = db_manager.connect_to_db()
            connected = connection_check.is_connected()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            db_manager.close_connection()
        print(connected)

        return connected

    def clear_input_fields(self):
        self.clear_message()
        self.ids.address.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def check_connection(self, address_field):
        address = address_field.text
        app = App.get_running_app()

        if self.validate_input(address):
            connected = self.check_in_database(address)
            if connected:
                print('Successfully connected to the database')
                self.show_message(f'Połączono z adresem {address}.')
                app.root.change_screen()
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


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
