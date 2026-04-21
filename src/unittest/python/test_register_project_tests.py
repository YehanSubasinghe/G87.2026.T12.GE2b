"""class for testing the regsiter_order method"""
import os
import unittest
from unittest.mock import patch
from datetime import datetime
from uc3m_consulting import EnterpriseManager, EnterpriseManagementException


class TestRegisterProject(unittest.TestCase): # pylint: disable=too-many-public-methods
    """Test cases for register_project using EC and BV analysis"""

    VALID_CIF = "B12345674"
    VALID_ACR = "PROJ1"
    VALID_DESC = "ValidProj01"
    VALID_DEPT = "HR"
    VALID_DATE = "15/06/2026"
    VALID_BUD = 50000.00
    JSON_FILE = "corporate_operations.json"

    def setUp(self):
        """Remove JSON file before each test"""
        if os.path.exists(self.JSON_FILE):
            os.remove(self.JSON_FILE)

    def tearDown(self):
        """Remove JSON file after each test"""
        if os.path.exists(self.JSON_FILE):
            os.remove(self.JSON_FILE)

    # ── VALID ──────────────────────────────────────────────────────────────
    def test_tc1_valid_all_ecs_bvv_lower_bounds(self):
        """TC1 - Valid case covering all ECs and lower BVVs"""
        result = EnterpriseManager.register_project(
            "B12345674", "PROJ1", "ValidProj01", "HR", "15/06/2026", 50000.00)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)
        self.assertRegex(result, r'^[0-9a-f]{32}$')

    def test_tc2_valid_finance_acr6_desc11_bvv(self):
        """TC2 - Valid FINANCE, acronym len=6, desc len=11, DD=02 MM=02 YYYY=2027"""
        result = EnterpriseManager.register_project(
            "B12345674", "PROJ12", "ValidProject01", "FINANCE", "02/02/2027", 50000.01)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)
        self.assertRegex(result, r'^[0-9a-f]{32}$')

    def test_tc3_valid_legal_acr9_desc29_bvv(self):
        """TC3 - Valid LEGAL, acronym len=9, desc len=29, DD=30 MM=11"""
        result = EnterpriseManager.register_project(
            "B12345674", "PROJ12345", "12345678901234567890123456789",
            "LEGAL", "30/11/2027", 999999.99)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)
        self.assertRegex(result, r'^[0-9a-f]{32}$')

    def test_tc4_valid_logistics_acr10_desc30_bvv_upper(self):
        """TC4 - Valid LOGISTICS, acronym len=10, desc len=30, DD=31 MM=12"""
        result = EnterpriseManager.register_project(
            "B12345674", "PROJ123456", "123456789012345678901234567890",
            "LOGISTICS", "31/12/2027", 1000000.00)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)
        self.assertRegex(result, r'^[0-9a-f]{32}$')

    @patch("uc3m_consulting.enterprise_manager.EnterpriseManager._get_today")
    def test_tc5_valid_yyyy_2025_mock_datetime(self, mock_today):
        """TC5 - Valid YYYY=2025, mocking _get_today to 2024-12-31"""
        mock_today.return_value = datetime(2024, 12, 31)
        result = EnterpriseManager.register_project(
            "B12345674", "PROJ1A", "ValidProj05",
            "HR", "01/01/2025", 500000.00)
        self.assertIsInstance(result, str)
        self.assertEqual(len(result), 32)

    # ── INVALID – company_cif ──────────────────────────────────────────────
    def test_tc6_invalid_cif_length_8(self):
        """TC6 - CIF length=8, lower boundary -1 (ECNV3, BVNV1)"""
        with self.assertRaisesRegex(EnterpriseManagementException, "length must be 9"):
            EnterpriseManager.register_project(
                "B1234567", self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc7_invalid_cif_length_10(self):
        """TC7 - CIF length=10, upper boundary +1 (ECNV4, BVNV2)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                "B123456789", self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc8_invalid_cif_first_char_not_letter(self):
        """TC8 - CIF first char is not a letter (ECNV5)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                "112345674", self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc9_invalid_cif_middle_not_digits(self):
        """TC9 - CIF middle 7 chars not all digits (ECNV6)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                "BA2345674", self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc10_invalid_cif_fails_algorithm(self):
        """TC10 - CIF fails control digit validation (ECNV2, ECNV7)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                "B12345670", self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    # ── INVALID – project_acronym ──────────────────────────────────────────
    def test_tc11_invalid_acronym_length_4(self):
        """TC11 - Acronym length=4, lower boundary -1 (ECNV9, BVNV3)"""
        with self.assertRaisesRegex(EnterpriseManagementException, "length must be between 5 and 10"):
            EnterpriseManager.register_project(
                self.VALID_CIF, "PRJ1", self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc12_invalid_acronym_length_11(self):
        """TC12 - Acronym length=11, upper boundary +1 (ECNV10, BVNV4)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, "PROJ1234567", self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc13_invalid_acronym_lowercase(self):
        """TC13 - Acronym contains invalid characters (ECNV11)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, "proj1", self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    # ── INVALID – project_description ─────────────────────────────────────
    def test_tc14_invalid_desc_length_9(self):
        """TC14 - Description length=9, lower boundary -1 (ECNV13, BVNV5)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, "123456789",
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    def test_tc15_invalid_desc_length_31(self):
        """TC15 - Description length=31, upper boundary +1 (ECNV14, BVNV6)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, "1234567890123456789012345678901",
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

    # ── INVALID – department ──────────────────────────────────────────────
    def test_tc16_invalid_department_not_allowed(self):
        """TC16 - Department not in allowed list (ECNV16)"""
        with self.assertRaisesRegex(EnterpriseManagementException, "must be HR"):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                "MARKETING", self.VALID_DATE, self.VALID_BUD)

    # ── INVALID – date ────────────────────────────────────────────────────
    def test_tc17_invalid_date_wrong_format(self):
        """TC17 - Date format not DD/MM/YYYY (ECNV17)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "2027-06-15", self.VALID_BUD)

    def test_tc18_invalid_date_dd_00(self):
        """TC18 - DD=00, lower boundary -1 (ECNV18, BVNV7)"""
        with self.assertRaisesRegex(EnterpriseManagementException, "DD must be between 01 and 31"):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "00/06/2027", self.VALID_BUD)

    def test_tc19_invalid_date_dd_32(self):
        """TC19 - DD=32, upper boundary +1 (ECNV19, BVNV8)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "32/06/2027", self.VALID_BUD)

    def test_tc20_invalid_date_mm_00(self):
        """TC20 - MM=00, lower boundary -1 (ECNV20, BVNV9)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "15/00/2027", self.VALID_BUD)

    def test_tc21_invalid_date_mm_13(self):
        """TC21 - MM=13, upper boundary +1 (ECNV21, BVNV10)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "15/13/2027", self.VALID_BUD)

    def test_tc22_invalid_date_yyyy_2024(self):
        """TC22 - YYYY=2024, lower boundary -1 (ECNV22, BVNV11)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "15/06/2024", self.VALID_BUD)

    def test_tc23_invalid_date_yyyy_2028(self):
        """TC23 - YYYY=2028, upper boundary +1 (ECNV23, BVNV12)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "15/06/2028", self.VALID_BUD)

    def test_tc24_invalid_date_not_calendar_date(self):
        """TC24 - Date does not convert to valid Python date (ECNV24)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "31/02/2027", self.VALID_BUD)

    def test_tc25_invalid_date_in_past(self):
        """TC25 - Date is before request date (ECNV25)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, "01/01/2026", self.VALID_BUD)

    # ── INVALID – budget ──────────────────────────────────────────────────
    def test_tc26_invalid_budget_not_float(self):
        """TC26 - Budget is not a float/string passed (ECNV26)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, "50000")

    def test_tc27_invalid_budget_below_minimum(self):
        """TC27 - Budget=49999.99, lower boundary -0.01 (ECNV28, BVNV13)"""
        with self.assertRaisesRegex(EnterpriseManagementException, "50000.00"):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, 49999.99)

    def test_tc28_invalid_budget_above_maximum(self):
        """TC28 - Budget=1000000.01, upper boundary +0.01 (ECNV27, BVNV14)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, 1000000.01)

    def test_tc29_invalid_budget_no_decimals(self):
        """TC29 - Budget with no decimal places, integer (ECNV29)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, 500000)

    def test_tc30_invalid_budget_three_decimals(self):
        """TC30 - Budget with 3 decimal places (ECNV30)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, 50000.123)

    # ── DUPLICATE ─────────────────────────────────────────────────────────
    def test_tc31_invalid_duplicate_project(self):
        """TC31 - Duplicate CIF + acronym already in JSON"""
        EnterpriseManager.register_project(
            self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
            self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)
        with self.assertRaisesRegex(EnterpriseManagementException, "Duplicate"):
            EnterpriseManager.register_project(
                self.VALID_CIF, self.VALID_ACR, self.VALID_DESC,
                self.VALID_DEPT, self.VALID_DATE, self.VALID_BUD)

if __name__ == '__main__':
    unittest.main()
