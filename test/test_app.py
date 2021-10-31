import json
from unittest import TestCase

def test_post_whenempty_then400(app, client):

    # arrange
    expected = { "status": "error", "message": "malformed request body"}
    data = ""

    # act
    response = client.post("/steps", data=json.dumps(data), headers=None)

    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))

def test_post_whenemissingfields_then400(app, client):
    
    # arrange
    expected = { "status": "error", "message": "malformed request body"}
    data = {"id" : {
            "name": "A Name for the New Step", 
            "depends_on": [
                "an-old-step"
                ] }}

    # act
    response = client.post("/steps", data=json.dumps(data), headers=None)

    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))


def test_post_whenimproperkey_returns400(app, client):
    
    # arrange
    expected = { "status": "error", "message": "malformed request body"}
    data = {"id" : {
            "name": "A Name for the New Step", 
            "description": "This new step does a new thing.", 
            "depends_on_____": [
                "2"
                ] }}

    # act
    response = client.post("/steps", data=json.dumps(data), headers=None)

    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))

def test_post_dataOK_returns200(app, client):
    
    # arrange
    expected = { "status": "ok"}
    data1 = {"id" : {
            "name": "A Name for the New Step",
            "description": "This new step does a new thing.", \
            "depends_on": [
                "2"
                ] }}

    # act
    response = client.post("/steps", data=json.dumps(data1), headers=None)

    # assert
    assert response.status_code == 200
    assert expected == json.loads(response.get_data(as_text=True))

    # clean up
    cleanUpDB(client)
    
def test_post_whendupplicateID_returns409(app, client):

    # arrange
    expected = { "status": "error", "message": "id already exists"}
    data1 = {"id" : {
            "name": "A Name for the New Step",
            "description": "This new step does a new thing.",
            "depends_on": [
                "2"
                ] }}

    
    response1 = client.post("/steps", data=json.dumps(data1), headers=None)

    # insert a first object that will be accepted
    assert response1.status_code == 200

    # act - insert an object with the same id
    response2 = client.post("/steps", data=json.dumps(data1), headers=None)

    # assert
    assert response2.status_code == 409
    assert expected == json.loads(response2.get_data(as_text=True))
    
    # clean up
    cleanUpDB(client)

def test_post_whenCircularRefCreated_returns422(app, client):

    # arrange
    expected = { "status": "error", "message": "cycles not allowed in workflow graph"}
    data1 = {"id" : {
            "name": "A Name for the New Step",
            "description": "This new step does a new thing.",
            "depends_on": [
                "id2"
                ] }}
    data2 = {"id2" : {
            "name": "A Name for the New Step",
            "description": "This new step does a new thing.",
            "depends_on": [
                "id"
                ] }}

    response1 = client.post("/steps", data=json.dumps(data1), headers=None)

    # insert a first object that will be accepted
    assert response1.status_code == 200

    # act - insert an object that depends on the first, creating a circular ref
    response2 = client.post("/steps", data=json.dumps(data2), headers=None)

    # assert
    assert response2.status_code == 422
    assert expected == json.loads(response2.get_data(as_text=True))
    
    # clean up
    cleanUpDB(client)

def test_get_whenEmpty_returns200(app, client):

    # arrange
    expected = {}

    # hit the get endpint
    getResponse = client.get("/steps")

    actual = json.loads(getResponse.get_data(as_text=True))

    # assert
    assert getResponse.status_code == 200
    TestCase().assertDictEqual(expected, actual)
    
    # clean up
    cleanUpDB(client)

def test_get_whenTwoObjects_returns200(app, client):

    # arrange
    expected = {
                "a-cool-step": {
                    "name": "Human-readable Step Name", 
                    "description": "This step does a thing", 
                    "depends_on": [],
                    "status": "ok"
                    }, 
                "another-step": {
                    "name": "Another Step Name",
                    "description": "This step does _another_ thing", 
                    "depends_on": [
                        "a-cool-step",
                        "one-more-step" ],
                    "status": { "error": {
                        "msg": "Missing dependency",
                        "detail": "one-more-step" }
                        }} 
                }
    
    data1 = {"a-cool-step" : {
                                "name": "Human-readable Step Name", 
                    "description": "This step does a thing", 
                    "depends_on": []}}

    data2 = {"another-step": {
                    "name": "Another Step Name",
                    "description": "This step does _another_ thing", 
                    "depends_on": [
                        "a-cool-step",
                        "one-more-step" ]}}
    # insert a first object that will be accepted
    response1 = client.post("/steps", data=json.dumps(data1), headers=None)
    assert response1.status_code == 200

    # insert a second object that will be accepted
    response2 = client.post("/steps", data=json.dumps(data2), headers=None)
    assert response2.status_code == 200

    # hit the get endpint
    getResponse = client.get("/steps")

    actual = json.loads(getResponse.get_data(as_text=True))

    # assert
    assert getResponse.status_code == 200
    assert len(actual.keys()) == 2
    TestCase().assertDictEqual(expected, actual)
    
    # clean up
    cleanUpDB(client)

