"""Notario core exceptions module."""


class NotarioError(Exception):
    """Generic errors."""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class NotarioConfigError(NotarioError):
    pass


class NotarioRuntimeError(NotarioError):
    pass


class NotarioArgumentError(NotarioError):
    pass
