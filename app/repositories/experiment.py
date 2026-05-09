from app.models.models import Experiment
from app.repositories.base import BaseRepository

class ExperimentRepository(BaseRepository[Experiment]):
    def __init__(self):
        super().__init__(Experiment)

experiment_repo = ExperimentRepository()
