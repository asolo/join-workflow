import os
import pytest
import sys
import unittest

sys.path.append(os.path.join(os.path.abspath(os.path.curdir), '..'))

import workflow

class TestMethods(unittest.TestCase):

    def test_hasCircularDependency_whenCircular(self):

        input_workflow = {\
                            "id1" : {"depends_on": ["id2"]},\
                            "id2" : {"depends_on": ["id3", "id4"]},\
                            "id3" : {"depends_on": ["id1"]},\
                            "id4" : {"depends_on": []}\
                        }

        # act
        result = workflow.hasCircularDependency(input_workflow)

        # assert
        assert result == True

if __name__ == '__main__':
    unittest.main()
