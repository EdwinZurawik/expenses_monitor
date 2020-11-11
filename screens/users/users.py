from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from screens.gui_elements import SelectableListItem


class UsersListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        users_list = self.get_users_list()
        for user in users_list:
            box.add_widget(SelectableListItem(text=f"{user['username']}", item_id=user['user_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_users_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę użytkowników')
        users_list = db_manager.get_all_users(app.root.account_id)
        print(users_list)
        return users_list


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


class EditUserScreen(Screen):
    user = ObjectProperty(None)

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.user = self.load_user(App.get_running_app().root.item_id)
        self.populate_fields()

    def populate_fields(self):
        self.ids.name.text = self.user['username']

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

    def load_user(self, user_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać użytkownika')
        user = db_manager.get_user(user_id)
        print(user)
        return user

    def check_in_database(self, name):
        db_manager = App.get_running_app().db_manager
        print('Próbuję dodać użytkownika')
        user_id = db_manager.edit_user(self.user['user_id'], name)
        return user_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''

    def show_message(self, message):
        self.ids.message.text = message

    def compare_changes(self, name):
        self.clear_message()
        print('Comparing changes in user:')
        print(self.user)
        has_changed = False
        if self.user['username'] != name:
            has_changed = True
            print(self.user['username'], '!=', name)
        return has_changed

    def update_user(self, name_field):
        name = name_field.text

        if self.validate_input(name) and self.compare_changes(name):
            errors = self.check_in_database(name)
            if errors is None:
                print('user succesfully updated')
                self.show_message(f'Zmiany dla użytkownika {name} zostały zapisane.')
                self.user = self.load_user(self.user['user_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')
