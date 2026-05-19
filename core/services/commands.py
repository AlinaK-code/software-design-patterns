from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction
from core.services.device_router import DeviceRouter


class DeviceCommand:
    """Command — базовая команда устройства."""

    action_name: str = ""

    def __init__(self, device: Device, value: str = "") -> None:
        self.device = device
        self.value = value
        self._router = DeviceRouter()
        self._previous_status = device.status
        self._previous_value = device.value

    def execute(self) -> dict[str, Any]:
        return self._router.execute_command(
            self.device,
            self.action_name,
            self.value,
        )

    def undo(self) -> dict[str, Any]:
        self.device.status = self._previous_status
        self.device.value = self._previous_value
        self.device.save()
        return {
            "success": True,
            "message": f"Отмена команды {self.action_name} для {self.device.name}",
            "status": self.device.status,
        }


class TurnOnCommand(DeviceCommand):
    action_name = DeviceAction.TURN_ON


class TurnOffCommand(DeviceCommand):
    action_name = DeviceAction.TURN_OFF


class ToggleCommand(DeviceCommand):
    action_name = DeviceAction.TOGGLE


class SetTemperatureCommand(DeviceCommand):
    action_name = DeviceAction.SET_TEMPERATURE


class SetBrightnessCommand(DeviceCommand):
    action_name = DeviceAction.SET_BRIGHTNESS


class LockCommand(DeviceCommand):
    action_name = DeviceAction.LOCK


class UnlockCommand(DeviceCommand):
    action_name = DeviceAction.UNLOCK


class CommandInvoker:
    """Invoker — выполняет команды и хранит историю."""

    def __init__(self) -> None:
        self.history: list[DeviceCommand] = []

    def execute(self, command: DeviceCommand) -> dict[str, Any]:
        result = command.execute()
        self.history.append(command)
        return result

    def get_history(self) -> list[str]:
        return [command.__class__.__name__ for command in self.history]
