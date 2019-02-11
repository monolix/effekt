class EventNotFound(BaseException):
    """No events found with this name."""

class TooLowPriority(BaseException):
    """Cannot have priority less than 0."""