import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models import Base
from core.storage import SQLAlchemyStorage


@pytest.fixture(scope="function")
def session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)

    connection = engine.connect()
    transaction = connection.begin()

    SessionLocal = sessionmaker(bind=connection, expire_on_commit=False, future=True)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
        engine.dispose()


@pytest.fixture(scope="function")
def storage(session: Session) -> SQLAlchemyStorage:
    return SQLAlchemyStorage(session)
