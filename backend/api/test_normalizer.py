"""
Unit tests for ESG data normalization.

Tests verify that data normalization correctly:
- Converts units (GAL→L, MWh→kWh)
- Assigns emission scopes (1/2/3)
- Handles edge cases and decimal precision
"""

import unittest
from decimal import Decimal
from .normalizer import normalize_record, _parse_decimal


class TestNormalizerHelpers(unittest.TestCase):
    """Tests for normalizer helper functions."""
    
    def test_parse_decimal_with_floats(self):
        """Test parsing decimal from float values."""
        self.assertEqual(_parse_decimal(10.5), Decimal("10.5"))
        self.assertEqual(_parse_decimal(0.0), Decimal("0"))
    
    def test_parse_decimal_exception_handling(self):
        """Test that invalid values don't cause exceptions."""
        # Should not raise exception
        result = _parse_decimal("invalid")
        self.assertEqual(result, Decimal(0))


class TestSAPNormalization(unittest.TestCase):
    """Tests for SAP data normalization."""
    
    def test_sap_liter_normalization(self):
        """Test SAP data already in liters."""
        row = {"Quantity": "100", "UOM": "L"}
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(amount, Decimal("100"))
        self.assertEqual(unit, "L")
        self.assertEqual(scope, "Scope 1")
    
    def test_sap_gallon_to_liter_conversion(self):
        """Test SAP gallon to liter conversion."""
        row = {"Quantity": "1", "UOM": "GAL"}
        amount, unit, scope = normalize_record("SAP", row)
        
        # 1 gallon = 3.78541 liters
        self.assertAlmostEqual(float(amount), 3.78541, places=4)
        self.assertEqual(unit, "L")
        self.assertEqual(scope, "Scope 1")
    
    def test_sap_large_quantity_conversion(self):
        """Test SAP conversion with large quantities."""
        row = {"Quantity": "1000", "UOM": "GAL"}
        amount, unit, scope = normalize_record("SAP", row)
        
        expected = Decimal("1000") * Decimal("3.78541")
        self.assertEqual(amount, expected)
        self.assertEqual(scope, "Scope 1")
    
    def test_sap_decimal_precision(self):
        """Test SAP preserves decimal precision."""
        row = {"Quantity": "10.123456", "UOM": "L"}
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(amount, Decimal("10.123456"))
    
    def test_sap_zero_quantity(self):
        """Test SAP with zero quantity."""
        row = {"Quantity": "0", "UOM": "L"}
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(amount, Decimal("0"))
        self.assertEqual(scope, "Scope 1")


class TestUtilityNormalization(unittest.TestCase):
    """Tests for UTILITY data normalization."""
    
    def test_utility_kwh_normalization(self):
        """Test UTILITY data already in kWh."""
        row = {"Consumption": "5000", "Unit": "kWh"}
        amount, unit, scope = normalize_record("UTILITY", row)
        
        self.assertEqual(amount, Decimal("5000"))
        self.assertEqual(unit, "kWh")
        self.assertEqual(scope, "Scope 2")
    
    def test_utility_mwh_to_kwh_conversion(self):
        """Test UTILITY MWh to kWh conversion."""
        row = {"Consumption": "1", "Unit": "MWh"}
        amount, unit, scope = normalize_record("UTILITY", row)
        
        # 1 MWh = 1000 kWh
        self.assertEqual(amount, Decimal("1000"))
        self.assertEqual(unit, "kWh")
        self.assertEqual(scope, "Scope 2")
    
    def test_utility_large_mwh_conversion(self):
        """Test UTILITY conversion with large MWh values."""
        row = {"Consumption": "500", "Unit": "MWh"}
        amount, unit, scope = normalize_record("UTILITY", row)
        
        expected = Decimal("500") * Decimal("1000")
        self.assertEqual(amount, expected)
        self.assertEqual(scope, "Scope 2")
    
    def test_utility_decimal_precision(self):
        """Test UTILITY preserves decimal precision."""
        row = {"Consumption": "2.5", "Unit": "kWh"}
        amount, unit, scope = normalize_record("UTILITY", row)
        
        self.assertEqual(amount, Decimal("2.5"))
    
    def test_utility_fractional_mwh(self):
        """Test UTILITY with fractional MWh."""
        row = {"Consumption": "0.5", "Unit": "MWh"}
        amount, unit, scope = normalize_record("UTILITY", row)
        
        # 0.5 MWh = 500 kWh
        self.assertEqual(amount, Decimal("500"))


