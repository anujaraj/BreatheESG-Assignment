"""
Unit tests for ESG data validation.

Tests cover validation edge cases for all three data source types:
- SAP: Fuel/material consumption
- UTILITY: Energy consumption  
- TRAVEL: Business travel

These tests verify proper error detection, severity classification,
and handling of boundary conditions.
"""

import unittest
from decimal import Decimal
from datetime import datetime
from .validator import validate_record, _parse_decimal, _parse_date


class TestValidatorHelpers(unittest.TestCase):
    """Tests for helper functions."""
    
    def test_parse_decimal_valid(self):
        """Test decimal parsing with valid values."""
        self.assertEqual(_parse_decimal("10.5"), Decimal("10.5"))
        self.assertEqual(_parse_decimal("0"), Decimal("0"))
        self.assertEqual(_parse_decimal("-5.2"), Decimal("-5.2"))
        self.assertEqual(_parse_decimal(100), Decimal("100"))
    
    def test_parse_decimal_invalid(self):
        """Test decimal parsing with invalid values."""
        self.assertIsNone(_parse_decimal("invalid"))
        self.assertIsNone(_parse_decimal(""))
        self.assertIsNone(_parse_decimal(None))
        self.assertIsNone(_parse_decimal([]))
    
    def test_parse_date_valid_formats(self):
        """Test date parsing with multiple valid formats."""
        # ISO format
        result = _parse_date("2024-05-15")
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 5)
        self.assertEqual(result.day, 15)
        
        # US format
        result = _parse_date("05/15/2024")
        self.assertEqual(result.year, 2024)
        
        # European format
        result = _parse_date("15.05.2024", dayfirst=True)
        self.assertEqual(result.year, 2024)
    
    def test_parse_date_invalid(self):
        """Test date parsing with invalid values."""
        self.assertIsNone(_parse_date("invalid-date"))
        self.assertIsNone(_parse_date(""))
        self.assertIsNone(_parse_date(None))
        self.assertIsNone(_parse_date("2024-13-01"))  # Invalid month


class TestSAPValidation(unittest.TestCase):
    """Tests for SAP source type validation."""
    
    def test_valid_sap_record(self):
        """Test validation of valid SAP record."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "100",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertFalse(result["flagged"])
        self.assertEqual(result["severity"], "none")
    
    def test_sap_missing_required_fields(self):
        """Test SAP validation with missing required fields."""
        record = {
            "Document_Number": "DOC001",
            # Missing Posting_Date
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "100",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "error")
        self.assertIn("missing Posting_Date", result["reasons"])
    
    def test_sap_negative_quantity(self):
        """Test SAP validation rejects negative quantity."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "-50",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "error")
        self.assertIn("negative Quantity", result["reasons"])
    
    def test_sap_invalid_uom(self):
        """Test SAP validation rejects invalid UOM."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "100",
            "UOM": "KG"  # Invalid UOM
        }
        result = validate_record("SAP", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "error")
        self.assertIn("unsupported UOM: KG", result["reasons"])
    
    def test_sap_unknown_plant_code_warning(self):
        """Test SAP validation warns on unknown plant code."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "XX999",  # Unknown plant
            "Material_Description": "Fuel",
            "Quantity": "100",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "warning")
        self.assertIn("unknown Plant_Code: XX999", result["reasons"])
    
    def test_sap_zero_quantity(self):
        """Test SAP validation allows zero quantity."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "0",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertFalse(result["flagged"])
    
    def test_sap_invalid_quantity_format(self):
        """Test SAP validation rejects invalid quantity format."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "not-a-number",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "error")
        self.assertIn("invalid Quantity", result["reasons"])


