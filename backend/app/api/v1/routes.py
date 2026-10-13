from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.diagnostics.network import NetworkRequest, demo_network, run_network
from app.diagnostics.system import collect_system, demo_system
from app.incidents.models import Device, Incident, Note
from app.incidents.schemas import (
    DeviceCreate,
    DeviceOut,
    IncidentCreate,
    IncidentOut,
    IncidentPatch,
    NoteCreate,
    NoteOut,
)
from app.reports.exporters import build_report, to_json, to_markdown

DbSession = Annotated[Session, Depends(get_db)]

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health():
    return {
        "status": "ok",
        "version": settings.version,
    }


@router.get("/diagnostics/system")
def system_diagnostics(demo: bool = False):
    if demo or settings.demo_mode:
        return demo_system()

    return collect_system(settings.show_hostname)


@router.post("/diagnostics/network")
def network_diagnostics(
    request: NetworkRequest,
    demo: bool = False,
):
    if demo or settings.demo_mode:
        return demo_network(request)

    return run_network(request)


@router.get("/incidents")
def list_incidents(
    db: DbSession,
    status_: str | None = Query(default=None, alias="status"),
    priority: str | None = None,
    category: str | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    statement = select(Incident)

    filters = (
        (Incident.status, status_),
        (Incident.priority, priority),
        (Incident.category, category),
    )

    for column, value in filters:
        if value:
            statement = statement.where(column == value)

    if q:
        statement = statement.where(Incident.title.ilike(f"%{q.strip()}%"))

    total_statement = select(func.count()).select_from(statement.subquery())
    total = db.scalar(total_statement) or 0

    statement = statement.order_by(Incident.created_at.desc()).offset((page - 1) * size).limit(size)

    incidents = db.scalars(statement).all()

    return {
        "items": [IncidentOut.model_validate(incident) for incident in incidents],
        "total": total,
        "page": page,
    }


@router.post(
    "/incidents",
    response_model=IncidentOut,
    status_code=201,
)
def create_incident(
    data: IncidentCreate,
    db: DbSession,
):
    incident = Incident(**data.model_dump())

    db.add(incident)
    db.commit()
    db.refresh(incident)

    return incident


@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentOut,
)
def get_incident(
    incident_id: int,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.patch(
    "/incidents/{incident_id}",
    response_model=IncidentOut,
)
def update_incident(
    incident_id: int,
    data: IncidentPatch,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    updates = data.model_dump(exclude_unset=True)

    for field_name, value in updates.items():
        setattr(incident, field_name, value)

    db.commit()
    db.refresh(incident)

    return incident


@router.delete(
    "/incidents/{incident_id}",
    status_code=204,
)
def delete_incident(
    incident_id: int,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    db.delete(incident)
    db.commit()

    return Response(status_code=204)


@router.post(
    "/incidents/{incident_id}/notes",
    response_model=NoteOut,
    status_code=201,
)
def add_note(
    incident_id: int,
    data: NoteCreate,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    note = Note(
        incident_id=incident_id,
        **data.model_dump(),
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


@router.get("/reports/{incident_id}.json")
def report_json(
    incident_id: int,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    incident_data = IncidentOut.model_validate(incident).model_dump(mode="json")

    report = build_report(
        incident_data,
        version=settings.version,
    )

    return Response(
        content=to_json(report),
        media_type="application/json",
        headers={"Content-Disposition": (f'attachment; filename="incident-{incident_id}.json"')},
    )


@router.get("/reports/{incident_id}.md")
def report_markdown(
    incident_id: int,
    db: DbSession,
):
    incident = db.get(Incident, incident_id)

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    incident_data = IncidentOut.model_validate(incident).model_dump(mode="json")

    report = build_report(
        incident_data,
        version=settings.version,
    )

    return Response(
        content=to_markdown(report),
        media_type="text/markdown",
        headers={"Content-Disposition": (f'attachment; filename="incident-{incident_id}.md"')},
    )


@router.get(
    "/devices",
    response_model=list[DeviceOut],
)
def list_devices(
    db: DbSession,
):
    statement = select(Device).order_by(Device.last_seen_at.desc())

    return db.scalars(statement).all()


@router.post(
    "/devices",
    response_model=DeviceOut,
    status_code=201,
)
def add_device(
    data: DeviceCreate,
    db: DbSession,
):
    device = Device(**data.model_dump())

    db.add(device)
    db.commit()
    db.refresh(device)

    return device


@router.delete(
    "/history",
    status_code=204,
)
def clear_history(
    db: DbSession,
):
    incidents = db.scalars(select(Incident)).all()

    for incident in incidents:
        db.delete(incident)

    db.commit()

    return Response(status_code=204)
