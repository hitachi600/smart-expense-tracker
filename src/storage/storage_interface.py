"""
Storage Abstract Base Class.
Demonstrates: Abstract Base Classes (abc.ABC, @abstractmethod), Polymorphism, Interface Design.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class StorageInterface(ABC):
    """
    Abstract contract for persistence backends (JSON, CSV, Database, etc.).
    Ensures that any storage adapter implements load, save, and backup capabilities.
    """

    @abstractmethod
    def load(self) -> List[Dict[str, Any]]:
        """
        Loads expense records from persistence medium.

        :return: List of raw expense dictionary objects
        :raises StorageError: If loading fails
        """
        pass

    @abstractmethod
    def save(self, data: List[Dict[str, Any]]) -> bool:
        """
        Persists expense records to storage medium.

        :param data: List of expense dictionaries
        :return: True if save succeeded
        :raises StorageError: If saving fails
        """
        pass

    @abstractmethod
    def create_backup(self) -> str:
        """
        Creates a timestamped snapshot/backup of the current database.

        :return: Path to the backup file created
        :raises StorageError: If backup fails
        """
        pass
