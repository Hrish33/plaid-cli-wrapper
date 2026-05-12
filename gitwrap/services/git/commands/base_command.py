from abc import ABC, abstractmethod


class BaseCommand(ABC):
    def __init__(self, service):
        self.service = service

    @abstractmethod
    def run(self, args) -> dict:
        pass

    def execute(self, args) -> dict:
        return self.run(args)
