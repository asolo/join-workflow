from flask import app, request
from flask import Flask

from Step import Step

app = Flask(__name__)

# this is a placeholder datastore
WORKFLOW = []

@app.route('/steps', methods=['GET', 'POST'])
def steps():
    if request.method == 'POST':
        try:
        # initialize a new step
            step = Step(request.form["id"], request.form["name"], request.form["description"], request.form["depends_on"])

            # TODO call a validation sub method to check
            ## 2. Fields are properly formed
            ## IDS are unique! 
            ## 3. Set the status (probably)
            ## 1. Circular dependency

            # print(step.id)
            WORKFLOW.append(step)
            print(str(len(WORKFLOW)))
            return "OK"
        except ValueError:
            print("Malformed Request Body")
            return "Error Message"
        except: # TODO REMOVE
            return "Error Message 2"
    else:

        # init a new dictionary for our GET result
        result = {}

        # Convert workflow object to special formatted json, and return as json
        for step in WORKFLOW:
            result[step.id] = step.__dict__
        return result

    # curl -X "POST" http://127.0.0.1:5000/steps


@app.route('/step/<string:id>', methods=['DELETE'])
def step(id):

    for step in WORKFLOW:
        if step.id == id:
            WORKFLOW.remove(step)
    return "ACCEPTED"

    # curl -X "DELETE" http://127.0.0.1:5000/step/1

if __name__ == '__main__':
    app.run(debug=True)