import streamlit as st
from datetime import datetime
from typing import Dict, List
from config import (
    FITNESS_LEVELS, GOAL_OPTIONS, TRAINING_DAYS_OPTIONS, DURATION_OPTIONS,
    TARGET_AREA_OPTIONS, PREFERENCE_OPTIONS, GENDER_OPTIONS
)
from utils import create_workout_json_output, create_text_format, get_youtube_tutorial

def load_css():
    """Load custom CSS for professional styling"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #779bc9 15%, #d48383 90%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0 !important;
    }
    
    /* Form sections */
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
    }
    
    .form-section:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .section-title {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #4a5568 !important;
        margin-bottom: 1.5rem !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
    }
    
    /* Fitness level card */
    .fitness-card {
        background: linear-gradient(135deg, #8194eb 40%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.3);
    }
    
    .fitness-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .fitness-description {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Loading screen */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
        background: linear-gradient(135deg, #779bc9 15%, #d48383 90%);
        border-radius: 25px;
        padding: 3rem;
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .loading-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(180deg); }
    }
    
    .workout-animation {
        font-size: 5rem;
        margin-bottom: 2rem;
        animation: bounce 2s infinite, rotate 4s linear infinite;
        z-index: 1;
    }
    
    @keyframes bounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-30px); }
        60% { transform: translateY(-15px); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    .loading-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        z-index: 1;
    }
    
    .loading-subtitle {
        font-size: 1.3rem;
        color: rgba(255,255,255,0.9);
        margin-bottom: 3rem;
        z-index: 1;
    }
    
    /* Results page styling */
    .results-header {
        background: linear-gradient(135deg, #779bc9 15%, #d48383 90%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .day-header {
        background: linear-gradient(135deg, #c2b0a7 15%, #86a8ba 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 2rem 0 1.5rem 0;
        text-align: center;
        box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
    
    .exercise-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
    }
    
    .exercise-card:hover {
        box-shadow: 0 7px 25px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    
    .exercise-header {
        background-color: #f8f9fa;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: #2d3748;
        border-bottom: 1px solid #e2e8f0;
        border-top-left-radius: 15px;
        border-top-right-radius: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .exercise-type {
        background: linear-gradient(135deg, #c4b486 30%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .exercise-content {
        padding: 1.5rem;
        flex-grow: 1;
    }

    .exercise-content p {
        color: #4a5568;
        margin-bottom: 0.5rem;
    }
    
    .exercise-footer {
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 1rem 1.5rem;
        background-color: #f8f9fa;
        border-top: 1px solid #e2e8f0;
        border-bottom-left-radius: 15px;
        border-bottom-right-radius: 15px;
    }
    
    .exercise-detail {
        text-align: center;
        color: #4a5568;
        font-size: 0.9rem;
    }
    
    .exercise-detail strong {
        display: block;
        font-size: 1.25rem;
        font-weight: 600;
        color: #2d3748;
    }

    .edit-form-container {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 2rem;
        border-radius: 20px;
        margin: 2rem 0;
        box-shadow: 0 10px 30px rgba(252, 182, 159, 0.3);
        border: 1px solid rgba(255, 236, 210, 0.5);
    }
    
    .edit-header {
        text-align: center;
        color: #8b4513;
        margin-bottom: 2rem;
    }
    
    .success-message {
        background: linear-gradient(135deg, #8ed4b5 10%, #8fd3f4 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: #2d5016;
        font-weight: 600;
        margin: 1rem 0;
        box-shadow: 0 5px 20px rgba(132, 250, 176, 0.3);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem !important; }
        .loading-title { font-size: 2rem; }
        .exercise-footer { flex-wrap: wrap; gap: 1rem; }
        .exercise-detail { flex-basis: 40%; }
        .exercise-header { flex-direction: column; gap: 0.5rem; text-align: center; }
    }
    
    </style>
    """, unsafe_allow_html=True)

