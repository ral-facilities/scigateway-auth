"""
Main module contains the API entrypoint.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from scigateway_auth.common.logger_setup import setup_logger
from scigateway_auth.routers import authentication, maintenance

app = FastAPI()

setup_logger()
logger = logging.getLogger()
logger.info("Logging now setup")


@app.exception_handler(Exception)
async def custom_general_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """
    Custom exception handler for FastAPI to handle uncaught exceptions. It logs the error and returns an appropriate
    response.

    :param _: Unused
    :param exc: The exception object that triggered this handler.
    :return: A JSON response indicating that something went wrong.
    """
    logger.exception(exc)
    return JSONResponse(
        content={"detail": "Something went wrong"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(authentication.router)
app.include_router(maintenance.router)
