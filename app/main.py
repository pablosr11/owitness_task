from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

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

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}
