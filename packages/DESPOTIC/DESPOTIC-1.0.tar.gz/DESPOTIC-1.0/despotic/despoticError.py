########################################################################
# class despoticError
#
# A generic exception class for DESPOTIC-specific errors
########################################################################

class despoticError(Exception):
    """Exception raised by DESPOTIC-specific errors.

    Attributes
    ----------
    __init__ -- initialize
    """

    def __init__(self, message):
        Exception.__init__(self, message)
        self.message = message
