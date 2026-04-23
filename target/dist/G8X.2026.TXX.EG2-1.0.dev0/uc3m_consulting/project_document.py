"""Contains the class ProjectDocument"""
from datetime import datetime, timezone
import hashlib


class ProjectDocument:
    """Represents a document registered against an enterprise project."""

    def __init__(self, project_id: str, file_name: str):
        self.__alg = "SHA-256"
        self.__typ = "DOCUMENT"
        self.__project_id = project_id
        self.__file_name = file_name
        justnow = datetime.now(timezone.utc)
        self.__register_date = datetime.timestamp(justnow)

    def to_json(self):
        """Returns the object data in json format."""
        return {"alg": self.__alg,
                "typ": self.__typ,
                "project_id": self.__project_id,
                "file_name": self.__file_name,
                "register_date": self.__register_date,
                "file_signature": self.file_signature}

    def __signature_string(self):
        """Composes the string encoded with SHA-256 to produce the signature."""
        return ("{alg:" + str(self.__alg) +
                ", typ:" + str(self.__typ) +
                ", project_id:" + str(self.__project_id) +
                ", file_name:" + str(self.__file_name) + "}")

    @property
    def project_id(self):
        """Project identifier (MD5 from Method 1)."""
        return self.__project_id

    @project_id.setter
    def project_id(self, value):
        self.__project_id = value

    @property
    def file_name(self):
        """Name of the registered file (name + extension)."""
        return self.__file_name

    @file_name.setter
    def file_name(self, value):
        self.__file_name = value

    @property
    def register_date(self):
        """UTC timestamp of the registration."""
        return self.__register_date

    @register_date.setter
    def register_date(self, value):
        self.__register_date = value

    @property
    def file_signature(self):
        """SHA-256 signature in hexadecimal format."""
        return hashlib.sha256(self.__signature_string().encode()).hexdigest()