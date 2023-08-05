#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
import uuid
import os
import sys
import baker
from sqlalchemy import Table, Column, String, create_engine, MetaData
from sqlalchemy.ext.sqlsoup import SqlSoup, Session

id_replacements = {}

def Assign(row,fld):
    return getattr(row,fld)

def id_to_balancesheet(row,fld):
    v = int(getattr(row,fld))
    #print v,type(v)
    return v == 0 or v == 1 or v == 2

class ExistingId:
    def __init__(self,label,exclude=None):
        self.label = label
        global id_replacements
        if not id_replacements.has_key(label):
            id_replacements[label] = {}
        self.mapper = id_replacements[label]
        self.exclude = exclude

    def __call__(self,row,fld):
        if getattr(row,fld) == self.exclude:
            return None
        global id_replacements
        if not self.mapper.has_key(getattr(row,fld)):
            self.mapper[getattr(row,fld)] = uuid.uuid1().hex
        return self.mapper[getattr(row,fld)]

tables_to_convert =\
    {"accounttypes":
        {"id": (ExistingId("accounttypes.id"), "id"),
         "name": (Assign, "name"),
         "debit": (lambda r,x:getattr(r,x)==1, "leftplus"),
         "balance_sheet": (id_to_balancesheet, "id"),
         "retained_earnings": (lambda r,x: int(getattr(r,x))==2, "id")},
     "journals": 
        {"id": (ExistingId("journals.id"), "id"),
         "name": (Assign, "name"),
         "description": (Assign, "description")},
     "accounts":
        {"id": (ExistingId("accounts.id"), "id"),
         "name": (Assign, "name"),
         "description": (Assign, "description"),
         "type_id": (ExistingId("accounttypes.id"), "type"),
         "journal_id": (ExistingId("journals.id"), "journalid"),
         "retearn_id": (ExistingId("accounts.id",exclude=0), "retearnid"),
         "ccnum": (Assign, "ccnum"),
         "cc3digit": (Assign, "cc3digit"),
         "ccexdate": (Assign, "ccexdate"),
         "ccpin": (Assign, "ccpin"),
         "num": (Assign, "num"),
         "inactive": (Assign, "inactive"),
         "instname": (Assign, "instname"),
         "instaddr1": (Assign, "instaddr1"),
         "instaddr2": (Assign, "instaddr2"),
         "instcity": (Assign, "instcity"),
         "inststate": (Assign, "inststate"),
         "instzip": (Assign, "instzip"),
         "instphone": (Assign, "instphone"),
         "instfax": (Assign, "instfax"),
         "instemail": (Assign, "instemail"),
         "instcontact": (Assign, "instcontact"),
         "instnotes": (Assign, "instnotes"),
         "category": (Assign, "category"),
         "taxed": (Assign, "taxed")},
    "transactions":
        {"tid": (ExistingId("transactions.tid"), "tid"),
         "date": (Assign, "date"),
         "journal_id": (ExistingId("journals.id"), "journalid"),
         "reference": (Assign, "num"),
         "payee": (Assign, "payee"),
         "memo": (Assign, "memo")},
    "splits":
        {"sid": (ExistingId("splits.sid"), "sid"),
         "stid": (ExistingId("transactions.tid"), "stid"),
         "account_id": (ExistingId("accounts.id"), "acctid"),
         "sum": (Assign, "sum")},
    }

@baker.command
def convert(src,dst,reset=True):
    """
    Converts a qhacc database to a pyhacc database.
    
Examples of connection strings for src and dst parameter are:
    
MySql:  mysql://username:password@server/database

Sqlite in-memory:  sqlite://

Sqlite Disk:  sqlite:///filename
    """
    import pyhacc.PyHaccLib as PyHaccLib
    import re
    m=re.match("([a-zA-Z0-9]*)://(.*)", dst)
    if m is None:
        raise ValueError( "The destination \"%s\" is invalid." % (dst,) )
    else:
        if m.group(1) == "sqlite" and reset and os.path.exists(m.group(2)[1:]):
            print "Deleting file %s " % (m.group(2)[1:],)
            os.remove(m.group(2)[1:])

    if reset:
        PyHaccLib.SessionSource(dst,1)

    db_src=SqlSoup(src)
    
    engine = create_engine(dst)
    metadata = MetaData(bind=engine)
    tagsplits = Table('tagsplits', metadata, 
        Column('tag_id', String, primary_key=True),
        Column('split_id', String, primary_key=True), autoload=True)

    db_dest=SqlSoup(metadata)
    db_dest.map(tagsplits)

    db_dest.accounttypes.delete()

    for table in ("accounttypes","journals","accounts","transactions","splits"):
        print table
        q = getattr(db_src,table)
        if table == "accounts":
            q = q.filter(db_src.accounts.name!="").order_by('name')
        for row in q.all():
            to_assign = dict((fld, assign[0](row,assign[1])) for fld, assign in tables_to_convert[table].iteritems())
            ins=getattr(db_dest,table).insert(**to_assign)
        Session.commit()
        db_dest.flush()

    # convert reconciliation details
    print "mark reconciled"
    splits = db_src.splits
    reconciled = db_dest.tags.filter(db_dest.tags.name=="Bank Reconciled").one()
    pending = db_dest.tags.filter(db_dest.tags.name=="Bank Pending").one()
    for row in splits.all():
        if row.reco == 1:
            db_dest.tagsplits.insert(tag_id=pending.id, split_id=ExistingId("splits.sid")(row, "sid"))
        if row.reco == 2:
            db_dest.tagsplits.insert(tag_id=reconciled.id, split_id=ExistingId("splits.sid")(row, "sid"))
    Session.commit()
    db_dest.flush()

baker.run()
