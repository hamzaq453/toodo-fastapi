from contextlib import asynccontextmanager

from typing import Union, Optional

from toodo_1 import settings

from sqlmodel import Field, Session, SQLModel, create_engine, select

from fastapi import FastAPI

class Todo(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    content: str = Field(index=True)


connection_string = str(settings.DATABASE_URL).replace(

    "postgresql", "postgresql+psycopg"

)


engine = create_engine(

    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300

)



def create_db_and_tables():

    SQLModel.metadata.create_all(engine)


@asynccontextmanager

async def lifespan(app: FastAPI):

    print("Creating tables..")

    create_db_and_tables()

    yield


app = FastAPI(lifespan=lifespan)

@app.get("/")

def read_root():

    return {"Hello": "World"}


@app.post("/todos/")

def create_todo(todo: Todo):

    with Session(engine) as session:

        session.add(todo)

        session.commit()

        session.refresh(todo)

        return todo


@app.get("/todos/")

def read_todos():

    with Session(engine) as session:

        todos = session.exec(select(Todo)).all()

        return todos
    

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo: Todo):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            return {"error": "Todo not found"}

        todo.content = updated_todo.content  # Update the content
        session.commit()
        session.refresh(todo)  # Refresh to reflect changes
        return todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            return {"error": "Todo not found"}

        session.delete(todo)
        session.commit()

        return {"message": "Todo deleted successfully"}