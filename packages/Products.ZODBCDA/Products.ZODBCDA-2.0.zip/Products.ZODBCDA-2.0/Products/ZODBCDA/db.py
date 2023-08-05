##############################################################################
# 
# Zope Public License (ZPL) Version 1.0
# -------------------------------------
# 
# Copyright (c) Digital Creations.  All rights reserved.
# 
# This license has been certified as Open Source(tm).
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
# 
# 1. Redistributions in source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions, and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
# 
# 3. Digital Creations requests that attribution be given to Zope
#    in any manner possible. Zope includes a "Powered by Zope"
#    button that is installed by default. While it is not a license
#    violation to remove this button, it is requested that the
#    attribution remain. A significant investment has been put
#    into Zope, and this effort will continue if the Zope community
#    continues to grow. This is one way to assure that growth.
# 
# 4. All advertising materials and documentation mentioning
#    features derived from or use of this software must display
#    the following acknowledgement:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    In the event that the product being advertised includes an
#    intact Zope distribution (with copyright and license included)
#    then this clause is waived.
# 
# 5. Names associated with Zope or Digital Creations must not be used to
#    endorse or promote products derived from this software without
#    prior written permission from Digital Creations.
# 
# 6. Modified redistributions of any form whatsoever must retain
#    the following acknowledgment:
# 
#      "This product includes software developed by Digital Creations
#      for use in the Z Object Publishing Environment
#      (http://www.zope.org/)."
# 
#    Intact (re-)distributions of any official Zope release do not
#    require an external acknowledgement.
# 
# 7. Modifications are encouraged but must be packaged separately as
#    patches to official Zope releases.  Distributions that do not
#    clearly separate the patches from the original work must be clearly
#    labeled as unofficial distributions.  Modifications which do not
#    carry the name Zope may be packaged in any form, as long as they
#    conform to all of the clauses above.
# 
# 
# Disclaimer
# 
#   THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND ANY
#   EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#   PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL CREATIONS OR ITS
#   CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#   LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
#   USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#   ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
#   OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#   SUCH DAMAGE.
# 
# 
# This software consists of contributions made by Digital Creations and
# many individuals on behalf of Digital Creations.  Specific
# attributions are listed in the accompanying credits file.
# 
###############################################################################
        
# Revision History
#-------------------------------------------------------------------------------
# Updated   By  Modifications
#-------------------------------------------------------------------------------
# 11/05/2005 CGT Log long running queries
# 19/11/2008 NFI Enhanced ODBC reconnection code TAUR 359565 et al.
# 04/12/2008 CGT GOSF 395300 Transaction committed/aborted by another session
# 15/01/2009 CGT ADVA 240760 3.07.155 Oracle reconnection
# 

# NOTE 1 - NFI - 359565
# self.lock.release() has had errors suppressed.
# For some reason, if the ODBC connection was lost then regained, this would
# get called when there was no lock, and raise an assertion error.  I checked
# to make sure the lock count was 0 in threading.py, so despite the fact that
# something isn't working as advertised, it should be harmless.
# I don't know how this happens, but it causes terrible error messages in the browser
# once the db reconnection has succeeded, so I just suppressed it.

LONG_QUERY_SECS = 4.0

from sql import *
from string import join, split, find, strip
import sys
import time
from Shared.DC.ZRDB.TM import TM
import threading
import traceback
from DataWrks.DWDateTime.DWDateTime import DWDateTime
from zLOG import LOG, WARNING, INFO, ERROR, DEBUG, TRACE

rc=sys.getrefcount

# Commented out: clashes with sql.error
#error=DatabaseError='ODBC Database Error'

def manage_ODBCDataSources(*args):
    r=[]
    status, name, desc = SQLDataSources(SQL_FETCH_FIRST)
    while status==SQL_SUCCESS:
        r.append((name, desc))
        status, name, desc = SQLDataSources(SQL_FETCH_NEXT)
    return r

