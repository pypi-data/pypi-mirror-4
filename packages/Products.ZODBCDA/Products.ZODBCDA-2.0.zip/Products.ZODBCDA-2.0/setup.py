#from setuptools import setup, find_packages
from distutils.core import setup, Extension

setup(
        name = "Products.ZODBCDA",
        version = "2.0",

        packages = ["Products", "Products.ZODBCDA"],
        namespace_packages = ["Products"],

        package_dir = {'Products'        : 'Products',
                       'Products.ZODBCDA': 'Products/ZODBCDA',
                      },

        package_data = { 
            'Products.ZODBCDA': ['*.dtml', 'icons/*'],
        },

        scripts = [],
        ext_modules = [Extension('_sql',sources=['src/sql_wrap.c', ], libraries=["odbc32"], 
                                        depends=["src/pysql.c", "src/sql.i", "src/sqlext.h"],
                                        extra_compile_args=["/Z7"],
                                        #extra_compile_args=["/Zi", "/Fd_sql.pdb"],                                        
                                        )],

        # Project uses Shared.DC.ZRDB
        requires = ['Products.ZSQLMethods'],


        # metadata for upload to PyPI
        author = "Zope Corp",
        author_email = "",
        maintainer = "Chui Tey",
        maintainer_email = "teyc@cognoware.com",
        description  = "ODBC database adapter for Zope",
        license = "ZPL",
        keywords = "ODBC Zope",
        url = "http://packages.python.org/Products.ZODBCDA",
        
        # url = "",

)
