class RepositoryException(Exception):
    """Base repository exception type."""


class RepositoryConflictException(RepositoryException):
    """Exception for data integrity errors."""


class RepositoryNotFoundException(RepositoryException):
    """Raised when a method referencing a specific instance by identity is
    called and no instance with that identity exists."""
