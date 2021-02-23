from reports.BalanceReport import BalanceReport
from reports.SettlementReport import SettlementReport
from reports.PaymentMethodReport import PaymentMethodReport


class ReportFactory(object):
    def factory(type):
        if type == "BalanceReport":
            return BalanceReport()
        if type == "SettlementReport":
            return SettlementReport()
        if type == "PaymentMethodReport":
            return PaymentMethodReport()

    factory = staticmethod(factory)
