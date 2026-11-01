from flask import Flask, make_response, request
from flask_migrate import Migrate
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import *
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True, exclude=('workout_exercises',))
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True, exclude=('workout_exercises',))
workout_exercise_schema = WorkoutExerciseSchema()


def error_response(errors, status):
    """Return a consistent JSON error body."""
    return make_response({'errors': errors}, status)


def save_new(obj):
    """Add obj to the database. Returns an error response, or None on success."""
    try:
        db.session.add(obj)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        # e.g. a duplicate exercise name or a failed CHECK constraint
        return error_response(f'Database constraint failed: {e.orig}', 409)
    return None


# ---------- Workouts ----------

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)


@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response(f'Workout {id} not found', 404)
    return make_response(workout_schema.dump(workout), 200)


@app.route('/workouts', methods=['POST'])
def create_workout():
    json_data = request.get_json(silent=True) or {}
    try:
        data = workout_schema.load(json_data)   # schema validations
        workout = Workout(**data)               # model validations
    except ValidationError as err:
        return error_response(err.messages, 422)
    except ValueError as err:
        return error_response(str(err), 422)

    failure = save_new(workout)
    if failure:
        return failure
    return make_response(workout_schema.dump(workout), 201)


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = db.session.get(Workout, id)
    if not workout:
        return error_response(f'Workout {id} not found', 404)

    # The cascade on Workout.workout_exercises deletes the join rows too
    db.session.delete(workout)
    db.session.commit()
    return make_response('', 204)


# ---------- Exercises ----------

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)


@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response(f'Exercise {id} not found', 404)
    return make_response(exercise_schema.dump(exercise), 200)


@app.route('/exercises', methods=['POST'])
def create_exercise():
    json_data = request.get_json(silent=True) or {}
    try:
        data = exercise_schema.load(json_data)
        exercise = Exercise(**data)
    except ValidationError as err:
        return error_response(err.messages, 422)
    except ValueError as err:
        return error_response(str(err), 422)

    failure = save_new(exercise)
    if failure:
        return failure
    return make_response(exercise_schema.dump(exercise), 201)


@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = db.session.get(Exercise, id)
    if not exercise:
        return error_response(f'Exercise {id} not found', 404)

    # The cascade on Exercise.workout_exercises deletes the join rows too
    db.session.delete(exercise)
    db.session.commit()
    return make_response('', 204)


# ---------- Add an exercise to a workout ----------

@app.route(
    '/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises',
    methods=['POST']
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return error_response(f'Workout {workout_id} not found', 404)

    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return error_response(f'Exercise {exercise_id} not found', 404)

    json_data = request.get_json(silent=True) or {}
    try:
        data = workout_exercise_schema.load(json_data)
        workout_exercise = WorkoutExercise(workout=workout, exercise=exercise, **data)
    except ValidationError as err:
        return error_response(err.messages, 422)
    except ValueError as err:
        return error_response(str(err), 422)

    failure = save_new(workout_exercise)
    if failure:
        return failure
    return make_response(workout_exercise_schema.dump(workout_exercise), 201)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
