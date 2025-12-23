from fastapi.testclient import TestClient
from src.db import Rack, Device, create_db_and_tables, get_async_session
from src.algorithm_for_allocation import distribute_devices
from src.app import app
import re

client = TestClient(app)


def test_all_devices_are_assigned():
    racks = [
        Rack(
            serial_number='r1',
            name='R1',
            description='rack1 is up',
            rack_units='42U',
            max_power_capacity_watts='5000W',),
        Rack(
            serial_number='r2',
            name='R2',
            description='rack2 is up',
            rack_units='48U',
            max_power_capacity_watts='5500W', ),
        Rack(
            serial_number='r3',
            name='R3',
            description='rack3 is up',
            rack_units='42U',
            max_power_capacity_watts='5600W', ),
    ]
    devices = [
        Device(
            serial_number='d1',
            name='D1',
            description='Device1 is up',
            number_of_taken_rack_units=6,
            power_consumption_watts='500W',
            rack_serial_number='r1',),
        Device(
            serial_number='d2',
            name='D2',
            description='Device2 is up',
            number_of_taken_rack_units=7,
            power_consumption_watts='600W',
            rack_serial_number='r2', ),
        Device(
            serial_number='d3',
            name='D3',
            description='Device3 is up',
            number_of_taken_rack_units=3,
            power_consumption_watts='500W',
            rack_serial_number='r3', ),
        Device(
            serial_number='d4',
            name='D4',
            description='Device4 is up',
            number_of_taken_rack_units=8,
            power_consumption_watts='600W',
            rack_serial_number='r2', ),
        Device(
            serial_number='d5',
            name='D5',
            description='Device5 is up',
            number_of_taken_rack_units=5,
            power_consumption_watts='700W',
            rack_serial_number='r1', ),
    ]

    result = distribute_devices(devices, racks)

    assigned_devices = [
        device for rack in result.values() for device in rack['devices']
    ]
    assert set(assigned_devices) == {d.serial_number for d in devices}

def test_rack_power_capacity_not_exceeded():
    racks = [
        Rack(
            serial_number='r1',
            name='R1',
            description='rack1 is up',
            rack_units='42U',
            max_power_capacity_watts='2000W', ),
        Rack(
            serial_number='r2',
            name='R2',
            description='rack2 is up',
            rack_units='42U',
            max_power_capacity_watts='2000W', ),
    ]

    devices = [
        Device(
            serial_number='d1',
            name='D1',
            description='Device1 is up',
            number_of_taken_rack_units=6,
            power_consumption_watts='1000W',
            rack_serial_number='r2', ),
        Device(
            serial_number='d2',
            name='D2',
            description='Device2 is up',
            number_of_taken_rack_units=7,
            power_consumption_watts='900W',
            rack_serial_number='r2', ),
    ]

    result = distribute_devices(devices, racks)

    for rack in racks:
        for rack_in_output_key, values in result.items():
            if rack.serial_number == rack_in_output_key:
                assert values['rackUsedPower'] <= int(re.findall(r'\d+',rack.max_power_capacity_watts)[0])

def test_rack_units_not_exceeded():
    racks = [
        Rack(
            serial_number='r1',
            name='R1',
            description='rack1 is up',
            rack_units='5U',
            max_power_capacity_watts='5000W', ),
        Rack(
            serial_number='r2',
            name='R2',
            description='rack2 is up',
            rack_units='5U',
            max_power_capacity_watts='2000W', ),
    ]

    devices = [
        Device(
            serial_number='d1',
            name='D1',
            description='Device1 is up',
            number_of_taken_rack_units=3,
            power_consumption_watts='1000W',
            rack_serial_number='r2', ),
        Device(
            serial_number='d2',
            name='D2',
            description='Device2 is up',
            number_of_taken_rack_units=2,
            power_consumption_watts='900W',
            rack_serial_number='r2', ),
    ]

    result = distribute_devices(devices, racks)

    for rack in racks:
        for rack_in_output_key, values in result.items():
            if rack.serial_number == rack_in_output_key:
                assert values['rackUnitsUsed'] <= int(re.findall(r'\d+',rack.rack_units)[0])

def test_rack_utilization_is_balanced():
    racks = [
        Rack(
            serial_number='r1',
            name='R1',
            description='rack1 is up',
            rack_units='42U',
            max_power_capacity_watts='5000W', ),
        Rack(
            serial_number='r2',
            name='R2',
            description='rack2 is up',
            rack_units='42U',
            max_power_capacity_watts='5000W', ),
        Rack(
            serial_number='r3',
            name='R3',
            description='rack3 is up',
            rack_units='42U',
            max_power_capacity_watts='5000W', ),
    ]

    devices = [
        Device(
            serial_number='d1',
            name='D1',
            description='Device1 is up',
            number_of_taken_rack_units=7,
            power_consumption_watts='900W',
            rack_serial_number='r1', ),
        Device(
            serial_number='d2',
            name='D2',
            description='Device2 is up',
            number_of_taken_rack_units=6,
            power_consumption_watts='850W',
            rack_serial_number='r2', ),
        Device(
            serial_number='d3',
            name='D3',
            description='Device3 is up',
            number_of_taken_rack_units=3,
            power_consumption_watts='800W',
            rack_serial_number='r3', ),
    ]

    result = distribute_devices(devices, racks)

    utilizations = []
    for rack in racks:
        for rack_in_output_key, values in result.items():
            if rack.serial_number == rack_in_output_key:
                utilizations.append(values['rackUsedPower'] / int(re.findall(r'\d+', rack.max_power_capacity_watts)[0]))
    assert max(utilizations) - min(utilizations) <= 0.10

def test_raises_when_device_cannot_be_assigned():
    racks = [
        Rack(
            serial_number='r1',
            name='R1',
            description='rack1 is up',
            rack_units='42U',
            max_power_capacity_watts='400W', ),
    ]

    devices = [
        Device(
            serial_number='d1',
            name='D1',
            description='Device1 is up',
            number_of_taken_rack_units=2,
            power_consumption_watts='900W',
            rack_serial_number='r1', ),
    ]

    result = distribute_devices(devices, racks)
    assert isinstance(result, Exception)