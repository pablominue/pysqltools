import datetime

import yaml

class Dependency:
    """
    A Dependency represents a dependency between two data sources.
    Attributes:
        source (str): The name of the source data source.
        target (str): The name of the target data source.
        freshness (datetime.datetime): The freshness timestamp of the dependency.
        dependency_type (str): The type of dependency (e.g., "upstream", "downstream").
        description (str): A brief description of the dependency.
    """



class Sensor:
    """
    A Sensor represents a data source with a table and a freshness timestamp.
    Attributes:
        table (str): The name of the table in the database.
        freshness (datetime.datetime): The freshness timestamp of the data source.
    Methods:
        update_freshness(): Updates the freshness timestamp to the current time.
        to_yaml(): Returns a YAML representation of the Sensor.
    
    """
    def __init__(self, table: str) -> None:
        self._freshness: datetime.datetime
        self.table = table

    @staticmethod
    def from_yaml(yaml_file_path: str) -> "Sensor":
        try:
            with open(yaml_file_path, 'r') as file:
                data = yaml.safe_load(file)
            sensor = Sensor(table=data['table'])
            sensor._freshness = datetime.datetime.fromisoformat(data['freshness'])
            return sensor
        except (yaml.YAMLError, KeyError, ValueError) as e:
            raise Exception(f"Invalid YAML content: {e}")

    @property
    def freshness(self) -> datetime.datetime:
        return self._freshness

    @freshness.setter
    def freshness(self, value: datetime.datetime) -> None:
        raise Exception("Freshness can not be manually set")

    def update_freshness(self) -> "Sensor":
        self._freshness = datetime.datetime.now()
        return self

    def to_yaml(self):
        return yaml.dump(
            {
                "table": self.table,
                "freshness": self._freshness.isoformat(),
            }
        )


sensor = Sensor(table="myTable")
sensor.update_freshness()
file = sensor.to_yaml()
print(file)