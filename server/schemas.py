from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError

VALID_CATEGORIES = ['strength', 'cardio', 'flexibility', 'balance', 'core']


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='Name must be 1 to 100 characters'),
    )
    category = fields.Str(required=True)
    # truthy/falsy restrict this field to real booleans only
    equipment_needed = fields.Boolean(
        required=True,
        truthy={True},
        falsy={False},
        error_messages={'invalid': 'equipment_needed must be true or false'},
    )

    # Show the workouts an exercise appears in (with reps/sets/duration).
    # Excluding 'exercise' avoids an endless loop between the schemas.
    workout_exercises = fields.List(
        fields.Nested('WorkoutExerciseSchema', exclude=('exercise',)),
        dump_only=True
    )

    @validates('name')
    def validate_name(self, value):
        if not value.strip():
            raise ValidationError('Name cannot be blank')

    @validates('category')
    def validate_category(self, value):
        if value.strip().lower() not in VALID_CATEGORIES:
            raise ValidationError(f'Category must be one of: {", ".join(VALID_CATEGORIES)}')


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1, max=600, error='duration_minutes must be between 1 and 600'),
    )
    notes = fields.Str(
        allow_none=True,
        validate=validate.Length(max=500, error='Notes can be at most 500 characters'),
    )

    # Show the exercises in a workout (with reps/sets/duration).
    # Excluding 'workout' avoids an endless loop between the schemas.
    workout_exercises = fields.List(
        fields.Nested('WorkoutExerciseSchema', exclude=('workout',)),
        dump_only=True
    )


class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(dump_only=True)
    exercise_id = fields.Int(dump_only=True)
    reps = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1, max=1000))
    sets = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1, max=100))
    duration_seconds = fields.Int(allow_none=True, strict=True, validate=validate.Range(min=1, max=86400))

    # Only a few fields of the related objects, to keep the output small
    workout = fields.Nested(
        'WorkoutSchema',
        only=('id', 'date', 'duration_minutes', 'notes'),
        dump_only=True
    )
    exercise = fields.Nested(
        'ExerciseSchema',
        only=('id', 'name', 'category', 'equipment_needed'),
        dump_only=True
    )

    @validates_schema
    def validate_has_measurement(self, data, **kwargs):
        """At least one of reps, sets or duration_seconds must be given."""
        if all(data.get(field) is None for field in ('reps', 'sets', 'duration_seconds')):
            raise ValidationError('Provide at least one of reps, sets, or duration_seconds')