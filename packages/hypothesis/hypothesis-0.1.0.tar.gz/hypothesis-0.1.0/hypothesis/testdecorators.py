from functools import wraps
from hypothesis.verifier import Verifier, Unfalsifiable, UnsatisfiedAssumption

def given(*generator_arguments,**kwargs):
    try:
        verifier = kwargs["verifier"]
    except KeyError:
        verifier = Verifier()

    def run_test_with_generator(test):
        @wraps(test)
        def wrapped_test(*arguments):
            # The only thing we accept in falsifying the test are exceptions 
            # Returning successfully is always a pass.
            def to_falsify(*xs): 
                try:
                    test(*(arguments + xs)) 
                    return True
                except UnsatisfiedAssumption as e:
                    raise e
                except:
                    return False

            try:
                falsifying_example = verifier.falsify(to_falsify, *generator_arguments)
            except Unfalsifiable:
                return
          
            # We run this one final time so we get good errors 
            # Otherwise we would have swallowed all the reports of it actually
            # having gone wrong.
            test(*(arguments + falsifying_example))
        return wrapped_test
    return run_test_with_generator
