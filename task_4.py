"""
Напишите API для управления списком задач. Для этого создайте модель Task
со следующими полями:
○ id: int (первичный ключ)
○ title: str (название задачи)
○ description: str (описание задачи)
○ done: bool (статус выполнения задачи)
API должно поддерживать следующие операции:
○ Получение списка всех задач: GET /tasks/
○ Получение информации о конкретной задаче: GET /tasks/{task_id}/
○ Создание новой задачи: POST /tasks/
○ Обновление информации о задаче: PUT /tasks/{task_id}/
○ Удаление задачи: DELETE /tasks/{task_id}/
Для валидации данных используйте параметры Field модели Task.
Для работы с базой данных используйте SQLAlchemy и модуль databases.
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field
import sqlalchemy
import databases
from typing import List

app = FastAPI()
DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()
task = sqlalchemy.Table(
    'task',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String(30)),
    sqlalchemy.Column('description', sqlalchemy.String(100)),
    sqlalchemy.Column('done', sqlalchemy.Boolean),
)


class TaskIn(BaseModel):
    title: str = Field(max_length=30)
    description: str = Field(max_length=100)
    done: bool


class Task(TaskIn):
    id: int


engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


@app.get('/')
async def index():
    return {'message': 'task_4'}


@app.get('/task/', response_model=List[Task])
async def get_tasks():
    query = task.select()
    return await database.fetch_all(query)


@app.get('/task/{task_id:int}', response_model=Task)
async def get_task(task_id: int):
    query = task.select().where(task.c.id == task_id)
    return await database.fetch_one(query)


@app.post('/task/', response_model=Task)
async def great_task(new_task: TaskIn):
    query = task.insert().values(**new_task.model_dump())
    last_record_id = await database.execute(query)
    return {**new_task.model_dump(), "id": last_record_id}


@app.put("/task/{task_id}", response_model=Task)
async def update_task(task_id: int, new_task: TaskIn):
    query = task.update().where(task.c.id == task_id).values(**new_task.model_dump())
    await database.execute(query)
    return await get_task(task_id)


@app.delete('/task/{task_id}')
async def delite_task(task_id: int):
    query = task.delete().where(task.c.id == task_id)
    await database.execute(query)
    return {'msg': 'Delete'}

# @app.get('/create_table/{cnt:int}')
# async def create_table(cnt: int):
#     for i in range(cnt):
#         query = task.insert().values(title=f'title{i}', description=f'description{i}', done=False)
#         await database.execute(query)
#     return {'message': f'{cnt} create'}
