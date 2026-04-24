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

    # ----- Path P8 / TC_M2_ST_08 -----
    def test_tc_m2_st_08_generic_exception_is_wrapped(self):
        """P8: non-EME exception from inside the try block -> wrapped as EME."""

        path = self._write_json_file(
            "test_valid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.pdf"})
        with patch.object(EnterpriseManager, "_save_document",
                          side_effect=IOError("disk full")):
            with self.assertRaises(EnterpriseManagementException) as ctx:
                EnterpriseManager.register_document(path)
        self.assertIn("internal processing error",
                      ctx.exception.message.lower())

    # ----- Path P7 / TC_M2_ST_07 -----
    def test_tc_m2_st_07_eme_is_propagated_unchanged(self):
        """P7: inner EME must propagate with its original message, not be wrapped."""

        path = self._write_json_file(
            "test_valid.json",
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": "abcd1234.pdf"})
        original = EnterpriseManagementException("inner pre-check failed")
        # Patch ProjectDocument inside the EM namespace (imported there)
        import uc3m_consulting.enterprise_manager as em_mod
        with patch.object(em_mod, "ProjectDocument",
                          side_effect=original):
            with self.assertRaises(EnterpriseManagementException) as ctx:
                EnterpriseManager.register_document(path)
        # original message preserved, NOT replaced by the generic wrapper
        self.assertEqual(ctx.exception.message, "inner pre-check failed")

    _VALID_PID = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
    _VALID_FN = "abcd1234.pdf"

    def _assert_not_json(self, filename, raw_content):
        path = self._write_json_file(filename, raw_content)

        with self.assertRaises(EnterpriseManagementException) as ctx:
            EnterpriseManager.register_document(path)
        self.assertIn("json", ctx.exception.message.lower())

    # TC_M2_11 — opening brace deleted
    def test_tc_m2_11_missing_open_brace(self):
        self._assert_not_json(
            "test_no_open.json",
            f'"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    # TC_M2_12 — closing brace deleted
    def test_tc_m2_12_missing_close_brace(self):
        self._assert_not_json(
            "test_no_close.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"')

    # TC_M2_13 — comma between pairs deleted
    def test_tc_m2_13_missing_comma(self):
        self._assert_not_json(
            "test_no_comma.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}""FILENAME":"{self._VALID_FN}"}}')

    # TC_M2_14 — colon after PROJECT_ID deleted
    def test_tc_m2_14_missing_colon_after_pid(self):
        self._assert_not_json(
            "test_no_colon1.json",
            f'{{"PROJECT_ID""{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    # TC_M2_15 — colon after FILENAME deleted
    def test_tc_m2_15_missing_colon_after_fn(self):
        self._assert_not_json(
            "test_no_colon2.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}","FILENAME""{self._VALID_FN}"}}')

    # TC_M2_16 — opening brace duplicated
    def test_tc_m2_16_duplicated_open_brace(self):
        self._assert_not_json(
            "test_double_open.json",
            f'{{{{"PROJECT_ID":"{self._VALID_PID}","FILENAME":"{self._VALID_FN}"}}')

    # TC_M2_17 — comma duplicated
    def test_tc_m2_17_duplicated_comma(self):
        self._assert_not_json(
            "test_extra_comma.json",
            f'{{"PROJECT_ID":"{self._VALID_PID}",,"FILENAME":"{self._VALID_FN}"}}')

    def _valid_payload(self, name, filename="abcd1234.pdf"):
        """Helper: write a valid JSON file in the temp dir and return its path."""

        return self._write_json_file(
            name,
            {"PROJECT_ID": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
             "FILENAME": filename})

    # ----- L1: all_documents.json does not exist -----
    def test_l1_zero_iterations_creates_file(self):
        path = self._valid_payload("p1.json")

        self.assertFalse(os.path.exists("all_documents.json"))
        EnterpriseManager.register_document(path)
        with open("all_documents.json", "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 1)

    # ----- L2: file already contains one entry -----
    def test_l2_one_existing_entry_appends_second(self):
        EnterpriseManager.register_document(self._valid_payload("p1.json"))

        EnterpriseManager.register_document(
            self._valid_payload("p2.json", "zzzz9999.docx"))
        with open("all_documents.json", "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[1]["file_name"], "zzzz9999.docx")

    # ----- L3: file already contains n > 1 entries -----
    def test_l3_multiple_existing_entries_appends_one_more(self):
        for i in range(5):
            EnterpriseManager.register_document(
                self._valid_payload(f"p{i}.json",
                                    f"file{i:04d}.pdf"))

        EnterpriseManager.register_document(
            self._valid_payload("plast.json", "lastfile.xlsx"))
        with open("all_documents.json", "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 6)
        self.assertEqual(entries[-1]["file_name"], "lastfile.xlsx")

if __name__ == "__main__":
    unittest.main()
