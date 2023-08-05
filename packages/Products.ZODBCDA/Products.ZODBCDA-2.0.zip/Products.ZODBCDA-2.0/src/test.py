import sql
import unittest
import datetime

connString = "UID=ecm402iis;PWD=ecm402iis;Driver=SQL Server Native Client 10.0;Server=.\\SQL2008R2;Database=ecm402iis"
connParams = ("ecm402iis", "ecm402iis", "ecm402iis")

class TestCase(unittest.TestCase):

  def setUp(self):
      self.c = self.testDriverConnect()

  def tearDown(self):
      del self.c

  def testBadConnection(self):
      with self.assertRaises(sql.error):
          badConnParams = (connParams[0] + 'XXX', connParams[1], connParams[2])
          sql.SQLConnection(*badConnParams)

  def testSQLConnect(self):
      hdbc = sql.SQLConnection(*connParams)
      self.dsn = connParams[0]
      return hdbc 

  def testDriverConnect(self):
      hdbc, info = sql.SQLDriverConnection(connString, sql.SQL_DRIVER_NOPROMPT)  
      self.assertTrue(info.startswith("DRIVER=SQL Server Native Client 10.0"), info)
      self.dsn = ""
      return hdbc

  def testDriverConnect2(self):
      connString = "DSN=ecm402iis;UID=ecm402iis;PWD=ecm402iis"
      hdbc, info = sql.SQLDriverConnection(connString, sql.SQL_DRIVER_NOPROMPT)  
      self.assertTrue(info.startswith("DSN=ecm402iis"), info)
      return hdbc

  def testStatement(self):

      stmt = self.c()
      results = sql.SQLPrepare(stmt, "SELECT UserId, LogonName FROM Users")
      results = sql.SQLExecute(stmt)
      success, columnname, columntype, size, digits, nullable = sql.SQLDescribeCol(stmt, 1)
      self.assertEqual(columnname, 'UserId')
      success, columnname, columntype, size, digits, nullable = sql.SQLDescribeCol(stmt, 2)
      self.assertEqual(columnname, 'LogonName')

      # this should fail
      with self.assertRaises(sql.error):
          success, columnname, columntype, size, digits, nullable = sql.SQLDescribeCol(stmt, 0)

      # get number of columns
      status, ncol = sql.SQLNumResultCols(stmt)
      for i in range(ncol):
          # ODBC column numbers are 1-based
          status, name, tp, prec, scale, nullable=sql.SQLDescribeCol(stmt,i+1)
          sql.SQLDescribeCol(stmt, i+1)


  def testConnectionInfo(self):

      result = sql.SQLGetInfo(self.c, sql.SQL_DATA_SOURCE_NAME)
      self.assertEqual(result, self.dsn)

      result = sql.SQLGetInfo(self.c, sql.SQL_DRIVER_ODBC_VER)
      self.assertEqual(result, '03.52')

      result = sql.SQLGetInfo(self.c, sql.SQL_DRIVER_NAME)
      self.assertEqual(result, 'sqlncli10.dll')

  def testPreparedStatement(self):

      stmt = self.c()
      results = sql.SQLPrepare(stmt, "SELECT UserId, LogonName FROM Users WHERE LogonName = ?")  

      sql.SQLBindInputParameter(stmt, 1, sql.SQL_VARCHAR, "bob")
      sql.SQLExecute(stmt)
      sql.SQLFetch(stmt)
      userId, logonName = sql.SQLGetInt(stmt, 1), sql.SQLGetString(stmt, 2, 0)
      sql.SQLFreeStmt(stmt, sql.SQL_CLOSE)
      self.assertEqual((userId, logonName), (564, 'bob'))

      sql.SQLBindInputParameter(stmt, 1, sql.SQL_VARCHAR, "trixie")
      sql.SQLExecute(stmt)
      sql.SQLFetch(stmt)
      userId, logonName = sql.SQLGetInt(stmt, 1), sql.SQLGetString(stmt, 2, 0)
      sql.SQLFreeStmt(stmt, sql.SQL_CLOSE)
      self.assertEqual((userId, logonName), (565, 'TRIXIE'))

      del stmt
  
  def testDataSources(self):

      status, name, desc = sql.SQLDataSources(sql.SQL_FETCH_FIRST)
      while status != sql.SQL_NO_DATA_FOUND:
        status, name, desc = sql.SQLDataSources(sql.SQL_FETCH_NEXT)


  def testCrash(self):
      # this routine was crashing because the string was too long
      stmt = self.c()
      results = sql.SQLPrepare(stmt, """SELECT blobfieldid, bloborder, blobvalue
                  FROM BlobField
                  WHERE (blobfieldid=1764)
                  ORDER BY BlobFieldID, BlobOrder""")
      results = sql.SQLExecute(stmt)
      results = sql.SQLFetch(stmt)
      while results == sql.SQL_SUCCESS:
        sql.SQLGetString(stmt, 3, False)
        results = sql.SQLFetch(stmt); 

  def testBadStatement(self):

      with self.assertRaises(sql.error) as context:
          stmt = self.c()
          results = sql.SQLPrepare(stmt, "SELECT XUserId, LogonName FROM Users")
          results = sql.SQLExecute(stmt)

      self.assertEqual(('S0022', 207, "[Microsoft][SQL Server Native Client 10.0][SQL Server]Invalid column name 'XUserId'."), 
              context.exception.args)

  def testColumnTypes(self):
      sql_ddml   = """
CREATE TABLE [zzodbctest](
    [myint] [int] NOT NULL,
    [mybigint] [bigint] NULL,
    [mybinary] [binary](50) NULL,
    [mybit] [bit] NULL,
    [mychar] [char](10) NULL,
    [mydate] [date] NULL,
    [mydatetime] [datetime] NULL,
    [mydatetime2] [datetime2](7) NULL,
    [mydatetimeoffset] [datetimeoffset](7) NULL,
    [mydecimal] [decimal](18, 0) NULL,
    [myfloat] [float] NULL,
    [mygeography] [geography] NULL,
    [myhierarchyid] [hierarchyid] NULL,
    [myimage] [image] NULL,
    [mymoney] [money] NULL,
    [mynchar] [nchar](10) NULL,
    [mynumeric] [numeric](18, 0) NULL,
    [myntext] [ntext] NULL,
    [mynvarchar] [nvarchar](50) NULL,
    [myreal] [real] NULL,
    [mysmalldatetime] [smalldatetime] NULL,
    [mysmallint] [smallint] NULL,
    [mysmallmoney] [smallmoney] NULL,
    [mysql_variant] [sql_variant] NULL,
    [mytext] [text] NULL,
    [mytimestamp] [timestamp] NULL,
    [mytinyint] [tinyint] NULL,
    [myuniqueidentifier] [uniqueidentifier] NULL,
    [myvarbinary] [varbinary](50) NULL,
    [myvarchar] [varchar](50) NULL,
    [myxml] [xml] NULL,
 CONSTRAINT [PK_zzodbctest] PRIMARY KEY CLUSTERED 
(
            [myint] ASC
            )
) 

      """
      SQL_TYPE_DATETIMEOFFSET = -155
      SQL_TYPE_XML = -152
      SQL_TYPE_GEO = -151
      SQL_TYPE_VT  = -150

      sql_select = "SELECT TOP 5 * FROM zzodbctest"
      SQLGetColumn={sql.SQL_CHAR   : sql.SQLGetString,                                     # 1
                    sql.SQL_NUMERIC: lambda stmt, col, binary: sql.SQLGetFloat(stmt, col), # 2
                    sql.SQL_DECIMAL: lambda stmt, col, binary: sql.SQLGetFloat(stmt, col), # 3
                    sql.SQL_INTEGER: lambda stmt, col, binary: sql.SQLGetInt(stmt, col),   # 4
                    sql.SQL_SMALLINT:lambda stmt, col, binary: sql.SQLGetInt(stmt, col),   # 5
                    sql.SQL_FLOAT:   lambda stmt, col, binary: sql.SQLGetFloat(stmt, col), # 6
                    sql.SQL_REAL:    lambda stmt, col, binary: sql.SQLGetFloat(stmt, col), # 7
                    sql.SQL_DOUBLE:  lambda stmt, col, binary: sql.SQLGetFloat(stmt, col), # 8
                    sql.SQL_WVARCHAR: sql.SQLGetString,
                    sql.SQL_VARCHAR       : sql.SQLGetString,

                    # extended data types
                    sql.SQL_DATE          : lambda stmt, col, binary: sql.SQLGetDateTime(stmt, col),
                    sql.SQL_TIME          : lambda stmt, col, binary: sql.SQLGetDateTime(stmt, col),
                    sql.SQL_TIMESTAMP     : lambda stmt, col, binary: sql.SQLGetDateTime(stmt, col),
                    sql.SQL_TIMESTAMP     : lambda stmt, col, binary: sql.SQLGetDateTime(stmt, col),
                    #sql.SQL_SS_TIMESTAMPOFFSET : lambda stmt, col, binary: sql.SQLGetDateTime(stmt, col), #-155 (SQLNCLI.h)
                    sql.SQL_LONGVARCHAR   : sql.SQLGetString,
                    sql.SQL_WCHAR         : sql.SQLGetString,  # -8
                    sql.SQL_WLONGVARCHAR  : sql.SQLGetString,  # -10
                    sql.SQL_GUID          : sql.SQLGetString,  # -11
                    sql.SQL_BINARY        : sql.SQLGetString,
                    sql.SQL_VARBINARY     : sql.SQLGetString,
                    sql.SQL_LONGVARBINARY : sql.SQLGetString,
                    sql.SQL_BIGINT        : lambda stmt, col, binary: sql.SQLGetLong(stmt, col),
                    sql.SQL_TINYINT       : lambda stmt, col, binary: sql.SQLGetInt(stmt, col),
                    sql.SQL_BIT           : lambda stmt, col, binary: sql.SQLGetBool(stmt, col),

                    SQL_TYPE_DATETIMEOFFSET : None,
                    SQL_TYPE_XML            : None,
                    SQL_TYPE_GEO            : None,
                    SQL_TYPE_VT             : None,

                    }

      stmt = self.c()
      results = sql.SQLPrepare(stmt, sql_select)
      results = sql.SQLExecute(stmt)

      # get number of columns
      status, ncol = sql.SQLNumResultCols(stmt)

      for rowindex in range(2):
          sql.SQLFetch(stmt)
          for i in range(ncol):
              # ODBC column numbers are 1-based
              status, name, tp, prec, scale, nullable=sql.SQLDescribeCol(stmt,i+1)

              func = SQLGetColumn.get(tp, sql)
              if func == sql:
                  print i+1, sql.SQLDescribeCol(stmt, i+1)
                  continue
              if func == None:
                  continue

              result = func(stmt, i+1, False)
              if result is None:
                  continue

              if name == 'mydate':
                  self.assertIsInstance(result, datetime.datetime)
              elif name == 'mydatetime':
                  self.assertIsInstance(result, datetime.datetime)
              elif name == 'mydatetime2':
                  self.assertIsInstance(result, datetime.datetime)
              elif name == 'mydatetimeoffset':
                  self.assertIsInstance(result, datetime.datetime)
              elif name == 'mysmalldatetime':
                  self.assertIsInstance(result, datetime.datetime)
              elif name == 'myint':
                  self.assertEqual(tp, sql.SQL_INTEGER)
              else:
                  pass #print "Fetch", name, `func(stmt, i+1, False)`

      sql.SQLFreeStmt(stmt, sql.SQL_CLOSE)

  def testGetDateTime(self):
        stmt = self.c()
        sql.SQLPrepare(stmt, "SELECT TOP 1 ExpectedDuration FROM I1L1 WHERE ExpectedDuration Is Null")
        sql.SQLExecute(stmt)
        sql.SQLFetch(stmt)
        self.assertIsNone(sql.SQLGetDateTime(stmt, 1))

#raw_input("Hit enter to start")      
unittest.main()

