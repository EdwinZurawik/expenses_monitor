import mysql.connector
# from mysql.connector import errorcode
from configuration_data import ConfigurationData
from datetime import datetime
from datetime import date


class DatabaseManager:
    db = None
    cursor = None

    def connect_to_db(self):
        self.db = mysql.connector.connect(**ConfigurationData.db_config)
        self.cursor = self.db.cursor()
        return self.db

    def close_connection(self):
        self.db.close()
        self.cursor = None

    # ------------------------------------------------- CREATE ------------------------------------------------------- #

    def create_account(self, username, password, email):
        # Creating new account
        account_id = self.__insert_account(username, password, email)
        if account_id is None:
            account_id = {}
        else:
            # Creating default expense category for this account
            self.create_category(account_id, 'Wydatki',
                                 'Domyślna kategoria dla wydatków.', 1)
            # Creating default income category for this account
            self.create_category(account_id, 'Wpływy',
                                 'Domyślna kategoria dla wpływów.', 2)
            # Creating default payment method for this account
            self.create_payment_method(account_id, 'Domyślna metoda płatności')

        return account_id

    def create_user(self, account_id, username):
        # Creating default group for this user
        group_id = self.create_group(account_id, username, f'Default group of the user {username}',
                                     1, is_main_group=True)
        user_id = {}
        if group_id != {}:
            user_id = self.__insert_user(account_id, username, group_id)
            if user_id is None:
                user_id = {}
            # Adding user to his default group
            self.add_user_to_group(user_id, group_id, 100, 1)
        return user_id

    def create_group(self, account_id, name, description, settlement_type_id, is_main_group=False):
        group_id = self.__insert_group(account_id, name, description, settlement_type_id, is_main_group)
        if group_id is None:
            group_id = {}
        return group_id

    def add_user_to_group(self, user_id, group_id, amount, priority):
        self.__insert_user_to_group(user_id, group_id, amount, priority)

    def create_category(self, account_id, name, description, category_type_id):
        category_id = self.__insert_category(account_id, name, description, category_type_id)
        if category_id is None:
            category_id = {}
        return category_id

    def create_expense(self, operation_date, name, description, payer_id,
                       category_id, amount, payment_method_id, group_id):
        expense_id = self.__insert_expense(operation_date, name, description, payer_id,
                                           category_id, amount, payment_method_id, group_id)
        if expense_id is None:
            expense_id = {}
        return expense_id

    def create_income(self, operation_date, name, description, category_id, amount, group_id):
        income_id = self.__insert_income(operation_date, name, description, category_id, amount, group_id)
        if income_id is None:
            income_id = {}
        return income_id

    def create_payment_method(self, account_id, name):
        payment_method_id = self.__insert_payment_method(account_id, name)
        if payment_method_id is None:
            payment_method_id = {}
        return payment_method_id

    # ---------------------------------------------- EDIT ------------------------------------------------------------ #

    def edit_account(self, account_id, password, email):  # not possible to edit username
        self.__update_account(account_id, password, email)

    def edit_user(self, user_id, username):
        return self.__update_user(user_id, username)

    def edit_group(self, group_id, name, description, settlement_type_id, is_main_group=False):
        return self.__update_group(group_id, name, description, settlement_type_id, is_main_group)

    def edit_category(self, category_id, name, description, category_type_id):
        return self.__update_category(category_id, name, description, category_type_id)

    def edit_expense(self, expense_id, operation_date, name, description, amount,
                     payer_id, category_id, group_id, payment_method_id):
        return self.__update_expense(expense_id, operation_date, name, description, amount,
                                     payer_id, category_id, group_id, payment_method_id)

    def edit_income(self, income_id, operation_date, name, description, amount, category_id, group_id):
        return self.__update_income(income_id, operation_date, name, description, amount, category_id, group_id)

    def edit_payment_method(self, payment_method_id, name):
        return self.__update_payment_method(payment_method_id, name)

    def edit_user_from_group(self, user_id, group_id, amount, priority):
        return self.__update_user_from_group(user_id, group_id, amount, priority)

    # ----------------------------------------------- GET ------------------------------------------------------------ #

    def get_account(self, username, password):
        data = self.__select_account(username, password)
        result = {}
        if data is not None:
            result = {
                'account_id': data[0],
                'username': data[1],
                'password': data[2],
                'email': data[3]
            }
        return result

    def get_all_users(self, account_id, order_by='username'):
        data = self.__select_all_users(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'user_id': row[0],
                    'username': row[1],
                    'main_group_id': row[2],
                    'account_id': row[3]
                }
            )
        return results

    def get_all_users_from_group(self, group_id, order_by='username'):
        data = self.__select_all_users_from_group(group_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'user_id': row[0],
                    'username': row[1],
                    'main_group_id': row[2],
                    'account_id': row[3],
                    'amount': row[4],
                    'priority': row[5]
                }
            )
        return results

    def get_all_categories(self, account_id, order_by='name'):
        data = self.__select_all_categories(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'category_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'category_type_id': row[3],
                    'account_id': row[4]
                }
            )
        return results

    def get_all_groups(self, account_id, order_by='name'):
        data = self.__select_all_groups(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'group_id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'settlement_type_id': row[3],
                    'is_main_group': row[4],
                    'account_id': row[5]
                }
            )
        return results

    def get_all_payment_methods(self, account_id, order_by='name'):
        data = self.__select_all_payment_methods(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'payment_method_id': row[0],
                    'name': row[1],
                    'account_id': row[2]
                }
            )
        return results

    def get_all_category_types(self, order_by='name'):
        data = self.__select_all_category_types(order_by)
        results = []
        for row in data:
            results.append(
                {
                    'name': row[0],
                    'description': row[1]
                }
            )
        return results

    def get_all_settlement_types(self, order_by='name'):
        data = self.__select_all_settlement_types(order_by)
        results = []
        for row in data:
            results.append(
                {
                    'settlement_type_id': row[0],
                    'name': row[1],
                    'description': row[2]
                }
            )
        return results

    def get_all_expenses(self, account_id, order_by='e.operationDate, c.name, e.name'):
        data = self.__select_all_expenses(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'expense_id': row[0],
                    'operation_date': row[1],
                    'amount': row[2],
                    'expense_name': row[3],
                    'description': row[4],
                    'username': row[5],
                    'category_name': row[6],
                    'payment_method_name': row[7],
                    'group_name': row[8],
                    'user_id': row[9],
                    'category_id': row[10],
                    'payment_method_id': row[11],
                    'group_id': row[12],
                    'settlement_type_id': row[13]
                }
            )
        return results

    def get_all_expenses_between_dates(self, account_id, date_from=None,
                                       date_to=None, order_by='e.operationDate, c.name, e.name'):
        data = self.__select_all_expenses_between_dates(account_id, date_from, date_to, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'expense_id': row[0],
                    'operation_date': row[1],
                    'amount': row[2],
                    'expense_name': row[3],
                    'description': row[4],
                    'username': row[5],
                    'category_name': row[6],
                    'payment_method_name': row[7],
                    'group_name': row[8],
                    'user_id': row[9],
                    'category_id': row[10],
                    'payment_method_id': row[11],
                    'group_id': row[12],
                    'settlement_type_id': row[13]
                }
            )
        return results

    def get_all_incomes(self, account_id, order_by='i.operationDate, c.name, i.name'):
        data = self.__select_all_incomes(account_id, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'income_id': row[0],
                    'operation_date': row[1],
                    'amount': row[2],
                    'income_name': row[3],
                    'description': row[4],
                    'category_name': row[5],
                    'group_name': row[6],
                    'category_id': row[7],
                    'group_id': row[8],
                    'settlement_type_id': row[9]
                }
            )
        return results

    def get_all_incomes_between_dates(self, account_id, date_from=None,
                                      date_to=None, order_by='i.operationDate, c.name, i.name'):
        data = self.__select_all_incomes_between_dates(account_id, date_from, date_to, order_by)
        results = []
        for row in data:
            results.append(
                {
                    'income_id': row[0],
                    'operation_date': row[1],
                    'amount': row[2],
                    'income_name': row[3],
                    'description': row[4],
                    'category_name': row[5],
                    'group_name': row[6],
                    'category_id': row[7],
                    'group_id': row[8],
                    'settlement_type_id': row[9]
                }
            )
        return results

    def get_default_expense_category(self, account_id):
        data = self.__select_default_expense_category(account_id)
        result = {}
        if data is not None:
            result = {
                'category_id': data[0],
                'name': data[1],
                'description': data[2],
                'category_type_id': data[3],
                'account_id': data[4]
            }
        return result

    def get_default_income_category(self, account_id):
        data = self.__select_default_income_category(account_id)
        result = {}
        if data is not None:
            result = {
                'category_id': data[0],
                'name': data[1],
                'description': data[2],
                'category_type_id': data[3],
                'account_id': data[4]
            }
        return result

    def get_users_default_group(self, user_id):
        data = self.__select_users_default_group(user_id)
        result = {}
        if data is not None:
            result = {
                'group_id': data[0],
                'name': data[1],
                'description': data[2],
                'settlement_type_id': data[3],
                'is_main_group': data[4],
                'account_id': data[5]
            }
        return result

    def get_default_payment_method(self, account_id):
        data = self.__select_default_payment_method(account_id)
        result = {}
        if data is not None:
            result = {
                'payment_method_id': data[0],
                'name': data[1],
                'account_id': data[2]
            }
        return result

    def get_user(self, user_id):
        data = self.__select_user(user_id)
        result = {}
        if data is not None:
            result = {
                'user_id': data[0],
                'username': data[1],
                'main_group_id': data[2],
                'account_id': data[3]
            }
        return result

    def get_category(self, category_id):
        data = self.__select_category(category_id)
        result = {}
        if data is not None:
            result = {
                'category_id': data[0],
                'name': data[1],
                'description': data[2],
                'category_type_id': data[3],
                'account_id': data[4]
            }
        return result

    def get_group(self, group_id):
        data = self.__select_group(group_id)
        result = {}
        if data is not None:
            result = {
                'group_id': data[0],
                'name': data[1],
                'description': data[2],
                'settlement_type_id': data[3],
                'is_main_group': data[4],
                'account_id': data[5]
            }
        return result

    def get_payment_method(self, payment_method_id):
        data = self.__select_payment_method(payment_method_id)
        result = {}
        if data is not None:
            result = {
                'payment_method_id': data[0],
                'name': data[1],
                'account_id': data[2]
            }
        return result

    def get_expense(self, expense_id):
        data = self.__select_expense(expense_id)
        result = {}
        if data is not None:
            result = {
                'expense_id': data[0],
                'operation_date': data[1],
                'amount': data[2],
                'expense_name': data[3],
                'description': data[4],
                'username': data[5],
                'category_name': data[6],
                'payment_method_name': data[7],
                'group_name': data[8],
                'user_id': data[9],
                'category_id': data[10],
                'payment_method_id': data[11],
                'group_id': data[12],
                'settlement_type_id': data[13]
            }

        return result

    def get_income(self, income_id):
        data = self.__select_income(income_id)
        result = {}
        if data is not None:
            result = {
                'income_id': data[0],
                'operation_date': data[1],
                'amount': data[2],
                'income_name': data[3],
                'description': data[4],
                'category_name': data[5],
                'group_name': data[6],
                'category_id': data[7],
                'group_id': data[8],
                'settlement_type_id': data[9]
            }
        return result

    # ---------------------------------------------- REMOVE ---------------------------------------------------------- #

    def remove_user_from_group(self, user_id, group_id):
        return self.__delete_user_from_group(user_id, group_id)

    # ------------------------------------------ INSERT QUERIES ------------------------------------------------------ #

    def __insert_account(self, username, password, email):
        sql = ('INSERT INTO account_tbl'
               '(username, password, email)'
               'VALUES'
               '(%s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (username, password, email))
            self.db.commit()
            account_id = self.cursor.lastrowid
            return account_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __insert_user(self, account_id, username, main_group_id):
        sql = ('INSERT INTO user_tbl'
               '(username, mainGroupId, accountId)'
               'VALUES'
               '(%s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (username, main_group_id, account_id))
            self.db.commit()
            user_id = self.cursor.lastrowid
            return user_id
        except mysql.connector.Error as err:
            print(err.msg)
            raise
        finally:
            self.close_connection()

    def __insert_group(self, account_id, name, description, settlement_type_id, is_main_group=False):
        sql = ('INSERT INTO group_tbl'
               '(name, description, settlementTypeId, isMainGroup, accountId)'
               'VALUES'
               '(%s, %s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, settlement_type_id, is_main_group, account_id))
            self.db.commit()
            group_id = self.cursor.lastrowid
            return group_id
        except mysql.connector.Error as err:
            print(err.msg)
            raise
        finally:
            self.close_connection()

    def __insert_user_to_group(self, user_id, group_id, amount, priority):
        sql = ('INSERT INTO user_group_tbl'
               '(userId, groupId, amount, priority)'
               'VALUES'
               '(%s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id, group_id, amount, priority))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            raise
        finally:
            self.close_connection()

    def __insert_users_to_group(self):
        pass

    def __insert_category(self, account_id, name, description, category_type_id):
        sql = ('INSERT INTO category_tbl'
               '(name, description, categoryTypeId, accountId)'
               'VALUES'
               '(%s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, category_type_id, account_id))
            self.db.commit()
            category_id = self.cursor.lastrowid
            return category_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __insert_expense(self, operation_date, name, description, payer_id,
                         category_id, amount, payment_method_id, group_id):
        sql = ('INSERT INTO expense_tbl'
               '(operationDate, name, description, payerId, categoryId, amount, paymentMethodId, groupId)'
               'VALUES'
               '(%s, %s, %s, %s, %s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (operation_date, name, description, payer_id,
                                      category_id, amount, payment_method_id, group_id))
            self.db.commit()
            expense_id = self.cursor.lastrowid
            return expense_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __insert_income(self, operation_date, name, description, category_id, amount, group_id):
        sql = ('INSERT INTO income_tbl'
               '(operationDate, name, description, categoryId, amount, groupId)'
               'VALUES'
               '(%s, %s, %s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (operation_date, name, description, category_id, amount, group_id))
            self.db.commit()
            income_id = self.cursor.lastrowid
            return income_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __insert_payment_method(self, account_id, name):
        sql = ('INSERT INTO payment_method_tbl'
               '(name, accountId)'
               'VALUES'
               '(%s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, account_id))
            self.db.commit()
            payment_method_id = self.cursor.lastrowid
            return payment_method_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    # -------------------------------------------- UPDATE QUERIES ---------------------------------------------------- #

    def __update_account(self, account_id, password, email):  # not possible to update username
        sql = ('UPDATE account_tbl '
               'SET '
               'password = %s, '
               'email = %s '
               'WHERE accountId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (password, email, account_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __update_user(self, user_id, username):
        sql = ('UPDATE user_tbl '
               'SET '
               'username = %s '
               'WHERE userId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (username, user_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_group(self, group_id, name, description, settlement_type_id, is_main_group=False):
        sql = ('UPDATE group_tbl '
               'SET '
               'name = %s, '
               'description = %s, '
               'settlementTypeId = %s, '
               'isMainGroup = %s '
               'WHERE groupId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, settlement_type_id, is_main_group, group_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_category(self, category_id, name, description, category_type_id):
        sql = ('UPDATE category_tbl '
               'SET '
               'name = %s, '
               'description = %s, '
               'categoryTypeId = %s '
               'WHERE categoryId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, category_type_id, category_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_expense(self, expense_id, operation_date, name, description, amount,
                         payer_id, category_id, group_id, payment_method_id):
        sql = ('UPDATE expense_tbl '
               'SET '
               'operationDate = %s, '
               'name = %s, '
               'description = %s, '
               'amount = %s, '
               'payerId = %s, '
               'categoryId = %s, '
               'groupId = %s,'
               'paymentMethodId = %s '
               'WHERE expenseId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (operation_date, name, description, amount,
                                      payer_id, category_id, group_id,
                                      payment_method_id, expense_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_income(self, income_id, operation_date, name, description, amount, category_id, group_id):
        sql = ('UPDATE income_tbl '
               'SET '
               'operationDate = %s, '
               'name = %s, '
               'description = %s, '
               'amount = %s, '
               'categoryId = %s, '
               'groupId = %s '
               'WHERE incomeId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (operation_date, name, description, amount,
                                      category_id, group_id, income_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_payment_method(self, payment_method_id, name):
        sql = ('UPDATE payment_method_tbl '
               'SET '
               'name = %s '
               'WHERE paymentMethodId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, payment_method_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def __update_user_from_group(self, user_id, group_id, amount, priority):
        print('Trying to update:', user_id, group_id, amount, priority)
        sql = ('UPDATE user_group_tbl '
               'SET '
               'amount = %s, '
               'priority = %s '
               'WHERE userId = %s '
               'AND groupId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (amount, priority, user_id, group_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    # -------------------------------------------- SELECT QUERIES ---------------------------------------------------- #

    def __select_account(self, username, password):
        sql = ('SELECT '
               'accountId, '
               'username, '
               'password, '
               'email '
               'FROM account_tbl '
               'WHERE '
               'username = %s '
               'AND password = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (username, password))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_users(self, account_id, order_by='username'):
        sql = ('SELECT '
               'userId, '
               'username, '
               'mainGroupId, '
               'accountId '
               ' FROM user_tbl '
               'WHERE '
               'accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_users_from_group(self, group_id, order_by='username'):
        sql = ('SELECT '
               'u.userId, '
               'u.username, '
               'u.mainGroupId, '
               'u.accountId, '
               'ug.amount, '
               'ug.priority '
               'FROM user_tbl u '
               'JOIN user_group_tbl ug '
               'ON u.userId=ug.userId '
               'WHERE '
               'ug.groupId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (group_id,))
            results = self.cursor.fetchall()
            if results is None:
                results = {}
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_categories(self, account_id, order_by='name'):
        sql = ('SELECT '
               'categoryId, '
               'name, '
               'description, '
               'categoryTypeId, '
               'accountId '
               'FROM category_tbl '
               'WHERE '
               'accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_groups(self, account_id, order_by='name'):
        sql = ('SELECT '
               'groupId, '
               'name, '
               'description, '
               'settlementTypeId, '
               'isMainGroup, '
               'accountId '
               'FROM group_tbl '
               'WHERE '
               'accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_payment_methods(self, account_id, order_by='name'):
        sql = ('SELECT '
               'paymentMethodId, '
               'name, '
               'accountId '
               'FROM payment_method_tbl '
               'WHERE '
               'accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_category_types(self, order_by='name'):
        sql = ('SELECT '
               'name, '
               'description '
               'FROM category_type_tbl '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_settlement_types(self, order_by='name'):
        sql = ('SELECT '
               'settlementTypeId, '
               'name, '
               'description, '
               'FROM settlement_type_tbl '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_expenses(self, account_id, order_by='e.operationDate, c.name, e.name'):
        sql = ('SELECT '
               'e.expenseId, '
               'e.operationDate, '
               'e.amount, '
               'e.name, '
               'e.description, '
               'u.username, '
               'c.name, '
               'p.name, '
               'g.name, '
               'u.userId, '
               'c.categoryId, '
               'p.paymentMethodId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM expense_tbl e '
               'LEFT JOIN user_tbl u '
               'ON e.payerId=u.userId '
               'LEFT JOIN category_tbl c '
               'ON e.categoryId=c.categoryId '
               'LEFT JOIN payment_method_tbl p '
               'ON e.paymentMethodId=p.paymentMethodId '
               'LEFT JOIN group_tbl g '
               'ON e.groupId=g.groupId '
               'WHERE '
               'u.accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_expenses_between_dates(self, account_id, date_from=None,
                                            date_to=None, order_by='e.operationDate, c.name, e.name'):
        if date_from is None:
            date_from = datetime(1000, 1, 1)
        else:
            date_from = datetime.combine(date_from, datetime.min.time())
        if date_to is None:
            date_to = datetime(9999, 12, 31, 23, 59, 59)
        else:
            date_to = datetime.combine(date_to, datetime.max.time())

        sql = ('SELECT '
               'e.expenseId, '
               'e.operationDate, '
               'e.amount, '
               'e.name, '
               'e.description, '
               'u.username, '
               'c.name, '
               'p.name, '
               'g.name, '
               'u.userId, '
               'c.categoryId, '
               'p.paymentMethodId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM expense_tbl e '
               'LEFT JOIN user_tbl u '
               'ON e.payerId=u.userId '
               'LEFT JOIN category_tbl c '
               'ON e.categoryId=c.categoryId '
               'LEFT JOIN payment_method_tbl p '
               'ON e.paymentMethodId=p.paymentMethodId '
               'LEFT JOIN group_tbl g '
               'ON e.groupId=g.groupId '
               'WHERE '
               'u.accountId=%s '
               'AND e.operationDate BETWEEN %s and %s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id, date_from, date_to))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_incomes(self, account_id, order_by='i.operationDate, c.name, i.name'):
        sql = ('SELECT '
               'i.incomeId, '
               'i.operationDate, '
               'i.amount, '
               'i.name, '
               'i.description, '
               'c.name, '
               'g.name, '
               'c.categoryId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM income_tbl i '
               'INNER JOIN category_tbl c '
               'ON i.categoryId=c.categoryId '
               'INNER JOIN group_tbl g '
               'ON i.groupId=g.groupId '
               'WHERE '
               'g.accountId=%s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_all_incomes_between_dates(self, account_id, date_from=None,
                                           date_to=None, order_by='i.operationDate, c.name, i.name'):
        if date_from is None:
            date_from = datetime(1000, 1, 1)
        else:
            date_from = datetime.combine(date_from, datetime.min.time())
        if date_to is None:
            date_to = datetime(9999, 12, 31, 23, 59, 59)
        else:
            date_to = datetime.combine(date_to, datetime.max.time())

        sql = ('SELECT '
               'i.incomeId, '
               'i.operationDate, '
               'i.amount, '
               'i.name, '
               'i.description, '
               'c.name, '
               'g.name, '
               'c.categoryId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM income_tbl i '
               'INNER JOIN category_tbl c '
               'ON i.categoryId=c.categoryId '
               'INNER JOIN group_tbl g '
               'ON i.groupId=g.groupId '
               'WHERE '
               'g.accountId=%s '
               'AND i.operationDate BETWEEN %s and %s '
               f'ORDER BY {order_by}')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id, date_from, date_to))
            results = self.cursor.fetchall()
            return results
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_default_expense_category(self, account_id):
        sql = ('SELECT '
               'categoryId, '
               'name, '
               'description, '
               'categoryTypeId, '
               'accountId '
               'FROM category_tbl '
               'WHERE '
               'accountId=%s '
               'AND categoryTypeId=%s '
               'ORDER BY categoryId '
               'LIMIT 1')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id, 1))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_default_income_category(self, account_id):
        sql = ('SELECT '
               'categoryId, '
               'name, '
               'description, '
               'categoryTypeId, '
               'accountId '
               'FROM category_tbl '
               'WHERE '
               'accountId=%s '
               'AND categoryTypeId=%s '
               'ORDER BY categoryId '
               'LIMIT 1')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id, 2))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_users_default_group(self, user_id):
        sql = ('SELECT '
               'g.groupId, '
               'g.name, '
               'g.description, '
               'g.settlementTypeId, '
               'g.isMainGroup, '
               'g.accountId '
               'FROM group_tbl g '
               'JOIN user_tbl u '
               'ON g.groupId=u.mainGroupId '
               'WHERE userId=%s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_default_payment_method(self, account_id):
        sql = ('SELECT '
               'paymentMethodId, '
               'name, '
               'accountId '
               'FROM payment_method_tbl '
               'WHERE '
               'accountId=%s '
               'ORDER BY payment_method_id '
               'LIMIT 1')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_user(self, user_id):
        sql = ('SELECT '
               'userId, '
               'username, '
               'mainGroupId, '
               'accountId '
               'FROM user_tbl '
               'WHERE '
               'userId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_category(self, category_id):
        sql = ('SELECT '
               'categoryId, '
               'name, '
               'description, '
               'categoryTypeId, '
               'accountId '
               'FROM category_tbl '
               'WHERE '
               'categoryId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (category_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_group(self, group_id):
        sql = ('SELECT '
               'groupId, '
               'name, '
               'description, '
               'settlementTypeId, '
               'isMainGroup, '
               'accountId '
               'FROM group_tbl '
               'WHERE '
               'groupId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (group_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_payment_method(self, payment_method_id):
        sql = ('SELECT '
               'paymentMethodId, '
               'name, '
               'accountId '
               'FROM payment_method_tbl '
               'WHERE '
               'paymentMethodId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (payment_method_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_expense(self, expense_id):
        sql = ('SELECT '
               'e.expenseId, '
               'e.operationDate, '
               'e.amount, '
               'e.name, '
               'e.description, '
               'u.username, '
               'c.name, '
               'p.name, '
               'g.name, '
               'u.userId, '
               'c.categoryId, '
               'p.paymentMethodId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM expense_tbl e '
               'INNER JOIN user_tbl u '
               'ON e.payerId=u.userId '
               'INNER JOIN category_tbl c '
               'ON e.categoryId=c.categoryId '
               'INNER JOIN payment_method_tbl p '
               'ON e.paymentMethodId=p.paymentMethodId '
               'INNER JOIN group_tbl g '
               'ON e.groupId=g.groupId '
               'WHERE '
               'e.expenseId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (expense_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_income(self, income_id):
        sql = ('SELECT '
               'i.incomeId, '
               'i.operationDate, '
               'i.amount, '
               'i.name, '
               'i.description, '
               'c.name, '
               'g.name, '
               'c.categoryId, '
               'g.groupId, '
               'g.settlementTypeId '
               'FROM income_tbl i '
               'INNER JOIN category_tbl c '
               'ON i.categoryId=c.categoryId '
               'INNER JOIN group_tbl g '
               'ON i.groupId=g.groupId '
               'WHERE '
               'i.incomeId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (income_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    # -------------------------------------------- DELETE QUERIES ---------------------------------------------------- #

    def delete_account(self):
        pass

    def delete_user(self):
        pass

    def delete_group(self):
        pass

    def __delete_user_from_group(self, user_id, group_id):
        sql = ('DELETE FROM user_group_tbl '
               'WHERE '
               'userId = %s '
               'AND groupId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id, group_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
            return err.msg
        finally:
            self.close_connection()
        return None

    def delete_users_from_group(self):
        pass

    def delete_category(self):
        pass

    def delete_expense(self):
        pass

    def delete_income(self):
        pass

    def delete_payment_method(self):
        pass
