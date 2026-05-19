from __future__ import annotations

from typing import Any

from core.models import Device


class DeviceState:
    """State — базовое состояние устройства."""

    name: str = ""

    def turn_on(self, device: Device) -> dict[str, Any]:
        raise NotImplementedError

    def turn_off(self, device: Device) -> dict[str, Any]:
        raise NotImplementedError

    def report(self, device: Device) -> dict[str, Any]:
        return {
            "device": device.name,
            "state": self.name,
            "status": device.status,
        }


class OffState(DeviceState):
    name = "off"

    def turn_on(self, device: Device) -> dict[str, Any]:
        device.status = Device.Status.ON
        device.save(update_fields=["status", "updated_at"])
        return {"success": True, "message": f"{device.name} включено", "status": device.status}

    def turn_off(self, device: Device) -> dict[str, Any]:
        return {"success": True, "message": f"{device.name} уже выключено", "status": device.status}


class OnState(DeviceState):
    name = "on"

    def turn_on(self, device: Device) -> dict[str, Any]:
        return {"success": True, "message": f"{device.name} уже включено", "status": device.status}

    def turn_off(self, device: Device) -> dict[str, Any]:
        device.status = Device.Status.OFF
        device.save(update_fields=["status", "updated_at"])
        return {"success": True, "message": f"{device.name} выключено", "status": device.status}


class ErrorState(DeviceState):
    name = "error"

    def turn_on(self, device: Device) -> dict[str, Any]:
        return {
            "success": False,
            "message": f"{device.name} в состоянии ошибки — включение запрещено",
            "status": device.status,
        }

    def turn_off(self, device: Device) -> dict[str, Any]:
        device.status = Device.Status.OFF
        device.save(update_fields=["status", "updated_at"])
        return {"success": True, "message": f"{device.name} сброшено в off", "status": device.status}


class MaintenanceState(DeviceState):
    name = "maintenance"

    def turn_on(self, device: Device) -> dict[str, Any]:
        return self._blocked(device)

    def turn_off(self, device: Device) -> dict[str, Any]:
        return self._blocked(device)

    def _blocked(self, device: Device) -> dict[str, Any]:
        return {
            "success": False,
            "message": f"{device.name} на обслуживании — управление недоступно",
            "status": device.status,
        }


STATE_MAP: dict[str, DeviceState] = {
    Device.Status.OFF: OffState(),
    Device.Status.ON: OnState(),
    Device.Status.ERROR: ErrorState(),
    Device.Status.MAINTENANCE: MaintenanceState(),
}


class DeviceStateContext:
    """Context для State."""

    def __init__(self, device: Device) -> None:
        self.device = device

    def get_state(self) -> DeviceState:
        return STATE_MAP.get(self.device.status, OffState())

    def turn_on(self) -> dict[str, Any]:
        return self.get_state().turn_on(self.device)

    def turn_off(self) -> dict[str, Any]:
        return self.get_state().turn_off(self.device)

    def report(self) -> dict[str, Any]:
        return self.get_state().report(self.device)
