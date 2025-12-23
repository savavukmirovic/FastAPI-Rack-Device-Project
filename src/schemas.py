from pydantic import BaseModel, Field
from typing import Any

# class DeviceCreate(BaseModel):
#     # gt=0 znači "greater than 0" (prirodni brojevi 1, 2, 3...)
#     # ge=0 bi značilo "greater or equal" (uključujući nulu)
#     port_count: int = Field(gt=0)

class RackCreate(BaseModel):
    serial_number: str
    name: str
    description: str
    rack_units: Any
    max_power_capacity_watts: Any


class DeviceCreate(BaseModel):
    serial_number: str
    name: str
    description: str
    number_of_taken_rack_units: int = Field(gt=0)
    power_consumption_watts: Any
    rack_serial_number: str

class RackUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    rack_units: Any | None = None
    max_power_capacity_watts: Any | None = None

class DeviceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    number_of_taken_rack_units: int | None = Field(gt=0)
    power_consumption_watts: Any | None = None
    rack_serial_number: str | None = None
