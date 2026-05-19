from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction
from core.services.device_router import DeviceRouter


class DeviceAccessProxy:
    """Proxy — контроль доступа к устройству."""

    RESTRICTED_ACTIONS = (
        DeviceAction.LOCK,
        DeviceAction.UNLOCK,
        DeviceAction.SET_TEMPERATURE,
    )

    def __init__(self, device: Device, user_role: str = "user") -> None:
        self.device = device
        self.user_role = user_role
        self._router = DeviceRouter()

    def check_access(self, action_name: str) -> dict[str, Any]:
        """Проверка доступа без выполнения команды."""
        if (
            self.user_role != "admin"
            and action_name in self.RESTRICTED_ACTIONS
        ):
            return {
                "success": False,
                "message": (
                    f"Доступ запрещён: роль '{self.user_role}' "
                    f"не может выполнить '{action_name}'"
                ),
            }

        if not self.device.is_active:
            return {
                "success": False,
                "message": f"Устройство {self.device.name} неактивно",
            }

        return {"success": True}

    def execute(self, action_name: str, value: str = "") -> dict[str, Any]:
        access = self.check_access(action_name)
        if not access.get("success"):
            return access

        return self._router.execute_command(self.device, action_name, value)
