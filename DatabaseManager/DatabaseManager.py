import mysql.connector
# from mysql.connector import errorcode
from ConfigurationData import ConfigurationData


class DatabaseManager:
    db = None
    cursor = None

    def connect_to_db(self):
        self.db = mysql.connector.connect(**ConfigurationData.db_config)
        self.cursor = self.db.cursor()

    def close_connection(self):
        self.db.close()
        self.cursor = None

    # ------------------------------------------------- CREATE ------------------------------------------------------- #

    def create_account(self, username, password, email):
        # Creating new account
        account_id = self.__insert_account(username, password, email)

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
        # Creating default settlement rule for this user
        settlement_rule_id = self.create_settlement_rule(account_id, 'default settlement',
                                                         'Domyślny typ rozliczenia.', 1)
        # Creating default group for this user
        group_id = self.create_group(account_id, username, f'Default group of the user {username}',
                                     settlement_rule_id, is_main_group=True)
        user_id = self.__insert_user(account_id, username, group_id)
        self.add_user_to_group(user_id, group_id)
        return user_id

    def create_group(self, account_id, name, description, settlement_rule_id, is_main_group=False):
        group_id = self.__insert_group(account_id, name, description, settlement_rule_id, is_main_group)
        return group_id

    def add_user_to_group(self, user_id, group_id):
        self.__insert_user_to_group(user_id, group_id)

    def create_category(self, account_id, name, description, category_type_id):
        category_id = self.__insert_category(account_id, name, description, category_type_id)
        return category_id

    def create_settlement_rule(self, account_id, name, description, settlement_type_id):
        settlement_rule_id = self.__insert_settlement_rule(account_id, name, description, settlement_type_id)
        return settlement_rule_id

    def add_user_to_settlement_rule(self, settlement_rule_id, user_id, amount, priority):
        self.__insert_user_to_settlement_rule(settlement_rule_id, user_id, amount, priority)

    def create_expense(self, operation_date, name, description, payer_id,
                       category_id, amount, payment_method_id, group_id):
        expense_id = self.__insert_expense(operation_date, name, description, payer_id,
                                           category_id, amount, payment_method_id, group_id)
        return expense_id

    def create_income(self, operation_date, name, description, category_id, amount, group_id):
        income_id = self.__insert_income(operation_date, name, description, category_id, amount, group_id)
        return income_id

    def create_payment_method(self, account_id, name):
        payment_method_id = self.__insert_payment_method(account_id, name)
        return payment_method_id

    # ---------------------------------------------- EDIT ------------------------------------------------------------ #

    def edit_account(self, account_id, password, email):  # not possible to edit username
        self.__update_account(account_id, password, email)

    def edit_user(self, user_id, username):
        self.__update_user(user_id, username)

    def edit_group(self, group_id, name, description, settlement_rule_id):
        self.__update_group(group_id, name, description, settlement_rule_id)

    def edit_category(self, category_id, name, description, category_type_id):
        self.__update_category(category_id, name, description, category_type_id)

    def edit_settlement_rule(self, settlement_rule_id, name, description, settlement_type_id):
        self.__update_settlement_rule(settlement_rule_id, name, description, settlement_type_id)

    def edit_expense(self, expense_id, operation_date, name, description, amount, payer_id, category_id, group_id):
        self.__update_expense(expense_id, operation_date, name, description, amount, payer_id, category_id, group_id)

    def edit_income(self, income_id, operation_date, name, description, amount, category_id, group_id):
        self.__update_income(income_id, operation_date, name, description, amount, category_id, group_id)

    def edit_payment_method(self, payment_method_id, name):
        self.__update_payment_method(payment_method_id, name)

    # ----------------------------------------------- GET ------------------------------------------------------------ #

    def get_account(self, username, password):
        result = self.__select_account(username, password)
        return result

    def get_all_users(self, account_id, order_by='username'):
        results = self.__select_all_users(account_id, order_by)
        return results

    def get_all_categories(self, account_id, order_by='name'):
        results = self.__select_all_categories(account_id, order_by)
        return results

    def get_all_groups(self, account_id, order_by='name'):
        results = self.__select_all_groups(account_id, order_by)
        return results

    def get_all_payment_methods(self, account_id, order_by='name'):
        results = self.__select_all_payment_methods(account_id, order_by)
        return results

    def get_all_category_types(self, order_by='name'):
        results = self.__select_all_category_types(order_by)
        return results

    def get_all_settlement_types(self, order_by='name'):
        results = self.__select_all_settlement_types(order_by)
        return results

    def get_all_settlement_rules(self, account_id, order_by='name'):
        results = self.__select_all_settlement_rules(account_id, order_by)
        return results

    def get_all_expenses(self, account_id, order_by='e.operationDate, c.name, e.name'):
        results = self.__select_all_expenses(account_id, order_by)
        return results

    def get_all_incomes(self, account_id, order_by='i.operationDate, c.name, i.name'):
        results = self.__select_all_incomes(account_id, order_by)
        return results

    def get_default_expense_category(self, account_id):
        result = self.__select_default_expense_category(account_id)
        return result

    def get_default_income_category(self, account_id):
        result = self.__select_default_income_category(account_id)
        return result

    def get_users_default_group(self, user_id):
        result = self.__select_users_default_group(user_id)

        return result

    def get_default_settlement_rule(self, account_id):
        result = self.__select_default_settlement_rule(account_id)
        return result

    def get_default_payment_method(self, account_id):
        result = self.__select_default_payment_method(account_id)
        return result

    def get_user(self, user_id):
        result = self.__select_user(user_id)
        return result

    def get_category(self, category_id):
        result = self.__select_category(category_id)
        return result

    def get_group(self, group_id):
        result = self.__select_group(group_id)
        return result

    def get_payment_method(self, payment_method_id):
        result = self.__select_payment_method(payment_method_id)
        return result

    def get_settlement_rule(self, settlement_rule_id):
        result = self.__select_settlement_rule(settlement_rule_id)
        return result

    def get_expense(self, expense_id):
        result = self.__select_expense(expense_id)
        return result

    def get_income(self, income_id):
        result = self.__select_income(income_id)
        return result

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

    def __insert_group(self, account_id, name, description, settlement_rule_id, is_main_group=False):
        sql = ('INSERT INTO group_tbl'
               '(name, description, settlementRuleId, isMainGroup, accountId)'
               'VALUES'
               '(%s, %s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, settlement_rule_id, is_main_group, account_id))
            self.db.commit()
            group_id = self.cursor.lastrowid
            return group_id
        except mysql.connector.Error as err:
            print(err.msg)
            raise
        finally:
            self.close_connection()

    def __insert_user_to_group(self, user_id, group_id):
        sql = ('INSERT INTO user_group_tbl'
               '(userId, groupId)'
               'VALUES'
               '(%s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id, group_id))
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

    def __insert_settlement_rule(self, account_id, name, description, settlement_type_id):
        sql = ('INSERT INTO settlement_rule_tbl'
               '(name, description, settlementTypeId, accountId)'
               'VALUES'
               '(%s, %s, %s, %s)')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (name, description, settlement_type_id, account_id))
            self.db.commit()
            settlement_rule_id = self.cursor.lastrowid
            return settlement_rule_id
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __insert_user_to_settlement_rule(self, settlement_rule_id, user_id, amount, priority):
        sql = ('INSERT INTO settlement_rule_user_tbl'
               '(settlementRuleId, userId, amount, priority)'
               'VALUES'
               '(%s, %s, %s, %s)')
        try:
            self.cursor.execute(sql, (settlement_rule_id, user_id, amount, priority))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)

    def __insert_users_to_settlement_rule(self):
        pass

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
        finally:
            self.close_connection()

    def __update_group(self, group_id, name, description, settlement_rule_id):
        sql = ('UPDATE group_tbl '
               'SET '
               'name = %s, '
               'description = %s, '
               'settlementRuleId = %s '
               'WHERE groupId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (group_id, name, description, settlement_rule_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __update_category(self, category_id, name, description, category_type_id):
        sql = ('UPDATE category_tbl '
               'SET '
               'name = %s, '
               'description = %s, '
               'categoryTypeId = %s '
               'WHERE categoryId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (category_id, name, description, category_type_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __update_settlement_rule(self, settlement_rule_id, name, description, settlement_type_id):
        sql = ('UPDATE settlement_rule_tbl '
               'SET '
               'name = %s, '
               'description = %s, '
               'settlementTypeId = %s '
               'WHERE settlementRuleId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (settlement_rule_id, name, description, settlement_type_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __update_expense(self, expense_id, operation_date, name, description, amount, payer_id, category_id, group_id):
        sql = ('UPDATE expense_tbl '
               'SET '
               'operationDate = %s, '
               'name = %s, '
               'description = %s, '
               'amount = %s, '
               'payerId = %s, '
               'categoryId = %s, '
               'groupId = %s '
               'WHERE expenseId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (operation_date, name, description, amount,
                                      payer_id, category_id, group_id, expense_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

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
        finally:
            self.close_connection()

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
        finally:
            self.close_connection()

    # -------------------------------------------- SELECT QUERIES ---------------------------------------------------- #

    def __select_account(self, username, password):
        sql = ('SELECT * FROM account_tbl '
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
        sql = ('SELECT * FROM user_tbl ' 
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

    def __select_all_categories(self, account_id, order_by='name'):
        sql = ('SELECT * FROM category_tbl ' 
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
        sql = ('SELECT * FROM group_tbl ' 
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
        sql = ('SELECT * FROM payment_method_tbl ' 
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
        sql = ('SELECT * FROM category_type_tbl ' 
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
        sql = ('SELECT * FROM settlement_type_tbl ' 
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

    def __select_all_settlement_rules(self, account_id, order_by='name'):
        sql = ('SELECT * FROM settlement_rule_tbl ' 
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

    def __select_all_expenses(self, account_id, order_by='e.operationDate, c.name, e.name'):
        sql = ('SELECT '
               'e.expenseId, '
               'e.operationDate, '
               'e.amount, '
               'e.name, '
               'u.username, '
               'c.name, '
               'p.name, '
               'g.name '
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

    def __select_all_incomes(self, account_id, order_by='i.operationDate, c.name, i.name'):
        sql = ('SELECT '
               'i.incomeId, '
               'i.operationDate, '
               'i.amount, '
               'i.name, '
               'c.name, '
               'g.name '
               'FROM income_tbl i '
               'LEFT JOIN category_tbl c '
               'ON i.categoryId=c.categoryId '
               'LEFT JOIN group_tbl g '
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

    def __select_default_expense_category(self, account_id):
        sql = ('SELECT * FROM category_tbl '
               'WHERE '
               'accountId=%s '
               'AND categoryTypeId=%s '
               'ORDER BY categoryId')
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
        sql = ('SELECT * FROM category_tbl '
               'WHERE '
               'accountId=%s '
               'AND categoryTypeId=%s '
               'ORDER BY categoryId')
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
        sql = ('SELECT g.* FROM group_tbl g '
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

    def __select_default_settlement_rule(self, account_id):
        sql = ('SELECT * FROM settlement_rule_tbl '
               'WHERE '
               'accountId=%s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (account_id,))
            result = self.cursor.fetchone()
            return result
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def __select_default_payment_method(self, account_id):
        sql = ('SELECT * FROM payment_method_tbl '
               'WHERE '
               'accountId=%s')
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
        sql = ('SELECT * FROM user_tbl ' 
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
        sql = ('SELECT * FROM category_tbl '
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
        sql = ('SELECT * FROM group_tbl '
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
        sql = ('SELECT * FROM payment_method_tbl '
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

    def __select_settlement_rule(self, settlement_rule_id):
        sql = ('SELECT * FROM settlement_rule_tbl '
               'WHERE '
               'settlementRuleId=%s ')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (settlement_rule_id,))
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
               'g.groupId '
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
               'g.groupId '
               'FROM income_tbl i '
               'LEFT JOIN category_tbl c '
               'ON i.categoryId=c.categoryId '
               'LEFT JOIN group_tbl g '
               'ON i.groupId=g.groupId '
               'WHERE '
               'g.accountId=%s ')
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
               'userId = %s, '
               'groupId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id, group_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def delete_users_from_group(self):
        pass

    def delete_category(self):
        pass

    def delete_settlement_rule(self):
        pass

    def __delete_user_from_settlement_rule(self, user_id, settlement_rule_id):
        sql = ('DELETE FROM settlement_rule_user_tbl '
               'WHERE '
               'userId = %s, '
               'settlementRuleId = %s')
        try:
            self.connect_to_db()
            self.cursor.execute(sql, (user_id, settlement_rule_id))
            self.db.commit()
        except mysql.connector.Error as err:
            print(err.msg)
        finally:
            self.close_connection()

    def delete_users_from_settlement_rule(self):
        pass

    def delete_expense(self):
        pass

    def delete_income(self):
        pass

    def delete_payment_method(self):
        pass
