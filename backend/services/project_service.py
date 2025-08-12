from .base_service import BaseService
from models.project import Project

class ProjectService(BaseService):
    model = Project