class TestUtilityValidation(unittest.TestCase):
    """Tests for UTILITY source type validation."""
    
    def test_valid_utility_record(self):
        """Test validation of valid utility record."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "2024-05-01",
            "Billing_End": "2024-05-31",
            "Consumption": "1500",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertFalse(result["flagged"])
        self.assertEqual(result["severity"], "none")
    
    def test_utility_invalid_billing_dates(self):
        """Test UTILITY validation with invalid date format."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "invalid-date",
            "Billing_End": "2024-05-31",
            "Consumption": "1500",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("invalid Billing_Start", result["reasons"])
    
    def test_utility_end_before_start(self):
        """Test UTILITY validation rejects billing end before start."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "2024-05-31",
            "Billing_End": "2024-05-01",  # End before start
            "Consumption": "1500",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("Billing_End < Billing_Start", result["reasons"])
    
    def test_utility_negative_consumption(self):
        """Test UTILITY validation rejects negative consumption."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "2024-05-01",
            "Billing_End": "2024-05-31",
            "Consumption": "-500",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("negative Consumption", result["reasons"])
    
    def test_utility_zero_consumption(self):
        """Test UTILITY validation rejects zero consumption."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "2024-05-01",
            "Billing_End": "2024-05-31",
            "Consumption": "0",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("zero Consumption", result["reasons"])
    
    def test_utility_invalid_unit(self):
        """Test UTILITY validation rejects invalid unit."""
        record = {
            "Meter_ID": "METER001",
            "Billing_Start": "2024-05-01",
            "Billing_End": "2024-05-31",
            "Consumption": "1500",
            "Unit": "Joules"  # Invalid unit
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("unsupported Unit: Joules", result["reasons"])
    
    def test_utility_missing_fields(self):
        """Test UTILITY validation with missing required fields."""
        record = {
            "Meter_ID": "METER001",
            # Missing Billing_Start
            "Billing_End": "2024-05-31",
            "Consumption": "1500",
            "Unit": "kWh"
        }
        result = validate_record("UTILITY", record)
        self.assertTrue(result["flagged"])
        self.assertIn("missing Billing_Start", result["reasons"])


class TestTravelValidation(unittest.TestCase):
    """Tests for TRAVEL source type validation."""
    
    def test_valid_travel_record(self):
        """Test validation of valid travel record."""
        record = {
            "Trip_Type": "Flight",
            "Origin": "LHR",
            "Destination": "JFK",
            "Travel_Date": "2024-05-15",
            "Distance": "5560"
        }
        result = validate_record("TRAVEL", record)
        self.assertFalse(result["flagged"])
        self.assertEqual(result["severity"], "none")
    
    def test_travel_invalid_trip_type(self):
        """Test TRAVEL validation rejects invalid trip type."""
        record = {
            "Trip_Type": "Teleportation",  # Invalid
            "Origin": "LHR",
            "Destination": "JFK",
            "Travel_Date": "2024-05-15",
            "Distance": "5560"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertIn("invalid Trip_Type: Teleportation", result["reasons"])
    
    def test_travel_same_origin_destination(self):
        """Test TRAVEL validation rejects same origin/destination for flights."""
        record = {
            "Trip_Type": "Flight",
            "Origin": "LHR",
            "Destination": "LHR",  # Same as origin
            "Travel_Date": "2024-05-15",
            "Distance": "0"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertIn("same Origin and Destination for flights", result["reasons"])
    
    def test_travel_negative_distance(self):
        """Test TRAVEL validation rejects negative distance."""
        record = {
            "Trip_Type": "Flight",
            "Origin": "LHR",
            "Destination": "JFK",
            "Travel_Date": "2024-05-15",
            "Distance": "-100"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertIn("negative Distance", result["reasons"])
    
    def test_travel_unknown_airport_code_warning(self):
        """Test TRAVEL validation warns on unknown airport codes."""
        record = {
            "Trip_Type": "Flight",
            "Origin": "XXX",  # Unknown airport
            "Destination": "JFK",
            "Travel_Date": "2024-05-15",
            "Distance": "5560"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertEqual(result["severity"], "warning")
        self.assertIn("unknown airport code: XXX", result["reasons"])
    
    def test_travel_invalid_date(self):
        """Test TRAVEL validation rejects invalid travel date."""
        record = {
            "Trip_Type": "Flight",
            "Origin": "LHR",
            "Destination": "JFK",
            "Travel_Date": "invalid-date",
            "Distance": "5560"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertIn("invalid Travel_Date", result["reasons"])
    
    def test_travel_missing_fields(self):
        """Test TRAVEL validation with missing required fields."""
        record = {
            # Missing Trip_Type
            "Origin": "LHR",
            "Destination": "JFK",
            "Travel_Date": "2024-05-15",
            "Distance": "5560"
        }
        result = validate_record("TRAVEL", record)
        self.assertTrue(result["flagged"])
        self.assertIn("missing Trip_Type", result["reasons"])
    
    def test_travel_zero_distance_non_flight(self):
        """Test TRAVEL validation allows zero distance for non-flights."""
        record = {
            "Trip_Type": "Hotel",  # Not a flight
            "Origin": "LHR",
            "Destination": "LHR",
            "Travel_Date": "2024-05-15",
            "Distance": "0"
        }
        result = validate_record("TRAVEL", record)
        # Should not have same origin/destination error for Hotel
        error_about_same_origin = any("same Origin and Destination" in r for r in result["reasons"])
        self.assertFalse(error_about_same_origin)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and boundary conditions."""
    
    def test_case_insensitive_source_type(self):
        """Test that source type is case insensitive."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "100",
            "UOM": "L"
        }
        result_upper = validate_record("SAP", record)
        result_lower = validate_record("sap", record)
        result_mixed = validate_record("SaP", record)
        
        self.assertEqual(result_upper["flagged"], result_lower["flagged"])
        self.assertEqual(result_upper["flagged"], result_mixed["flagged"])
    
    def test_whitespace_handling(self):
        """Test that whitespace in fields is handled properly."""
        record = {
            "Document_Number": "  DOC001  ",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "  Fuel  ",
            "Quantity": "100",
            "UOM": "  L  "  # UOM has whitespace - validator doesn't strip this
        }
        result = validate_record("SAP", record)
        # UOM with spaces won't match "L" exactly, so it should be flagged as unsupported
        self.assertTrue(result["flagged"])
        # Check for the actual error message format
        self.assertTrue(any("unsupported UOM" in reason for reason in result["reasons"]))
    
    def test_very_large_numbers(self):
        """Test validation with very large numbers."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "999999999999.999999",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertFalse(result["flagged"])
    
    def test_decimal_precision(self):
        """Test validation with high decimal precision."""
        record = {
            "Document_Number": "DOC001",
            "Posting_Date": "2024-05-15",
            "Plant_Code": "DE100",
            "Material_Description": "Fuel",
            "Quantity": "100.123456789",
            "UOM": "L"
        }
        result = validate_record("SAP", record)
        self.assertFalse(result["flagged"])


if __name__ == "__main__":
    unittest.main()
