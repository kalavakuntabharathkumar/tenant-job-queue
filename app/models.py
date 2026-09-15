from datetime import datetime,timezone
from sqlalchemy import String,Integer,DateTime,Text,JSON,Index
from sqlalchemy.orm import Mapped,mapped_column
from app.database import Base
def now(): return datetime.now(timezone.utc)
class Job(Base):
    __tablename__='jobs'
    __table_args__=(Index('ix_jobs_tenant_created','tenant_id','created_at'),)
    id:Mapped[str]=mapped_column(String(36),primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(100),index=True)
    owner_id:Mapped[str]=mapped_column(String(100))
    status:Mapped[str]=mapped_column(String(20),default='queued',index=True)
    file_path:Mapped[str]=mapped_column(Text)
    idempotency_key:Mapped[str]=mapped_column(String(200),unique=True)
    result:Mapped[dict|None]=mapped_column(JSON,nullable=True)
    error:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now,onupdate=now)
class AuditEvent(Base):
    __tablename__='audit_events'
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    tenant_id:Mapped[str]=mapped_column(String(100),index=True)
    actor_id:Mapped[str]=mapped_column(String(100))
    action:Mapped[str]=mapped_column(String(100))
    resource_id:Mapped[str|None]=mapped_column(String(200),nullable=True)
    detail:Mapped[str|None]=mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=now)
