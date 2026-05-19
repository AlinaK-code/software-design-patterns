from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    Device,
    DeviceAction,
    DeviceCapability,
    EventLog,
    Home,
    Room,
    Scenario,
    ScenarioAction,
    SensorReading,
)

DEMO_HOME_NAME = "Демо-дом"
DEMO_HOME_ADDRESS = "ул. Ленина, 10"

ROOM_NAMES = ("Гостиная", "Кухня", "Спальня", "Коридор")

DEVICE_SPECS = (
    {
        "room": "Гостиная",
        "name": "Умная лампа",
        "device_type": Device.DeviceType.LIGHT,
        "status": Device.Status.OFF,
        "value": "0",
        "power_watts": 12,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.TOGGLE,
            DeviceAction.SET_BRIGHTNESS,
            DeviceAction.SET_COLOR,
        ),
    },
    {
        "room": "Гостиная",
        "name": "Телевизор",
        "device_type": Device.DeviceType.MEDIA,
        "status": Device.Status.OFF,
        "value": "0",
        "power_watts": 120,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.TOGGLE,
            DeviceAction.SET_VOLUME,
        ),
    },
    {
        "room": "Гостиная",
        "name": "Датчик движения",
        "device_type": Device.DeviceType.SENSOR,
        "status": Device.Status.ON,
        "value": "active",
        "power_watts": 2,
        "capabilities": (DeviceAction.START, DeviceAction.STOP),
    },
    {
        "room": "Кухня",
        "name": "Чайник",
        "device_type": Device.DeviceType.KITCHEN,
        "status": Device.Status.OFF,
        "value": "0",
        "power_watts": 1800,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.SET_TEMPERATURE,
        ),
    },
    {
        "room": "Кухня",
        "name": "Умная розетка",
        "device_type": Device.DeviceType.OTHER,
        "status": Device.Status.ON,
        "value": "enabled",
        "power_watts": 5,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.TOGGLE,
        ),
    },
    {
        "room": "Кухня",
        "name": "Датчик температуры кухни",
        "device_type": Device.DeviceType.SENSOR,
        "status": Device.Status.ON,
        "value": "24",
        "power_watts": 2,
        "capabilities": (DeviceAction.START, DeviceAction.STOP),
    },
    {
        "room": "Спальня",
        "name": "Кондиционер",
        "device_type": Device.DeviceType.CLIMATE,
        "status": Device.Status.OFF,
        "value": "22",
        "power_watts": 1200,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.SET_TEMPERATURE,
        ),
    },
    {
        "room": "Спальня",
        "name": "Ночник",
        "device_type": Device.DeviceType.LIGHT,
        "status": Device.Status.OFF,
        "value": "30",
        "power_watts": 8,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.SET_BRIGHTNESS,
        ),
    },
    {
        "room": "Коридор",
        "name": "Камера безопасности",
        "device_type": Device.DeviceType.SECURITY,
        "status": Device.Status.ON,
        "value": "recording",
        "power_watts": 15,
        "capabilities": (
            DeviceAction.TURN_ON,
            DeviceAction.TURN_OFF,
            DeviceAction.START,
            DeviceAction.STOP,
        ),
    },
    {
        "room": "Коридор",
        "name": "Умный замок",
        "device_type": Device.DeviceType.SECURITY,
        "status": Device.Status.ON,
        "value": "locked",
        "power_watts": 6,
        "capabilities": (DeviceAction.LOCK, DeviceAction.UNLOCK),
    },
)

SCENARIO_SPECS = (
    {
        "name": "Утро",
        "description": "Включает мягкий свет и подготавливает кухню.",
        "actions": (
            ("Ночник", DeviceAction.TURN_OFF, "off", 1),
            ("Умная лампа", DeviceAction.TURN_ON, "on", 2),
            ("Чайник", DeviceAction.TURN_ON, "90", 3),
        ),
    },
    {
        "name": "Ночь",
        "description": "Выключает лишние устройства и переводит дом в ночной режим.",
        "actions": (
            ("Телевизор", DeviceAction.TURN_OFF, "off", 1),
            ("Умная лампа", DeviceAction.TURN_OFF, "off", 2),
            ("Ночник", DeviceAction.TURN_ON, "30", 3),
            ("Умный замок", DeviceAction.LOCK, "locked", 4),
        ),
    },
    {
        "name": "Я ушёл",
        "description": "Отключает бытовые устройства и включает безопасность.",
        "actions": (
            ("Умная лампа", DeviceAction.TURN_OFF, "off", 1),
            ("Чайник", DeviceAction.TURN_OFF, "0", 2),
            ("Камера безопасности", DeviceAction.START, "recording", 3),
            ("Умный замок", DeviceAction.LOCK, "locked", 4),
        ),
    },
    {
        "name": "Экономия энергии",
        "description": "Снижает энергопотребление дома.",
        "actions": (
            ("Кондиционер", DeviceAction.SET_TEMPERATURE, "20", 1),
            ("Телевизор", DeviceAction.TURN_OFF, "off", 2),
            ("Умная розетка", DeviceAction.TURN_OFF, "disabled", 3),
        ),
    },
)

