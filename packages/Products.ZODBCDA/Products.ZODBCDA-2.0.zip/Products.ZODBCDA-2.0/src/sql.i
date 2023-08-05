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

%module sql
%{
#ifdef SOLIDSQLAPI
#include "cli0defs.h"
#include "cli0core.h"
#include "cli0ext1.h"
#define SQLHENV HENV
#define SQLHDBC HDBC
#define SQLHSTMT HSTMT

typedef UCHAR                   SQLCHAR;
typedef SCHAR                   SQLSCHAR;
typedef SDWORD                  SQLINTEGER;
typedef SWORD                   SQLSMALLINT;
typedef UDWORD                  SQLUINTEGER;
typedef UWORD                   SQLUSMALLINT;
typedef void*              SQLPOINTER;

SWORD SQLDataSources(
    SQLHENV            henv,
    SQLUSMALLINT       fDirection,
    SQLCHAR       *OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT   *ODIM1,
    SQLCHAR       *OUT2,
    SQLSMALLINT        DIM2,
    SQLSMALLINT   *ODIM2)
{
  return SQL_NO_DATA_FOUND;
}

#else
#include <windows.h>
#include "sql.h"
#include "sqlext.h"
#endif

#include "datetime.h"

static PyObject *PyExc_SQLError;
static SQLHENV SQLEnv;

static void
PyVar_Assign(PyObject **v,  PyObject *e)
{
  Py_XDECREF(*v);
  *v=e;
}

#define ASSIGN(V,E) PyVar_Assign(&(V),(E))
#define UNLESS(E) if(!(E))
#define UNLESS_ASSIGN(V,E) ASSIGN(V,E); UNLESS(V)

#include "pysql.c"

%}

%include sqlutil.i
%include pointer.i
%include sqldefs.i

#define RC_INVOKED
%include sqlext.h

/* CGT New SWIG 2.0 uses OUTPUT instead of T_OUTPUT */
%apply           long *OUTPUT { SQLINTEGER   *T_OUTPUT };
%apply  unsigned long *OUTPUT { SQLUINTEGER  *T_OUTPUT };
%apply          short *OUTPUT { SQLSMALLINT  *T_OUTPUT };
%apply unsigned short *OUTPUT { SQLUSMALLINT *T_OUTPUT };

/* Core Function Prototypes */

SWORD SQLDataSources(
    SQLHENV            henv,
    SQLUSMALLINT       fDirection,
    SQLCHAR       *OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT   *ODIM1,
    SQLCHAR       *OUT2,
    SQLSMALLINT        DIM2,
    SQLSMALLINT   *ODIM2);

SWORD SQLError(
    SQLHENV            henv,
    SQLHDBC            hdbc,
    SQLHSTMT           hstmt,
    SQLCHAR       *szSqlState,
    SQLINTEGER    *T_OUTPUT,
    SQLCHAR       *OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT   *ODIM1);

SWORD SQLTransact(
    SQLHENV            henv,
    SQLHDBC            hdbc,
    SQLUSMALLINT       fType);

