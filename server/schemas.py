from marshmallow import Schema, fields


class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    # Show the workouts an exercise appears in (with reps/sets/duration).
    # Excluding 'exercise' avoids an endless loop between the schemas.
    workout_exercises = fields.List(
        fields.Nested('WorkoutExerciseSchema', exclude=('exercise',)),
        dump_only=True
    )


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)

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
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)

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
