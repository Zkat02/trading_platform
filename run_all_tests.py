import unittest

from orders.tests.test_check_condition_for_close import TestCheckConditionForClose

test_suite = unittest.TestLoader().loadTestsFromTestCase(TestCheckConditionForClose)

unittest.TextTestRunner(verbosity=2).run(test_suite)
