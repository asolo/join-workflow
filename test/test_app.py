import json

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
    data = {"id" : {\
            "name": "A Name for the New Step", \
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
    data = {"id" : {\
            "name": "A Name for the New Step", \
            "description": "This new step does a new thing.", \
            "depends_on_____": [
                "2"
                ] }}

    # act
    response = client.post("/steps", data=json.dumps(data), headers=None)

    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))

def test_post_dataOK_returns200(app, client):
    
    # arrange
    expected = { "status": "OK"}
    data1 = {"id" : {\
            "name": "A Name for the New Step", \
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
    data1 = {"id" : {\
            "name": "A Name for the New Step", \
            "description": "This new step does a new thing.", \
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

def test_post_whenCircularRefCreated_returns409(app, client):

    # arrange
    expected = { "status": "error", "message": "cycles not allowed in workflow graph"}
    data1 = {"id" : {\
            "name": "A Name for the New Step", \
            "description": "This new step does a new thing.", \
            "depends_on": [
                "id2"
                ] }}
    data2 = {"id2" : {\
            "name": "A Name for the New Step", \
            "description": "This new step does a new thing.", \
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
    
    


def cleanUpDB(client):

    # get the items in the DB
    getResponse = client.get("/steps")
    for step in json.loads(getResponse.get_data(as_text=True)).keys():
        
        # call the delete points to clean up these items
        delResponse = client.delete(f"/step/{step}")
        assert delResponse.status_code == 202



        # data = {"id" : {\
        # "name": "A Name for the New Step", \
        # "description": "This new step does a new thing.", \
        # "depends_on": [
        #     "an-old-step"
        #     ] }}