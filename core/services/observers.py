from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import EventLog, SensorReading


class SensorObserver(ABC):
    @abstractmethod
    def update(self, reading: SensorReading) -> None:
        pass


class SensorSubject:
    """Observer — субъект для показаний датчиков."""

    def __init__(self) -> None:
        self._observers: list[SensorObserver] = []

    def attach(self, observer: SensorObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: SensorObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, reading: SensorReading) -> None:
        for observer in self._observers:
            observer.update(reading)


class EventLogObserver(SensorObserver):
    def update(self, reading: SensorReading) -> None:
        home = reading.device.room.home
        EventLog.objects.create(
            home=home,
            device=reading.device,
            event_type=EventLog.EventType.SENSOR,
            message=(
                f"Показание: {reading.get_reading_type_display()} "
                f"= {reading.value} {reading.unit}".strip()
            ),
        )


class ConsoleNotificationObserver(SensorObserver):
    def __init__(self) -> None:
        self.last_message: str = ""

    def update(self, reading: SensorReading) -> None:
        self.last_message = (
            f"[Console] {reading.device.name}: "
            f"{reading.reading_type} = {reading.value}"
        )


class EnergyWarningObserver(SensorObserver):
    def update(self, reading: SensorReading) -> None:
        from core.models import SensorReading as SR

        if (
            reading.reading_type == SR.ReadingType.ENERGY
            and reading.value > 2
        ):
            EventLog.objects.create(
                home=reading.device.room.home,
                device=reading.device,
                event_type=EventLog.EventType.WARNING,
                message=(
                    f"Высокое энергопотребление: {reading.value} "
                    f"{reading.unit}"
                ),
            )
