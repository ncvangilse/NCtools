# -*- coding: utf-8 -*-
"""
Created on Mon Nov 07 14:32:41 2016

@author: fbx182
"""

import re
import fdb
import os


class Fdb_connection(object):

    def __init__(self, fnam, create=False):
        """Return a jupiter object with file connection to *fnam*
        it assumes that any string that goes into the connection is utf8 formatted"""
        self.fnam = fnam
        if os.path.exists(fnam):
            self.con = fdb.connect(dsn=fnam, user='sysdba',
                                   password='masterkey', charset='utf8')
        else:
            if create:
                if os.path.exists(fnam):
                    raise('File: {} already exists!'.format(fnam))
                print ('Creating database: {}'.format(fnam))
                self.con = fdb.create_database("create database '{}' user 'sysdba' password 'masterkey'".format(fnam))
            else:
                raise('File: {} doent exist!'.format(fnam))
        self.cur = self.con.cursor()

    def list_to_str(self, lst):
        return '(' + ', '.join(["'" + x + "'" for x in lst]) + ')'

    def run(self, statement):
        """ Send a statement the the firebird server.
        If  'CREATE TABLE' or 'CREATE VIEW' is found inside the statement, it will check if exists,
        and drop it if it exists'
        Note: It will decode the string to be utf8 encoded (and thus compliant with the reqirement for the connection)"""
        print(statement)
        p = re.compile('CREATE\s+(TABLE|VIEW)\s+(\S+)')
        m = p.search(statement.upper())
        if m:
            name = m.group(2)
            x = m.group(1)
            if x == 'TABLE':
                self.drop_table(name, cut_constraints=True)
            elif x == 'VIEW':
                self.drop_view(name)
