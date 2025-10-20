"""JSON Schema definitions for policy DSL validation."""

POLICY_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "version", "country", "effective_from", "name", "rules", "bas_version"],
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^[A-Z]{2}_[A-Z_]+_V[0-9]+$",
            "description": "Policy ID in format COUNTRY_TYPE_VERSION"
        },
        "version": {
            "type": "string",
            "pattern": "^V[0-9]+$",
            "description": "Version in format V1, V2, etc."
        },
        "country": {
            "type": "string",
            "enum": ["SE", "NO", "DK", "FI"],
            "description": "Country code"
        },
        "effective_from": {
            "type": "string",
            "format": "date",
            "description": "Policy effective date"
        },
        "effective_to": {
            "type": "string",
            "format": "date",
            "description": "Policy end date (optional)"
        },
        "name": {
            "type": "string",
            "description": "Human-readable policy name"
        },
        "description": {
            "type": "string",
            "description": "Policy description"
        },
        "bas_version": {
            "type": "string",
            "description": "BAS version this policy references (e.g., '2025_v1.0')"
        },
        "rules": {
            "type": "object",
            "required": ["match", "posting"],
            "properties": {
                "match": {
                    "type": "object",
                    "description": "Conditions for policy to apply",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "description": "Required intent name"
                        },
                        "vendor_patterns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Vendor name patterns"
                        },
                        "amount_min": {
                            "type": "number",
                            "description": "Minimum amount"
                        },
                        "amount_max": {
                            "type": "number",
                            "description": "Maximum amount"
                        }
                    }
                },
                "requires": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["field", "op"],
                        "properties": {
                            "field": {
                                "type": "string",
                                "description": "Field path (e.g., 'slots.attendees_count')"
                            },
                            "op": {
                                "type": "string",
                                "enum": ["exists", ">=", "<=", "==", "!=", "in", "not_in"],
                                "description": "Comparison operator"
                            },
                            "value": {
                                "description": "Value to compare against (not required for 'exists' operation)"
                            }
                        }
                    },
                    "description": "Required fields and their values"
                },
                "vat": {
                    "type": "object",
                    "properties": {
                        "rate": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "VAT rate percentage"
                        },
                        "cap_sek_per_person": {
                            "type": "number",
                            "minimum": 0,
                            "description": "VAT cap per person in SEK"
                        },
                        "code": {
                            "type": "string",
                            "description": "VAT code"
                        },
                        "reverse_charge": {
                            "type": "boolean",
                            "description": "Whether this is reverse charge VAT"
                        },
                        "deductible_split": {
                            "type": "boolean",
                            "description": "Whether to split into deductible/non-deductible portions"
                        },
                        "report_boxes": {
                            "type": "object",
                            "description": "VAT report box mappings"
                        }
                    },
                    "description": "VAT calculation rules"
                },
                "posting": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["account", "side", "amount"],
                        "properties": {
                            "account": {
                                "type": "string",
                                "description": "Account code"
                            },
                            "side": {
                                "type": "string",
                                "enum": ["D", "K"],
                                "description": "Debit (D) or Credit (K)"
                            },
                            "amount": {
                                "type": "string",
                                "enum": [
                                    "net_after_cap",
                                    "vat_allowed",
                                    "gross",
                                    "net_before_cap",
                                    "vat_before_cap",
                                    "vat_excess",
                                    "deductible_net",
                                    "non_deductible_net",
                                    "vat_deductible"
                                ],
                                "description": "Amount calculation method"
                            },
                            "dimension_project": {
                                "type": "string",
                                "description": "Project dimension value"
                            },
                            "dimension_cost_center": {
                                "type": "string",
                                "description": "Cost center dimension value"
                            }
                        }
                    },
                    "description": "Journal entry posting rules"
                },
                "stoplight": {
                    "type": "object",
                    "properties": {
                        "on_missing_required": {
                            "type": "string",
                            "enum": ["GREEN", "YELLOW", "RED"],
                            "description": "Action when required fields are missing"
                        },
                        "on_fail": {
                            "type": "string",
                            "enum": ["GREEN", "YELLOW", "RED"],
                            "description": "Action when policy fails to apply"
                        },
                        "confidence_threshold": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Minimum confidence for GREEN decision"
                        }
                    },
                    "description": "Stoplight decision rules"
                }
            }
        }
    }
}

# Example policy for validation
EXAMPLE_POLICY = {
    "id": "SE_REPR_MEAL_V1",
    "version": "V1",
    "country": "SE",
    "effective_from": "2024-01-01",
    "name": "Swedish Representation Meal Policy",
    "description": "Policy for representation meals in Sweden",
    "bas_version": "2025_v1.0",
    "rules": {
        "match": {
            "intent": "representation_meal"
        },
        "requires": [
            {"field": "attendees_count", "op": ">=", "value": 1},
            {"field": "purpose", "op": "exists"}
        ],
        "vat": {
            "rate": 12,
            "cap_sek_per_person": 300,
            "code": "12"
        },
        "posting": [
            {"account": "6071", "side": "D", "amount": "net_after_cap"},
            {"account": "2641", "side": "D", "amount": "vat_allowed"},
            {"account": "1930", "side": "K", "amount": "gross"}
        ],
        "stoplight": {
            "on_missing_required": "YELLOW",
            "on_fail": "RED",
            "confidence_threshold": 0.8
        }
    }
}
