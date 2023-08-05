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
from PyHaccSchema import *

class AccountTypeEditor(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a = AccountTypeEditor(None,row=s.query(AccountTypes).filter(AccountTypes.name=="Asset").one())
    """
    def __init__(self, parent, row=None, Session=None, row_id=None, flush=True):
        BoundDialog.__init__(self,parent)

        self.setObjectName("AccountTypesInfo")
        self.setDataReader(Session, AccountTypes, "id")

        main = QtGui.QVBoxLayout()
        self.setLayout(main)
        grid = LayoutLayout(main,QtGui.QFormLayout())
        self.mm = self.mapClass(AccountTypes)
        self.mm.addBoundField(grid,"name")
        
        tabs = LayoutWidget(main,QtGui.QTabWidget())

        tab1 = QtGui.QWidget()
        page_layout = QtGui.QVBoxLayout(tab1)
        self.mm.addBoundForm(page_layout,"sort balance_sheet debit retained_earnings description".split(' '))
        tabs.addTab(tab1,"Settings")

        self.account_tab = PBTableTab(self, Session, AccountEntity, 
                        [(AccountTypes.id, lambda dataContext: dataContext.id)], 
                        Query((Accounts.id,Accounts.name.label("Account Name"),Journals.name.label("Journal"))).outerjoin(Journals).join(AccountTypes), 
                        extensionId=suffixExtId(self, "Accounts"))
        tabs.addTab(self.account_tab,"Accounts")

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self, position=False, tabs=[tabs])

        self.readData(row, row_id)
        
    def load(self):
        self.mm.connect_instance(self.main_row)
        self.account_tab.refresh(self.main_row)
        self.setWindowTitle("Account Type {0.name}".format(self.main_row))
