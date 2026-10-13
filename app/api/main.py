from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from .database.core import connect_db
from .api import register_routers
# from .logging import configure_logging, LogLevels

# configure_logging(LogLevels.info)

api = FastAPI()
origins=[
    "http://localhost:5173"
]

api.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
register_routers(api)