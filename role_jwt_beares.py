from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException
from jose import jwt
from models import User
from fastapi import  Depends, HTTPException
from sqlalchemy.orm import Session
from dependencies import get_db_session

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"  # should be kept secret

class RoleJWTBearer(HTTPBearer):
    def __init__(self,  auto_error: bool = True):
        super(RoleJWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db_session)):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            if not self.if_refresh_token_available(credentials.credentials, db):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            if not self.validate_role(credentials.credentials):
                raise HTTPException(status_code=404, detail=f"Insufficient permissions. Required role: Organizer")
            return self.get_user_from_token(credentials.credentials, db) 
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
        
    def get_user_from_token(self, jwtoken: str, db: Session) -> User:
        payload = self.decode_jwt(jwtoken)
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                return user
        raise HTTPException(status_code=403, detail="User not found.")
    
    def if_refresh_token_available(self, jwtoken: str, db: Session) -> User:
        payload = self.decode_jwt(jwtoken)
        user_id = payload.get("sub")
        try:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user.refresh_token is None:
                return False
            return True
        except:
            raise HTTPException(status_code=403, detail="User not found.")
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            self.decode_jwt(jwtoken)
            return True
        except:
            return False

    def decode_jwt(self, jwtoken: str):
        try:
            decoded_token = jwt.decode(jwtoken, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired.")
        except jwt.JWTError as e:
            raise HTTPException(status_code=403, detail="Invalid token.")

    def validate_role(self, jwtoken: str) -> bool:
        payload = jwt.decode(jwtoken, JWT_SECRET_KEY, algorithms=ALGORITHM)
        if "role" in payload:
            return payload["role"] == "Organizer" or payload["role"]=="Admin"
        return False

# Example of usage:
jwt_bearer_organizer = RoleJWTBearer()

