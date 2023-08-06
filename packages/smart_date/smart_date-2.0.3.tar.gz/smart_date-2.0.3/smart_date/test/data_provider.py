def data_provider(fn_data_provider):
    """
    Data provider decorator, allows another callable to provide
    the data for the test
    """
    def test_decorator(fnct):
        # pylint: disable=W0613
        def repl(self, *args):
            for i in fn_data_provider():
                try:
                    fnct(self, *i)
                except AssertionError:
                    print "Assertion error caught with data set ", i
                    raise
        return repl
    return test_decorator