from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.models import (
    Device,
    DeviceAction,
    EventLog,
    Home,
    Room,
    Scenario,
    ScenarioAction,
)
from core.services.adapters import ExternalWeatherService, WeatherServiceAdapter
from core.services.commands import (
    CommandInvoker,
    LockCommand,
    SetBrightnessCommand,
    SetTemperatureCommand,
    ToggleCommand,
    TurnOffCommand,
    TurnOnCommand,
    UnlockCommand,
)
from core.services.composite import build_home_composite
from core.services.controller import SmartHomeController
from core.services.decorators import (
    BasicDeviceService,
    EnergyMonitoringDecorator,
    LoggingDeviceDecorator,
    NotificationDeviceDecorator,
)
from core.services.demo import run_patterns_demo
from core.services.energy import calculate_home_energy_report
from core.services.factories import (
    ClimateDeviceFactory,
    LightingDeviceFactory,
    SecurityDeviceFactory,
)
from core.services.iterators import get_active_devices
from core.services.proxy import DeviceAccessProxy
from core.services.scenarios import ScenarioRunnerFactory
from core.services.states import DeviceStateContext
from core.services.strategies import (
    ComfortStrategy,
    EconomyStrategy,
    SecurityStrategy,
    SmartHomeModeContext,
)

STRATEGY_CLASSES = {
    "comfort": ComfortStrategy,
    "economy": EconomyStrategy,
    "security": SecurityStrategy,
}

BUTTON_ACTIONS = {
    DeviceAction.TURN_ON,
    DeviceAction.TURN_OFF,
    DeviceAction.TOGGLE,
}

COMMAND_CLASSES = {
    DeviceAction.TURN_ON: TurnOnCommand,
    DeviceAction.TURN_OFF: TurnOffCommand,
    DeviceAction.TOGGLE: ToggleCommand,
    DeviceAction.SET_TEMPERATURE: SetTemperatureCommand,
    DeviceAction.SET_BRIGHTNESS: SetBrightnessCommand,
    DeviceAction.LOCK: LockCommand,
    DeviceAction.UNLOCK: UnlockCommand,
}

FACTORY_CLASSES = {
    "lighting": LightingDeviceFactory,
    "climate": ClimateDeviceFactory,
    "security": SecurityDeviceFactory,
}

FACTORY_LABELS = {
    "lighting": "лампу",
    "climate": "климатическое устройство",
    "security": "устройство безопасности",
}

FACTORY_DEFAULT_NAMES = {
    "lighting": "Лампа (фабрика)",
    "climate": "Климат (фабрика)",
    "security": "Охрана (фабрика)",
}

PATTERN_CARDS = (
    ("singleton", "Singleton", "Единый контроллер умного дома (core/services/controller.py)."),
    ("energy_model", "Energy Model", "Математическая модель энергопотребления (core/services/energy.py)."),
    ("strategy", "Strategy", "Стратегии Comfort / Economy / Security (core/services/strategies.py)."),
    ("command", "Command", "Команды устройств и история выполнения (core/services/commands.py)."),
    ("state", "State", "Состояния устройства Off / On / Error / Maintenance (core/services/states.py)."),
    ("adapter", "Adapter", "Адаптер внешнего погодного API (core/services/adapters.py)."),
    ("composite", "Composite", "Иерархия Дом → Комната → Устройство (core/services/composite.py)."),
    ("iterator", "Iterator", "Перебор активных устройств (core/services/iterators.py)."),
    ("template_method", "Template Method", "Шаблон выполнения сценариев (core/services/scenarios.py)."),
    ("proxy", "Proxy", "Контроль доступа к устройству (core/services/proxy.py)."),
    ("decorator", "Decorator", "Декораторы сервиса устройства (core/services/decorators.py)."),
    ("observer", "Observer", "Наблюдатели за показаниями датчиков (core/services/observers.py)."),
)


def _get_demo_home() -> Home | None:
    return Home.objects.first()


def _get_user_role(request) -> str:
    if getattr(request, "user", None) and request.user.is_staff:
        return "admin"
    return "user"


def _build_decorated_service_description(device: Device) -> str:
    service = BasicDeviceService(device)
    service = LoggingDeviceDecorator(service)
    service = NotificationDeviceDecorator(service)
    service = EnergyMonitoringDecorator(service)
    return service.get_description()


def dashboard_view(request):
    home = _get_demo_home()
    context = {"home": home, "no_data": home is None}

    if home:
        controller = SmartHomeController()
        home_composite = build_home_composite(home)
        active_devices = get_active_devices(home)
        environment = WeatherServiceAdapter(ExternalWeatherService()).get_environment()

        context.update(
            {
                "controller_summary": controller.get_home_summary(home),
                "controller_status": controller.get_status(),
                "rooms_count": Room.objects.filter(home=home).count(),
                "devices_count": Device.objects.filter(room__home=home).count(),
                "active_devices_count": len(active_devices),
                "scenarios_count": Scenario.objects.filter(home=home).count(),
                "recent_events": EventLog.objects.filter(home=home)[:5],
                "energy_report": calculate_home_energy_report(home, hours=24),
                "rooms": Room.objects.filter(home=home).prefetch_related("devices"),
                "total_power_watts": home_composite.get_power_usage(),
                "active_devices": active_devices,
                "environment": environment,
            }
        )

    return render(request, "core/dashboard.html", context)