defs={
    SQL_BIGINT: 'i',
    SQL_BINARY: 't',
    SQL_BIT: 'i',
    SQL_CHAR: 't',
    SQL_DATE: 'd',
    SQL_DECIMAL: 'N',
    SQL_DOUBLE: 'n',
    SQL_FLOAT: 'n',
    SQL_INTEGER: 'i',
    SQL_LONGVARBINARY: 't',
    SQL_LONGVARCHAR: 't',
    SQL_NUMERIC: 'N',
    SQL_REAL: 'n',
    SQL_SMALLINT: 'i',
    SQL_TIME: 't',
    SQL_TIMESTAMP: 'd',
    SQL_TINYINT: 'i',
    SQL_VARBINARY: 't',
    SQL_VARCHAR: 't',
    }
tpnames={
    SQL_BIGINT: 'BIGINT',
    SQL_BINARY: 'BINARY',
    SQL_BIT: 'BIT',
    SQL_CHAR: 'CHAR',
    SQL_DATE: 'DATE',
    SQL_DECIMAL: 'DECIMAL',
    SQL_DOUBLE: 'DOUBLE',
    SQL_FLOAT: 'FLOAT',
    SQL_INTEGER: 'INTEGER',
    SQL_LONGVARBINARY: 'LONGVARBINARY',
    SQL_LONGVARCHAR: 'LONGVARCHAR',
    SQL_NUMERIC: 'NUMERIC',
    SQL_REAL: 'REAL',
    SQL_SMALLINT: 'SMALLINT',
    SQL_TIME: 'TIME',
    SQL_TIMESTAMP: 'TIMESTAMP',
    SQL_TINYINT: 'TINYINT',
    SQL_VARBINARY: 'VARBINARY',
    SQL_VARCHAR: 'VARCHAR',
    }

binary_types=SQL_BINARY, SQL_LONGVARBINARY,  SQL_VARBINARY

SQLGetColumn={'n': lambda stmt, col, binary: SQLGetFloat(stmt, col),
              'N': lambda stmt, col, binary: SQLGetFloat(stmt, col),
              'f': lambda stmt, col, binary: SQLGetFloat(stmt, col),
              'i': lambda stmt, col, binary: SQLGetInt(stmt, col),
              'l': lambda stmt, col, binary: SQLGetInt(stmt, col),
              'd': lambda stmt, col, binary: _dateTimeWrapper(SQLGetString(stmt, col, binary)),
              't': SQLGetString,
              's': SQLGetString
              }

def _dateTimeWrapper(astring):
    if astring is None:
        return None
    else:
        return DWDateTime(astring)



