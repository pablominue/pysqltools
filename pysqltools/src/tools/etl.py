from .sensor import Sensor, Dependency
import typing as t

from abc import abstractmethod

class ETL:
    def __init__(
        self,
        destination_table: str,
        dependencies: t.Optional[t.Iterable[Dependency]] = None,
        
    ) -> None:
        self.table = destination_table
        self.dependencies = dependencies
        
    @abstractmethod
    def extract(self):
        pass
    
    @abstractmethod
    def transform(self):
        pass
    
    @abstractmethod
    def load(self):
        pass
    
class DumpETL(ETL):
    def __init__(
        self,
        destination_table: str,
        dependencies: t.Iterable[Dependency],
        *args,
        **kwargs
    ) -> None:
        super().__init__(destination_table, dependencies)
        
    def extract(self) -> "DumpETL":
        pass
    
    def transform(self) -> "DumpETL":
        pass
    
    def load(self) -> "DumpETL":
        pass