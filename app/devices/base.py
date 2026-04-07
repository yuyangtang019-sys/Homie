from __future__ import annotations

from abc import ABC, abstractmethod
from app.models import Device


class DeviceAdapter(ABC):
    @abstractmethod
    def execute(self, device: Device, command: str, params: dict) -> Device:
        raise NotImplementedError
