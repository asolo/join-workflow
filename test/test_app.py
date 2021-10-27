import json

def test_post_whenempty_then400(app, client):
    
    # arrange
    mimetype = 'application/json'
    expected = { "status": "error", "message": "malformed request body"}
    data = ""

    # act
    response = client.post("/steps", data=json.dumps(data), headers=None)

    assert response.status_code == 400
    assert expected == json.loads(response.get_data(as_text=True))


