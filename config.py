# GPT-4o Pricing Constants (per 1M tokens)
GPT4O_INPUT_COST_PER_MILLION = 2.5  # $2.5 per 1M input tokens
GPT4O_OUTPUT_COST_PER_MILLION = 10.0  # $10.0 per 1M output tokens

# Streamlit page configuration
PAGE_CONFIG = {
    "page_title": "AI Workout Plan Generator",
    "page_icon": "💪",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}

# Form options
FITNESS_LEVELS = ["Beginner", "Intermediate", "Advanced"]
GOAL_OPTIONS = ["Muscle Gain", "Weight Loss", "General Fitness", "Strength Building", "Endurance", "Flexibility"]
TRAINING_DAYS_OPTIONS = [3, 4, 5, 6, 7]
DURATION_OPTIONS = [30, 45, 60, 75, 90]
TARGET_AREA_OPTIONS = ["Chest", "Back", "Shoulders", "Arms", "Core", "Legs", "Glutes", "Full Body"]
EQUIPMENT_OPTIONS = [
    "Dumbbells", "Barbells", "Kettlebells", "Resistance Bands",
    "Pull-up Bar", "Gym Machine", "Bodyweight Only", "Yoga Mat", "Stability Ball"
]
PREFERENCE_OPTIONS = [
    "Strength", "Cardio", "Flexibility", "HIIT/Circuit", "Mixed", "Calisthenics", "Pilates", "Yoga"
]

# Fitness level descriptions
FITNESS_LEVEL_DESCRIPTIONS = {
    "Beginner": "New to structured exercise, learning proper form",
    "Intermediate": "Regular exercise routine, familiar with basic movements",
    "Advanced": "Experienced with complex exercises and training principles"
}

# Gender options
GENDER_OPTIONS = ["Male", "Female", "Other"]

# MET values for common exercises (Metabolic Equivalent of Task)
# Formula: Calories = METs x 3.5 x Weight(kg) / 200 x Duration(minutes)
EXERCISE_MET_VALUES = {
    # Strength Training
    "weight lifting": 6.0,
    "circuit training": 8.0,
    "bodyweight exercises": 3.8,
    "push ups": 3.8,
    "pull ups": 8.0,
    "sit ups": 3.8,
    "squats": 5.5,
    "deadlifts": 6.0,
    "bench press": 6.0,
    "lunges": 3.8,
    "planks": 4.0,
    
    # Cardio
    "running": 9.8,
    "jogging": 7.0,
    "walking": 3.5,
    "cycling": 8.0,
    "swimming": 9.8,
    "rowing": 7.0,
    "jumping jacks": 8.0,
    "burpees": 8.0,
    "jump rope": 12.3,
    "hiit": 8.0,
    
    # Flexibility & Recovery
    "yoga": 3.0,
    "stretching": 2.3,
    "pilates": 3.0,
    "cooldown": 2.0,
    "warm up": 3.0,
    
    # Default for unknown exercises
    "default": 5.0
}
