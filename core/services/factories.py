from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import Device, DeviceAction, DeviceCapability, Room


class SmartDeviceFactory(ABC):
    """Abstract Factory — создание устройств и их возможностей."""

    device_type: str = Device.DeviceType.OTHER
    default_power_watts: int = 0
    default_status: str = Device.Status.OFF
    default_value: str = ""
    capability_actions: tuple[str, ...] = ()

    @abstractmethod
    def create_device(self, room: Room, name: str) -> Device:
        pass

    def create_default_capabilities(self, device: Device) -> list[DeviceCapability]:
        capabilities = []
        for action in self.capability_actions:
            capability, _ = DeviceCapability.objects.get_or_create(
                device=device,
                action_name=action,
                defaults={"is_enabled": True},
            )
            capabilities.append(capability)
        return capabilities

    def build(self, room: Room, name: str) -> Device:
        device = self.create_device(room, name)
        self.create_default_capabilities(device)
        return device


class LightingDeviceFactory(SmartDeviceFactory):
    device_type = Device.DeviceType.LIGHT
    default_power_watts = 12
    default_status = Device.Status.OFF
    capability_actions = (
        DeviceAction.TURN_ON,
        DeviceAction.TURN_OFF,
        DeviceAction.TOGGLE,
        DeviceAction.SET_BRIGHTNESS,
        DeviceAction.SET_COLOR,
    )

    def create_device(self, room: Room, name: str) -> Device:
        device, _ = Device.objects.update_or_create(
            room=room,
            name=name,
            defaults={
                "device_type": self.device_type,
                "status": self.default_status,
                "value": self.default_value,
                "power_watts": self.default_power_watts,
                "is_active": True,
            },
        )
        return device


class ClimateDeviceFactory(SmartDeviceFactory):
    device_type = Device.DeviceType.CLIMATE
    default_power_watts = 1200
    default_status = Device.Status.OFF
    default_value = "22"
    capability_actions = (
        DeviceAction.TURN_ON,
        DeviceAction.TURN_OFF,
        DeviceAction.SET_TEMPERATURE,
    )

    def create_device(self, room: Room, name: str) -> Device:
        device, _ = Device.objects.update_or_create(
            room=room,
            name=name,
            defaults={
                "device_type": self.device_type,
                "status": self.default_status,
                "value": self.default_value,
                "power_watts": self.default_power_watts,
                "is_active": True,
            },
        )
        return device


class SecurityDeviceFactory(SmartDeviceFactory):
    device_type = Device.DeviceType.SECURITY
    default_power_watts = 10
    default_status = Device.Status.ON
    capability_actions = (
        DeviceAction.TURN_ON,
        DeviceAction.TURN_OFF,
        DeviceAction.START,
        DeviceAction.STOP,
        DeviceAction.LOCK,
        DeviceAction.UNLOCK,
    )

    def create_device(self, room: Room, name: str) -> Device:
        device, _ = Device.objects.update_or_create(
            room=room,
            name=name,
            defaults={
                "device_type": self.device_type,
                "status": self.default_status,
                "value": self.default_value,
                "power_watts": self.default_power_watts,
                "is_active": True,
            },
        )
        return device
