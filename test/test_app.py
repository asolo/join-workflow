import json
# import sys
# import os
# sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))

def test_index(app, client):

    

    # act
    result = client.get('/')

    # assert
    assert result.status_code == 200
    expected = {'hello': 'world'}
    assert expected == json.loads(result.get_data(as_text=True))

def test_post_whenempty_then400(app, client):
    
    # arrange
    expected = { "status": "error", "message": "malformed request body"}
    inputjson = "{}"

    # act
    client.post('/steps')



