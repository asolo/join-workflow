class Methods:

    def hasCircularDependency(self, workflow):
        
        # loop through each step in the workflow graph and test circular dependency chains
        for step_id in workflow.keys():
            if self.hasCircularDependencyStep(workflow, step_id, set()):
                return True

        # we made it through the whole graph with no circular dependencies 
        return False

    def hasCircularDependencyStep(self, workflow, curr_id, steps_seen=set()):
        
        # list dependencies of current step
        depends_on = workflow[curr_id]["depends_on"]

        # check if this step has already been visited, indicating a circular dependency
        if curr_id in steps_seen:
            return True

        # step is new, so note that we have been at the current step
        steps_seen.add(curr_id)

        # travel to the next step in the graph
        for next_id in depends_on:
            
            if next_id in workflow.keys():
                return self.hasCircularDependencyStep(workflow, next_id, steps_seen)

        # We made it to the end of this chain with no circular dependencies    
        return False

    def getUpdatedStatusOfSteps(self, workflow):

        # traverse each step
        for step_id in workflow:
            step = workflow[step_id]
            depends_on = step["depends_on"]
            error = False

            # check if dependencies exist
            for dependency in depends_on:
                if dependency not in workflow.keys():
                    error = True
                    detail = dependency

            # add or set status for each workflow step
            if error:
                workflow[step_id]["status"] =  {"error" : \
                                                {"msg":"Missing dependency", "detail":detail}}
            else:
                workflow[step_id]["status"] =  "OK"
        
        return workflow