class TestTravelNormalization(unittest.TestCase):
    """Tests for TRAVEL data normalization."""
    
    def test_travel_distance_normalization(self):
        """Test TRAVEL distance normalization."""
        row = {"Distance": "1000"}
        amount, unit, scope = normalize_record("TRAVEL", row)
        
        self.assertEqual(amount, Decimal("1000"))
        self.assertEqual(unit, "km")
        self.assertEqual(scope, "Scope 3")
    
    def test_travel_short_distance(self):
        """Test TRAVEL with short distances."""
        row = {"Distance": "5"}
        amount, unit, scope = normalize_record("TRAVEL", row)
        
        self.assertEqual(amount, Decimal("5"))
        self.assertEqual(scope, "Scope 3")
    
    def test_travel_decimal_distance(self):
        """Test TRAVEL with decimal distances."""
        row = {"Distance": "123.456"}
        amount, unit, scope = normalize_record("TRAVEL", row)
        
        self.assertEqual(amount, Decimal("123.456"))
    
    def test_travel_zero_distance(self):
        """Test TRAVEL with zero distance."""
        row = {"Distance": "0"}
        amount, unit, scope = normalize_record("TRAVEL", row)
        
        self.assertEqual(amount, Decimal("0"))


class TestNormalizationEdgeCases(unittest.TestCase):
    """Tests for edge cases in normalization."""
    
    def test_missing_quantity_defaults_to_zero(self):
        """Test that missing quantity defaults to 0."""
        row = {}  # Missing Quantity
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(amount, Decimal("0"))
    
    def test_missing_uom_defaults_to_liter(self):
        """Test that missing UOM defaults to L for SAP."""
        row = {"Quantity": "100"}  # Missing UOM
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(unit, "L")
    
    def test_case_insensitive_source_type(self):
        """Test that source type is case insensitive."""
        row_sap = {"Quantity": "100", "UOM": "L"}
        row_utility = {"Consumption": "1000", "Unit": "kWh"}
        row_travel = {"Distance": "500"}
        
        _, _, scope1 = normalize_record("SAP", row_sap)
        _, _, scope2 = normalize_record("sap", row_sap)
        self.assertEqual(scope1, scope2)
        
        _, _, scope3 = normalize_record("UTILITY", row_utility)
        _, _, scope4 = normalize_record("utility", row_utility)
        self.assertEqual(scope3, scope4)
    
    def test_unknown_source_type_defaults(self):
        """Test that unknown source type returns safe defaults."""
        row = {}
        amount, unit, scope = normalize_record("UNKNOWN", row)
        
        self.assertEqual(amount, Decimal(0))
        self.assertEqual(unit, "")
        self.assertEqual(scope, "Scope 1")
    
    def test_very_large_values(self):
        """Test normalization with very large values."""
        row = {"Quantity": "999999999", "UOM": "GAL"}
        amount, unit, scope = normalize_record("SAP", row)
        
        expected = Decimal("999999999") * Decimal("3.78541")
        self.assertEqual(amount, expected)
    
    def test_very_small_values(self):
        """Test normalization with very small decimal values."""
        row = {"Quantity": "0.000001", "UOM": "L"}
        amount, unit, scope = normalize_record("SAP", row)
        
        self.assertEqual(amount, Decimal("0.000001"))
    
    def test_whitespace_in_numeric_values(self):
        """Test that whitespace in numeric values is handled."""
        row = {"Quantity": "  100  ", "UOM": "  L  "}
        amount, unit, scope = normalize_record("SAP", row)
        
        # Should handle this gracefully
        self.assertEqual(amount, Decimal("100"))


class TestScopeAssignment(unittest.TestCase):
    """Tests for correct scope assignment across data types."""
    
    def test_sap_always_scope_1(self):
        """Test that SAP data is always assigned Scope 1."""
        test_cases = [
            {"Quantity": "100", "UOM": "L"},
            {"Quantity": "50", "UOM": "GAL"},
            {"Quantity": "0.5", "UOM": "L"},
        ]
        
        for row in test_cases:
            _, _, scope = normalize_record("SAP", row)
            self.assertEqual(scope, "Scope 1")
    
    def test_utility_always_scope_2(self):
        """Test that UTILITY data is always assigned Scope 2."""
        test_cases = [
            {"Consumption": "1000", "Unit": "kWh"},
            {"Consumption": "1", "Unit": "MWh"},
            {"Consumption": "0.5", "Unit": "kWh"},
        ]
        
        for row in test_cases:
            _, _, scope = normalize_record("UTILITY", row)
            self.assertEqual(scope, "Scope 2")
    
    def test_travel_always_scope_3(self):
        """Test that TRAVEL data is always assigned Scope 3."""
        test_cases = [
            {"Distance": "1000"},
            {"Distance": "5000"},
            {"Distance": "0.1"},
        ]
        
        for row in test_cases:
            _, _, scope = normalize_record("TRAVEL", row)
            self.assertEqual(scope, "Scope 3")


if __name__ == "__main__":
    unittest.main()
