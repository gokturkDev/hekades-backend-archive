import logging
import warnings

import inject
from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from interface.auth.auth import setup_auth
from interface.routers.auth.auth_router import router as auth_router
from interface.routers.conversation.conversation_router import router as conversation_router
from interface.routers.health.health_router import router as health_router
from interface.routers.medicine_info.medicine_info_router import router as medicine_info_router
from interface.routers.patient.patient_router import router as patient_router
from interface.routers.resource.resource_router import router as resource_router
from interface.routers.source.source_router import router as source_router
from interface.routers.speech_to_text.speech_to_text_router import router as speech_to_text_router
from interface.routers.user.user_router import router as user_router
from main.dependency_container import DepContainer, DepContainerImpl
from main.hekades_logger import configure_logger

warnings.filterwarnings("ignore")


def initialize_api_with_dependencies():
    DepContainerImpl.initialize_dependencies()
    inject.configure(lambda binder: binder.bind(DepContainer, DepContainerImpl))
    setup_auth()
    return initialize_api_instance()


def initialize_api_instance():
    configure_logger()
    logger = logging.getLogger("hekades")

    api = FastAPI()
    _setup_cors(api)

    api.include_router(health_router)
    api.include_router(auth_router)
    api.include_router(conversation_router)
    api.include_router(user_router)
    api.include_router(source_router)
    api.include_router(patient_router)
    api.include_router(medicine_info_router)
    api.include_router(resource_router)
    api.include_router(speech_to_text_router)

    @api.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation error in {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"message": exc.errors()[0]}),
        )

    @api.exception_handler(Exception)
    async def unicorn_exception_handler(request: Request, exc: Exception):
        logger.error(f"Internal server error in {request.url}: {exc}")
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder({"message": "Internal server error"}),
        )

    return api


def _setup_cors(api):
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "https://apphkds.hekades.com",
        "https://app.hekades.com"
    ]

    api.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
