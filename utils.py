import os
import re
import json
import requests
import streamlit as st
from youtubesearchpython import VideosSearch
from typing import Dict, List
from datetime import datetime
from config import GPT4O_INPUT_COST_PER_MILLION, GPT4O_OUTPUT_COST_PER_MILLION, EXERCISE_MET_VALUES

def _parse_duration_to_seconds(duration_str: str) -> int:
    """Convert YouTube duration string (e.g. '1:15', '10:05', '45') to seconds."""
    if not duration_str:
        return 9999 
    try:
        parts = [int(p) for p in duration_str.split(':')]
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return parts[0] * 60 + parts[1]
        elif len(parts) == 3:
            return parts[0] * 3600 + parts[1] * 60 + parts[2]
    except:
        pass
    return 9999

def fetch_youtube_link(exercise_name: str, fitness_level: str = "") -> str:
    """Fetch the top YouTube video link using the official YouTube API."""
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        return ""
        
    # Clean exercise name to prevent search errors
    clean_exercise = re.sub(r'[^a-zA-Z0-9\s]', '', str(exercise_name))
    url = "https://www.googleapis.com/youtube/v3/search"
    base_params = {
        "part": "snippet",
        "type": "video",
        "key": api_key,
        "videoCategoryId": "17",  
        "relevanceLanguage": "en"
    }
    
    # Priority handles extracted from your exact links
    priority_handles = ["@DeltaBolic", "@tyler-path"]
    
    # Phase 1: Try priority channels specifically for SHORTS
    for handle in priority_handles:
        params = base_params.copy()
        params["q"] = f"{clean_exercise} {handle} #shorts"
        params["videoDuration"] = "short"  # YouTube API filter for < 4 mins
        params["maxResults"] = 3
        
        try:
            response = requests.get(url, params=params, timeout=5)
            data = response.json()
            if data.get("items"):
                for item in data["items"]:
                    channel_title = item.get("snippet", {}).get("channelTitle", "").lower().replace(" ", "")
                    # Strip symbols to ensure exact channel match
                    target_clean = handle.replace('@', '').replace('-', '').lower()
                    
                    if target_clean in channel_title:
                        video_id = item["id"]["videoId"]
                        # Return direct shorts URL format
                        return f"https://www.youtube.com/shorts/{video_id}"
        except Exception as e:
            continue
            
    # Phase 2: Fallback search (Long videos)
    params = base_params.copy()
    params["q"] = f"{clean_exercise} {fitness_level} exercise proper form tutorial"
    params["videoDuration"] = "medium"  # Forces > 4 minutes
    params["maxResults"] = 1
    
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        if data.get("items"):
            video_id = data["items"][0]["id"]["videoId"]
            return f"https://www.youtube.com/watch?v={video_id}"
    except Exception as e:
        pass
        
    return ""

@st.cache_data(ttl=86400, show_spinner=False)
def get_youtube_tutorial(exercise_name: str) -> str:
    """
    Fetch the top YouTube video using youtube-search-python.
    Optimized to search the exact handles from your URLs for Shorts first.
    """
    clean_exercise = re.sub(r'[^a-zA-Z0-9\s]', '', str(exercise_name))
    if not clean_exercise.strip():
        return None

    # Extracted from your links
    priority_handles = ["@DeltaBolic", "@tyler-path"]
    
    # Phase 1: Search Priority Channels strictly for SHORTS
    for handle in priority_handles:
        search_query = f"{clean_exercise} {handle} #shorts"
        print(f"🔍 Searching: '{search_query}'...")
        
        try: 
            videosSearch = VideosSearch(search_query, limit=3)
            result = videosSearch.result()
            
            if result and result.get('result'):
                for video_data in result['result']:
                    channel_name = video_data.get('channel', {}).get('name', '').lower().replace(' ', '')
                    target_handle_clean = handle.replace('@', '').replace('-', '').lower()
                    
                    # Check 1: Did YouTube return the requested channel?
                    is_correct_channel = target_handle_clean in channel_name
                    
                    # Check 2: Is it a Short? (<= 65 seconds)
                    duration_seconds = _parse_duration_to_seconds(video_data.get('duration'))
                    is_short = duration_seconds <= 65
                    
                    if is_correct_channel and is_short:
                        video_id = video_data.get('id')
                        print(f"✅ Priority SHORT Found from {handle}!\n")
                        # Return properly formatted Shorts URL
                        return f"https://www.youtube.com/shorts/{video_id}"
                        
        except Exception as e:
            print(f"⚠️ Search error for {handle}: {e}")
            continue
            
    # Phase 2: Fallback General Search (Long Videos)
    fallback_query = f"{clean_exercise} exercise proper form tutorial"
    print(f"🔄 Falling back to general search (Long Videos): '{fallback_query}'...\n")
    
    try:
        videosSearch = VideosSearch(fallback_query, limit=3)
        result = videosSearch.result()
        
        if result and result.get('result'):
            for video_data in result['result']:
                duration_seconds = _parse_duration_to_seconds(video_data.get('duration'))
                
                # Prefer videos > 65 seconds to guarantee long-form format
                if duration_seconds > 65:
                    print("✅ Fallback Match Found (Long Video)!\n")
                    video_id = video_data.get('id')
                    return f"https://www.youtube.com/watch?v={video_id}"
            
            # Failsafe: return the first result if everything else fails
            video_id = result['result'][0].get('id')
            return f"https://www.youtube.com/watch?v={video_id}"
            
    except Exception as e:
        print(f"⚠️ An error occurred during fallback search: {e}")
        
    return None
    
