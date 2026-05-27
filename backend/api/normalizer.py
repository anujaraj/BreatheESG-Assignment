from decimal import Decimal


def _parse_decimal(value):
    try:
        return Decimal(str(value))
    except Exception:
        return Decimal(0)


def normalize_record(source_type, row):
    """
    Normalize ESG data to standard units and assign emission scope.
    
    Scope Assignment Logic:
    - SAP (Fuel/Material consumption) → Scope 1 (Direct emissions from fuel burning/material processing)
    - UTILITY (Energy consumption) → Scope 2 (Indirect emissions from purchased electricity/utilities)
    - TRAVEL (Business travel) → Scope 3 (Indirect emissions from business travel)
    
    Unit Conversion:
    - Fuel: GAL → L (1 gallon = 3.78541 liters)
    - Energy: MWh → kWh (1 MWh = 1000 kWh)
    - Travel: Distance kept in km (standard unit)
    """
    if isinstance(source_type, str):
        source_type = source_type.strip().upper()
    if source_type == "SAP":
        # SAP data: Direct fuel/material consumption → Scope 1
        quantity = _parse_decimal(row.get("Quantity"))
        uom = (row.get("UOM") or "").strip()
        if uom == "GAL":
            normalized_amount = quantity * Decimal("3.78541")
            normalized_unit = "L"
        else:
            normalized_amount = quantity
            normalized_unit = "L"
        scope = "Scope 1"
        return normalized_amount, normalized_unit, scope

    if source_type == "UTILITY":
        # Utility data: Energy consumption from grid → Scope 2
        consumption = _parse_decimal(row.get("Consumption"))
        unit = (row.get("Unit") or "").strip()
        if unit == "MWh":
            normalized_amount = consumption * Decimal("1000")
            normalized_unit = "kWh"
        else:
            normalized_amount = consumption
            normalized_unit = "kWh"
        scope = "Scope 2"
        return normalized_amount, normalized_unit, scope

    if source_type == "TRAVEL":
        # Travel data: Business travel distance → Scope 3
        distance = _parse_decimal(row.get("Distance"))
        normalized_amount = distance
        normalized_unit = "km"
        scope = "Scope 3"
        return normalized_amount, normalized_unit, scope

    return Decimal(0), "", "Scope 1"
