from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExternalWeatherService:
    """Внешний API с несовместимым форматом данных."""

    def get_weather_data(self) -> dict[str, Any]:
        return {
            "temp_c": 18,
            "humidity_percent": 55,
            "condition": "cloudy",
        }


class HomeEnvironmentProvider(ABC):
    """Целевой интерфейс для данных окружения дома."""

    @abstractmethod
    def get_environment(self) -> dict[str, Any]:
        pass


class WeatherServiceAdapter(HomeEnvironmentProvider):
    """Adapter — преобразует внешний API во внутренний формат."""

    def __init__(self, weather_service: ExternalWeatherService) -> None:
        self._weather_service = weather_service

    def get_environment(self) -> dict[str, Any]:
        data = self._weather_service.get_weather_data()
        return {
            "temperature": data["temp_c"],
            "humidity": data["humidity_percent"],
            "source": "external_weather",
        }
