import uuid
from typing import Generator

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, Task
from utils.decorators import catch_exceptions


class UserDAL:
    """
    Business logic of the User entity.
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @catch_exceptions
    async def create_user(self, name: str, surname: str, email: str, hashed_password: str) -> User:
        """
        Creates a User entity and enters it into the database.
        :param name:
        :param surname:
        :param email:
        :param hashed_password:
        :return: New user in database.
        """
        new_user = User(name=name, surname=surname, email=email, hashed_password=hashed_password)
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    @catch_exceptions
    async def get_user_by_email(self, email: str) -> User:
        """
        :param email:
        :return: Returns the user from the database by their email.
        """
        user = await self.db_session.execute(select(User).where(User.email == email).limit(1))
        return user.scalars().one()


class TaskDAL:
    """
    Business logic of the Task entity.
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @catch_exceptions
    async def create_task(self, user_id: uuid.UUID, name: str, content: str) -> Task:
        """
        Creates a Task entity and enters it into the database.
        :param user_id:
        :param name:
        :param content:
        :return: New task in database.
        """
        new_task = Task(user_id=user_id, name=name, content=content)
        self.db_session.add(new_task)
        await self.db_session.flush()
        return new_task

    @catch_exceptions
    async def get_tasks(self, user_id: uuid.UUID) -> Generator[Task, None, None]:
        """
        :param user_id:
        :return: Returns all user tasks from the database.
        """
        tasks = await self.db_session.execute(select(Task).where(Task.user_id == user_id))
        return (item for item in tasks.scalars())

    @catch_exceptions
    async def get_task(self, user_id: uuid.UUID, task_id: uuid.UUID) -> Task:
        """
        :param user_id:
        :param task_id:
        :return: Returns the task by its task_Id and user_id.
        """
        task = await self.db_session.execute(select(Task).where(
            (Task.task_id == task_id) & (Task.user_id == user_id)
        ).limit(1))
        return task.scalars().one()

    @catch_exceptions
    async def delete_task(self, user_id: uuid.UUID, task_id: uuid.UUID) -> bool:
        """
        :param user_id:
        :param task_id:
        :return: Deletes a task by its task_Id and user_id.
        """
        task = await self.db_session.execute(select(Task).where(
            (Task.task_id == task_id) & (Task.user_id == user_id)
        ).limit(1))
        task = task.scalars().one()
        if not task:
            return False
        await self.db_session.execute(delete(Task).where((Task.task_id == task_id) & (Task.user_id == user_id)))
        await self.db_session.commit()
        return True

    @catch_exceptions
    async def edit_task(self, user_id: uuid.UUID, task_id: uuid.UUID, name: str, context: str):
        """
        :param user_id:
        :param task_id:
        :param name:
        :param context:
        :return: Changes the job values by its task_Id and user_id.
        """
        result = await self.db_session.execute(select(Task).where(
            (Task.task_id == task_id) & (Task.user_id == user_id)
        ).limit(1))
        task: Task = result.scalars().one()
        task.name = name
        task.content = context
        await self.db_session.commit()
        return task
