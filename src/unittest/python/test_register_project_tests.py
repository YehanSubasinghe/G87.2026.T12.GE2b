"""Tests for EnterpriseManager.register_document (CM-FR-01-O2)."""
import json
import os
import shutil
import tempfile
import unittest

from uc3m_consulting import EnterpriseManager, EnterpriseManagementException


class TestRegisterDocument(unittest.TestCase):
    """Test cases for register_document, following GE2b syntactic + structural analysis."""

    def setUp(self):
        """Create a fresh temp directory for each test."""
        self.tmp_dir = tempfile.mkdtemp(prefix="ge2b_")
        # Switch cwd so all_documents.json is written inside the temp dir
        self._prev_cwd = os.getcwd()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self._prev_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _write_json_file(self, name: str, content) -> str:
        """Write arbitrary content (dict/list for JSON, str for raw) and return the path."""
        path = os.path.join(self.tmp_dir, name)
        with open(path, "w", encoding="utf-8") as f:
            if isinstance(content, str):
                f.write(content)
            else:
                json.dump(content, f)
        return path

    # ----- Path P1 / TC_M2_04 / TC_M2_ST_01 -----
    def test_tc_m2_st_01_input_file_not_found(self):
        """P1: input file does not exist on disk."""
        missing_path = os.path.join(self.tmp_dir, "nonexistent.json")
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(missing_path)
        self.assertIn("not found", ctx.exception.message.lower())

    def test_tc_m2_st_02_file_is_not_json(self):
        """P2: file exists but its contents cannot be parsed as JSON."""
        path = self._write_json_file("test_notjson.json", "this is not json at all")
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("json", ctx.exception.message.lower())


if __name__ == "__main__":
    unittest.main()
