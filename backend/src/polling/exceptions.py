"""
Polling Engine Exceptions

Custom exception classes for polling engine operations.
"""


class PollingException(Exception):
    """Base exception for all polling-related errors"""
    pass


class PollingGroupNotFoundError(PollingException):
    """Raised when a polling group cannot be found"""
    pass


class PollingGroupAlreadyRunningError(PollingException):
    """Raised when attempting to start an already running polling group"""
    pass


class PollingGroupNotRunningError(PollingException):
    """Raised when attempting to stop a non-running polling group"""
    pass


class MaxPollingGroupsReachedError(PollingException):
    """Raised when maximum number of polling groups (10) is reached"""
    pass


class QueueFullError(PollingException):
    """Raised when the data queue is full and cannot accept more data"""
    pass


class PollingThreadError(PollingException):
    """Raised when a polling thread encounters an unrecoverable error"""
    pass


class InvalidPollingModeError(PollingException):
    """Raised when an invalid polling mode is specified"""
    pass


class ConfigurationError(PollingException):
    """Raised when polling group configuration is invalid"""
    pass
