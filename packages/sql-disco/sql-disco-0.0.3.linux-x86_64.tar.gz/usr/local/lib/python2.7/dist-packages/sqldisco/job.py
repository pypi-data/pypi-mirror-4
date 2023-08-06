'''
File: job.py
Author: Jon Eisen
Description: sql-disco Job Wrapper

'''
from disco.job import Job
from sqldb_io import sql_input_stream, sql_packages
from splitter import calculate_splits
import logging

class SqlJob(Job):

    def run(self, **jobargs):
        """
        Run a map-reduce job with SQL data
        
        Args = {
          sqltype: 'mssql' ## one of ('sqlite3', 'mysql', 'pg', 'mssql')
          connargs: {'some_conn_parameter':'some_conn_value'} ## passed to connect(**kwargs)
          query: "SELECT * FROM my_table"
          input_key: "id"
          split: False ## True is not implemented
        }
        """

        if jobargs.get('sqltype', '') not in sql_packages.keys():
            msg = 'You must specify a valid sqltype from %r' % list(sql_packages.keys())
            logging.info(msg)
            raise Exception(msg)
        elif type(jobargs.get('connargs', None)) is not dict:
            msg = 'Parameter connargs must be a dictionary (passed to connect(**kwargs))'
            logging.info(msg)
            raise Exception(msg)

        if type(jobargs.get('params', {})) is not dict:
            msg = 'You must have params as a dict object'
            logging.info(msg)
            raise Exception(msg)

        params = jobargs.get('params', {})

        if 'SELECT' in jobargs.get('query', ''):
            jobargs['map_input_stream'] = sql_input_stream
            jobargs['input'] = calculate_splits(jobargs)


        # TODO Output
            
        jobargs.setdefault('required_modules', []).extend([
            'sqldisco.sqldb_io'
        ])

        jobargs['params'] = params


        super(SqlJob, self).run(**jobargs)
        return self

