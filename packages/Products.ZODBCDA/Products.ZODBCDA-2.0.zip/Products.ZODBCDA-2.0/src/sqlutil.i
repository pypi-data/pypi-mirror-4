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


%{
static char *
PySequence_CharArray(PyObject *s, int *OUTPUT)
{
  Py_ssize_t d;
  if((d=PyString_Size(s)) < 0) 
  {
    *OUTPUT = (int) d;
    return NULL;
  }
  *OUTPUT = (int) d;
  return PyString_AsString(s);
}  

static void ___FreeConnect(void *p)
{
  if(p && (SQLHDBC*)p != SQL_NULL_HDBC)
    {
      UNLESS(SQLFreeConnect(*(SQLHDBC*)p) == SQL_SUCCESS)
	PyErr_SetString(PyExc_SQLError,
			"error calling SQLFreeConnect in destructor");
      free(p);
    }
}

static void ___FreeStmt(void *p)
{
  if(p && (SQLHSTMT*)p != SQL_NULL_HSTMT)
    {
      UNLESS(SQLFreeStmt(*(SQLHSTMT*)p, SQL_DROP) == SQL_SUCCESS)
	PyErr_SetString(PyExc_SQLError,
			"error calling SQLFreeStmt in destructor");
      free(p);
    }
}

%}

%include typemaps.i

%typemap(python, ignore) SQLHDBC * {
  $target = ($type)malloc(sizeof(SQLHDBC));
}

%typemap(python,argout,fragment="t_output_helper") SQLHDBC * {
  $target = t_output_helper($target,PyCObject_FromVoidPtr((void*)$source,
							  ___FreeConnect));
}

%typemap(python, ignore) SQLHSTMT * {
  $target = ($type)malloc(sizeof(SQLHSTMT));
}

%typemap(python,argout) SQLHSTMT * {
  $target = t_output_helper($target, PyCObject_FromVoidPtr((void*)$source,
							   ___FreeStmt));
}

%typemap(python,ignore) SQLHENV { $target=SQLEnv; }

%typemap(python,in) SQLHDBC(SQLHDBC handle) {
  if($source==Py_None) $target=NULL;
  else if($source->ob_type == &ConnectionType)
    {
      $target = ((Connection*)$source)->connection;
    }
  else
    {
      UNLESS(PyCObject_Check($source))
	{
	  PyErr_SetString(PyExc_TypeError,
			  "Expected CObject");
	  return NULL;
	}
      $target=*($type *)PyCObject_AsVoidPtr($source);
    }
  handle=$target;
}

%typemap(python,in) SQLHSTMT(SQLHSTMT handle) {
  if($source==Py_None) $target=NULL;
  else if($source->ob_type == &StatementType)
    {
      $target = ((Statement*)$source)->stmt;
    }
  else
    {
      UNLESS(PyCObject_Check($source))
	{
	  PyErr_SetString(PyExc_TypeError,
			  "Expected CObject");
	  return NULL;
	}
      $target=*($type *)PyCObject_AsVoidPtr($source);
    }
  handle=$target;
}

%typemap(in, numinputs=0) (SQLCHAR *OUT1, SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) ( char lpszOut[256], SQLSMALLINT odim = 0) { $1 = lpszOut; $2 = 256; $3 = &odim; }
%typemap(argout         ) (SQLCHAR *OUT1, SQLSMALLINT DIM1, SQLSMALLINT *ODIM1)                      { $result = t_output_helper($result, PyString_FromStringAndSize( $1, *$3)); }
%apply                    (SQLCHAR *OUT1, SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) { (SQLCHAR *OUT2, SQLSMALLINT DIM2, SQLSMALLINT *ODIM2) };
%apply                    (SQLCHAR *OUT1, SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) { (SQLCHAR *OUT3, SQLSMALLINT DIM3, SQLSMALLINT *ODIM3) };
%apply                    (SQLCHAR *OUT1, SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) { (SQLCHAR *OUT4, SQLSMALLINT DIM4, SQLSMALLINT *ODIM4) };

/* SQLPOINTER* [Output] A pointer to memory in which to return the
   current value of the attribute specified by Attribute in SQLGetConnectAttribute.
   For integer-type attributes, drivers may write lower 32 bit of a buffer but leave
   higher-order bit unchanged. Use a bufer of SQLULEN and initialize to 0 
   before calling SQLGetConnectAttribute
*/
%typemap(in, numinputs=0) 
    ( SQLPOINTER ,  SQLINTEGER  , SQLINTEGER* ) 
    ( SQLCHAR buf[256], SQLINTEGER szbuf = 0 ) {
    $1=buf; $2=256; $3=&szbuf; 
}

%typemap(argout) ( SQLPOINTER , SQLINTEGER , SQLINTEGER*) {
    $result = t_output_helper($result, PyString_FromStringAndSize($1, *$3));
}

%typemap(in, numinputs=0) 
    ( SQLPOINTER OUT1,  SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) 
    ( SQLCHAR buf[256], SQLSMALLINT szbuf  = 0) {
    $1=buf; $2=256; $3=&szbuf; 
}

%typemap(argout) ( SQLPOINTER OUT1,  SQLSMALLINT DIM1, SQLSMALLINT *ODIM1) {
    $result = PyString_FromStringAndSize($1, *$3);
}


/* CGT parse strings into two parameters -> char*, int size */
%typemap(python, in, numinputs=1) (SQLCHAR *IN1, SQLSMALLINT DIM1) (int sz=0)
  { 
    if($source==Py_None) { $1=NULL; }
    else UNLESS($target=PySequence_CharArray($source, &sz)) return NULL; 
    $2=sz;
  }

%apply (SQLCHAR *IN1, SQLSMALLINT DIM1) {
       (SQLCHAR *IN2, SQLSMALLINT DIM2) ,
       (SQLCHAR *IN3, SQLSMALLINT DIM3) ,
       (SQLCHAR *IN4, SQLSMALLINT DIM4)
}

%typemap(python, in, numinputs=1) (SQLCHAR *IN1, SQLINTEGER  DIM1)
  { 
    if($source==Py_None) { $1=NULL; }
    else UNLESS($target=PySequence_CharArray($source, &$2)) return NULL; 
  }

%typemap(in, numinputs=0) SQLCHAR *szSqlState (char buf[6]) { $1=buf;}
%typemap(argout)          SQLCHAR *szSqlState (char buf[6]) { $result = t_output_helper($result, PyString_FromStringAndSize(buf, 5)); }


%typemap(in, numinputs=0) SQLLEN *T_OUTPUT (SQLLEN temp)   { $1=&temp; }
%typemap(argout) SQLLEN *T_OUTPUT {$result = t_output_helper($result, SWIG_From_long((long) *$1));};

%typemap(in, numinputs=0) SQLULEN *T_OUTPUT (SQLULEN temp)   { $1=&temp; }
%typemap(argout) SQLULEN *T_OUTPUT {$result = t_output_helper($result, SWIG_From_long((long) *$1));};

/* Used for SQLGetConnectOption */
%typemap(in, numinputs=0) SQLPOINTER *OUTPUT (SQLPOINTER temp) { $1=&temp; }
%typemap(argout) SQLPOINTER *OUTPUT { $result = t_output_helper($result, PyString_FromString((char*) $1)); }
