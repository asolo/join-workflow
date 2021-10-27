from flask import app, request
from flask import Flask
import json

from step import Step
from utils import Utils

app = Flask(__name__)

# this is a placeholder datastore
WORKFLOW = {}

@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if request.method == 'POST':
            try:
                # convert raw json input to a dictionary
                convertedDict = json.loads(request.data)

                # identify the step id, the outer field of the nested json
                step_id = list(convertedDict.keys())[0]
                
                # parse out the remaining fields
                step_name = convertedDict[step_id]["name"]
                step_description = convertedDict[step_id]["description"]
                step_depends_on = convertedDict[step_id]["depends_on"]
            except ValueError or TypeError:
                return "MALFORMED REQUEST BODY", 400

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

            WORKFLOW[new_step.id] = list(convertedDict.values())[0]

            print(WORKFLOW)

            # check circular dependencies
            utils = Utils()
            if utils.hasCircularDependency(workflow=WORKFLOW, curr_id=None, steps_seen=set()):
                del WORKFLOW[new_step.id]
                return "CYCLES NOT ALLOWED IN WORKFLOW GRAPH", 422
            
            
            # TODO call a validation sub method to check
            ## 2. Fields are properly formed
            ## 3. Set the status (probably)
            ## 1. Circular dependency
            return "OK - POST COMPLETE", 200
        # except ValueError:
        #     print("Malformed Request Body")
        #     return "Error Message", 400
        # except: # TODO REMOVE
        #     return "Error Message 2", 400
    else:

        return WORKFLOW


@app.route('/step/<string:id>', methods=['DELETE'])
def step(id):

    del WORKFLOW[id]

    return "ACCEPTED", 202

    # curl -X "DELETE" http://127.0.0.1:5000/step/1

if __name__ == '__main__':
    app.run(debug=True)