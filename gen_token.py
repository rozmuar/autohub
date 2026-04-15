import sys, json
sys.path.insert(0, '/app')
from app.core.security import create_access_token
token = create_access_token({'sub': 'f5c03ba6-7faf-468f-bf8a-0a4870fc3735', 'type': 'access', 'role': 'client'})
print(token)
