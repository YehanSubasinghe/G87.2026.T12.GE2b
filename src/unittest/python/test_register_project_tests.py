import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch

from uc3m_consulting import EnterpriseManager, EnterpriseManagementException
import uc3m_consulting.enterprise_manager as em_mod


class TestRegisterDocument(unittest.TestCase):  # pylint: disable=too-many-public-methods
    """Test cases for register_document."""

    _VALID_PID = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
    _VALID_FN = "abcd1234.pdf"

    def setUp(self):
        """Create a fresh temp directory for each test."""
        self.tmp_dir = tempfile.mkdtemp(prefix="ge2b_")
        self._prev_cwd = os.getcwd()
        os.chdir(self.tmp_dir)

    def tearDown(self):
        os.chdir(self._prev_cwd)
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ------------------------------------------------------------------ helpers
    def _write_json_file(self, name, content):
        """Write JSON (for dict/list) or a raw string; return the absolute path."""
        path = os.path.join(self.tmp_dir, name)
        with open(path, "w", encoding="utf-8") as file_handle:
            if isinstance(content, str):
                file_handle.write(content)
            else:
                json.dump(content, file_handle)
        return path

    def _valid_payload(self, name, filename=None):
        """Helper for happy-path / loop tests: write valid JSON and return path."""
        return self._write_json_file(
            name,
            {"PROJECT_ID": self._VALID_PID,
             "FILENAME": filename or self._VALID_FN})

    def _assert_not_json(self, filename, raw_content):
        """Shortcut: raw malformed content must produce the 'not JSON' EME."""
        path = self._write_json_file(filename, raw_content)
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("json", ctx.exception.message.lower())

    # =========================================================== structural P1
    def test_tc_m2_st_01_input_file_not_found(self):
        """P1 / TC_M2_04: input file does not exist on disk."""
        missing = os.path.join(self.tmp_dir, "nonexistent.json")
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(missing)
        self.assertIn("not found", ctx.exception.message.lower())

    # =========================================================== structural P2
    def test_tc_m2_st_02_file_is_not_json(self):
        """P2 / TC_M2_05: file exists but contents are not JSON."""
        path = self._write_json_file("test_notjson.json",
                                     "this is not json at all")
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("json", ctx.exception.message.lower())

    # =========================================================== structural P3
    def test_tc_m2_st_03_missing_project_id_key(self):
        """P3 / TC_M2_07: PAIR_PID deleted — only FILENAME key present."""
        path = self._write_json_file("test_no_pid.json",
                                     {"FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    def test_tc_m2_06_empty_object(self):
        """TC_M2_06: empty JSON object (PAIR_LIST deleted)."""
        path = self._write_json_file("test_empty.json", {})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    def test_tc_m2_08_missing_filename_key(self):
        """TC_M2_08: PAIR_FN deleted — only PROJECT_ID key present."""
        path = self._write_json_file("test_no_fn.json",
                                     {"PROJECT_ID": self._VALID_PID})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    def test_tc_m2_18_bad_pid_key_name(self):
        """TC_M2_18: PROJECT_ID key renamed to PROJECT."""
        path = self._write_json_file(
            "test_bad_key1.json",
            {"PROJECT": self._VALID_PID, "FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    def test_tc_m2_19_bad_fn_key_name(self):
        """TC_M2_19: FILENAME key renamed to FILE."""
        path = self._write_json_file(
            "test_bad_key2.json",
            {"PROJECT_ID": self._VALID_PID, "FILE": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("structure", ctx.exception.message.lower())

    # =========================================================== structural P4
    def test_tc_m2_st_04_empty_project_id(self):
        """P4 / TC_M2_09: PROJECT_ID value is empty string."""
        path = self._write_json_file(
            "test_empty_pid.json",
            {"PROJECT_ID": "", "FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_10_empty_filename(self):
        """TC_M2_10: FILENAME value is empty string."""
        path = self._write_json_file(
            "test_empty_fn.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": ""})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # =========================================================== structural P5
    def test_tc_m2_st_05_pid_non_hex_char(self):
        """P5 / TC_M2_22: PROJECT_ID contains non-hex character 'z'."""
        path = self._write_json_file(
            "test_nonhex_pid.json",
            {"PROJECT_ID": "z1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_20_pid_short(self):
        """TC_M2_20: PROJECT_ID is 31 chars (short by 1)."""
        path = self._write_json_file(
            "test_short_pid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d",
             "FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_21_pid_long(self):
        """TC_M2_21: PROJECT_ID is 33 chars (long by 1)."""
        path = self._write_json_file(
            "test_long_pid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4f",
             "FILENAME": self._VALID_FN})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ------------------------------------------ FILENAME regex (TC_M2_23..27)
    def test_tc_m2_23_filename_short_name(self):
        """TC_M2_23: filename NAME part is 5 chars (short by 3)."""
        path = self._write_json_file(
            "test_short_name.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": "abcde.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_24_filename_long_name(self):
        """TC_M2_24: filename NAME part is 10 chars (long by 2)."""
        path = self._write_json_file(
            "test_long_name.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": "abcd123456.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_25_filename_special_char(self):
        """TC_M2_25: filename NAME contains '@'."""
        path = self._write_json_file(
            "test_special_name.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": "abcd@234.pdf"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_26_filename_no_extension(self):
        """TC_M2_26: EXTENSION node deleted — no extension."""
        path = self._write_json_file(
            "test_no_ext.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": "abcd1234"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    def test_tc_m2_27_filename_bad_extension(self):
        """TC_M2_27: extension '.txt' is not in the allowed set."""
        path = self._write_json_file(
            "test_bad_ext.json",
            {"PROJECT_ID": self._VALID_PID, "FILENAME": "abcd1234.txt"})
        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("no valid values", ctx.exception.message.lower())

    # ============================================== structural P6 (happy path)
    def test_tc_m2_st_06_happy_path_pdf(self):
        """P6 / TC_M2_01: valid .pdf — returns SHA-256 and persists entry."""
        path = self._valid_payload("test_valid.json")
        signature = EnterpriseManager.register_document(path)
        self.assertIsInstance(signature, str)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")

        with open("all_documents.json", "r", encoding="utf-8") as file_handle:
            entries = json.load(file_handle)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["project_id"], self._VALID_PID)
        self.assertEqual(entries[0]["file_name"], self._VALID_FN)
        self.assertEqual(entries[0]["alg"], "SHA-256")
        self.assertEqual(entries[0]["typ"], "DOCUMENT")
        self.assertEqual(entries[0]["file_signature"], signature)

    def test_tc_m2_02_happy_path_docx(self):
        """TC_M2_02: valid .docx — returns SHA-256."""
        path = self._valid_payload("test_valid_docx.json", "abcd1234.docx")
        signature = EnterpriseManager.register_document(path)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")

    def test_tc_m2_03_happy_path_xlsx(self):
        """TC_M2_03: valid .xlsx — returns SHA-256."""
        path = self._valid_payload("test_valid_xlsx.json", "abcd1234.xlsx")
        signature = EnterpriseManager.register_document(path)
        self.assertRegex(signature, r"^[0-9a-f]{64}$")

    # =========================================================== structural P7
    def test_tc_m2_st_07_eme_is_propagated_unchanged(self):
        """P7: inner EME must propagate with its original message."""
        path = self._valid_payload("test_valid.json")
        original = EnterpriseManagementException("inner pre-check failed")
        with patch.object(em_mod, "ProjectDocument", side_effect=original):
            with self.assertRaises(EnterpriseManagementException) as ctx:
                EnterpriseManager.register_document(path)
        self.assertEqual(ctx.exception.message, "inner pre-check failed")

    # =========================================================== structural P8
    def test_tc_m2_st_08_generic_exception_is_wrapped(self):
        """P8: non-EME exception from inside the try block -> wrapped as EME."""
        path = self._valid_payload("test_valid.json")
        with patch.object(EnterpriseManager, "_save_document",
                          side_effect=IOError("disk full")):
            with self.assertRaises(EnterpriseManagementException) as ctx:
                EnterpriseManager.register_document(path)
        self.assertIn("internal processing error",
                      ctx.exception.message.lower())

    # ------------------------------- terminal deletions/duplications (11..17)
    def test_tc_m2_11_missing_open_brace(self):
        """TC_M2_11: opening brace deleted."""
        self._assert_not_json(
            "test_no_open.json",
            f'"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    def test_tc_m2_12_missing_close_brace(self):
        """TC_M2_12: closing brace deleted."""
        self._assert_not_json(
            "test_no_close.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"')

    def test_tc_m2_13_missing_comma(self):
        """TC_M2_13: comma between the two pairs deleted."""
        self._assert_not_json(
            "test_no_comma.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}""FILENAME":"{self._VALID_FN}"}}')

    def test_tc_m2_14_missing_colon_after_pid(self):
        """TC_M2_14: colon after PROJECT_ID deleted."""
        self._assert_not_json(
            "test_no_colon1.json",
            f'{{"PROJECT_ID""{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    def test_tc_m2_15_missing_colon_after_fn(self):
        """TC_M2_15: colon after FILENAME deleted."""
        self._assert_not_json(
            "test_no_colon2.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}","FILENAME""{self._VALID_FN}"}}')

    def test_tc_m2_16_duplicated_open_brace(self):
        """TC_M2_16: opening brace duplicated."""
        self._assert_not_json(
            "test_double_open.json",
            f'{{{{"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    def test_tc_m2_17_duplicated_comma(self):
        """TC_M2_17: comma duplicated."""
        self._assert_not_json(
            "test_extra_comma.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}",,"FILENAME":"{self._VALID_FN}"}}')

    # ---------------------------------------------- loop boundary cases (L1-L3)
    def test_l1_zero_iterations_creates_file(self):
        """L1: all_documents.json does not exist — created with one entry."""
        path = self._valid_payload("p1.json")
        self.assertFalse(os.path.exists("all_documents.json"))
        EnterpriseManager.register_document(path)
        with open("all_documents.json", "r", encoding="utf-8") as file_handle:
            entries = json.load(file_handle)
        self.assertEqual(len(entries), 1)

    def test_l2_one_existing_entry_appends_second(self):
        """L2: file already contains one entry — second is appended."""
        EnterpriseManager.register_document(self._valid_payload("p1.json"))
        EnterpriseManager.register_document(
            self._valid_payload("p2.json", "zzzz9999.docx"))
        with open("all_documents.json", "r", encoding="utf-8") as file_handle:
            entries = json.load(file_handle)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]["file_name"], "zzzz9999.docx")

    def test_l3_multiple_existing_entries_appends_one_more(self):
        """L3: file contains n>1 entries — one more is appended."""
        for i in range(5):
            EnterpriseManager.register_document(
                self._valid_payload(f"p{i}.json", f"file{i:04d}.pdf"))
        EnterpriseManager.register_document(
            self._valid_payload("plast.json", "lastfile.xlsx"))
        with open("all_documents.json", "r", encoding="utf-8") as file_handle:
            entries = json.load(file_handle)
        self.assertEqual(len(entries), 6)
        self.assertEqual(entries[-1]["file_name"], "lastfile.xlsx")


if __name__ == "__main__":
    unittest.main()
