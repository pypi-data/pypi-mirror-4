__author__ = 'bdeggleston'
from rexpro import RexProConnection

from contextlib import contextmanager
import json
from time import time
import requests

iterations = 1000
graphname = 'emptygraph'

@contextmanager
def timer(name=''):
    start = time()
    yield
    end = time()
    print name, 'took', (end-start), 'seconds'

conn = RexProConnection('localhost', 8184, graphname)

script = """
def v1 = g.addVertex([param1:p1, param2:p2])
def v2 = g.addVertex([param3:p3, param4:p4])
def e1 = g.addEdge(v1, v2, 'connects', [param5:p5])
"""

with timer('rexpro'):
    with conn.transaction():
        for i in range(iterations):
            params = {'p{}'.format(n+1):n*5 for n in range(5)}
            conn.execute(script, params=params)



with timer('rexster'):
    for i in range(iterations):
        params = {'p{}'.format(n+1):n*5 for n in range(5)}

        #add the transactional stuff
        query = '\n'.join([
            'g.stopTransaction(FAILURE)',
            script,
            'g.stopTransaction(SUCCESS)',
        ])

        data = json.dumps({'script':query, 'params': params})
        headers = {'Content-Type':'application/json', 'Accept':'application/json'}
        response = requests.post('http://localhost:8182/graphs/{}/tp/gremlin'.format(graphname), data, headers=headers)
