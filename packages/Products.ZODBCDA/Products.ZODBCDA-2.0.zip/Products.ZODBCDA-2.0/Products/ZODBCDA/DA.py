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
##############################################################################

database_type='ODBC'
__doc__='''%s Database Connection

$Id: DA.py,v 1.12 1999/09/02 14:47:38 petrilli Exp $''' % database_type
__version__='$Revision: 1.12 $'[11:-2]

from db import DB, manage_ODBCDataSources
import Shared.DC.ZRDB.Connection, sys
from Globals import HTMLFile, package_home
from App.ImageFile import ImageFile
from ExtensionClass import Base
from App.Dialogs import MessageDialog

manage_addZODBCConnectionForm=HTMLFile('connectionAdd',globals())

def manage_addZODBCConnection(self, id, title,
                                     connection_string, connection='',
                                     check=None, REQUEST=None):
    """Add a DB connection to a folder"""
    self._setObject(id, Connection(
        id, title, connection_string or connection, check))
    if REQUEST is not None: return self.manage_main(self,REQUEST)

class Connection(Shared.DC.ZRDB.Connection.Connection):
    " "
    database_type=database_type
    id='%s_database_connection' % database_type
    meta_type=title='Z %s Database Connection' % database_type
    icon='misc_/Z%sDA/conn' % database_type
    _isAnSQLConnection=1

    def factory(self): return DB

    manage_options=Shared.DC.ZRDB.Connection.Connection.manage_options+(
        {'label': 'Browse', 'action':'manage_browse'},
        # {'label': 'Design', 'action':'manage_tables'},
        )

    # manage_tables=HTMLFile('tables',globals())
    manage_browse=HTMLFile('browse',globals())
    manage_properties=HTMLFile('connectionEdit',globals())

    def connect(self, s):
        Shared.DC.ZRDB.Connection.Connection.connect(self, s)
        self._v_database_connection.id = self.id
        
    def DSN(self):
        try: return self.connection_string.split(" ", 3)[0]
        except IndexError: return ""    

    def UID(self):
        try: return self.connection_string.split(" ", 3)[1]
        except IndexError: return ""    

    def PWD(self):
        try: return self.connection_string.split(" ", 3)[2]
        except IndexError: return ""    

    def table_info(self):
        return self._v_database_connection.table_info()

    def manage_edit(self, title, DSN, UID, PWD, PWDConfirm, check=None, REQUEST=None):
        """Change connection
        """
        if PWD != PWDConfirm:
            if REQUEST is not None:
                return MessageDialog(
                    title='Error',
                    message='Passwords do not match',
                    action = './manage_properties',
                )

        connection_string = "%s %s %s" % (DSN, UID, PWD.strip())
        self.edit(title, connection_string, check)
        if REQUEST is not None:
            return MessageDialog(
                title='Edited',
                message='<strong>%s</strong> has been edited.' % self.id,
                action ='./manage_main',
                )
    info=None
        
    def tpValues(self):
        r=[]
        c=self._v_database_connection
        try:
            for d in c.tables(rdb=0):
                try:
                    d['_columns']=c.columns(d['TABLE_NAME'])
                    b=TableBrowser()
                    b._d=d
                    try: b.icon=table_icons[d['TABLE_TYPE']]
                    except: pass
                    r.append(b)
                except:
                    # print d['TABLE_NAME'], sys.exc_type, sys.exc_value
                    pass

        finally: pass
        return r

    def manage_wizard(self, tables):
        " "

    def manage_join(self, tables, select_cols, join_cols, REQUEST=None):
        """Create an SQL join"""

    def manage_insert(self, table, cols, REQUEST=None):
        """Create an SQL insert"""

    def manage_update(self, table, keys, cols, REQUEST=None):
        """Create an SQL update"""

class Browser(Base):
    def __getattr__(self, name):
        try: return self._d[name]
        except KeyError: raise AttributeError, name

class TableBrowser(Browser):
    icon='what'
    Description=''
    info=HTMLFile('table_info',globals())

    def tpValues(self):
        r=[]
        for d in self._d['_columns']:
            b=ColumnBrowser()
            b._d=d
            try: b.icon=field_icons[d['Type']]
            except: pass
            r.append(b)
        return r
            
    def tpId(self): return self._d['TABLE_NAME']
    def tpURL(self): return "Table/%s" % self._d['TABLE_NAME']
    def Name(self): return self._d['TABLE_NAME']
    def Type(self): return self._d['TABLE_TYPE']



class ColumnBrowser(Browser):
    icon='field'
    
    def tpId(self): return self._d['Name']
    def tpURL(self): return "Column/%s" % self._d['Name']
    def Description(self):
        d=self._d
        if d['Scale']:
            return " %(Type)s(%(Precision)s,%(Scale)s) %(Nullable)s" % d
        else:
            return " %(Type)s(%(Precision)s) %(Nullable)s" % d

classes=('DA.Connection',)

meta_types=(
    {'name':'Z %s Database Connection' % database_type,
     'action':'manage_addZ%sConnectionForm' % database_type,
     },
    )

folder_methods={
    'manage_addZODBCConnection':
    manage_addZODBCConnection,
    'manage_addZODBCConnectionForm':
    manage_addZODBCConnectionForm,
    'manage_ODBCDataSources': manage_ODBCDataSources
    }

__ac_permissions__=(
    ('Add Z ODBC Database Connections',
     ('manage_addZODBCConnectionForm',
      'manage_addZODBCConnection')),
    )

misc_={
    'conn':   ImageFile(package_home(globals()) + '/icons/DBAdapterFolder_icon.gif'),
    }

for icon in ('table', 'view', 'stable', 'what',
             'field', 'text','bin','int','float',
             'date','time','datetime'):
    misc_[icon]=ImageFile('icons/%s.gif' % icon, globals())

table_icons={
    'TABLE': 'table',
    'VIEW':'view',
    'SYSTEM_TABLE': 'stable',
    }

field_icons={
    'BIGINT': 'int',
    'BINARY': 'bin',
    'BIT': 'bin',
    'CHAR': 'text',
    'DATE': 'date',
    'DECIMAL': 'float',
    'DOUBLE': 'float',
    'FLOAT': 'float',
    'INTEGER': 'int',
    'LONGVARBINARY': 'bin',
    'LONGVARCHAR': 'text',
    'NUMERIC': 'float',
    'REAL': 'float',
    'SMALLINT': 'int',
    'TIME': 'time',
    'TIMESTAMP': 'datetime',
    'TINYINT': 'int',
    'VARBINARY': 'bin',
    'VARCHAR': 'text',
    }

