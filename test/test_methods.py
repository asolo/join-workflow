import os
import sys
sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))
import unittest
from workflow.app import Methods


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

    def test_getUpdatedStatusOfSteps_whenStatusOK(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": []},\
                        }
        test = Methods()

        expected_workflow = {\
                            "id4" : {"depends_on": [], "status":"ok"},\
                            "id1" : {"depends_on": ["id2"], "status":"ok"},\
                            "id2" : {"depends_on": ["id3", "id4"], "status":"ok"},\
                            "id3" : {"depends_on": [], "status":"ok"},\
                        }

        # act
        result = test.getUpdatedStatusOfSteps(input_workflow)

        # assert
        self.assertDictEqual(expected_workflow, result)

    def test_getUpdatedStatusOfSteps_whenStatusMixed(self):

        input_workflow = {\
                            "id4" : {"depends_on": []},\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                        }
        test = Methods()

        expected_workflow = {\
                            "id4" : {"depends_on": [], "status":"ok"},\
                            "id1" : {"depends_on": ["id2"], "status":"ok"},\
                            "id2" : {"depends_on": ["id3", "id4"], "status":\
                                {"error":{"msg":"Missing dependency", "detail":"id3"}}}\
                        }

        # act
        result = test.getUpdatedStatusOfSteps(input_workflow)

        # assert
        self.assertDictEqual(expected_workflow, result)

if __name__ == '__main__':
    unittest.main()
