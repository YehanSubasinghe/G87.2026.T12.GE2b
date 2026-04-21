"""Tests for the register_document method"""
import os
import unittest
from uc3m_consulting import EnterpriseManager, EnterpriseManagementException


class TestRegisterDocument(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for register_document using Syntactic Analysis"""

    VALID_PID = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
    VALID_NAME = "abcd1234"
    JSON_FILE = "all_documents.json"

    def setUp(self):
        """Clean up before each test"""
        if os.path.exists(self.JSON_FILE):
            os.remove(self.JSON_FILE)

    def tearDown(self):
        """Clean up after each test"""
        if os.path.exists(self.JSON_FILE):
            os.remove(self.JSON_FILE)
        for f in os.listdir("."):
            if f.startswith("test_") and f.endswith(".json"):
                os.remove(f)

    def _write_input(self, filename, content):
        """Helper to write a test input file"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    # ── VALID ──────────────────────────────────────────────────────────────
    def test_tc_m2_01_valid_pdf(self):
        """TC_M2_01 - Valid JSON input with .pdf extension"""
        self._write_input("test_valid.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"}}')
        result = EnterpriseManager.register_document("test_valid.json")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)
        self.assertRegex(result, r'^[0-9a-f]{64}$')
        self.assertTrue(os.path.exists(self.JSON_FILE))

    def test_tc_m2_02_valid_docx(self):
        """TC_M2_02 - Valid JSON input with .docx extension"""
        self._write_input("test_valid_docx.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.docx"}}')
        result = EnterpriseManager.register_document("test_valid_docx.json")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)
        self.assertRegex(result, r'^[0-9a-f]{64}$')

    def test_tc_m2_03_valid_xlsx(self):
        """TC_M2_03 - Valid JSON input with .xlsx extension"""
        self._write_input("test_valid_xlsx.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.xlsx"}}')
        result = EnterpriseManager.register_document("test_valid_xlsx.json")
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 64)
        self.assertRegex(result, r'^[0-9a-f]{64}$')

    # ── FILE LEVEL ────────────────────────────────────────────────────────
    def test_tc_m2_04_file_not_found(self):
        """TC_M2_04 - Input file does not exist (node 1 deleted)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("nonexistent.json")

    def test_tc_m2_05_file_not_json(self):
        """TC_M2_05 - File is not JSON formatted (node 2 modified)"""
        self._write_input("test_notjson.json", "this is not json at all")
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_notjson.json")

    # ── NT DELETIONS ──────────────────────────────────────────────────────
    def test_tc_m2_06_empty_object(self):
        """TC_M2_06 - Empty JSON object, PAIR_LIST deleted (node 4)"""
        self._write_input("test_empty.json", "{}")
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_empty.json")

    def test_tc_m2_07_missing_project_id_pair(self):
        """TC_M2_07 - PROJECT_ID pair missing (node 6 deleted)"""
        self._write_input("test_no_pid.json", '{"FILENAME": "abcd1234.pdf"}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_pid.json")

    def test_tc_m2_08_missing_filename_pair(self):
        """TC_M2_08 - FILENAME pair missing (node 8 deleted)"""
        self._write_input("test_no_fn.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_fn.json")

    def test_tc_m2_09_empty_pid_value(self):
        """TC_M2_09 - PROJECT_ID value is empty (node 11 deleted)"""
        self._write_input("test_empty_pid.json",
            '{"PROJECT_ID": "", "FILENAME": "abcd1234.pdf"}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_empty_pid.json")

    def test_tc_m2_10_empty_filename_value(self):
        """TC_M2_10 - FILENAME value is empty (node 14 deleted)"""
        self._write_input("test_empty_fn.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": ""}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_empty_fn.json")

    # ── T DELETIONS ───────────────────────────────────────────────────────
    def test_tc_m2_11_missing_opening_brace(self):
        """TC_M2_11 - Missing opening brace (node 3 deleted)"""
        self._write_input("test_no_open.json",
            f'"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_open.json")

    def test_tc_m2_12_missing_closing_brace(self):
        """TC_M2_12 - Missing closing brace (node 5 deleted)"""
        self._write_input("test_no_close.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_close.json")

    def test_tc_m2_13_missing_comma(self):
        """TC_M2_13 - Missing comma between pairs (node 7 deleted)"""
        self._write_input("test_no_comma.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}" "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_comma.json")

    def test_tc_m2_14_missing_colon_pid(self):
        """TC_M2_14 - Missing colon after PROJECT_ID key (node 10 deleted)"""
        self._write_input("test_no_colon1.json",
            f'{{"PROJECT_ID" "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_colon1.json")

    def test_tc_m2_15_missing_colon_filename(self):
        """TC_M2_15 - Missing colon after FILENAME key (node 13 deleted)"""
        self._write_input("test_no_colon2.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME" "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_colon2.json")

    # ── T DUPLICATIONS ────────────────────────────────────────────────────
    def test_tc_m2_16_duplicate_opening_brace(self):
        """TC_M2_16 - Duplicate opening brace (node 3 duplicated)"""
        self._write_input("test_double_open.json",
            f'{{{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_double_open.json")

    def test_tc_m2_17_duplicate_comma(self):
        """TC_M2_17 - Duplicate comma between pairs (node 7 duplicated)"""
        self._write_input("test_extra_comma.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}",, "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_extra_comma.json")

    # ── T MODIFICATIONS ───────────────────────────────────────────────────
    def test_tc_m2_18_wrong_key_project_id(self):
        """TC_M2_18 - Wrong key instead of PROJECT_ID (node 9 modified)"""
        self._write_input("test_bad_key1.json",
            f'{{"PROJECT": "{self.VALID_PID}", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_bad_key1.json")

    def test_tc_m2_19_wrong_key_filename(self):
        """TC_M2_19 - Wrong key instead of FILENAME (node 12 modified)"""
        self._write_input("test_bad_key2.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILE": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_bad_key2.json")

    def test_tc_m2_20_pid_too_short(self):
        """TC_M2_20 - PROJECT_ID 31 hex chars (node 17 modified)"""
        self._write_input("test_short_pid.json",
            f'{{"PROJECT_ID": "{self.VALID_PID[:-1]}", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_short_pid.json")

    def test_tc_m2_21_pid_too_long(self):
        """TC_M2_21 - PROJECT_ID 33 hex chars (node 17 modified)"""
        self._write_input("test_long_pid.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}a", "FILENAME": "abcd1234.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_long_pid.json")

    def test_tc_m2_22_pid_non_hex(self):
        """TC_M2_22 - PROJECT_ID contains non-hex char (node 17 modified)"""
        self._write_input("test_nonhex_pid.json",
            '{"PROJECT_ID": "z1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4", '
            '"FILENAME": "abcd1234.pdf"}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_nonhex_pid.json")

    def test_tc_m2_23_name_too_short(self):
        """TC_M2_23 - FILENAME NAME 5 chars (node 20 modified)"""
        self._write_input("test_short_name.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcde.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_short_name.json")

    def test_tc_m2_24_name_too_long(self):
        """TC_M2_24 - FILENAME NAME 10 chars (node 20 duplicated)"""
        self._write_input("test_long_name.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd123456.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_long_name.json")

    def test_tc_m2_25_name_special_char(self):
        """TC_M2_25 - FILENAME NAME contains special char (node 20 modified)"""
        self._write_input("test_special_name.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "ab@cd123.pdf"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_special_name.json")

    def test_tc_m2_26_missing_extension(self):
        """TC_M2_26 - FILENAME missing extension (node 19 deleted)"""
        self._write_input("test_no_ext.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_no_ext.json")

    def test_tc_m2_27_invalid_extension(self):
        """TC_M2_27 - FILENAME extension not allowed (node 21 modified)"""
        self._write_input("test_bad_ext.json",
            f'{{"PROJECT_ID": "{self.VALID_PID}", "FILENAME": "abcd1234.txt"}}')
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_document("test_bad_ext.json")


if __name__ == "__main__":
    unittest.main()
