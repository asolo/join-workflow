
from src.Abstractions.Status import Status

class Task:
    """
    Represents a task in a workflow graph.

    Attributes:
        
    """

    def __init__(self, step: int, name: str, description: str, depends_on: list(int), status: Status):

        self.step = step
        self.name = name
        self.description = description
        self.depends_on = depends_on
        self.status = status # TODO how do we define and implement the status object of this class/JSON object