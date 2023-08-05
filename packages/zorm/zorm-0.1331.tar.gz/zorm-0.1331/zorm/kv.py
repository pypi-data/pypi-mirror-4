#!/usr/bin/env python
# -*- coding: utf-8 -*-
from array import array
from hashlib import md5
from zorm.config import db_by_table, mc
from zorm.model import _key_by_table

class Kv(object):
    def __init__(self, table, NULL=''):
        self.__table__ = table
        db = db_by_table(table)
        self.cursor = cursor = db.cursor()
        mc_key = _key_by_table(db, table, cursor) 
        self.__mc_id__ = "%s'+%%s"%mc_key
        self.NULL = NULL


    def get(self, id):
        mc_key = self.__mc_id__ % id
        r = mc.get(mc_key)
        if r is None:
            cursor = self.cursor
            cursor.execute('select value from %s where id=%%s' % self.__table__, id)
            r = cursor.fetchone()
            if r:
                r = r[0]
            if r is None:
                r = self.NULL
            mc.set(mc_key, r)
        return r

    def get_dict(self, id_list):
        if type(id_list) not in (array, list, tuple, dict):
            id_list = tuple(id_list)
        mc_key = self.__mc_id__
        result = mc.get_dict([mc_key%i for i in id_list])
        r = {}
        for i in id_list:
            t = result.get(mc_key%i)
            if t is None:
                t = self.get(i)
            r[i] = t
        return r

    def get_list(self, id_list):
        if type(id_list) not in (array, list, tuple, dict):
            id_list = tuple(id_list)
        mc_key = self.__mc_id__
        result = mc.get_dict([mc_key%i for i in id_list])
        r = []
        for i in id_list:
            t = result.get(mc_key%i)
            if t is None:
                t = self.get(i)
            r.append(t)
        return r

    def bind(self, li, property, key='id'):
        for i, value in zip(li, self.get_list(getattr(i,key) for i in li)):
            i.__dict__[property] = value

    def iteritems(self):
        id = 0
        cursor = self.cursor
        while True:
            cursor.execute('select id,value from %s where id>%%s order by id limit 128' % self.__table__, id)
            result = cursor.fetchall()
            if not result:
                break
            for id, value in result:
                yield id, value


    def set(self, id, value):
        r = self.get(id)
        if r != value:
            table = self.__table__
            cursor = self.cursor
            cursor.execute(
                'insert into %s (id,value) values (%%s,%%s) on duplicate key update value=%%s' % table,
                (id, value, value)
            )
            cursor.connection.commit()
            if value is None:
                value = False
            mc_key = self.__mc_id__ % id
            mc.set(mc_key, value)

    def mc_flush(self, id):
        mc_key = self.__mc_id__ % id
        mc.delete(mc_key)

    def delete(self, id):
        cursor = self.cursor
        cursor.execute('delete from %s where id=%%s' % self.__table__, id)
        mc_key = self.__mc_id__ % id
        mc.delete(mc_key)

    def id_by_value(self, value):
        cursor = self.cursor
        cursor.execute(
            'select id from %s where value=%%s' % self.__table__,
            value
        )
        r = cursor.fetchone()
        if r:
            r = r[0]
        else:
            r = 0
        return r

