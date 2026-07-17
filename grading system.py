# Student Grading System
"""
=====================================================================
 STUDENT GRADING SYSTEM
 Course: Object Oriented Programming (BCSNT 6063)
 Theme : Management Systems -> Student Grading System
---------------------------------------------------------------------
 Demonstrates:
   - Abstract Base Class (ABC) + @abstractmethod
   - Inheritance
   - Encapsulation (private attributes + property getters/setters)
   - Polymorphism (overridden abstract methods)
   - Custom Exception Handling
   - JSON based Data Persistence
   - Interactive Menu Driven Console Interface
=====================================================================
"""
 
import json
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
 
 
# =====================================================================
# CUSTOM EXCEPTION
# =====================================================================
class InvalidMarkError(Exception):
    """Custom exception raised when a subject mark is out of the valid range (0-100)."""
 
    def __init__(self, mark: float, message: str = "Marks must be between 0 and 100") -> None:
        self.mark = mark
        self.message = f"{message}. Received: {mark}"
        super().__init__(self.message)
 
 
# =====================================================================
# ABSTRACT BASE CLASS
# =====================================================================
class Person(ABC):
    """Abstract base class representing a generic person."""
 
    def __init__(self, name: str, person_id: str) -> None:
        self._name = name
        self._person_id = person_id
 
    @abstractmethod
    def get_details(self) -> str:
        """Return a formatted string describing this person. Must be overridden."""
        raise NotImplementedError
 
    @abstractmethod
    def calculate_performance(self) -> float:
        """Return a numeric performance score for this person. Must be overridden."""
        raise NotImplementedError
 
 
