from .base_service import BaseService
from models.decision import Decision

class DecisionService(BaseService):
    model = Decision