@require_POST
def apply_strategy_view(request, strategy_name):
    home = _get_demo_home()
    if home is None:
        messages.error(request, "Демо-данные не найдены. Запустите: python manage.py seed_smart_home")
        return redirect("dashboard")

    strategy_class = STRATEGY_CLASSES.get(strategy_name)
    if strategy_class is None:
        messages.error(request, f"Неизвестная стратегия: {strategy_name}")
        return redirect("dashboard")

    context = SmartHomeModeContext(strategy_class())
    result = context.apply_strategy(home)
    messages.success(request, result.get("message", "Стратегия применена"))
    return redirect("dashboard")


def devices_view(request):
    home = _get_demo_home()
    devices = (
        Device.objects.filter(room__home=home)
        .select_related("room")
        .prefetch_related("capabilities")
        .order_by("room__name", "name")
        if home
        else Device.objects.none()
    )

    device_items = [
        {
            "device": device,
            "decorator_description": _build_decorated_service_description(device),
            "state_report": DeviceStateContext(device).report(),
        }
        for device in devices
    ]

    return render(
        request,
        "core/devices.html",
        {
            "home": home,
            "no_data": home is None,
            "device_items": device_items,
            "button_actions": BUTTON_ACTIONS,
        },
    )


@require_POST
def device_command_view(request, device_id):
    device = get_object_or_404(Device, pk=device_id)
    action_name = request.POST.get("action_name", "")
    value = request.POST.get("value", "")

    proxy = DeviceAccessProxy(device, user_role=_get_user_role(request))
    access = proxy.check_access(action_name)
    if not access.get("success"):
        messages.error(request, access.get("message", "Доступ запрещён"))
        return redirect("devices")

    command_class = COMMAND_CLASSES.get(action_name)
    if command_class:
        result = CommandInvoker().execute(command_class(device, value))
    else:
        result = proxy.execute(action_name, value)

    if result.get("success"):
        messages.success(request, result.get("message", "Команда выполнена"))
    else:
        messages.error(request, result.get("message", "Команда не выполнена"))

    return redirect("devices")


@require_POST
def factory_device_create_view(request, factory_type):
    factory_class = FACTORY_CLASSES.get(factory_type)
    if factory_class is None:
        messages.error(request, "Неизвестный тип фабрики")
        return redirect("devices")

    home = _get_demo_home()
    if home is None:
        messages.error(request, "Сначала создайте демо-данные: seed_smart_home")
        return redirect("devices")

    room = Room.objects.filter(home=home).order_by("id").first()
    if room is None:
        messages.error(request, "В доме нет комнат")
        return redirect("devices")

    base_name = FACTORY_DEFAULT_NAMES[factory_type]
    existing_count = Device.objects.filter(room=room, name__startswith=base_name).count()
    device_name = base_name if existing_count == 0 else f"{base_name} {existing_count + 1}"

    device = factory_class().build(room, device_name)
    messages.success(
        request,
        f"Создано устройство «{device.name}» через {factory_class.__name__}",
    )
    return redirect("devices")


def scenarios_view(request):
    home = _get_demo_home()
    scenarios = (
        Scenario.objects.filter(home=home)
        .prefetch_related(
            Prefetch(
                "actions",
                queryset=ScenarioAction.objects.select_related("device").order_by("order"),
            )
        )
        if home
        else Scenario.objects.none()
    )

    return render(
        request,
        "core/scenarios.html",
        {"home": home, "no_data": home is None, "scenarios": scenarios},
    )


@require_POST
def run_scenario_view(request, scenario_id):
    scenario = get_object_or_404(Scenario, pk=scenario_id)
    runner = ScenarioRunnerFactory.get_runner(scenario)
    result = runner.run()

    if result.get("valid") is False or result.get("success") is False:
        messages.error(request, result.get("message", "Сценарий не выполнен"))
    else:
        messages.success(
            request,
            result.get("message", f"Сценарий «{scenario.name}» выполнен"),
        )

    return redirect("scenarios")


def events_view(request):
    home = _get_demo_home()
    events = (
        EventLog.objects.filter(home=home)
        .select_related("device")
        .order_by("-created_at")[:50]
        if home
        else EventLog.objects.none()
    )

    return render(
        request,
        "core/events.html",
        {"home": home, "no_data": home is None, "events": events},
    )


def patterns_demo_view(request):
    home = _get_demo_home()
    context = {"home": home, "no_data": home is None, "pattern_cards": []}

    if home:
        demo_result = run_patterns_demo(home)
        context["demo_result"] = demo_result
        context["pattern_cards"] = [
            {
                "key": key,
                "title": title,
                "description": description,
                "data": demo_result.get(key, "Нет данных"),
            }
            for key, title, description in PATTERN_CARDS
        ]

    return render(request, "core/patterns_demo.html", context)
