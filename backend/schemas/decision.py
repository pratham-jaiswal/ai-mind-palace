from models import ma, Decision

class DecisionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Decision
        load_instance = True
