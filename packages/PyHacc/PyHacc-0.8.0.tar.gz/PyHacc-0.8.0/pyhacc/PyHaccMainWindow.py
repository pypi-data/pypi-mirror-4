# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import *
from PySide import QtCore, QtGui
import reports
import datetime
import qtviews
from sqlalchemy import MetaData, ForeignKey, create_engine, select, join

from PyHaccSchema import *
from PyHaccLib import *
from transactions import *
from BalanceDock import *
from DateDock import *

def module_ver(name):
    import importlib
    try:
        if name == "Python":
            import sys
            v = sys.version.split(' ')[0]
        elif name == "PyQt4":
            x = importlib.import_module("PyQt4.QtCore")
            v = x.PYQT_VERSION_STR
        else:
            x = importlib.import_module(name)
            v = x.__version__
    except:
        v = "unknown version"
    return "{0} ({1})".format(name, v)

def AccountTypeList(Session):
    x = PBMdiTableView(Session, AccountTypeEntity)
    x.title = 'Account Type List'
    x.appType = 'AccountTypeList'
    return x

def JournalList(Session):
    x = PBMdiTableView(Session, JournalEntity)
    x.title = 'Journal List'
    x.appType = 'JournalList'
    return x

def AccountList(Session):
    x = PBMdiTableView(Session, AccountEntity)
    x.title = 'Account List'
    x.appType = 'AccountList'
    return x

def TagList(Session):
    x = PBMdiTableView(Session, TagEntity)
    x.title = 'Tag List'
    x.appType = 'TagList'
    return x

def BalanceAccounts(Session):
    w = BalanceSheetAccountBalances(None, Session)
    w.refresh()
    Session.balance_refresh = w.refresh
    return w

def ProfitAndLossAccounts(Session):
    w = ProfitAndLossAccountBalances(None, Session)
    w.refresh()
    Session.balance_refresh = w.refresh
    return w

