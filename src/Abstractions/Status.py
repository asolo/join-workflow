class Status:
    """
    Represents a status of a task in a workflow graph.

    Attributes:
        step (int): surrogate identifier of workflow step 

    """

    def __init__(self, status: str, name: str):
        self.status = status
