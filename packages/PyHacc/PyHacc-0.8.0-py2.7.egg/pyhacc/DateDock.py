# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2012, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PySide import QtCore, QtGui
from PyHaccSchema import *

class DateObject(ModelObject):
    date = UserAttr(datetime.date, "Transaction Date")

class DateWidget(QtGui.QWidget, MapperMixin):
    """
    >>> app, Session = qtappsession()
    >>> a = DateWidget(None, Session)
    >>> a.dateSettings.date = datetime.date(2012, 2, 4)
    >>> Session.date
    datetime.date(2012, 2, 4)
    """

    title = 'Date'
    factory = 'Date'

    def __init__(self, parent, Session):
        QtGui.QWidget.__init__(self, parent)

        self.setWindowTitle( "Date" )
        self.setObjectName("DateDock")

        self.Session = Session

        self.dateSettings = DateObject()

        if self.Session.date is None:
            self.dateSettings.date = datetime.date.today()
        else:
            self.dateSettings.date = self.Session.date

        box = QtGui.QHBoxLayout(self)
        self.mm = self.mapClass(DateObject)
        self.mm.addBoundField(box, "date")
        self.mm.connect_instance(self.dateSettings)

        instanceEvent(self.dateSettings, "set", "date")(self.setDate)

    def setDate(self, obj, attr, value):
        self.Session.date = self.dateSettings.date
        
