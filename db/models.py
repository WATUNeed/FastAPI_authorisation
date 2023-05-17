import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Boolean, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    hashed_password = Column(String, nullable=False)

    questions_rel = relationship('Task')

    def __repr__(self):
        return f'User: {self.name} {self.surname} ' \
               f'id: {self.user_id} ' \
               f'email: {self.email} ' \
               f'hash: {self.hashed_password}'


class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)

    themes_rel = relationship('User')

    def __repr__(self):
        return f'task: {self.name} with id: {self.task_id}. Author: {self.user_id}'