%inline %{

static PyObject *
SQLException(SQLHDBC hdbc, SQLHSTMT hstmt)
  {
    char state[6];
    SDWORD native;
    char mess[SQL_MAX_MESSAGE_LENGTH];
    SWORD lmess;
    SWORD status;
    PyObject *v;
    SWIG_PYTHON_THREAD_BEGIN_BLOCK;

    status=SQLError(SQLEnv, hdbc, hstmt,state,&native,
		      mess,SQL_MAX_MESSAGE_LENGTH-1,&lmess);

     if(status != SQL_SUCCESS ||
	 !(v=Py_BuildValue("s#is#",state,5,(long)native,mess,lmess))
	 )
	{
	  v=Py_None;
	  Py_INCREF(v);
	}
    PyErr_SetObject(PyExc_SQLError,v);
    Py_DECREF(v);

    SWIG_PYTHON_THREAD_END_BLOCK; 

    return NULL;
  }

static PyObject *
SQLGetBool(SQLHSTMT hstmt, SQLUSMALLINT icol)
  {
    SQLCHAR v;
    SWORD status;
    SQLLEN sz;

    status=SQLGetData(hstmt, icol, SQL_C_BIT, &v, sizeof(v), &sz);
    
    if(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO)
    {
      if(sz==SQL_NULL_DATA) 
      {
        Py_INCREF(Py_None);
        return Py_None;
      }
      else
      {
        return PyBool_FromLong((long) v);
      }
    }

    return SQLException(SQL_NULL_HDBC, hstmt);      
  }

static PyObject *
SQLGetDateTime(SQLHSTMT hstmt, SQLUSMALLINT icol)
  {
    struct tagTIMESTAMP_STRUCT {
       SQLSMALLINT year;
       SQLUSMALLINT month;
       SQLUSMALLINT day;
       SQLUSMALLINT hour;
       SQLUSMALLINT minute;
       SQLUSMALLINT second;
       SQLUINTEGER fraction;
    } v; 

    SWORD status;
    SQLLEN sz;

    status=SQLGetData(hstmt, icol, SQL_C_TIMESTAMP, &v, sizeof(v), &sz);
    
    if(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO)
    {
      if(sz==SQL_NULL_DATA) 
      {
        Py_INCREF(Py_None);
        return Py_None;
      }
      else
        return PyDateTime_FromDateAndTime(v.year, v.month, v.day, v.hour, v.minute, v.second, v.fraction);
    }

    return SQLException(SQL_NULL_HDBC, hstmt);      
  }

static PyObject *
SQLGetFloat(SQLHSTMT hstmt, SQLUSMALLINT icol)
  {
    double v;
    SWORD status;
    SQLLEN sz;

    status=SQLGetData(hstmt, icol, SQL_C_DOUBLE, &v, sizeof(v), &sz);
    
    if(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO)
    {
      if(sz==SQL_NULL_DATA) 
      {
        Py_INCREF(Py_None);
        return Py_None;
      }
      else
        return PyFloat_FromDouble(v);
    }

    return SQLException(SQL_NULL_HDBC, hstmt);      
  }

static PyObject *
SQLGetLong(SQLHSTMT hstmt, SQLUSMALLINT icol)
{
    _int64 v;
  
    SWORD status;
    SQLLEN sz;

    status=SQLGetData(hstmt, icol, SQL_C_SBIGINT, &v, sizeof(v), &sz);
    
    if(status!=SQL_SUCCESS && status!=SQL_SUCCESS_WITH_INFO)
        return SQLException(SQL_NULL_HDBC, hstmt);      

    if (sz==SQL_NULL_DATA)
    {
        Py_INCREF(Py_None);
        return Py_None;
    }
    else
    {
        return PyLong_FromLongLong(v);
    }

}

static PyObject *
SQLGetInt(SQLHSTMT hstmt, SQLUSMALLINT icol)
  {
    long v;
    SWORD status;
    SQLLEN sz;

    status=SQLGetData(hstmt, icol, SQL_C_SLONG, &v, sizeof(v), &sz);
    
    if(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO)
    {
      if(sz==SQL_NULL_DATA) 
      {
	    Py_INCREF(Py_None);
        return Py_None;
      }
      else 
        return PyInt_FromLong(v);
    }

    return SQLException(SQL_NULL_HDBC, hstmt);      
  }

static PyObject *
SQLGetString(SQLHSTMT hstmt, SQLUSMALLINT icol, int binary)
  {
#define BUFSIZE 256 
    char v[BUFSIZE];
    SWORD status, fCType;
    SQLLEN sz;
    PyObject *list=0, *s=0;

    fCType=binary ? SQL_C_BINARY : SQL_C_CHAR;
    status=SQLGetData(hstmt, icol, fCType, &v, BUFSIZE, &sz);
    if(sz==SQL_NULL_DATA) return PyString_FromString("");
    if(binary)
      {
	if(sz==SQL_NO_TOTAL || sz > BUFSIZE) sz=BUFSIZE;
      }
    else if(sz==SQL_NO_TOTAL || sz > BUFSIZE-1) sz=BUFSIZE-1;

    if(status==SQL_SUCCESS) return PyString_FromStringAndSize(v,sz);
    UNLESS(list=PyList_New(0)) return NULL;
    while(status==SQL_SUCCESS_WITH_INFO)
      {
	char state[6];
	char mess[1];
	SDWORD native;
	SWORD esz, estatus;

	estatus=SQLError(SQLEnv, SQL_NULL_HDBC, hstmt, state, &native,
		    mess,1,&esz);

	if(estatus != SQL_SUCCESS && estatus != SQL_SUCCESS_WITH_INFO) break;
	if(strcmp(state,"01004") != 0) break;
	       
	UNLESS(s=PyString_FromStringAndSize(v,sz)) goto err;
	if(PyList_Append(list,s) < 0) goto err;
	Py_DECREF(s);
        status=SQLGetData(hstmt, icol, fCType, &v, BUFSIZE, &sz);    
	if(binary)
	  {
	    if(sz==SQL_NO_TOTAL || sz > BUFSIZE) sz=BUFSIZE;
	  }
	else if(sz==SQL_NO_TOTAL || sz > BUFSIZE-1) sz=BUFSIZE-1;
      }
    
    if(status==SQL_SUCCESS)
      {
	static PyObject *join=0, *empty=0;

    SWIG_PYTHON_THREAD_BEGIN_BLOCK;
	if(! empty)
	  {
	    UNLESS(join=PyImport_ImportModule("string")) goto err;
	    UNLESS_ASSIGN(join, PyObject_GetAttrString(join,"join")) goto err;
	    UNLESS(empty=PyString_FromString("")) goto err;
	  }

	UNLESS(s=PyString_FromStringAndSize(v,sz)) goto err;
	if(PyList_Append(list,s) < 0) goto err;

	ASSIGN(s,PyObject_CallFunction(join,"OO",list,empty));
	Py_DECREF(list);
    SWIG_PYTHON_THREAD_END_BLOCK;
	return s;
      }

    SQLException(SQL_NULL_HDBC, hstmt);
  err:

    Py_XDECREF(list);
    Py_XDECREF(s);
    return NULL;
  }

static PyObject *
SQLDriverConnection(
    char*      conn_string,
    SQLUSMALLINT driverCompletion)
{
  SWORD       status;
  Connection *self;
  SQLSMALLINT BUFLEN = 1024;
  SQLSMALLINT buflenRequired;
  SQLCHAR  * outBuf = malloc(BUFLEN);
  PyObject * result = NULL;

  memset(outBuf, 0, BUFLEN);

  UNLESS(self = PyObject_NEW(Connection, &ConnectionType)) return NULL;

  status=SQLAllocConnect(SQLEnv, &(self->connection));
  UNLESS(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO) goto err;
  
  status = SQLDriverConnect(self->connection, NULL, conn_string, (SQLSMALLINT) strlen(conn_string), 
    outBuf, BUFLEN, &buflenRequired, driverCompletion);
  if (BUFLEN < buflenRequired)
  {
    free(outBuf);
    outBuf = malloc(buflenRequired+2); /* must be even for wchar */
    memset(outBuf, 0, buflenRequired+2);
    status = SQLDriverConnect(self->connection, NULL, conn_string, (SQLSMALLINT) strlen(conn_string), 
      outBuf, buflenRequired, &buflenRequired, driverCompletion);
  }
  UNLESS(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO) goto err;

  result = SWIG_Python_AppendOutput((PyObject*) self, PyString_FromStringAndSize(outBuf, buflenRequired));
  free(outBuf);
  return result;

err:
  free(outBuf);

  self->connection=SQL_NULL_HDBC;
  Py_DECREF(self);
  return SQLException(SQL_NULL_HDBC, SQL_NULL_HSTMT);
}
    
     
static PyObject *
SQLConnection(
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3)
{
  Connection *self;
  SWORD status;
	
  UNLESS(self = PyObject_NEW(Connection, &ConnectionType)) return NULL;

  status=SQLAllocConnect(SQLEnv, &(self->connection));
  UNLESS(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO) goto err;

  status=SQLConnect(self->connection,IN1,DIM1,IN2,DIM2,IN3,DIM3);
  UNLESS(status==SQL_SUCCESS || status==SQL_SUCCESS_WITH_INFO) goto err;

  return (PyObject*)self;

err:
  self->connection=SQL_NULL_HDBC;
  Py_DECREF(self);
  return SQLException(SQL_NULL_HDBC, SQL_NULL_HSTMT);
}

%}