#            self.cur.execute("SELECT rdb$relation_name FROM rdb$relations WHERE rdb$relation_name = '{}'".format(name))
#            if self.cur.fetchall():
#                print 'Dropping {} {}'.format(m.group(1), name)
#                self.cur.execute('DROP {} {}'.format(m.group(1), name))
#                self.commit()
        p = re.compile('ALTER TABLE\s+(\S+)\s+ADD\s+(\S+)')
        m = p.search(statement.upper())
        if m:
            field = m.group(2)
            table = m.group(1)
            self.cur.execute(
                "SELECT rdb$field_name FROM rdb$relation_fields WHERE rdb$relation_name = '{}' and rdb$field_name = '{}'".format(table, field))
            if self.cur.fetchall():
                print('Dropping {} {}'.format(table, field))
                self.cur.execute('ALTER TABLE {} DROP {}'.format(table, field))
                self.commit()

        self.cur.execute(statement)
        self.commit()

    def drop_view(self, view):
        view = view.upper()
        if view in self.get_view_names():
            print('Dropping {}'.format(view))
            self.run('DROP VIEW {}'.format(view))

    def drop_table(self, table, cut_constraints=False):
        table = table.upper()
        if table in self.get_table_names():
            if cut_constraints:
                self.cut_constraints(table)
            print('Dropping {} '.format(table))
            self.run('DROP TABLE {}'.format(table))

    def get_table_count(self, tablename=None):
        if not tablename:
            tablename = self.get_table_names()
        out = []
        N = len(tablename)
        i = 0
        for tn in tablename:
            i += 1
            print('Counting rows in table ({} / {}) {}'.format(i, N, tn))
            self.cur.execute("select COUNT(*) from {}".format(tn))
            cnt = self.fetch_to_arr(self.cur.fetchall())
            out += [[tn, cnt]]
        return out

    def get_constraints(self, table, cType=None):
        table = table.upper()
        if not cType:
            self.cur.execute(
                'select a.RDB$CONSTRAINT_NAME '
                'FROM RDB$RELATION_CONSTRAINTS a '
                "where a.RDB$RELATION_NAME='{}'".format(table)
            )
        else:
            cType = cType.upper()
            self.cur.execute(
                'select a.RDB$CONSTRAINT_NAME '
                'FROM RDB$RELATION_CONSTRAINTS a '
                "where a.RDB$CONSTRAINT_TYPE = '{}' and a.RDB$RELATION_NAME='{}'".format(
                    cType, table)
            )
        dat = self.cur.fetchall()
        return self.fetch_to_arr(dat)

    def fetch_to_arr(self, dat):
        out = []
        for lst in dat:
            lstout = []
            if len(lst) > 1:
                for t in lst:
                    if isinstance(t, str):
                        lstout += [t.strip()]
                    else:
                        lstout += [t]
                out += [lstout]
            else:
                if isinstance(lst[0], str):
                    out += [lst[0].strip()]
                else:
                    out += [lst[0]]
        return out

    def get_field_names(self, table):
        if table not in self.get_table_names():
            print('Table: {}  does not exist!')
        self.cur.execute(
            'select rdb$field_name from rdb$relation_fields '
            "where rdb$relation_name='{}'".format(table))
        dat = self.cur.fetchall()
        return self.fetch_to_arr(dat)

    def get_view_names(self):
        self.cur.execute('select rdb$relation_name '
                         'from rdb$relations '
                         'where rdb$view_blr is not null '
                         'and (rdb$system_flag is null or rdb$system_flag = 0) ')
        dat = self.cur.fetchall()
        return self.fetch_to_arr(dat)

    def get_table_names(self):
        self.cur.execute(
            'select rdb$relation_name '
            'from rdb$relations '
            'where rdb$view_blr is null '
            'and (rdb$system_flag is null or rdb$system_flag = 0) '
        )
        dat = self.cur.fetchall()
        return self.fetch_to_arr(dat)


    def cut_constraints(self, table):
        """
        Detect if any of the primary keys in the table acts as a foreign key in
        another table. If it does, drop the foreign key constraint in the other table

        """
        #Get the Primary keys for this table
        PKs = self.get_constraints(table, 'PRIMARY KEY')
        for PK in PKs:
            #Search to see if the PK is used as a constraint elsewhere and get the constraint name
            self.cur.execute(
                'SELECT a.RDB$CONSTRAINT_NAME '
                'FROM RDB$REF_CONSTRAINTS a '
                "where a.RDB$CONST_NAME_UQ = '{}'".format(PK)
            )
            cNames = self.fetch_to_arr(self.cur.fetchall())
            #From the constraint name(s) find which tables they come from
            if cNames:
                self.cur.execute(
                    'SELECT a.RDB$CONSTRAINT_NAME, a.RDB$RELATION_NAME '
                    'FROM RDB$RELATION_CONSTRAINTS a '
                    'where a.RDB$CONSTRAINT_NAME in {}'.format(self.list_to_str(cNames))
                )
                constraints = self.fetch_to_arr(self.cur.fetchall())
                #Cut all detected constraints
                for cName, tbl in constraints:
                    # print 'Cutting constraint in {}'.format(tbl)
                    self.run('ALTER TABLE {} DROP CONSTRAINT {}'.format(tbl, cName))

    def insertDct(self, target, dct):
        prepstr = 'insert into {} ({}) values ({})'.format(target, ', '.join(dct.keys()), ','.join(['?']*len(dct.keys())))
        values = [v for v in dct.values()]
        insertStatement = self.cur.prep(prepstr)
        self.cur.execute(insertStatement, values)
        self.commit()

    def insertArray(self, target, dct):
        prepstr = 'insert into {} ({}) values ({})'.format(target, ', '.join(dct.keys()), ','.join(['?']*len(dct.keys())))
        values = [x for x in zip(*dct.values())]
        insertStatement = self.cur.prep(prepstr)
        self.cur.executemany(insertStatement, values)
        self.commit()
                    
                    
    def exefetch(self, statement):
        self.cur.execute(statement)
        return self.fetch_to_arr(self.cur.fetchall())

    def commit(self):
        self.con.commit()

    def close(self):
        self.con.close()
