"""Module: enterprise_manager. Contains the EnterpriseManager class."""
import os
from uc3m_consulting.enterprise_management_exception import (
EnterpriseManagementException,
)

class EnterpriseManager:
    """Provides the methods for managing enterprise projects and their documents."""

    def __init__(self):
        pass

    @staticmethod
    def validate_cif(cif: str):
        """Returns True if the CIF received is a valid Spanish CIF, False otherwise."""
        return True

    @staticmethod
    def register_document(input_file: str):
        """..."""
        if not os.path.exists(input_file):
            raise EnterpriseManagementException("Input file not found")
        return None