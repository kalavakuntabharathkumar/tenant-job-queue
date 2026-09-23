from app.auth import create_token
from jose import jwt
from app.config import JWT_SECRET,JWT_ALGORITHM
def test_jwt_contains_tenant_role():
    p=jwt.decode(create_token('u','t','analyst'),JWT_SECRET,algorithms=[JWT_ALGORITHM])
    assert p['tenant_id']=='t' and p['role']=='analyst'
