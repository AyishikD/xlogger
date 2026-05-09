from app.models.models import Relationship
from app.repositories.base import BaseRepository

class RelationshipRepository(BaseRepository[Relationship]):
    def __init__(self):
        super().__init__(Relationship)

relationship_repo = RelationshipRepository()
