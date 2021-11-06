from typing import List
from fastapi import FastAPI, Depends, Request
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from enum import Enum
from sqlalchemy import create_engine, func, desc
from sqlalchemy import Column, Text, Integer
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session, Query
from sqlalchemy.sql.sqltypes import String

# Configuration
PAGE_SIZE: int = 10

# On a larger project probably makes sense to move the DB
# variables, config and schemas out of the main module to
# decouple it form the main app definition, define boundaries
# and have a clear picture of where every part of the system
# is (api, db interface, business logic, data validation/schemas etc)

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


# Normally we would separate the different api namespaces/scopes/resources into diff packages and modules
# each of which would contain their prefixed router linked to the main app here.
# Given this API only has 2 endpoints I decided to keep it in a single module and route through the main app.
DEFAULT_PARAMS = {"_order": OrderKeys.asc, "_sort": SortKeys.id}
app = FastAPI()


##
## Titles CRUD operations and helpers
##
def parse_comma_separated_params(param_name: str):
    def parse(request: Request):
        splitted_params: List[str] = request.query_params.get(
            param_name, DEFAULT_PARAMS[param_name]
        ).split(",")
        # Ideally, validate custom query parameters here.
        return splitted_params

    return parse


async def get_titles(
    db: Session,
    title_class: TitleClass,
    _sort: List[SortKeys],
    _order: List[OrderKeys],
    _limit: int,
    _page: int,
) -> List[DBTitle]:

    query: Query = db.query(DBTitle.id, DBTitle.title_class, DBTitle.title_number)

    if title_class:
        query = query.where(func.lower(DBTitle.title_class) == func.lower(title_class))

    for idx, sorting_field in enumerate(_sort):
        # No constraint on _sort vs _order params. Default to asc if no order param found.
        ordering = _order[idx] if len(_order) > idx else OrderKeys.asc
        if ordering != OrderKeys.asc:
            query = query.order_by(desc(getattr(DBTitle, sorting_field)))
        else:
            query = query.order_by(getattr(DBTitle, sorting_field))

    # Assuming with page we mean an offset?
    query = query.offset(_page * PAGE_SIZE).limit(_limit)

    output = query.all()
    return output


async def get_title_by_id(title_id: int, db: Session) -> DBTitle:
    return db.query(DBTitle).filter(DBTitle.id == title_id).first()


##
## Titles API helpers
##
async def validate_params(sort: List[str], order: List[str]):
    if len(sort) != len(order):
        raise HTTPException(
            status_code=400,
            detail="Mismatched number of _sort and _order parameters",
        )

    # Manual validation of sort and order params as they don't
    # get validated.
    for param in sort:
        if param not in SortKeys._member_names_:
            raise HTTPException(status_code=422, detail="Invalid _sort query parameter")
    for param in order:
        if param not in OrderKeys._member_names_:
            raise HTTPException(
                status_code=422, detail="Invalid _order query parameter"
            )


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
    _sort: List[str] = Depends(parse_comma_separated_params("_sort")),
    _order: List[str] = Depends(parse_comma_separated_params("_order")),
    _limit: int = 50,
    _page: int = 0,
    db: Session = Depends(get_db),
):
    # Currently there are no restriction on who can use the endpoints. These would normally be
    # handled at the router level to restrict a set of endpoints to specific users.

    # Basic validation
    await validate_params(sort=_sort, order=_order)

    # Trigger crud query
    output: List[DBTitle] = await get_titles(
        db=db,
        title_class=title_class,
        _sort=_sort,
        _order=_order,
        _limit=_limit,
        _page=_page,
    )

    if not output:
        raise HTTPException(status_code=404, detail="No titles found")

    return output