def test_get_whenStatusChanges_returnsNoErrorsAfterUpdate(app, client):

    # arrange
    expected1 = {
        "another-step": {
            "name": "Another Step Name",
            "description": "This step does _another_ thing",
            "depends_on": [
                "a-cool-step"],
            "status": {"error": {
                "msg": "Missing dependency",
                "detail": "a-cool-step"}
            }}
    }

    expected2 = {
        "a-cool-step": {
            "name": "Human-readable Step Name",
            "description": "This step does a thing",
            "depends_on": [],
            "status": "ok"
        },
        "another-step": {
            "name": "Another Step Name",
            "description": "This step does _another_ thing",
            "depends_on": [
                "a-cool-step"],
            "status": "ok"}
            }

    data1 = {"another-step": {
        "name": "Another Step Name",
        "description": "This step does _another_ thing",
        "depends_on": [
            "a-cool-step"
            ]}}

    data2 = {"a-cool-step": {
        "name": "Human-readable Step Name",
        "description": "This step does a thing",
        "depends_on": []}}

    # insert a first object that will be accepted
    response1 = client.post("/steps", data=json.dumps(data1), headers=None)
    assert response1.status_code == 200

    # hit the get endpint for the first time
    getResponse1 = client.get("/steps")

    actual1 = json.loads(getResponse1.get_data(as_text=True))

    # assert the first expected response which has an error on the object
    assert getResponse1.status_code == 200
    TestCase().assertDictEqual(expected1, actual1)

    # insert a second object that will be accepted
    response2 = client.post("/steps", data=json.dumps(data2), headers=None)
    assert response2.status_code == 200

    # hit the get endpint
    getResponse2 = client.get("/steps")

    actual2 = json.loads(getResponse2.get_data(as_text=True))

    # assert
    assert getResponse2.status_code == 200
    assert len(actual2.keys()) == 2
    TestCase().assertDictEqual(expected2, actual2)

    # clean up
    cleanUpDB(client)

def test_delete_whenDoesNotExist_returns400(app, client):
    
    # arrange
    expected = {"status": "error", "message": "resource with ID: id1 does not exist"}

    # hit the delete endpint
    response = client.delete("/step/id1")

    # assert
    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))

    # clean up
    cleanUpDB(client)

def test_delete_whenTwoObjects_deletesCorrectOne_returns200(app, client):

    # arrange
    expected = {
                "a-cool-step": {
                    "name": "Human-readable Step Name", 
                    "description": "This step does a thing", 
                    "depends_on": [],
                    "status": "ok"
                    }, 
                }
    
    expectedDeleteResponse = { "status": "accepted" }
    
    data1 = {"a-cool-step" : {
                                "name": "Human-readable Step Name", 
                    "description": "This step does a thing", 
                    "depends_on": []}}

    data2 = {"another-step": {
                    "name": "Another Step Name",
                    "description": "This step does _another_ thing", 
                    "depends_on": [
                        "a-cool-step",
                        "one-more-step" ]}}
                        
    # insert a first object that will be accepted
    response1 = client.post("/steps", data=json.dumps(data1), headers=None)
    assert response1.status_code == 200

    # insert a second object that will be accepted
    response2 = client.post("/steps", data=json.dumps(data2), headers=None)
    assert response2.status_code == 200

    # act
    # hit the delete endpoint with the id "another-step", assert delete response as expected
    delResponse = client.delete("/step/another-step")
    assert delResponse.status_code == 202
    assert expectedDeleteResponse == json.loads(delResponse.get_data(as_text=True))

    # hit the get endpint
    getResponse = client.get("/steps")
    actual = json.loads(getResponse.get_data(as_text=True))

    # assert
    # make sure there's just one object, and it is the one NOT deleted, "a-cool-step": 
    assert getResponse.status_code == 200
    assert len(actual.keys()) == 1
    TestCase().assertDictEqual(expected, actual)
    
    # clean up
    cleanUpDB(client)
    
def cleanUpDB(client):

    # get the items in the DB
    getResponse = client.get("/steps")
    for step in json.loads(getResponse.get_data(as_text=True)).keys():
        
        # call the delete endpoint to clean up these items
        delResponse = client.delete(f"/step/{step}")
        assert delResponse.status_code == 202