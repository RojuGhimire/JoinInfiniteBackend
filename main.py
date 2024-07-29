from fastapi import FastAPI
from database import Base,engine
from controllers import usercontroller, eventcontroller
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(engine)


app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usercontroller.router, prefix="/users", tags=["users"])
app.include_router(eventcontroller.router, prefix="/events", tags=["events"])






