# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy import PBTableTab
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PySide import QtCore, QtGui
from PyHaccSchema import *
from PyHaccLib import *


class ReconcileCommands(object):
    def __init__(self, Session, parent):
        self.Session = Session
        self.parent = parent

    commands = CommandMenu("_commands")

    #@commands.itemAction("&Print", iconFile=":/pyhacc/document-print.ico", requireSelection=False, viewRelated=False)
    #def print_(self, id=None):
    #    q = self.query(self.Session)
    #    # TODO:  implement the report!

    @commands.itemAction("&Refresh", iconFile=":/pyhacc/refresh.ico", requireSelection=False, viewRelated=False)
    def refresh(self, id=None):
        # do nothing, just be a place-holder for save/load bracketing
        pass

class AccountEditor(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a = AccountEditor(None,row=s.query(Accounts).filter(Accounts.name=="Cash").one())
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setObjectName("AccountsInfo")
        self.setDataReader(Session, Accounts, "id")

        main = QtGui.QVBoxLayout(self)
        top_grid = LayoutLayout(main,QtGui.QGridLayout())

        self.mm = self.mapClass(Accounts)
        self.mm.addBoundFieldGrid(top_grid,"name",0,0)
        self.mm.addBoundFieldGrid(top_grid,"type",0,2)

        self.tab = LayoutWidget(main,QtGui.QTabWidget())

        self.accounting_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.accounting_tab),["journal_name","retearn_name","description"])
        self.tab.addTab( self.accounting_tab,"&Accounting" )

        self.institution_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.institution_tab),"instname,instaddr1,instaddr2,instcity".split(','))
        self.tab.addTab( self.institution_tab,"&Institution" )

        self.rec_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.rec_tab),"rec_note".split(','))
        self.tab.addTab( self.rec_tab,"&Reconciliation" )

        self.transactions_tab = PBTableTab(self, Session, TransactionEntity, 
                        [(Splits.account_id, lambda dataContext: dataContext.id)], 
                        Query((Transactions.tid.label("id"),Transactions.date, Transactions.reference, Transactions.payee, Transactions.memo, Splits.sum)).join(Splits).order_by(Transactions.date.desc()), 
                        extensionId=suffixExtId(self, "Transactions"))
        self.tab.addTab(self.transactions_tab,"Tran&sactions")

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self, position=False, tabs=[self.tab])

        self.readData(row, row_id)

    def load(self):
        self.mm.connect_instance(self.main_row)
        self.transactions_tab.refresh(self.main_row)
        self.setWindowTitle( "Account Information - {0.name}".format(self.main_row) )

class SplitQuery(ModelObject):
    def __init__(self):
        self.thisTag = None
        self.thisAccount = None
        self.thisType = None
        self.fiscal_range = "This Year"

    def set(self, account_id, type_id, tag_id):
        if tag_id is not None:
            self.thisTag = self.session().query(Tags).filter(Tags.id==tag_id).one()
        if type_id is not None:
            self.thisType = self.session().query(AccountTypes).filter(AccountTypes.id==type_id).one()
        if account_id is not None:
            self.thisAccount = self.session().query(Accounts).filter(Accounts.id==account_id).one()

    classEvents = ModelObject.Events()

    tag = TagReferral("Tag", "thisTag") 
    account = AccountReferral("Account", "thisAccount") 
    type_name = AccountTypeReferral("Account Type","thisType")
    fiscal_range = FiscalRangeAttr(str, "Range")
    begin_date = UserAttr(datetime.date, "Beginning Date")
    end_date = UserAttr(datetime.date, "Ending Date")
    tagged = UserAttr(bool, "Only show tagged splits")

    fiscalDateRangeEvents(classEvents, "fiscal_range", "begin_date", "end_date")

    def query(self, Session):
        session = Session()
        tag = session.query(Tags).filter(Tags.id==self.thisTag.id).one()
        q = session.query(Splits).join(Transactions)
        if self.begin_date is not None:
            q = q.filter(Transactions.date>=self.begin_date)
        if self.end_date is not None:
            q = q.filter(Transactions.date<=self.end_date)
        if self.thisType is not None:
            q = q.join(Accounts).filter(Accounts.type_id==self.thisType.id)
        if self.thisAccount is not None:
            q = q.filter(Splits.account_id==self.thisAccount.id)
        if self.tagged:
            q = q.join(Tagsplits).filter(Tagsplits.tag_id==self.thisTag.id)
        q = q.order_by(Transactions.date, Transactions.payee)
        return session, tag, q

