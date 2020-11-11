from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from screens.gui_elements import SelectableListItem


class PaymentMethodsListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        payment_methods_list = self.get_payment_methods_list()
        for payment_method in payment_methods_list:
            box.add_widget(SelectableListItem(text=f"{payment_method['name']}",
                                           item_id=payment_method['payment_method_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_payment_methods_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę metod płatności')
        payment_methods_list = db_manager.get_all_payment_methods(app.root.account_id)
        print(payment_methods_list)
        return payment_methods_list


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


class EditPaymentMethodScreen(Screen):
    payment_method = ObjectProperty(None)

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.payment_method = self.load_payment_method(App.get_running_app().root.item_id)
        self.populate_fields()

    def populate_fields(self):
        self.ids.name.text = self.payment_method['name']

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

    def load_payment_method(self, payment_method_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać metodę płatności')
        payment_method = db_manager.get_payment_method(payment_method_id)
        print(payment_method)
        return payment_method

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        print('Próbuję dodać metodę płatności')
        payment_method_id = db_manager.edit_payment_method(self.payment_method['payment_method_id'], name)
        return payment_method_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def compare_changes(self, name):
        self.clear_message()
        print('Comparing changes in payment method:')
        print(self.payment_method)
        has_changed = False
        if self.payment_method['name'] != name:
            has_changed = True
            print(self.payment_method['name'], '!=', name)
        return has_changed

    def show_message(self, message):
        self.ids.message.text = message

    def update_payment_method(self, name_field):
        name = name_field.text

        if self.validate_input(name) and self.compare_changes(name):
            errors = self.check_in_database(name)
            if errors is None:
                print('payment method succesfully updated')
                self.show_message(f'Zmiany dla metody płatności {name} zostały zapisane.')
                self.payment_method = self.load_payment_method(self.payment_method['payment_method_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')
