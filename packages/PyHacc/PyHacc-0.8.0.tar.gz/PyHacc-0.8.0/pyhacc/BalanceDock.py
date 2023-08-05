# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PySide import QtCore, QtGui
from PyHaccSchema import *
import threading

class QueryCheck(threading.Thread):
    def __init__(self, Session, query):
        threading.Thread.__init__(self)
        self.Session = Session
        self.query = query._clone()

    def run(self):
        s = self.Session()
        self.query.session = s
        self.result = self.query.all()
        self.query.session.close()

class DockCommands(object):
    def __init__(self, Session, parent):
        self.Session = Session
        self.parent = parent
        self.ReportClass = None

    commands = CommandMenu("_commands")

    @commands.itemAction("&Print", iconFile=":/pyhacc/document-print.ico", requireSelection=False, viewRelated=False)
    def cmd_print(self, id=None):
        if self.ReportClass is None:
            raise RuntimeError("DockCommands report class is not initialized.")

        bs = self.ReportClass(self.Session)
        bs.construct()
        import tempfile
        import os
        import qtalchemy.xplatform as xplatform
        tempdir = tempfile.mkdtemp()
        fullpath = os.path.join(tempdir, bs.filename + ".pdf")
        bs.geraldo(fullpath, None)
        xplatform.xdg_open(fullpath)

    @commands.itemAction("&Refresh", iconFile=":/pyhacc/refresh.ico", requireSelection=False, viewRelated=False)
    def refresh(self, id=None):
        # do nothing, just be a place-holder for save/load bracketing
        pass

class AccountBalanceList(QtGui.QWidget):
    def __init__(self, parent, Session):
        super(AccountBalanceList, self).__init__(parent)

        self.Session = Session

        vbox = QtGui.QVBoxLayout(self)
        self.toolbar = LayoutWidget(vbox, QtGui.QToolBar())
        self.table = LayoutWidget(vbox, TableView(self))

        self.q = self.query()
        self.table.setModel(QueryTableModel(self.q, ssrc=self.Session, objectConverter = lambda x: x.id), extensionId=suffixExtId(self, "Table"))

        self.entity = AccountEntity(self.Session, self.parent())
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=False)
        self.bindings.fillToolbar(self.toolbar)

        self.toolbar.addSeparator()

        self.entity2 = DockCommands(self.Session, self.parent())
        self.bindings2 = self.entity2.commands.withView(self.table, bindDefault=False)
        self.bindings2.fillToolbar(self.toolbar)
        self.bindings2.refresh.connect(self.refresh)

        self.loading = None

    def refresh(self):
        if self.loading is not None:
            return

        self.loading = QueryCheck(self.Session, self.q)
        self.loading.start()

        self.timer = QtCore.QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.checkLoad)

    def checkLoad(self):
        if not self.loading.isAlive():
            self.timer.stop()
            self.timer = None
            self.table.model().reset_content_from_list(self.loading.result)
            self.loading = None

class BalanceSheetAccountBalances(AccountBalanceList):
    """
    >>> app, Session = qtappsession()
    >>> a = BalanceSheetAccountBalances(None, Session)
    """

    title = 'Balance Accounts'
    factory = 'BalanceAccounts'

    def __init__(self, parent, Session):
        super(BalanceSheetAccountBalances, self).__init__(parent, Session)

        import pyhacc.reports as reports
        self.entity2.ReportClass = reports.BalanceSheet

        self.setWindowTitle("Balances")
        self.setObjectName("BalanceDock")

    def query(self):
        self.qsub = Query((Splits.account_id.label("account_id"), func.sum(Splits.sum).label("sum"))) \
                        .join(Accounts).join(AccountTypes).join(Transactions) \
                        .filter(AccountTypes.balance_sheet==True) \
                        .filter(AccountTypes.retained_earnings==False) \
                        .group_by(Splits.account_id).subquery()

        self.pre_q = Query((Accounts.id, Accounts.name, AccountTypes.name.label("type"), self.qsub.c.sum.label("Balance"))) \
                        .join((self.qsub, self.qsub.c.account_id==Accounts.id)) \
                        .join(AccountTypes) \
                        .filter(AccountTypes.balance_sheet==True) \
                        .filter(AccountTypes.retained_earnings==False) \
                        .filter(self.qsub.c.sum!=decimal.Decimal()) \
                        .order_by(AccountTypes.sort, Accounts.name)

        return self.pre_q

class ProfitAndLossAccountBalances(AccountBalanceList):
    """
    >>> app, Session = qtappsession()
    >>> a = ProfitAndLossAccountBalances(None, Session)
    """

    title = 'Profit && Loss Accounts'
    factory = 'PandLAccounts'

    def __init__(self, parent, Session):
        super(ProfitAndLossAccountBalances, self).__init__(parent, Session)

        import pyhacc.reports as reports
        self.entity2.ReportClass = reports.ProfitAndLoss

        self.setWindowTitle("Profit && Loss")
        self.setObjectName("PandLAccounts")

    def query(self):
        tranCriteria = expr.and_(Transactions.date>=datetime.datetime(2012, 1, 1), Transactions.date<=datetime.datetime(2012, 12, 31))

        self.qsub = Query((Splits.account_id.label("account_id"), func.sum(Splits.sum).label("sum"))) \
                        .join(Accounts).join(AccountTypes).join(Transactions) \
                        .filter(tranCriteria) \
                        .filter(AccountTypes.balance_sheet==False) \
                        .group_by(Splits.account_id).subquery()

        self.pre_q = Query((Accounts.id, Accounts.name, AccountTypes.name.label("type"), self.qsub.c.sum.label("Balance"))) \
                        .join((self.qsub, self.qsub.c.account_id==Accounts.id)) \
                        .join(AccountTypes) \
                        .filter(AccountTypes.balance_sheet==False) \
                        .filter(self.qsub.c.sum!=decimal.Decimal()) \
                        .order_by(AccountTypes.sort, Accounts.name)

        return self.pre_q
