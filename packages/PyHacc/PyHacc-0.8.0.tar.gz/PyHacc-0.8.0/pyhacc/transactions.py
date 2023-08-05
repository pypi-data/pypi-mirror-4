# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy import *
from PySide import QtCore, QtGui
from qtalchemy.dialogs import *
from qtalchemy.widgets import *

import sqlalchemy.sql.expression as expr
from PyHaccSchema import *
from PyHaccUI import *

class TransactionEditor(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a = TransactionEditor(None,row=s.query(Transactions).filter(Transactions.memo=="Groceries")[0])
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setWindowTitle("Transaction")
        self.setObjectName("Transaction Editor")

        self.setDataReader(Session, Transactions, "tid")

        main = QtGui.QVBoxLayout(self)
        top_grid = LayoutLayout(main,QtGui.QGridLayout())

        self.mapping = self.mapClass(Transactions)
        self.mapping.addBoundFieldGrid(top_grid,"date",0,0)
        self.mapping.addBoundFieldGrid(top_grid,"reference",0,2)
        self.mapping.addBoundFieldGrid(top_grid,"payee",1,0,columnSpan=3)
        self.mapping.addBoundFieldGrid(top_grid,"memo",2,0,columnSpan=3)

        self.tab = LayoutWidget(main, QtGui.QTabWidget())

        # first tab: transactions
        self.splitme = QtGui.QSplitter()
        self.tags_table = TableView()
        self.splits_table = TableView()
        self.splitme.addWidget(self.splits_table)
        self.splitme.addWidget(self.tags_table)
        self.tab.addTab(self.splitme, "&Transactions")

        # second tab:  receipt memo
        self.receipt = QtGui.QTextEdit(self)
        self.tab.addTab(self.receipt, "&Receipt")
        self.mapping.bind(self.receipt, "receipt")

        self.splits_model = ClassTableModel(Splits, ("account", "debit", "credit"), readonly=False)
        self.splits_table.setModel(self.splits_model, extensionId=suffixExtId(self, "Splits"))
        self.splits_table.setItemDelegate(AlchemyModelDelegate())

        self.tags_model = ClassTableModel(CheckableTagList, ("checked", "tag_name"), readonly=False, fixed_rows=True)
        self.tags_table.setModel(self.tags_model, extensionId=suffixExtId(self, "Tags"))
        self.tags_table.setItemDelegate(AlchemyModelDelegate())

        self.split_model_sel = self.splits_table.selectionModel()
        self.split_model_sel.selectionChanged.connect(self.setupChecks)

        self.buttonBox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.addButton(QtGui.QDialogButtonBox.Apply).clicked.connect(self.commitAndRefresh)
        self.buttonBox.addButton("To Cli&pboard", QtGui.QDialogButtonBox.ActionRole).clicked.connect(self.copyClipboard)
        
        self.actionBalance = QtGui.QAction("&Balance on Current Line", self)
        self.actionBalance.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_B)
        self.actionBalance.triggered.connect(self.balance)
        self.addAction(self.actionBalance)

        self.geo = WindowGeometry(self, position=False, tabs=[self.tab], splitters=[self.splitme])

        self.readData(row, row_id)

    def load(self):
        self.mapping.connect_instance(self.main_row)
        self.splits_model.reset_content_from_list(self.main_row.splits, self.main_row.session())

    def balance(self):
        index = self.splits_table.currentIndex()
        r = index.internalPointer()
        b = decimal.Decimal('0')
        for row in self.main_row.splits:
            if row is not r:
                b += AttrNumeric(2)(row.sum)
        debitIndex = self.splits_model.index(index.row(), 1, None)
        creditIndex = self.splits_model.index(index.row(), 2, None)
        for i in [debitIndex, creditIndex]:
            w = self.splits_table.indexWidget(i)
            self.splits_table.closeEditor(w, QtGui.QAbstractItemDelegate.NoHint)
        #self.splits_table.closePersistentEditor(debitIndex)
        #self.splits_table.closePersistentEditor(creditIndex)
        if b > 0:
            self.splits_model.setData(debitIndex, 0)
            self.splits_model.setData(creditIndex, b)
        else:
            self.splits_model.setData(debitIndex, -b)
            self.splits_model.setData(creditIndex, 0)

    def setupChecks(self):
        l = self.splits_table.selectedIndexes()
        if len(l) == 0:
            split = None
        else:
            split = l[0].internalPointer()

        if split:
            tags = self.main_row.session().query(Tags).order_by(Tags.name)
            checkable = [CheckableTagList(split, x) for x in tags]
            self.tags_model.reset_content_from_list(checkable)
        else:
            self.tags_table.setEnabled(False)

    def copyClipboard(self):
        QtGui.QApplication.clipboard().setText(self.main_row.ascii_repr())

