import os
DATABASE_URL=os.getenv('DATABASE_URL','postgresql+psycopg://postgres:postgres@localhost:5432/jobs')
if DATABASE_URL.startswith('postgresql://'): DATABASE_URL=DATABASE_URL.replace('postgresql://','postgresql+psycopg://',1)
REDIS_URL=os.getenv('REDIS_URL','redis://localhost:6379/0')
JWT_SECRET=os.getenv('JWT_SECRET','dev-only-change-me')
JWT_ALGORITHM=os.getenv('JWT_ALGORITHM','HS256')
TOKEN_MINUTES=int(os.getenv('ACCESS_TOKEN_MINUTES','60'))
APP_ENV=os.getenv('APP_ENV','development')
UPLOAD_DIR=os.getenv('UPLOAD_DIR','./data/uploads')
