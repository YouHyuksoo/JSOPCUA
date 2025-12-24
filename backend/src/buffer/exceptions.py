"""
Buffer Exceptions

Custom exceptions for buffer operations.
"""


class BufferError(Exception):
    """Base exception for buffer-related errors"""
    pass


class BufferFullError(BufferError):
    """Raised when attempting to add to a full buffer that doesn't allow overflow"""
    pass


class BufferEmptyError(BufferError):
    """Raised when attempting to read from an empty buffer"""
    pass


class BufferConsumerError(BufferError):
    """Raised when buffer consumer encounters an error"""
    pass
