import os
import re
import json
import openai
import streamlit as st
from typing import Dict, List
from dotenv import load_dotenv
from utils import update_session_usage, calculate_token_costs,calculate_calories_burned,estimate_exercise_duration
from config import FITNESS_LEVEL_DESCRIPTIONS
from utils import fetch_youtube_link  # Add to existing import
import base64 



# Load environment variables
load_dotenv()

class WorkoutPlanGenerator:
    def __init__(self):
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai
    
    def set_api_key(self, api_key: str):
        """Set OpenAI API key"""
        openai.api_key = api_key
        self.client = openai
    
    def get_fitness_level_description(self, level: str) -> str:
        """Get fitness level description"""
        return FITNESS_LEVEL_DESCRIPTIONS.get(level, "Unknown level")
    
    def create_prompt(self, user_data: Dict) -> str:
        """Create comprehensive prompt for GPT-4o focused on detailed workout plans in JSON format"""
        
        # Determine exercise types based on workout preferences
        exercise_types_text = ""
        if user_data['workout_preferences']:
            if isinstance(user_data['workout_preferences'], list):
                exercise_types_text = f"- Preferred Exercise Types: {', '.join(user_data['workout_preferences'])}"
            else:
                exercise_types_text = f"- Preferred Exercise Types: {user_data['workout_preferences']}"
        
        # Equipment preference text
        equipment_text = ""
        if user_data.get('available_equipment'):
            equipment_text = (
                f"- Available Equipment (detected from user's actual gym photos): "
                f"{', '.join(user_data['available_equipment'])}\n"
                f"  IMPORTANT: Generate exercises SPECIFICALLY for these machines. "
                f"Do not suggest alternatives — use only what is listed."
            )

        # Health limitations text
        limitations_text = ""
        if user_data.get('health_limitations'):
            limitations_text = f"- Health Limitations: {user_data['health_limitations']}"
        
        # Target areas text
        target_areas_text = ""
        if user_data.get('target_areas'):
            target_areas_text = f"- Target Areas: {', '.join(user_data['target_areas'])}"
        
        prompt = f"""Create a comprehensive, personalized {user_data['weekly_frequency']}-day workout plan based on the following information:

PERSONAL INFORMATION:
- Name: {user_data.get('name', 'User')}
- Age: {user_data['age']} years
- Gender: {user_data['gender']}
- Weight: {user_data.get('weight', 'N/A')}
- Height: {user_data.get('height', 'N/A')}

FITNESS PROFILE:
- Current Fitness Level: {user_data['fitness_level']}
- Primary Fitness Goal: {user_data['goal']}
- Training Days per Week: {user_data.get('training_days_per_week', user_data['weekly_frequency'])}
- Session Duration: {user_data.get('session_duration', user_data['duration_per_session'])} minutes
{exercise_types_text}

EQUIPMENT & PREFERENCES:
{equipment_text}    
{target_areas_text}   

HEALTH & LIMITATIONS:
{limitations_text}
- Exercises to Avoid: {user_data.get('exercises_to_avoid', 'None')}

ADDITIONAL INFORMATION:
- Additional Notes: {user_data.get('additional_notes', 'None')}

WORKOUT PLAN REQUIREMENTS:
Create a detailed workout plan in JSON format that includes:
- Day-wise breakdown for {user_data['weekly_frequency']} workout days
- Each day should have a specific workout type (Strength, Cardio, Flexibility, HIIT/Circuit, etc.)
- Exercise-level details for each workout
- Progressive difficulty based on fitness level  
- Proper warm-up and cool-down exercises  
- Equipment requirements and alternatives  

Return the response in the following JSON structure:
{{
  "workout_plan": {{
    "day_1": {{
      "day_name": "Day 1 - Monday",
      "workout_type": "Strength Training",
      "workout_duration": {user_data.get('session_duration', user_data['duration_per_session'])},
      "exercises": [
        {{
          "exercise_name": "Exercise name",
          "exercise_type": "Compound/Isolation/Warm-up/Cooldown",
          "equipment_required": "Equipment needed or Bodyweight",
          "target_muscle_group": "Primary muscle groups targeted",
          "total_sets": 1,
          "reps": "Number of repetitions or duration",
          "tempo": "3-1-2 (3 sec down, 1 sec pause, 2 sec up)",
          "rest_time": "Rest duration between sets (e.g., 60s)",
          "weight": "Recommended weight based on fitness level",
          "speed_level": "For cardio exercises: Slow/Moderate/Fast",
          "breathing_pattern": "Inhale/exhale rhythm instructions",
          "superset_indicator": "None or paired exercise name",
          "workoutparametertype": ["Repetition-Based", "Duration-Based"]  

        }}
      ]
    }},
    // Continue for all {user_data['weekly_frequency']} workout days
  }}
}}

Guidelines:
1. Provide specific rep ranges appropriate for the fitness level:
   - Beginner: 8-12 reps, lighter weights, more rest
   - Intermediate: 10-15 reps, moderate intensity
   - Advanced: 12-20 reps or advanced techniques
2. Include proper progression and variety across days
3. Balance different muscle groups throughout the week
4. Include warm-up and cool-down exercises for each session
5. Provide equipment alternatives when possible
6. Match workout types to user's preferred exercise types
7. Ensure total workout duration matches specified session time
8. Include proper rest periods between sets
9. Add tempo instructions for strength exercises
10. Include breathing patterns for all exercises
11. Consider health limitations and exercises to avoid
12. Focus on target areas if specified
13.**CRITICAL: workoutparametertype MUST be ARRAY ["Type1", "Type2"] with ALL applicable types - NEVER single string.
    Available Types: Repetition-Based, Duration-Based, Distance-Based, Speed-Based, Mixed/Interval-Based
    Multi-category Examples:**
    - Repetition + Duration: Mountain Climbers, Burpees, Plank Jacks, Lateral Band Walk
    - Duration + Speed: Running, Cycling, Rowing 
    - Repetition + Speed: Jump Squat, Box Jump 
    - Repetition + Distance: Walking Lunges, Farmer's Carry 
   
    
Workout Type Distribution for {user_data['weekly_frequency']} days:
- Focus on {user_data['goal']} with {user_data['workout_preferences']} preferences
- Ensure balanced approach with strength, cardio, and recovery
- Progressive overload principles for continuous improvement"""
        
        return prompt
    
    def generate_workout_plan(self, user_data: Dict) -> str:
        """Generate workout plan using OpenAI GPT-4o with JSON output"""
        try:
            prompt = self.create_prompt(user_data)
            print(prompt)
            
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a certified personal trainer and exercise physiologist with over 15 years of experience in creating personalized workout plans. You specialize in strength training, cardiovascular fitness, functional movement, and injury prevention. Always provide specific exercise parameters including sets, reps, tempo, and rest periods. Always respond in valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},
            )
            print(response)
            # Extract token usage information
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            
            # Update session usage tracking
            update_session_usage(input_tokens, output_tokens, "Workout Plan Generation")
            
            # Store latest usage in session state for display
            st.session_state.latest_usage = {
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'costs': calculate_token_costs(input_tokens, output_tokens)   
            }
            
            return response.choices[0].message.content
        
        except Exception as e:
            raise Exception(f"Error generating workout plan: {str(e)}")
    
    def detect_equipment_from_images(self, uploaded_files) -> list:
        
    # import base64

        image_messages = []
        for file in uploaded_files:
            file.seek(0)  # reset buffer in case it was read before
            b64 = base64.b64encode(file.read()).decode("utf-8")
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{file.type};base64,{b64}",
                    "detail": "low"  # saves tokens
                }
            })

        image_messages.append({
            "type": "text",
            "text": (
                "Analyse these gym images carefully. Identify every piece of fitness equipment "
                "or machine you can see. Return ONLY a valid JSON array of specific equipment names. "
                "Be precise — e.g. [\"Lat Pulldown Machine\", \"Cable Crossover\", \"Treadmill\", "
                "\"Adjustable Dumbbells\", \"Leg Press Machine\"]. "
                "Do not include any explanation, just the JSON array."
            )
        })

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": image_messages}],
            max_tokens=300
        )

        # Track token usage
        usage = response.usage
        update_session_usage(usage.prompt_tokens, usage.completion_tokens, "Equipment Detection")

        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if GPT wraps in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())

    
    def parse_workout_plan(self, workout_plan_json: str) -> List[Dict]:
        """Parse the JSON workout plan into structured daily workout data"""
        try:
            # 1. Clean up the JSON string in case GPT wraps it in markdown code blocks
            json_str = workout_plan_json.strip()
            if json_str.startswith("```"):
                json_str = json_str.split("```")[1]
                if json_str.lower().startswith("json"):
                    json_str = json_str[4:]
            json_str = json_str.strip()

            # 2. Parse JSON response
            workout_data = json.loads(json_str)
            
            # Extract workout plan data
            if "workout_plan" in workout_data:
                plan_data = workout_data["workout_plan"]
            else:
                plan_data = workout_data
            
            days_data = []
            
            # 3. Safely handle cases where GPT returns a list instead of a dictionary
            if isinstance(plan_data, list):
                day_items = [(f"day_{i+1}", day_info) for i, day_info in enumerate(plan_data)]
            elif isinstance(plan_data, dict):
                day_items = plan_data.items()
            else:
                return []

            # Process each day
            for day_key, day_info in day_items:
                # 4. CRITICAL FIX: Skip if day_info is not a dict (e.g. GPT returned {"plan_name": "..."})
                if not isinstance(day_info, dict):
                    continue
                    
                # Extract day number from key safely
                day_numbers = re.findall(r'\d+', str(day_key))
                day_number = int(day_numbers[0]) if day_numbers else len(days_data) + 1
                
                day_data = {
                    'day': day_number,
                    'title': day_info.get('day_name', f'Day {day_number}'),
                    'workout_type': day_info.get('workout_type', 'Workout'),
                    'workout_duration': day_info.get('workout_duration', 0),
                    'exercises': []
                }
                
                # Default to NA if session state missing
                user_weight_input = st.session_state.form_data.get('weight', 'NA') if 'form_data' in st.session_state else 'NA'

                # Process exercises for this day
                for exercise in day_info.get('exercises', []):
                    # Safely skip non-dict exercises
                    if not isinstance(exercise, dict):
                        continue
                        
                    exercise_name = exercise.get('exercise_name', '') or ''
                    exercise_type = exercise.get('exercise_type', '') or ''
                    
                    # Calculate estimated duration for this exercise
                    est_duration = estimate_exercise_duration(
                        exercise.get('total_sets', 1),
                        exercise.get('reps', '10'),
                        exercise.get('rest_time', '60s')
                    )
                    
                    # Calculate calories burned
                    if user_weight_input != 'NA': 
                        calories_burned = calculate_calories_burned(
                            exercise_name,
                            user_weight_input,
                            est_duration, 
                            exercise_type
                        )
                    else:
                        calories_burned = 0
                        
                    exercise_data = {
                        'exercise_name': exercise_name,
                        'exercise_type': exercise_type,
                        'equipment_required': exercise.get('equipment_required', ''),
                        'target_muscle_group': exercise.get('target_muscle_group', ''),
                        'total_sets': exercise.get('total_sets', 1),
                        'reps': exercise.get('reps', ''),
                        'tempo': exercise.get('tempo', ''),
                        'rest_time': exercise.get('rest_time', ''),
                        'weight': exercise.get('weight', ''),
                        'speed_level': exercise.get('speed_level', ''),
                        'breathing_pattern': exercise.get('breathing_pattern', ''),
                        'workoutparametertype': exercise.get('workoutparametertype', []),
                        'superset_indicator': exercise.get('superset_indicator', 'None'),
                        'estimated_duration': est_duration,
                        'calories_burned': calories_burned
                    }

                    # Note: We commented out YouTube fetching to prevent severe API timeouts/lag. 
                    # If you wish to fetch them, ensure it checks `exercise_name` not `exercisename`
                    
                    # Only add exercise if it has a name
                    if exercise_data['exercise_name']:
                        day_data['exercises'].append(exercise_data)
                
                # Only add day if it has valid exercises
                if day_data['exercises']:
                    days_data.append(day_data)
            
            # Ensure days stay in order
            return sorted(days_data, key=lambda x: x['day'])
            
        except json.JSONDecodeError as e:
            st.error(f"Error parsing JSON response: {str(e)}")
            return []
        except Exception as e:
            st.error(f"Error processing workout plan: {str(e)}")
            return []