def calculate_token_costs(input_tokens: int, output_tokens: int) -> Dict[str, float]:
    """Calculate costs for GPT-4o token usage"""
    input_cost = (input_tokens / 1_000_000) * GPT4O_INPUT_COST_PER_MILLION
    output_cost = (output_tokens / 1_000_000) * GPT4O_OUTPUT_COST_PER_MILLION
    total_cost = input_cost + output_cost
    
    return {
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost
    }

def initialize_session_usage():
    """Initialize session token usage tracking"""
    if 'session_usage' not in st.session_state:
        st.session_state.session_usage = {
            'total_input_tokens': 0,
            'total_output_tokens': 0,
            'total_requests': 0,
            'requests': []
        }

def update_session_usage(input_tokens: int, output_tokens: int, request_type: str = "Workout Generation"):
    """Update session token usage tracking"""
    initialize_session_usage()
    
    # Add to totals
    st.session_state.session_usage['total_input_tokens'] += input_tokens
    st.session_state.session_usage['total_output_tokens'] += output_tokens
    st.session_state.session_usage['total_requests'] += 1
    
    # Add individual request
    costs = calculate_token_costs(input_tokens, output_tokens)
    st.session_state.session_usage['requests'].append({
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'type': request_type,
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'input_cost': costs['input_cost'],
        'output_cost': costs['output_cost'],
        'total_cost': costs['total_cost']
    })
    
def create_workout_json_output(form_data: Dict, days_data: List[Dict]) -> str:
    """Create comprehensive JSON output for workout plan"""
    
    # Calculate weekly stats
    total_exercises = sum(len(day['exercises']) for day in days_data)
    total_duration = sum(day.get('workout_duration', 0) for day in days_data)
    
    # Process days data
    processed_days = []
    for day_data in days_data:
        day_exercises = []
        
        for exercise in day_data.get('exercises', []):
            exercise_info = {
                "exercise_name": exercise.get('exercise_name', ''),
                "exercise_type": exercise.get('exercise_type', ''),
                "equipment_required": exercise.get('equipment_required', ''),
                "target_muscle_group": exercise.get('target_muscle_group', ''),
                "parameters": {
                    "total_sets": exercise.get('total_sets', 1),
                    "reps": exercise.get('reps', ''),
                    "tempo": exercise.get('tempo', ''),
                    "rest_time": exercise.get('rest_time', ''),
                    "weight": exercise.get('weight', ''),
                    "speed_level": exercise.get('speed_level', ''),
                    "breathing_pattern": exercise.get('breathing_pattern', ''),
                    "superset_indicator": exercise.get('superset_indicator', 'None')
                }
            }
            day_exercises.append(exercise_info)
        
        processed_days.append({
            "day": day_data.get('title', f"Day {day_data.get('day', 1)}"),
            "workout_type": day_data.get('workout_type', 'Workout'),
            "workout_duration": day_data.get('workout_duration', 0),
            "total_exercises": len(day_exercises),
            "exercises": day_exercises
        })
    
    # Create the complete JSON structure
    workout_json = {
        "workout_plan": {
            "plan_name": f"{form_data.get('training_days_per_week', form_data.get('weekly_frequency', 3))}-Day {form_data['goal']} Workout Plan",
            "meta_data": {
                "name": form_data.get('name', ''),
                "goal": form_data.get('goal', ''),
                "fitness_level": form_data.get('fitness_level', ''),
                "age": form_data.get('age', 0),
                "gender": form_data.get('gender', ''),
                "weight": form_data.get('weight', 0),
                "height": form_data.get('height', 0),
                "workout_preferences": form_data.get('workout_preferences', []),
                "training_days_per_week": form_data.get('training_days_per_week', form_data.get('weekly_frequency', 3)),
                "session_duration": form_data.get('session_duration', form_data.get('duration_per_session', 45)),
                "available_equipment": form_data.get('available_equipment', []),
                "target_areas": form_data.get('target_areas', []),
                "health_limitations": form_data.get('health_limitations', ''),
                "exercises_to_avoid": form_data.get('exercises_to_avoid', ''),
                "additional_notes": form_data.get('additional_notes', '')
            },
            "days": processed_days,
            "weekly_summary": {
                "total_workout_days": len(days_data),
                "total_exercises": total_exercises,
                "total_weekly_duration_minutes": total_duration,
                "average_duration_per_session": round(total_duration / len(days_data)) if days_data else 0
            },
            "audit_info": {
                "created_by": "AI Workout Plan Generator",
                "created_on": datetime.now().isoformat(),
                "updated_by": None,
                "updated_on": None
            }
        }
    }
    
    return json.dumps(workout_json, indent=2, ensure_ascii=False)

