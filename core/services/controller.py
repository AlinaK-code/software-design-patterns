from __future__ import annotations

from typing import Any

from core.models import Device, EventLog, Home, Room, Scenario


class SmartHomeController:
    """Singleton — единый контроллер умного дома."""

    _instance: SmartHomeController | None = None

    def __new__(cls) -> SmartHomeController:
        if cls._instance is None:
            instance = super().__new__(cls)
            instance.initialized = True
            cls._instance = instance
        return cls._instance

    def get_status(self) -> dict[str, Any]:
        return {
            "controller": "SmartHomeController",
            "initialized": self.initialized,
        }

    def get_home_summary(self, home: Home) -> dict[str, int]:
        return {
            "home": home.name,
            "rooms": Room.objects.filter(home=home).count(),
            "devices": Device.objects.filter(room__home=home).count(),
            "scenarios": Scenario.objects.filter(home=home).count(),
            "events": EventLog.objects.filter(home=home).count(),
        }
