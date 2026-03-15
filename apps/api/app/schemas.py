from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class EndpointBase(BaseModel):
    name: str
    slug: str
    method: str
    path: str
    category: Optional[str] = None
    tags: Optional[List[str]] = Field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None
    enabled: bool = True
    auth_mode: str = "none"
    request_schema: Optional[Dict[str, Any]] = Field(default_factory=dict)
    response_schema: Optional[Dict[str, Any]] = Field(default_factory=dict)
    success_status_code: int = 200
    error_rate: float = 0.0
    latency_min_ms: int = 0
    latency_max_ms: int = 0
    seed_key: Optional[str] = None


class EndpointCreate(EndpointBase):
    pass


class EndpointUpdate(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    method: Optional[str]
    path: Optional[str]
    category: Optional[str]
    tags: Optional[List[str]]
    summary: Optional[str]
    description: Optional[str]
    enabled: Optional[bool]
    auth_mode: Optional[str]
    request_schema: Optional[Dict[str, Any]]
    response_schema: Optional[Dict[str, Any]]
    success_status_code: Optional[int]
    error_rate: Optional[float]
    latency_min_ms: Optional[int]
    latency_max_ms: Optional[int]
    seed_key: Optional[str]


class EndpointRead(EndpointBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PreviewRequest(BaseModel):
    response_schema: Dict[str, Any] = Field(default_factory=dict)
    seed_key: Optional[str] = None


class PreviewResponse(BaseModel):
    preview: Any


class PublicEndpointReference(BaseModel):
    id: int
    name: str
    method: str
    path: str
    example_path: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    description: Optional[str] = None
    success_status_code: int
    request_schema: Dict[str, Any] = Field(default_factory=dict)
    response_schema: Dict[str, Any] = Field(default_factory=dict)
    sample_response: Any = None
    updated_at: datetime


class PublicReferenceResponse(BaseModel):
    product_name: str
    description: str
    endpoint_count: int
    refreshed_at: datetime
    endpoints: List[PublicEndpointReference] = Field(default_factory=list)