def create_text_format(days_data: List[Dict], user_data: Dict) -> str:
    """Create a formatted text version of the workout plan"""
    text_content = []
    
    # Header
    text_content.append("=" * 70)
    text_content.append("💪 PERSONALIZED WORKOUT PLAN")
    text_content.append("=" * 70)
    text_content.append("")
    
    # User profile summary
    text_content.append("👤 PROFILE SUMMARY:")
    text_content.append("-" * 30)
    text_content.append(f"Name: {user_data.get('name', 'N/A')}")
    text_content.append(f"Age: {user_data.get('age', 'N/A')} years")
    text_content.append(f"Gender: {user_data.get('gender', 'N/A').title()}")
    text_content.append(f"Weight: {user_data.get('weight', 'N/A')} kg")
    text_content.append(f"Height: {user_data.get('height', 'N/A')} cm")
    text_content.append(f"Fitness Goal: {user_data.get('goal', 'N/A')}")
    text_content.append(f"Fitness Level: {user_data.get('fitness_level', 'N/A')}")
    text_content.append(f"Training Days: {user_data.get('training_days_per_week', user_data.get('weekly_frequency', 'N/A'))} days/week")
    text_content.append(f"Session Duration: {user_data.get('session_duration', user_data.get('duration_per_session', 'N/A'))} minutes")
    
    if user_data.get('workout_preferences'):
        text_content.append(f"Workout Preferences: {', '.join(user_data['workout_preferences'])}")
    
    if user_data.get('available_equipment'):
        text_content.append(f"Available Equipment: {', '.join(user_data['available_equipment'])}")
    
    if user_data.get('target_areas'):
        text_content.append(f"Target Areas: {', '.join(user_data['target_areas'])}")
    
    if user_data.get('health_limitations'):
        text_content.append(f"Health Limitations: {user_data['health_limitations']}")
    
    text_content.append("")
    text_content.append("")
    
    # Daily workout plans
    for day_data in days_data:
        text_content.append("=" * 70)
        text_content.append(f"🏋️ {day_data['title']}")
        text_content.append(f"Workout Type: {day_data['workout_type']}")
        text_content.append(f"Duration: {day_data['workout_duration']} minutes")
        text_content.append("=" * 70)
        text_content.append("")
        
        for exercise in day_data['exercises']:
            text_content.append(f"💪 {exercise['exercise_name'].upper()}")
            text_content.append("-" * 50)
            
            if exercise.get('exercise_type'):
                text_content.append(f"Type: {exercise['exercise_type']}")
            if exercise.get('target_muscle_group'):
                text_content.append(f"Target Muscles: {exercise['target_muscle_group']}")
            if exercise.get('equipment_required'):
                text_content.append(f"Equipment: {exercise['equipment_required']}")
            
            # Exercise parameters
            params = []
            if exercise.get('reps'):
                params.append(f"Reps: {exercise['reps']}")
            if exercise.get('rest_time'):
                params.append(f"Rest: {exercise['rest_time']}")
            if exercise.get('weight'):
                params.append(f"Weight: {exercise['weight']}")
            if exercise.get('tempo'):
                params.append(f"Tempo: {exercise['tempo']}")
            
            if params:
                text_content.append(f"Parameters: {' | '.join(params)}")
            
            if exercise.get('breathing_pattern'):
                text_content.append(f"Breathing: {exercise['breathing_pattern']}")
            
            text_content.append("")
        
        text_content.append("")
    
    # Footer
    text_content.append("=" * 70)
    text_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    text_content.append("Generated by: AI Workout Plan Generator")
    text_content.append("=" * 70)
    
    return "\n".join(text_content)

