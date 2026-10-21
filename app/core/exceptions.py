import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger("eastvantage.address_book.exceptions")


class DomainError(Exception):
    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class AddressNotFoundError(DomainError):
    def __init__(self, address_id: str):
        super().__init__(
            message=f"Address with identifier '{address_id}' was not found.",
            code="ADDRESS_NOT_FOUND",
        )
        self.address_id = address_id


class InvalidCoordinateError(DomainError):
    def __init__(self, message: str):
        super().__init__(message=message, code="INVALID_COORDINATES")


def register_exception_handlers(app: FastAPI) -> None:
    """Map domain exceptions to HTTP status codes, decoupling handlers from FastAPI."""

    @app.exception_handler(AddressNotFoundError)
    async def address_not_found_handler(
        request: Request, exc: AddressNotFoundError
    ) -> JSONResponse:
        logger.warning(f"Address not found: {exc.address_id} for path {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": exc.code,
                "message": exc.message,
                "address_id": exc.address_id,
            },
        )

    @app.exception_handler(InvalidCoordinateError)
    async def invalid_coordinate_handler(
        request: Request, exc: InvalidCoordinateError
    ) -> JSONResponse:
        logger.warning(f"Invalid coordinate error: {exc.message} for path {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(
        request: Request, exc: DomainError
    ) -> JSONResponse:
        logger.error(f"Domain error occurred: {exc.message} ({exc.code})")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )
