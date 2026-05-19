from django.contrib import admin

from .models import (
    Device,
    DeviceCapability,
    EventLog,
    Home,
    Room,
    Scenario,
    ScenarioAction,
    SensorReading,
)


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ("name", "floor")
    show_change_link = True


class DeviceInline(admin.TabularInline):
    model = Device
    extra = 0
    fields = ("name", "device_type", "status", "value", "is_active")
    show_change_link = True


class DeviceCapabilityInline(admin.TabularInline):
    model = DeviceCapability
    extra = 1
    fields = ("action_name", "is_enabled")


class ScenarioActionInline(admin.TabularInline):
    model = ScenarioAction
    extra = 1
    fields = ("order", "device", "command", "value")
    autocomplete_fields = ("device",)
    ordering = ("order",)


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "address", "created_at")
    search_fields = ("name", "address")
    list_filter = ("created_at",)
    readonly_fields = ("created_at",)
    inlines = (RoomInline,)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "home", "floor")
    search_fields = ("name", "home__name")
    list_filter = ("home", "floor")
    autocomplete_fields = ("home",)
    inlines = (DeviceInline,)


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "device_type",
        "status",
        "value",
        "room",
        "power_watts",
        "is_active",
        "updated_at",
    )
    search_fields = ("name", "value", "room__name", "room__home__name")
    list_filter = ("device_type", "status", "is_active", "room__home")
    autocomplete_fields = ("room",)
    readonly_fields = ("created_at", "updated_at")
    inlines = (DeviceCapabilityInline,)


@admin.register(DeviceCapability)
class DeviceCapabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "action_name", "is_enabled")
    search_fields = ("device__name", "action_name")
    list_filter = ("action_name", "is_enabled", "device__device_type")
    autocomplete_fields = ("device",)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "home", "is_active", "created_at")
    search_fields = ("name", "description", "home__name")
    list_filter = ("is_active", "home", "created_at")
    autocomplete_fields = ("home",)
    readonly_fields = ("created_at",)
    inlines = (ScenarioActionInline,)


@admin.register(ScenarioAction)
class ScenarioActionAdmin(admin.ModelAdmin):
    list_display = ("id", "scenario", "device", "command", "value", "order")
    search_fields = (
        "scenario__name",
        "device__name",
        "command",
        "value",
    )
    list_filter = ("command", "scenario__home")
    autocomplete_fields = ("scenario", "device")
    ordering = ("scenario", "order")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("id", "device", "reading_type", "value", "unit", "created_at")
    search_fields = ("device__name", "unit")
    list_filter = ("reading_type", "device__device_type", "created_at")
    autocomplete_fields = ("device",)
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("id", "home", "device", "event_type", "message", "created_at")
    search_fields = ("message", "home__name", "device__name")
    list_filter = ("event_type", "home", "created_at")
    autocomplete_fields = ("home", "device")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
