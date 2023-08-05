# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from PyHaccSchema import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy.pool

def SessionSource(conn, create_level=0, demo_info = None):
    if conn == 'sqlite://':
        engine = create_engine(conn, poolclass=sqlalchemy.pool.StaticPool, connect_args={'check_same_thread':False})
    else:
        engine = create_engine(conn)
    metadata.bind = engine
    s = PBSessionMaker(bind=engine)
    if create_level > 0:
        metadata.create_all()
        InsertSystemRows(s)
        if create_level > 1:
            BuildDemoData(s, demo_info = demo_info)
    else:
        # Execute a query to fling an exception on an unrecognized database
        # Truly speaking, this is a merely a most rudimentary check, but it will
        # prevent hooking up to obviously wrong or massively uninitialized
        # data-sets.
        try:
            test = s()
            test.query(Options).count()
            test.close()
        except Exception as e:
            raise RuntimeError('Database inaccessible; there may be a problem with server ({0})'.format(conn))
    s.date = None
    return s

def MemorySource(end_date = None):
    return SessionSource('sqlite://', 2, {'end_date': end_date})

def init_session_maker(conn):
    """
    Create a demo session or persisted session as determined by the connection
    string.
    """
    if conn == "sqlite://":
        # special case the in-memory database
        Session = SessionSource(conn,2)  # create data
    else:
        Session = SessionSource(conn)
    return Session

def initdb(conn,level=1):
    s = SessionSource(conn,create_level=level)

def gui_app(conn=None):
    import sys
    app = QtGui.QApplication(sys.argv)
    app.setOrganizationName("Mohler")
    app.setOrganizationDomain("kiwistrawberry.us")
    app.setApplicationName("PyHacc")

    addGlobalYoke('fiscal_range', FiscalDateRangeYoke)
    
    # we graduate to a more gui friendly message
    sys.excepthook = message_excepthook

    class X:
        def __call__(self, conn):
            self.Session = init_session_maker(conn)

    SessionHolder = X()
    make_db = lambda conn: SessionSource(conn, create_level=1)

    if conn is None:
        from qtalchemy.dialogs import multi_auth_dialog
        if multi_auth_dialog(parent=None, init_session_maker=SessionHolder,
                init_db=make_db) != QtGui.QDialog.Accepted:
            return
    else:
        SessionHolder(conn)

    from PyHaccMainWindow import MainWindow

    mainwindow = MainWindow(Session=SessionHolder.Session)
    mainwindow.show()
    app.exec_()


def visual_date(date):
    return date.strftime( "%Y.%m.%d" )

def month_end(year,month):
    if month == 12:
        date = datetime.date(year,12,31)
    else:
        date = datetime.date(year,month+1,1)-datetime.timedelta(1)
    return date

def month_safe_day(year,month,day):
    """
    >>> month_safe_day(2011,2,30)
    datetime.date(2011, 2, 28)
    >>> month_safe_day(2012,2,30)
    datetime.date(2012, 2, 29)
    >>> month_safe_day(2011,4,31)
    datetime.date(2011, 4, 30)
    >>> month_safe_day(2011,4,15)
    datetime.date(2011, 4, 15)
    >>> month_safe_day(2011,12,33)
    datetime.date(2011, 12, 31)
    """
    try:
        return datetime.date(year,month,day)
    except:
        if month == 12:
            return datetime.date(year+1,1,1)-datetime.timedelta(1)
        else:
            return datetime.date(year,month+1,1)-datetime.timedelta(1)

def prior_month_end(date):
    pme = datetime.date(date.year,date.month,1)
    return pme-datetime.timedelta(1)


def fiscal_year_prior():
    d = datetime.date.today()
    return datetime.date(d.year-1, 1, 1), datetime.date(d.year-1, 12, 31)

def fiscal_year_current():
    d = datetime.date.today()
    return datetime.date(d.year, 1, 1), datetime.date(d.year, 12, 31)

def fiscal_month_prior():
    d = datetime.date.today()
    d = prior_month_end(d)
    return datetime.date(d.year, d.month, 1), d

def fiscal_month_current():
    d = datetime.date.today()
    return datetime.date(d.year, d.month, 1), month_end(d.year, d.month)

def fiscal_custom():
    return None, None

fiscal_date_range = {
        'Last Year': fiscal_year_prior,
        'This Year': fiscal_year_current,
        'Last Month': fiscal_month_prior,
        'This Month': fiscal_month_current,
        'Custom': fiscal_custom}

def FiscalDateRangeYoke(mapper, attr):
    l = fiscal_date_range.keys()[:]
    l.sort()
    return SelectionYoke(mapper, attr, l)

def fiscalDateRangeEvents(classEvents, range, begin, end):
    @classEvents.add("set", end)
    @classEvents.add("set", begin)
    def date_set(obj, attr, oldvalue):
        try:
            if not obj.is_setting(range):
                setattr(obj, range, 'Custom')
        except Exception as e:
            pass

    @classEvents.add("set", range)
    def range_set(obj, attr, oldvalue):
        try:
            b, e = fiscal_date_range[getattr(obj, range)]()
            if not obj.is_setting(begin) and b is not None:
                setattr(obj, begin, b)
            if not obj.is_setting(end) and e is not None:
                setattr(obj, end, e)
        except Exception as e:
            pass

class FiscalRangeAttr(UserAttr):
    def yoke_specifier(self):
        return 'fiscal_range'
