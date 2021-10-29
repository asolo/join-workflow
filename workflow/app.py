from flask import app, request
from flask import Flask
import json
from typing import Dict, Iterable, Set

# create a flask application
app = Flask(__name__)

# this is a placeholder in-memory datastore
WORKFLOW = {}

@app.route('/steps', methods=['GET', 'POST'])
def steps():
    """
    POST adds and validates a new step for the workflow graph. GET returns the workflow graph
    with step statuses evaluated.
    """

    if request.method == 'POST':

            # Validate: ensure the json can be parsed
            try:
                # convert raw json input to a dictionary
                convertedDict = json.loads(request.data)

                # identify the step id
                step_id = list(convertedDict.keys())[0]
                
                # parse out the remaining fields for validation
                step_name = convertedDict[step_id]["name"]
                step_description = convertedDict[step_id]["description"]
                step_depends_on = convertedDict[step_id]["depends_on"]
            
            except (ValueError, KeyError, IndexError, AttributeError):
                return { "status": "error", "message": "malformed request body"}, 400

            # Validate: ensure that step Id is unique
            if step_id in WORKFLOW.keys():
                return { "status": "error", "message": "id already exists"}, 409

            # add new step to workflow graph
            WORKFLOW[step_id] = list(convertedDict.values())[0]

            # Validate: check if we have a circular dependency
            methods = Methods()
            if methods.hasCircularDependency(workflow=WORKFLOW):
                
                # remove the added step that created a circular dependency
                del WORKFLOW[step_id]

                # return error
                return { "status": "error", "message": "cycles not allowed in workflow graph"}, 422
            
            # validations passed, post successful
            return {"status": "ok"}, 200
    else:

        # prior to returning a GET, set the status object within each step
        methods = Methods()
        return methods.getUpdatedStatusOfSteps(WORKFLOW), 200

@app.route('/step/<string:id>', methods=['DELETE'])
def step(id):
    """
    Removes a step in the workflow graph. 
    """

    # Validate: Make sure the step exists before attempting to remove
    if id in WORKFLOW.keys():
        del WORKFLOW[id]
        return { "status": "accepted" }, 202
    else:
        return {"status": "error", "message": f"resource with ID: {id} does not exist"}, 400

