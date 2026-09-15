from datetime import datetime,timedelta,timezone
from jose import jwt,JWTError
from fastapi import Depends,HTTPException
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.config import JWT_SECRET,JWT_ALGORITHM,TOKEN_MINUTES
bearer=HTTPBearer(auto_error=False)
class Principal(BaseModel):
    user_id:str
    tenant_id:str
    role:str
def create_token(user_id,tenant_id,role):
    exp=datetime.now(timezone.utc)+timedelta(minutes=TOKEN_MINUTES)
    return jwt.encode({'sub':user_id,'tenant_id':tenant_id,'role':role,'exp':exp},JWT_SECRET,algorithm=JWT_ALGORITHM)
async def current_user(creds:HTTPAuthorizationCredentials|None=Depends(bearer)):
    if not creds: raise HTTPException(401,'Bearer token required')
    try:
        p=jwt.decode(creds.credentials,JWT_SECRET,algorithms=[JWT_ALGORITHM]); role=p.get('role')
        if role not in {'admin','analyst'}: raise ValueError()
        return Principal(user_id=p['sub'],tenant_id=p['tenant_id'],role=role)
    except (JWTError,KeyError,ValueError): raise HTTPException(401,'Invalid or expired token')
def require_admin(user:Principal=Depends(current_user)):
    if user.role!='admin': raise HTTPException(403,'Admin role required')
    return user
