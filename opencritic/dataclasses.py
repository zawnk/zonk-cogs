from dataclasses import dataclass

@dataclass
class Game:
    id: int
    tier: str
    name: str
    averageScore: float
    description: str
    numReviews: int