def display_loading_animation():
    """Display a modern, animated loading screen for workout generation"""
    st.markdown("""
    <div class="loading-container">
        <div class="workout-animation">🏋️‍♂️</div>
        <div class="loading-title">Crafting Your Perfect Workout Plan</div>
        <div class="loading-subtitle">Our AI trainer is analyzing your fitness profile...</div>
    </div>
    """, unsafe_allow_html=True)

def display_professional_workout_plan(days_data: List[Dict]):
    """Display the workout plan with professional styling"""
    for day_data in days_data:
        st.markdown(f'<div class="day-header"><h2>🏋️ {day_data["title"]}</h2><p>Workout Type: {day_data["workout_type"]} | Duration: {day_data["workout_duration"]} minutes</p></div>', 
                   unsafe_allow_html=True)
        
        for exercise in day_data['exercises']:
            exercise_emojis = {
                'Compound': '🏋️‍♂️', 'Isolation': '💪', 'Warm-up': '🔥',
                'Cooldown': '🧘‍♀️', 'Cardio': '🏃‍♂️', 'Flexibility': '🤸‍♀️'
            }
            emoji = exercise_emojis.get(exercise['exercise_type'], '💪')
            
            # Build content HTML
            content_parts = []
            if exercise.get('target_muscle_group'):
                content_parts.append(f"<p><strong>Target Muscles:</strong> {exercise['target_muscle_group']}</p>")
            if exercise.get('equipment_required'):
                content_parts.append(f"<p><strong>Equipment:</strong> {exercise['equipment_required']}</p>")
            if exercise.get('tempo'):
                content_parts.append(f"<p><strong>Tempo:</strong> {exercise['tempo']}</p>")
            if exercise.get('breathing_pattern'):
                content_parts.append(f"<p><strong>Breathing:</strong> {exercise['breathing_pattern']}</p>")
            if exercise.get('superset_indicator') and exercise.get('superset_indicator') != 'None':
                content_parts.append(f"<p><strong>Superset with:</strong> {exercise['superset_indicator']}</p>")
            if exercise.get('workoutparametertype'):
                param_types = ', '.join(exercise['workoutparametertype']) if isinstance(exercise['workoutparametertype'], list) else exercise['workoutparametertype']
                content_parts.append(f"<p><strong>Parameter Type:</strong> {param_types}</p>")
            
            content_html = "".join(content_parts)
            
            # Build footer HTML dynamically with calories
            footer_html = f"""
            <div class="exercise-footer">
                <div class="exercise-detail"><strong>{exercise['total_sets']}</strong><span>Total Sets</span></div>
                <div class="exercise-detail"><strong>{exercise['reps']}</strong><span>Reps</span></div>
                <div class="exercise-detail"><strong>{exercise['rest_time']}</strong><span>Rest</span></div>
                <div class="exercise-detail"><strong>{exercise['weight']}</strong><span>Weight</span></div>
            """
            
            # Add calories section if available
            if exercise.get('calories_burned', 0) > 0:
                footer_html += f"""<div class="exercise-detail"><strong style="display: block;">{exercise['calories_burned']}</strong><span style="display: block;">Calories</span></div>"""
            
            # footer_html += "</div>"
            
            # Render exercise card
            st.markdown(f"""
            <div class="exercise-card">
                <div class="exercise-header">
                    <div>{emoji} <strong>{exercise['exercise_name']}</strong></div>  
                    <div class="exercise-type">{exercise['exercise_type']}</div>
                </div>
                <div class="exercise-content">
                    {content_html}
                </div>
                {footer_html}
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"📹 Watch {exercise['exercise_name']} Tutorial"):
                video_url = get_youtube_tutorial(exercise['exercise_name'])
                if video_url:
                    st.video(video_url)
                else:
                    st.info("No video tutorial found for this exercise.")
        
        st.markdown("<br>", unsafe_allow_html=True)

def display_form(generator, is_edit=False):
    """Display the input form for workout plan generation with all additional fields"""
    
    # Pre-fill form with existing data if editing
    form_data = st.session_state.get('form_data', {}) if is_edit else {}
    
    if is_edit:
        st.markdown("""
        <div class="edit-form-container">
            <div class="edit-header">
                <h2>✏️ Edit Your Fitness Profile</h2>
                <p>Update any information and regenerate your personalized workout plan</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<h3 class="section-title">📸 Gym Equipment Detection</h3>', unsafe_allow_html=True)

    st.info(
        "📷 Upload photos of your gym (1–10 images). "
        "GPT-4o will identify every machine and piece of equipment, "
        "then build your workout plan specifically around what you have."
    )

    uploaded_images = st.file_uploader(
        "Upload gym photos",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        help="Take photos of all machines and equipment in your gym",
        key="gym_images"
    )

    # Thumbnail preview (up to 5)
    if uploaded_images:
        thumb_cols = st.columns(min(len(uploaded_images), 5))
        for i, img in enumerate(uploaded_images[:5]):
            with thumb_cols[i]:
                st.image(img, use_container_width=True, caption=f"Photo {i+1}")

    # Detect button — separate from the main form submit
    if uploaded_images:
        if st.button("🔍 Detect Equipment from Photos", use_container_width=True, key="detect_btn"):
            with st.spinner("Analysing your gym with GPT-4o... this may take a few seconds"):
                try:
                    detected = generator.detect_equipment_from_images(uploaded_images)
                    st.session_state.detected_equipment = detected
                    st.success(f"✅ Detected {len(detected)} piece(s) of equipment!")
                except Exception as e:
                    st.error(f"❌ Detection failed: {str(e)}")
                    st.session_state.detected_equipment = []

    # Show detected equipment chips + editable text area
    if "detected_equipment" in st.session_state and st.session_state.detected_equipment:
        badges_html = "".join(
            f'<span class="detected-badge">✓ {item}</span>'
            for item in st.session_state.detected_equipment
        )
        st.markdown(
            f'<div class="detection-box"><strong>Detected Equipment:</strong><br>{badges_html}</div>',
            unsafe_allow_html=True
        )
        st.markdown("<br>", unsafe_allow_html=True)
        detected_str = st.text_area(
            "✏️ Edit detected equipment if needed (comma-separated)",
            value=", ".join(st.session_state.detected_equipment),
            height=80,
            key="detected_equipment_edit",
            help="You can add, remove, or correct any equipment names here before generating the plan."
        )
    else:
        st.warning("⚠️ No equipment detected yet. Upload photos and click **Detect Equipment from Photos**.")
        detected_str = st.text_input(
            "Or enter your equipment manually (comma-separated)",
            placeholder="e.g. Treadmill, Lat Pulldown Machine, Adjustable Dumbbells, Leg Press",
            key="manual_equipment_input",
            help="Type each piece of equipment separated by commas."
        )

    st.markdown('</div>', unsafe_allow_html=True)
    
    with st.form("workout_form", clear_on_submit=not is_edit):
        # Personal Information Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">👤 Personal Information</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name (Optional)", value=form_data.get('name', ''), placeholder="Enter your name")
            age = st.text_input("Age", value=form_data.get('age_display', ' '), help="Enter either single age or range like '20-30'")
            weight = st.text_input("Weight (kg)", value=form_data.get('weight_display', ' '), help="Enter either single weight or range like '60-70'")
        with col2:
            gender_index = 0
            if is_edit and 'gender' in form_data:
                gender_value = form_data['gender'].title()
                gender_index = GENDER_OPTIONS.index(gender_value) if gender_value in GENDER_OPTIONS else 0
            gender = st.selectbox("Gender", GENDER_OPTIONS, index=gender_index) 
            height = st.text_input("Height (cm)", value=form_data.get('height', ' '), help="Enter either single height or range like '170-175'")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Fitness Profile Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">🏃‍♂️ Fitness Profile</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fitness_index = 0
            if is_edit and 'fitness_level' in form_data:
                fitness_index = FITNESS_LEVELS.index(form_data['fitness_level']) if form_data['fitness_level'] in FITNESS_LEVELS else 0
            fitness_level = st.selectbox("Current Fitness Level", FITNESS_LEVELS, index=fitness_index)
            
            goal_index = 0
            if is_edit and 'goal' in form_data:
                goal_index = GOAL_OPTIONS.index(form_data['goal']) if form_data['goal'] in GOAL_OPTIONS else 0
            goal = st.selectbox("Primary Goal", GOAL_OPTIONS, index=goal_index)
            
        with col2:
            training_days_index = 0
            if is_edit and 'training_days_per_week' in form_data:
                training_days_index = TRAINING_DAYS_OPTIONS.index(form_data['training_days_per_week']) if form_data['training_days_per_week'] in TRAINING_DAYS_OPTIONS else 0
            training_days_per_week = st.selectbox("Training Days per Week", TRAINING_DAYS_OPTIONS, index=training_days_index)
            
            duration_index = 1
            if is_edit and 'session_duration' in form_data:
                duration_index = DURATION_OPTIONS.index(form_data['session_duration']) if form_data['session_duration'] in DURATION_OPTIONS else 1
            session_duration = st.selectbox("Session Duration (minutes)", DURATION_OPTIONS, index=duration_index)
        
        # Target Areas
        default_target_areas = form_data.get('target_areas', []) if is_edit else []
        target_areas = st.multiselect("Target Areas (Optional)", TARGET_AREA_OPTIONS, 
                                    default=default_target_areas)
        
        # Fitness Level Description
        if fitness_level:
            description = generator.get_fitness_level_description(fitness_level)
            st.markdown(f"""
            <div class="fitness-card">
                <div class="fitness-value">{fitness_level}</div>
                <div class="fitness-description">{description}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Equipment & Preferences Section
        # ── REPLACE OLD EQUIPMENT SECTION WITH THIS ──────────────────────────────────
        
# ─────────────────────────────────────────────────────────────────────────────
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">🎯 Workout Preferences</h3>', unsafe_allow_html=True)

        default_preferences = form_data.get('workout_preferences', []) if is_edit else []
        workout_preferences = st.multiselect("Workout Style Preferences", PREFERENCE_OPTIONS, default=default_preferences)

        st.markdown('</div>', unsafe_allow_html=True)
    
        
        # Health & Limitations Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">🏥 Health & Limitations</h3>', unsafe_allow_html=True)
        
        health_limitations = st.text_area("Current Injuries or Physical Limitations", 
                                        value=form_data.get('health_limitations', ''),
                                        placeholder="e.g., Lower back pain, knee injury, shoulder issues...",
                                        help="Please describe any injuries or physical limitations")
        
        exercises_to_avoid = st.text_area("Exercises to Avoid", 
                                        value=form_data.get('exercises_to_avoid', ''),
                                        placeholder="e.g., squats, deadlifts, overhead press...",
                                        help="List specific exercises you want to avoid")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Additional Information Section
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<h3 class="section-title">📝 Additional Information</h3>', unsafe_allow_html=True)
        
        additional_notes = st.text_area("Additional Information", 
                                      value=form_data.get('additional_notes', ''),
                                      placeholder="Any other information you'd like to share about your fitness goals, preferences, or circumstances...",
                                      help="Optional: Share any additional context that might help create a better workout plan")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit Button
        button_text = "🔄 Regenerate My Workout Plan" if is_edit else "🚀 Generate My Personalized Workout Plan"
        submitted = st.form_submit_button(button_text, use_container_width=True)
        
        if submitted:  
            raw_equipment_str = st.session_state.get("detected_equipment_edit", "") or                                 st.session_state.get("manual_equipment_input", "")
            available_equipment = [e.strip() for e in raw_equipment_str.split(",") if e.strip()]

            if not available_equipment:
                st.warning(
                    "⚠️ No gym equipment detected or entered. "
                    "Please upload photos and click **Detect Equipment** first, "
                    "or enter your equipment manually above."
                )
                            
            if not all([age, gender, weight, height, fitness_level, goal, training_days_per_week, session_duration]):
                st.error("❌ Please fill in all required fields.(Age, Gender, Weight, Height, Fitness Level, Primary Fitness Goal, Training Days per Week, Session Duration)")
            else:
                st.session_state.form_data = {
                    'name': name,
                    'age': age,
                    'gender': gender.lower(),
                    'weight': weight,
                    'height': height,
                    'fitness_level': fitness_level,
                    'goal': goal,
                    'training_days_per_week': training_days_per_week,
                    'session_duration': session_duration,
                    'target_areas': target_areas,
                    'available_equipment': available_equipment,
                    'workout_preferences': workout_preferences,
                    'health_limitations': health_limitations,
                    'exercises_to_avoid': exercises_to_avoid,
                    'additional_notes': additional_notes,
                    # Keep compatibility with existing code
                    'weekly_frequency': training_days_per_week,
                    'duration_per_session': session_duration
                }
                
                st.session_state.page = 'generating'
                st.rerun()

def display_results():
    """Display the generated workout plan with edit functionality and format options"""
    st.markdown("""
    <div class="results-header">
        <h1>💫 Your Personalized Workout Plan</h1>
        <p>Crafted specifically for your fitness goals and experience level</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action buttons with dropdown for download format
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        # Download dropdown with format selection
        download_format = st.selectbox(
            "📥 Download Plan",
            options=[
                "Select Format", 
                "Text (.txt)", 
                "JSON (.json)"
            ],
            key="download_format_select"
        )
        
        if download_format != "Select Format" and 'days_data' in st.session_state and 'form_data' in st.session_state:
            if download_format == "Text (.txt)":
                filename = f"workout_plan_{timestamp}.txt"
                text_content = create_text_format(
                    st.session_state.days_data, 
                    st.session_state.form_data
                )
                st.download_button(
                    label="⬇️ Download Text File",
                    data=text_content,
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True,
                    key="download_text_btn"
                )
            
            elif download_format == "JSON (.json)":
                filename = f"workout_plan_{timestamp}.json"
                json_content = create_workout_json_output(
                    st.session_state.form_data,
                    st.session_state.days_data
                )
                st.download_button(
                    label="⬇️ Download JSON File",
                    data=json_content,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True,
                    key="download_json_btn"
                )
    
    with col2:
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.page = 'edit'
            st.rerun()
    
    with col3:
        if st.button("🆕 New Plan", use_container_width=True):
            # Clear session state
            for key in ['form_data', 'workout_plan', 'days_data', 'generation_time']:
                if key in st.session_state:
                    del st.session_state[key]
            st.session_state.page = 'form'
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display user profile summary
    if 'form_data' in st.session_state:
        user_data = st.session_state.form_data
        st.markdown(f"""
        <div class="form-section" style="margin-bottom: 2rem;">
            <h3 class="section-title">👤 Profile Summary</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div><strong>Name:</strong> {user_data.get('name', 'N/A')}</div>
                <div><strong>Age:</strong> {user_data['age']} years</div>
                <div><strong>Gender:</strong> {user_data['gender'].title()}</div>
                <div><strong>Goal:</strong> {user_data['goal']}</div>
                <div><strong>Fitness Level:</strong> {user_data['fitness_level']}</div>
                <div><strong>Training Days:</strong> {user_data.get('training_days_per_week', user_data.get('weekly_frequency', 3))} days/week</div>
                <div><strong>Duration:</strong> {user_data.get('session_duration', user_data.get('duration_per_session', 45))} min/session</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display workout plan
    if ('days_data' in st.session_state and st.session_state.days_data):
        display_professional_workout_plan(st.session_state.days_data)    
        # Weekly Calorie Summary
        total_weekly_calories = sum(
            sum(ex.get('calories_burned', 0) for ex in day['exercises'])
            for day in st.session_state.days_data
        )
        
        # Display success message with generation time
        if 'generation_time' in st.session_state:
            gen_time = st.session_state.generation_time
            st.markdown(f"""
            <div class="success-message">
                🎉 Workout plan generated successfully in {gen_time:.2f} seconds! Your personalized fitness journey starts here.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="success-message">
                🎉 Workout plan generated successfully! Your personalized fitness journey starts here.
            </div>
            """, unsafe_allow_html=True)
            
    else:
        st.error("❌ Could not parse the workout plan. Please try again.")
        with st.expander("View Raw Workout Plan"):
            st.text_area("Raw Workout Plan", value=st.session_state.workout_plan, height=400)
