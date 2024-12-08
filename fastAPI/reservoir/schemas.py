from pydantic import BaseModel


class ScoreRequest(BaseModel):
    rainfall: float
    evaporation: float
    mean_storage: float
    flood_cushion: float
    population: int
    siltation: float
    capacity : float
    age : int

