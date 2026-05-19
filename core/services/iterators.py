from __future__ import annotations

from collections.abc import Iterable, Iterator

from core.models import Device, Home


class DeviceIterator:
    """Iterator — перебор устройств."""

    def __init__(self, devices: Iterable[Device]) -> None:
        self._devices = list(devices)
        self._index = 0

    def __iter__(self) -> DeviceIterator:
        return self

    def __next__(self) -> Device:
        if self._index >= len(self._devices):
            raise StopIteration
        device = self._devices[self._index]
        self._index += 1
        return device


class ActiveDeviceIterator(DeviceIterator):
    """Iterator — только активные устройства."""

    def __init__(self, devices: Iterable[Device]) -> None:
        active_devices = [device for device in devices if device.is_active]
        super().__init__(active_devices)


def get_active_devices(home: Home) -> list[Device]:
    devices = Device.objects.filter(room__home=home).order_by("room__name", "name")
    iterator = ActiveDeviceIterator(devices)
    return list(iterator)
