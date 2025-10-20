"""Validation utilities for the Fire & Forget Accounting API."""

import re
from typing import Any
from uuid import UUID

from src.app.exceptions import ValidationError


def validate_uuid(value: Any, field_name: str) -> UUID:
    """Validate that a value is a valid UUID."""
    if isinstance(value, UUID):
        return value

    if isinstance(value, str):
        try:
            return UUID(value)
        except ValueError:
            raise ValidationError(
                field=field_name,
                value=value,
                reason="Invalid UUID format"
            )

    raise ValidationError(
        field=field_name,
        value=value,
        reason="Expected UUID or string"
    )


def validate_company_id(company_id: Any) -> UUID:
    """Validate company ID."""
    return validate_uuid(company_id, "company_id")


def validate_user_id(user_id: Any) -> UUID | None:
    """Validate user ID (optional)."""
    if user_id is None:
        return None
    return validate_uuid(user_id, "user_id")


def validate_document_id(document_id: Any) -> UUID:
    """Validate document ID."""
    return validate_uuid(document_id, "document_id")


def validate_pipeline_run_id(pipeline_run_id: Any) -> UUID:
    """Validate pipeline run ID."""
    return validate_uuid(pipeline_run_id, "pipeline_run_id")


def validate_booking_id(booking_id: Any) -> UUID:
    """Validate booking ID."""
    return validate_uuid(booking_id, "booking_id")


def validate_policy_id(policy_id: Any) -> str:
    """Validate policy ID."""
    if not isinstance(policy_id, str):
        raise ValidationError(
            field="policy_id",
            value=policy_id,
            reason="Expected string"
        )

    if not policy_id.strip():
        raise ValidationError(
            field="policy_id",
            value=policy_id,
            reason="Policy ID cannot be empty"
        )

    # Policy ID should match pattern: COUNTRY_CATEGORY_VERSION
    pattern = r'^[A-Z]{2}_[A-Z_]+_V\d+$'
    if not re.match(pattern, policy_id):
        raise ValidationError(
            field="policy_id",
            value=policy_id,
            reason="Policy ID must match pattern: COUNTRY_CATEGORY_VERSION (e.g., SE_MEAL_V1)"
        )

    return policy_id


def validate_country_code(country: Any) -> str:
    """Validate country code."""
    if not isinstance(country, str):
        raise ValidationError(
            field="country",
            value=country,
            reason="Expected string"
        )

    country = country.upper().strip()
    valid_countries = ["SE", "NO", "DK", "FI"]

    if country not in valid_countries:
        raise ValidationError(
            field="country",
            value=country,
            reason=f"Country must be one of: {', '.join(valid_countries)}"
        )

    return country


def validate_pagination_params(limit: Any, offset: Any) -> tuple[int, int]:
    """Validate pagination parameters."""
    # Validate limit
    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            raise ValidationError(
                field="limit",
                value=limit,
                reason="Expected integer"
            )

    if limit < 1:
        raise ValidationError(
            field="limit",
            value=limit,
            reason="Limit must be at least 1"
        )

    if limit > 1000:
        raise ValidationError(
            field="limit",
            value=limit,
            reason="Limit cannot exceed 1000"
        )

    # Validate offset
    if not isinstance(offset, int):
        try:
            offset = int(offset)
        except (ValueError, TypeError):
            raise ValidationError(
                field="offset",
                value=offset,
                reason="Expected integer"
            )

    if offset < 0:
        raise ValidationError(
            field="offset",
            value=offset,
            reason="Offset must be non-negative"
        )

    return limit, offset


def validate_file_upload(file_content: bytes, content_type: str, filename: str) -> None:
    """Validate file upload."""
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if len(file_content) > max_size:
        raise ValidationError(
            field="file",
            value=filename,
            reason=f"File size exceeds maximum allowed size of {max_size} bytes"
        )

    # Check if file is empty
    if len(file_content) == 0:
        raise ValidationError(
            field="file",
            value=filename,
            reason="File cannot be empty"
        )

    # Validate content type
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "application/pdf"
    ]

    if content_type not in allowed_types:
        raise ValidationError(
            field="content_type",
            value=content_type,
            reason=f"Content type must be one of: {', '.join(allowed_types)}"
        )

    # Validate filename
    if not filename or not filename.strip():
        raise ValidationError(
            field="filename",
            value=filename,
            reason="Filename cannot be empty"
        )

    # Check filename length
    if len(filename) > 255:
        raise ValidationError(
            field="filename",
            value=filename,
            reason="Filename cannot exceed 255 characters"
        )


def validate_user_text(user_text: str | None) -> str | None:
    """Validate user text input."""
    if user_text is None:
        return None

    if not isinstance(user_text, str):
        raise ValidationError(
            field="user_text",
            value=user_text,
            reason="Expected string or null"
        )

    # Check length
    if len(user_text) > 1000:
        raise ValidationError(
            field="user_text",
            value=user_text,
            reason="User text cannot exceed 1000 characters"
        )

    return user_text.strip() if user_text.strip() else None