class MainWindow(QtGui.QMainWindow, qtviews.TabbedWorkspaceMixin):
    WindowName = 'PyHaccMainWindow'

    fileCommands = CommandMenu("_file_menu")
    accountsCommands = CommandMenu("_accounts_menu")
    transactionsCommands = CommandMenu("_transactions_menu")
    windowCommands = CommandMenu("_window_menu")
    helpCommands = CommandMenu("_help_menu")

    def __init__(self, parent=None, Session=None):
        super(MainWindow, self).__init__(parent)

        self.setWindowIcon(QtGui.QIcon(":/pyhacc/money-2.ico"))
        self.setObjectName("MainWindow")
        
        self.initTabbedWorkspace()
        self.updateViewFactory({
            'TagList': lambda:  TagList(Session),
            'AccountList': lambda: AccountList(Session),
            'AccountTypeList': lambda: AccountTypeList(Session),
            'JournalList': lambda: JournalList(Session),
            'BalanceAccounts': lambda: BalanceAccounts(Session),
            'PandLAccounts': lambda: ProfitAndLossAccounts(Session),
            'TransactionsByDate': lambda: TransactionsByDate(Session),
            'TransactionsPopular': lambda: TransactionsPopular(Session),
            'TransactionsCalendar': lambda: TransactionsCalendar(Session),
            'Date': lambda: DateWidget(None, Session)
            })

        self.createMenus()
        self.Session = Session

        self.updateWindowTitle()
        self.setMinimumSize(160,160)
        self.resize(480,320)

        self.loadView(self.WindowName, defaultDocks=['BalanceAccounts'])

    def updateWindowTitle(self):
        session = self.Session()
        options = session.query(Options).one()
        self.setWindowTitle(self.tr("PyHacc - {0}").format(options.data_name))
        session.close()

    @fileCommands.command("&Options...", statusTip="Set Global Options")
    def options(self):
        session = self.Session()
        options = session.query(Options).one()
        dlg = BoundDialog(self)
        main = QtGui.QVBoxLayout(dlg)
        dlg.setDataReader(self.Session, Options, None)
        dlg.readData(options, load=False)
        m = dlg.mapClass(Options)
        m.addBoundForm(main, ["data_name"])
        m.connect_instance(options)

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox())
        buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
        buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dlg.accept)
        buttonbox.rejected.connect(dlg.reject)
        dlg.show()
        dlg.exec_()
        session.close()

        self.updateWindowTitle()

    @fileCommands.command("Date &Default", statusTip="Set a transaction date")
    def dateDefaulter(self):
        self.addWorkspaceWindowOrSelect('Date')

    @fileCommands.command("View Ta&gs", statusTip="View Tag List", key="Ctrl+G")
    def tagList(self):
        self.addWorkspaceWindowOrSelect('TagList')

    fileCommands.command("E&xit", key="Ctrl+Q", statusTip="Exit the application")(QtGui.QMainWindow.close)

    @accountsCommands.command("View &Journals", statusTip="View Journal List", key="Ctrl+J")
    def jrnList(self):
        self.addWorkspaceWindowOrSelect('JournalList')

    @accountsCommands.command("Balance Accounts", statusTip="View Balances")
    def winBalanceAccounts(self):
        self.addWorkspaceWindowOrSelect('BalanceAccounts')

    @accountsCommands.command("P&&L Accounts", statusTip="View P&L Balances")
    def winProfitAndLossAccounts(self):
        self.addWorkspaceWindowOrSelect('PandLAccounts')

    @accountsCommands.command("View &Accounts", statusTip="View Account List", key="Ctrl+A")
    def acctList(self):
        self.addWorkspaceWindowOrSelect('AccountList')

    @accountsCommands.command("View Account &Types", statusTip="View Account type List", key="Ctrl+T")
    def acctTypeList(self):
        self.addWorkspaceWindowOrSelect('AccountTypeList')

    @transactionsCommands.command("&Recent Transactions...", statusTip="View Recent Transactions", key="Ctrl+R")
    def tranRecent(self):
        self.addWorkspaceWindowOrSelect('TransactionsByDate')

    @transactionsCommands.command("&Calendar...", statusTip="Calendar Transaction")
    def tranCalendar(self):
        self.addWorkspaceWindowOrSelect('TransactionsCalendar')

    @transactionsCommands.command("&Popular...", statusTip="Popular Transaction")
    def tranPopular(self):
        self.addWorkspaceWindowOrSelect('TransactionsPopular')

    @transactionsCommands.command("&New...", statusTip="New Transaction", key="Ctrl+N", type="new")
    def tranNew(self):
        b = TransactionEntity(self.Session, self)
        b.new()

    def updateEditMenu(self):
        self.editMenu.clear()

        activeWindow = self.workspace.currentWidget()
        if hasattr(activeWindow, "bindings"):
            activeWindow.bindings.fillMenu(self.editMenu)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowCommands.fillMenu(self.windowMenu)
        
        if self.workspace.count() > 0:
            self.windowMenu.addSeparator()

        self.tabsInWindowMenu()

    def reports(self):
        try:
            return self.report_list
        except AttributeError, e:
            self.report_list = []
            for r in reports.report_classes:
                act=QtGui.QAction(self.tr(r.name.replace("&","&&")), self)
                act.setStatusTip(self.tr(r.name+" Report"))
                act.triggered.connect(reports.ReportChooser(self,r))
                self.report_list.append(act)

            return self.report_list

    @windowCommands.command("Cl&ose", statusTip="Close the active window", key="Ctrl+W")
    def closeActiveWindow(self):
        if self.workspace.currentIndex() >= 0:
            self.workspace.removeTab(self.workspace.currentIndex())

    @windowCommands.command("Close &All", statusTip="Close all the windows")
    def closeAllWindows(self):
        while self.workspace.count() > 0:
            self.workspace.removeTab(0)

    @helpCommands.command("&About", statusTip="Show the application's About box")
    def about(self):
        modules = ["Python", "pyhacc", "sqlalchemy", "qtalchemy", "qtviews", "fuzzyparsers", "geraldo", QtCore.__name__.split('.')[0]]
        vers = "<br />".join([module_ver(m) for m in modules])
        QtGui.QMessageBox.about(self, self.tr("About Menu"),
                self.tr("""This is PyHacc!<br />
<a href="http://bitbucket.org/jbmohler/pyhacc">Bit Bucket Page</a>

<p>Library Versions:  <br />{vers}</p>

<p>Copyright 2010-2012 Joel B. Mohler</p>""".format(vers=vers)))

    @helpCommands.command("About &Qt", statusTip="Show the Qt library's About box")
    def aboutQt(self):
        QtGui.qApp.aboutQt()

    def createMenus(self):
        self.fileCommands.fillMenu(self.menuBar().addMenu(self.tr("&File")))

        self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.editMenu.aboutToShow.connect(self.updateEditMenu)

        self.accountsCommands.fillMenu(self.menuBar().addMenu(self.tr("&Accounts")))

        self.transactionsCommands.fillMenu(self.menuBar().addMenu(self.tr("&Transactions")))

        self.reportMenu = self.menuBar().addMenu(self.tr("&Reports"))
        for r in self.reports():
            self.reportMenu.addAction(r)

        self.windowMenu = self.menuBar().addMenu(self.tr("&Window"))
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)
        self.windowCommands.fillMenu(self.windowMenu)

        self.helpCommands.fillMenu(self.menuBar().addMenu(self.tr("&Help")))

    def closeEvent(self, event):
        self.saveView(self.WindowName)
        super(MainWindow, self).closeEvent(event)
