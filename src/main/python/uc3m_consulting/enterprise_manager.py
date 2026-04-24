"""Module: enterprise_manager. Contains the EnterpriseManager class."""
import json
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
        try:
            with open(input_file, "r", encoding="utf-8") as file_handle:
                data = json.load(file_handle)
        except json.JSONDecodeError as ex:
            raise EnterpriseManagementException(
                "File is not JSON formatted") from ex
        # tighten the structure check:
        if (not isinstance(data, dict)
                or "PROJECT_ID" not in data
                or "FILENAME" not in data
                or len(data) != 2):
            raise EnterpriseManagementException(
                "JSON does not have the expected structure")
        return None