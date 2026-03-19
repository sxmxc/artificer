from __future__ import annotations

from typing import Callable

from sqlmodel import Session

from app.crud import list_endpoints
from app.models import EndpointDefinition
from app.services.admin_endpoint_policy import is_reserved_public_path
from app.services.route_status import RoutePublicationFacts, build_route_publication_status, load_route_publication_facts


def _is_public_contract_route(endpoint: EndpointDefinition, facts: RoutePublicationFacts | None) -> bool:
    if is_reserved_public_path(endpoint.path):
        return False
    return build_route_publication_status(endpoint, facts).is_public


def _uses_legacy_mock_fallback(endpoint: EndpointDefinition, facts: RoutePublicationFacts | None) -> bool:
    if is_reserved_public_path(endpoint.path):
        return False
    return build_route_publication_status(endpoint, facts).uses_legacy_mock


def _list_routes_by_policy(
    session: Session,
    *,
    limit: int,
    offset: int,
    selector: Callable[[EndpointDefinition, RoutePublicationFacts | None], bool],
) -> list[EndpointDefinition]:
    endpoints = list_endpoints(session, limit=limit, offset=offset)
    route_ids = [int(endpoint.id) for endpoint in endpoints if endpoint.id is not None]
    states = load_route_publication_facts(session, route_ids)
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
