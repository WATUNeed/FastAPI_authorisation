import uuid

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from api.controllers import (
    create_user_controller, create_task_controller, get_tasks_controller, get_task_controller, delete_task_controller,
    edit_task_controller, get_current_user_from_token, login_user_controller
)
from api.models import (
    UserCreate, ShowUser, TaskCreate, ShowTask, ShowTasks, TaskById, TaskEdit, ShowToken, ShowSuccess,
)
from config import settings
from db.models import User
from db.redis_tools.tools import RedisTools
from db.session import get_db_session


main_router = APIRouter()
task_router = APIRouter()

limiter = Limiter(key_func=get_remote_address)


@main_router.post('/register', response_model=ShowUser)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def create_user(
        request: Request,
        response: Response,
        body: UserCreate,
        session: AsyncSession = Depends(get_db_session)
) -> ShowUser:
    return await create_user_controller(body, session=session)


@main_router.post('/login', response_model=ShowToken)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def login_user(
        request: Request,
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: AsyncSession = Depends(get_db_session)
) -> ShowToken:
    return await login_user_controller(form_data=form_data, session=session)


@main_router.post('/logout', response_model=ShowSuccess)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def logout_user(
        request: Request,
        response: Response,
        current_user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowSuccess:
    return ShowSuccess(success=RedisTools.delete_value(str(current_user.email)))


@main_router.post('/tasks', response_model=ShowTask)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def create_task(
        body: TaskCreate,
        request: Request,
        response: Response,
        current_user: ShowUser = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowTask:
    return await create_task_controller(current_user, body, session=session)


@main_router.get('/tasks', response_model=ShowTasks)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def get_tasks(
        request: Request,
        response: Response,
        current_user: ShowUser = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowTasks:
    return await get_tasks_controller(current_user, session=session)


@task_router.get('/{task_id}', response_model=ShowTask)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def get_task(
        request: Request,
        response: Response,
        task_id: uuid.UUID,
        current_user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowTask:
    return await get_task_controller(current_user, TaskById(task_id=task_id), session=session)


@task_router.delete('/{task_id}', response_model=ShowSuccess)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def delete_task(
        request: Request,
        response: Response,
        task_id: uuid.UUID,
        current_user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowSuccess:
    return await delete_task_controller(current_user, TaskById(task_id=task_id), session=session)


@task_router.put('/{body.task_id}', response_model=ShowTask)
@limiter.shared_limit(settings.request_limit, scope=settings.request_scope)
async def edit_task(
        request: Request,
        response: Response,
        body: TaskEdit,
        current_user: User = Depends(get_current_user_from_token),
        session: AsyncSession = Depends(get_db_session)
) -> ShowTask:
    return await edit_task_controller(current_user, body, session=session)
