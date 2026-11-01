from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates

db = SQLAlchemy()

VALID_CATEGORIES = ['strength', 'cardio', 'flexibility', 'balance', 'core']


def validate_positive_int(value, field_name, allow_none=False):
    """Return value if it is a positive integer, otherwise raise ValueError."""
    if value is None and allow_none:
        return value
    # bool is a subclass of int in Python, so reject it explicitly
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f'{field_name} must be a positive integer')
    return value


class Exercise(db.Model):
    __tablename__ = 'exercises'

    # Table constraints (enforced by the database)
    __table_args__ = (
        db.CheckConstraint('length(name) > 0', name='ck_exercise_name_not_empty'),
        db.CheckConstraint('length(category) > 0', name='ck_exercise_category_not_empty'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    category = db.Column(db.String, nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    # An Exercise has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='exercise',
        cascade='all, delete-orphan'
    )

    # An Exercise has many Workouts through WorkoutExercises
    workouts = association_proxy('workout_exercises', 'workout')

    # Model validations (enforced when the attribute is set)
    @validates('name')
    def validate_name(self, key, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError('Exercise name must be a non-empty string')
        return value.strip()

    @validates('category')
    def validate_category(self, key, value):
        if not isinstance(value, str) or value.strip().lower() not in VALID_CATEGORIES:
            raise ValueError(f'Category must be one of: {", ".join(VALID_CATEGORIES)}')
        return value.strip().lower()

    @validates('equipment_needed')
    def validate_equipment_needed(self, key, value):
        if not isinstance(value, bool):
            raise ValueError('equipment_needed must be true or false')
        return value

    def __repr__(self):
        return f'<Exercise {self.id}: {self.name}>'


class Workout(db.Model):
    __tablename__ = 'workouts'

    # Table constraints
    __table_args__ = (
        db.CheckConstraint('duration_minutes > 0', name='ck_workout_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)

    # A Workout has many WorkoutExercises
    workout_exercises = db.relationship(
        'WorkoutExercise',
        back_populates='workout',
        cascade='all, delete-orphan'
    )

    # A Workout has many Exercises through WorkoutExercises
    exercises = association_proxy('workout_exercises', 'exercise')

    # Model validations
    @validates('date')
    def validate_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError('date must be a valid date')
        return value

    @validates('duration_minutes')
    def validate_duration_minutes(self, key, value):
        return validate_positive_int(value, 'duration_minutes')

    def __repr__(self):
        return f'<Workout {self.id}: {self.date}>'


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    # Table constraints (NULL values pass a CHECK, so these fields stay optional)
    __table_args__ = (
        db.CheckConstraint('reps > 0', name='ck_we_reps_positive'),
        db.CheckConstraint('sets > 0', name='ck_we_sets_positive'),
        db.CheckConstraint('duration_seconds > 0', name='ck_we_duration_positive'),
    )

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workouts.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)
    reps = db.Column(db.Integer)
    sets = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)

    # A WorkoutExercise belongs to a Workout
    workout = db.relationship('Workout', back_populates='workout_exercises')

    # A WorkoutExercise belongs to an Exercise
    exercise = db.relationship('Exercise', back_populates='workout_exercises')

    # Model validations
    @validates('reps', 'sets', 'duration_seconds')
    def validate_positive_fields(self, key, value):
        return validate_positive_int(value, key, allow_none=True)

    def __repr__(self):
        return f'<WorkoutExercise {self.id}: workout {self.workout_id}, exercise {self.exercise_id}>'
        