# =====================================================================
# STUDENT CLASS (Inheritance + Encapsulation + Polymorphism)
# =====================================================================
class Student(Person):
    """Represents a student, storing subject marks and computing grades/CGPA."""
 
    # Grade boundaries -> (letter grade, grade point on a 4.0 scale)
    GRADE_TABLE = [
        (90, "A+", 4.0),
        (80, "A", 3.7),
        (70, "B+", 3.3),
        (60, "B", 3.0),
        (50, "C", 2.5),
        (40, "D", 2.0),
        (0, "F", 0.0),
    ]
 
    def __init__(self, student_id: str, name: str, subjects: Optional[Dict[str, float]] = None) -> None:
        super().__init__(name, student_id)
        self.__student_id: str = student_id           # private attribute
        self.__name: str = name                        # private attribute
        self.__subjects: Dict[str, float] = {}          # private attribute {subject: marks}
        self.__cgpa: float = 0.0                        # private attribute
 
        # Load any pre-existing subjects (e.g. when restoring from JSON)
        if subjects:
            for subject, marks in subjects.items():
                self.add_subject(subject, marks)
 
    # ------------------------------------------------------------------
    # PROPERTIES (Encapsulation: controlled access to private attributes)
    # ------------------------------------------------------------------
    @property
    def student_id(self) -> str:
        return self.__student_id
 
    @property
    def name(self) -> str:
        return self.__name
 
    @name.setter
    def name(self, new_name: str) -> None:
        if not new_name or not new_name.strip():
            raise ValueError("Name cannot be empty.")
        self.__name = new_name.strip()
 
    @property
    def subjects(self) -> Dict[str, float]:
        # Return a copy so callers cannot mutate the private dict directly
        return dict(self.__subjects)
 
    @property
    def cgpa(self) -> float:
        return self.__cgpa
 
    # ------------------------------------------------------------------
    # SUBJECT / MARKS MANAGEMENT
    # ------------------------------------------------------------------
    def add_subject(self, subject_name: str, marks: float) -> None:
        """Add or update a subject's marks. Raises InvalidMarkError if out of range."""
        if not isinstance(marks, (int, float)):
            raise InvalidMarkError(marks, "Marks must be numeric")
        if marks < 0 or marks > 100:
            raise InvalidMarkError(marks)
        self.__subjects[subject_name.strip()] = float(marks)
        self.calculate_performance()  # keep CGPA in sync whenever marks change
 
    def remove_subject(self, subject_name: str) -> bool:
        """Remove a subject if it exists; return True if removed."""
        if subject_name in self.__subjects:
            del self.__subjects[subject_name]
            self.calculate_performance()
            return True
        return False
 
    # ------------------------------------------------------------------
    # GRADE / PERFORMANCE CALCULATIONS
    # ------------------------------------------------------------------
    def calculate_total(self) -> float:
        """Sum of all subject marks."""
        return sum(self.__subjects.values())
 
    def calculate_percentage(self) -> float:
        """Overall percentage across all subjects (0 if no subjects)."""
        if not self.__subjects:
            return 0.0
        return self.calculate_total() / (len(self.__subjects) * 100) * 100
 
    @classmethod
    def _grade_for_marks(cls, marks: float) -> tuple:
        """Return (letter, grade_point) for a given mark value using GRADE_TABLE."""
        for lower_bound, letter, point in cls.GRADE_TABLE:
            if marks >= lower_bound:
                return letter, point
        return "F", 0.0
 
    def get_subject_grade(self, subject_name: str) -> str:
        """Letter grade for a single subject."""
        marks = self.__subjects.get(subject_name)
        if marks is None:
            return "N/A"
        letter, _ = self._grade_for_marks(marks)
        return letter
 
    def get_overall_grade(self) -> str:
        """Letter grade based on overall percentage."""
        letter, _ = self._grade_for_marks(self.calculate_percentage())
        return letter
 
    def calculate_performance(self) -> float:
        """
        Overridden abstract method (Polymorphism).
        Calculates and stores CGPA (average grade point across subjects, 4.0 scale).
        Returns the overall percentage as the numeric 'performance' value.
        """
        if not self.__subjects:
            self.__cgpa = 0.0
            return 0.0
 
        total_points = 0.0
        for marks in self.__subjects.values():
            _, point = self._grade_for_marks(marks)
            total_points += point
 
        self.__cgpa = round(total_points / len(self.__subjects), 2)
        return self.calculate_percentage()
 
    # ------------------------------------------------------------------
    # POLYMORPHIC OVERRIDE OF get_details()
    # ------------------------------------------------------------------
    def get_details(self) -> str:
        """Overridden abstract method: returns a formatted student summary."""
        self.calculate_performance()  # ensure CGPA is up-to-date
        lines: List[str] = []
        lines.append(f"Student ID   : {self.__student_id}")
        lines.append(f"Name         : {self.__name}")
        lines.append("Subjects     :")
        if self.__subjects:
            for subject, marks in self.__subjects.items():
                letter = self.get_subject_grade(subject)
                lines.append(f"    - {subject:<15}: {marks:>6.2f}  (Grade: {letter})")
        else:
            lines.append("    (No subjects recorded yet)")
        lines.append(f"Total        : {self.calculate_total():.2f}")
        lines.append(f"Percentage   : {self.calculate_percentage():.2f}%")
        lines.append(f"Overall Grade: {self.get_overall_grade()}")
        lines.append(f"CGPA (4.0)   : {self.__cgpa:.2f}")
        return "\n".join(lines)
 
    # ------------------------------------------------------------------
    # SERIALIZATION (for JSON persistence)
    # ------------------------------------------------------------------
    def to_dict(self) -> dict:
        """Convert the student object into a JSON-serializable dictionary."""
        return {
            "student_id": self.__student_id,
            "name": self.__name,
            "subjects": self.__subjects,
        }
 
    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Reconstruct a Student object from a dictionary (loaded from JSON)."""
        return cls(
            student_id=data["student_id"],
            name=data["name"],
            subjects=data.get("subjects", {}),
        )
 
    def __str__(self) -> str:
        return f"Student(ID={self.__student_id}, Name={self.__name}, CGPA={self.__cgpa:.2f})"
 
 
# =====================================================================
# STUDENT GRADING SYSTEM (Manager class + Menu Console Interface)
# =====================================================================
class StudentGradingSystem:
    """Manages a collection of Student objects with JSON persistence and a console menu."""
 
    def __init__(self, filename: str = "students_data.json") -> None:
        self.filename = filename
        self.students: Dict[str, Student] = {}
        self.load_data()  # automatic loading on startup
 
    # ------------------------------------------------------------------
    # DATA PERSISTENCE
    # ------------------------------------------------------------------
    def load_data(self) -> None:
        """Load student records from the JSON file if it exists."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, "r", encoding="utf-8") as f:
                    raw_data = json.load(f)
            else:
                raw_data = []
        except FileNotFoundError:
            print(f"[Info] No existing data file found. A new one will be created as '{self.filename}'.")
            raw_data = []
        except json.JSONDecodeError:
            print(f"[Warning] '{self.filename}' is corrupted or unreadable. Starting with an empty database.")
            raw_data = []
        except OSError as e:
            print(f"[Error] Could not read data file: {e}")
            raw_data = []
        else:
            print(f"[Info] Loaded {len(raw_data)} student record(s) from '{self.filename}'.")
        finally:
            self.students = {}
            for record in raw_data:
                try:
                    student = Student.from_dict(record)
                    self.students[student.student_id] = student
                except (KeyError, InvalidMarkError) as e:
                    print(f"[Warning] Skipped a corrupted record: {e}")
 
    def save_data(self) -> None:
        """Persist all student records to the JSON file."""
        try:
            data_to_save = [student.to_dict() for student in self.students.values()]
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4)
        except OSError as e:
            print(f"[Error] Could not save data to file: {e}")
        else:
            print(f"[Info] Data successfully saved to '{self.filename}'.")
        finally:
            pass  # nothing else to clean up
 
    # ------------------------------------------------------------------
    # CORE OPERATIONS
    # ------------------------------------------------------------------
    def add_student(self) -> None:
        """Interactive: add a new student with one or more subjects."""
        student_id = input("Enter new Student ID: ").strip()
 
        if not student_id:
            print("[Error] Student ID cannot be empty.")
            return
 
        if student_id in self.students:
            print(f"[Error] A student with ID '{student_id}' already exists.")
            return
 
        name = input("Enter Student Name: ").strip()
        if not name:
            print("[Error] Name cannot be empty.")
            return
 
        student = Student(student_id, name)
 
        # Enter subjects in a loop with full validation
        try:
            num_subjects = int(input("How many subjects to enter? "))
            if num_subjects <= 0:
                raise ValueError("Number of subjects must be a positive integer.")
        except ValueError as e:
            print(f"[Error] Invalid number of subjects: {e}")
            return
 
        for i in range(1, num_subjects + 1):
            while True:
                try:
                    subject_name = input(f"  Subject {i} name: ").strip()
                    if not subject_name:
                        raise ValueError("Subject name cannot be empty.")
                    marks_input = input(f"  Marks for {subject_name} (0-100): ").strip()
                    marks = float(marks_input)
                    student.add_subject(subject_name, marks)
                except ValueError as e:
                    print(f"  [Error] Invalid input: {e}. Please try again.")
                    continue
                except InvalidMarkError as e:
                    print(f"  [Error] {e}. Please try again.")
                    continue
                else:
                    break
                finally:
                    pass
 
        self.students[student_id] = student
        self.save_data()  # save on update
        print(f"[Success] Student '{name}' (ID: {student_id}) added successfully.\n")
 
    def view_all_students(self) -> None:
        """Display a summary table of all students."""
        if not self.students:
            print("[Info] No student records found.")
            return
 
        print("\n" + "=" * 70)
        print(f"{'ID':<10}{'Name':<20}{'Total':<10}{'Percent':<10}{'Grade':<8}{'CGPA':<6}")
        print("=" * 70)
        for student in self.students.values():
            student.calculate_performance()
            print(
                f"{student.student_id:<10}{student.name:<20}"
                f"{student.calculate_total():<10.2f}{student.calculate_percentage():<10.2f}"
                f"{student.get_overall_grade():<8}{student.cgpa:<6.2f}"
            )
        print("=" * 70 + "\n")
 
    def search_student(self) -> Optional[Student]:
        """Search and display a student's full details by ID."""
        student_id = input("Enter Student ID to search: ").strip()
        student = self.students.get(student_id)
        if student is None:
            print(f"[Error] No student found with ID '{student_id}'.\n")
            return None
        print("\n" + "-" * 50)
        print(student.get_details())
        print("-" * 50 + "\n")
        return student
 
    def update_student_marks(self) -> None:
        """Update or add subject marks for an existing student."""
        student_id = input("Enter Student ID to update: ").strip()
        student = self.students.get(student_id)
        if student is None:
            print(f"[Error] No student found with ID '{student_id}'.\n")
            return
 
        while True:
            try:
                subject_name = input("  Subject name to add/update: ").strip()
                if not subject_name:
                    raise ValueError("Subject name cannot be empty.")

                marks = float(input(f"  New marks for {subject_name} (0-100): ").strip())
                student.add_subject(subject_name, marks)
            except ValueError as e:
                print(f"  [Error] Invalid input: {e}")
                continue
            except InvalidMarkError as e:
                print(f"  [Error] {e}")
                continue
            else:
                print(f"[Success] '{subject_name}' updated for student '{student.name}'.")
                again = input("Update another subject for this student? (y/n): ").strip().lower()
                if again != "y":
                    break

        self.save_data()
 
    def delete_student(self) -> None:
        """Delete a student record by ID."""
        student_id = input("Enter Student ID to delete: ").strip()
        if student_id in self.students:
            confirm = input(f"Are you sure you want to delete '{self.students[student_id].name}'? (y/n): ").strip().lower()
            if confirm == "y":
                del self.students[student_id]
                self.save_data()
                print("[Success] Student record deleted.\n")
            else:
                print("[Info] Deletion cancelled.\n")
        else:
            print(f"[Error] No student found with ID '{student_id}'.\n")
 
    def generate_report(self) -> None:
        """Generate a full performance report for every student, ranked by CGPA."""
        if not self.students:
            print("[Info] No student records found.")
            return
 
        ranked = sorted(self.students.values(), key=lambda s: s.cgpa, reverse=True)
 
        print("\n" + "#" * 70)
        print("PERFORMANCE REPORT (Ranked by CGPA)")
        print("#" * 70)
        for rank, student in enumerate(ranked, start=1):
            print(f"\nRank #{rank}")
            print("-" * 50)
            print(student.get_details())
        print("#" * 70 + "\n")
 
    # ------------------------------------------------------------------
    # MENU / ENTRY POINT
    # ------------------------------------------------------------------
    def display_menu(self) -> None:
        print("\n" + "=" * 40)
        print("   STUDENT GRADING SYSTEM - MAIN MENU")
        print("=" * 40)
        print("1. Add New Student")
        print("2. View All Students")
        print("3. Search Student by ID")
        print("4. Update Student Marks")
        print("5. Delete Student")
        print("6. Generate Performance Report")
        print("7. Save & Exit")
        print("=" * 40)
 
    def run(self) -> None:
        """Main interactive loop for the menu-driven console interface."""
        while True:
            self.display_menu()
            try:
                choice = input("Enter your choice (1-7): ").strip()
                if choice not in {"1", "2", "3", "4", "5", "6", "7"}:
                    raise ValueError("Choice must be a number between 1 and 7.")
            except ValueError as e:
                print(f"[Error] {e}")
                continue
            else:
                if choice == "1":
                    self.add_student()
                elif choice == "2":
                    self.view_all_students()
                elif choice == "3":
                    self.search_student()
                elif choice == "4":
                    self.update_student_marks()
                elif choice == "5":
                    self.delete_student()
                elif choice == "6":
                    self.generate_report()
                elif choice == "7":
                    self.save_data()
                    print("Goodbye! All data has been saved.")
                    break
            finally:
                
                pass
 
 

# PROGRAM ENTRY POINT

if __name__ == "__main__":
    system = StudentGradingSystem(filename="students_data.json")
    try:
        system.run()
    except KeyboardInterrupt:
        print("\n[Info] Program interrupted by user. Saving data before exit...")
        system.save_data()
    except Exception as unexpected_error:  # final safety net for unforeseen errors
        print(f"[Fatal Error] An unexpected error occurred: {unexpected_error}")
        system.save_data()
 