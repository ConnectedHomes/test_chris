# ASSERTION_NAME_LIST = [
#     'assertEqual',
#     'assertIn',
#     'assertNotIn'
# ]

from digital_Web_CI_Stack.python_lambdas.lib.logger import configure_logger

class CountNumberOfAssertionsMixin():

    # leaving it, but not working for now
    # #https://stackoverflow.com/questions/34794634/how-to-use-a-variable-as-function-name-in-python
    # def test_prepare_count_nb_of_assertions(self):
    #     for assertion_name in ASSERTION_NAME_LIST:
    #         def _f():
    #             nb_of_assertions_tracking[assertion_name] = nb_of_assertions_tracking.get(assertion_name) or 0
    #             nb_of_assertions_tracking[assertion_name] += 1
    #         # not working : TypeError: super does not support item assignment
    #         # https://bugs.python.org/issue805304
    #         super()[assertion_name] = _f
    #         del _f

    nb_of_assertions_tracking = {}

    def setup_mock(self, assertName):
        stack_name = self.count_nb_assertions_mixin_print_test_stack
        self.nb_of_assertions_tracking[stack_name] = self.nb_of_assertions_tracking.get(stack_name) or {}
        assoc_array = self.nb_of_assertions_tracking[stack_name]
        assoc_array[assertName] = assoc_array.get(assertName) or 0
        return assoc_array

    def assertEqual(self, *argv):
        assoc_array = self.setup_mock('assertEqual')
        assoc_array['assertEqual'] += 1
        return super().assertEqual(*argv)

    def assertIn(self, *argv):
        assoc_array = self.setup_mock('assertIn')
        assoc_array['assertIn'] += 1
        return super().assertIn(*argv)

    def assertNotIn(self, *argv):
        assoc_array = self.setup_mock('assertNotIn')
        assoc_array['assertNotIn'] += 1
        return super().assertNotIn(*argv)

    def count_nb_assertions_mixin_print_nb_assertions(self):
        #print(f'\033[92m # of assertions run: {self.nb_of_assertions_tracking}')
        LOGGER = configure_logger(__name__, '', 'DARKGREEN')
        LOGGER.info(
            f'# of assertions run: {self.nb_of_assertions_tracking}'
        )
