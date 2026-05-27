from decimal import Decimal, InvalidOperation
from datetime import datetime


SAP_ALLOWED_UOM = {"L", "GAL"}
SAP_ALLOWED_PLANT_CODES = {"DE100", "IN200", "PL300"}

UTILITY_ALLOWED_UNIT = {"kWh", "MWh"}

TRAVEL_ALLOWED_TRIP_TYPES = {"Flight", "Hotel", "Taxi"}
KNOWN_AIRPORT_CODES = {"LHR", "JFK", "DEL", "FRA", "DXB", "SFO", "ORD", "SIN", "AMS", "BOM"}


def _parse_decimal(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None


def _parse_date(value, dayfirst=False):
    if value is None or str(value).strip() == "":
        return None
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except Exception:
        try:
            if dayfirst:
                return datetime.strptime(str(value), "%d.%m.%Y").date()
            return datetime.strptime(str(value), "%m/%d/%Y").date()
        except Exception:
            try:
                return datetime.fromisoformat(str(value)).date()
            except Exception:
                return None


def validate_record(source_type, row):
    if isinstance(source_type, str):
        source_type = source_type.strip().upper()
    reasons = []
    severity = "warning"

    def add_error(msg):
        nonlocal severity
        reasons.append(msg)
        severity = "error"

    def add_warning(msg):
        nonlocal severity
        if severity != "error":
            severity = "warning"
        reasons.append(msg)

    if source_type == "SAP":
        required = ["Document_Number", "Posting_Date", "Plant_Code", "Material_Description", "Quantity", "UOM"]
        for field in required:
            if not row.get(field):
                add_error(f"missing {field}")

        quantity = _parse_decimal(row.get("Quantity"))
        if quantity is None:
            add_error("invalid Quantity")
        elif quantity < 0:
            add_error("negative Quantity")

        uom = row.get("UOM")
        if uom and uom not in SAP_ALLOWED_UOM:
            add_error(f"unsupported UOM: {uom}")

        plant = row.get("Plant_Code")
        if plant and plant not in SAP_ALLOWED_PLANT_CODES:
            add_warning(f"unknown Plant_Code: {plant}")

    elif source_type == "UTILITY":
        required = ["Meter_ID", "Billing_Start", "Billing_End", "Consumption", "Unit"]
        for field in required:
            if not row.get(field):
                add_error(f"missing {field}")

        start = _parse_date(row.get("Billing_Start"), dayfirst=True)
        end = _parse_date(row.get("Billing_End"), dayfirst=True)
        if row.get("Billing_Start") and not start:
            add_error("invalid Billing_Start")
        if row.get("Billing_End") and not end:
            add_error("invalid Billing_End")
        if start and end and end < start:
            add_error("Billing_End < Billing_Start")

        consumption = _parse_decimal(row.get("Consumption"))
        if consumption is None:
            add_error("invalid Consumption")
        else:
            if consumption < 0:
                add_error("negative Consumption")
            if consumption == 0:
                add_error("zero Consumption")

        unit = row.get("Unit")
        if unit and unit not in UTILITY_ALLOWED_UNIT:
            add_error(f"unsupported Unit: {unit}")

    elif source_type == "TRAVEL":
        trip_type = row.get("Trip_Type")
        if not trip_type:
            add_error("missing Trip_Type")
        elif trip_type not in TRAVEL_ALLOWED_TRIP_TYPES:
            add_error(f"invalid Trip_Type: {trip_type}")

        origin = row.get("Origin")
        destination = row.get("Destination")
        if not origin:
            add_error("missing Origin")
        if not destination:
            add_error("missing Destination")

        travel_date = _parse_date(row.get("Travel_Date"))
        if not row.get("Travel_Date"):
            add_error("missing Travel_Date")
        elif not travel_date:
            add_error("invalid Travel_Date")

        distance = _parse_decimal(row.get("Distance"))
        if distance is None:
            add_error("missing Distance")
        elif distance < 0:
            add_error("negative Distance")

        if trip_type == "Flight" and origin and destination and origin == destination:
            add_error("same Origin and Destination for flights")

        if origin and origin not in KNOWN_AIRPORT_CODES:
            add_warning(f"unknown airport code: {origin}")
        if destination and destination not in KNOWN_AIRPORT_CODES:
            add_warning(f"unknown airport code: {destination}")

    else:
        add_warning("no validation rules for source_type")

    flagged = len(reasons) > 0
    return {"flagged": flagged, "severity": severity if flagged else "none", "reasons": reasons}


def normalize_record(source_type, row):
    if source_type == "SAP":
        quantity = _parse_decimal(row.get("Quantity")) or Decimal(0)
        uom = row.get("UOM") or ""
        if uom == "GAL":
            normalized_amount = quantity * Decimal("3.78541")
            normalized_unit = "L"
        else:
            normalized_amount = quantity
            normalized_unit = "L"
        scope = "Scope 1"
        return normalized_amount, normalized_unit, scope

    if source_type == "utility":
        consumption = _parse_decimal(row.get("Consumption")) or Decimal(0)
        unit = row.get("Unit") or ""
        if unit == "MWh":
            normalized_amount = consumption * Decimal("1000")
            normalized_unit = "kWh"
        else:
            normalized_amount = consumption
            normalized_unit = "kWh"
        scope = "Scope 2"
        return normalized_amount, normalized_unit, scope

    if source_type == "travel":
        distance = _parse_decimal(row.get("Distance")) or Decimal(0)
        normalized_amount = distance
        normalized_unit = "km"
        scope = "Scope 3"
        return normalized_amount, normalized_unit, scope

    return Decimal(0), "", "Scope 1"
