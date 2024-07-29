import bcrypt
from datetime import datetime, timedelta
from typing import Union, Any
from fastapi import HTTPException
from jose import jwt
from sqlalchemy.orm import Session

from models import User


ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

class UserAuthenticationService:
    @classmethod
    
    def hash_password(cls, password: str) -> str:
        # Hash a password using bcrypt
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')
    
    def verify_password(cls, password:str, hashed_password:str) -> bool:
        isPasswordCorrect = bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        return isPasswordCorrect

    def create_access_token(self,subject: Union[str, Any],role:str ,expires_delta: datetime = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
        to_encode = {"exp": expires_delta, "sub": str(subject),"role":role}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
        return encoded_jwt
    
    
    def create_refresh_token(self,subject: Union[str, Any],role:str, expires_delta: datetime = datetime.utcnow()+timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)) -> str:
        to_encode = {"exp": expires_delta, "sub": str(subject),"role":role}
        encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        return encoded_jwt
    
    def decode_jwt(self, jwtoken: str):
        try:
            decoded_token = jwt.decode(jwtoken, JWT_SECRET_KEY, algorithms=[ALGORITHM])
            return decoded_token
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=403, detail="Token has expired.")
        except jwt.JWTError as e:
            raise HTTPException(status_code=403, detail="Invalid token.")

    def decode_access_return_user(self, jwtoken: str, db: Session) -> User:
        payload = self.decode_jwt(jwtoken)
        user_id = payload.get("sub")
        if user_id:
            user = db.query(User).filter(User.id == int(user_id)).first()
            if user:
                return user
        raise HTTPException(status_code=403, detail="User not found.")
