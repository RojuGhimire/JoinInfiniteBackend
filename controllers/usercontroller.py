# controllers/controller1.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.userAutenticationService import UserAuthenticationService
from models import User, UserRole, Event, UserInteraction
from schemas import UserCreate, UserResponse, LoginDetails, UserProfilePhotoUpdate, LocationDetails, RefreshToken, UserPasswordUpdate, UserUpdate
from dependencies import get_db_session
from auth_bearer import JWTBearer
from jose import jwt
import datetime
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()
authenticationService = UserAuthenticationService()
ALGORITHM = "HS256"
JWT_SECRET_KEY = "narscbjim@$@&^@&%^&RFghgjvbdsha"   # should be kept secret
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
JWT_REFRESH_SECRET_KEY = "13ugfdfgh@#$%^@&jkl45678902"

@router.get("",response_model=list[UserResponse])
def get_all_users(current_user:User = Depends(JWTBearer()), db:Session = Depends(get_db_session)):
    if(current_user.role.lower() != 'admin'):
        raise HTTPException(status_code=401, detail="Only admin can access this")
    users = db.query(User).all()
    return users


@router.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_db_session)):
    existing_user = session.query(User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = authenticationService.hash_password(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=user.role,
        age=user.age,
        address=user.address,
        interested_genre=user.interested_genre
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return {"message": "User registered by controller 1"}

@router.post("/login")
def login(request: LoginDetails,db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code= 400, detail="Incorrect email")
    if user.role.lower() == 'admin':
        raise HTTPException(status_code=401, detail="Invalid request")
    hashed_pass = user.password
    if not authenticationService.verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )
        
    refresh_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access= authenticationService.create_access_token(subject=user.id, role=user.role,expires_delta=access_token_expiry)
    refresh = authenticationService.create_refresh_token(subject=user.id,role=user.role, expires_delta=refresh_token_expiry)
    user.refresh_token_expiry=refresh_token_expiry
    user.refresh_token=refresh

    user_details =  {"id":user.id, "username":user.username,"email": user.email,"age":user.age, "address":user.address,"photo_url":user.photo_url, "interested_genre":user.interested_genre,"latitude":user.latitude, "longitude":user.longitude,"role":user.role}

    db.commit()
    db.refresh(user)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "user_details":user_details
    }

@router.post("/admin/login")
def admin_login(request: LoginDetails,db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code= 400, detail="Incorrect email")
    if user.role.lower() != 'admin':
        raise HTTPException(status_code=401, detail="Invalid request")
    hashed_pass = user.password
    if not authenticationService.verify_password(request.password, hashed_pass):
        raise HTTPException(
            status_code=400,
            detail="Incorrect password"
        )
    
    refresh_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access= authenticationService.create_access_token(subject=user.id, role=user.role,expires_delta=access_token_expiry)
    refresh = authenticationService.create_refresh_token(subject=user.id,role=user.role, expires_delta=refresh_token_expiry)
    user.refresh_token_expiry=refresh_token_expiry
    user.refresh_token=refresh

    user_details =  {"id":user.id, "username":user.username,"email": user.email,"role":user.role}

    db.commit()
    db.refresh(user)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "user_details":user_details
    }


@router.post("/login-location")
def userLoginLocation(location:LocationDetails ,db: Session = Depends(get_db_session),user:User = Depends(JWTBearer())):
    try:
        existing_user = db.query(User).filter(User.id == user.id).first()
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid user")
        existing_user.latitude = location.latitude
        existing_user.longitude = location.longitude
        db.commit()
        db.refresh(existing_user)
        return {"message":"Got the location successfully"}

    except:
        raise HTTPException(status_code=500, detail="Internal server error")





@router.post("/refresh-token")
def refresh_token(request: RefreshToken, db: Session = Depends(get_db_session)):
    try:
        payload = jwt.decode(request.refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
    
        if user is None:
            raise HTTPException(status_code=400, detail="Invalid user")
        if user.refresh_token != request.refresh_token:
            raise HTTPException(status_code=400, detail="Invalid refresh token")

        # Check if the refresh token has expired
        if datetime.datetime.utcfromtimestamp(payload['exp']) < datetime.datetime.utcnow():
            raise HTTPException(status_code=400, detail="Refresh token has expired")
        

        access_token_expiry = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = authenticationService.create_access_token(
            subject=user.id,
            role=user.role,
            expires_delta=access_token_expiry
        )

        return {"access_token": access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Refresh token has expired")

    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token")

@router.post('/logout')
def logout(current_user:User=Depends(JWTBearer()), db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user:
        user.refresh_token = None
        user.refresh_token_expiry = None
        db.commit()
    
    return {"message": "Logout successful"}

@router.get("/{user_id}", response_model=UserResponse)
def get_specific_user(user_id: int, db: Session = Depends(get_db_session),user:User = Depends(JWTBearer())):
    # Check if the user exists
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    return existing_user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db_session)):
    # Check if the user exists
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update only the fields that are present in the request and not None
    if user_update.username is not None:
        existing_user.username = user_update.username
    if user_update.email is not None:
        existing_user.email = user_update.email
    if user_update.age is not None:
        existing_user.age = user_update.age
    if user_update.address is not None:
        existing_user.address = user_update.address
    if user_update.interested_genre is not None:
        existing_user.interested_genre = user_update.interested_genre

    db.commit()
    db.refresh(existing_user)

    return existing_user


@router.post("/upload-profile", response_model=UserResponse)
def upload_profile( profile_update:UserProfilePhotoUpdate, db: Session = Depends(get_db_session), user:User = Depends(JWTBearer())):
    existing_user = db.query(User).filter(User.id == user.id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    existing_user.photo_url =  profile_update.photo_url

    db.commit()
    db.refresh(existing_user)

    return existing_user




@router.post("/change-password")
def upload_profile( password_update:UserPasswordUpdate, db: Session = Depends(get_db_session), user:User = Depends(JWTBearer())):
    if(password_update.new_password == password_update.old_password):
        raise HTTPException(status_code=400, detail="New password cant be same as old password")
    existing_user = db.query(User).filter(User.id == user.id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    verifyOldPassword = authenticationService.verify_password(password_update.old_password, existing_user.password)
    if(verifyOldPassword is False):
        raise HTTPException(status_code=400,detail="Old password is in correct")
    new_hashed_password = authenticationService.hash_password(password_update.new_password)
    existing_user.password =  new_hashed_password

    db.commit()
    db.refresh(existing_user)

    return {"message":"Password changed"}

@router.delete("/{user_id}")
def delete_user(user_id: int, current_user:User=Depends(JWTBearer()) ,db: Session = Depends(get_db_session)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if current_user.role.lower() != 'admin':
            raise HTTPException(status_code=400, detail="Only admin can  handle")
        if user.role.lower() == 'organizer' :
            db.query(Event).filter(Event.organizer_id == user.id).delete(synchronize_session=False)
        db.query(UserInteraction).filter(UserInteraction.user_id == user.id).delete(synchronize_session=False)
        db.delete(user)
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    return {"message": "User deleted successfully"}
