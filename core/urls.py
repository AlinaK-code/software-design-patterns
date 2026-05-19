from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path(
        "strategy/<str:strategy_name>/",
        views.apply_strategy_view,
        name="apply_strategy",
    ),
    path("devices/", views.devices_view, name="devices"),
    path(
        "devices/<int:device_id>/command/",
        views.device_command_view,
        name="device_command",
    ),
    path(
        "devices/factory/<str:factory_type>/create/",
        views.factory_device_create_view,
        name="factory_device_create",
    ),
    path("scenarios/", views.scenarios_view, name="scenarios"),
    path(
        "scenarios/<int:scenario_id>/run/",
        views.run_scenario_view,
        name="run_scenario",
    ),
    path("events/", views.events_view, name="events"),
    path("patterns/", views.patterns_demo_view, name="patterns_demo"),
]
