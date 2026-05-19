from __future__ import annotations

from typing import Any

from core.models import Device, DeviceAction, DeviceCapability, Home, Scenario, SensorReading
from core.services.adapters import ExternalWeatherService, WeatherServiceAdapter
from core.services.commands import CommandInvoker, TurnOnCommand
from core.services.composite import build_home_composite
from core.services.controller import SmartHomeController
from core.services.decorators import (
    BasicDeviceService,
    EnergyMonitoringDecorator,
    LoggingDeviceDecorator,
    NotificationDeviceDecorator,
)
from core.services.energy import calculate_home_energy_report
from core.services.iterators import get_active_devices
from core.services.observers import (
    ConsoleNotificationObserver,
    EnergyWarningObserver,
    EventLogObserver,
    SensorSubject,
)
from core.services.proxy import DeviceAccessProxy
from core.services.scenarios import ScenarioRunnerFactory
from core.services.states import DeviceStateContext
from core.services.strategies import EconomyStrategy, SmartHomeModeContext


def _safe(message: str) -> dict[str, Any]:
    return {"success": False, "message": message}


def run_patterns_demo(home: Home | None = None) -> dict[str, Any]:
    """Демонстрация всех паттернов проектирования на данных дома."""
    result: dict[str, Any] = {}

    if home is None:
        home = Home.objects.first()

    if home is None:
        return {
            "error": "Нет домов в базе. Выполните: python manage.py seed_smart_home",
        }

    # Singleton
    controller = SmartHomeController()
    result["singleton"] = {
        "status": controller.get_status(),
        "summary": controller.get_home_summary(home),
        "same_instance": SmartHomeController() is controller,
    }

    # Energy model
    result["energy_model"] = calculate_home_energy_report(home)

    # Strategy
    try:
        context = SmartHomeModeContext(EconomyStrategy())
        result["strategy"] = context.apply_strategy(home)
    except Exception as exc:
        result["strategy"] = _safe(str(exc))

    # Command
    try:
        device = (
            Device.objects.filter(
                room__home=home,
                capabilities__action_name=DeviceAction.TURN_ON,
                capabilities__is_enabled=True,
            )
            .distinct()
            .first()
        )
        if device is None:
            result["command"] = _safe("Нет устройств с turn_on")
        else:
            invoker = CommandInvoker()
            cmd_result = invoker.execute(TurnOnCommand(device))
            result["command"] = {
                "result": cmd_result,
                "history": invoker.get_history(),
            }
    except Exception as exc:
        result["command"] = _safe(str(exc))

    # State
    try:
        state_device = Device.objects.filter(room__home=home).first()
        if state_device is None:
            result["state"] = _safe("Нет устройств")
        else:
            state_ctx = DeviceStateContext(state_device)
            result["state"] = {
                "report": state_ctx.report(),
                "turn_on": state_ctx.turn_on(),
            }
    except Exception as exc:
        result["state"] = _safe(str(exc))

    # Adapter
    try:
        adapter = WeatherServiceAdapter(ExternalWeatherService())
        result["adapter"] = adapter.get_environment()
    except Exception as exc:
        result["adapter"] = _safe(str(exc))

    # Composite
    try:
        composite = build_home_composite(home)
        result["composite"] = {
            "home": composite.get_name(),
            "total_power_watts": composite.get_power_usage(),
            "rooms": [room.get_name() for room in composite.get_children()],
        }
    except Exception as exc:
        result["composite"] = _safe(str(exc))

    # Iterator
    try:
        active = get_active_devices(home)
        result["iterator"] = {
            "active_count": len(active),
            "devices": [device.name for device in active],
        }
    except Exception as exc:
        result["iterator"] = _safe(str(exc))

    # Template Method
    try:
        scenario = Scenario.objects.filter(home=home).first()
        if scenario is None:
            result["template_method"] = _safe("Нет сценариев")
        else:
            runner = ScenarioRunnerFactory.get_runner(scenario)
            result["template_method"] = runner.run()
    except Exception as exc:
        result["template_method"] = _safe(str(exc))

    # Proxy
    try:
        security_device = Device.objects.filter(
            room__home=home,
            device_type=Device.DeviceType.SECURITY,
        ).first()
        if security_device is None:
            result["proxy"] = _safe("Нет устройств безопасности")
        else:
            user_proxy = DeviceAccessProxy(security_device, user_role="user")
            admin_proxy = DeviceAccessProxy(security_device, user_role="admin")
            result["proxy"] = {
                "user_lock": user_proxy.execute(DeviceAction.LOCK),
                "admin_lock": admin_proxy.execute(DeviceAction.LOCK, "locked"),
            }
    except Exception as exc:
        result["proxy"] = _safe(str(exc))

    # Decorator
    try:
        decor_device = Device.objects.filter(room__home=home).first()
        if decor_device is None:
            result["decorator"] = _safe("Нет устройств")
        else:
            service = BasicDeviceService(decor_device)
            service = LoggingDeviceDecorator(service)
            service = NotificationDeviceDecorator(service)
            service = EnergyMonitoringDecorator(service)
            action = (
                DeviceCapability.objects.filter(
                    device=decor_device,
                    is_enabled=True,
                )
                .values_list("action_name", flat=True)
                .first()
                or DeviceAction.TURN_ON
            )
            result["decorator"] = {
                "description": service.get_description(),
                "execute": service.execute(action),
            }
    except Exception as exc:
        result["decorator"] = _safe(str(exc))

    # Observer (бонус для демо, не в keys но полезно)
    try:
        reading = SensorReading.objects.filter(device__room__home=home).first()
        if reading:
            subject = SensorSubject()
            console = ConsoleNotificationObserver()
            subject.attach(EventLogObserver())
            subject.attach(console)
            subject.attach(EnergyWarningObserver())
            subject.notify(reading)
            result["observer"] = {"last_message": console.last_message}
    except Exception:
        pass

    return result
