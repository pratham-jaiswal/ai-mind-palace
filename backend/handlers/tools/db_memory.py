from models import db, Decision, Person, Project
from typing import List, Optional
from datetime import datetime
from sqlalchemy.sql import func

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

    def get_last_n_decisions_by_date(self, n: int = 5) -> Optional[List[Decision]]:
        """
        Retrieve the last `n` decisions made by the user, ordered by date.

        Args:
            n (int): The number of most recent decisions to retrieve.
        
        Returns:
            Optional[List[Decision]]: A list of the last `n` decisions made by the user, ordered by date, or None if no decisions exist.
        """
        decisions = db.session.query(
            Decision
        ).filter_by(user_id=self.user_id).order_by(
            Decision.date.desc()
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
                        date_str: Optional[str] = None
                    ) -> Decision:
        """
        Create a new decision for the user.

        Args:
            decision_name (str): The name of the decision. Should be very clear and concise, between 5 and 15 words.
            decision_text (str): The text of the decision.
            additional_info (Optional[dict]): Additional information about the decision.
            date_str (Optional[str]): The date of the decision in "YYYY-MM-DD" format. Defaults to the current date if not provided.
        
        Returns:
            Decision: The created decision object.
        """
        word_count = len(decision_name.split())
        if word_count < 5 or word_count > 15:
            raise ValueError("decision_name must be between 5 and 15 words.")

        date = datetime.utcnow()
        if date_str and isinstance(date_str, str):
            date = datetime.strptime(date_str, "%Y-%m-%d")

        new_decision = Decision(
            user_id=self.user_id,
            decision_name=decision_name,
            decision_text=decision_text,
            additional_info=additional_info,
            date=date
        )
        db.session.add(new_decision)
        db.session.commit()
        return new_decision

