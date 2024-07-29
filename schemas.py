from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional, List, Union



class UserCreate(BaseModel):
    username: str
    email: EmailStr  
    password: constr(min_length=8)
    role:str
    age: Optional[str] = '18'
    address:str
    photo_url:Optional[str]=None
    interested_genre: List[str] = []

class UserUpdate(BaseModel):
    username: Optional[str]
    email: EmailStr  
    age: Optional[str] 
    address: Optional[str]
    interested_genre: List[str] = []


    

class UserProfilePhotoUpdate(BaseModel):
    photo_url:str

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    age: str
    address: str
    photo_url:Optional[str]=None
    interested_genre:Optional[List[str]] = []
    latitude:Optional[float]=None
    longitude:Optional[float]=None

    class Config:
        orm_mode = True


class LoginDetails(BaseModel):
    email:str
    password:str

class LocationDetails(BaseModel):
    longitude:float
    latitude:float
    
        

class EventGenreEnum(str, Enum):
    adventure = "Adventure"
    comedy = "Comedy"
    drama = "Drama"
    sci_fi = "Sci-Fi"
    it = "IT"
    sports="Sports"
    music = "Music"

class EventCreate(BaseModel):
    event_name: str
    description: str
    date: datetime
    location_latitude: float
    location_longitude: float
    location_address:str
    photo_url: str
    genre: str

class EventResponse(BaseModel):
    id: int
    organizer_id: int
    organicer_username:str
    event_name: str
    description: str
    date: datetime
    location_latitude: float
    location_longitude: float
    location_address:Optional[str]=None
    created_date: datetime
    photo_url: Optional[str]=None
    genre:Optional[str]=None

class EventUpdate(BaseModel):
    event_name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location_latitude: Optional[float] = None
    location_longitude: Optional[float] = None
    photo_url : Optional[str] = None
    genre:Optional[str] = None


class EventLiked(BaseModel):
    liked:bool

class EventInterested(BaseModel):
    interested:bool


class RefreshToken(BaseModel):
    refresh_token:str

class UserPasswordUpdate(BaseModel):
    old_password:str
    new_password:str