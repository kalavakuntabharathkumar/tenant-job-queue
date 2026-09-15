from app.models import AuditEvent
def record(db,tenant_id,actor_id,action,resource_id=None,detail=None):
    db.add(AuditEvent(tenant_id=tenant_id,actor_id=actor_id,action=action,resource_id=resource_id,detail=detail));db.flush()
