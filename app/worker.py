import pandas as pd
from celery import Celery
from sqlalchemy import create_engine
from app.config import REDIS_URL,DATABASE_URL
from app.database import SessionLocal,Base,engine
from app.models import Job,now
celery_app=Celery('analytics',broker=REDIS_URL,backend=REDIS_URL)
celery_app.conf.update(task_acks_late=True,worker_prefetch_multiplier=1,task_serializer='json',accept_content=['json'],result_serializer='json')
@celery_app.task(bind=True,autoretry_for=(OSError,),retry_backoff=True,retry_kwargs={'max_retries':3})
def process_csv(self,job_id):
    Base.metadata.create_all(bind=engine);db=SessionLocal()
    try:
        job=db.get(Job,job_id)
        if not job:return {'status':'missing'}
        job.status='running';job.updated_at=now();db.commit()
        df=pd.read_csv(job.file_path)
        job.result={'rows':int(len(df)),'columns':list(map(str,df.columns)),'missing_by_column':{str(k):int(v) for k,v in df.isna().sum().items()},'duplicate_rows':int(df.duplicated().sum())}
        job.status='completed';job.updated_at=now();db.commit();return {'job_id':job_id,'status':'completed'}
    except Exception as exc:
        db.rollback();job=db.get(Job,job_id)
        if job:job.status='failed';job.error=type(exc).__name__;job.updated_at=now();db.commit()
        raise
    finally:db.close()
