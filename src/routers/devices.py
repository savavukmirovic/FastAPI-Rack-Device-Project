from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import re
from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from src.schemas import DeviceCreate, DeviceUpdate

from src.db import Rack, Device, create_db_and_tables, get_async_session


def check_number_of_watts_and_units(rack, new_device_number_of_units, new_device_power_consumption_watts):
    rack_units = int(re.findall(r'\d+', rack.rack_units)[0])
    rack_max_watts_capacity = int(re.findall(r'\d+', rack.max_power_capacity_watts)[0])

    rack_watts_consumption = 0
    rack_units_used = 0
    for device in rack.devices:
        device_watts_consumption = re.findall(r'\d+', device.power_consumption_watts)[0]
        rack_watts_consumption += int(device_watts_consumption)
        rack_units_used += device.number_of_taken_rack_units

    rack_units_left = rack_units - rack_units_used
    rack_watts_left = rack_max_watts_capacity - rack_watts_consumption

    new_device_power_consumption_watts = int(re.findall(r'\d+', new_device_power_consumption_watts)[0])
    if rack_units_left < new_device_number_of_units or rack_watts_left < new_device_power_consumption_watts:
        return True
    return False


router = APIRouter(
    prefix="/devices",
    tags=["Devices"],
)


@router.get("/")
async def get_all_devices(
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Device).order_by(Device.serial_number))
    devices = [row[0] for row in result.all()]

    devices_data = []
    for device in devices:
        devices_data.append(
            {
                'serial_number': device.serial_number,
                'name': device.name,
                'description': device.description,
                'number_of_taken_rack_units': device.number_of_taken_rack_units,
                'power_consumption_watts': device.power_consumption_watts,
                'rack_serial_number': device.rack_serial_number,
            }
        )

    return {"devices": devices_data}


@router.post("/")
async def upload_device(device: DeviceCreate, session: AsyncSession = Depends(get_async_session),):
    try:
        new_device = Device(
            serial_number=device.serial_number,
            name=device.name,
            description=device.description,
            number_of_taken_rack_units=device.number_of_taken_rack_units,
            power_consumption_watts=device.power_consumption_watts,
            rack_serial_number=device.rack_serial_number,
        )
        rack_result = await session.execute(select(Rack).where(Rack.serial_number == device.rack_serial_number))
        rack = rack_result.scalars().first()

        if not rack:
            raise HTTPException(status_code=404, detail="Rack not found")

        if check_number_of_watts_and_units(rack=rack,
                                           new_device_number_of_units=device.number_of_taken_rack_units,
                                           new_device_power_consumption_watts=device.power_consumption_watts):
            raise HTTPException(status_code=404, detail=f"Check number of {rack.name} units and watts left.")

        session.add(new_device)
        await session.commit()
        await session.refresh(new_device)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return new_device

@router.get("/{device_serial_number}")
async def get_device(
        device_serial_number: str,
        session: AsyncSession = Depends(get_async_session),
):
    result = await session.execute(select(Device).where(Device.serial_number == device_serial_number))
    device = result.scalars().first()

    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"device": device}

@router.put("/{device_serial_number}")
async def update_device(
        device_serial_number: str,
        device_update: DeviceUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(select(Device).where(Device.serial_number == device_serial_number))
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        rack_result = await session.execute(select(Rack).where(Rack.serial_number == device.rack_serial_number))
        rack = rack_result.scalars().first()

        for field, value in device_update.model_dump(exclude_unset=True).items():
            setattr(device, field, value)

        if check_number_of_watts_and_units(rack=rack,
                                           new_device_number_of_units=device_update.number_of_taken_rack_units,
                                           new_device_power_consumption_watts=device_update.power_consumption_watts):
            raise HTTPException(status_code=404, detail=f"Check number of {rack.name} units and watts left.")

        session.add(device)
        await session.commit()
        await session.refresh(device)

        return {"device": device}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{device_serial_number}")
async def update_device_part(
        device_serial_number: str,
        device_update: DeviceUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    try:
        result = await session.execute(select(Device).where(Device.serial_number == device_serial_number))
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        rack_result = await session.execute(select(Rack).where(Rack.serial_number == device.rack_serial_number))
        rack = rack_result.scalars().first()

        update_data = device_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(device, field, value)

        if check_number_of_watts_and_units(rack=rack,
                                           new_device_number_of_units=update_data.get('number_of_taken_rack_units',
                                                                                      device.number_of_taken_rack_units),
                                           new_device_power_consumption_watts=update_data.get('power_consumption_watts',
                                                                                              device.power_consumption_watts)):
            raise HTTPException(status_code=404, detail=f"Check number of {rack.name} units and watts left.")

        session.add(device)
        await session.commit()
        await session.refresh(device)

        return {"device": device_update}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_serial_number}")
async def delete_device(device_serial_number: str, session: AsyncSession = Depends(get_async_session),):

    try:
        result = await session.execute(select(Device).where(Device.serial_number == device_serial_number))
        device = result.scalars().first()

        if not device:
            raise HTTPException(status_code=404, detail="Device not found")

        await session.delete(device)
        await session.commit()

        return {"success": True, "message": "Device deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

