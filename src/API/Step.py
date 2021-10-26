
from typing import List
from Status import Status

class Step:
    """
    Represents a task in a workflow graph.

    Attributes:
        
    """

    def __init__(self, id: str, name: str, description: str, depends_on: List[str]):

        self.id = id
        self.name = name
        self.description = description
        self.depends_on = depends_on
        # self.status = status # TODO how do we define and implement the status object of this class/JSON object

    # def Validate(self):
        