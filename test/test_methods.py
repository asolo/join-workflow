import os
import sys
import unittest

sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))

from workflow.methods import Methods

class TestMethods(unittest.TestCase):

    def test_hasCircularDependency_whenNotCircular(self):

        input_workflow = {\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id4"]},\
                            "id4" : {"depends_on": []}\
                        }

        test = Methods()

        # act
        result = test.hasCircularDependency(input_workflow)

        # assert
        self.assertFalse(result)

    def test_hasCircularDependency_whenCircular(self):

        input_workflow = {\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id1"]},\
                            "id4" : {"depends_on": []}\
                        }

        test = Methods()

        # act
        result = test.hasCircularDependency(input_workflow)

        # assert
        self.assertTrue(result)

    def test_hasCircularDependency_whenCircularButDifferentOrder(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id1"]},\
                        }
        test = Methods()

        # act
        result = test.hasCircularDependency(input_workflow)

        # assert
        self.assertTrue(result)

    def test_hasCircularDependency_whenCircular_withOneStep(self):

        input_workflow = {\
                            "id4" : {"depends_on": ["id4"]}
                        }
        test = Methods()

        # act
        result = test.hasCircularDependency(input_workflow)

        # assert
        self.assertTrue(result)

    def test_getUpdatedStatusOfSteps_WhenStatusOK(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": []},\
                        }
        test = Methods()

        expected_workflow = {\
                            "id4" : {"depends_on": [], "status":"OK"},\
                            "id1" : {"depends_on": ["id2"], "status":"OK"},\
                            "id2" : {"depends_on": ["id3", "id4"], "status":"OK"},\
                            "id3" : {"depends_on": [], "status":"OK"},\
                        }

        # act
        result = test.getUpdatedStatusOfSteps(input_workflow)

        # assert
        self.assertDictEqual(expected_workflow, result)

    def test_getUpdatedStatusOfSteps_WhenStatusMixed(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                        }
        test = Methods()

        expected_workflow = {\
                            "id4" : {"depends_on": [], "status":"OK"},\
                            "id1" : {"depends_on": ["id2"], "status":"OK"},\
                            "id2" : {"depends_on": ["id3", "id4"], "status":\
                                {"error":{"msg":"Missing dependency", "detail":"id3"}}}\
                        }

        # act
        result = test.getUpdatedStatusOfSteps(input_workflow)

        # assert
        self.assertDictEqual(expected_workflow, result)

if __name__ == '__main__':
    unittest.main()