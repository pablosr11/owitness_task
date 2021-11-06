from fastapi.testclient import TestClient
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import pytest
from sqlalchemy.orm.session import Session

from app.main import app, get_db, Base, DBTitle

engine = sqlalchemy.create_engine(
    "sqlite:///./test.db", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database once
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Needed for sqlite for proper SAVEPOINT / nested transaction support.
# From: https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
@sqlalchemy.event.listens_for(engine, "connect")
def do_connect(dbapi_connection, connection_record):
    # Disable pysqlite's emitting of the BEGIN and COMMIT statemenets.
    dbapi_connection.isolation_level = None


@sqlalchemy.event.listens_for(engine, "begin")
def do_begin(conn):
    # emit our own BEGIN
    conn.exec_driver_sql("BEGIN")


# Creates a nested transaction and recreates it when the code
# calls session.commit and rolls it back at the end.
# Based on: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
@pytest.fixture()
def session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    # Begin a nested transaction (using SAVEPOINT).
    nested = connection.begin_nested()

    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        # If the application code calls session.commit, it
        # will end the nested transaction. Need to start
        # a new one when that happens.
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    session.close()
    transaction.rollback()
    connection.close()


# A fixture for the fastapi test client which depends on the
# previous session fixture. Instead of creating a new session in the
# dependency override as before, it uses the one provided by the
# session fixture.
@pytest.fixture()
def client(session):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


def title_factory(
    session: Session,
    title_class="Freehold",
    title_number="MYBKZ10625",
    content="random",
):
    session.add(
        DBTitle(title_number=title_number, title_class=title_class, content=content)
    )
    session.commit()
