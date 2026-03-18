from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from sqlalchemy import select
from sqlmodel import Session

from app.crud import list_endpoints
from app.models import EndpointDefinition, RouteDeployment, RouteImplementation


@dataclass(slots=True)
class RouteDeploymentState:
    has_any_runtime_record: bool = False
    has_any_deployment: bool = False
    has_active_deployment: bool = False


def _deployment_states_by_route_id(session: Session, route_ids: list[int]) -> dict[int, RouteDeploymentState]:
    if not route_ids:
        return {}

    implementation_route_ids = session.execute(
        select(RouteImplementation.route_id).where(RouteImplementation.route_id.in_(route_ids)).distinct()
    ).scalars()
    states = {
        int(route_id): RouteDeploymentState(has_any_runtime_record=True)
        for route_id in implementation_route_ids
        if route_id is not None
    }

    rows = session.execute(
        select(RouteDeployment.route_id, RouteDeployment.is_active).where(RouteDeployment.route_id.in_(route_ids))
    ).all()

    for route_id, is_active in rows:
        state = states.setdefault(int(route_id), RouteDeploymentState())
        state.has_any_runtime_record = True
        state.has_any_deployment = True
        if is_active:
            state.has_active_deployment = True

    return states


def _is_public_contract_route(endpoint: EndpointDefinition, state: RouteDeploymentState | None) -> bool:
    if not endpoint.enabled:
        return False
    if state and state.has_any_runtime_record:
        return state.has_active_deployment
    return True


def _uses_legacy_mock_fallback(endpoint: EndpointDefinition, state: RouteDeploymentState | None) -> bool:
    if not endpoint.enabled:
        return False
    return not (state and state.has_any_runtime_record)


def _list_routes_by_policy(
    session: Session,
    *,
    limit: int,
    offset: int,
    selector: Callable[[EndpointDefinition, RouteDeploymentState | None], bool],
) -> list[EndpointDefinition]:
    endpoints = list_endpoints(session, limit=limit, offset=offset)
    route_ids = [int(endpoint.id) for endpoint in endpoints if endpoint.id is not None]
    states = _deployment_states_by_route_id(session, route_ids)
    return [
        endpoint
        for endpoint in endpoints
        if selector(endpoint, states.get(int(endpoint.id or 0)))
    ]


def list_public_endpoints(session: Session, *, limit: int = 100, offset: int = 0) -> list[EndpointDefinition]:
    return _list_routes_by_policy(
        session,
        limit=limit,
        offset=offset,
        selector=_is_public_contract_route,
    )


def list_legacy_fallback_endpoints(session: Session, *, limit: int = 100, offset: int = 0) -> list[EndpointDefinition]:
    return _list_routes_by_policy(
        session,
        limit=limit,
        offset=offset,
        selector=_uses_legacy_mock_fallback,
    )
