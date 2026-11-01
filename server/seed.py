#!/usr/bin/env python3

from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise

with app.app_context():

    # Clear existing data (join table first, because it depends on the others)
    print("Clearing tables...")
    WorkoutExercise.query.delete()
    Exercise.query.delete()
    Workout.query.delete()
    db.session.commit()

    
    # Exercises
    print('Seeding exercises...')
    pushups = Exercise(name='Push-ups', category='strength', equipment_needed=False)
    squats = Exercise(name='Squats', category='strength', equipment_needed=False)
    bench = Exercise(name='Bench Press', category='strength', equipment_needed=True)
    running = Exercise(name='Running', category='cardio', equipment_needed=False)
    jump_rope = Exercise(name='Jump Rope', category='cardio', equipment_needed=True)
    plank = Exercise(name='Plank', category='core', equipment_needed=False)
    yoga = Exercise(name='Yoga Stretch', category='flexibility', equipment_needed=False)

    db.session.add_all([pushups, squats, bench, running, jump_rope, plank, yoga])
    db.session.commit()

    # Workouts
    print('Seeding workouts...')
    w1 = Workout(date=date(2026, 10, 26), duration_minutes=45, notes='Upper body focus')
    w2 = Workout(date=date(2026, 10, 28), duration_minutes=30, notes='Cardio and core')
    w3 = Workout(date=date(2026, 10, 30), duration_minutes=60, notes='Full body session')

    db.session.add_all([w1, w2, w3])
    db.session.commit()
    
    # WorkoutExercises (links a workout to an exercise, with sets/reps/duration)
    print('Seeding workout exercises...')
    entries = [
        WorkoutExercise(workout=w1, exercise=pushups, sets=3, reps=15),
        WorkoutExercise(workout=w1, exercise=bench, sets=4, reps=8),
        WorkoutExercise(workout=w2, exercise=running, duration_seconds=900),
        WorkoutExercise(workout=w2, exercise=plank, sets=3, duration_seconds=60),
        WorkoutExercise(workout=w3, exercise=squats, sets=4, reps=12),
        WorkoutExercise(workout=w3, exercise=jump_rope, sets=3, duration_seconds=120),
        WorkoutExercise(workout=w3, exercise=yoga, duration_seconds=300),
    ]

    db.session.add_all(entries)
    db.session.commit()

    print('Done seeding!')
                                                             