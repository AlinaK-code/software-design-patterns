from __future__ import annotations

from typing import Any

from core.models import Device, Home, Scenario
from core.services.composite import build_home_composite
from core.services.controller import SmartHomeController
from core.services.energy import calculate_home_energy_report
from core.services.iterators import get_active_devices
from core.services.observers import SensorSubject, EventLogObserver
from core.services.strategies import (
    ComfortStrategy,
    EconomyStrategy,
    SecurityStrategy,
    SmartHomeModeContext,
)
from core.services.states import DeviceStateContext


class SmartHomeFacade:
    """
    Facade — упрощённый интерфейс для взаимодействия со всеми подсистемами умного дома.
    Скрывает сложность работы с контроллером, стратегиями, состояниями, наблюдателями и т.д.
    """

    def __init__(self, home: Home) -> None:
        self.home = home
        self._controller = SmartHomeController()
        self._composite = build_home_composite(home)

    def get_home_status(self) -> dict[str, Any]:
        """Получить общий статус дома через Singleton контроллер."""
        return {
            "controller_status": self._controller.get_status(),
            "home_summary": self._controller.get_home_summary(self.home),
            "total_power_watts": self._composite.get_power_usage(),
        }

    def set_mode(self, mode: str) -> dict[str, Any]:
        """Установить режим работы дома через Strategy."""
        strategy_map = {
            "comfort": ComfortStrategy,
            "economy": EconomyStrategy,
            "security": SecurityStrategy,
        }

        strategy_class = strategy_map.get(mode)
        if not strategy_class:
            return {"success": False, "message": f"Неизвестный режим: {mode}"}

        context = SmartHomeModeContext(strategy_class())
        return context.apply_strategy(self.home)

    def toggle_device(self, device_id: int) -> dict[str, Any]:
        """Переключить устройство через State."""
        device = Device.objects.get(pk=device_id, room__home=self.home)
        state_ctx = DeviceStateContext(device)

        if device.status == Device.Status.ON:
            return state_ctx.turn_off()
        return state_ctx.turn_on()

    def get_energy_report(self, hours: float = 24) -> dict[str, Any]:
        """Получить отчёт по энергопотреблению (математическая модель)."""
        return calculate_home_energy_report(self.home, hours)

    def get_active_devices_list(self) -> list[Device]:
        """Получить список активных устройств через Iterator."""
        return get_active_devices(self.home)

    def attach_sensor_observer(self, observer_type: str = "log") -> SensorSubject:
        """Подключить наблюдателя к датчикам через Observer."""
        subject = SensorSubject()
        if observer_type == "log":
            subject.attach(EventLogObserver())
        return subject

    def get_structure_info(self) -> dict[str, Any]:
        """Получить информацию о структуре дома через Composite."""
        return {
            "home_name": self._composite.get_name(),
            "rooms": [room.get_name() for room in self._composite.get_children()],
            "total_power": self._composite.get_power_usage(),
        }
