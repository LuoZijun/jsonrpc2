# -*- coding:utf-8 -*-
from __future__ import unicode_literals
import json
from webtest import TestApp
from jsonrpc2 import JsonRpc
from jsonrpc2 import JsonRpcApplication
from webob import exc

def subtract(minuend, subtrahend):
    return minuend - subtrahend

def greeting(name):
    return "Hello, %s!" % name

def update(*args):
    pass

def notify_hello(*args):
    pass

def get_data(*args):
    return ["hello", 5]

def raise_exception():
    raise Exception()

class TestingException(Exception):
    pass

def raise_testing_exception():
    raise TestingException()

def createapp():
    app = JsonRpcApplication(
        dict(subtract=subtract,
             update=update,
             notify_hello=notify_hello,
             get_data=get_data,
             raise_exception=raise_exception,
             raise_testing_exception=raise_testing_exception),
        application_errors={
            TestingException: -32001
        })
    app = TestApp(app)
    return app


app = createapp()

"""
rpc call with positional parameters:
"""

def test_mimetype_with_charset():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
    <-- {"jsonrpc": "2.0", "result": 19, "id": 1}
    """
    data = {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
    
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json-rpc;charset=utf-8'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == 19
    assert data['id'] == 1

def test_positional_params1():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
    <-- {"jsonrpc": "2.0", "result": 19, "id": 1}
    """
    data = {"jsonrpc": "2.0", "method": "subtract", "params": [42, 23], "id": 1}
    
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == 19
    assert data['id'] == 1

def test_positional_params2():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}
    
    <-- {"jsonrpc": "2.0", "result": -19, "id": 2}
    """
    data = {"jsonrpc": "2.0", "method": "subtract", "params": [23, 42], "id": 2}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == -19
    assert data['id'] == 2


"""
rpc call with named parameters:
"""
def test_named_params1():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
    <-- {"jsonrpc": "2.0", "result": 19, "id": 3}
    """
    data = {"jsonrpc": "2.0", "method": "subtract", "params": {"subtrahend": 23, "minuend": 42}, "id": 3}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == 19
    assert data['id'] == 3