class TagWorksheet(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a = TagWorksheet(None, account_id=s.query(Accounts).filter(Accounts.name=="Cash").one().id, Session=Session)
    """
    def __init__(self, parent, account_id=None, type_id=None, tag_id=None, Session=None):
        BoundDialog.__init__(self,parent)

        self.setWindowTitle("Split Tagger Worksheet")
        self.setObjectName("TagWorksheet")
        self.setDataReader(Session, SplitQuery, None)

        main = QtGui.QHBoxLayout(self)
        left_controls = LayoutLayout(main,QtGui.QVBoxLayout())

        self.mm = self.mapClass(SplitQuery)
        self.mm.addBoundForm(left_controls,["tag", "fiscal_range", "begin_date", "end_date", "account", "type_name", "tagged"])

        right_controls = LayoutLayout(main, QtGui.QVBoxLayout())
        self.toolbar = LayoutWidget(right_controls, QtGui.QToolBar())
        self.checkTable = LayoutWidget(right_controls, TableView(extensionId=suffixExtId(self, "Table")))
        self.model = ClassTableModel(SplitTaggerSimple,"tagged,debit,credit,date,reference,payee,memo".split(','), readonly=False, fixed_rows=True)
        self.checkTable.setModel(self.model)
        main.setStretch(1,15) # massively favor the table side of things

        self.buttonBox = LayoutWidget(left_controls,QtGui.QDialogButtonBox())

        self.okBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.cancelBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)
        self.refreshBtn = self.buttonBox.addButton("Refresh", QtGui.QDialogButtonBox.ActionRole)
        self.refreshBtn.clicked.connect(lambda checked=False: self.load())

        self.geo = WindowGeometry(self)

        self.entity = TransactionEntity(Session, self)
        self.binding = self.entity.itemCommands.withView(self.checkTable, objectConverter=lambda x:x.split.Transaction.tid)
        self.binding.fillToolbar(self.toolbar)
        self.binding.preCommand.connect(self.preCommandSave)
        self.binding.refresh.connect(self.refresh)

        self.toolbar.addSeparator()

        self.entity2 = ReconcileCommands(self.Session, self.parent())
        self.bindings2 = self.entity2.commands.withView(self.checkTable, bindDefault=False)
        self.bindings2.fillToolbar(self.toolbar)
        self.bindings2.preCommand.connect(self.preCommandSave)
        self.bindings2.refresh.connect(self.refresh)

        self.queryStuff = SplitQuery()
        self.queryStuffSession = Session()
        self.queryStuffSession.npadd(self.queryStuff)
        self.queryStuff.set(account_id=account_id, type_id=type_id, tag_id=tag_id)

        self.entity2.queryStuff = self.queryStuff

        self.main_row = self.queryStuff
        self.load()
        #self.readData(self.queryStuff, None)

    def load(self):
        self.submit()
        self.checkTable.setEnabled(self.queryStuff.thisTag is not None)

        if self.queryStuff.thisTag is not None:
            progress = QtGui.QProgressDialog("Loading...", "", 0, 2, self)
            progress.setCancelButton(None)
            progress.setMinimumDuration(1)
            progress.setWindowModality(QtCore.Qt.WindowModal)

            #TODO: it seems I don't know how to make the QProgressDialog show at a convenient point
            progress.setValue(0)

            self.session, self.tag, q = self.queryStuff.query(self.Session)
            self.split_list = q.all()
            progress.setValue(1)

            self.shown_check_split_list = []
            for i in range(len(self.split_list)):
                progress.setValue(i)
                split = self.split_list[i]
                self.shown_check_split_list.append(SplitTaggerSimple(split, self.tag))

            self.model.reset_content_from_list(self.shown_check_split_list)
            for x in self.shown_check_split_list:
                instanceEvent(x, "set", "tagged")(lambda obj, attr, value: self.model.rowEmitChange(obj, "all"))

            progress.setValue(2)

            progress.hide()

        self.mm.connect_instance(self.queryStuff)

        if self.main_row.thisAccount is not None:
            self.setWindowTitle( "Account Tag Worksheet - {0}".format(self.main_row.thisAccount.name) )

class AccountReconcile(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a = AccountReconcile(None,row=s.query(Accounts).filter(Accounts.name=="Cash").one())
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setObjectName("AccountReconciliation")
        self.setDataReader(Session, Accounts, "id")

        main = QtGui.QHBoxLayout(self)
        left_controls = LayoutLayout(main,QtGui.QVBoxLayout())

        self.mm = self.mapClass(SplitTagger.ReconciliationStatus)
        self.mm.addBoundForm(left_controls,["reconciled_balance","pending_balance","outstanding_balance"])
        self.mm_account = self.mapClass(Accounts)
        self.mm_account.addBoundForm(left_controls,["rec_note"])

        right_controls = LayoutLayout(main, QtGui.QVBoxLayout())
        self.toolbar = LayoutWidget(right_controls, QtGui.QToolBar())
        self.checkTable = LayoutWidget(right_controls, TableView(extensionId=suffixExtId(self, "Table")))
        self.model = ClassTableModel(SplitTagger,"pending,reconciled,debit,credit,date,reference,payee,memo".split(','), readonly=False, fixed_rows=True)
        self.checkTable.setModel(self.model)
        main.setStretch(1,15) # massively favor the table side of things

        self.buttonBox = LayoutWidget(left_controls,QtGui.QDialogButtonBox())

        self.okBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.reconcileBtn = self.buttonBox.addButton("&Reconcile",QtGui.QDialogButtonBox.ActionRole)
        self.reconcileBtn.clicked.connect(self.reconcile_now)
        self.cancelBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self)

        self.entity = TransactionEntity(Session, self)
        self.binding = self.entity.itemCommands.withView(self.checkTable, objectConverter=lambda x:x.split.Transaction.tid)
        self.binding.fillToolbar(self.toolbar)
        self.binding.preCommand.connect(self.preCommandSave)
        self.binding.refresh.connect(self.refresh)

        self.toolbar.addSeparator()

        self.entity2 = ReconcileCommands(self.Session, self.parent())
        self.bindings2 = self.entity2.commands.withView(self.checkTable, bindDefault=False)
        self.bindings2.fillToolbar(self.toolbar)
        self.bindings2.preCommand.connect(self.preCommandSave)
        self.bindings2.refresh.connect(self.refresh)

        self.readData(row, row_id)

    def load(self):
        self.recStatus = SplitTagger.ReconciliationStatus()

        self.tagRec = self.session.query(Tags).filter(Tags.name==Tags.Names.BankReconciled).one()
        self.tagPen = self.session.query(Tags).filter(Tags.name==Tags.Names.BankPending).one()
        q = self.session.query(Tagsplits, Tags.name.label('tag_name_s')).join(Tags).filter(Tags.name==Tags.Names.BankReconciled).subquery()
        self.outstanding_split_list = self.session.query(Splits) \
                            .outerjoin(q) \
                            .join(Accounts) \
                            .join(Transactions) \
                            .filter(Accounts.id==self.main_row.id) \
                            .filter(q.c.tag_name_s==None) \
                            .order_by(Transactions.date) \
                            .all()

        progress = QtGui.QProgressDialog("Loading...", "", 0, len(self.outstanding_split_list), self)
        progress.setCancelButton(None)
        progress.setMinimumDuration(1)
        progress.setWindowModality(QtCore.Qt.WindowModal)

        self.shown_check_split_list = []
        for i in range(len(self.outstanding_split_list)):
            progress.setValue(i)
            split = self.outstanding_split_list[i]
            self.shown_check_split_list.append(SplitTagger(split,self.tagRec,self.tagPen,self.recStatus))

        self.reconciled_split_list = self.session.query(Splits) \
                            .outerjoin(q) \
                            .join(Accounts) \
                            .filter(Accounts.id==self.main_row.id) \
                            .filter(q.c.tag_name_s==Tags.Names.BankReconciled) \
                            .all()
        self.recStatus.reconciled_balance = sum([split.sum for split in self.reconciled_split_list],decimal.Decimal())
        self.recStatus.pending_balance = self.recStatus.reconciled_balance + sum([split.amount for split in self.shown_check_split_list if split.pending],decimal.Decimal())
        self.recStatus.outstanding_balance = self.recStatus.reconciled_balance + sum([split.amount for split in self.shown_check_split_list],decimal.Decimal())

        self.model.reset_content_from_list(self.shown_check_split_list)
        for x in self.shown_check_split_list:
            instanceEvent(x, "set", "pending")(lambda obj, attr, value: self.model.rowEmitChange(obj, "all"))
            instanceEvent(x, "set", "reconciled")(lambda obj, attr, value: self.model.rowEmitChange(obj, "all"))

        progress.setValue(len(self.outstanding_split_list))

        self.mm.connect_instance(self.recStatus)
        self.mm_account.connect_instance(self.main_row)

        self.setWindowTitle( "Account Reconciliation - {0}".format(self.main_row.name) )

    def reconcile_now(self):
        for s in self.shown_check_split_list:
            if s.pending:
                s.reconciled = True
                s.pending = False
