#!/usr/bin/env python3
"""
Validate fixture file structure and content
"""
import json
import sys
import os
from pathlib import Path


def validate_fixture(fixture_path: str) -> dict:
    """Validate fixture file"""
    errors = []
    warnings = []
    
    if not os.path.exists(fixture_path):
        return {
            "valid": False,
            "errors": [f"File not found: {fixture_path}"],
            "warnings": []
        }
    
    try:
        with open(fixture_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "errors": [f"Invalid JSON: {e}"],
            "warnings": []
        }
    
    # Required fields
    required_fields = ["transaction_version", "activities", "timestamp"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    
    # Validate activities
    if "activities" in data:
        activities = data["activities"]
        if not isinstance(activities, list):
            errors.append("activities must be a list")
        else:
            for i, activity in enumerate(activities):
                activity_fields = ["event_index", "owner_address", "asset_type", "type", "amount"]
                for field in activity_fields:
                    if field not in activity:
                        warnings.append(f"Activity {i} missing field: {field}")
    
    # Check for analysis
    if "analysis" not in data:
        warnings.append("No analysis field - run discovery to generate analysis")
    elif "fee_candidates" in data.get("analysis", {}):
        fee_candidates = data["analysis"]["fee_candidates"]
        if not fee_candidates:
            warnings.append("No fee candidates found in analysis")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "data": data
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_fixture.py <fixture_file>")
        print("\nExample:")
        print("  python validate_fixture.py tests/fixtures/tx_123456789.json")
        sys.exit(1)
    
    fixture_path = sys.argv[1]
    result = validate_fixture(fixture_path)
    
    if result["valid"]:
        print(f"✅ Fixture is valid: {fixture_path}")
    else:
        print(f"❌ Fixture has errors: {fixture_path}")
        for error in result["errors"]:
            print(f"   - {error}")
    
    if result["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in result["warnings"]:
            print(f"   - {warning}")
    
    # Print summary
    if "data" in result:
        data = result["data"]
        print(f"\n📊 Summary:")
        print(f"   Transaction: {data.get('transaction_version', 'N/A')}")
        print(f"   DEX: {data.get('dex_slug', 'N/A')}")
        print(f"   Activities: {len(data.get('activities', []))}")
        if "analysis" in data:
            analysis = data["analysis"]
            print(f"   Fee candidates: {len(analysis.get('fee_candidates', []))}")
    
    sys.exit(0 if result["valid"] else 1)


if __name__ == "__main__":
    main()

