from flask import app, request
from flask import Flask
import json
from methods import Methods

app = Flask(__name__)

# this is a placeholder datastore
WORKFLOW = {}

@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if request.method == 'POST':
            try:
                # convert raw json input to a dictionary
                convertedDict = json.loads(request.data)

                # identify the step id
                step_id = list(convertedDict.keys())[0]
                
                # parse out the remaining fields for validation
                step_name = convertedDict[step_id]["name"]
                step_description = convertedDict[step_id]["description"]
                step_depends_on = convertedDict[step_id]["depends_on"]
            
            except ValueError or IndexError:
                return { "status": "error", "message": "malformed request body"}, 400

            # Validate: Ensure that step ID is unique
            if step_id in WORKFLOW.keys():
                return { "status": "error", "message": "id already exists"}, 409

            # add new step to workflow graph
            WORKFLOW[step_id] = list(convertedDict.values())[0]

            # Validate: check circular dependencies
            methods = Methods()
            if methods.hasCircularDependency(workflow=WORKFLOW, curr_id=None, steps_seen=set()):
                
                # remove the added step with circular dependency
                del WORKFLOW[step_id]

                # return error
                return { "status": "error", "message": "cycles not allowed in workflow graph"}, 422
            
            # validations past, post successful
            return {"status": "OK"}, 200
    else:

        # prior to returning a GET, set the status object within each step
        methods = Methods()
        return methods.getUpdatedStatusOfSteps(WORKFLOW)

@app.route('/step/<string:id>', methods=['DELETE'])
def step(id):

    if id in WORKFLOW.keys():
        del WORKFLOW[id]
        return { "status": "accepted" }, 202
    else:
        return f"RESOURCE WITH ID: {id} DOES NOT EXIST", 400

if __name__ == '__main__':
    app.run(debug=True)