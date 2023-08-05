# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from sqlalchemy import Table, Column, Integer, String, Text, Date, Boolean, Numeric, MetaData, ForeignKey, create_engine, select, join
from sqlalchemy.orm import mapper, create_session, relationship, object_session, Query
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy.sql.functions as func
import sqlalchemy.sql.expression as expr
import datetime
import decimal
import uuid

from qtalchemy import *
from qtalchemy.dialogs import *
from PySide import QtCore, QtGui

import icons_rc

metadata = MetaData()
Base = declarative_base(metadata=metadata,cls=ModelObject)

class Options(Base):
    __table__ = Table('options', metadata,
                    Column('id', UUID, primary_key=True, default=lambda: uuid.uuid1()),
                    Column('data_name', String(50)))

class EntityHelper(DomainEntity):
    def session_item(self, id):
        session = self.Session()
        a = session.query(self.table_cls).filter(self.key_column==id).one()
        return session, a

class AccountTypes(Base):
    __table__ = Table('accounttypes', metadata,
                    Column('id', UUID, primary_key=True, default=lambda:uuid.uuid1()),
                    Column('name', String(20)),
                    Column('description', Text),
                    Column('balance_sheet', Boolean, default=True),
                    Column('debit', Boolean, default=True),
                    Column('retained_earnings', Boolean, default=False),
                    Column('sort', Integer))

    accounts = relationship("Accounts", backref="AccountType")

def AccountTypeReferral(label, backref):
    return ForeignKeyReferral(
                    str, 
                    label, 
                    backref=backref, 
                    class_=AccountTypes, 
                    userkey="name")

