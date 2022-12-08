import requests
import json
import os
import hashlib

server_host = 'http://127.0.0.1:8282/'

def test_hello_world():
    req = requests.get(server_host)
    assert ('Hello World!' in req.text)
    
#testing nominal test case. 
# put some data in the datastorage
# get the data and check the hash key
# delete the data
def test_nominal():
    if os.path.isfile('upload/test/onigiri.png'):
        os.remove('upload/test/onigiri.png')
    
    test_oid = 'b44b1de94d321891436795ab96b1266767a60b969ee03f876dff52614665163c'
    req = requests.delete(server_host + '/data/test/' + test_oid)
    
    files = {'file': open('test_image/onigiri.png', 'rb')}
    
    #writing file in datastore
    req = requests.put(server_host + '/data/test', files=files)
    assert (req.status_code == 201)
    
    req_json = json.loads(req.content)
    oid = req_json['oid']
    size = req_json['size']
    
    #comparing result from request to what is expected
    assert(size == 3378)
    assert(oid == test_oid)
    
    req = requests.get(server_host + 'data/test/' + oid)
    #comparing queried hash value with oid from the server
    assert(hashlib.sha3_256(req.content).hexdigest() == oid)
    
    req = requests.delete(server_host + '/data/test/' + oid)
    assert (req.status_code == 200)

# Testing deduplicate data
def test_put_no_duplicate():
    files = {'file': open('test_image/onigiri.png', 'rb')}

    req = requests.put(server_host + '/data/test', files=files)
    assert (req.status_code == 201)
    
    req_json = json.loads(req.content)
    oid = req_json['oid']
    
    files = {'file': open('test_image/onigiri_duplicate.png', 'rb')}
    req = requests.put(server_host + '/data/test', files=files)
    #checking if duplicate condition worked
    assert (req.status_code == 603)
    
    req = requests.delete(server_host + '/data/test/' + oid)
    assert (req.status_code == 200)

#Testing different error cases for data upload and storage
def test_put_error():
    test_oid = 'b44b1de94d321891436795ab96b1266767a60b969ee03f876dff52614665163c'
    req = requests.delete(server_host + '/data/test/' + test_oid)
    
    files = {'data': open('test_image/onigiri.png', 'rb')}
    req = requests.put(server_host + '/data/test', files=files)
    assert (req.status_code == 400)

    req = requests.put(server_host + '/data/test')
    assert (req.status_code == 400)
    
    files = {'file': open('test_image/onigiri.png', 'rb')}
    req = requests.put(server_host + '/data/test', files=files)
    req = requests.put(server_host + '/data/test', files=files)
    assert (req.status_code == 602)
    
    req = requests.delete(server_host + '/data/test/' + test_oid)

#testing delete error use cases
def test_delete_error():
    req = requests.delete(server_host + '/data/test/1234')
    assert (req.status_code == 404)

#testing get object error use cases
def test_get_object_error():
    req = requests.get(server_host + '/data/404/1234')
    assert (req.status_code == 404)

#testing delete object error use cases
def test_404_error():
    req = requests.get(server_host + '/test_404')
    assert (req.status_code == 404)