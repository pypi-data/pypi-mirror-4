from traceback import print_exc

from django.db import connection


def start_profiling():
    connection.queries = []


def stop_profiling():
    return connection.queries


def print_queries(queries):
    num = len(queries)
    if num == 0:
        print('NO queries performed.')
    elif num == 1:
        print('ONE query:')
        print('%s; (%s secs)' % (queries[0]['sql'], queries[0]['time']))
    else:
        print('%s queries:' % num)
        for query in queries:
            print('%s; (%s secs)' % (query['sql'], query['time']))


def profile(func, args=[], kwargs={}):
    start_profiling()

    try:
        response = func(*args, **kwargs)
        return response
    except:
        print_exc()
    finally:
        queries = stop_profiling()
        print_queries(queries)
