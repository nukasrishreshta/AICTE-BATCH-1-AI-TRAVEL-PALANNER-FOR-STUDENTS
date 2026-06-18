import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image

# =====================================================================
# 1. AI GENERATIVE CORE CONFIGURATION
# =====================================================================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found. Please set it as a secret in Streamlit Cloud.")
    st.stop()
genai.configure(api_key=GOOGLE_API_KEY)

def call_gemini_ai(prompt_text, raw_image=None):
    model = genai.GenerativeModel('gemini-2.5-flash')
    payload = [prompt_text]

    if raw_image is not None:
        image_bytes = raw_image.getvalue()
        formatted_image = [{
            "mime_type": raw_image.type,
            "data": image_bytes
        }]
        payload.extend(formatted_image)

    try:
        ai_response = model.generate_content(payload)
        return ai_response.text
    except Exception as error_message:
        return f"AI Server Busy: {str(error_message)}"

# =====================================================================
# 2. SITE GLOBAL CONTAINER STRUCTURE
# =====================================================================
st.set_page_config(page_title="WanderStudent AI", layout="wide")

st.title("🎒 WanderStudent: AI Travel Workspace")
st.markdown("##### *Smart, personalized, and budget-optimized trip routing designed specifically for students.*")
st.write("---")

# Initialize global session variables if missing
if 'budget_tier' not in st.session_state:
    st.session_state.budget_tier = "Backpacker Level (Budget Street Food)"
if 'student_hobbies' not in st.session_state:
    st.session_state.student_hobbies = "Exploring, Local Sights, Parks"
if 'vehicle_preference' not in st.session_state:
    st.session_state.vehicle_preference = "Public Transport (Trains & Local Buses)"

# =====================================================================
# 3. GLOBAL PROFILE SIDEBAR (Applies Choices Automatically to All Tabs)
# =====================================================================
with st.sidebar:
    st.header("🪪 Student Travel Profile")
    st.write("Set your baseline rules here. The AI tabs on the right dynamically adjust to these configurations.")

    selected_budget = st.selectbox(
        "My Spending Baseline:",
        ["Low Level (Hotels & Street Food)", "Medium Level (Budget Street Food & small Restaurants)", "High Level (Cafes & Restaurants)"]
    )
    written_hobbies = st.text_input("My Primary Hobbies:", value=st.session_state.student_hobbies)

    # NEW FEATURE: Asked once globally, saving user input hassle inside individual tabs!
    chosen_vehicle = st.selectbox(
        "Preferred Transport Mode:",
        ["Public Transport (Trains & Local Buses)", "Budget Car Rental / Self-Drive", "Two-Wheeler / Scooter Riding", "Walking / Hitchhiking Friendly"]
    )

    if st.button("Lock Student Travel Profile"):
        st.session_state.budget_tier = selected_budget
        st.session_state.student_hobbies = written_hobbies
        st.session_state.vehicle_preference = chosen_vehicle
        st.success("Global constraints active!")

    st.write("---")
    st.markdown("### 📋 Active Constraints Snapshot:")
    st.caption(f"💰 **Budget:** {st.session_state.budget_tier}")
    st.caption(f"🎨 **Interests:** {st.session_state.student_hobbies}")
    st.caption(f"🚌 **Vehicle Mode:** {st.session_state.vehicle_preference}")

# =====================================================================
# 4. MULTI-TAB WORKSPACE
# =====================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ 1. Budget Planner",
    "📸 2. Photo Explorer",
    "🛣️ 3. Route & Weather Planner",
    "👥 4. Group Trip Matcher"
])

# ---------------------------------------------------------------------
# TAB 1: BUDGET PLANNER
# ---------------------------------------------------------------------
with tab1:
    st.image("https://images.unsplash.com/photo-1501555088652-021faa106b9b?auto=format&fit=crop&w=1200&q=80",
             caption="Plan custom itineraries tailored around your global transport rules.", use_container_width=True)

    st.header("🗺️ Customized Destination Itinerary Builder")

    col1, col2 = st.columns(2)
    with col1:
        target_city = st.text_input("Where are you traveling to?", placeholder="e.g., Kyoto, Prague, Paris", key="t1_city")
    with col2:
        trip_days = st.slider("How many days will you stay?", min_value=1, max_value=20, value=3, key="t1_days")

    extra_wishes = st.text_area("Any specific custom timeline requests?", placeholder="e.g., 'Looking for free museum entry hours on day 1'", key="t1_wishes")

    if st.button(" Create My Pocket Guide", key="t1_btn"):
        if not target_city:
            st.error("Please enter a destination city name to run the planner engine!")
        else:
            with st.spinner("✨ Mapping out your itinerary data..."):
                prompt = f"""
                Act as a friendly student tour manager. Create a fun {trip_days}-day budget travel plan for {target_city}.
                Take into account these global user configurations:
                - Spending Profile: {st.session_state.budget_tier}
                - Interests: {st.session_state.student_hobbies}
                - Preferred Vehicle/Transit Mode: {st.session_state.vehicle_preference}
                - Custom requirements: {extra_wishes if extra_wishes else "None"}

                Format beautifully using conversational language, markdown headers, and fun emojis. Ensure travel suggestions prioritize their vehicle preference!
                """
                output = call_gemini_ai(prompt)
                st.success("Your itinerary layout template is complete!")
                st.markdown(output)

