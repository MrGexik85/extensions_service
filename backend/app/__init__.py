from fastapi import FastAPI
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from .core import core as core_router
from app.utils.db_loader import connect_db, disconnect_db
from app.utils.error_handlers import http_error_handler, http_422_error_handler

import config


app = FastAPI()

# add middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=config.ALLOWED_HOSTS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# connect to database
app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", disconnect_db)

# error handling
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(
    HTTP_422_UNPROCESSABLE_ENTITY, http_422_error_handler)


# include various routes
app.include_router(core_router)