SENSOR_READING_SPECS = (
    ("Датчик температуры кухни", SensorReading.ReadingType.TEMPERATURE, 24.5, "°C"),
    ("Датчик температуры кухни", SensorReading.ReadingType.HUMIDITY, 42.0, "%"),
    ("Датчик движения", SensorReading.ReadingType.MOTION, 1.0, "bool"),
    ("Камера безопасности", SensorReading.ReadingType.MOTION, 0.0, "bool"),
    ("Умная лампа", SensorReading.ReadingType.ENERGY, 0.12, "kWh"),
    ("Телевизор", SensorReading.ReadingType.ENERGY, 1.4, "kWh"),
    ("Чайник", SensorReading.ReadingType.ENERGY, 0.8, "kWh"),
    ("Кондиционер", SensorReading.ReadingType.ENERGY, 2.5, "kWh"),
    ("Ночник", SensorReading.ReadingType.LIGHT, 30.0, "%"),
    ("Умная розетка", SensorReading.ReadingType.ENERGY, 0.3, "kWh"),
)

EVENT_LOG_SPECS = (
    (EventLog.EventType.INFO, None, "Демо-дом создан"),
    (EventLog.EventType.INFO, None, "Комнаты успешно добавлены"),
    (EventLog.EventType.COMMAND, "Умная лампа", "Устройство Умная лампа зарегистрировано"),
    (EventLog.EventType.COMMAND, "Чайник", "Устройство Чайник зарегистрировано"),
    (
        EventLog.EventType.SENSOR,
        "Датчик температуры кухни",
        "Получено показание температуры кухни",
    ),
    (EventLog.EventType.SCENARIO, None, "Сценарий Утро готов к запуску"),
    (EventLog.EventType.SCENARIO, None, "Сценарий Ночь готов к запуску"),
    (EventLog.EventType.WARNING, "Кондиционер", "Кондиционер потребляет много энергии"),
    (EventLog.EventType.INFO, "Камера безопасности", "Камера безопасности активна"),
    (
        EventLog.EventType.INFO,
        "Умный замок",
        "Умный замок находится в состоянии locked",
    ),
)


class Command(BaseCommand):
    help = "Заполняет базу демо-данными умного дома (идемпотентно)."

    def handle(self, *args, **options):
        with transaction.atomic():
            stats = self._seed()

        self.stdout.write(
            self.style.SUCCESS("Smart home demo data created successfully.")
        )
        self._print_stats(stats)

    def _seed(self) -> dict[str, int]:
        home, _ = Home.objects.get_or_create(
            name=DEMO_HOME_NAME,
            defaults={"address": DEMO_HOME_ADDRESS},
        )
        if home.address != DEMO_HOME_ADDRESS:
            home.address = DEMO_HOME_ADDRESS
            home.save(update_fields=["address"])

        rooms: dict[str, Room] = {}
        for index, room_name in enumerate(ROOM_NAMES, start=1):
            room, _ = Room.objects.get_or_create(
                home=home,
                name=room_name,
                defaults={"floor": index},
            )
            rooms[room_name] = room

        devices: dict[str, Device] = {}
        for spec in DEVICE_SPECS:
            device, _ = Device.objects.update_or_create(
                room=rooms[spec["room"]],
                name=spec["name"],
                defaults={
                    "device_type": spec["device_type"],
                    "status": spec["status"],
                    "value": spec["value"],
                    "power_watts": spec["power_watts"],
                    "is_active": True,
                },
            )
            devices[spec["name"]] = device

            for action in spec["capabilities"]:
                DeviceCapability.objects.get_or_create(
                    device=device,
                    action_name=action,
                    defaults={"is_enabled": True},
                )

        for scenario_spec in SCENARIO_SPECS:
            scenario, _ = Scenario.objects.update_or_create(
                home=home,
                name=scenario_spec["name"],
                defaults={
                    "description": scenario_spec["description"],
                    "is_active": True,
                },
            )

            for device_name, command, value, order in scenario_spec["actions"]:
                ScenarioAction.objects.update_or_create(
                    scenario=scenario,
                    order=order,
                    defaults={
                        "device": devices[device_name],
                        "command": command,
                        "value": value,
                    },
                )

        for device_name, reading_type, value, unit in SENSOR_READING_SPECS:
            SensorReading.objects.get_or_create(
                device=devices[device_name],
                reading_type=reading_type,
                value=value,
                defaults={"unit": unit},
            )

        for event_type, device_name, message in EVENT_LOG_SPECS:
            EventLog.objects.get_or_create(
                home=home,
                message=message,
                defaults={
                    "event_type": event_type,
                    "device": devices[device_name] if device_name else None,
                },
            )

        device_ids = [device.pk for device in devices.values()]
        scenario_ids = list(
            Scenario.objects.filter(home=home).values_list("pk", flat=True)
        )

        return {
            "homes": Home.objects.filter(pk=home.pk).count(),
            "rooms": Room.objects.filter(home=home).count(),
            "devices": Device.objects.filter(room__home=home).count(),
            "capabilities": DeviceCapability.objects.filter(
                device_id__in=device_ids
            ).count(),
            "scenarios": Scenario.objects.filter(home=home).count(),
            "scenario_actions": ScenarioAction.objects.filter(
                scenario_id__in=scenario_ids
            ).count(),
            "sensor_readings": SensorReading.objects.filter(
                device_id__in=device_ids
            ).count(),
            "event_logs": EventLog.objects.filter(home=home).count(),
        }

    def _print_stats(self, stats: dict[str, int]) -> None:
        labels = {
            "homes": "Homes",
            "rooms": "Rooms",
            "devices": "Devices",
            "capabilities": "Capabilities",
            "scenarios": "Scenarios",
            "scenario_actions": "Scenario actions",
            "sensor_readings": "Sensor readings",
            "event_logs": "Event logs",
        }
        for key, label in labels.items():
            self.stdout.write(f"{label}: {stats[key]}")