# ---------------------------------------------------------------------
# TAB 2: PHOTO EXPLORER
# ---------------------------------------------------------------------
with tab2:
    st.image("https://images.unsplash.com/photo-1452626038306-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80",
             caption="Snap a photograph to safely calculate route parameters and nearby activities.", use_container_width=True)

    st.header("📸 Smart Camera Lens & Sight Identifier")

    col1, col2 = st.columns(2)
    with col1:
        user_location = st.text_input("Your Current Location (City/Country):", placeholder="e.g., New Delhi, India")
        uploaded_pic = st.file_uploader("Upload an image of a landmark, historical marker, or ticket:", type=["jpg", "png", "jpeg"])
    with col2:
        if uploaded_pic is not None:
            st.image(Image.open(uploaded_pic), caption="Uploaded File Preview", width=320)

    if st.button(" Run Intelligent Visual Scan", key="t2_btn"):
        if not uploaded_pic or not user_location:
            st.error("Please ensure you have uploaded an image file and filled out your current location city!")
        else:
            with st.spinner("Decoding image structures..."):
                vision_prompt = f"""
                Analyze this photo carefully.
                1. Identify the name of this place/landmark.
                2. List interesting historical details or locations students can explore around it.
                3. Name famous local items (must-try local dishes, budget souvenirs, unique items).
                4. Estimate the approximate travel distance from the user's location ({user_location}) to this destination. Give explicit advice on how to navigate this journey using their preferred vehicle choice: {st.session_state.vehicle_preference}.
                """
                vision_result = call_gemini_ai(vision_prompt, uploaded_pic)
                st.write("---")
                st.subheader("📋 Photo Analysis Results")
                st.markdown(vision_result)

# ---------------------------------------------------------------------
# TAB 3: ROUTE & WEATHER PLANNER
# ---------------------------------------------------------------------
with tab3:
    st.image("https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?auto=format&fit=crop&w=1200&q=80",
             caption="Analyze open roads, pitstop milestones, and local seasonal trends.", use_container_width=True)

    st.header("🛣️ Smart Route Explorer & Logistics Roadmap")

    col1, col2 = st.columns(2)
    with col1:
        start_loc = st.text_input("Starting Point City:", placeholder="e.g., Mumbai", key="t3_start")
        end_loc = st.text_input("Destination City:", placeholder="e.g., Goa", key="t3_end")
    with col2:
        travel_month = st.selectbox("When are you heading out?", ["January - March", "April - June", "July - September", "October - December"], key="t3_month")

    if st.button("🗺️ Map Out My Route Logistics", key="t3_btn"):
        if not start_loc or not end_loc:
            st.error("Please supply both a valid starting point and destination city layout!")
        else:
            with st.spinner("Compiling cross-route parameters..."):
                route_prompt = f"""
                Design a student roadmap from {start_loc} to {end_loc} matching a timeline during {travel_month}.
                The user's preferred method of transit is: {st.session_state.vehicle_preference}.

                Please split your output cleanly across these target areas:

                📍 ROAD TRIP DETOURS & INTERESTING SIGHTS
                Suggest 2 or 3 fun roadside attractions or scenic outlook stops optimized for someone traveling by {st.session_state.vehicle_preference}.

                🌤️ CLIMATE TRENDS & WEATHER FORECAST INTEGRATION
                Provide an overview of historical weather conditions for this path during {travel_month} and specify packing gear requirements.

                🏨 STUDENT BUDGET HOTEL & HOSTEL RECOMMENDATIONS
                Provide 3 highly rated, cheap student accommodations along or at the end of the route.

                🚌 TRANSIT HACKS & LOGISTIC SUGGESTIONS
                Provide money-saving tricks specific to utilizing {st.session_state.vehicle_preference} across this route.
                """
                route_result = call_gemini_ai(route_prompt)
                st.write("---")
                st.markdown(route_result)

# ---------------------------------------------------------------------
# TAB 4: GROUP TRIP MATCHER
# ---------------------------------------------------------------------
with tab4:
    st.image("https://images.unsplash.com/photo-1539635278303-d4002c07eae3?auto=format&fit=crop&w=1200&q=80",
             caption="Tailor unique group adventures with smart budget distribution tracking.", use_container_width=True)

    st.header("👥 Group Trip Dynamic Matcher")

    col1, col2 = st.columns(2)
    with col1:
        # User Choice: Friends vs Parents
        group_type = st.radio("Who is joining you on this trip?", ["Traveling with Friends 🎒🔥", "Traveling with Parents & Family 👨‍👩‍👧‍👦❤️"])

        # NEW FEATURE: Dynamic group member size selector
        num_people = st.number_input("Number of Group Travelers:", min_value=1, max_value=50, value=4, step=1)

    with col2:
        max_total_budget = st.text_input("Estimated Budget Cap per Person:", placeholder="e.g., ₹5000 / $150")
        group_vibe = st.text_input("What is the preferred vacation style?", placeholder="e.g., Relaxing beach holiday, historic walk, hiking")

    if st.button("✨ Match Best Group Trip", key="t4_btn"):
        with st.spinner("Evaluating matching group itineraries..."):
            group_prompt = f"""
            You are a youth travel expert. Suggest 2 highly relevant destination trip packages matching these parameters:
            - Travel Dynamics: {group_type}
            - Group Size: {num_people} travelers
            - Target Budget per Individual: {max_total_budget}
            - Style Theme/Vibe: {group_vibe}
            - Preferred Shared Vehicle Style: {st.session_state.vehicle_preference}

            Tailor the recommendation context perfectly to the group type:
            - If with friends: Suggest group discount activities, lively student hostels, and affordable transport grouping based on {st.session_state.vehicle_preference}.
            - If with parents: Emphasize comfort, well-guided walking routes, accessible and clean dining spots, and practical travel pace adjustments for a group of {num_people} people.
            """
            group_result = call_gemini_ai(group_prompt)
            st.write("---")
            st.success("Group package recommendations finalized!")
            st.markdown(group_result)
