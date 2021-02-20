from __future__ import annotations

@dataclass
class Game:
    id: int
    tier: str
    name: str
    averageScore: float
    description: str
    numReviews: int