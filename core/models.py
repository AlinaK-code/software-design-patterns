from django.db import models


class DeviceAction(models.TextChoices):
    TURN_ON = "turn_on", "Включить"
    TURN_OFF = "turn_off", "Выключить"
    TOGGLE = "toggle", "Переключить"
    SET_TEMPERATURE = "set_temperature", "Установить температуру"
    SET_BRIGHTNESS = "set_brightness", "Установить яркость"
    SET_COLOR = "set_color", "Установить цвет"
    SET_VOLUME = "set_volume", "Установить громкость"
    START = "start", "Запустить"
    STOP = "stop", "Остановить"
    LOCK = "lock", "Заблокировать"
    UNLOCK = "unlock", "Разблокировать"


class Home(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Дом"
        verbose_name_plural = "Дома"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Room(models.Model):
    home = models.ForeignKey(
        Home,
        related_name="rooms",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    floor = models.IntegerField(default=1)

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"
        ordering = ["home", "floor", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.home.name})"


class Device(models.Model):
    class DeviceType(models.TextChoices):
        LIGHT = "light", "Освещение"
        CLIMATE = "climate", "Климат"
        SECURITY = "security", "Безопасность"
        KITCHEN = "kitchen", "Кухня"
        SENSOR = "sensor", "Датчик"
        MEDIA = "media", "Медиа"
        OTHER = "other", "Другое"

    class Status(models.TextChoices):
        OFF = "off", "Выключено"
        ON = "on", "Включено"
        ERROR = "error", "Ошибка"
        MAINTENANCE = "maintenance", "Обслуживание"

    room = models.ForeignKey(
        Room,
        related_name="devices",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    device_type = models.CharField(
        max_length=20,
        choices=DeviceType.choices,
        default=DeviceType.OTHER,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OFF,
    )
    value = models.CharField(max_length=100, blank=True, default="")
    power_watts = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Устройство"
        verbose_name_plural = "Устройства"
        ordering = ["room", "name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.get_device_type_display()}]"


class DeviceCapability(models.Model):
    device = models.ForeignKey(
        Device,
        related_name="capabilities",
        on_delete=models.CASCADE,
    )
    action_name = models.CharField(
        max_length=30,
        choices=DeviceAction.choices,
    )
    is_enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Возможность устройства"
        verbose_name_plural = "Возможности устройств"
        ordering = ["device", "action_name"]

    def __str__(self) -> str:
        return f"{self.device.name}: {self.get_action_name_display()}"


class Scenario(models.Model):
    home = models.ForeignKey(
        Home,
        related_name="scenarios",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сценарий"
        verbose_name_plural = "Сценарии"
        ordering = ["home", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.home.name})"


class ScenarioAction(models.Model):
    scenario = models.ForeignKey(
        Scenario,
        related_name="actions",
        on_delete=models.CASCADE,
    )
    device = models.ForeignKey(
        Device,
        related_name="scenario_actions",
        on_delete=models.CASCADE,
    )
    command = models.CharField(
        max_length=30,
        choices=DeviceAction.choices,
    )
    value = models.CharField(max_length=100, blank=True, default="")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Действие сценария"
        verbose_name_plural = "Действия сценариев"
        ordering = ["order"]

    def __str__(self) -> str:
        return (
            f"#{self.order} {self.scenario.name} → "
            f"{self.device.name}: {self.get_command_display()}"
        )


class SensorReading(models.Model):
    class ReadingType(models.TextChoices):
        TEMPERATURE = "temperature", "Температура"
        HUMIDITY = "humidity", "Влажность"
        MOTION = "motion", "Движение"
        ENERGY = "energy", "Энергопотребление"
        LIGHT = "light", "Освещённость"
        OTHER = "other", "Другое"

    device = models.ForeignKey(
        Device,
        related_name="readings",
        on_delete=models.CASCADE,
    )
    reading_type = models.CharField(
        max_length=20,
        choices=ReadingType.choices,
    )
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Показание датчика"
        verbose_name_plural = "Показания датчиков"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        unit = f" {self.unit}" if self.unit else ""
        return (
            f"{self.device.name}: {self.get_reading_type_display()} "
            f"= {self.value}{unit}"
        )


class EventLog(models.Model):
    class EventType(models.TextChoices):
        INFO = "info", "Информация"
        COMMAND = "command", "Команда"
        WARNING = "warning", "Предупреждение"
        ERROR = "error", "Ошибка"
        SCENARIO = "scenario", "Сценарий"
        SENSOR = "sensor", "Датчик"

    home = models.ForeignKey(
        Home,
        related_name="events",
        on_delete=models.CASCADE,
    )
    device = models.ForeignKey(
        Device,
        related_name="events",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.INFO,
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Событие"
        verbose_name_plural = "Журнал событий"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        device_part = f" / {self.device.name}" if self.device else ""
        return f"[{self.get_event_type_display()}] {self.home.name}{device_part}"