from qtviews import *
from BalanceDock import DockCommands

def TransactionsCalendar(Session):
    win = QtGui.QMainWindow()

    win.toolbar = QtGui.QToolBar()

    today = Session.demo_end_date if hasattr(Session, 'demo_end_date') else datetime.date.today()
    prior_sunday = today-datetime.timedelta((today.weekday()+1)%7)
    day0 = prior_sunday-datetime.timedelta(28)
    day1 = prior_sunday+datetime.timedelta(14)
    c = CalendarView()
    c.Session = Session
    c.setDateRange(day0, 6, dayHeight=4)

    def load(obj):
        s = Session()
        trans = s.query(Transactions) \
                .filter(expr.and_(Transactions.date >= day0, Transactions.date <= day1)) \
                .all()
        c.setEventList(trans,
                startDate=lambda x: x.date,
                endDate=lambda x: x.date,
                text=lambda x: x.payee if x.payee != "" else x.memo,
                bkColor=lambda x: QtGui.QColor(0, 0, 224))
        s.close()

    win.setCentralWidget(c)
    win.title = 'Transaction Calendar'
    win.factory = 'TransactionsCalendar'
    win.tranEntity = TransactionEntity(Session, win)
    win.entity = DockCommands(Session, win)
    win.bindings = win.entity.commands
    win.tranBindings = win.tranEntity.basicNew
    win.tranBindings.fillToolbar(win.toolbar)
    win.toolbar.addSeparator()
    win.bindings.fillToolbar(win.toolbar)
    win.bindings.refresh.connect(load)
    win.tranBindings.refresh.connect(load)
    win.addToolBar(win.toolbar)

    import pyhacc.reports as reports
    win.entity.ReportClass = reports.TransactionList

    def contextMenu(pos, tran):
        c.thingMenu = QtGui.QMenu(c)
        c.thingBinding = c.entity.itemCommands.withObject(tran, objectConverter=lambda x:x.tid)
        c.thingBinding.fillMenu(c.thingMenu)
        c.thingBinding.refresh.connect(load)
        c.thingMenu.popup(c.viewport().mapToGlobal(pos))

    c.contextMenuCalendarEvent.connect(contextMenu)

    c.entity = TransactionEntity(Session, c)
    c.doubleClickCalendarEvent.connect(lambda tran: c.entity.view(tran.tid))

    load(None)

    return win

from qtalchemy.PBSearchDialog import PBSearchableListDialog

class TransactionsByDate(PBMdiTableView):
    title = 'Transaction List'
    factory = 'TransactionsByDate'

    def __init__(self,Session):
        extensionId = "{0}/MDIRecent".format(self.__class__.__name__)

        PBSearchableListDialog.__init__(self, extensionId=extensionId)

        self.Session = Session
        self.entity = TransactionEntity(Session, self)
        self.base_query, converter = self.entity.list_query_converter()
        self.base_query = self.base_query.order_by(expr.desc(Transactions.date))
        self.table.setModel(QueryTableModel(self.base_query, ssrc=Session,objectConverter=converter), extensionId=suffixExtId(self,"Table"))
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)

        self.table.model().reset_content_from_session()

from sqlalchemy.orm import column_property

class TransactionsPopular(PBMdiTableView):
    title = 'Popular Transactions'
    factory = 'TransactionsPopular'

    def __init__(self,Session):
        extensionId = "{0}/MDIPopular".format(self.__class__.__name__)

        PBSearchableListDialog.__init__(self, extensionId=extensionId)

        self.Session = Session
        self.entity = TransactionEntity(Session, self)
        q = Query((Transactions.payee,Transactions.memo,func.count().label("count")))\
                .filter(Transactions.date>datetime.date.today()-datetime.timedelta(366))\
                .group_by(Transactions.payee,Transactions.memo).order_by(expr.desc("count")).subquery()
        q2= Query((q.c.count.label("count"),q.c.payee,q.c.memo)).order_by(expr.desc(q.c.count)).subquery()
        
        class Thing(object):
            __tablename__ = "sam"

            @property
            def tid(self):
                s = Session()
                r = s.query(Transactions.tid)\
                        .filter(Transactions.memo==self.memo)\
                        .filter(Transactions.payee==self.payee)\
                        .order_by(expr.desc(Transactions.date)).limit(1).one()[0]
                s.close()
                return r

        mapper(Thing, q2, primary_key=[q2.c.memo, q2.c.payee])

        self.base_query, converter = Query(Thing), lambda x: x.tid
        #self.base_query = self.base_query.order_by(expr.desc(Transactions.date))
        self.table.setModel(QueryTableModel(self.base_query, ssrc=Session,objectConverter=converter), extensionId=suffixExtId(self,"Table"))
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)

        self.table.model().reset_content_from_session()
