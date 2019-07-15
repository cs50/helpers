if __name__ == "__main__":
    import doctest
    import helpers
    import inspect
    for mod in dir(helpers):
        if inspect.ismodule(getattr(helpers, mod)):
            doctest.testmod(getattr(helpers, mod))

