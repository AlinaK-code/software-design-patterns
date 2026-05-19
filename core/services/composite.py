from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Device, Home, Room


class SmartHomeComponent(ABC):
    """Composite — базовый компонент иерархии умного дома."""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_children(self) -> list[SmartHomeComponent]:
        pass

    @abstractmethod
    def get_power_usage(self) -> int:
        pass


class DeviceLeaf(SmartHomeComponent):
    def __init__(self, device: Device) -> None:
        self.device = device

    def get_name(self) -> str:
        return self.device.name

    def get_children(self) -> list[SmartHomeComponent]:
        return []

    def get_power_usage(self) -> int:
        return self.device.power_watts


class RoomComposite(SmartHomeComponent):
    def __init__(self, room: Room, children: list[SmartHomeComponent] | None = None) -> None:
        self.room = room
        self._children = children or []

    def get_name(self) -> str:
        return self.room.name

    def get_children(self) -> list[SmartHomeComponent]:
        return self._children

    def get_power_usage(self) -> int:
        return sum(child.get_power_usage() for child in self._children)


class HomeComposite(SmartHomeComponent):
    def __init__(self, home: Home, children: list[SmartHomeComponent] | None = None) -> None:
        self.home = home
        self._children = children or []

    def get_name(self) -> str:
        return self.home.name

    def get_children(self) -> list[SmartHomeComponent]:
        return self._children

    def get_power_usage(self) -> int:
        return sum(child.get_power_usage() for child in self._children)


def build_home_composite(home: Home) -> HomeComposite:
    room_composites: list[RoomComposite] = []

    for room in Room.objects.filter(home=home).prefetch_related("devices"):
        device_leaves = [DeviceLeaf(device) for device in room.devices.all()]
        room_composites.append(RoomComposite(room, device_leaves))

    return HomeComposite(home, room_composites)
