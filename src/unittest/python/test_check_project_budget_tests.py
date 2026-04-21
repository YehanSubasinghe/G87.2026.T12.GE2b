"""Tests for the check_project_budget method"""
import json
import os
import unittest
from uc3m_consulting import EnterpriseManager, EnterpriseManagementException

class TestCheckProjectBudget(unittest.TestCase):
    """Structural test cases for check_project_budget"""

    VALID_PID  = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
    VALID_PID2 = "b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5"
    FLOWS_FILE = "flows.json"

    def setUp(self):
        """Back up flows.json before each test"""
        if os.path.exists(self.FLOWS_FILE):
            with open(self.FLOWS_FILE, "r", encoding="utf-8") as f:
                self._flows_backup = f.read()
        else:
            self._flows_backup = None

    def tearDown(self):
        """Restore flows.json and clean output files after each test"""
        if self._flows_backup is not None:
            with open(self.FLOWS_FILE, "w", encoding="utf-8") as f:
                f.write(self._flows_backup)
        elif os.path.exists(self.FLOWS_FILE):
            os.remove(self.FLOWS_FILE)
        for f in os.listdir("."):
            if f.startswith("expenses_") and f.endswith(".json"):
                os.remove(f)

    def _write_flows(self, data):
        """Helper to write custom flows.json"""
        with open(self.FLOWS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)

    # Path 1: 1→2→3
    def test_tc_m3_01_invalid_project_id(self):
        """TC_M3_01 - Invalid PROJECT_ID format (path 1→2→3)"""
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.check_project_budget("ZZZZ")

    # Path 2: 1→2→4→5→6
    def test_tc_m3_02_flows_file_not_found(self):
        """TC_M3_02 - flows.json does not exist (path 1→2→4→5→6)"""
        if os.path.exists(self.FLOWS_FILE):
            os.remove(self.FLOWS_FILE)
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.check_project_budget(self.VALID_PID)

    # Path 3: 1→2→4→5→7→8→14→15
    def test_tc_m3_03_empty_flows(self):
        """TC_M3_03 - flows.json empty list, loop not entered (path 1→2→4→5→7→8→14→15)"""
        self._write_flows([])
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.check_project_budget(self.VALID_PID)

    # Path 4: 1→2→4→5→7→8→9→8→14→15
    def test_tc_m3_04_no_matching_pid(self):
        """TC_M3_04 - PROJECT_ID not in flows (path 1→2→4→5→7→8→9→8→14→15)"""
        self._write_flows([
            {"PROJECT_ID": self.VALID_PID2, "inflow": "1000.00"}
        ])
        with self.assertRaises(EnterpriseManagementException):
            EnterpriseManager.check_project_budget(self.VALID_PID)

    # Path 5: 1→2→4→5→7→8→9→10→11→8→14→16→17
    def test_tc_m3_05_single_inflow(self):
        """TC_M3_05 - Single inflow entry (path 1→2→4→5→7→8→9→10→11→8→14→16→17)"""
        self._write_flows([
            {"PROJECT_ID": self.VALID_PID, "inflow": "2500.00"}
        ])
        result = EnterpriseManager.check_project_budget(self.VALID_PID)
        self.assertTrue(result)
        output_file = "expenses_" + self.VALID_PID + ".json"
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["PROJECT_ID"], self.VALID_PID)
        self.assertAlmostEqual(data["balance"], 2500.00)

    # Path 6: 1→2→4→5→7→8→9→10→12→8→14→16→17
    def test_tc_m3_06_single_outflow(self):
        """TC_M3_06 - Single outflow entry (path 1→2→4→5→7→8→9→10→12→8→14→16→17)"""
        self._write_flows([
            {"PROJECT_ID": self.VALID_PID, "outflow": "750.50"}
        ])
        result = EnterpriseManager.check_project_budget(self.VALID_PID)
        self.assertTrue(result)
        output_file = "expenses_" + self.VALID_PID + ".json"
        self.assertTrue(os.path.exists(output_file))
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertAlmostEqual(data["balance"], -750.50)

    # Path 7: loop multiple iterations
    def test_tc_m3_07_multiple_flows(self):
        """TC_M3_07 - Multiple inflow+outflow entries (loop multiple iterations)"""
        self._write_flows([
            {"PROJECT_ID": self.VALID_PID,  "inflow":  "2500.00"},
            {"PROJECT_ID": self.VALID_PID,  "outflow": "1000.00"},
            {"PROJECT_ID": self.VALID_PID,  "inflow":  "500.00"},
            {"PROJECT_ID": self.VALID_PID2, "inflow":  "9999.00"}
        ])
        result = EnterpriseManager.check_project_budget(self.VALID_PID)
        self.assertTrue(result)
        output_file = "expenses_" + self.VALID_PID + ".json"
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertAlmostEqual(data["balance"], 2000.00)


if __name__ == "__main__":
    unittest.main()