SWORD SQLFetch(
    SQLHSTMT           hstmt);

%except(python) {
  SWORD status;
  status=$function;
  if(status != SQL_SUCCESS && status != SQL_SUCCESS_WITH_INFO)
    return SQLException(SQL_NULL_HDBC, SQL_NULL_HSTMT);
}

SWORD SQLAllocConnect(
    SQLHENV            henv,
    SQLHDBC       *phdbc);


%exception {
  $action;
  UNLESS (result ==SQL_SUCCESS || result==SQL_SUCCESS_WITH_INFO)
    return SQLException(handle1, SQL_NULL_HSTMT);
}

   
SWORD SQLConnect(
    SQLHDBC            hdbc,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3);

SWORD SQLDisconnect(
    SQLHDBC            hdbc);

SWORD SQLAllocStmt(
    SQLHDBC            hdbc,
    SQLHSTMT      *phstmt);

SWORD SQLGetConnectOption(
    SQLHDBC            hdbc,
    SQLUSMALLINT       fOption,
    SQLPOINTER         *OUTPUT);

SWORD SQLGetFunctions(
    SQLHDBC            hdbc,
    SQLUSMALLINT       fFunction,
    SQLUSMALLINT  *T_OUTPUT);

SWORD SQLGetInfo(
    SQLHDBC            hdbc,
    SQLUSMALLINT       fInfoType,
    SQLPOINTER         OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT   *ODIM1);

