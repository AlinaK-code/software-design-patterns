from __future__ import annotations

from typing import Any

from core.models import Device, EventLog
from core.services.device_router import DeviceRouter


class DeviceService:
    """Decorator — базовый сервис устройства."""

    def __init__(self, device: Device) -> None:
        self.device = device

    def get_description(self) -> str:
        raise NotImplementedError

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        raise NotImplementedError


class BasicDeviceService(DeviceService):
    def __init__(self, device: Device) -> None:
        super().__init__(device)
        self._router = DeviceRouter()

    def get_description(self) -> str:
        return f"Базовый сервис для {self.device.name}"

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        return self._router.execute_command(self.device, action_name, value)


class DeviceServiceDecorator(DeviceService):
    def __init__(self, wrapped: DeviceService) -> None:
        self._wrapped = wrapped
        super().__init__(wrapped.device)

    def get_description(self) -> str:
        return self._wrapped.get_description()

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        return self._wrapped.execute(action_name, value)


class LoggingDeviceDecorator(DeviceServiceDecorator):
    def get_description(self) -> str:
        return f"Логирование: {self._wrapped.get_description()}"

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        result = super().execute(action_name, value)
        EventLog.objects.create(
            home=self.device.room.home,
            device=self.device,
            event_type=EventLog.EventType.INFO,
            message=(
                f"[LoggingDecorator] Действие {action_name} "
                f"на устройстве {self.device.name}"
            ),
        )
        return result


class NotificationDeviceDecorator(DeviceServiceDecorator):
    def get_description(self) -> str:
        return f"Уведомления: {self._wrapped.get_description()}"

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        result = super().execute(action_name, value)
        result["notification"] = (
            f"Уведомление: {self.device.name} — {action_name} "
            f"({'успех' if result.get('success') else 'ошибка'})"
        )
        return result


class EnergyMonitoringDecorator(DeviceServiceDecorator):
    def get_description(self) -> str:
        return f"Мониторинг энергии: {self._wrapped.get_description()}"

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        result = super().execute(action_name, value)
        result["estimated_power_watts"] = self.device.power_watts
        return result
