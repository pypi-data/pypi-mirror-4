'''
File: sql_io.py
Author: Jon Eisen
Description: Input and output routines for sql-disco
'''

# Package mappings to DB-API 2.0 compliant dbs
sql_packages = {
    'mssql': 'pymssql'
}

def _import(sqltype):
	''' Import the sql package in question '''
	return __import__(sql_packages[sqltype]) ## Allow the throw condition to notify the user of errors

def _input(query, sqltype, connargs, **kwargs):
	package = _import(sqltype)
	conn = package.connect(**connargs)
	cursor = conn.cursor()

	cursor.execute(query)
	return InputWrapper(cursor)

class InputWrapper(object):
    """Want to wrap the cursor in an object that
    supports the following operations: """

    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        # Try to use DB-API iteration extension
        if hasattr(self.cursor, '__iter__'):
        	return self.cursor.__iter__()
        else:
            return self.cursor_iter()

    def cursor_iter(self):
    	row = self.cursor.fetchone()
    	while row:
    		yield row
    		row = self.cursor.fetchone()

    def __len__(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()

    def read(self, size=-1):
        #raise a non-implemented error to see if this ever pops up
        raise Exception("read is not implemented- investigate why this was called")

def sql_input(stream, size, url, params):
    # This looks like a mistake, but it is intentional.
    # Due to the way that Disco imports and uses this
    # function, we must re-import the module here.
    from sqldisco.sqldb_io import _input
    import json
    return _input(**json.loads(url)) # url contains our splitter parameters

sql_input_stream = (sql_input,)