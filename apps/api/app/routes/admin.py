from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session

from app.config import Settings
from app.crud import (
    create_endpoint,
    delete_endpoint,
    get_endpoint,
    list_endpoints,
    update_endpoint,
)
from app.db import get_session
from app.schemas import EndpointCreate, EndpointRead, EndpointUpdate

router = APIRouter()
security = HTTPBasic()
settings = Settings()


def require_admin(credentials: HTTPBasicCredentials = Depends(security)) -> None:
    if (
        credentials.username != settings.admin_username
        or credentials.password != settings.admin_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("/endpoints", response_model=list[EndpointRead])
def list_all_endpoints(session: Session = Depends(get_session), _: None = Depends(require_admin)):
    return list_endpoints(session)


@router.get("/endpoints/{endpoint_id}", response_model=EndpointRead)
def read_endpoint(endpoint_id: int, session: Session = Depends(get_session), _: None = Depends(require_admin)):
    endpoint = get_endpoint(session, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return endpoint


@router.post("/endpoints", response_model=EndpointRead, status_code=status.HTTP_201_CREATED)
def create_new_endpoint(endpoint_in: EndpointCreate, session: Session = Depends(get_session), _: None = Depends(require_admin)):
    return create_endpoint(session, endpoint_in)


@router.put("/endpoints/{endpoint_id}", response_model=EndpointRead)
def update_existing_endpoint(
    endpoint_id: int,
    endpoint_in: EndpointUpdate,
    session: Session = Depends(get_session),
    _: None = Depends(require_admin),
):
    endpoint = get_endpoint(session, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return update_endpoint(session, endpoint, endpoint_in)


@router.delete("/endpoints/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_endpoint(endpoint_id: int, session: Session = Depends(get_session), _: None = Depends(require_admin)):
    endpoint = get_endpoint(session, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    delete_endpoint(session, endpoint)
