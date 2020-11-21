import re

from kivy.app import App
from kivy.properties import ObjectProperty, DictProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen

from screens.gui_elements import SelectableListItem, FloatInput, IntegerInput, ButtonWithData


class GroupsListScreen(Screen):
    def on_pre_enter(self, *args):
        box = self.ids.box
        groups_list = self.get_groups_list()
        for group in groups_list:
            box.add_widget(SelectableListItem(text=f"{group['name']}", item_id=group['group_id']))

    def on_pre_leave(self, *args):
        self.ids.box.clear_widgets()

    def get_groups_list(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        print('Próbuję pobrać listę grup')
        groups_list_all = db_manager.get_all_groups(app.root.account_id)
        groups_list = []
        for group in groups_list_all:
            if not group['is_main_group']:
                groups_list.append(group)
        print(groups_list)
        return groups_list


class CreateGroupScreen(Screen):
    users_dropdowns = DictProperty({})
    highest_id = 0

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def add_user_field(self):
        self.highest_id += 1
        deletebtn = ButtonWithData(text='-', id=f'delete{self.highest_id}')
        userbtn = ButtonWithData(button_data={'text': 'Wybierz', 'id': 0},
                                 id=f'user{self.highest_id}')
        widgets = [userbtn,
                   FloatInput(text='', id=f'amount{self.highest_id}'),
                   IntegerInput(text='', id=f'priority{self.highest_id}'),
                   deletebtn]
        deletebtn.bind(on_release=lambda btn: self.remove_user_field(btn.id))

        for widget in widgets:
            self.ids.box.add_widget(widget)

        new_dropdown = DropDown()
        self.users_dropdowns[f'{self.highest_id}'] = new_dropdown
        self.populate_users_dropdown(str(self.highest_id))
        userbtn.bind(on_release=self.users_dropdowns[str(self.highest_id)].open)
        self.users_dropdowns[str(self.highest_id)].bind(
            on_select=lambda instance, x: setattr(userbtn, 'button_data', x))

    def remove_user_field(self, id):
        id_regex = re.compile(r'([0-9]+)')
        id_match = re.search(id_regex, id)

        names = ['user', 'amount', 'priority', 'delete']

        for i in range(len(names)):
            names[i] = names[i] + str(id_match.group(1))
        box = self.ids.box

        for child in box.children[:]:
            if child.id in names:
                box.remove_widget(child)

        self.users_dropdowns.pop(str(id_match.group(1)))

    def populate_users_dropdown(self, id):

        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        self.users_dropdowns[id].clear_widgets()
        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithData(text=user['username'],
                                 button_data={'text': user['username'], 'id': user['user_id']})
            btn.bind(on_release=lambda btn: self.users_dropdowns[id].select(btn.button_data))
            self.users_dropdowns[id].add_widget(btn)

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, description, settlement_percent, settlement_value):
        return self.validate_name(name) \
               and self.validate_description(description) \
               and self.validate_type(settlement_percent, settlement_value) \
               and self.validate_users_list(settlement_percent)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa grupy powinna składać się z co najmniej 3 znaków.')
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

    def validate_type(self, settlement_percent, settlement_value):
        valid = False
        if settlement_percent.state == 'normal' and settlement_value.state == 'normal':
            self.show_message('Wybierz typ rozliczenia dla grupy.')
        elif settlement_percent.state == 'down' and settlement_value.state == 'down':
            self.show_message('Można wybrać tylko jeden typ rozliczenia.')
        else:
            valid = True
        return valid

    def validate_users_list(self, settlement_percent):
        valid = False
        all_users_valid = True
        number_of_users = 0
        users_list = []
        priority_list = []
        total_amount = 0
        box = self.ids.box

        for child in box.children[:]:
            if child.id is not None and 'user' in child.id:
                if self.validate_user(child, users_list):
                    users_list.append(child.button_data['id'])
                    number_of_users = number_of_users + 1
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'amount' in child.id:
                if self.validate_amount(child):
                    total_amount = total_amount + float(child.text)
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'priority' in child.id:
                if self.validate_priority(child, priority_list):
                    priority_list.append(int(child.text))
                else:
                    all_users_valid = False
                    break

        if not all_users_valid:
            pass
        elif number_of_users < 1:
            self.show_message('Nie można utworzyć pustej grupy.')
        elif settlement_percent.state == 'down' and total_amount != 100:
            self.show_message('Dla rozliczenia procentowego suma procent członków grupy musi wynosić 100.')

        else:
            valid = True
        return valid

    def validate_user(self, user, users_list):
        user_valid = False
        print(users_list)
        print('Validating user:', user.button_data)
        if user.button_data['id'] == 0:
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('user id', user.button_data['id'])
        elif user.button_data['id'] in users_list:
            self.show_message('Wykryto zduplikowaną wartość "Użytkownik".')
        else:
            user_valid = True
        return user_valid

    def validate_amount(self, amount):
        amount_valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount.text)
        if amount.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
        elif amount_match is None or amount_match.group(1) != amount.text:
            self.show_message('Błędna kwota.')
        else:
            amount_valid = True
        return amount_valid

    def validate_priority(self, priority, priority_list):
        priority_valid = False
        if priority.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('priority', priority.text)
        elif int(priority.text) in priority_list:
            self.show_message('Wykryto zduplikowaną wartość "priorytet".')
        else:
            priority_valid = True
        return priority_valid

    def check_in_database(self, name, description, settlement_percent):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        settlement_type_id = 1 if settlement_percent.state == 'down' else 2
        print('Próbuję dodać grupę')
        group_id = db_manager.create_group(app.root.account_id, name, description, settlement_type_id,
                                           is_main_group=False)
        print(app.root.account_id, name, description, settlement_type_id)
        print(group_id)

        # adding users to user_group_tbl
        box = self.ids.box
        child_id_regex = re.compile(r'([0-9])+')

        # collecting data

        data = {}

        for child in box.children:
            if child.id is None:
                pass
            elif 'user' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['user_id'] = int(child.button_data['id'])
                else:
                    data[id] = {}
                    data[id]['user_id'] = int(child.button_data['id'])
            elif 'amount' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['amount'] = float(child.text)
                else:
                    data[id] = {}
                    data[id]['amount'] = float(child.text)
            elif 'priority' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['priority'] = int(child.text)
                else:
                    data[id] = {}
                    data[id]['priority'] = int(child.text)

        # adding users to group
        print('data:', data)
        for k, v in data.items():
            print(f'Próbuję dodać usera: {v["user_id"]} do grupy')
            db_manager.add_user_to_group(v['user_id'], group_id, v['amount'], v['priority'])

        return group_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.settlement_percent.state = 'down'
        self.ids.settlement_value.state = 'normal'
        self.highest_id = 0
        self.ids.box.clear_widgets()
        self.users_dropdowns = {}

    def show_message(self, message):
        self.ids.message.text = message

    def add_group(self, name_field, description_field, settlement_percent, settlement_value):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, settlement_percent, settlement_value):
            group_id = self.check_in_database(name, description, settlement_percent)
            if group_id != {}:
                print('group succesfully added')
                self.clear_input_fields()
                self.show_message(f'Grupa {name} została dodana.')
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')


