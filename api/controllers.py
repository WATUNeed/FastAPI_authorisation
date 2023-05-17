from datetime import timedelta

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from utils.validation import validate_email
from config import settings
from api.models import (
    UserCreate, ShowUser, TaskCreate, ShowTask, ShowTasks, TaskById, TaskEdit, ShowUserWithPassword, ShowEmail,
    ShowToken, ShowSuccess
)
from services.dals import UserDAL, TaskDAL
from db.redis_tools.tools import RedisTools
from db.session import get_db_session
from utils.decorators import request
from utils.hashing import Hasher
from utils.security import create_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/login')


@request
async def create_user_controller(body: UserCreate, session: AsyncSession) -> ShowUser:
    """
    Creates a user in the database.
    :param body:
    :param session:
    :return: User in view.
    """
    user_dal = UserDAL(session)
    user = await user_dal.create_user(
        name=body.name,
        surname=body.surname,
        email=body.email,
        hashed_password=Hasher.get_password_hash(body.password)
    )
    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active
    )


@request
async def create_task_controller(current_user: ShowUser, body: TaskCreate, session: AsyncSession) -> ShowTask:
    """
    Creates a task in the database.
    :param current_user:
    :param body:
    :param session:
    :return: Task in view.
    """
    task_dal = TaskDAL(session)
    task = await task_dal.create_task(
        user_id=current_user.user_id,
        name=body.name,
        content=body.content
    )
    return ShowTask(
        task_id=task.task_id,
        user_id=task.user_id,
        name=task.name,
        content=task.content
    )


@request
async def get_tasks_controller(current_user: ShowUser, session: AsyncSession) -> ShowTasks:
    """
    Outputs all tasks from the database.
    :param current_user:
    :param session:
    :return: List of tasks in view.
    """
    task_dal = TaskDAL(session)
    tasks = await task_dal.get_tasks(current_user.user_id)
    return ShowTasks(task=[
        ShowTask(
            task_id=task.task_id,
            user_id=task.user_id,
            name=task.name,
            content=task.content
        ) for task in tasks
    ])


@request
async def get_task_controller(current_user: ShowUser, body: TaskById, session: AsyncSession) -> ShowTasks:
    """
    Outputs the task from the database.
    :param current_user:
    :param body:
    :param session:
    :return: Task in view.
    """
    task_dal = TaskDAL(session)
    task = await task_dal.get_task(current_user.user_id, body.task_id)
    return ShowTask(
        task_id=task.task_id,
        user_id=task.user_id,
        name=task.name,
        content=task.content
    )


@request
async def delete_task_controller(current_user: ShowUser, body: TaskById, session: AsyncSession) -> ShowSuccess:
    """
    Removes the user's task from the database.
    :param current_user:
    :param body:
    :param session:
    :return:
    """
    task_dal = TaskDAL(session)
    return ShowSuccess(success=await task_dal.delete_task(current_user.user_id, body.task_id))


@request
async def edit_task_controller(current_user: ShowUser, body: TaskEdit, session: AsyncSession) -> ShowTasks:
    """
    Changes the contents of the user's task.
    :param current_user:
    :param body:
    :param session:
    :return: Edited task in database.
    """
    task_dal = TaskDAL(session)
    task = await task_dal.edit_task(current_user.user_id, body.task_id, body.name, body.content)
    return ShowTask(
        task_id=task.task_id,
        user_id=task.user_id,
        name=task.name,
        content=task.content
    )


@request
async def get_user_by_email_for_auth(body: ShowEmail, session: AsyncSession) -> ShowUserWithPassword:
    """
    Outputs the user with the hashed_password field.
    :param body:
    :param session:
    :return:
    """
    user_dal = UserDAL(session)
    user = await user_dal.get_user_by_email(email=body.email)
    return ShowUserWithPassword(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
        hashed_password=user.hashed_password,
    )


async def authenticate_user(email: ShowEmail, password: str, session: AsyncSession):
    """
    Password verification via JWT token.
    :param email:
    :param password:
    :param session:
    :return: User
    """

    user = await get_user_by_email_for_auth(email, session=session)

    if not user:
        return False

    if not Hasher.verify_password(plain_password=str(password), hashed_password=user.hashed_password):
        return False

    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )


async def get_current_user_from_token(
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_db_session)
) -> ShowUser:
    """
    Decrypts the hash and outputs the owner of that hash.
    :param token:
    :param session:
    :return: User
    """
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get('sub')

        if not email:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    email = validate_email(email)
    user = await get_user_by_email_for_auth(email, session=session)

    if not user:
        raise credentials_exception

    return ShowUser(
        user_id=user.user_id,
        name=user.name,
        surname=user.surname,
        email=user.email,
        is_active=user.is_active,
    )


async def login_user_controller(form_data: OAuth2PasswordRequestForm, session: AsyncSession) -> ShowToken:
    """
    Generates or returns a JWT user token.
    :param form_data:
    :param session:
    :return: JWT token
    """
    password = form_data.password
    email = validate_email(form_data.username)
    user = await authenticate_user(email, password, session)

    if not user:
        raise HTTPException(status_code=401, detail='Incorrect username or password')

    if email.email in RedisTools.get_keys():
        return {'access_token': RedisTools.get_value(email.email)}

    access_token_expires = timedelta(minutes=settings.access_token_expire_min)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    RedisTools.set_key(key=email.email, value=access_token)
    return ShowToken(access_token=access_token)