def calculate_calories_burned(exercise_name: str, weight_str: str, duration_minutes: float, exercise_type: str) -> float:
    if not weight_str or weight_str == 'NA':
        return 0.0
    
    # Parse weight: take average of range or use single value
    try:
        if '-' in weight_str:
            low, high = map(float, weight_str.split('-'))
            weight_kg = (low + high) / 2  # Use midpoint for calculations
        else:
            weight_kg = float(weight_str)
    except:
        return 0.0
    
    if weight_kg <= 0:
        return 0.0
    
    # Convert exercise name to lowercase for matching
    exercise_lower = exercise_name.lower()
    
    # Try to find matching MET value
    met_value = EXERCISE_MET_VALUES.get("default", 5.0)
    
    # Check for exact or partial matches
    for key, value in EXERCISE_MET_VALUES.items():
        if key in exercise_lower or exercise_lower in key:
            met_value = value
            break
    
    # Adjust based on exercise type if no match found
    if met_value == EXERCISE_MET_VALUES["default"]:
        exercise_type_lower = exercise_type.lower()
        if "cardio" in exercise_type_lower or "hiit" in exercise_type_lower:
            met_value = 8.0
        elif "strength" in exercise_type_lower or "compound" in exercise_type_lower:
            met_value = 6.0
        elif "warm" in exercise_type_lower:
            met_value = 3.0
        elif "cool" in exercise_type_lower or "flexibility" in exercise_type_lower:
            met_value = 2.5
    
    # Calculate calories: METs x 3.5 x Weight(kg) / 200 x Duration(minutes)
    calories = met_value * 3.5 * weight_kg / 200 * duration_minutes
    
    return round(calories, 1)


def estimate_exercise_duration(total_sets: int, reps: str, rest_time: str) -> float:
    """
    Estimate exercise duration in minutes based on sets, reps, and rest time.
    
    Args:
        total_sets: Number of sets
        reps: Rep count (can be a number or range like "10-12")
        rest_time: Rest time between sets (e.g., "60s", "2min")
    
    Returns:
        Estimated duration in minutes
    """
    # Parse reps - take average if it's a range
    try:
        if '-' in str(reps):
            rep_parts = re.findall(r'\d+', str(reps))
            avg_reps = sum(int(r) for r in rep_parts) / len(rep_parts) if rep_parts else 10
        else:
            avg_reps = float(re.findall(r'\d+', str(reps))[0]) if re.findall(r'\d+', str(reps)) else 10
    except:
        avg_reps = 10
    
    # Estimate time per rep (3 seconds average)
    time_per_set = (avg_reps * 3) / 60  # Convert to minutes
    
    # Parse rest time
    rest_minutes = 0
    try:
        rest_str = str(rest_time).lower()
        if 'min' in rest_str:
            rest_minutes = float(re.findall(r'\d+', rest_str)[0]) if re.findall(r'\d+', rest_str) else 1
        elif 's' in rest_str:
            rest_seconds = float(re.findall(r'\d+', rest_str)[0]) if re.findall(r'\d+', rest_str) else 60
            rest_minutes = rest_seconds / 60
        else:
            rest_minutes = 1  # Default 1 minute
    except:
        rest_minutes = 1
    
    # Total duration: (time per set + rest) * number of sets
    total_duration = (time_per_set + rest_minutes) * total_sets
    
    return round(total_duration, 2)

def parse_range_or_value(value_str):
            """Parse '25' or '25-35' → returns '25-35' for prompt (range preserved)"""
            if not value_str or value_str.strip() == "":
                return None
            value_str = value_str.strip()
            if '-' in value_str:
                parts = value_str.split('-')
                if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
                    return value_str.strip()  # Keep range as-is for prompt
            elif value_str.isdigit():
                return value_str  # Single value
            return None  # 
        
# @st.cache_data(ttl=86400, show_spinner=False)
# def get_youtube_tutorial(exercise_name: str) -> str:
#     """
#     Fetch the top YouTube video tutorial for a given exercise.
#     Caches the result for 24 hours (86400 seconds) to improve performance.
#     """
#     search_query = f"{exercise_name} exercise proper form tutorial"
#     print(f"🔍 Searching YouTube for: '{search_query}'...\n")
    
#     try: 
#         # Initialize search with a limit of 1 result
#         videosSearch = VideosSearch(search_query, limit=1)
#         result = videosSearch.result()
        
#         # Safely extract the data if it exists
#         if result and result.get('result'):
#             video_data = result['result'][0]
            
#             print("✅ Match Found!\n")
#             print(f"📺 Title:    {video_data.get('title')}")
#             print(f"🔗 URL:      {video_data.get('link')}")
#             print(f"👤 Channel:  {video_data.get('channel', {}).get('name')}")
#             print(f"⏱️ Duration: {video_data.get('duration')}")
#             print(f"👁️ Views:    {video_data.get('viewCount', {}).get('short')}")
            
#             return video_data.get('link')
#         else:
#             print("❌ No results found.")
#             return None
            
#     except Exception as e:
#         print(f"⚠️ An error occurred: {e}")
#         return None