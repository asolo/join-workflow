from flask import app, request
from flask import Flask
import json

from step import Step
# import workflow

app = Flask(__name__)

# this is a placeholder datastore
WORKFLOW = {}

@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if request.method == 'POST':
        # try:

            # convert raw json input to a dictionary
            convertedDict = json.loads(request.data)

            # identify the step id, the outer field of the nested json
            step_id = list(convertedDict.keys())[0]
            
            # parse out the remaining fields
            step_name = convertedDict[step_id]["name"]
            step_description = convertedDict[step_id]["description"]
            step_depends_on = convertedDict[step_id]["depends_on"]

            # initialize a new step
            new_step = Step(
                        id=step_id, 
                        name=step_name, 
                        description=step_description, 
                        depends_on=step_depends_on)

            ## TODO: VALIDATIONS
            
            # Validate: Ensure that step ID is unique
            # TODO: Should we remove this, not in requirements
            if new_step.id in WORKFLOW.keys():
                return "ID ALREADY EXISTS", 409

            # check circular dependencies
            if hasCircularDependency(WORKFLOW):
                return "CYCLES NOT ALLOWED IN WORKFLOW GRAPH", 422
            
            
            # TODO call a validation sub method to check
            ## 2. Fields are properly formed
            ## 3. Set the status (probably)
            ## 1. Circular dependency

            WORKFLOW[new_step.id] = list(convertedDict.values())[0]
            return "OK - POST COMPLETE", 200
        # except ValueError:
        #     print("Malformed Request Body")
        #     return "Error Message", 400
        # except: # TODO REMOVE
        #     return "Error Message 2", 400
    else:

        # init a new dictionary for our GET result
        result = {}

        # Convert workflow object to special formatted json, and return as json
        # for step in WORKFLOW:
            
        #     # get the object, convert to dict
            
        #     result[step.id] = step[step.id].__dict__
        return WORKFLOW

    # curl -X "POST" http://127.0.0.1:5000/steps


@app.route('/step/<string:id>', methods=['DELETE'])
def step(id):

    for step in WORKFLOW:
        if step.id == id:
            WORKFLOW.remove(step)
    return "ACCEPTED"

    # curl -X "DELETE" http://127.0.0.1:5000/step/1

def hasCircularDependency(workflow):
    
    # Create a set of steps seen while traversing dependency chains
    steps_seen = ()

    # start at the first node
    current_id = list(workflow.keys())[0]

    depends_on = workflow[current_id]["depends_on"]
    
    return True

if __name__ == '__main__':
    app.run(debug=True)