class AccountTypeEntity(EntityHelper):
    def __init__(self, Session, parent, info=None):
        DomainEntity.__init__(self, info=info)
        self.Session = Session
        self.parent = parent

        self.table_cls = AccountTypes
        self.key_column = AccountTypes.id
        self.list_display_columns = [AccountTypes.name, AccountTypes.description, AccountTypes.debit, AccountTypes.sort]
        self.list_search_columns = [AccountTypes.name, AccountTypes.description]

    def list_query_converter(self):
        from sqlalchemy.orm import Query
        queryCols = tuple([self.key_column.label("_hidden_id")] + self.list_display_columns)
        return (Query(queryCols).order_by(AccountTypes.sort, AccountTypes.name, self.key_column), lambda x: x._hidden_id)

    def view_row(self, session, row):
        import accounttypes as mod
        aa=mod.AccountTypeEditor(self.parent,Session=self.Session,row=row)
        aa.show()
        aa.exec_()
        session.close()

    itemCommands = CommandMenu("_item_commands")
    contextCommands = CommandMenu("_context_commands")

    @contextCommands.itemAction("&Edit...", iconFile=":/qtalchemy/default-edit.ico")
    @itemCommands.itemAction("&Edit...", default=True, iconFile=":/qtalchemy/default-edit.ico")
    def view(self, id):
        session, a = self.session_item(id)
        self.view_row(session, a)

    @contextCommands.itemNew()
    @itemCommands.itemNew()
    def new(self, id=None):
        session = self.Session()
        a = self.table_cls()
        session.add(a)
        for k,v in self.info.iteritems():
            setattr(a,k,v)
        self.view_row(session, a)

    @itemCommands.itemAction("&Tag Transactions...", iconFile=":/pyhacc/money.ico")
    def view(self, id):
        session, a = self.session_item(id)
        import accounts as mod
        aa=mod.TagWorksheet(self.parent, Session=self.Session, type_id=a.id)
        aa.show()
        aa.exec_()
        session.close()

    @itemCommands.itemDelete()
    def delete(self, id):
        session, a = self.session_item(id)
        if QtGui.QMessageBox.question(self.parent, "PyHacc", "Are you sure that you wish to delete the type {0.name}?".format(a),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            session.delete(a)
            messaged_commit(session, self.parent)
        session.close()

class Accounts(Base):
    __table__ = Table('accounts', metadata, 
                    Column('id', UUID, primary_key=True, default=lambda:uuid.uuid1()),
                    Column('type_id', UUID, ForeignKey('accounttypes.id'), nullable=False),
                    Column('journal_id', UUID, ForeignKey('journals.id', ondelete='RESTRICT'), nullable=False),
                    Column('name', String(20)),
                    Column('description', Text),
                    Column('rec_note', Text, info={'label': 'Reconciliation Note'}),
                    Column('retearn_id', UUID, ForeignKey('accounts.id'), default=None),
                    Column('instname', Text),
                    Column('instaddr1', Text),
                    Column('instaddr2', Text),
                    Column('instcity', Text),
                    Column('inststate', Text),
                    Column('instzip', Text))

    type = AccountTypeReferral("Account Type", "AccountType")
    splits = relationship("Splits", backref="Account")
    CapitalAccount = relationship("Accounts", backref="profit_and_loss_list", remote_side="Accounts.id", uselist=False)

def AccountReferral(label, backref):
    return ForeignKeyReferral(
                    str, 
                    label, 
                    backref=backref, 
                    class_=Accounts, 
                    userkey="name", 
                    entity = AccountEntity)

def CapitalAccountReferral(label, backref):
    return ForeignKeyReferral(
                    str, 
                    label, 
                    backref=backref, 
                    class_=Accounts, 
                    userkey="name",
                    filter_query = lambda q: q.join(AccountTypes).filter(AccountTypes.retained_earnings==True))

class AccountEntity(EntityHelper):
    def __init__(self, Session, parent, info=None):
        DomainEntity.__init__(self, info=info)
        self.Session = Session
        self.parent = parent

        self.table_cls = Accounts
        self.key_column = Accounts.id
        self.list_display_columns = [Accounts.name, Accounts.description, Accounts.type_id]
        self.list_search_columns = [Accounts.name, Accounts.description]

    def view_row(self, session, row):
        import accounts as mod
        aa=mod.AccountEditor(self.parent,Session=self.Session,row=row)
        aa.show()
        aa.exec_()
        session.close()

    itemCommands = CommandMenu("_item_commands")
    contextCommands = CommandMenu("_context_commands")

    @contextCommands.itemAction("&Edit...", iconFile=":/qtalchemy/default-edit.ico")
    @itemCommands.itemAction("&Edit...", default=True, iconFile=":/qtalchemy/default-edit.ico")
    def view(self, id):
        session, a = self.session_item(id)
        self.view_row(session, a)

    @itemCommands.itemAction("&Reconcile...", iconFile=":/pyhacc/money.ico")
    def view(self, id):
        session, a = self.session_item(id)
        import accounts as mod
        aa=mod.AccountReconcile(self.parent,Session=self.Session,row=a)
        aa.show()
        aa.exec_()
        session.close()

    @itemCommands.itemAction("&Tag Transactions...", iconFile=":/pyhacc/money.ico")
    def view(self, id):
        session, a = self.session_item(id)
        import accounts as mod
        aa=mod.TagWorksheet(self.parent, Session=self.Session, account_id=a.id)
        aa.show()
        aa.exec_()
        session.close()

    @contextCommands.itemNew()
    @itemCommands.itemNew()
    def new(self, id=None):
        session = self.Session()
        a = self.table_cls()
        session.add(a)
        for k,v in self.info.iteritems():
            setattr(a,k,v)
        self.view_row(session, a)

    @itemCommands.itemDelete()
    def delete(self, id):
        session, a = self.session_item(id)
        if QtGui.QMessageBox.question(self.parent, "PyHacc", "Are you sure that you wish to delete the account {0.name}?".format(a),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            session.delete(a)
            messaged_commit(session, self.parent)
        session.close()

class Journals(Base):
    __table__ = Table('journals', metadata, 
                    Column('id', UUID, primary_key=True, default=lambda: uuid.uuid1()),
                    Column('name', String(20)),
                    Column('description', Text))

    accounts = relationship("Accounts", backref="Journal")

def JournalReferral(label, backref):
    return ForeignKeyReferral(
                    str, 
                    label, 
                    backref=backref, 
                    class_=Journals, 
                    userkey="name")

Accounts.journal_name = JournalReferral("Journal","Journal")
Accounts.retearn_name = CapitalAccountReferral("Retained Earnings Account","CapitalAccount")

class JournalEntity(EntityHelper):
    def __init__(self, Session, parent, info=None):
        DomainEntity.__init__(self, info=info)
        self.Session = Session
        self.parent = parent

        self.table_cls = Journals
        self.key_column = Journals.id
        self.list_display_columns = [Journals.name, Journals.description]
        self.list_search_columns = [Journals.name, Journals.description]

    def view_row(self, session, row):
        import journals as mod
        aa=mod.JournalEditor(self.parent,Session=self.Session,row=row)
        aa.show()
        aa.exec_()
        session.close()

    itemCommands = CommandMenu("_item_commands")
    contextCommands = CommandMenu("_context_commands")

    @contextCommands.itemAction("&Edit...", iconFile=":/qtalchemy/default-edit.ico")
    @itemCommands.itemAction("&Edit...", default=True, iconFile=":/qtalchemy/default-edit.ico")
    def view(self, id):
        session, a = self.session_item(id)
        self.view_row(session, a)

    @contextCommands.itemNew()
    @itemCommands.itemNew()
    def new(self, id=None):
        session = self.Session()
        a = self.table_cls()
        session.add(a)
        for k,v in self.info.iteritems():
            setattr(a,k,v)
        self.view_row(session, a)

    @itemCommands.itemDelete()
    def delete(self, id):
        session, a = self.session_item(id)
        if QtGui.QMessageBox.question(self.parent, "PyHacc", "Are you sure that you wish to delete the journal {0.name}?".format(a),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            session.delete(a)
            messaged_commit(session, self.parent)
        session.close()

class Transactions(Base):
    __table__ = Table('transactions', metadata, 
                    Column('tid', UUID, primary_key=True, default=lambda: uuid.uuid1()),
                    Column('date', Date),
                    Column('reference', String(15)),
                    Column('payee', Text, info={"yoke": "line"}), 
                    Column('memo', Text, info={"yoke": "line"}),
                    Column('receipt', Text, info={"yoke": "formatted"}))

    splits = relationship("Splits", backref="Transaction", cascade='all')

    def __init__(self):
        self.date = datetime.date.today()

    def ValidateBalanced(self):
        if sum([AttrNumeric(2)(s.sum) for s in self.splits], decimal.Decimal()) != 0:
            raise ValidationError("The transactions are not balanced.")

    def ascii_repr(self):
        lines = []
        if self.date is not None:
            lines.append("Date:  {0}".format(self.date))
        if self.reference not in [None, ""]:
            lines.append("Reference:  {0}".format(self.reference))
        if self.payee not in [None, ""]:
            lines.append("Payee:  {0}".format(self.payee))
        if self.memo not in [None, ""]:
            lines.append("Memo:  {0}".format(self.memo))
        lines.append("-"*(20+1+12+1+12))
        for x in self.splits:
            lines.append("{0.account:<20} {0.debit:12.2f} {0.credit:12.2f}".format(x))
        lines.append("-"*(20+1+12+1+12))

        return '\n'.join(lines)

    def __before_update__(self):
        self.ValidateBalanced()

    def __before_insert__(self):
        self.ValidateBalanced()

class TransactionEntity(EntityHelper):
    def __init__(self, Session, parent, info=None):
        DomainEntity.__init__(self, info=info)
        self.Session = Session
        self.parent = parent

        self.key_column = Transactions.tid
        self.list_display_columns = [Transactions.date, Transactions.reference, Transactions.payee, Transactions.memo]
        self.list_search_columns = [Transactions.payee, Transactions.memo]

    def list_query_converter(self):
        from sqlalchemy.orm import Query
        queryCols = tuple([self.key_column.label("_hidden_id")] + self.list_display_columns)
        return (Query(queryCols).order_by(expr.desc(self.list_display_columns[0]), self.key_column), lambda x: x._hidden_id)

    itemCommands = CommandMenu("_item_commands")
    contextCommands = CommandMenu("_context_commands")
    basicNew = CommandMenu("_basic_new")

    @basicNew.itemNew(iconFile=":/pyhacc/transactions-new.ico")
    @itemCommands.itemNew(iconFile=":/pyhacc/transactions-new.ico")
    def new(self, id=None):
        import transactions as mod
        session = self.Session()
        new = Transactions()
        session.add(new)
        if self.Session.date is not None:
            new.date = self.Session.date
        aa=mod.TransactionEditor(self.parent,Session=self.Session,row=new)
        aa.show()
        aa.exec_()
        session.close()

    @itemCommands.itemNew(descr="Copy...", requireSelection=True, iconFile=":/pyhacc/transactions-copy.ico")
    def copy(self,id):
        import transactions as mod
        session = self.Session()
        a = session.query(Transactions).filter(Transactions.tid==id).one()
        
        new = Transactions()
        for c in "reference,payee,memo".split(','):
            setattr(new,c,getattr(a,c))
        for line in a.splits:
            nl = Splits()
            new.splits += [nl]
            for c in "Account,sum".split(','):
                setattr(nl,c,getattr(line,c))
        if self.Session.date is not None:
            new.date = self.Session.date

        session.add(new)
        aa=mod.TransactionEditor(self.parent,Session=self.Session,row=new)
        aa.show()
        aa.exec_()
        session.close()

    @itemCommands.itemAction("&Edit...", default=True, iconFile=":/pyhacc/transactions-edit.ico")
    def view(self, id):
        import transactions as mod
        session = self.Session()
        a = session.query(Transactions).filter(Transactions.tid==id).one()
        aa=mod.TransactionEditor(self.parent,Session=self.Session,row=a)
        aa.show()
        aa.exec_()
        session.close()
        if hasattr(session.__class__, "balance_refresh"):
            session.__class__.balance_refresh()

    @itemCommands.itemDelete(iconFile=":/pyhacc/transactions-delete.ico")
    def delete(self, id):
        session = self.Session()
        a = session.query(Transactions).filter(Transactions.tid==id).one()
        if QtGui.QMessageBox.question(self.parent, "PyHacc", "Are you sure that you wish to delete the transaction for {0.payee} with description {0.memo}?".format(a),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            session.delete(a)
            messaged_commit(session, self.parent)
        session.close()

class Splits(Base):
    __table__ = Table('splits', metadata, 
                    Column('sid', UUID, primary_key=True, default=lambda: uuid.uuid1()),
                    Column('stid', UUID, ForeignKey('transactions.tid'), nullable=False),
                    Column('account_id', UUID, ForeignKey('accounts.id'), nullable=False), 
                    Column('sum', Numeric(precision=10,scale=2,asdecimal=True)))

    classEvents = ModelObject.Events()

    def __init__(self,acctId=None,amt=0):
        self.account_id = acctId
        self.sum = AttrNumeric(2)(amt)

    account = AccountReferral("Account","Account")

    debit = UserAttr(float, "Debit")
    credit = UserAttr(float, "Credit")

    def quantize(self,v):
        v=decimal.Decimal(v)
        w=decimal.Decimal('0.00')
        v.quantize(w)
        return v

    @credit.on_first_get
    def get_credit(self):
        return -self.sum if self.sum <= 0 else decimal.Decimal('0.00')

    @debit.on_first_get
    def get_debit(self):
        return self.sum if self.sum >= 0 else decimal.Decimal('0.00')

    @classEvents.add("set", "debit")
    def set_debit(self, attr, oldvalue):
        if not self.is_setting("sum") and not self.is_setting("credit"):
            self.sum = self.debit - self.credit

    @classEvents.add("set", "credit")
    def set_credit(self, attr, oldvalue):
        if not self.is_setting("sum") and not self.is_setting("debit"):
            self.sum = self.debit - self.credit

    @classEvents.add("set", "sum")
    def set_sum(self, attr, oldvalue):
        if not self.is_setting("credit") and not self.is_setting("debit"):
            self.debit = decimal.Decimal('0.00') if self.sum <= 0 else self.sum
            self.credit = decimal.Decimal('0.00') if self.sum >= 0 else -self.sum

class Tagsplits(Base):
    __table__ = Table('tagsplits', metadata, 
                    Column('tag_id', UUID, ForeignKey('tags.id', ondelete='RESTRICT'), primary_key=True, nullable=False),
                    Column('split_id', UUID, ForeignKey('splits.sid'), primary_key=True, nullable=False))

class Tags(Base):
    __table__ = Table('tags', metadata, 
                    Column('id', UUID, primary_key=True, default=lambda: uuid.uuid1()),
                    Column('name', String(20)),
                    Column('description', Text))

    class Names:
        BankReconciled = "Bank Reconciled"
        BankPending = "Bank Pending"

    # tags to splits is a many-to-many relationship
    splits = relationship('Splits', secondary='tagsplits', backref='tags')


def TagReferral(label, backref):
    return ForeignKeyReferral(
                    str, 
                    label, 
                    backref=backref, 
                    class_=Tags, 
                    userkey="name")

class TagEntity(EntityHelper):
    def __init__(self, Session, parent, info=None):
        DomainEntity.__init__(self, info=info)
        self.Session = Session
        self.parent = parent

        self.table_cls = Tags
        self.key_column = Tags.id
        self.list_display_columns = [Tags.name, Tags.description]
        self.list_search_columns = [Tags.name, Tags.description]

    def view_row(self, session, row):
        import tags as mod
        aa=mod.TagEditor(self.parent,Session=self.Session,row=row)
        aa.show()
        aa.exec_()
        session.close()

    itemCommands = CommandMenu("_item_commands")
    contextCommands = CommandMenu("_context_commands")

    @contextCommands.itemAction("&Edit...", iconFile=":/qtalchemy/default-edit.ico")
    @itemCommands.itemAction("&Edit...", default=True, iconFile=":/qtalchemy/default-edit.ico")
    def view(self, id):
        session, a = self.session_item(id)
        self.view_row(session, a)

    @contextCommands.itemNew()
    @itemCommands.itemNew()
    def new(self, id=None):
        session = self.Session()
        a = self.table_cls()
        session.add(a)
        for k,v in self.info.iteritems():
            setattr(a,k,v)
        self.view_row(session, a)

    @itemCommands.itemDelete()
    def delete(self, id):
        session, a = self.session_item(id)
        if QtGui.QMessageBox.question(self.parent, "PyHacc", "Are you sure that you wish to delete the tag {0.name}?".format(a),  QtGui.QMessageBox.Yes | QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            session.delete(a)
            messaged_commit(session, self.parent)
        session.close()

class CheckableTagList(ModelObject):
    def __init__(self, split, tag):
        self.split = split
        self.tag = tag

    classEvents = ModelObject.Events()

    checked = UserAttr(bool, 'Checked', readonly=False)
    @checked.on_first_get
    def am_i_checked(self):
        return self.tag in self.split.tags

    @classEvents.add("set", "checked")
    def set_checked(self, attr, oldvalue):
        if self.checked:
            self.split.tags += [self.tag]
        else:
            self.split.tags.remove(self.tag)

    tag_name = UserAttr(str, 'Tag', storage='tag.name', readonly=True)

class SplitTaggerSimple(ModelObject):
    classEvents = ModelObject.Events()

    def __init__(self, split, tag):
        self.split = split
        self.tag = tag
        # we front-load these to be able to have an effective progress bar
        # TODO:  consider sqlalchemy eager-load
        load_me = self.split.tags
        load_me = self.split.Transaction

    tagged = UserAttr(bool,"Tagged",readonly=False)
    @tagged.on_first_get
    def tagged_get(self):
        return self.tag in self.split.tags
    
    @classEvents.add("set", "tagged")
    def tagged_set(self, attr, oldvalue):
        linked_now = self.tag in self.split.tags
        if not linked_now and self.tagged == True:
            self.split.tags += [self.tag]
        if linked_now and self.tagged == False:
            self.split.tags.remove(self.tag)

    debit = UserAttr(AttrNumeric(2), "Debit", readonly=True)
    @debit.on_first_get
    def debit_get(self):
        if self.split.sum > 0:
            return AttrNumeric(2)(self.split.sum)
        return AttrNumeric(2)(0)

    credit = UserAttr(AttrNumeric(2), "Credit", readonly=True)
    @credit.on_first_get
    def credit_get(self):
        if self.split.sum < 0:
            return AttrNumeric(2)(-self.split.sum)
        return AttrNumeric(2)(0)

    def foregroundRole(self, attr=None):
        if self.tagged:
            return QtGui.QBrush(QtCore.Qt.darkGreen)

    def backgroundRole(self, attr=None):
        if self.tagged:
            return QtGui.QBrush(QtCore.Qt.cyan)

    date = UserAttr(datetime.date,"Date",readonly=True,storage="split.Transaction.date")
    reference = UserAttr(str,"Reference",readonly=True,storage="split.Transaction.reference")
    payee = UserAttr(str,"Payee",readonly=True,storage="split.Transaction.payee")
    memo = UserAttr(str,"Memo",readonly=True,storage="split.Transaction.memo")
    amount = UserAttr(AttrNumeric(2),"Amount",readonly=True,storage="split.sum")


class SplitTagger(ModelObject):
    class ReconciliationStatus(ModelObject):
        """
        Auxiliary class for a reconcile header data
        """
        def __init__(self):
            pass

        pending_balance = UserAttr(AttrNumeric(2),"Pending Balance",readonly=True)
        outstanding_balance = UserAttr(AttrNumeric(2),"Outstanding Balance",readonly=True)
        reconciled_balance = UserAttr(AttrNumeric(2),"Reconciled Balance",readonly=True)

    classEvents = ModelObject.Events()

    def __init__(self,split,tagRec,tagPen,recStatus):
        self.split = split
        self.tagRec = tagRec
        self.tagPen = tagPen
        self.recStatus = recStatus
        # we front-load these to be able to have an effective progress bar
        # TODO:  consider sqlalchemy eager-load
        load_me = self.split.tags
        load_me = self.split.Transaction

    pending = UserAttr(bool,"Pending",readonly=False)
    @pending.on_first_get
    def pending_get(self):
        return self.tagPen in self.split.tags
    
    @classEvents.add("set", "pending")
    def pending_set(self, attr, oldvalue):
        linked_now = self.tagPen in self.split.tags
        if not linked_now and self.pending == True:
            self.split.tags += [self.tagPen]
            self.recStatus.pending_balance += self.amount
        if linked_now and self.pending == False:
            self.split.tags.remove(self.tagPen)
            self.recStatus.pending_balance -= self.amount

    reconciled = UserAttr(bool,"Reconcile",readonly=False)
    @reconciled.on_first_get
    def reconciled_get(self):
        return self.tagRec in self.split.tags

    debit = UserAttr(AttrNumeric(2), "Debit", readonly=True)
    @debit.on_first_get
    def debit_get(self):
        if self.split.sum > 0:
            return AttrNumeric(2)(self.split.sum)
        return AttrNumeric(2)(0)

    credit = UserAttr(AttrNumeric(2), "Credit", readonly=True)
    @credit.on_first_get
    def credit_get(self):
        if self.split.sum < 0:
            return AttrNumeric(2)(-self.split.sum)
        return AttrNumeric(2)(0)

    @classEvents.add("set", "reconciled")
    def reconciled_set(self, attr, oldvalue):
        linked_now = self.tagRec in self.split.tags
        if not linked_now and self.reconciled == True:
            self.split.tags += [self.tagRec]
            self.recStatus.reconciled_balance += self.amount
        if linked_now and self.reconciled == False:
            self.split.tags.remove(self.tagRec)
            self.recStatus.reconciled_balance -= self.amount

    def foregroundRole(self, attr=None):
        if self.pending:
            return QtGui.QBrush(QtCore.Qt.darkGreen)

    def backgroundRole(self, attr=None):
        if self.reconciled:
            return QtGui.QBrush(QtCore.Qt.cyan)

    date = UserAttr(datetime.date,"Date",readonly=True,storage="split.Transaction.date")
    reference = UserAttr(str,"Reference",readonly=True,storage="split.Transaction.reference")
    payee = UserAttr(str,"Payee",readonly=True,storage="split.Transaction.payee")
    memo = UserAttr(str,"Memo",readonly=True,storage="split.Transaction.memo")
    amount = UserAttr(AttrNumeric(2),"Amount",readonly=True,storage="split.sum")

def Utilities(session_source):
    s = session_source()
    for account in s.query(Accounts).join(AccountTypes).filter(expr.and_(AccountTypes.balance_sheet == False,Accounts.retearn_id==None)).all():
        print account.id, account.name, account.AccountTypes.balance_sheet, account.AccountTypes.name

def Sessionize(session_source,func,**kwargs):
    session = session_source()
    func(session,**kwargs)
    session.commit()
    session.flush()

def SimpleTransaction(session,account1,account2,account1_sum,**kwargs):
    t=Transactions()
    t.date = kwargs['date']
    if kwargs.has_key('reference'):
        t.reference = kwargs['reference']
    t.payee = kwargs['payee']
    t.memo = kwargs['memo']
    session.add(t)
    t.splits += [Splits(),Splits()]
    t.splits[0].account = account1
    t.splits[0].sum = account1_sum
    t.splits[1].account = account2
    t.splits[1].sum = -account1_sum

class TransactionTemplate:
    def __init__(self,transaction):
        self.tid = transaction.tid
        self.payee = transaction.payee
        self.memo = transaction.memo
        self.accounts = tuple(sorted([(s.account_id, s.sum>0) for s in transaction.splits]))

    def __hash__(self):
        return hash(self.payee) ^ hash(self.memo) ^ hash(self.accounts)

    def __cmp__(self,other):
        return 0 if self.payee == other.payee and self.memo == other.memo and self.accounts == other.accounts else 1

_test_app = None
_test_session = None

def qtapp():
    """
    A QApplication creator for test cases.  QApplication is a single-ton and 
    this provides a safe construction wrapper.
    
    >>> app=qtapp()
    >>> # put test code here
    """
    global _test_app
    _test_app = QtGui.QApplication.instance()
    if _test_app is None:
        _test_app = QtGui.QApplication([])
    from pyhacc.PyHaccLib import FiscalDateRangeYoke
    addGlobalYoke('fiscal_range', FiscalDateRangeYoke)
    return _test_app

def testsession(**kwargs):
    global _test_session
    if _test_session is None:
        from PyHaccLib import MemorySource
        if not kwargs.has_key('end_date'):
            kwargs['end_date'] = datetime.date(2011,3,31)
        _test_session = MemorySource(**kwargs)
    return _test_session
    
def qtappsession(**kwargs):
    """
    >>> app, Session = qtappsession()
    >>> Session is not None
    True
    """
    return qtapp(), testsession(**kwargs)

def InsertSystemRows(Session):
    """
    Create the most basic rows needed for meaningful pyhacc usage.
    """

    # add account types
    session = Session()
    assets = AccountTypes(name="Asset")
    assets.debit = True
    assets.sort = 1
    assets.balance_sheet = True
    liabilities = AccountTypes(name="Liability")
    liabilities.debit = False
    liabilities.sort = 3
    liabilities.balance_sheet = True
    capital = AccountTypes(name="Capital")
    capital.debit = False
    capital.retained_earnings = True
    capital.sort = 5
    capital.balance_sheet = True
    revenue = AccountTypes(name="Revenue")
    revenue.debit = False
    revenue.sort = 7
    revenue.balance_sheet = False
    expense = AccountTypes(name="Expense")
    expense.debit = True
    expense.sort = 9
    expense.balance_sheet = False
    for t in [assets,liabilities,capital,revenue,expense]:
        session.add(t)
    session.commit()

    # add a default journal
    session = Session()
    session.add(Journals(name="General"))
    session.commit()

    # add system tags
    session = Session()
    session.add(Tags(name=Tags.Names.BankReconciled,description="System tag for bank reconciliation"))
    session.add(Tags(name=Tags.Names.BankPending,description="System tag for bank pending reconciliation"))
    session.commit()

    session = Session()
    opt = Options()
    opt.data_name = "Home Accounting"
    session.add(opt)
    session.commit()

def BuildDemoData(Session,verbose=False,demo_info=None):
    if demo_info is None:
        demo_info = {}

    session = Session()

    session = Session()
    opt = session.query(Options).one()
    opt.data_name = "Demo Home Accounting"
    session.add(opt)
    session.commit()

    # add accounts
    session = Session()
    assets = session.query(AccountTypes).filter(AccountTypes.name=='Asset').one()
    journal = session.query(Journals).filter(Journals.name=='General').one()
    cash = Accounts()
    cash.name="Cash"
    cash.description="Petty Cash"
    checking = Accounts()
    checking.name="Checking"
    checking.description="Checking Account"
    assets.accounts += [cash,checking]
    journal.accounts += [cash,checking]

    liabilities = session.query(AccountTypes).filter(AccountTypes.name=='Liability').one()
    credit = Accounts()
    credit.name="Mastercard"
    credit.description="Credit Card"
    liabilities.accounts += [credit]
    journal.accounts += [credit]

    cap = session.query(AccountTypes).filter(AccountTypes.name=='Capital').one()
    capital = Accounts()
    capital.name="Capital"
    capital.description="Main Capital Account"
    cap.accounts += [capital]
    journal.accounts += [capital]

    expense = session.query(AccountTypes).filter(AccountTypes.name=='Expense').one()
    a = Accounts()
    a.name="Groceries"
    a.description="Groceries"
    a.CapitalAccount = capital
    expense.accounts += [a]
    journal.accounts += [a]
    a = Accounts()
    a.name="House"
    a.description="Mortgage & Improvements"
    a.CapitalAccount = capital
    expense.accounts += [a]
    journal.accounts += [a]

    revenue = session.query(AccountTypes).filter(AccountTypes.name=='Revenue').one()
    a = Accounts()
    a.name="Day Job"
    a.description="Full Time Employment"
    a.CapitalAccount = capital
    revenue.accounts += [a]
    journal.accounts += [a]

    session.commit()

    final_date = demo_info['end_date'] if demo_info.has_key('end_date') else None
    if final_date is None:
        final_date = datetime.date.today()
    Session.demo_end_date = final_date
    # make some exciting transactions
    # pay the mortgage for a year
    for i in range(12):
        session = Session()
        t = Transactions()
        session.add(t)
        t.date = final_date-datetime.timedelta(i*30)
        t.journal_id = session.query(Journals).filter("name='General'").one().id
        t.payee = "Central Bank"
        t.memo = "Mortgage"
        t.splits += [Splits(session.query(Accounts).filter("name='Checking'").one().id,-550)]
        t.splits += [Splits(session.query(Accounts).filter("name='House'").one().id,550)]
        #print t.splits[0].account
        session.commit()

    for i in range(52):
        session = Session()
        t = Transactions()
        session.add(t)
        t.date = final_date-datetime.timedelta(i*7-3)
        t.journal_id = session.query(Journals).filter("name='General'").one().id
        t.payee = "ACME Inc"
        t.memo = "Payroll"
        t.splits += [Splits(session.query(Accounts).filter("name='Checking'").one().id,400)]
        t.splits += [Splits(session.query(Accounts).filter("name='Day Job'").one().id,-400)]
        #print t.splits[0].account
        session.commit()

    # buy some groceries
    Sessionize(Session,SimpleTransaction,account1='Cash',account2='Groceries',account1_sum=-11.24,date=final_date,payee='Giant',memo='Groceries')
    
    if verbose:
        session = Session()
        for r in session.query(AccountTypes).all():
            print r.name
            for acnt in r.accounts:
                print " " + acnt.name