SWORD SQLSetConnectOption(
    SQLHDBC            hdbc,
    SQLUSMALLINT       fOption,
    SQLUINTEGER        vParam);

%typemap(except) SWORD 
{
    $action;
    UNLESS ($1==SQL_SUCCESS || $1==SQL_SUCCESS_WITH_INFO)
        return SQLException(SQL_NULL_HDBC, handle1);
        
}

SWORD SQLFreeStmt(
    SQLHSTMT           hstmt,
    UWORD              foption);

SWORD SQLBindCol(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       icol,
    SQLSMALLINT        fCType,
    SQLPOINTER         rgbValue,
    SQLLEN             cbValueMax,
    SQLLEN        *pcbValue);

%inline %{

SWORD SQLBindInputParameter(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       ipar,
    SQLSMALLINT        fSqlType,
    PyObject *v
    )
{
  void *p;
  SQLLEN *lp;

  if(PyString_Check(v))
    {
      p=PyString_AsString(v);
      lp=&(((PyStringObject*)v)->ob_size);
      return SQLBindParameter(hstmt,ipar,SQL_PARAM_INPUT,SQL_C_BINARY,
			      fSqlType,*lp,0,
			      p,*lp,lp);
    }
  else if(PyInt_Check(v))
    {
      p=&(((PyIntObject*)v)->ob_ival);
      return SQLBindParameter(hstmt,ipar,SQL_PARAM_INPUT,SQL_C_SLONG,
			      fSqlType,0,0,
			      p,sizeof(long),NULL);
    }
  else if(PyFloat_Check(v))
    {
      p=&(((PyFloatObject*)v)->ob_fval);
      return SQLBindParameter(hstmt,ipar,SQL_PARAM_INPUT,SQL_C_DOUBLE,
			      fSqlType,0,0,
			      p,sizeof(double),NULL);
    }
  return 0;
}

%}

SWORD SQLCancel(
    SQLHSTMT           hstmt);

SWORD SQLColAttributes(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       icol,
    SQLUSMALLINT       fDescType,
    SQLPOINTER         OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT       *ODIM1,
    SQLLEN            *T_OUTPUT);

