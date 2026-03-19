from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import desc, select
from sqlmodel import Session

from app.models import EndpointDefinition, RouteDeployment, RouteImplementation
from app.schemas import EndpointRead, RoutePublicationStatus


@dataclass(slots=True)
class RoutePublicationFacts:
    has_saved_implementation: bool = False
    has_deployment_history: bool = False
    has_active_deployment: bool = False
    active_deployment_environment: str | None = None
    active_implementation_id: int | None = None
    active_deployment_id: int | None = None

    @property
    def has_runtime_history(self) -> bool:
        return self.has_saved_implementation or self.has_deployment_history


def load_route_publication_facts(
    session: Session,
    route_ids: Iterable[int],
) -> dict[int, RoutePublicationFacts]:
    normalized_route_ids = sorted({int(route_id) for route_id in route_ids if route_id is not None})
    if not normalized_route_ids:
        return {}

    facts_by_route_id: dict[int, RoutePublicationFacts] = {}

    implementation_route_ids = session.execute(
        select(RouteImplementation.route_id)
        .where(RouteImplementation.route_id.in_(normalized_route_ids))
        .distinct()
    ).scalars()
    for route_id in implementation_route_ids:
        if route_id is None:
            continue
        facts_by_route_id[int(route_id)] = RoutePublicationFacts(has_saved_implementation=True)

    deployment_rows = session.execute(
        select(
            RouteDeployment.route_id,
            RouteDeployment.id,
            RouteDeployment.implementation_id,
            RouteDeployment.environment,
            RouteDeployment.is_active,
        )
        .where(RouteDeployment.route_id.in_(normalized_route_ids))
        .order_by(RouteDeployment.route_id, desc(RouteDeployment.published_at), desc(RouteDeployment.id))
    ).all()

    for route_id, deployment_id, implementation_id, environment, is_active in deployment_rows:
        if route_id is None:
            continue

        facts = facts_by_route_id.setdefault(int(route_id), RoutePublicationFacts())
        facts.has_deployment_history = True

        if is_active and not facts.has_active_deployment:
            facts.has_active_deployment = True
            facts.active_deployment_environment = str(environment or "").strip() or None
            facts.active_implementation_id = int(implementation_id) if implementation_id is not None else None
            facts.active_deployment_id = int(deployment_id) if deployment_id is not None else None

    return facts_by_route_id


def build_route_publication_status(
    endpoint: EndpointDefinition,
    facts: RoutePublicationFacts | None = None,
) -> RoutePublicationStatus:
    current_facts = facts or RoutePublicationFacts()
    enabled = bool(endpoint.enabled)

    if not enabled:
        code = "disabled"
        label = "Disabled"
        tone = "error"
    elif current_facts.has_active_deployment:
        code = "published_live"
        label = "Published live"
        tone = "success"
    elif current_facts.has_deployment_history:
        code = "live_disabled"
        label = "Live disabled"
        tone = "warning"
    elif current_facts.has_saved_implementation:
        code = "draft_only"
        label = "Draft only"
        tone = "warning"
    else:
        code = "legacy_mock"
        label = "Legacy mock"
        tone = "secondary"

    return RoutePublicationStatus(
        code=code,
        label=label,
        tone=tone,
        enabled=enabled,
        is_public=enabled and code in {"published_live", "legacy_mock"},
        is_live=code == "published_live",
        uses_legacy_mock=code == "legacy_mock",
        has_saved_implementation=current_facts.has_saved_implementation,
        has_runtime_history=current_facts.has_runtime_history,
        has_deployment_history=current_facts.has_deployment_history,
        has_active_deployment=current_facts.has_active_deployment,
        active_deployment_environment=current_facts.active_deployment_environment,
        active_implementation_id=current_facts.active_implementation_id,
        active_deployment_id=current_facts.active_deployment_id,
    )


def build_endpoint_read(
    endpoint: EndpointDefinition,
    publication_status: RoutePublicationStatus | None = None,
) -> EndpointRead:
    resolved_publication_status = publication_status or build_route_publication_status(endpoint)
    auth_mode = endpoint.auth_mode.value if hasattr(endpoint.auth_mode, "value") else str(endpoint.auth_mode)

    return EndpointRead(
        id=int(endpoint.id or 0),
        name=endpoint.name,
        slug=endpoint.slug,
        method=endpoint.method,
        path=endpoint.path,
        category=endpoint.category,
        tags=endpoint.tags or [],
        summary=endpoint.summary,
        description=endpoint.description,
        enabled=bool(endpoint.enabled),
        auth_mode=auth_mode,
        request_schema=endpoint.request_schema or {},
        response_schema=endpoint.response_schema or {},
        success_status_code=int(endpoint.success_status_code or 200),
        error_rate=float(endpoint.error_rate or 0),
        latency_min_ms=int(endpoint.latency_min_ms or 0),
        latency_max_ms=int(endpoint.latency_max_ms or 0),
        seed_key=endpoint.seed_key,
        created_at=endpoint.created_at,
        updated_at=endpoint.updated_at,
        publication_status=resolved_publication_status,
    )
