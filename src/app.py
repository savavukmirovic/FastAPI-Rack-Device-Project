from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from src.schemas import DeviceCreate, RackCreate
from uvicorn import lifespan

from src.db import Rack, Device, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
import os
from src.routers.devices import router as devices_router
from src.routers.racks import router as racks_router
from src.algorithm_for_allocation import distribute_devices

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(devices_router)
app.include_router(racks_router)


@app.get("/")
async def root():
    return {"message": "Swagger UI doc is on  http://0.0.0.0:8000/docs"}

@app.get("/devicerackallocation")
async def devicerackallocation(
            devices_serials_numbers: str,
            racks_serials_numbers: str,
            session: AsyncSession = Depends(get_async_session),):
    try:
        devices = []
        racks =  []
        for device_serial_number in devices_serials_numbers.split(","):
            result = await session.execute(select(Device).where(Device.serial_number == device_serial_number))
            device = result.scalars().first()

            if not device:
                raise HTTPException(status_code=404, detail=f"Device {device_serial_number} not found")

            devices.append(device)

        for rack_serial_number in racks_serials_numbers.split(","):
            result = await session.execute(select(Rack).where(Rack.serial_number == rack_serial_number))
            rack = result.scalars().first()

            if not rack:
                raise HTTPException(status_code=404, detail=f"Rack {rack_serial_number} not found")
            racks.append(rack)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        allocation_of_devices = distribute_devices(devices=devices, racks=racks)

        if isinstance(allocation_of_devices, Exception):
            raise HTTPException(status_code=400, detail=str(allocation_of_devices))
        return {"racks": allocation_of_devices}
