# join-workflows
### introduction
The workflow app will run an API at http://localhost:5000 built with python and the Flask framework to manage a single workfow graph. The API supports a POST endpoint for a adding a single step in a workflow, a GET endpoint for retrieving the entire workflow, and a DELETE endpoint for removing a single step from a workflow.

### functionality
POST requests should be formed with the following parameters in JSON:
```json
"id":{
   "name":"A Name for the New Step",
   "description":"This new step does a new thing.",
   "depends_on":[
      "an-old-step"
```

Malformed POST requests will return a 400 error response. 

Workflow steps can refer to other steps in the graph. POSTing a workflow step which introduces a circuler reference will be rejected with a 422 response. 

Workflow step IDs must be unique. Repeated step Ids will be rejected with a 409 response. 

When executing a GET request, the entire workflow graph is returned. In executing the GET, the status of each workflow step will be determined, specifically if any dependent steps are missing. If all dependent steps are present, a status of "ok" will be returned. Otherwise, a status of "error" will be returned with a "detail" attribute that shows the *first* missing dependency step detected.

Finally, the DELETE endpoint will remove a single step by including the Id at the end of the URL endpoint. (`.../step/<id>`). If a specified Id to be deleted does not exist, a 400 response will be returned.

### notes
This API is only configured to run locally. This API is also using a temporary in-memory data store, so each time the app is restarted, the datastore (containing the workflow graph) will be empty. 


# prerequisites:
python 3.x

# how to configure and launch application
Navigate to the root directory of `join-workflows` and create a virtual environment with
```bash
$ python3 -m venv venv
```

Then activate the venv:
```$ . venv/bin/activate```

Install requirements to your venv:
```$ pip install Flask```
```$ pip install pytest```

Start the application by running:
```$ python3 workflow/app.py```

# how to execute tests
From the root directory of `join-workflows`, and with the virtual environment active, execute:
```python -m pytest```

# manually testing the API
Once the application is up. You can use curl commands to post, get, and delete data using the from the terminal. Alternatively, a handy POSTMAN collection has also been included. 

### POST a step
```curl -d '{"id" : {"name": "A Name for the New Step", "description": "This new step does a new thing.", "depends_on": ["id1"] }}' -H "Content-Type: application/json" -X POST http://localhost:5000/steps```

### GET workflow graph
```curl http://localhost:5000/steps```

### DELETE a step
```curl -X DELETE http://localhost:5000/step/id```

# future work

- Add a datastore: for the purposes of this project, a datastore is created in memory each time this API is launched.
- More detailed error handling on input validations: currently any incorrect typing, empty request body, or otherwise unexpected input returns the same error path and message. 
