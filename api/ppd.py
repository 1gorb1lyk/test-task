import os
import uuid
from functools import lru_cache
from typing import Iterator, List, Optional

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, create_engine, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DatabaseError
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from datetime import datetime

SQL_BASE = declarative_base()


@lru_cache(maxsize=None)
def get_engine(db_string: str):
    return create_engine(db_string, pool_pre_ping=True)


class PPDDefinition(SQL_BASE):  # type: ignore
    __tablename__ = "price_paid_data"

    id = Column(UUID(as_uuid=True), primary_key=True)
    price = Column(Integer(), nullable=False)
    date_of_transfer = Column(DateTime(), nullable=False)
    postcode = Column(String(), default=False)
    property_type = Column(String(length=1), default=False)
    is_residential = Column(String(length=1), default=False)
    estate_type = Column(String(length=1), default=False)
    duration = Column(Integer(), default=False)
    paon = Column(String(), default=False)
    saon = Column(String(), default=False)
    street = Column(String(), default=False)
    locality = Column(String(), default=False)
    town = Column(String(), default=False)
    district = Column(String(), default=False)
    category_type = Column(String(length=1), default=False)
    record_status = Column(String(length=1), default=False)


class PPD(BaseModel):
    id: uuid.UUID
    price: int
    date_of_transfer: datetime
    postcode: str
    property_type: str
    is_residential: str
    estate_type: str
    duration: int
    paon: str
    saon: str
    street: str
    locality: str
    town: str
    district: str
    category_type: str
    record_status: str


class PPDFilter(BaseModel):
    limit: Optional[int] = None
    price: Optional[int] = None
    record_status: Optional[str] = None


class PPDManager:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def save(self, ppd: PPD) -> None:
        raise NotImplementedError()

    def clear_table_ppd(self) -> None:
        raise NotImplementedError()

    def get(self, ppd_filter: PPDFilter) -> List[PPD]:
        raise NotImplementedError()


class SQLPPDManager(PPDManager):
    def __init__(self, session):
        self._session: Session = session

    def __exit__(self, exc_type, exc_value: str, exc_traceback: str) -> None:
        if any([exc_type, exc_value, exc_traceback]):
            self._session.rollback()
            return

        try:
            self._session.commit()
        except DatabaseError as e:
            self._session.rollback()
            raise e

    def save(self, ppd: PPD) -> None:
        self._session.add(PPDDefinition(
            id=ppd.id,
            price=ppd.price,
            date_of_transfer=ppd.date_of_transfer,
            postcode=ppd.postcode,
            property_type=ppd.property_type,
            is_residential=ppd.is_residential,
            estate_type=ppd.estate_type,
            duration=ppd.duration,
            paon=ppd.paon,
            saon=ppd.saon,
            street=ppd.street,
            locality=ppd.locality,
            town=ppd.town,
            district=ppd.district,
            category_type=ppd.category_type,
            record_status=ppd.record_status
        ))

    def clear_table_ppd(self):
        self._session.execute('truncate table price_paid_data;')

    def get(self, ppd_filter: PPDFilter) -> List[PPD]:
        query = self._session.query(PPDDefinition)

        if ppd_filter.price is not None:
            query = query.filter(PPDDefinition.price == ppd_filter.price)

        if ppd_filter.record_status is not None:
            query = query.filter(PPDDefinition.record_status == ppd_filter.record_status)

        if ppd_filter.limit is not None:
            query = query.limit(ppd_filter.limit)

        return [
            PPD(
                id=ppd.id,
                price=ppd.price,
                date_of_transfer=ppd.date_of_transfer,
                postcode=ppd.postcode,
                property_type=ppd.property_type,
                is_residential=ppd.is_residential,
                estate_type=ppd.estate_type,
                duration=ppd.duration,
                paon=ppd.paon,
                saon=ppd.saon,
                street=ppd.street,
                locality=ppd.locality,
                town=ppd.town,
                district=ppd.district,
                category_type=ppd.category_type,
                record_status=ppd.record_status
            ) for ppd in query
        ]


def create_ppd() -> Iterator[PPDDefinition]:
    session = sessionmaker(bind=get_engine(os.getenv("DB_STRING")))()
    ppd = SQLPPDManager(session)

    try:
        yield ppd
    except Exception as error:
        session.rollback()
        raise error
    finally:
        session.close()
