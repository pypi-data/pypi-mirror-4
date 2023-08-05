/*****************************************************************************
 
  Zope Public License (ZPL) Version 0.9.4
  ---------------------------------------
  
  Copyright (c) Digital Creations.  All rights reserved.
  
  Redistribution and use in source and binary forms, with or
  without modification, are permitted provided that the following
  conditions are met:
  
  1. Redistributions in source code must retain the above
     copyright notice, this list of conditions, and the following
     disclaimer.
  
  2. Redistributions in binary form must reproduce the above
     copyright notice, this list of conditions, and the following
     disclaimer in the documentation and/or other materials
     provided with the distribution.
  
  3. Any use, including use of the Zope software to operate a
     website, must either comply with the terms described below
     under "Attribution" or alternatively secure a separate
     license from Digital Creations.
  
  4. All advertising materials, documentation, or technical papers
     mentioning features derived from or use of this software must
     display the following acknowledgement:
  
       "This product includes software developed by Digital
       Creations for use in the Z Object Publishing Environment
       (http://www.zope.org/)."
  
  5. Names associated with Zope or Digital Creations must not be
     used to endorse or promote products derived from this
     software without prior written permission from Digital
     Creations.
  
  6. Redistributions of any form whatsoever must retain the
     following acknowledgment:
  
       "This product includes software developed by Digital
       Creations for use in the Z Object Publishing Environment
       (http://www.zope.org/)."
  
  7. Modifications are encouraged but must be packaged separately
     as patches to official Zope releases.  Distributions that do
     not clearly separate the patches from the original work must
     be clearly labeled as unofficial distributions.
  
  Disclaimer
  
    THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS ``AS IS'' AND
    ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
    FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT
    SHALL DIGITAL CREATIONS OR ITS CONTRIBUTORS BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
    CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
    LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
    IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
    THE POSSIBILITY OF SUCH DAMAGE.
  
  Attribution
  
    Individuals or organizations using this software as a web site
    must provide attribution by placing the accompanying "button"
    and a link to the accompanying "credits page" on the website's
    main entry point.  In cases where this placement of
    attribution is not feasible, a separate arrangment must be
    concluded with Digital Creations.  Those using the software
    for purposes other than web sites must provide a corresponding
    attribution in locations that include a copyright using a
    manner best suited to the application environment.
  
  This software consists of contributions made by Digital
  Creations and many individuals on behalf of Digital Creations.
  Specific attributions are listed in the accompanying credits
  file.
  
 ****************************************************************************/

static PyObject *
SQLException(SQLHDBC hdbc, SQLHSTMT hstmt);

typedef struct {
  PyObject_HEAD
  SQLHDBC connection;
} Connection;

typedef struct {
  PyObject_HEAD
  Connection *connection;
  SQLHSTMT stmt;
} Statement;

staticforward PyTypeObject StatementType;

static void
Connection_dealloc(Connection *self)
{
  if(self->connection != SQL_NULL_HDBC)
    {
      UNLESS(SQLDisconnect(self->connection) == SQL_SUCCESS &&
	     SQLFreeConnect(self->connection) == SQL_SUCCESS)
	PyErr_SetString(PyExc_SQLError,
			"error in SQL connection destructor");
    }
  PyObject_FREE(self);
}

static PyObject *
Connection_call(Connection *self, PyObject *args, PyObject *kw)
{
  Statement *stmt;

  UNLESS(stmt = PyObject_NEW(Statement, &StatementType)) return NULL;
  stmt->connection=self;
  Py_INCREF(self);
  UNLESS(SQLAllocStmt(self->connection, &(stmt->stmt)) == SQL_SUCCESS)
    {
      Py_DECREF(stmt);
      return SQLException(self->connection, SQL_NULL_HSTMT);
    }
  return (PyObject*)stmt;
}

static PyTypeObject ConnectionType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "Connection",			/*tp_name*/
  sizeof(Connection),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)Connection_dealloc,	/*tp_dealloc*/
  (printfunc)0,	/*tp_print*/
  (getattrfunc)0,		/*obsolete tp_getattr*/
  (setattrfunc)0,		/*obsolete tp_setattr*/
  (cmpfunc)0,	/*tp_compare*/
  (reprfunc)0,		/*tp_repr*/
  0,		/*tp_as_number*/
  0,		/*tp_as_sequence*/
  0,		/*tp_as_mapping*/
  (hashfunc)0,		/*tp_hash*/
  (ternaryfunc)Connection_call,	/*tp_call*/
  (reprfunc)0,		/*tp_str*/
  (getattrofunc)0,	/*tp_getattro*/
  (setattrofunc)0,	/*tp_setattro*/
  0,                /*tp_as_buffer*/
  0,                /*tp_flags*/
  "ODBC/CLI database connections",
};

static void
Statement_dealloc(Statement *self)
{
  if(self->stmt != SQL_NULL_HSTMT &&
     SQLFreeStmt(self->stmt, SQL_DROP) != SQL_SUCCESS)
    PyErr_SetString(PyExc_SQLError,
		    "error in SQL statement destructor");
  Py_DECREF(self->connection);
  PyObject_FREE(self);
}

static PyTypeObject StatementType = {
  PyObject_HEAD_INIT(NULL)
  0,				/*ob_size*/
  "Statement",			/*tp_name*/
  sizeof(Statement),		/*tp_basicsize*/
  0,				/*tp_itemsize*/
  /* methods */
  (destructor)Statement_dealloc,	/*tp_dealloc*/
  (printfunc)0,	/*tp_print*/
  (getattrfunc)0,		/*obsolete tp_getattr*/
  (setattrfunc)0,		/*obsolete tp_setattr*/
  (cmpfunc)0,	/*tp_compare*/
  (reprfunc)0,		/*tp_repr*/
  0,		/*tp_as_number*/
  0,		/*tp_as_sequence*/
  0,		/*tp_as_mapping*/
  (hashfunc)0,		/*tp_hash*/
  (ternaryfunc)0,	/*tp_call*/
  (reprfunc)0,		/*tp_str*/
  (getattrofunc)0,	/*tp_getattro*/
  (setattrofunc)0,	/*tp_setattro*/
  
  /* Space for future expansion */
  0L,0L,
  "ODBC/CLI Statement handles"
};
