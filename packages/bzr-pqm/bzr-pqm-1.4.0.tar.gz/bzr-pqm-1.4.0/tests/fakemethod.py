__metaclass__ = type

class FakeMethod:
    """Catch any function or method call, and record the fact."""

    def __init__(self, result=None, failure=None):
        """Set up a fake function or method.

        :param result: Value to return.
        :param failure: Exception to raise.
        """
        self.result = result
        self.failure = failure

    def __call__(self, *args, **kwargs):
        """Catch an invocation to the method."""

        if self.failure is None:
            return self.result
        else:
            raise self.failure
