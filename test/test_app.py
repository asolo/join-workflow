import os
import sys
import unittest

sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))

from workflow.utils import Utils

class TestMethods(unittest.TestCase):

    def test_hasCircularDependency_whenCircular(self):

        input_workflow = {\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id1"]},\
                            "id4" : {"depends_on": []}\
                        }

        test = Utils()

        # act
        result = test.hasCircularDependency(input_workflow, None, set())

        # assert
        self.assertTrue(result)

    def test_hasCircularDependency_whenCircularButDifferentOrder(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id1"]},\
                        }
        test = Utils()

        # act
        result = test.hasCircularDependency(input_workflow, None, set())

        # assert
        self.assertTrue(result)

    def test_hasCircularDependency_whenCircular_withOneStep(self):

        input_workflow = {\
                            "id4" : {"depends_on": ["id4"]}
                        }
        test = Utils()

        # act
        result = test.hasCircularDependency(input_workflow, None, set())

        # assert
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
