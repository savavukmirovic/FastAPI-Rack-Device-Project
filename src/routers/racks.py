from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from src.schemas import RackCreate, RackUpdate

from src.db import Rack, Device, create_db_and_tables, get_async_session

def check_power_consumption(rack):
    watts_consumption = [re.findall(r'\d+', device.power_consumption_watts)[0] for device in rack.devices]
    watts_consumption = sum([int(wc) for wc in watts_consumption])
    return watts_consumption

router = APIRouter(
    prefix="/racks",
    tags=["Racks"]
)

@router.get("/")
async def get_all_racks(
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Rack).order_by(Rack.serial_number))
    racks = [row[0] for row in result.all()]


    racks_data = []
    for rack in racks:
        racks_data.append(
            {
                'serial_number': rack.serial_number,
                'name': rack.name,
                'description': rack.description,
                'rack_units': rack.rack_units,
                'max_power_capacity_watts': rack.max_power_capacity_watts,
                'devices_consumption_watts': check_power_consumption(rack),
            }
        )

    return {"racks": racks_data}

@router.post("/")
async def upload_rack(rack: RackCreate, session: AsyncSession = Depends(get_async_session),):
    try:
        new_rack = Rack(
            serial_number=rack.serial_number,
            name=rack.name,
            description=rack.description,
            rack_units=rack.rack_units,
            max_power_capacity_watts=rack.max_power_capacity_watts,
        )
        session.add(new_rack)
        await session.commit()
        await session.refresh(new_rack)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return new_rack

@router.get("/{rack_serial_number}")
async def get_rack(
        rack_serial_number: str,
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Rack).where(Rack.serial_number == rack_serial_number))
    rack = result.scalars().first()

    if not rack:
        raise HTTPException(status_code=404, detail="Rack not found")

    rack.devices_consumption_watts = check_power_consumption(rack)
    return {"rack": rack}

@router.put("/{rack_serial_number}")
async def update_rack(
        rack_serial_number: str,
        rack_update: RackUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(select(Rack).where(Rack.serial_number == rack_serial_number))
        rack = result.scalars().first()

        if not rack:
            raise HTTPException(status_code=404, detail="Rack not found")

        for field, value in rack_update.model_dump(exclude_unset=True).items():
            setattr(rack, field, value)

        session.add(rack)
        await session.commit()
        await session.refresh(rack)

        return {"rack": rack}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{rack_serial_number}")
async def update_rack_part(
        rack_serial_number: str,
        rack_update: RackUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(select(Rack).where(Rack.serial_number == rack_serial_number))
        rack = result.scalars().first()

        if not rack:
            raise HTTPException(status_code=404, detail="Rack not found")

        update_data = rack_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rack, field, value)

        session.add(rack)
        await session.commit()
        await session.refresh(rack)

        return {"rack": rack}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{rack_serial_number}")
async def delete_rack(rack_serial_number: str, session: AsyncSession = Depends(get_async_session), ):
    try:
        result = await session.execute(select(Rack).where(Rack.serial_number == rack_serial_number))
        rack = result.scalars().first()

        if not rack:
            raise HTTPException(status_code=404, detail="rack not found")

        await session.delete(rack)
        await session.commit()

        return {"success": True, "message": "Rack deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
