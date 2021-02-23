import datetime
import re

from kivy.app import App
from kivy.properties import NumericProperty, StringProperty, ObjectProperty
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen
from kivymd.uix.picker import MDDatePicker

from reports import ReportFactory, BalanceReport, SettlementReport, PaymentMethodReport
from screens.gui_elements import CenteredLabel, ButtonWithData


class ReportsListScreen(Screen):
    pass


class ReportScreen(Screen):
    group_id = NumericProperty(0)
    category_id = NumericProperty(0)
    groups_dropdown = DropDown()
    reports_dropdown = DropDown()
    date_from = StringProperty('')
    date_to = StringProperty('')
    report = ObjectProperty(0)

    reports_list = [
        {'id': 1, 'name': 'BalanceReport', 'name_pl': 'Raport bilansu'},
        {'id': 2, 'name': 'SettlementReport', 'name_pl': 'Raport rozliczenia'},
        {'id': 3, 'name': 'PaymentMethodReport', 'name_pl': 'Raport metod płatności'},
    ]

    def on_pre_leave(self, *args):
        self.clear_input_fields()

    def on_pre_enter(self, *args):
        self.add_groups_dropdown()
        self.add_reports_dropdown()

    def add_groups_dropdown(self):
        db_manager = App.get_running_app().db_manager
        app = App.get_running_app()
        groups_list = db_manager.get_all_groups(app.root.account_id)

        for group in groups_list:
            btn = ButtonWithData(text=group['name'],
                                 button_data={'text': group['name'], 'id': group['group_id']})
            btn.bind(on_release=lambda btn: self.groups_dropdown.select(btn.button_data))
            self.groups_dropdown.add_widget(btn)
        groups_btn = self.ids.groups_btn
        groups_btn.bind(on_release=self.groups_dropdown.open)
        self.groups_dropdown.bind(on_select=lambda instance, x: setattr(groups_btn, 'button_data', x))

    def add_reports_dropdown(self):

        for report in self.reports_list:
            btn = ButtonWithData(text=report['name_pl'],
                                 button_data={'text': report['name_pl'], 'id': report['id']})
            btn.bind(on_release=lambda btn: self.reports_dropdown.select(btn.button_data))
            self.reports_dropdown.add_widget(btn)
        reports_btn = self.ids.reports_btn
        reports_btn.bind(on_release=self.reports_dropdown.open)
        self.reports_dropdown.bind(on_select=lambda instance, x: setattr(reports_btn, 'button_data', x))

    def set_group_id(self):
        self.group_id = self.ids.groups_btn.button_data['id']

    def set_report(self):
        for report in self.reports_list:
            if report['id'] == self.ids.reports_btn.button_data['id']:
                self.report = ReportFactory.ReportFactory.factory(report['name'])
                break

    def clear_message(self):
        self.ids.message.text = ''

    def validate_input(self, date_from, date_to):
        return self.validate_dates(date_from, date_to) \
               and self.validate_group_id() \
               and self.validate_report()

    def validate_dates(self, date_from, date_to):
        valid = False

        if self.validate_date(date_from) and self.validate_date(date_to):
            d_from = datetime.datetime.strptime(date_from, '%d.%m.%Y')
            d_to = datetime.datetime.strptime(date_to, '%d.%m.%Y')
            if d_from > d_to:
                self.show_message('Końcowa data nie może być wcześniejsza niż początkowa.')
            else:
                valid = True
        return valid

    def validate_date(self, date):
        valid = False
        date_regex = re.compile(r'([0-9]{2}\.[0-9]{2}\.[0-9]{4})')
        date_match = re.search(date_regex, date)
        if date == '':
            self.show_message('Data jest polem wymaganym.')
        elif date_match is None or date_match.group(1) != date:
            self.show_message('Błędny format daty. (DD.MM.RRRR)')
        else:
            valid = True
        return valid

    def show_datepicker(self):
        picker = MDDatePicker(mode='range')
        picker.bind(on_save=self.save_date, on_cancel=self.cancel_save_date)
        picker.open()

    def save_date(self, instance, value, date_range):
        if not date_range:
            value = value.strftime('%d.%m.%Y')
            self.date_from = str(value)
            self.date_to = str(value)
        else:
            self.date_from = date_range[0].strftime('%d.%m.%Y')
            self.date_to = date_range[-1].strftime('%d.%m.%Y')
        print(self.date_from, self.date_to)

    def cancel_save_date(self, instance, value):
        pass

    def validate_group_id(self):
        valid = False
        self.set_group_id()
        if self.group_id == 0:
            self.show_message('Wybór grupy jest obowiązkowy.')
        else:
            valid = True
        return valid

    def validate_report(self):
        valid = False
        self.set_report()
        if self.report == 0:
            self.show_message('Wybór raportu jest obowiązkowy.')
        else:
            valid = True
        return valid

    def clear_input_fields(self):
        self.clear_message()
        self.date_to = ''
        self.date_from = ''
        self.ids.summary.text = ''
        self.ids.groups_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.ids.reports_btn.button_data = {'text': 'Wybierz', 'id': 0}
        self.groups_dropdown.clear_widgets()
        self.reports_dropdown.clear_widgets()
        self.report = 0
        self.ids.box.clear_widgets()

    def show_message(self, message):
        self.ids.message.text = message

    def print_report(self):
        box = self.ids.box
        self.ids.box.clear_widgets()
        if self.validate_input(self.date_from, self.date_to):
            date_from = datetime.datetime.strptime(self.date_from, '%d.%m.%Y')
            date_to = datetime.datetime.strptime(self.date_to, '%d.%m.%Y')

            report_data = self.generate_report(date_from, date_to)

            for item in report_data['results']:
                box.add_widget(CenteredLabel(text=item))

            self.ids.summary.text = report_data['summary']
            self.show_message('')

    def generate_report(self, date_from, date_to):
        account_id = App.get_running_app().root.account_id
        report_data = {'results': [], 'summary': ''}
        if isinstance(self.report, (BalanceReport.BalanceReport,
                                    SettlementReport.SettlementReport,
                                    PaymentMethodReport.PaymentMethodReport)):
            report_data = self.report.prepare_report(
                self.report.generate_report_data(account_id, self.group_id, date_from, date_to))
        return report_data
