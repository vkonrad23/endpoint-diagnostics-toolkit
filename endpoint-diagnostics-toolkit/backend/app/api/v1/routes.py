from fastapi import APIRouter,Depends,HTTPException,Query,Response,status
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.diagnostics.system import collect_system,demo_system
from app.diagnostics.network import NetworkRequest,run_network,demo_network
from app.incidents.models import Incident,Note,Device
from app.incidents.schemas import IncidentCreate,IncidentPatch,IncidentOut,NoteCreate,NoteOut,DeviceCreate,DeviceOut
from app.reports.exporters import build_report,to_json,to_markdown
router=APIRouter(prefix="/api/v1")
@router.get("/health")
def health(): return {"status":"ok","version":settings.version}
@router.get("/diagnostics/system")
def system_diagnostics(demo:bool=False): return demo_system() if demo or settings.demo_mode else collect_system(settings.show_hostname)
@router.post("/diagnostics/network")
def network_diagnostics(req:NetworkRequest,demo:bool=False): return demo_network(req) if demo or settings.demo_mode else run_network(req)
@router.get("/incidents")
def list_incidents(db:Session=Depends(get_db),status_:str|None=Query(None,alias="status"),priority:str|None=None,category:str|None=None,q:str|None=None,page:int=Query(1,ge=1),size:int=Query(20,ge=1,le=100)):
    stmt=select(Incident)
    for col,val in [(Incident.status,status_),(Incident.priority,priority),(Incident.category,category)]:
        if val: stmt=stmt.where(col==val)
    if q: stmt=stmt.where(Incident.title.ilike(f"%{q}%"))
    total=db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items=db.scalars(stmt.order_by(Incident.created_at.desc()).offset((page-1)*size).limit(size)).all()
    return {"items":[IncidentOut.model_validate(x) for x in items],"total":total,"page":page}
@router.post("/incidents",response_model=IncidentOut,status_code=201)
def create_incident(data:IncidentCreate,db:Session=Depends(get_db)):
    obj=Incident(**data.model_dump()); db.add(obj); db.commit(); db.refresh(obj); return obj
@router.get("/incidents/{incident_id}",response_model=IncidentOut)
def get_incident(incident_id:int,db:Session=Depends(get_db)):
    obj=db.get(Incident,incident_id)
    if not obj: raise HTTPException(404,"Incident not found")
    return obj
@router.patch("/incidents/{incident_id}",response_model=IncidentOut)
def update_incident(incident_id:int,data:IncidentPatch,db:Session=Depends(get_db)):
    obj=db.get(Incident,incident_id)
    if not obj: raise HTTPException(404,"Incident not found")
    for k,v in data.model_dump(exclude_unset=True).items(): setattr(obj,k,v)
    db.commit(); db.refresh(obj); return obj
@router.delete("/incidents/{incident_id}",status_code=204)
def delete_incident(incident_id:int,db:Session=Depends(get_db)):
    obj=db.get(Incident,incident_id)
    if not obj: raise HTTPException(404,"Incident not found")
    db.delete(obj); db.commit(); return Response(status_code=204)
@router.post("/incidents/{incident_id}/notes",response_model=NoteOut,status_code=201)
def add_note(incident_id:int,data:NoteCreate,db:Session=Depends(get_db)):
    if not db.get(Incident,incident_id): raise HTTPException(404,"Incident not found")
    note=Note(incident_id=incident_id,**data.model_dump()); db.add(note); db.commit(); db.refresh(note); return note
@router.get("/reports/{incident_id}.json")
def report_json(incident_id:int,db:Session=Depends(get_db)):
    obj=db.get(Incident,incident_id)
    if not obj: raise HTTPException(404,"Incident not found")
    report=build_report(IncidentOut.model_validate(obj).model_dump(mode="json"),version=settings.version)
    return Response(to_json(report),media_type="application/json",headers={"Content-Disposition":f"attachment; filename=incident-{incident_id}.json"})
@router.get("/reports/{incident_id}.md")
def report_md(incident_id:int,db:Session=Depends(get_db)):
    obj=db.get(Incident,incident_id)
    if not obj: raise HTTPException(404,"Incident not found")
    report=build_report(IncidentOut.model_validate(obj).model_dump(mode="json"),version=settings.version)
    return Response(to_markdown(report),media_type="text/markdown",headers={"Content-Disposition":f"attachment; filename=incident-{incident_id}.md"})
@router.get("/devices",response_model=list[DeviceOut])
def devices(db:Session=Depends(get_db)): return db.scalars(select(Device).order_by(Device.last_seen_at.desc())).all()
@router.post("/devices",response_model=DeviceOut,status_code=201)
def add_device(data:DeviceCreate,db:Session=Depends(get_db)):
    d=Device(**data.model_dump()); db.add(d); db.commit(); db.refresh(d); return d
@router.delete("/history",status_code=204)
def clear_history(db:Session=Depends(get_db)):
    for x in db.scalars(select(Incident)).all(): db.delete(x)
    db.commit(); return Response(status_code=204)
