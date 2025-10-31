from abc import ABC, abstractmethod

class BaseResource(ABC):
    @abstractmethod
    def get_title(self):
        pass
