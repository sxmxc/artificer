from __future__ import annotations

from sqlmodel import Session, select

from app.crud import create_endpoint
from app.db import get_session
from app.models import EndpointDefinition
from app.schemas import EndpointCreate


def _upsert_endpoint(session: Session, payload: EndpointCreate) -> EndpointDefinition:
    statement = select(EndpointDefinition).where(EndpointDefinition.slug == payload.slug)
    existing = session.exec(statement).first()
    if existing:
        for key, value in payload.dict().items():
            setattr(existing, key, value)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    return create_endpoint(session, payload)


def seed():
    seeds = [
        EndpointCreate(
            name="List Quotes",
            slug="list-quotes",
            method="GET",
            path="/api/quotes",
            category="quotes",
            summary="List funny quotes",
            description="Returns a list of randomly generated joke-style quotes.",
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "quote": {"type": "string"},
                        "author": {"type": "string"},
                    },
                },
            },
            example_template=[
                {"id": "q1", "quote": "We do not fear technical debt. We refinance it emotionally.", "author": "Captain Spreadsheet"}
            ],
        ),
        EndpointCreate(
            name="Random Quote",
            slug="random-quote",
            method="GET",
            path="/api/quotes/random",
            category="quotes",
            summary="Get a random quote",
            response_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "quote": {"type": "string"},
                    "author": {"type": "string"},
                },
            },
            example_template={
                "id": "q-random",
                "quote": "Don't worry, our mocks never lie (unless we want them to).",
                "author": "Senior Button Optimizer",
            },
        ),
        EndpointCreate(
            name="List Users",
            slug="list-users",
            method="GET",
            path="/api/users",
            category="users",
            summary="List users",
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "displayName": {"type": "string"},
                        "email": {"type": "string"},
                    },
                },
            },
            example_template=[
                {
                    "id": "user-1",
                    "displayName": "Captain Spreadsheet",
                    "email": "captain.spreadsheet@example.mock",
                }
            ],
        ),
        EndpointCreate(
            name="Get User",
            slug="get-user",
            method="GET",
            path="/api/users/{id}",
            category="users",
            summary="Get a user by ID",
            response_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "displayName": {"type": "string"},
                    "email": {"type": "string"},
                    "role": {"type": "string"},
                },
            },
            example_template={
                "id": "user-42",
                "displayName": "Vice President of Napping",
                "email": "vp.naps@mockservice.io",
                "role": "Senior Button Optimizer",
            },
        ),
        EndpointCreate(
            name="Create User",
            slug="create-user",
            method="POST",
            path="/api/users",
            category="users",
            summary="Create a new user",
            request_schema={
                "type": "object",
                "properties": {
                    "displayName": {"type": "string"},
                    "email": {"type": "string"},
                },
                "required": ["displayName", "email"],
            },
            response_schema={
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "displayName": {"type": "string"},
                    "email": {"type": "string"},
                    "createdAt": {"type": "string", "format": "date-time"},
                },
            },
            example_template={
                "id": "user-new",
                "displayName": "New User",
                "email": "new.user@mockservice.io",
                "createdAt": "2026-01-01T00:00:00Z",
            },
            success_status_code=201,
        ),
        EndpointCreate(
            name="List Devices",
            slug="list-devices",
            method="GET",
            path="/api/devices",
            category="devices",
            summary="List devices",
            response_schema={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "deviceId": {"type": "string"},
                        "model": {"type": "string"},
                        "status": {"type": "string"},
                    },
                },
            },
            example_template=[
                {
                    "deviceId": "device-123",
                    "model": "OctoCam 3000",
                    "status": "Device rejected request due to insufficient vibes",
                }
            ],
        ),
        EndpointCreate(
            name="Get Device",
            slug="get-device",
            method="GET",
            path="/api/devices/{deviceId}",
            category="devices",
            summary="Get device details",
            response_schema={
                "type": "object",
                "properties": {
                    "deviceId": {"type": "string"},
                    "model": {"type": "string"},
                    "status": {"type": "string"},
                    "lastSeen": {"type": "string", "format": "date-time"},
                },
            },
            example_template={
                "deviceId": "device-123",
                "model": "OctoCam 3000",
                "status": "All systems are go, mostly.",
                "lastSeen": "2026-03-14T12:34:56Z",
            },
        ),
        EndpointCreate(
            name="Trigger Something",
            slug="trigger-something",
            method="POST",
            path="/api/devices/{deviceId}/trigger-something",
            category="devices",
            summary="Trigger a device action",
            request_schema={
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                },
                "required": ["action"],
            },
            response_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                },
            },
            example_template={
                "status": "ok",
                "message": "The device is now performing the thing you asked for. Maybe.",
            },
        ),
        EndpointCreate(
            name="Get Something",
            slug="get-something",
            method="GET",
            path="/api/devices/{deviceId}/get-something",
            category="devices",
            summary="Get device derived data",
            response_schema={
                "type": "object",
                "properties": {
                    "details": {"type": "string"},
                    "query": {"type": "string"},
                },
            },
            example_template={
                "details": "The device reports that it is currently 73% sure it understands you.",
                "query": "please provide something",
            },
        ),
        EndpointCreate(
            name="Create Order",
            slug="create-order",
            method="POST",
            path="/api/orders",
            category="orders",
            summary="Create an order",
            request_schema={
                "type": "object",
                "properties": {
                    "productId": {"type": "string"},
                    "quantity": {"type": "integer"},
                },
                "required": ["productId", "quantity"],
            },
            response_schema={
                "type": "object",
                "properties": {
                    "orderId": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            example_template={
                "orderId": "order-999",
                "status": "pending",
            },
            success_status_code=201,
        ),
        EndpointCreate(
            name="Get Order",
            slug="get-order",
            method="GET",
            path="/api/orders/{id}",
            category="orders",
            summary="Get an order",
            response_schema={
                "type": "object",
                "properties": {
                    "orderId": {"type": "string"},
                    "status": {"type": "string"},
                    "total": {"type": "number"},
                },
            },
            example_template={
                "orderId": "order-999",
                "status": "processing",
                "total": 42.42,
            },
        ),
        EndpointCreate(
            name="Authorize Payment",
            slug="authorize-payment",
            method="POST",
            path="/api/payments/authorize",
            category="payments",
            summary="Authorize a payment",
            request_schema={
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "currency": {"type": "string"},
                    "cardLast4": {"type": "string"},
                },
                "required": ["amount", "currency", "cardLast4"],
            },
            response_schema={
                "type": "object",
                "properties": {
                    "transactionId": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            example_template={
                "transactionId": "txn-abc-123",
                "status": "authorized",
            },
        ),
        EndpointCreate(
            name="Report Generation Job",
            slug="report-job",
            method="POST",
            path="/api/jobs/report-generation",
            category="jobs",
            summary="Create a report generation job",
            request_schema={
                "type": "object",
                "properties": {
                    "reportType": {"type": "string"},
                },
                "required": ["reportType"],
            },
            response_schema={
                "type": "object",
                "properties": {
                    "jobId": {"type": "string"},
                    "status": {"type": "string"},
                },
            },
            example_template={
                "jobId": "job-42",
                "status": "pending",
            },
            success_status_code=202,
        ),
        EndpointCreate(
            name="Job Status",
            slug="job-status",
            method="GET",
            path="/api/jobs/{jobId}/status",
            category="jobs",
            summary="Get job status",
            response_schema={
                "type": "object",
                "properties": {
                    "jobId": {"type": "string"},
                    "status": {"type": "string"},
                    "progress": {"type": "number"},
                },
            },
            example_template={
                "jobId": "job-42",
                "status": "in_progress",
                "progress": 73,
            },
        ),
        EndpointCreate(
            name="Health",
            slug="health",
            method="GET",
            path="/api/health",
            category="system",
            summary="Health check",
            response_schema={
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                },
            },
            example_template={"status": "ok"},
        ),
    ]

    with get_session() as session:
        for seed in seeds:
            _upsert_endpoint(session, seed)


if __name__ == "__main__":
    seed()
