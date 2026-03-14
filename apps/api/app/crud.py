from __future__ import annotations

from typing import List, Optional

from sqlmodel import Session, select

from app.models import EndpointDefinition
from app.schemas import EndpointCreate, EndpointUpdate


def get_endpoint(session: Session, endpoint_id: int) -> Optional[EndpointDefinition]:
    return session.get(EndpointDefinition, endpoint_id)


def get_endpoint_by_path(session: Session, path: str, method: str) -> Optional[EndpointDefinition]:
    statement = select(EndpointDefinition).where(
        EndpointDefinition.path == path,
        EndpointDefinition.method == method.upper(),
        EndpointDefinition.enabled == True,
    )
    return session.exec(statement).first()


def list_endpoints(session: Session, limit: int = 100, offset: int = 0) -> List[EndpointDefinition]:
    statement = select(EndpointDefinition).offset(offset).limit(limit)
    return session.exec(statement).all()


def create_endpoint(session: Session, endpoint_in: EndpointCreate) -> EndpointDefinition:
    endpoint = EndpointDefinition(**endpoint_in.dict())
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)
    return endpoint


def update_endpoint(session: Session, endpoint: EndpointDefinition, endpoint_in: EndpointUpdate) -> EndpointDefinition:
    data = endpoint_in.dict(exclude_unset=True)
    for key, value in data.items():
        setattr(endpoint, key, value)
    session.add(endpoint)
    session.commit()
    session.refresh(endpoint)
    return endpoint


def delete_endpoint(session: Session, endpoint: EndpointDefinition) -> None:
    session.delete(endpoint)
    session.commit()