SWORD SQLDescribeCol(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       icol,
    SQLCHAR       *OUT1,
    SQLSMALLINT        DIM1,
    SQLSMALLINT   *ODIM1,
    SQLSMALLINT   *T_OUTPUT,
    SQLULEN       *T_OUTPUT,
    SQLSMALLINT   *T_OUTPUT,
    SQLSMALLINT   *T_OUTPUT);

SWORD SQLExecDirect(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLINTEGER         DIM1);

SWORD SQLExecute(
    SQLHSTMT           hstmt);

SWORD SQLGetCursorName(
    SQLHSTMT           hstmt,
    SQLCHAR       *OUT1,
    SQLSMALLINT    DIM1,
    SQLSMALLINT   *ODIM1);

SWORD SQLNumResultCols(
    SQLHSTMT           hstmt,
    SQLSMALLINT   *T_OUTPUT);

SWORD SQLPrepare(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLINTEGER     DIM1);

SWORD SQLRowCount(
    SQLHSTMT           hstmt,
    SQLLEN        *T_OUTPUT);

SWORD SQLSetCursorName(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1);

/* Level 1 Prototypes */
SWORD SQLColumns(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3,
    SQLCHAR       *IN4,
    SQLSMALLINT        DIM4);

SWORD SQLGetData(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       icol,
    SQLSMALLINT        fCType,
    SQLPOINTER         rgbValue,
    SQLLEN             cbValueMax,
    SQLLEN        *pcbValue);

SWORD SQLGetStmtOption(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       fOption,
    SQLPOINTER         pvParam);

SWORD SQLGetTypeInfo(
    SQLHSTMT           hstmt,
    SQLSMALLINT        fSqlType);

SWORD SQLParamData(
    SQLHSTMT           hstmt,
    SQLPOINTER    *prgbValue);

SWORD SQLPutData(
    SQLHSTMT           hstmt,
    SQLCHAR             *IN1,
    SQLINTEGER         DIM1);

SWORD SQLSetStmtOption(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       fOption,
    SQLUINTEGER        vParam);

SWORD SQLSpecialColumns(
    SQLHSTMT           hstmt,
    SQLUSMALLINT       fColType,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3,
    SQLUSMALLINT       fScope,
    SQLUSMALLINT       fNullable);

SWORD SQLStatistics(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3,
    SQLUSMALLINT       fUnique,
    SQLUSMALLINT       fAccuracy);

SWORD SQLTables(
    SQLHSTMT           hstmt,
    SQLCHAR       *IN1,
    SQLSMALLINT        DIM1,
    SQLCHAR       *IN2,
    SQLSMALLINT        DIM2,
    SQLCHAR       *IN3,
    SQLSMALLINT        DIM3,
    SQLCHAR       *IN4,
    SQLSMALLINT        DIM4);

#define error "sql.error"
#define SQL_OV_ODBC3                        3UL /* CGT hack */

%init %{

  /* To return datetime object, have to initialize this macro
     http://ramblings.timgolden.me.uk/2010/06/18/return-datetime-object-from-c-extension/ */
  PyDateTime_IMPORT;

  /* Define a new Exception type */
  PyExc_SQLError=PyErr_NewException("sql.error", NULL, NULL);
  PyDict_SetItemString(d, "error", PyExc_SQLError);

  PyDict_SetItemString(d,"__version__",
		       PyString_FromStringAndSize(
                          "$Revision: 1.3 $"+11,
                          strlen("$Revision: 1.3 $"+11)-2));

  if(sizeof(SDWORD) != sizeof(int))
    PyErr_SetString(PyExc_SQLError, 
		    "Binding parameters will fail because SDWORD is\n"
		    "not the same size as an int!"
		    );

  UNLESS(SQLAllocEnv(&SQLEnv)==SQL_SUCCESS)
    PyErr_SetString(PyExc_SQLError, "could not allocate environment");

  /*
  UNLESS(SQLSetEnvAttr(SQLEnv, SQL_ATTR_ODBC_VERSION, (SQLPOINTER*) SQL_OV_ODBC3, 0))
    PyErr_SetString(PyExc_SQLError, "could not set odbc driver to version 3.0");
  */

%}
