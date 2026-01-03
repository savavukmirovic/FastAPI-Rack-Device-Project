import re

def distribute_devices(devices, racks):
    # set initial state
    for rack in racks:
        rack.used_power = 0
        rack.used_units = 0
        rack.devices_distribution = []

    total_device_power_cons = sum(int(re.findall(r'\d+', d.power_consumption_watts)[0]) for d in devices)
    total_rack_power_cap = sum(int(re.findall(r'\d+',r.max_power_capacity_watts)[0]) for r in racks)

    target_ratio = total_device_power_cons / total_rack_power_cap


    # sort devices by power (descending)
    devices.sort(key=lambda d: d.power_consumption_watts, reverse=True)

    for device in devices:
        best_rack = None
        best_score = float("inf")

        for rack in racks:
            # check if fits
            if (rack.used_units + device.number_of_taken_rack_units > int(re.findall(
                    r'\d+',rack.rack_units)[0])):
                continue

            if (rack.used_power + int(re.findall(r'\d+', device.power_consumption_watts)[0]) > int(re.findall(
                    r'\d+',rack.max_power_capacity_watts)[0])):
                continue

            new_ratio = (rack.used_power + int(re.findall(r'\d+', device.power_consumption_watts)[0])) / int(re.findall(
                    r'\d+',rack.max_power_capacity_watts)[0])

            score = abs(new_ratio - target_ratio)

            if score < best_score:
                best_score = score
                best_rack = rack

        if not best_rack:
            return Exception(f"Device with serial number {device.serial_number} cannot be distributed.")

        # Allocation
        best_rack.devices_distribution.append(device)
        best_rack.used_units += device.number_of_taken_rack_units
        best_rack.used_power += int(re.findall(r'\d+', device.power_consumption_watts)[0])

    output_dict = {}
    for rack in racks:
        devices_in_rack = [device.serial_number for device in rack.devices_distribution]
        rack_units_used = rack.used_units
        rack_used_power = rack.used_power
        rack_used_power_percent = f'{round(rack.used_power / int(re.findall(r'\d+', rack.max_power_capacity_watts)[0]) * 100, 2)}%'
        output_dict[rack.serial_number] = {'devices': devices_in_rack,
                                           'rackUnitsUsed': rack_units_used,
                                           'rackUsedPower': rack_used_power,
                                           'rackUsedPowerPercentage': rack_used_power_percent}
    return output_dict