class DB(TM):

    def __init__(self, connection_string=''):
        self.query_timeout = 240 # NFI - was 15 # MLC - was 60
        self.connection_string=connection_string
        d=split(connection_string)
        if len(d) < 1 or len(d) > 3:
            raise 'Invalid Connection String', d
        self._connect()

    def connection_lost_error(self, (state, native, mess), routine):

        # Open IRs affected as at 19/11/2008:
        # TAUR 359565 3.05.13
        # HAWK 392635 3.04.34
        # CAMR 329748 3.05.04
        # MELV 366652 3.05.03
        # DUNE 370141 3.05.14 partial
        # MACK 333338 3.04.34 potentially
        # NSHO 336166 3.05.03 potentially, closed because they never got back to us
        # ADVA 240760         Oracle
        # 
        # ODBC Errors:
        # 08001 - Client unable to establish connection
        # 08002 - Connection name in use
        # 08003 - Connection does not exist
        # 08004 - Server rejected the connection
        # 08007 - Connection failure during transaction
        # 08S01 - Communication link failure
        # 01000/10054 - General network error
        # 01000/ 3926 - [Microsoft][SQL Native Client][SQL Server]The transaction active in this session has been committed or aborted by another session.
        # S1007 - Associated statement is not prepared
        # S1000/ 3114 - [Oracle][ODBC][Ora]ORA-03114: not connected to ORACLE
        # S1000/ 3135 - [Oracle][ODBC][Ora]ORA-03135: connection lost contact
        # 40003 - Statement completion unknown
        # HY001 - Memory allocation error
        # HY013 - Memory management error

        ret = False
        try:
            state = state.upper()
            mess = mess.upper()
            ret = (
                state.startswith("08") or
                (state=="01000" and native in (10054, 3926)) or
                (state=="S1000" and native in (3114, 3135 )) or
                state in ["40003", "HY001", "HY013", "S1007"] or
                (mess.find("COMMUNICATION LINK FAIL") > -1) or
                (mess.find("CONNECTION FAIL") > -1)  
                )
        except:
            pass
        if ret:
            LOG("ZODBCDA."+routine,ERROR,"%r Set reconnect=1" % self)
        return ret

    def warning_error(self, (state, native, mess), routine):
        ret = (state=="01003" and native in (8153, ))
        if ret: LOG("ZODBCDA."+routine, WARNING, mess)
        return ret

    def _connect(self):

        # disconnects if already connected
        if hasattr(self, 'connection'):
            LOG("ZODBCDA._connect", WARNING, "Reconnecting to ODBC %r" % self)

        #try: 
        #    del self.connection
        #    LOG("ZODBCDA._connect", WARNING, "Reconnecting to ODBC %r" % self)
        #except AttributeError: pass

        d=split(self.connection_string)
        while len(d) < 3: d.append('')

        try:            
            self.connection=c=SQLConnection(d[0],d[1],d[2])
        except error, v:
            # Note: v is None
            self.reconnect=1 # 359565
            raise error, ("",0,"Connection failed to %s" % d[0])
            
        try: self.setAutoCommit(0)
        except: LOG("ZODBCDA", ERROR, "ZODBCDA/db.py: Could not set AutoCommit OFF", error=sys.exc_info())

        self.reconnect=0
        self.lock = threading.RLock()

    def setConnectionOption(self, optname, optvalue):
        # eg. setConnectionOption("SQL_AUTOCOMMIT", "SQL_AUTOCOMMIT_ON")        
        c = self.connection
        if type(optname) == type(""): optname1 = globals()[optname]
        else: optname1 = optname
        
        if type(optvalue) == type(""): optvalue1 = globals()[optvalue]
        else: optvalue1 = optvalue
        
        try: SQLSetConnectOption(c, optname1, optvalue1)
        except: 
            try:
                # reverse dictionary lookup
                # There can be only one!
                if type(optname) <> type(""): optname = globals().keys()[globals().values().index(optname)]
                print "ZODBCDA/db.py: Could not set option " + optname
            except:
                print "ZODBCDA/db.py: Could not set unknown option."
                
    
    def setAutoCommit( self, value ):
        if value:
            self.setConnectionOption( SQL_AUTOCOMMIT, SQL_AUTOCOMMIT_ON)
        else:
            self.setConnectionOption( SQL_AUTOCOMMIT, SQL_AUTOCOMMIT_OFF)
            

    def table_info(self):
        stmt=self.connection()
        SQLTables(stmt, None, None, None, 'TABLE')
        r=[]
        for row in self._fetchResults_fast(stmt)[2]:
            q, owner, name, type, remarks = tuple(row)
            if owner: owner="(owned by %s) " % owner
            owner=owner+remarks
            if owner: owner=', '+owner
            r.append((name, owner))
        return r

    def tables(self, Qualifier=None, Owner=None, Name=None, Type=None, rdb=1):
        stmt=self.connection()
        SQLTables(stmt, Qualifier, Owner, Name, Type)
        return self._fetchResults(stmt, rdb=rdb)

    def execute(self, src=None):
        #
        # executes an SQL statement, returns the number of 
        # rows affected.
        #
        stmt = None #359565
        acquired = None #359565
        try:
            acquired=self.lock.acquire(1)
            if not acquired: raise "NoBigFatLock", "Where's the big fat lock %r" % self
            if src is not None:
                self._register()             # registers with ZODB transaction
                stmt=None
                stmt=self.connection()       # new statement handle
                try:
                    # 359565 - moved SQLSetStmtOption statements into this "try" block
                    SQLSetStmtOption(stmt, SQL_QUERY_TIMEOUT, self.query_timeout)
                    SQLSetStmtOption(stmt, SQL_CURSOR_TYPE, SQL_CURSOR_FORWARD_ONLY)

                    # 11/05/2005 CGT Log long running queries
                    t_start = time.clock()
                    SQLExecDirect(stmt,src)
                    t_end = time.clock()
                    if (t_end - t_start) > LONG_QUERY_SECS:
                        LOG("ZODBCDA.db", WARNING, "SQLExecDirect slow query: %5.1f secs" % (t_end-t_start), src)
                except error, v:
                    # 359565
                    if self.connection_lost_error(v, "execute"):
                        self.reconnect = 1
                    if self.warning_error(v, "execute"):
                        pass
                    else:
                        raise 

                hsuccessSQLRowCount, count = SQLRowCount(stmt) 

                #XXX
                status = SQLFetch(stmt)
                while status == SQL_SUCCESS: 
                    status = SQLFetch(stmt)

                return count
        finally:
            # 359565
            if stmt: 
                try:
                    SQLFreeStmt(stmt, SQL_CLOSE)
                except:
                    pass
            if acquired:
                try:
                    self.lock.release() # See Note 1
                except:
                    pass

    def query(self, src=None, max_rows=99999999, rdb=1):
        stmt = None #359565
        acquired = None #359565
        try:
            acquired=self.lock.acquire(1)
            LOG("ZODBCDA.query", WARNING, "Old query method", src)
            #LOG("ZODBCDA.query", TRACE, "RLock Count ->%r" % self.lock._RLock__count)
            if not acquired: raise "NoBigFatLock", "Where's the big fat lock"
            self._register()
            stmt=self.connection()
            try:
                # 359565 moved SQLSetStmtOption statements into this try block
                SQLSetStmtOption(stmt, SQL_QUERY_TIMEOUT, self.query_timeout)
                SQLSetStmtOption(stmt, SQL_CURSOR_TYPE, SQL_CURSOR_FORWARD_ONLY)
                if src is not None:
                    r=filter(strip,split(src,'\0'))
                    if not r: raise ValueError, 'null sql'
                    if len(r) > 1:
                        res=None
                        for s in r:
                            # 11/05/2005 CGT Log long running queries
                            t_start = time.clock()
                            SQLExecDirect(stmt,s)
                            t_end = time.clock()
                            if (t_end - t_start) > LONG_QUERY_SECS:
                                LOG("ZODBCDA.db", WARNING, "SQLExecDirect slow query: %5.1f secs" % (t_end-t_start), src)
                            status, ncol = SQLNumResultCols(stmt)
                            if ncol:
                                if res is not None:
                                    raise ValueError, (
                                        'multiple selects are not allowed')
                                res=self.query(None, max_rows, rdb)
                        if res==None:
                            if rdb: res="x\n8s\n"
                            else: res=()
                        return res

                    # 11/05/2005 CGT Log long running queries
                    t_start = time.clock()
                    SQLExecDirect(stmt,src)
                    t_end = time.clock()
                    if (t_end - t_start) > LONG_QUERY_SECS:
                        LOG("ZODBCDA.db", WARNING, "SQLExecDirect slow query: %5.1f secs" % (t_end-t_start), src)

            except error, v:
                # 359565
                if self.connection_lost_error(v, "query"):
                    self.reconnect = 1
                if self.warning_error(v, "execute"):
                    pass
                else:
                    raise 

            return self._fetchResults(stmt,rdb)

        finally:
            # 359565
            if stmt: 
                try:
                    SQLFreeStmt(stmt, SQL_CLOSE)
                except:
                    pass
            if acquired:
                try:
                    self.lock.release() # See Note 1
                except:
                    pass
            #LOG("ZODBCDA.query", TRACE, "RLock Count <-%r" % self.lock._RLock__count)


    def query_fast(self, src=None, max_rows=99999999, rdb=1):
        stmt = None #359565
        acquired = None #359565
        try:
            acquired = self.lock.acquire(1)
            #LOG("ZODBCDA.query_fast", TRACE, "RLock Count ->%r" % self.lock._RLock__count)
            if not acquired: print "NOT ACQUIRED QF"; raise "NoBigFatLock", "Where's the big fat lock"
            try:
                stmt=None
                self._register()
                stmt=self.connection()
                SQLSetStmtOption(stmt, SQL_QUERY_TIMEOUT, self.query_timeout)
                SQLSetStmtOption(stmt, SQL_CURSOR_TYPE, SQL_CURSOR_FORWARD_ONLY)
                if src is not None:
                    r=filter(strip,split(src,'\0'))
                    if not r: raise ValueError, 'null sql'
                    if len(r) > 1:
                        res=None
                        for s in r:
                            # 11/05/2005 CGT Log long running queries
                            t_start = time.clock()
                            SQLExecDirect(stmt,s)
                            t_end = time.clock()
                            if (t_end - t_start) > LONG_QUERY_SECS:
                                LOG("ZODBCDA.db", WARNING, "SQLExecDirect slow query: %5.1f secs" % (t_end-t_start), src)
                            status, ncol = SQLNumResultCols(stmt)
                            if ncol:
                                if res is not None:
                                    raise ValueError, (
                                        'multiple selects are not allowed')
                                res=self.query_fast(None, max_rows, rdb)
                        if res==None:
                            if rdb: res="x\n8s\n"
                            else: res=()
                        return res

                    # 11/05/2005 CGT Log long running queries
                    t_start = time.clock()
                    SQLExecDirect(stmt,src)
                    t_end = time.clock()
                    if (t_end - t_start) > LONG_QUERY_SECS:
                        LOG("ZODBCDA.db", WARNING, "SQLExecDirect slow query: %5.1f secs" % (t_end-t_start), src)
                                    
                retA,retB,retC = self._fetchResults_fast(stmt,rdb)
                
                return retA,retB,retC
        
            except error, v:
                # 359565
                if self.connection_lost_error(v, "query_fast"):
                    self.reconnect = 1
                if self.warning_error(v, "execute"):
                    pass
                else:
                    raise 
            
        finally:
            # 359565
            if stmt: 
                try:
                    SQLFreeStmt(stmt, SQL_CLOSE)
                except:
                    pass
            if acquired:
                try:
                    self.lock.release() # See Note 1
                except:
                    pass

    def _fetchResults(self, stmt, rdb=1):
        status, ncol = SQLNumResultCols(stmt)
        if ncol==0:
            SQLFreeStmt(stmt, SQL_CLOSE);
            if rdb: return "x\n8s\n"
            else: return ()
        r=[]
        row=['']*ncol
        names=['']*ncol
        rdbdefs=['']*ncol
        indexes=range(ncol)
        binary_flags=[0]*ncol
        for i in range(ncol):
            status, name, tp, prec, scale, nullable=SQLDescribeCol(stmt,i+1)
            names[i]=name
            if prec < 1: prec=8
            binary_flags[i]=tp in binary_types
            if defs.has_key(tp): tp=defs[tp]
            else: tp='t'
            if tp=='N' and scale==0: tp='i'
            rdbdefs[i]=tp
            row[i]="%s%s" % (prec,tp)

        if rdb:
            r.append(join(names,'\t'))
            r.append(join(row,'\t'))

        status=SQLFetch(stmt)
        while status==SQL_SUCCESS:
            for i in range(ncol):
                v=SQLGetString(stmt,i+1,binary_flags[i])
                if v is None: v=''
                if rdbdefs[i]=='t':
                    if find(v,'\\') >= 0: v=join(split(v,'\\'),'\\\\')
                    if find(v,'\n') >= 0: v=join(split(v,'\n'),'\\n')
                    if find(v,'\t') >= 0: v=join(split(v,'\t'),'\\t')
                row[i]=v
            if rdb: rd=join(row,'\t')
            else:
                rd={}
                for i in indexes: rd[names[i]]=row[i]
            r.append(rd)
            status=SQLFetch(stmt)

        SQLFreeStmt(stmt, SQL_CLOSE);
        if rdb: r=join(r,'\n')+'\n'
        return r

    def _fetchResults_fast(self, stmt, rdb=1):
        status, ncol = SQLNumResultCols(stmt)
        if ncol==0:
            SQLFreeStmt(stmt, SQL_CLOSE);
            if rdb: return "x\n8s\n"
            else: return ()

        rowNumber=0
        rows=[]
        names=['']*ncol
        rdbdefs=['']*ncol
        indexes=range(ncol)
        binary_flags=[0]*ncol
        for i in indexes:
            status, name, tp, prec, scale, nullable=SQLDescribeCol(stmt,i+1)
            names[i]=name
            binary_flags[i]=tp in binary_types
            if defs.has_key(tp): tp=defs[tp]
            else: tp='t'
            if (prec==0 or scale==0) and tp in ['n', 'N', 'f']: tp='i'
            rdbdefs[i]=tp

        status=SQLFetch(stmt)
        while status==SQL_SUCCESS:
            rows.append([])
            for i in indexes:
                v=SQLGetColumn[rdbdefs[i]](stmt,i+1,binary_flags[i])
                rows[rowNumber].append(v)

            rowNumber=rowNumber+1
            status=SQLFetch(stmt)

        return names, rdbdefs, rows


    def columns(self, table_name):
        stmt=self.connection()
        try: SQLExecDirect(stmt, 'select * from %s where 1=2' % table_name)
        except error, v:
            state, native, mess = v
            raise error, "%s (%s)" % (mess, state)

        status, ncol = SQLNumResultCols(stmt)
        r=[]
        standard_type=tpnames.has_key
        for i in range(ncol):
            status, name, tp, prec, scale, nullable=SQLDescribeCol(stmt,i+1)
            if standard_type(tp): tp=tpnames[tp]
            else: tp="Non-standard type %s" % tp
            r.append({'Name': name, 'Type': tp, 'Precision': prec,
                      'Scale': scale,
                      'Nullable': nullable and 'with Null' or ''})

        SQLFreeStmt(stmt, SQL_CLOSE);
        return r

    def _begin(self):
        # Note: this routine is called when TM._register is called
        #       for the first time in a transaction
        # This routine shouldn't fail
        try:
            if self.reconnect: LOG("ZODBCDA._begin", INFO, "reconnect: %s, %r" % (self.reconnect, self))
            if self.reconnect: self._connect()
        except:
            LOG("ZODBCDA._begin", ERROR, traceback.format_exception(*traceback.sys.exc_info()))

    def _finish(self):
        SQLTransact(self.connection, SQL_COMMIT)

    def _abort(self):
        # connection attribute may not exist if communication link was down
        if hasattr(self, 'connection'):
            SQLTransact(self.connection, SQL_ROLLBACK)
        #import inspect
        #message = "\n".join( \
        #    ["%s %s %s" % (framerecord[1], framerecord[2], framerecord[3]) \
        #    for framerecord in inspect.stack()[:5]])
        #LOG("ZODBCDA._abort", INFO, repr(self))
        #LOG("ZODBCDA.SQL_ROLLBACK", INFO, message)
        #del framerecord

if __name__=='__main__':
    #print manage_ODBCDataSources()
    db=DB('test')
    #print db.table_info()
    if len(sys.argv)==2: print db.query(sys.argv[1])
    else: print db.tables(rdb=0)
    #print db.columns('f')

      
