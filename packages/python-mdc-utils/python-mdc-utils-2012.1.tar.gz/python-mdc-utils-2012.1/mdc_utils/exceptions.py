"""Dragon warnings
"""


class ScraperError(RuntimeError):
    """Base exception for Mock Draft Central exceptions
    """


class AuthError(ScraperError, ValueError):
    """Could not authenticate with Mock Draft Central.
    """


class FormatterError(ScraperError, ValueError):
    """Could not format the results as requested by the user.
    """
