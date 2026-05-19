from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import SensorReading
from core.services.observers import (
    ConsoleNotificationObserver,
    EnergyWarningObserver,
    EventLogObserver,
    SensorSubject,
)

_sensor_subject: SensorSubject | None = None


def get_sensor_subject() -> SensorSubject:
    global _sensor_subject
    if _sensor_subject is None:
        subject = SensorSubject()
        subject.attach(EventLogObserver())
        subject.attach(ConsoleNotificationObserver())
        subject.attach(EnergyWarningObserver())
        _sensor_subject = subject
    return _sensor_subject


@receiver(post_save, sender=SensorReading)
def notify_sensor_observers(sender, instance: SensorReading, created: bool, **kwargs):
    if not created:
        return
    get_sensor_subject().notify(instance)
