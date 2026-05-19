from __future__ import annotations

from typing import Any

from core.models import Device, Home


def calculate_device_energy_kwh(device: Device, hours: float) -> float:
    return round(device.power_watts * hours / 1000, 2)


def calculate_device_energy_cost(
    device: Device,
    hours: float,
    tariff: float,
) -> float:
    kwh = calculate_device_energy_kwh(device, hours)
    return round(kwh * tariff, 2)


def calculate_home_energy_report(
    home: Home,
    hours: float = 24,
    tariff: float = 6.0,
) -> dict[str, Any]:
    devices = Device.objects.filter(room__home=home).order_by("name")
    device_reports: list[dict[str, Any]] = []
    total_kwh = 0.0
    total_cost = 0.0

    for device in devices:
        kwh = calculate_device_energy_kwh(device, hours)
        cost = calculate_device_energy_cost(device, hours, tariff)
        total_kwh += kwh
        total_cost += cost
        device_reports.append(
            {
                "name": device.name,
                "power_watts": device.power_watts,
                "kwh": kwh,
                "cost": cost,
            }
        )

    return {
        "home": home.name,
        "hours": hours,
        "tariff": tariff,
        "total_kwh": round(total_kwh, 2),
        "total_cost": round(total_cost, 2),
        "devices": device_reports,
    }
