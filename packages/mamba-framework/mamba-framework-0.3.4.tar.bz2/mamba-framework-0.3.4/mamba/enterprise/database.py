# -*- test-case-name: mamba.test.test_database -*-
# Copyright (c) 2012 Oscar Campos <oscar.campos@member.fsf.org>
# See LICENSE for more details

"""
.. module:: database
    :platform: Unix, Windows
    :synopsis: Storm ORM Database implementation for Mamba

.. moduleauthor:: Oscar Campos <oscar.campos@member.fsf.org>

"""

import datetime

from storm import properties
from storm.store import Store
from storm.expr import Undef, Column
from storm.zope.interfaces import IZStorm
from storm.zope.zstorm import global_zstorm
from storm.database import URI, create_database
from twisted.python.monkey import MonkeyPatcher
from twisted.python.threadpool import ThreadPool
from zope.component import provideUtility, getUtility

from mamba import version
from mamba.utils import config
from mamba.enterprise.mysql import MySQL
from mamba.enterprise.sqlite import SQLite
from mamba.enterprise.common import CommonSQL
from mamba.enterprise.postgres import PostgreSQL


class Database(object):
    """
    Storm ORM database provider for Mamba.

    :param pool: the thrad pool for this database
    :type pool: :class:`twisted.python.threadpool.ThreadPool`
    """

    monkey_patched = False
    pool = ThreadPool(
        config.Database().min_threads,
        config.Database().max_threads,
        'DatabasePool'
    )

    def __init__(self, pool=None, testing=False):
        if pool is not None:
            self.pool = pool

        self.started = False
        self.__testing = testing

        # we only use ZStorm zope container in tests because has been
        # impossible for us to make ZStorm working nice with daemonized
        # twisted ThreadPools
        if self.__testing is True:
            provideUtility(global_zstorm, IZStorm)
            self.zstorm = getUtility(IZStorm)
            self.zstorm.set_default_uri('mamba', config.Database().uri)
        else:
            self._database = None

        # register components
        SQLite.register()
        MySQL.register()
        PostgreSQL.register()

        # MonkeyPatch Storm
        if not self.monkey_patched:
            monkey_patcher = MonkeyPatcher(
                (properties, 'PropertyColumn', PropertyColumnMambaPatch)
            )
            monkey_patcher.patch()
            self.monkey_patched = True

    def start(self):
        """Starts the Database (and the threadpool)
        """

        if self.started:
            return

        if self.__testing is True:
            self.pool.start()
        else:
            self._database = create_database(config.Database().uri)

        self.started = True

    def stop(self):
        """Stops the Database (and the threadpool)
        """

        if not self.started:
            return

        self.started = False

    def adjust_poolsize(self, min_threads=None, max_threads=None):
        """
        Adjusts the underlying threadpool size

        :param min: minimum number of threads
        :type min: int
        :param max: maximum number of threads
        :type max: int
        """

        self.pool.adjustPoolsize(min_threads, max_threads)

    def store(self):
        """
        Returns a Store per-thread through :class:`storm.zope.zstorm.ZStorm`
        """

        if not self.started:
            self.start()

        if self.__testing is True:
            return self.zstorm.get('mamba')

        return Store(self._database)

    def dump(self, model_manager, full=False):
        """
        Dumps the full database

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        :param full: should be dumped full?
        :type full: bool
        """

        references = []
        sql = [
            '--',
            '-- Mamba SQL dump {}'.format(version.short()),
            '--',
            '-- Database Backend: {}'.format(self.backend),
            '-- Host: {}\tDatabase: {}'.format(self.host, self.database)
        ]
        app = config.Application('config/application.json')
        try:
            sql += [
                '-- Application: {}'.format(app.name.decode('utf-8')),
                '-- Application Version: {}'.format(app.version),
                '-- Application Description: {}'.format(
                    app.description.encode('utf-8')
                )
            ]
        except AttributeError:
            pass

        sql += [
            '-- ---------------------------------------------------------',
            '-- Dumped on: {}'.format(datetime.datetime.now().isoformat()),
            '--'
        ]

        if self.backend == 'mysql':
            sql += [
                '-- Disable foreign key checks for table creation',
                '--',
                'SET FOREIGN_KEY_CHECKS = 0;'
            ]

        if full is False:
            sql.append('')
            for model in model_manager.get_models().values():
                if self.backend == 'postgres':
                    references.append(model.get('object').dump_references())

                sql += [model.get('object').dump_table() + '\n']
        else:
            for model in model_manager.get_models().values():
                model_object = model.get('object')
                sql.append('--')
                sql.append('-- Table structure for table {}'.format(
                    model_object.__storm_table__
                ))
                sql.append('--\n')
                sql.append(model_object.dump_table())
                sql.append('--')
                sql.append('-- Dumping data for table {}'.format(
                    model_object.__storm_table__
                ))
                sql.append('--\n')
                sql.append(model_object.dump_data())

                if self.backend == 'postgres':
                    references.append(model_object.dump_references())

        if self.backend == 'mysql':
            sql += [
                '--',
                '-- Enable foreign key checks',
                '--',
                'SET FOREIGN_KEY_CHECKS = 1;'
            ]

        for reference in references:
            sql.append(reference)

        return '\n'.join(sql)

    def reset(self, model_manager):
        """
        Delete all the data in the database and return it to primitive state

        :param model_manager: the model manager from mamba application
        :type model_manager: :class:`~mamba.application.model.ModelManager`
        """

        cfg = config.Database()
        cfg.create_table_behaviours['create_table_if_not_exists'] = False
        cfg.create_table_behaviours['drop_table'] = True

        sql = [
            model.get('object').dump_table()
            for model in model_manager.get_models().values()
        ]

        return '\n'.join(sql)

    @property
    def backend(self):
        """Return the type of backend this databse is using
        """

        return URI(config.Database().uri).scheme

    @property
    def host(self):
        """Return the hostname this database is using
        """

        return URI(config.Database().uri).host

    @property
    def database(self):
        """Return the database name we are using
        """

        return URI(config.Database().uri).database


