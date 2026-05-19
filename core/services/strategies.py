from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction, Home
from core.services.device_router import DeviceRouter


class EnergyStrategy:
    """Strategy — базовая стратегия управления домом."""

    def apply(self, home: Home) -> dict[str, Any]:
        raise NotImplementedError


class ComfortStrategy(EnergyStrategy):
    def apply(self, home: Home) -> dict[str, Any]:
        return {
            "strategy": "ComfortStrategy",
            "home": home.name,
            "message": "Включён комфортный режим: приоритет — удобство жильцов",
            "processed_devices": 0,
        }


class EconomyStrategy(EnergyStrategy):
    def apply(self, home: Home) -> dict[str, Any]:
        router = DeviceRouter()
        processed = 0
        results: list[dict[str, Any]] = []

        devices = Device.objects.filter(
            room__home=home,
            power_watts__gt=100,
            is_active=True,
        )

        for device in devices:
            if router.check_action_allowed(device, DeviceAction.TURN_OFF):
                result = router.execute_command(device, DeviceAction.TURN_OFF)
                if result.get("success"):
                    processed += 1
                    results.append(result)

        return {
            "strategy": "EconomyStrategy",
            "home": home.name,
            "message": f"Экономичный режим: обработано устройств — {processed}",
            "processed_devices": processed,
            "results": results,
        }


class SecurityStrategy(EnergyStrategy):
    def apply(self, home: Home) -> dict[str, Any]:
        router = DeviceRouter()
        processed = 0
        security_devices = Device.objects.filter(
            room__home=home,
            device_type=Device.DeviceType.SECURITY,
            is_active=True,
        )

        for device in security_devices:
            for action in (
                DeviceAction.START,
                DeviceAction.LOCK,
                DeviceAction.TURN_ON,
            ):
                if router.check_action_allowed(device, action):
                    result = router.execute_command(device, action)
                    if result.get("success"):
                        processed += 1
                        break

        return {
            "strategy": "SecurityStrategy",
            "home": home.name,
            "message": f"Режим безопасности: активировано устройств — {processed}",
            "processed_devices": processed,
        }


class SmartHomeModeContext:
    """Context для Strategy."""

    def __init__(self, strategy: EnergyStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: EnergyStrategy) -> None:
        self._strategy = strategy

    def apply_strategy(self, home: Home) -> dict[str, Any]:
        return self._strategy.apply(home)
