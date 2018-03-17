from peewee import *
from SpiderMan.model.pymysqlpool.connection import MySQLConnectionPool


class MyConnectionPool(MySQLConnectionPool):
    pass


from peewee import (
    RESULTS_NAIVE,
    NaiveQueryResultWrapper, RESULTS_MODELS,
    ModelQueryResultWrapper, RESULTS_TUPLES,
    _TuplesQueryResultWrapper, TuplesQueryResultWrapper,
    _DictQueryResultWrapper, RESULTS_DICTS, DictQueryResultWrapper,
    RESULTS_AGGREGATE_MODELS, AggregateQueryResultWrapper
)


class MyNaiveQueryResultWrapper(NaiveQueryResultWrapper):
    def process_row(self, row):
        instance = self.model()
        for i, column, f in self.conv:
            setattr(instance, column, f(row[i]) if f is not None else row[i])
        instance._prepare_instance()

        return instance


class My_ModelQueryResultWrapper(MyNaiveQueryResultWrapper):
    pass


class database(MySQLDatabase):
    def _connect(self, database, **kwargs):
        kwargs["database"] = database
        kwargs["use_dict_cursor"] = False
        return MyConnectionPool(**kwargs)

    def execute_sql(self, sql, params=None, require_commit=True):

        with self.exception_wrapper:
            with self.get_conn().cursor() as cursor:
                try:
                    cursor.execute(sql, params or ())
                except Exception:
                    if self.autorollback and self.get_autocommit():
                        self.rollback()
                    raise
                else:
                    if require_commit and self.get_autocommit():
                        self.commit()
        return cursor

    def get_result_wrapper(self, wrapper_type):
        if wrapper_type == RESULTS_NAIVE:
            return (My_ModelQueryResultWrapper if self.use_speedups
                    else MyNaiveQueryResultWrapper)
        elif wrapper_type == RESULTS_MODELS:
            return ModelQueryResultWrapper
        elif wrapper_type == RESULTS_TUPLES:
            return (_TuplesQueryResultWrapper if self.use_speedups
                    else TuplesQueryResultWrapper)
        elif wrapper_type == RESULTS_DICTS:
            return (_DictQueryResultWrapper if self.use_speedups
                    else DictQueryResultWrapper)
        elif wrapper_type == RESULTS_AGGREGATE_MODELS:
            return AggregateQueryResultWrapper
        else:
            return (My_ModelQueryResultWrapper if self.use_speedups
                    else MyNaiveQueryResultWrapper)

    def commit(self):
        pass
