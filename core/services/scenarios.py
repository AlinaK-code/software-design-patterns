from __future__ import annotations

from abc import ABC
from typing import Any

from core.models import EventLog, Scenario
from core.services.device_router import DeviceRouter


class ScenarioTemplate(ABC):
    """Template Method — шаблон выполнения сценария."""

    def __init__(self, scenario: Scenario) -> None:
        self.scenario = scenario
        self._router = DeviceRouter()
        self._results: list[dict[str, Any]] = []

    def run(self) -> dict[str, Any]:
        validation = self.validate()
        if not validation.get("valid", True):
            return validation

        self.before_run()
        self.execute_actions()
        self.after_run()

        return {
            "scenario": self.scenario.name,
            "runner": self.__class__.__name__,
            "actions_executed": len(self._results),
            "results": self._results,
            "message": f"Сценарий «{self.scenario.name}» выполнен",
        }

    def validate(self) -> dict[str, Any]:
        if not self.scenario.is_active:
            return {
                "valid": False,
                "message": f"Сценарий «{self.scenario.name}» неактивен",
            }
        if not self.scenario.actions.exists():
            return {
                "valid": False,
                "message": f"У сценария «{self.scenario.name}» нет действий",
            }
        return {"valid": True}

    def before_run(self) -> None:
        EventLog.objects.create(
            home=self.scenario.home,
            event_type=EventLog.EventType.SCENARIO,
            message=f"Запуск сценария «{self.scenario.name}»",
        )

    def execute_actions(self) -> None:
        for action in self.scenario.actions.select_related("device").all():
            result = self._router.execute_command(
                action.device,
                action.command,
                action.value,
            )
            self._results.append(result)

    def after_run(self) -> None:
        EventLog.objects.create(
            home=self.scenario.home,
            event_type=EventLog.EventType.SCENARIO,
            message=f"Сценарий «{self.scenario.name}» завершён",
        )


class MorningScenarioRunner(ScenarioTemplate):
    pass


class NightScenarioRunner(ScenarioTemplate):
    pass


class EconomyScenarioRunner(ScenarioTemplate):
    pass


class DefaultScenarioRunner(ScenarioTemplate):
    pass


class ScenarioRunnerFactory:
    @staticmethod
    def get_runner(scenario: Scenario) -> ScenarioTemplate:
        name = scenario.name
        if name == "Утро":
            return MorningScenarioRunner(scenario)
        if name == "Ночь":
            return NightScenarioRunner(scenario)
        if "Экономия" in name:
            return EconomyScenarioRunner(scenario)
        return DefaultScenarioRunner(scenario)
