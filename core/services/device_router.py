from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction, DeviceCapability, EventLog


class DeviceRouter:
    """Маршрутизатор команд к устройствам."""

    def check_action_allowed(self, device: Device, action_name: str) -> bool:
        return DeviceCapability.objects.filter(
            device=device,
            action_name=action_name,
            is_enabled=True,
        ).exists()

    def execute_command(
        self,
        device: Device,
        action_name: str,
        value: str = "",
    ) -> dict[str, Any]:
        home = device.room.home

        if not device.is_active:
            message = f"Устройство {device.name} неактивно"
            EventLog.objects.create(
                home=home,
                device=device,
                event_type=EventLog.EventType.ERROR,
                message=message,
            )
            return {"success": False, "message": message}

        if not self.check_action_allowed(device, action_name):
            message = (
                f"Действие '{action_name}' не поддерживается устройством {device.name}"
            )
            EventLog.objects.create(
                home=home,
                device=device,
                event_type=EventLog.EventType.ERROR,
                message=message,
            )
            return {"success": False, "message": message}

        if action_name == DeviceAction.TURN_ON:
            device.status = Device.Status.ON
        elif action_name == DeviceAction.TURN_OFF:
            device.status = Device.Status.OFF
        elif action_name == DeviceAction.TOGGLE:
            device.status = (
                Device.Status.OFF
                if device.status == Device.Status.ON
                else Device.Status.ON
            )
        elif value:
            device.value = value

        device.save()

        EventLog.objects.create(
            home=home,
            device=device,
            event_type=EventLog.EventType.COMMAND,
            message=(
                f"Команда {action_name} выполнена для {device.name}"
                + (f" (value={value})" if value else "")
            ),
        )

        return {
            "success": True,
            "device": device.name,
            "action": action_name,
            "value": value,
            "status": device.status,
            "message": "Команда выполнена",
        }
