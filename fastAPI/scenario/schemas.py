from pydantic import BaseModel


class ScenarioRequest(BaseModel):
    rainfall: float
    evaporation: float
    inflow: float
    outflow: float
    population: int
    district: int