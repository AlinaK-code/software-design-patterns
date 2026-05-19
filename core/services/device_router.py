from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction, DeviceCapability, EventLog
from core.services.states import DeviceStateContext

STATE_ACTIONS = {
    DeviceAction.TURN_ON,
    DeviceAction.TURN_OFF,
    DeviceAction.TOGGLE,
}


class DeviceRouter:
    """Маршрутизатор команд к устройствам."""

    def check_action_allowed(self, device: Device, action_name: str) -> bool:
        return DeviceCapability.objects.filter(
            device=device,
            action_name=action_name,
            is_enabled=True,
        ).exists()

    def _execute_state_action(
        self,
        device: Device,
        action_name: str,
    ) -> dict[str, Any]:
        context = DeviceStateContext(device)

        if action_name == DeviceAction.TURN_ON:
            return context.turn_on()
        if action_name == DeviceAction.TURN_OFF:
            return context.turn_off()
        if action_name == DeviceAction.TOGGLE:
            if device.status == Device.Status.ON:
                return context.turn_off()
            return context.turn_on()

        return {"success": False, "message": "Неизвестное state-действие"}

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

        if action_name in STATE_ACTIONS:
            state_result = self._execute_state_action(device, action_name)
            device.refresh_from_db()

            if not state_result.get("success"):
                message = state_result.get("message", "Действие отклонено состоянием")
                EventLog.objects.create(
                    home=home,
                    device=device,
                    event_type=EventLog.EventType.ERROR,
                    message=message,
                )
                return {
                    "success": False,
                    "device": device.name,
                    "action": action_name,
                    "value": value,
                    "status": device.status,
                    "message": message,
                }

            device.save()
            message = state_result.get("message", "Команда выполнена")
            EventLog.objects.create(
                home=home,
                device=device,
                event_type=EventLog.EventType.COMMAND,
                message=f"Команда {action_name} (State): {message}",
            )
            return {
                "success": True,
                "device": device.name,
                "action": action_name,
                "value": value,
                "status": device.status,
                "message": message,
            }

        if value:
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
