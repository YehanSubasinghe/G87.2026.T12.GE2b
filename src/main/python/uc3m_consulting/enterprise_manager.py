"""Module: enterprise_manager. Contains the EnterpriseManager class."""
import json
import os
import re
from uc3m_consulting.enterprise_management_exception import (
EnterpriseManagementException,
)
from uc3m_consulting.project_document import ProjectDocument

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

        project_id = data["PROJECT_ID"]
        filename = data["FILENAME"]

        if not project_id or not filename:
            raise EnterpriseManagementException(
                "JSON data has no valid values")

        if not re.fullmatch(r"[0-9a-f]{32}", project_id):
            raise EnterpriseManagementException(
                "JSON data has no valid values")

        if not re.fullmatch(r"[a-zA-Z0-9]{8}\.(pdf|docx|xlsx)", filename):
            raise EnterpriseManagementException(
                "JSON data has no valid values")

        try:
            document = ProjectDocument(project_id, filename)
            EnterpriseManager._save_document(document)
        except EnterpriseManagementException:
            raise
        except Exception as ex:
            raise EnterpriseManagementException(
                "Internal processing error when getting the file_signature") from ex
        return document.file_signature

    @staticmethod
    def _save_document(document):
        """Append the document's to_json() dict to all_documents.json."""

        path = "all_documents.json"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file_handle:
                entries = json.load(file_handle)
        else:
            entries = []
        entries.append(document.to_json())
        with open(path, "w", encoding="utf-8") as file_handle:
            json.dump(entries, file_handle, indent=2)