from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer, CheckConstraint, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime, UTC
from fastapi import Depends

DATABASE_URL = "sqlite+aiosqlite:///./hardware.db"


class Base(DeclarativeBase):
    pass


class Rack(Base):
    __tablename__ = "racks"

    serial_number = Column(Text, nullable=False, unique=True, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    rack_units = Column(Text, nullable=False)
    max_power_capacity_watts = Column(Text, nullable=False)

    devices = relationship("Device", back_populates="rack", lazy="selectin")


class Device(Base):
    __tablename__ = "devices"

    serial_number = Column(Text, nullable=False, unique=True, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    number_of_taken_rack_units = Column(Integer, nullable=False)
    power_consumption_watts = Column(Text, nullable=False)

    rack_serial_number = Column(Text, ForeignKey("racks.serial_number"), nullable=False)
    rack = relationship("Rack", back_populates="devices", lazy="selectin")

    __table_args__ = (
        CheckConstraint('number_of_taken_rack_units > 0', name='check_number_of_taken_rack_units_positive'),
    )

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