class Methods:
    """
    This class contains methods to calculate relationships within a workflow graph
    """

    def hasCircularDependency(self, workflow: Dict) -> bool:
        """
        Given a workflow graph, evaluates the graph to determine if a circular
        dependency exists. 

        Args:
            workflow(Dict): a workflow graph

        Returns:
            bool: True indicates a circular reference exists in the workflow
        """
        
        # loop through each step in the workflow graph and test circular dependency chains
        for step_id in workflow.keys():
            if self._hasCircularDependencyStep(workflow, step_id, set()):
                return True

        # we made it through the whole graph with no circular dependencies 
        return False

    def _hasCircularDependencyStep(self, workflow: Dict, curr_id: str, steps_seen: Set=set()):
        """
        Given a workflow graph and a starting step, evaluates the graph linked to that step
        to determine if a circular reference exists in this segment using recursion.

        Args:
            workflow(Dict): a workflow graph
            curr_id(str): an step id from which to start evaluation
            steps_seen(Set): a set that records the steps visited

        Returns:
            bool: True indicates a circular reference exists in this segment of workflow
        """
        
        # list dependencies of current step
        depends_on = workflow[curr_id]["depends_on"]

        # check if this step has already been visited, indicating a circular dependency
        if curr_id in steps_seen:
            return True

        # step is new, so note that we have been at the current step
        steps_seen.add(curr_id)

        # travel to the next step(s) in the graph
        for next_id in depends_on:
            if next_id in workflow.keys():
                return self._hasCircularDependencyStep(workflow, next_id, steps_seen)

        # We made it to the end of this segment with no circular dependencies    
        return False

    def getUpdatedStatusOfSteps(self, workflow: Dict) -> Dict:
        """
        Given a workflow graph, evaluates the status of each step's dependencies. The returned workflow
        will contain the a status object for each step.

        Args:
            workflow (Dict): a workflow graph

        Returns:
            workflow (Dict): a workflow where each step has a status object indicating if dependencies are
            satisfied.
        """

        # create a dict of steps which err out at end failed dependency
        error_end_steps = {}

        # traverse each step
        for step_id in workflow:
            step = workflow[step_id]
            depends_on = step["depends_on"]
            error = False

            # check if dependencies exist
            for dependency in depends_on:

                # if a first missing dependency is found for a step, add to error dict
                if dependency not in workflow.keys() and step_id not in error_end_steps:
                    error_end_steps[step_id] = dependency

        # create a reverse dependency dictionary
        reverse_dependencies = self.getReverseDependencies(workflow)

        # next use the reverse dependency chain to set the upstream status of each error ending step
        for step_id in error_end_steps.keys():

            # recursively run up the chain from each error_end_step
            self._writeErrorSteps(workflow, reverse_dependencies, step_id, error_end_steps[step_id])

        # we made it through the whole graph, assign an "ok" status to non-error steps
        for step_id in workflow.keys():
            if "status" not in workflow[step_id]:
                workflow[step_id]["status"] = "ok"

        return workflow

    # def getUpdatedStatusOfSteps(self, workflow: Dict) -> Dict:
    #
    #     # loop through each step in the workflow graph and set dependency chain status
    #     for step_id in workflow.keys():
    #         self._getUpdatedStatusOfStep(workflow, step_id, set())
    #
    #     # we made it through the whole graph, assign an "ok" status to non-error steps
    #     for step_id in workflow.keys():
    #         if "status" not in workflow[step_id]:
    #             workflow[step_id]["status"] = "ok"
    #
    #     return workflow
    #
    # def _getUpdatedStatusOfStep(self, workflow: Dict, curr_id: str, steps_seen: Set = set()) -> None:
    #
    #     # list dependencies of current step
    #     depends_on = workflow[curr_id]["depends_on"]
    #
    #     # step is new, so note that we have been at the current step
    #     steps_seen.add(curr_id)
    #
    #
    #     if len(depends_on) == 0:
    #
    #
    #     # travel to the next step(s) in the graph if it exists
    #     for next_id in depends_on:
    #         if next_id in workflow.keys():
    #             self._getUpdatedStatusOfStep(workflow, next_id, steps_seen)
    #         else:
    #             # we have reached a break in dependency chain. Use the set to write an error status where not written
    #             # yet along this dependency chain
    #             for step_id in steps_seen:
    #                 # first, check if they have a status or if an error is already set
    #                 if "status" not in workflow[step_id]:
    #                     workflow[step_id]["status"] = {"error": {"msg": "Missing dependency", "detail": next_id}}
    #     return

    def getReverseDependencies(self, workflow):
        reverse_dependencies = {}

        for step_id in workflow.keys():
            depends_on = workflow[step_id]["depends_on"]
            for dependency in depends_on:
                if dependency not in reverse_dependencies:
                    reverse_dependencies[dependency] = [step_id]
                else:
                    reverse_dependencies[dependency].append(step_id)

        return reverse_dependencies

    def _writeErrorSteps(self, workflow: Dict, reverse_dependencies: Dict, curr_id: str, error_step: str):
        """

        Args:
            workflow(Dict): a workflow graph


        Returns:
            bool: True indicates a circular reference exists in this segment of workflow
        """

        # note the error details for this step if it has not been attributed yet
        if "status" not in workflow[curr_id]:
            workflow[curr_id]["status"] = {"error": {"msg": "Missing dependency", "detail": error_step}}

        # check if the top of the dependency chain has been reached, and exit
        if curr_id not in reverse_dependencies.keys():
            return

        reverse_depends_on = reverse_dependencies[curr_id]

        # travel to the next step(s) in the graph
        for next_id in reverse_depends_on:
            if next_id in workflow.keys():
                self._writeErrorSteps(workflow, reverse_dependencies, next_id, error_step)




if __name__ == '__main__':
    app.run(debug=True)