from typing import List
from fastapi import FastAPI, Depends, Request
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import create_engine, func
from sqlalchemy import Column, Text, Integer
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session, Query
from sqlalchemy.sql.sqltypes import String

# On apis where we expect a large number of concurrent request, we
# would have to switch to a client/server DB and pool connections.
# For demo purposes, sqlite.
DB_URI = "sqlite:///orbital.db"
engine: Engine = create_engine(
    url=DB_URI,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TitleClass(str, Enum):
    Freehold = "Freehold"
    Leasehold = "Leasehold"


class SortKeys(str, Enum):
    id = "id"
    title_number = "title_number"


class OrderKeys(str, Enum):
    asc = "asc"
    desc = "desc"


class Title(BaseModel):
    id: int
    title_number: str
    title_class: TitleClass
    content: str

    class Config:
        orm_mode = True


class TitleOutput(BaseModel):
    id: int
    title_number: str
    title_class: TitleClass

    class Config:
        orm_mode = True


class DBTitle(Base):
    __tablename__ = "titles"
    id = Column(Integer, primary_key=True)
    title_number = Column(Text)
    title_class = Column(String(10))
    content = Column(Text)

app = FastAPI()


##
## Titles CRUD operations and helpers
##
async def get_titles(
    db: Session,
    title_class: TitleClass,
) -> List[DBTitle]:

    query: Query = db.query(DBTitle.id, DBTitle.title_class, DBTitle.title_number)

    if title_class:
        query = query.where(func.lower(DBTitle.title_class) == func.lower(title_class))

    output = query.all()
    return output

async def get_title_by_id(title_id: int, db: Session) -> DBTitle:
    return db.query(DBTitle).filter(DBTitle.id == title_id).first()


##
## Titles API.
##
@app.get("/api/titles/{title_id}", response_model=Title)
async def titles_detail(title_id: int, db: Session = Depends(get_db)):
    output: DBTitle = await get_title_by_id(title_id=title_id, db=db)
    if not output:
        raise HTTPException(status_code=404, detail="Title not found")
    return output


@app.get("/api/titles", response_model=List[TitleOutput])
async def titles_list(
    title_class: TitleClass = None,
    db: Session = Depends(get_db),
):
    output: List[DBTitle] = await get_titles(
        db=db,
        title_class=title_class,
    )

    return output
