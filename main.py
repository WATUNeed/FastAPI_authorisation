import uvicorn

from fastapi import FastAPI
from fastapi.routing import APIRouter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.handlers import task_router, main_router


# Create app
app = FastAPI()


@app.on_event("startup")
async def app_startup():
    """
    Setting up the api at start-up.
    :return:
    """
    # Set requests limit settings
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Configuration router
    main_api_router = APIRouter()
    main_api_router.include_router(main_router)
    main_api_router.include_router(task_router, prefix='/tasks', tags=['tasks'])
    app.include_router(main_api_router)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