class DbPersonMemory:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_last_n_people(self, n: int = 5) -> Optional[List[Person]]:
        """
        Retrieve the last `n` people created/added by the user.

        Args:
            n (int): The number of most recent people to retrieve.
        
        Returns:
            Optional[List[Person]]: A list of the last `n` people created/added by the user, or None if no people exist.
        """
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).order_by(
            Person.id.desc()
        ).limit(n).all()
        return people if people else None
    
    def get_last_n_mentioned_people(self, n: int = 5) -> Optional[List[Person]]:
        """
        Retrieve the last `n` people mentioned by the user.

        Args:
            n (int): The number of most recent mentions to retrieve.
        
        Returns:
            Optional[List[Person]]: A list of the last `n` people mentioned by the user, or None if no mentions exist.
        """
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).order_by(
            Person.last_mentioned.desc()
        ).limit(n).all()
        return people if people else None

    def get_person_by_relationship(self, relationship: str) -> Optional[List[Person]]:
        """
        Retrieve people by their relationship to the user.

        Args:
            relationship (str): The relationship to filter by.
        
        Returns:
            Optional[List[Person]]: A list of people with the specified relationship, or None if no people exist.
        """
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).filter(
            func.coalesce(Person.additional_info["relationship"].astext, "stranger") == relationship
        ).all()
        return people if people else None
    
    def get_person_by_name(self, name: str) -> Optional[List[Person]]:
        """
        Retrieve people by their name.

        Args:
            name (str): The name to filter by.
        
        Returns:
            Optional[List[Person]]: A list of people with the specified name, or None if no people exist.
        """
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).filter(
            Person.name.ilike(f"%{name}%")
        ).all()
        return people if people else None
    
    def get_person_by_description(self, description: str) -> Optional[List[Person]]:
        """
        Retrieve people by their description.

        Args:
            description (str): The description to filter by.
        
        Returns:
            Optional[List[Person]]: A list of people with the specified description, or None if no people exist.
        """
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).filter(
            Person.notes.ilike(f"%{description}%")
        ).all()
        return people if people else None
    
    def get_person_by_date(self, date_str: str) -> Optional[List[Person]]:
        """
        Retrieve people mentioned on a specific date.

        Args:
            date_str (str): Date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Person]]: A list of people mentioned on the specified date, or None if no mentions exist.
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).filter(
            Person.last_mentioned == date
        ).all()
        return people if people else None
    
    def get_people_in_date_range(self, start_date_str: str, end_date_str: str) -> Optional[List[Person]]:
        """
        Retrieve people mentioned within a specific date range.

        Args:
            start_date_str (str): Start date in the format "YYYY-MM-DD".
            end_date_str (str): End date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Person]]: A list of people mentioned within the specified date range, or None if no mentions exist.
        """
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        people = db.session.query(
            Person
        ).filter_by(user_id=self.user_id).filter(
            Person.last_mentioned >= start_date,
            Person.last_mentioned <= end_date
        ).all()
        return people if people else None
    
    def get_all_people(self) -> Optional[List[dict]]:
        """
        Retrieve all people created/added by the user, returning only their id, name, and last_mentioned date.

        Returns:
            Optional[List[dict]]: A list of dictionaries containing the id, name, and last_mentioned date of all people created/added by the user, or None if no people exist.
        """
        people = db.session.query(
            Person.id, Person.name, Person.last_mentioned
        ).filter_by(user_id=self.user_id).all()
        
        if not people:
            return None
        
        return [{
            "id": p.id, 
            "name": p.name, 
            "last_mentioned": p.last_mentioned, 
            "relationship": p.additional_info.get("relationship", "stranger")
        } for p in people]

    def create_person(self, name: str,
                      notes: Optional[List[str]] = None, 
                      additional_info: Optional[dict] = None, 
                      last_mentioned_str: Optional[str] = None) -> Person:
        """
        Create a new person for the user.

        Args:
            name (str): The name of the person.
            notes (Optional[List[str]]): Notes about the person.
            additional_info (Optional[dict]): Additional information about the person.
            last_mentioned_str (Optional[str]): The date when the person was last mentioned in "YYYY-MM-DD" format. Defaults to the current date if not provided.
        
        Returns:
            Person: The created person object.
        """
        last_mentioned = datetime.utcnow()
        if last_mentioned_str and isinstance(last_mentioned_str, str):
            last_mentioned = datetime.strptime(last_mentioned_str, "%Y-%m-%d")

        new_person = Person(
            user_id=self.user_id,
            name=name,
            notes=notes or [],
            additional_info=additional_info or {},
            last_mentioned=last_mentioned
        )
        db.session.add(new_person)
        db.session.commit()
        return new_person
    
    def update_person(self, person_id: int,
                      name: Optional[str] = None,
                      notes: Optional[List[str]] = None,
                      additional_info: Optional[dict] = None) -> Person:
        """
        Update an existing person for the user.
        Args:
            person_id (int): The ID of the person to update.
            name (Optional[str]): The new name of the person.
            notes (Optional[List[str]]): The new notes about the person.
            additional_info (Optional[dict]): Additional information about the person.

        Returns:
            Person: The updated person object.
        """

        person = db.session.query(Person).filter_by(id=person_id, user_id=self.user_id).first()
        if not person:
            raise ValueError("Person not found or does not belong to the user.")
        if name:
            person.name = name
        if notes is not None:
            person.notes = notes
        if additional_info is not None:
            person.additional_info = additional_info
        person.last_mentioned = datetime.utcnow()
        db.session.commit()

    
        return person
    
    def delete_person(self, person_id: int) -> bool:
        """
        Delete a person for the user.

        Args:
            person_id (int): The ID of the person to delete.
        
        Returns:
            bool: True if the person was deleted successfully, False otherwise.
        """
        person = db.session.query(Person).filter_by(id=person_id, user_id=self.user_id).first()
        if not person:
            return False
        
        db.session.delete(person)
        db.session.commit()
        return True

class DbProjectMemory:
    def __init__(self, user_id):
        self.user_id = user_id

    def get_last_n_projects(self, n: int = 5) -> Optional[List[Project]]:
        """
        Retrieve the last `n` projects created by the user.

        Args:
            n (int): The number of most recent projects to retrieve.
        
        Returns:
            Optional[List[Project]]: A list of the last `n` projects created by the user, or None if no projects exist.
        """
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).order_by(
            Project.id.desc()
        ).limit(n).all()
        return projects if projects else None
    
    def get_last_n_projects_by_date(self, n: int = 5) -> Optional[List[Project]]:
        """
        Retrieve the last `n` projects created by the user, ordered by last updated date.

        Args:
            n (int): The number of most recent projects to retrieve.
        
        Returns:
            Optional[List[Project]]: A list of the last `n` projects created by the user, ordered by last updated date, or None if no projects exist.
        """
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).order_by(
            Project.last_updated.desc()
        ).limit(n).all()
        return projects if projects else None

    def get_project_by_status(self, status: str) -> Optional[List[Project]]:
        """
        Retrieve projects by their status.

        Args:
            status (str): The status to filter by.
        
        Returns:
            Optional[List[Project]]: A list of projects with the specified status, or None if no projects exist.
        """
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).filter(
            Project.status == status
        ).all()
        return projects if projects else None
    
    def get_project_by_title(self, title: str) -> Optional[List[Project]]:
        """
        Retrieve projects by their title.

        Args:
            title (str): The title to filter by.
        
        Returns:
            Optional[List[Project]]: A list of projects with the specified title, or None if no projects exist.
        """
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).filter(
            Project.title.ilike(f"%{title}%")
        ).all()
        return projects if projects else None
    
    def get_project_by_keyword(self, keyword: str) -> Optional[List[Project]]:
        """
        Search for projects containing a specific keyword in their title or description.

        Args:
            keyword (str): The keyword to search for in the project title or description.
        
        Returns:
            Optional[List[Project]]: A list of projects containing the keyword in their title or description, or None if no projects match.
        """
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).filter(
            (Project.title.ilike(f"%{keyword}%")) |
            (Project.description.ilike(f"%{keyword}%"))
        ).all()
        return projects if projects else None
    
    def get_project_by_date(self, date_str: str) -> Optional[List[Project]]:
        """
        Retrieve projects last updated on a specific date.

        Args:
            date_str (str): Date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Project]]: A list of projects last updated on the specified date, or None if no projects exist.
        """
        date = datetime.strptime(date_str, "%Y-%m-%d")
        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).filter(
            Project.last_updated == date
        ).all()
        return projects if projects else None
    
    def get_projects_in_date_range(self, start_date_str: str, end_date_str: str) -> Optional[List[Project]]:
        """
        Retrieve projects last updated within a specific date range.

        Args:
            start_date_str (str): Start date in the format "YYYY-MM-DD".
            end_date_str (str): End date in the format "YYYY-MM-DD".
        
        Returns:
            Optional[List[Project]]: A list of projects last updated within the specified date range, or None if no projects exist.
        """
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        projects = db.session.query(
            Project
        ).filter_by(user_id=self.user_id).filter(
            Project.last_updated >= start_date,
            Project.last_updated <= end_date
        ).all()
        return projects if projects else None
    
    def get_all_projects(self) -> Optional[List[dict]]:
        """
        Retrieve all projects created by the user, returning only their id, title, status, and last updated date.

        Returns:
            Optional[List[dict]]: A list of dictionaries containing the id, title, status, and last updated date of all projects created by the user, or None if no projects exist.
        """
        projects = db.session.query(
            Project.id, Project.title, Project.status, Project.last_updated
        ).filter_by(user_id=self.user_id).all()
        
        if not projects:
            return None
        
        return [{
            "id": p.id, 
            "title": p.title, 
            "status": p.status, 
            "last_updated": p.last_updated.isoformat()
        } for p in projects]
    
    def create_project(self, title: str,
                       description: Optional[str] = None, 
                       additional_info: Optional[dict] = None, 
                       status: str = 'idea', 
                       last_updated_str: Optional[str] = None) -> Project:
        """
        Create a new project for the user.

        Args:
            title (str): The title of the project.
            description (Optional[str]): A description of the project.
            additional_info (Optional[dict]): Additional information about the project.
            status (str): The status of the project. Defaults to 'idea'.
            last_updated_str (Optional[str]): The date when the project was last updated in "YYYY-MM-DD" format. Defaults to the current date if not provided.
        
        Returns:
            Project: The created project object.
        """
        last_updated = datetime.utcnow()
        if last_updated_str and isinstance(last_updated_str, str):
            last_updated = datetime.strptime(last_updated_str, "%Y-%m-%d")

        new_project = Project(
            user_id=self.user_id,
            title=title,
            description=description,
            additional_info=additional_info or {},
            status=status,
            last_updated=last_updated
        )
        db.session.add(new_project)
        db.session.commit()
        return new_project
    
    def update_project(self, project_id: int,
                       title: Optional[str] = None,
                       description: Optional[str] = None,
                       additional_info: Optional[dict] = None,
                       status: Optional[str] = None) -> Project:
        """
        Update an existing project for the user.

        Args:
            project_id (int): The ID of the project to update.
            title (Optional[str]): The new title of the project.
            description (Optional[str]): The new description of the project.
            additional_info (Optional[dict]): Additional information about the project.
            status (Optional[str]): The new status of the project.
        
        Returns:
            Project: The updated project object.
        """
        project = db.session.query(Project).filter_by(id=project_id, user_id=self.user_id).first()
        if not project:
            raise ValueError("Project not found or does not belong to the user.")

        if title:
            project.title = title
        if description:
            project.description = description
        if additional_info is not None:
            project.additional_info = additional_info
        if status:
            project.status = status
        project.last_updated = datetime.utcnow()

        db.session.commit()
        return project
    
    def delete_project(self, project_id: int) -> bool:
        """
        Delete a project for the user.

        Args:
            project_id (int): The ID of the project to delete.
        
        Returns:
            bool: True if the project was deleted successfully, False otherwise.
        """
        project = db.session.query(Project).filter_by(id=project_id, user_id=self.user_id).first()
        if not project:
            return False
        
        db.session.delete(project)
        db.session.commit()
        return True