def test_named_params2():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}
    
    <-- {"jsonrpc": "2.0", "result": 19, "id": 4}
    """
    data = {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == 19
    assert data['id'] == 4

def test_unicode_params():
    """
    --> {"jsonrpc": "2.0", "method": "subtract", "params": {"minuend": 42, "subtrahend": 23}, "id": 4}
    
    <-- {"jsonrpc": "2.0", "result": 19, "id": 4}
    """
    app = JsonRpcApplication(dict(greeting=greeting))
    app = TestApp(app)
    data = {"jsonrpc": "2.0", "method": "greeting", "params": {"name":"あ"}, "id": 4}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    data = res.json
    assert data['jsonrpc'] == '2.0'
    assert data['result'] == "Hello, あ!"
    assert data['id'] == 4

def test_notification():
    """
    a Notification:
    
    --> {"jsonrpc": "2.0", "method": "update", "params": [1,2,3,4,5]}
    """
    data = {"jsonrpc": "2.0", "method": "update", "params": [1, 2, 3, 4, 5]}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200

    assert len(res.body) == 0


def test_non_existent():
    """
    rpc call of non-existent method:
    
    --> {"jsonrpc": "2.0", "method": "foobar", "id": "1"}
    <-- {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Procedure not found."}, "id": "1"}
    """
    data = {"jsonrpc": "2.0", "method": "foobar", "id":"1"}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['error']['code'] == -32601


def test_generic_application_error():
    data = {"jsonrpc": "2.0", "method": "raise_exception", "id":"1"}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['error']['code'] == -32000

def test_application_error():
    data = {"jsonrpc": "2.0", "method": "raise_testing_exception", "id":"1"}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['error']['code'] == -32001


def test_invalid_json():
    """
    rpc call with invalid JSON:
    
    --> {"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]
    <-- {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error."}, "id": null}
    """

    res = app.post('/', params='{"jsonrpc": "2.0", "method": "foobar, "params": "bar", "baz]',
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['id'] is None
    assert d['error']['code'] == -32700

def test_invalid_request_object():
    """
    rpc call with invalid Request object:
    
    --> {"jsonrpc": "2.0", "method": 1, "params": "bar"}
    <-- {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": null}
    """
    data = {"jsonrpc":"2.0", "method":1, "params":"bar"}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['id'] is None
    assert d['error']['code'] == -32600

def test_invalid_batch():
    """
    rpc call with invalid Batch:
    
    --> [1,2,3]
    
    <-- {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": null}
    """

    data = [1, 2, 3]
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error')
    assert d['id'] is None
    assert d['error']['code'] == -32600


def test_rpc_call_batch():
    """
    rpc call Batch:
    
    --> [
    {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
    {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
    {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
    {"foo": "boo"},
    {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
    {"jsonrpc": "2.0", "method": "get_data", "id": "9"} 
    ]
    
    <-- [
    {"jsonrpc": "2.0", "result": 7, "id": "1"},
    {"jsonrpc": "2.0", "result": 19, "id": "2"},
    {"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request."}, "id": null},
    {"jsonrpc": "2.0", "error": {"code": -32601, "message": "Method not found."}, id: "5"},
    {"jsonrpc": "2.0", "result": ["hello", 5], "id": "9"}
    ]
    """

    data = [
        {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},
        {"jsonrpc": "2.0", "method": "notify_hello", "params": [7]},
        {"jsonrpc": "2.0", "method": "subtract", "params": [42,23], "id": "2"},
        {"foo": "boo"},
        {"jsonrpc": "2.0", "method": "foo.get", "params": {"name": "myself"}, "id": "5"},
        {"jsonrpc": "2.0", "method": "get_data", "id": "9"} 
        ]

    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert len(d) == 5
    assert d[0]['id'] == '1'
    assert d[1]['id'] == '2'
    assert d[2]['id'] is None
    assert d[2]['error']['code'] == -32600
    assert d[3]['id'] == '5'
    assert d[3]['error']['code'] == -32601
    assert d[4]['id'] == '9'
    assert d[4]['result'][0] == "hello"
    assert d[4]['result'][1] == 5

def test_rpc_call_batch_invalid_json():
    """
    rpc call Batch, invalid JSON:
    
    --> [ {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},{"jsonrpc": "2.0", "method" ]
    <-- {"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error."}, "id": null}
    
    
    """
    res = app.post('/', params='[ {"jsonrpc": "2.0", "method": "sum", "params": [1,2,4], "id": "1"},{"jsonrpc": "2.0", "method" ]',
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d['error']['code'] == -32700
    

def test_add_module():
    app = JsonRpcApplication()
    from . import sample
    app.rpc.addModule(sample)
    assert len(app.rpc.methods) == 2

    app = TestApp(app)
    data = {"jsonrpc": "2.0", "method": "tests.sample.greeting", "params": {"n":"あ"}, "id": 4}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error') is None
    assert d['result'] == 'Hello, あ'

    data = {"jsonrpc": "2.0", "method": "tests.sample.add", "params": [1, 2], "id": 4}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error') is None
    assert d.get('result') == 3


def test_lazy_loading1():
    app = JsonRpcApplication(rpcs={"greeting":"tests.sample:greeting"})
    app = TestApp(app)
    data = {"jsonrpc": "2.0", "method": "greeting", "params": {"n":"あ"}, "id": 4}
    res = app.post('/', params=json.dumps(data),
                   extra_environ={'CONTENT_TYPE':'application/json'})
    assert res.status_int == 200
    d = res.json
    assert d.get('error') is None
    assert d['result'] == 'Hello, あ'


def test_extra_vars():
    rpc = JsonRpc()
    rpc['add'] = lambda a, b: a + b
    args = {'a': 1}
    result = rpc({'jsonrpc': '2.0', 'method': 'add', 'id': 'test-rpc', 'params': args}, b=3)
    assert result['result'] == 4
    
    rpc['array_params_with_kwargs'] = lambda a, req: a + req.request_id
    args = [1]
    
    class Req:
        pass

    req = Req()
    req.request_id = 3
    result = rpc({
        'jsonrpc': '2.0', 
        'method': 'array_params_with_kwargs', 
        'id': 'test-rpc', 
        'params': args}, req=req)
    assert result['result'] == 4
