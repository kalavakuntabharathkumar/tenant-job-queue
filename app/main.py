import os,uuid,hashlib
from pathlib import Path
from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Header
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import Base,engine,get_db
from app.models import Job
from app.config import APP_ENV,UPLOAD_DIR
from app.auth import current_user,require_admin,create_token,Principal
from app.audit import record
from app.worker import process_csv
from pydantic import BaseModel
app=FastAPI(title='Multi-Tenant Job Queue and Analytics API')
Path(UPLOAD_DIR).mkdir(parents=True,exist_ok=True);Base.metadata.create_all(bind=engine)
class TokenRequest(BaseModel):
    user_id:str='demo-user';tenant_id:str='tenant-demo';role:str='analyst'
@app.get('/health')
def health():return {'status':'ok'}
@app.post('/dev/token')
def dev_token(b:TokenRequest):
    if APP_ENV!='development':raise HTTPException(404,'Not found')
    if b.role not in {'admin','analyst'}:raise HTTPException(422,'Role must be admin or analyst')
    return {'access_token':create_token(b.user_id,b.tenant_id,b.role),'token_type':'bearer'}
@app.post('/jobs')
async def submit(file:UploadFile=File(...),idempotency_key:str|None=Header(default=None,alias='Idempotency-Key'),user:Principal=Depends(current_user),db:Session=Depends(get_db)):
    if not file.filename or not file.filename.lower().endswith('.csv'):raise HTTPException(400,'Upload a .csv file')
    if not idempotency_key:raise HTTPException(400,'Idempotency-Key header required')
    key=f'{user.tenant_id}:{idempotency_key}';existing=db.scalar(select(Job).where(Job.idempotency_key==key))
    if existing:return {'job_id':existing.id,'status':existing.status,'deduplicated':True}
    content=await file.read()
    if len(content)>25*1024*1024:raise HTTPException(413,'CSV must be <=25MB')
    job_id=str(uuid.uuid4());name=hashlib.sha256(file.filename.encode()).hexdigest()[:12]+'-'+job_id+'.csv';path=os.path.join(UPLOAD_DIR,name)
    with open(path,'wb') as out:out.write(content)
    job=Job(id=job_id,tenant_id=user.tenant_id,owner_id=user.user_id,status='queued',file_path=path,idempotency_key=key)
    db.add(job);record(db,user.tenant_id,user.user_id,'job.submitted',job_id,file.filename);db.commit();process_csv.delay(job_id)
    return {'job_id':job_id,'status':'queued','deduplicated':False}
@app.get('/jobs')
def list_jobs(user:Principal=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Job).where(Job.tenant_id==user.tenant_id).order_by(Job.created_at.desc()).limit(100)).all()
    record(db,user.tenant_id,user.user_id,'job.listed',detail=f'count={len(rows)}');db.commit()
    return [{'job_id':j.id,'status':j.status,'created_at':j.created_at} for j in rows]
@app.get('/jobs/{job_id}')
def get_job(job_id:str,user:Principal=Depends(current_user),db:Session=Depends(get_db)):
    j=db.scalar(select(Job).where(Job.id==job_id,Job.tenant_id==user.tenant_id))
    if not j:raise HTTPException(404,'Job not found')
    record(db,user.tenant_id,user.user_id,'job.viewed',job_id);db.commit()
    return {'job_id':j.id,'status':j.status,'result':j.result,'error':j.error}
@app.delete('/jobs/{job_id}')
def delete_job(job_id:str,user:Principal=Depends(require_admin),db:Session=Depends(get_db)):
    j=db.scalar(select(Job).where(Job.id==job_id,Job.tenant_id==user.tenant_id))
    if not j:raise HTTPException(404,'Job not found')
    record(db,user.tenant_id,user.user_id,'job.deleted',job_id);db.delete(j);db.commit();return {'deleted':job_id}
@app.get('/audit')
def audit(user:Principal=Depends(require_admin),db:Session=Depends(get_db)):
    from app.models import AuditEvent
    rows=db.scalars(select(AuditEvent).where(AuditEvent.tenant_id==user.tenant_id).order_by(AuditEvent.created_at.desc()).limit(200)).all()
    return [{'id':e.id,'actor_id':e.actor_id,'action':e.action,'resource_id':e.resource_id,'detail':e.detail,'created_at':e.created_at} for e in rows]
