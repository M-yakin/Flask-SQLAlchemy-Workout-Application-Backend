# Workout Application Backend

## Description

A Flask REST API for a workout tracking application used by personal trainers.
It tracks workouts and the exercises in them. Exercises are reusable, so the
same exercise can be added to many workouts, with sets, reps, or duration
stored for each workout/exercise pair.

Built with Flask, Flask-SQLAlchemy, Flask-Migrate, and Marshmallow, using SQLite.

## Data Model

- **Exercise**: `id`, `name` (unique), `category`, `equipment_needed`
- **Workout**: `id`, `date`, `duration_minutes`, `notes`
- **WorkoutExercise** (join table): `id`, `workout_id`, `exercise_id`, `reps`, `sets`, `duration_seconds`

A workout has many exercises through WorkoutExercise, and an exercise has many
workouts through WorkoutExercise. Deleting a workout or exercise also deletes
its WorkoutExercise rows.

## Validations

- **Table constraints**: unique exercise name, non-null fields, `CHECK` constraints
  (positive duration, reps, sets, and duration_seconds; non-empty name and category)
- **Model validations**: non-empty name, category from an allowed list, boolean
  `equipment_needed`, positive integers for duration, reps, sets, and duration_seconds
- **Schema validations**: required fields, length and range limits, strict
  integer and boolean types, and at least one of reps, sets, or duration_seconds
  when adding an exercise to a workout

Allowed categories: `strength`, `cardio`, `flexibility`, `balance`, `core`.

## Installation

Requires Python 3.8 or newer and Pipenv.

```bash
git clone https://github.com/M-yakin/Flask-SQLAlchemy-Workout-Application-Backend.git
cd Flask-SQLAlchemy-Workout-Application-Backend
pipenv install
pipenv shell
cd server
flask db upgrade head
python seed.py
```

`python seed.py` clears the tables and loads example data. You can run it again
at any time to reset the database.

If you ever need to rebuild the migrations from scratch:

```bash
rm -rf migrations instance
flask db init
flask db migrate -m "Create tables"
flask db upgrade head
```

## Running the app

From the `server/` folder, with the virtual environment active:

```bash
python app.py
```

The API runs at `http://localhost:5555`.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workouts` | List all workouts |
| GET | `/workouts/<id>` | Show one workout with its exercises, including reps, sets, and duration |
| POST | `/workouts` | Create a workout |
| DELETE | `/workouts/<id>` | Delete a workout and its WorkoutExercises |
| GET | `/exercises` | List all exercises |
| GET | `/exercises/<id>` | Show one exercise with the workouts it appears in |
| POST | `/exercises` | Create an exercise |
| DELETE | `/exercises/<id>` | Delete an exercise and its WorkoutExercises |
| POST | `/workouts/<workout_id>/exercises/<exercise_id>/workout_exercises` | Add an exercise to a workout with reps, sets, and/or duration |

### Example requests

```bash
curl -X POST http://localhost:5555/workouts \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-11-02", "duration_minutes": 40, "notes": "Leg day"}'

curl -X POST http://localhost:5555/exercises \
  -H "Content-Type: application/json" \
  -d '{"name": "Lunges", "category": "strength", "equipment_needed": false}'

curl -X POST http://localhost:5555/workouts/1/exercises/4/workout_exercises \
  -H "Content-Type: application/json" \
  -d '{"sets": 3, "reps": 10}'
```

### Status codes

- `200` OK, `201` Created, `204` Deleted (no body)
- `404` Workout or exercise not found
- `409` Database constraint failed (for example, a duplicate exercise name)
- `422` Validation failed (the response lists the errors)