from models import db, Decision, Person, Project
from typing import List, Optional
from datetime import datetime

class DbDecisionMemory:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_last_n_decisions(self, n: int = 5) -> Optional[List[Decision]]:
        """
        Retrieve the last `n` decisions made by the user.

        Args:
            n (int): The number of most recent decisions to retrieve.
        
        Returns:
            Optional[List[Decision]]: A list of the last `n` decisions made by the user, or None if no decisions exist.
        """
        decisions = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).order_by(
            Decision.id.desc()
        ).limit(n).all()
        return decisions if decisions else None

    def get_nth_decision(self, n: int) -> Optional[Decision]:
        """
        Retrieve the `n`th decision made by the user.

        Args:
            n (int): The index of the decision to retrieve (1-based index).

        Returns:
            Optional[Decision]: The `n`th decision made by the user, or None if it does not exist.
        """
        decision = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).order_by(
            Decision.id.desc()
        ).offset(n - 1).first()
        return decision if decision else None
    
    def get_decision_by_date(self, date_str: str) -> Optional[List[Decision]]:
        """
        Retrieve decisions made on a specific date.

        Args:
            date_str (str): Date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Decision]]: A list of decisions made on the specified date, or None if no decisions exist.
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        decisions = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).filter(
            Decision.date == date
        ).all()
        return decisions if decisions else None

    def get_descisions_in_date_range(self, start_date_str: str, end_date_str: str) -> Optional[List[Decision]]:
        """
        Retrieve decisions made within a specific date range.

        Args:
            start_date_str (str): Start date in the format "YYYY-MM-DD".
            end_date_str (str): End date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Decision]]: A list of decisions made within the specified date range, or None if no decisions exist.
        """
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        decisions = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).filter(
            Decision.date >= start_date,
            Decision.date <= end_date
        ).all()
        return decisions if decisions else None
    
    def search_decisions_by_keyword(self, keyword: str) -> Optional[List[Decision]]:
        """
        Search for decisions containing a specific keyword in their description.

        Args:
            keyword (str): The keyword to search for in the decision descriptions.
        
        Returns:
            Optional[List[Decision]]: A list of decisions containing the keyword in their description, or None if no decisions match.
        """
        decisions = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).filter(
            (Decision.decision_name.ilike(f"%{keyword}%")) |
            (Decision.decision_text.ilike(f"%{keyword}%"))
        ).all()
        return decisions if decisions else None

    def get_all_decisions(self) -> Optional[List[dict]]:
        """
        Retrieve all decisions made by the user, returning only their name, id, and date.

        Returns:
            Optional[List[dict]]: A list of dictionaries containing the id, name, and date of all decisions made by the user, or None if no decisions exist.
        """
        decisions = db.session.query(
            Decision.id, Decision.decision_name, Decision.date
        ).filter_by(user_id=self.user_id).all()
        
        if not decisions:
            return None
        
        return [{"id": d.id, "name": d.decision_name, "date": d.date} for d in decisions]
    
    def create_decision(self, decision_name: str, 
                        decision_text: str, additional_info: Optional[dict] = None, 
                        date: Optional[datetime] = None
                    ) -> Decision:
        """
        Create a new decision for the user.

        Args:
            decision_name (str): The name of the decision. Should be very clear and concise, between 5 and 15 words.
            decision_text (str): The text of the decision.
            additional_info (Optional[dict]): Additional information about the decision.
            date (Optional[datetime]): The date of the decision. Defaults to the current date and time if not provided.
        
        Returns:
            Decision: The created decision object.
        """
        word_count = len(decision_name.split())
        if word_count < 5 or word_count > 15:
            raise ValueError("decision_name must be between 5 and 15 words.")

        new_decision = Decision(
            user_id=self.user_id,
            decision_name=decision_name,
            decision_text=decision_text,
            additional_info=additional_info,
            date=date or datetime.utcnow()
        )
        db.session.add(new_decision)
        db.session.commit()
        return new_decision