class EditGroupScreen(Screen):
    group = ObjectProperty(None)
    users_in_group = ObjectProperty(None)
    users_dropdowns = DictProperty({})
    highest_id = 0

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        group_id = App.get_running_app().root.item_id
        self.group = self.load_group(group_id)
        self.users_in_group = self.load_users_from_group(group_id)
        self.populate_fields()

    def populate_fields(self):
        self.clear_input_fields()
        self.ids.name.text = self.group['name']
        self.ids.description.text = self.group['description']
        if self.group['settlement_type_id'] == 1:
            self.ids.settlement_percent.state = 'down'
            self.ids.settlement_value.state = 'normal'
        else:
            self.ids.settlement_percent.state = 'normal'
            self.ids.settlement_value.state = 'down'
        # self.ids.box.clear_widgets()
        self.users_dropdowns = {}
        for user in self.users_in_group:
            self.add_user_field(user['username'], user['user_id'], str(round(user['amount'], 2)), str(user['priority']))

    def add_user_field(self, b_text='Wybierz', b_id=0, amount='', priority=''):
        self.highest_id += 1
        deletebtn = ButtonWithData(text='-', id=f'delete{self.highest_id}')
        userbtn = ButtonWithData(button_data={'text': b_text, 'id': b_id},
                                 id=f'user{self.highest_id}')
        widgets = [userbtn,
                   FloatInput(text=amount, id=f'amount{self.highest_id}'),
                   IntegerInput(text=priority, id=f'priority{self.highest_id}'),
                   deletebtn]
        deletebtn.bind(on_release=lambda btn: self.remove_user_field(btn.id))

        for widget in widgets:
            self.ids.box.add_widget(widget)

        new_dropdown = DropDown()
        self.users_dropdowns[f'{self.highest_id}'] = new_dropdown
        self.populate_users_dropdown(str(self.highest_id))
        userbtn.bind(on_release=self.users_dropdowns[str(self.highest_id)].open)
        self.users_dropdowns[str(self.highest_id)].bind(
            on_select=lambda instance, x: setattr(userbtn, 'button_data', x))

    def remove_user_field(self, id):
        id_regex = re.compile(r'([0-9]+)')
        id_match = re.search(id_regex, id)

        names = ['user', 'amount', 'priority', 'delete']

        for i in range(len(names)):
            names[i] = names[i] + str(id_match.group(1))
        box = self.ids.box

        for child in box.children[:]:
            if child.id in names:
                box.remove_widget(child)

        self.users_dropdowns.pop(str(id_match.group(1)))

    def populate_users_dropdown(self, id):

        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        self.users_dropdowns[id].clear_widgets()
        users_list = db_manager.get_all_users(app.root.account_id)

        for user in users_list:
            btn = ButtonWithData(text=user['username'],
                                 button_data={'text': user['username'], 'id': user['user_id']})
            btn.bind(on_release=lambda btn: self.users_dropdowns[id].select(btn.button_data))
            self.users_dropdowns[id].add_widget(btn)

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, name, description, settlement_percent, settlement_value):
        return self.validate_name(name) \
               and self.validate_description(description) \
               and self.validate_type(settlement_percent, settlement_value) \
               and self.validate_users_list(settlement_percent)

    def validate_name(self, name):
        valid = False
        if len(name) < 3:
            self.show_message('Nazwa grupy powinna składać się z co najmniej 3 znaków.')
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

    def validate_type(self, settlement_percent, settlement_value):
        valid = False
        if settlement_percent.state == 'normal' and settlement_value.state == 'normal':
            self.show_message('Wybierz typ rozliczenia dla grupy.')
        elif settlement_percent.state == 'down' and settlement_value.state == 'down':
            self.show_message('Można wybrać tylko jeden typ rozliczenia.')
        else:
            valid = True
        return valid

    def validate_users_list(self, settlement_percent):
        valid = False
        all_users_valid = True
        number_of_users = 0
        users_list = []
        priority_list = []
        total_amount = 0
        box = self.ids.box

        for child in box.children[:]:
            if child.id is not None and 'user' in child.id:
                if self.validate_user(child, users_list):
                    users_list.append(child.button_data['id'])
                    number_of_users = number_of_users + 1
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'amount' in child.id:
                if self.validate_amount(child):
                    total_amount = total_amount + float(child.text)
                else:
                    all_users_valid = False
                    break
            elif child.id is not None and 'priority' in child.id:
                if self.validate_priority(child, priority_list):
                    priority_list.append(int(child.text))
                else:
                    all_users_valid = False
                    break

        if not all_users_valid:
            pass
        elif number_of_users < 1:
            self.show_message('Nie można utworzyć pustej grupy.')
        elif settlement_percent.state == 'down' and total_amount != 100:
            self.show_message('Dla rozliczenia procentowego suma procent członków grupy musi wynosić 100.')

        else:
            valid = True
        return valid

    def validate_user(self, user, users_list):
        user_valid = False
        print(users_list)
        print('Validating user:', user.button_data)
        if user.button_data['id'] == 0:
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('user id', user.button_data['id'])
        elif user.button_data['id'] in users_list:
            self.show_message('Wykryto zduplikowaną wartość "Użytkownik".')
        else:
            user_valid = True
        return user_valid

    def validate_amount(self, amount):
        amount_valid = False
        amount_regex = re.compile(r'([0-9]+\.?[0-9]{0,2})')
        amount_match = re.search(amount_regex, amount.text)
        if amount.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
        elif amount_match is None or amount_match.group(1) != amount.text:
            self.show_message('Błędna kwota.')
        else:
            amount_valid = True
        return amount_valid

    def validate_priority(self, priority, priority_list):
        priority_valid = False
        if priority.text == '':
            self.show_message('Uzupełnij dane wszystkich członków grupy.')
            print('priority', priority.text)
        elif int(priority.text) in priority_list:
            self.show_message('Wykryto zduplikowaną wartość "priorytet".')
        else:
            priority_valid = True
        return priority_valid

    def load_group(self, group_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać grupę')
        group = db_manager.get_group(group_id)
        print(group)
        return group

    def load_users_from_group(self, group_id):
        db_manager = App.get_running_app().db_manager
        print('Próbuję wczytać członków grupy')
        users_in_group = db_manager.get_all_users_from_group(group_id)
        print(users_in_group)
        return users_in_group

    def check_in_database(self, name, description, settlement_percent):
        db_manager = App.get_running_app().db_manager
        settlement_type_id = 1 if settlement_percent.state == 'down' else 2
        print('Próbuję dodać grupę')
        group_id = db_manager.edit_group(self.group['group_id'], name, description, settlement_type_id,
                                         is_main_group=False)

        # adding users to user_group_tbl
        box = self.ids.box
        child_id_regex = re.compile(r'([0-9])+')

        # collecting data

        data = {}

        for child in box.children:
            if child.id is None:
                pass
            elif 'user' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['user_id'] = int(child.button_data['id'])
                else:
                    data[id] = {}
                    data[id]['user_id'] = int(child.button_data['id'])
            elif 'amount' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['amount'] = float(child.text)
                else:
                    data[id] = {}
                    data[id]['amount'] = float(child.text)
            elif 'priority' in child.id:
                id = re.search(child_id_regex, child.id).group(1)
                if id in data:
                    data[id]['priority'] = int(child.text)
                else:
                    data[id] = {}
                    data[id]['priority'] = int(child.text)

        # adding, editing and removing users from group
        print('data:', data)
        current_ids_list = []
        new_ids_list = []
        for user in self.users_in_group:
            current_ids_list.append(user['user_id'])
        for k, v in data.items():
            new_ids_list.append(v['user_id'])
            if v['user_id'] not in current_ids_list:
                print(f'Próbuję dodać usera: {v["user_id"]} do grupy')
                db_manager.add_user_to_group(v['user_id'], self.group['group_id'], v['amount'], v['priority'])
            else:
                print(f'Próbuję edytować usera: {v["user_id"]}')
                db_manager.edit_user_from_group(v['user_id'], self.group['group_id'], v['amount'], v['priority'])
        print('current_ids_list:', current_ids_list)
        print('new_ids_list:', new_ids_list)

        for user_id in current_ids_list:
            if user_id not in new_ids_list:
                print(f'Próbuję usunąć usera: {user_id} z grupy')
                db_manager.remove_user_from_group(user_id, self.group['group_id'])

        return group_id

    def clear_input_fields(self):
        self.clear_message()
        self.ids.name.text = ''
        self.ids.description.text = ''
        self.ids.settlement_percent.state = 'down'
        self.ids.settlement_value.state = 'normal'
        self.highest_id = 0
        self.ids.box.clear_widgets()
        self.users_dropdowns = {}

    def show_message(self, message):
        self.ids.message.text = message

    def compare_changes(self, name, description, settlement_percent, settlement_value):
        self.clear_message()
        print('Comparing changes in group:')
        print(self.group)
        has_changed = False
        if self.group['name'] != name:
            has_changed = True
            print(self.group['name'], '!=', name)
        elif self.group['description'] != description:
            has_changed = True
            print(self.group['description'], '!=', description)
        elif self.group['settlement_type_id'] == 1 \
                and (settlement_percent.state == 'normal' or settlement_value.state == 'down'):
            has_changed = True
            print('settlement_type_id has changed')
        elif self.group['settlement_type_id'] == 2 \
                and (settlement_percent.state == 'down' or settlement_value.state == 'normal'):
            has_changed = True
            print('settlement_type_id has changed')
        else:
            box = self.ids.box
            child_id_regex = re.compile(r'([0-9])+')

            # collecting data

            data = {}

            for child in box.children:
                if child.id is None:
                    pass
                elif 'user' in child.id:
                    id = re.search(child_id_regex, child.id).group(1)
                    if id in data:
                        data[id]['user_id'] = int(child.button_data['id'])
                    else:
                        data[id] = {}
                        data[id]['user_id'] = int(child.button_data['id'])
                elif 'amount' in child.id:
                    id = re.search(child_id_regex, child.id).group(1)
                    if id in data:
                        data[id]['amount'] = float(child.text)
                    else:
                        data[id] = {}
                        data[id]['amount'] = float(child.text)
                elif 'priority' in child.id:
                    id = re.search(child_id_regex, child.id).group(1)
                    if id in data:
                        data[id]['priority'] = int(child.text)
                    else:
                        data[id] = {}
                        data[id]['priority'] = int(child.text)

            # checking if there are differences between current users list and the new users list

            if len(self.users_in_group) != len(data):
                print('Number of users has changed.')
                has_changed = True
            else:
                for new_user in data:
                    has_changed = True
                    for old_user in self.users_in_group:
                        print('Checking user:', old_user)
                        if (data[new_user]['user_id'] == old_user['user_id']
                                and data[new_user]['amount'] == float(round(old_user['amount'], 2))
                                and data[new_user]['priority'] == old_user['priority']):
                            has_changed = False
                            break
                    if has_changed:
                        print('User data has changed')
                        print('Cannot find new user:', data[new_user])
                        break
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

    def update_group(self, name_field, description_field, settlement_percent, settlement_value):
        name = name_field.text
        description = description_field.text

        if self.validate_input(name, description, settlement_percent, settlement_value) \
                and self.compare_changes(name, description, settlement_percent, settlement_value):
            errors = self.check_in_database(name, description, settlement_percent)
            if errors is None:
                print('group succesfully updated')
                self.show_message(f'Zmiany dla grupy {name} zostały zapisane.')
                self.group = self.load_group(self.group['group_id'])
                self.users_in_group = self.load_users_from_group(self.group['group_id'])
            else:
                self.show_message('Błąd, skontaktuj się z administratorem.')
