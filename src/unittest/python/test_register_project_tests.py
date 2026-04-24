"""Tests for EnterpriseManager.register_document (CM-FR-01-O2)."""
import json
import os
import re
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

    # ----- Path P3 / TC_M2_ST_03 / TC_M2_07 -----
    def test_tc_m2_st_03_missing_project_id_key(self):
        """P3: JSON parses but PROJECT_ID key is missing."""
        path = self._write_json_file(
            "test_no_pid.json", {"FILENAME": "abcd1234.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # ----- TC_M2_06: empty JSON object (PAIR_LIST deleted) -----
    def test_tc_m2_06_empty_object(self):
        path = self._write_json_file("test_empty.json", {})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # ----- TC_M2_08: PAIR_FN deleted (no FILENAME key) -----
    def test_tc_m2_08_missing_filename_key(self):
        path = self._write_json_file(
            "test_no_fn.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # ----- TC_M2_18: PROJECT_ID key renamed to "PROJECT" -----
    def test_tc_m2_18_bad_pid_key_name(self):
        path = self._write_json_file(
            "test_bad_key1.json",
            {"PROJECT": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # ----- TC_M2_19: FILENAME key renamed to "FILE" -----
    def test_tc_m2_19_bad_fn_key_name(self):
        path = self._write_json_file(
            "test_bad_key2.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILE": "abcd1234.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # ----- Path P4 / TC_M2_ST_04 / TC_M2_09 -----
    def test_tc_m2_st_04_empty_project_id(self):
        """P4: structure valid but PROJECT_ID value is empty string."""

        path = self._write_json_file(
            "test_empty_pid.json",
            {"PROJECT_ID": "", "FILENAME": "abcd1234.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_10 -----
    def test_tc_m2_10_empty_filename(self):
        path = self._write_json_file(
            "test_empty_fn.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": ""})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- Path P5 / TC_M2_ST_05 / TC_M2_22 -----
    def test_tc_m2_st_05_pid_non_hex_char(self):
        """P5: PROJECT_ID contains a non-hex character."""

        path = self._write_json_file(
            "test_nonhex_pid.json",
            {"PROJECT_ID": "z1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_20: 31 hex chars -----
    def test_tc_m2_20_pid_short(self):
        path = self._write_json_file(
            "test_short_pid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d",
             "FILENAME": "abcd1234.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_21: 33 hex chars -----
    def test_tc_m2_21_pid_long(self):
        path = self._write_json_file(
            "test_long_pid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4f",
             "FILENAME": "abcd1234.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_23: NAME part 5 chars -----
    def test_tc_m2_23_filename_short_name(self):
        path = self._write_json_file(
            "test_short_name.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcde.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_24: NAME part 10 chars -----
    def test_tc_m2_24_filename_long_name(self):
        path = self._write_json_file(
            "test_long_name.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd123456.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_25: NAME contains "@" -----
    def test_tc_m2_25_filename_special_char(self):
        path = self._write_json_file(
            "test_special_name.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd@234.pdf"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_26: no extension -----
    def test_tc_m2_26_filename_no_extension(self):
        path = self._write_json_file(
            "test_no_ext.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- TC_M2_27: extension .txt -----
    def test_tc_m2_27_filename_bad_extension(self):
        path = self._write_json_file(
            "test_bad_ext.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.txt"})

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ----- Path P6 / TC_M2_ST_06 / TC_M2_01 -----
    def test_tc_m2_st_06_happy_path_pdf(self):
        """P6: valid input, .pdf extension — returns 64-char SHA-256."""

        path = self._write_json_file(
            "test_valid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.pdf"})
        signature = EnterpriseManager.register_document(path)
        self.assertIsInstance(signature, str)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")
        # and all_documents.json should now exist with one entry
        with open(os.path.join(self.tmp_dir, "all_documents.json"),
                  "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["project_id"],
                         "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4")
        self.assertEqual(entries[0]["file_name"], "abcd1234.pdf")
        self.assertEqual(entries[0]["alg"], "SHA-256")
        self.assertEqual(entries[0]["typ"], "DOCUMENT")
        self.assertEqual(entries[0]["file_signature"], signature)

    # ----- TC_M2_02 -----
    def test_tc_m2_02_happy_path_docx(self):
        path = self._write_json_file(
            "test_valid_docx.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.docx"})

        signature = EnterpriseManager.register_document(path)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")

    # ----- TC_M2_03 -----
    def test_tc_m2_03_happy_path_xlsx(self):
        path = self._write_json_file(
            "test_valid_xlsx.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.xlsx"})

        signature = EnterpriseManager.register_document(path)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")

if __name__ == "__main__":
    unittest.main()
