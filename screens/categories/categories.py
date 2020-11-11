from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from screens.gui_elements import SelectableListItem


class CategoriesListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        categories_list = self.get_categories_list()
        for category in categories_list:
            box.add_widget(SelectableListItem(text=f"{category['name']}", item_id=category['category_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_categories_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę kategorii')
        categories_list = db_manager.get_all_categories(app.root.account_id)
        print(categories_list)
        return categories_list


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


class EditCategoryScreen(Screen):
    category = ObjectProperty(None)

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.category = self.load_category(App.get_running_app().root.item_id)
        self.populate_fields()

    def populate_fields(self):
        self.ids.name.text = self.category['name']
        self.ids.description.text = self.category['description']
        if self.category['category_type_id'] == 1:
            self.ids.expense_category.state = 'down'
            self.ids.income_category.state = 'normal'
        else:
            self.ids.expense_category.state = 'normal'
            self.ids.income_category.state = 'down'

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

    def load_category(self, category_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać kategorię')
        category = db_manager.get_category(category_id)
        print(category)
        return category

    def check_in_database(self, name, description, expense_category):
        db_manager = App.get_running_app().db_manager
        category_type_id = 1 if expense_category.state == 'down' else 2
        print('Próbuję dodać kategorię')
        print(self.category['category_id'], name, description, category_type_id)
        category_id = db_manager.edit_category(self.category['category_id'], name, description, category_type_id)
        return category_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.expense_category.state = 'down'
        self.ids.income_category.state = 'normal'

    def show_message(self, message):
        self.ids.message.text = message

    def compare_changes(self, name, description, expense_category, income_category):
        self.clear_message()
        print('Comparing changes in category:')
        print(self.category)
        has_changed = False
        if self.category['name'] != name:
            has_changed = True
            print(self.category['name'], '!=', name)
        elif self.category['description'] != description:
            has_changed = True
            print(self.category['description'], '!=', description)
        elif self.category['category_type_id'] == 1 \
                and (expense_category.state == 'normal' or income_category.state == 'down'):
            has_changed = True
            print('category_type_id has changed')
        elif self.category['category_type_id'] == 2 \
                and (expense_category.state == 'down' or income_category.state == 'normal'):
            has_changed = True
            print('category_type_id has changed')
        return has_changed

    def update_category(self, name_field, description_field, expense_category, income_category):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, expense_category, income_category) \
                and self.compare_changes(name, description, expense_category, income_category):
            errors = self.check_in_database(name, description, expense_category)
            if errors is None:
                print('category succesfully updated')
                self.show_message(f'Zmiany dla kategorii {name} zostały zapisane.')
                self.category = self.load_category(self.category['category_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')
