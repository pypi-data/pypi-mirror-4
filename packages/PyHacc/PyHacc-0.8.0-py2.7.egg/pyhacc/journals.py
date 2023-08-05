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

class JournalEditor(BoundDialog):
    """
    >>> app, Session = qtappsession()
    >>> s = Session()
    >>> a=JournalEditor(None,row=s.query(Journals).filter(Journals.name=="General").one())
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)
        self.setObjectName("JournalsInfo")
        self.setDataReader(Session, Journals, "id")

        self.mm = self.mapClass(AccountTypes)

        main = QtGui.QVBoxLayout(self)
        grid = LayoutLayout(main,QtGui.QFormLayout())
        self.mm.addBoundField(grid,"name")

        tabs = LayoutWidget(main,QtGui.QTabWidget())

        tab1 = QtGui.QWidget()
        page_layout = QtGui.QVBoxLayout(tab1)
        self.mm.addBoundForm(page_layout,["description"])
        tabs.addTab(tab1,"Settings")

        self.accounts_tab = PBTableTab(self, Session, AccountEntity, 
                        [(Journals.id, lambda dataContext: dataContext.id)], 
                        Query((Accounts.id,Accounts.name.label("Account Name"),AccountTypes.name.label("Type"))).outerjoin(Journals).join(AccountTypes), 
                        extensionId=suffixExtId(self, "Accounts"))
        tabs.addTab(self.accounts_tab,"Accounts")

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self, position=False, tabs=[tabs])

        self.readData(row, row_id)
        
    def load(self):
        self.mm.connect_instance(self.main_row)
        self.accounts_tab.refresh(self.main_row)
        self.setWindowTitle("Journals - {0.name}".format(self.main_row))