class AdapterFactory(object):
    """
    This is a factory which produces SQL Adapters.

    :param scheme: the database scheme (one of PostgreSQL, MySQL, SQLite)
    :type scheme: str
    :param model: the model to use with this adapter
    :type model: :class:`~mamba.Model`
    """

    def __init__(self, scheme, model):
        self.scheme = scheme
        self.model = model

    def produce(self):
        if self.scheme == 'sqlite':
            return SQLite(self.model)
        elif self.scheme == 'mysql':
            return MySQL(self.model)
        elif self.scheme == 'postgres':
            return PostgreSQL(self.model)
        else:
            return CommonSQL(self.model)


# Monkey Patching Storm (only a bit)
class PropertyColumnMambaPatch(Column):
    """
    We need to monkey patch part of Storm to can use size, unsigned
    and auto_increment named values in Properties.

    I'am supossed to work well with Storm since rev 223 (v0.12)
    """
    def __init__(self, prop, cls, attr, name, primary,
                 variable_class, variable_kwargs):
        # here we go!
        self.size = variable_kwargs.pop('size', Undef)
        self.unsigned = variable_kwargs.pop('unsigned', False)
        self.auto_increment = variable_kwargs.pop('auto_increment', False)
        self.array = variable_kwargs.pop('array', None)

        Column.__init__(self, name, cls, primary,
                        properties.VariableFactory(
                            variable_class, column=self,
                            validator_attribute=attr,
                            **variable_kwargs)
                        )

        self.cls = cls  # Used by references

        # Copy attributes from the property to avoid one additional
        # function call on each access.
        for attr in ["__get__", "__set__", "__delete__"]:
            setattr(self, attr, getattr(prop, attr))


__all__ = ['Database', 'AdapterFactory']
