class EndpointResponseException(Exception):
    """Raised if endpoint doesn't respond."""

    pass


class DoNotSendToBotException(Exception):
    """
    Exception that should be logged but not sent.
    Basicly for use when bot fails.
    """

    pass

