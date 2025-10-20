"""Policy management API router."""


import structlog
from fastapi import APIRouter, Depends, HTTPException

from src.app.dependencies import get_policy_service
from src.app.dto import PolicyResponse
from src.domain.services import PolicyService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/policies", response_model=list[PolicyResponse])
async def list_policies(
    country: str = "SE",
    policy_service: PolicyService = Depends(get_policy_service)
):
    """List active policies for a country."""
    try:
        policies_data = await policy_service.get_active_policies(country)

        return [
            PolicyResponse(
                id=policy["id"],
                version=policy["version"],
                country=policy["country"],
                effective_from=policy["effective_from"],
                effective_to=policy["effective_to"],
                name=policy["name"],
                description=policy["description"]
            )
            for policy in policies_data
        ]

    except Exception as e:
        logger.error("Failed to list policies", country=country, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/policies/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: str,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """Get policy by ID."""
    try:
        policy_data = await policy_service.get_policy(policy_id)
        if not policy_data:
            raise HTTPException(status_code=404, detail="Policy not found")

        return PolicyResponse(
            id=policy_data["id"],
            version=policy_data["version"],
            country=policy_data["country"],
            effective_from=policy_data["effective_from"],
            effective_to=policy_data["effective_to"],
            name=policy_data["name"],
            description=policy_data["description"]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get policy", policy_id=policy_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policies", response_model=PolicyResponse)
async def create_policy(
    policy_data: dict,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """Create a new policy."""
    try:
        created_policy = await policy_service.create_policy(policy_data)

        return PolicyResponse(
            id=created_policy["id"],
            version=created_policy["version"],
            country=created_policy["country"],
            effective_from=created_policy["effective_from"],
            effective_to=created_policy["effective_to"],
            name=created_policy["name"],
            description=created_policy["description"]
        )

    except Exception as e:
        logger.error("Failed to create policy", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: str,
    policy_data: dict,
    policy_service: PolicyService = Depends(get_policy_service)
):
    """Update an existing policy."""
    try:
        updated_policy = await policy_service.update_policy(policy_id, policy_data)

        return PolicyResponse(
            id=updated_policy["id"],
            version=updated_policy["version"],
            country=updated_policy["country"],
            effective_from=updated_policy["effective_from"],
            effective_to=updated_policy["effective_to"],
            name=updated_policy["name"],
            description=updated_policy["description"]
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Failed to update policy", policy_id=policy_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
