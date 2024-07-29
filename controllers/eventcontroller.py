# controllers/eventcontroller.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.userAutenticationService import UserAuthenticationService
import models
import schemas
from dependencies import get_db_session
from role_jwt_beares import RoleJWTBearer 
from auth_bearer import JWTBearer
from fastapi import Query
from sqlalchemy.orm import aliased
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter()
authenticationService = UserAuthenticationService()


from sqlalchemy import func

@router.get("")
def get_all_events(skip: int = Query(0, alias="page", ge=0), limit: int = Query(10, le=100), db: Session = Depends(get_db_session), current_user: models.User = Depends(JWTBearer())):
    # Aliasing UserInteraction for liked and interested
    UserInteractionAlias = aliased(models.UserInteraction)

    events_query = db.query(models.Event, models.User, UserInteractionAlias)\
        .join(models.User, models.Event.organizer_id == models.User.id)\
        .outerjoin(UserInteractionAlias, (UserInteractionAlias.event_id == models.Event.id) & (UserInteractionAlias.user_id == current_user.id))\
        .order_by(models.Event.created_date.desc())

    total_events = events_query.count()

    events = events_query.offset(skip).limit(limit).all()

    result = [
        {
            "event_id": event.id,
            "event_name": event.event_name,
            "organizer_id": event.organizer.id,
            "organizer_username": event.organizer.username,
            "organizer_photo_url": event.organizer.photo_url,
            "genre": event.genre,
            "location_longitude": event.location_longitude,
            "location_latitude": event.location_latitude,
            "location_address": event.location_address,
            "photo_url": event.photo_url,
            "date": event.date,
            "description": event.description,
            "liked": user_interaction.liked if user_interaction else False,
            "interested": user_interaction.interested if user_interaction else False,
            "liked_user_count": db.query(func.count(UserInteractionAlias.id)).filter(UserInteractionAlias.event_id == event.id, UserInteractionAlias.liked == True).scalar(),
            "interested_user_count": db.query(func.count(UserInteractionAlias.id)).filter(UserInteractionAlias.event_id == event.id, UserInteractionAlias.interested == True).scalar()
        }
        for event, user, user_interaction in events
    ]

    return {
        "total_events": total_events,
        "events": result,
        "skip": skip,
        "limit": limit
    }


@router.get("/my-events/user/{user_id}")
def get_events_by_organizer(
    user_id:int,
    skip: int = Query(0, alias="page", ge=0),
    limit: int = Query(10, le=100),
    db: Session = Depends(get_db_session),
):
    UserInteractionAlias = aliased(models.UserInteraction)

    events_query = db.query(models.Event, models.User, UserInteractionAlias)\
        .join(models.User, models.Event.organizer_id == models.User.id)\
        .outerjoin(UserInteractionAlias, (UserInteractionAlias.event_id == models.Event.id) & (UserInteractionAlias.user_id == user_id))\
        .filter(models.Event.organizer_id == user_id)\
        .order_by(models.Event.created_date.desc())

    total_events = events_query.count()

    events = events_query.offset(skip).limit(limit).all()

    result = [
        {
            "event_id": event.id,
            "event_name": event.event_name,
            "organizer_id": event.organizer.id,
            "organizer_username": event.organizer.username,
            "organizer_photo_url": event.organizer.photo_url,
            "genre": event.genre,
            "location_longitude": event.location_longitude,
            "location_latitude": event.location_latitude,
            "location_address": event.location_address,
            "photo_url": event.photo_url,
            "date": event.date,
            "description": event.description,
            "liked": user_interaction.liked if user_interaction else False,
            "interested": user_interaction.interested if user_interaction else False,
            "liked_user_count": db.query(func.count(UserInteractionAlias.id)).filter(UserInteractionAlias.event_id == event.id, UserInteractionAlias.liked == True).scalar(),
            "interested_user_count": db.query(func.count(UserInteractionAlias.id)).filter(UserInteractionAlias.event_id == event.id, UserInteractionAlias.interested == True).scalar()
        }
        for event, user, user_interaction in events
    ]

    return {
        "total_events": total_events,
        "events": result,
        "skip": skip,
        "limit": limit
    }




@router.post("")
async def create_event(event: schemas.EventCreate, db: Session = Depends(get_db_session), current_user: models.User = Depends(RoleJWTBearer())):
    try:
        new_event = models.Event(
            event_name=event.event_name,
            description=event.description,
            date=event.date,
            location_latitude=event.location_latitude,
            location_longitude=event.location_longitude,
            photo_url=event.photo_url,
            organizer_id=current_user.id,
            location_address=event.location_address,
            genre=event.genre
        )

        db.add(new_event)
        db.commit()
        return {"message": "Event created by event controller"}
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()



@router.get("/{event_id}")
def read_event(event_id: int, db: Session = Depends(get_db_session), dependencies=Depends(RoleJWTBearer())):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.put("/{event_id}")
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db_session), dependencies=Depends(RoleJWTBearer())):
    existing_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if existing_event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    # Update event attributes based on the input
    for key, value in event.dict().items():
        setattr(existing_event, key, value)

    db.commit()
    db.refresh(existing_event)

    return {"message": "Event updated by event controller"}


@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    db: Session = Depends(get_db_session),
    current_user: models.User = Depends(RoleJWTBearer()),
):
    try:
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        if event is None:
            raise HTTPException(status_code=404, detail="Event not found")
        if event.organizer_id != current_user.id and current_user.role.lower() != 'admin':
            raise HTTPException(status_code=400, detail="You cannot delete this event.")
        db.query(models.UserInteraction).filter(models.UserInteraction.event_id == event.id).delete(synchronize_session=False)

        # Delete the event
        db.delete(event)
        db.commit()
        return {"message": "Event deleted by event controller"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/like/{event_id}")
def like_event(event_id: int, request: schemas.EventLiked, db: Session = Depends(get_db_session), current_user: models.User = Depends(JWTBearer())):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")

    user_interaction = db.query(models.UserInteraction).filter(
        models.UserInteraction.event_id == event_id,
        models.UserInteraction.user_id == current_user.id
    ).first()

    if user_interaction:
        user_interaction.liked = request.liked
    else:
        new_user_interaction = models.UserInteraction(
            user_id=current_user.id,
            event_id=event_id,
            liked=request.liked
        )
        db.add(new_user_interaction)
    db.commit()
    return {"message": "Interacted successfully"}


@router.post("/interested/{event_id}")
def mark_interested(event_id: int, request: schemas.EventInterested, db: Session = Depends(get_db_session), current_user: models.User = Depends(JWTBearer())):
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    user_interaction = db.query(models.UserInteraction).filter(
        models.UserInteraction.event_id == event_id,
        models.UserInteraction.user_id == current_user.id
    ).first()

    if user_interaction:
        user_interaction.interested = request.interested
    else:
        new_user_interaction = models.UserInteraction(
            user_id=current_user.id,
            event_id=event_id,
            interested=request.interested
        )
        db.add(new_user_interaction)

    db.commit()
    return {"message": "Interaction  successfully"}




