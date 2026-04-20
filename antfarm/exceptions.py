"""
Custom exception types for the ant farm.

All exceptions inherit from ``AntFarm Error`` so callers can catch all errors
in one clause if they want to.
"""


class AntFarmError(Exception):
    """Base class for all ant farm exceptions."""


class OutOfBoundsError(AntFarmError):
    """Raised when a coordinate falls outside the world grid."""


class TileNotDiggableError(AntFarmError):
    """Raised when something tries to dig a tile that can't be dug."""


