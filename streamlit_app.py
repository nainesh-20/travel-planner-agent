import streamlit as st
import asyncio
import os
from datetime import datetime, timedelta

# ---------------------------------------------------------
# 🔧 Environment Setup for Streamlit Cloud
# ---------------------------------------------------------
# Load keys from Streamlit secrets if available (for production)
if "GOOGLE_API_KEY" in st.secrets:
    os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

if "SERP_API_KEY" in st.secrets:
    os.environ["SERP_API_KEY"] = st.secrets["SERP_API_KEY"]

# Import backend logic directly (Monolithic Approach for easier deployment)
try:
    from gemini2_travel_v2 import (
        complete_travel_search,
        search_flights_endpoint,
        search_hotels_endpoint,
        FlightRequest,
        HotelRequest,
    )
except ImportError:
    st.error("Could not import backend logic. Ensure 'gemini2_travel_v2.py' is in the same directory.")
    st.stop()


# ---------------------------------------------------------
# 🎨 UI Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="✈️ AI-Powered Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
with st.sidebar:
    st.title("⚙️ Options")
    search_mode = st.radio(
        "Search Mode",
        ["Complete (Flights + Hotels + Itinerary)", "Flights Only", "Hotels Only"]
    )
    st.markdown("---")
    st.caption("AI-Powered Travel Planner v2.0")
    st.caption("© 2025 Travel AI Solutions")

# Main Header
st.title("✈️ AI-Powered Travel Planner")
st.markdown("""
    **Find flights, hotels, and get personalized recommendations with AI! Create your perfect travel itinerary in seconds.**
""")


# ---------------------------------------------------------
# 📝 Input Form
# ---------------------------------------------------------
with st.form(key="travel_search_form"):
    cols = st.columns([1, 1])

    with cols[0]:
        st.subheader("🛫 Flight Details")
        origin = st.text_input("Departure Airport (IATA code)", "ATL")
        destination = st.text_input("Arrival Airport (IATA code)", "LAX")

        tomorrow = datetime.now() + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7)
        outbound_date = st.date_input("Departure Date", tomorrow)
        return_date = st.date_input("Return Date", next_week)

    with cols[1]:
        st.subheader("🏨 Hotel Details")
        use_flight_destination = st.checkbox("Use flight destination for hotel", value=True)
        
        if use_flight_destination:
            location = destination
            st.info(f"Using flight destination ({destination}) for hotel search")
        else:
            location = st.text_input("Hotel Location", "")

        check_in_date = st.date_input("Check-In Date", outbound_date)
        check_out_date = st.date_input("Check-Out Date", return_date)

    submit_col1, submit_col2 = st.columns([3, 1])
    with submit_col2:
        submit_button = st.form_submit_button("🔍 Search", use_container_width=True)


# ---------------------------------------------------------
# 🚀 Search Implementation
# ---------------------------------------------------------
async def run_search():
    # Construct Request Objects
    flight_req = FlightRequest(
        origin=origin,
        destination=destination,
        outbound_date=str(outbound_date),
        return_date=str(return_date)
    )
    
    hotel_req = HotelRequest(
        location=location,
        check_in_date=str(check_in_date),
        check_out_date=str(check_out_date)
    )

    result = None
    
    try:
        if search_mode == "Complete (Flights + Hotels + Itinerary)":
            # Call backend function directly
            result = await complete_travel_search(flight_request=flight_req, hotel_request=hotel_req)
        
        elif search_mode == "Flights Only":
            result = await search_flights_endpoint(flight_request=flight_req)
            
        elif search_mode == "Hotels Only":
            result = await search_hotels_endpoint(hotel_request=hotel_req)
            
        return result

    except Exception as e:
        st.error(f"Search failed: {str(e)}")
        return None

if submit_button:
    # Validation
    if not origin or not destination:
        st.error("Please provide origin and destination.")
    else:
        with st.spinner("🤖 AI Agents are planning your trip... (Searching Flights, Hotels & Generating Itinerary)"):
            # Run Async Search
            search_result = asyncio.run(run_search())

        if search_result:
            # ---------------------------------------------------------
            # 📊 Display Results
            # ---------------------------------------------------------
            
            # Determine appropriate tabs
            if search_mode == "Flights Only":
                tabs = st.tabs(["✈️ Flights", "🏆 AI Recommendation"])
            elif search_mode == "Hotels Only":
                tabs = st.tabs(["🏨 Hotels", "🏆 AI Recommendation"])
            else:
                tabs = st.tabs(["✈️ Flights", "🏨 Hotels", "🏆 AI Recommendations", "📅 Itinerary"])

            # 1. Flights Tab
            if search_mode != "Hotels Only":
                with tabs[0]:
                    st.subheader(f"Flight Options ({len(search_result.flights)})")
                    if search_result.flights:
                        cols = st.columns(2)
                        for i, flight in enumerate(search_result.flights):
                            with cols[i % 2].container(border=True):
                                st.markdown(f"""
                                **{flight.airline}**  
                                💰 **${flight.price}** | ⏱️ {flight.duration} | {flight.stops}  
                                🛫 {flight.departure}  
                                🛬 {flight.arrival}
                                """)
                    else:
                        st.info("No flights found.")

            # 2. Hotels Tab
            if search_mode != "Flights Only":
                tab_idx = 1 if search_mode == "Complete (Flights + Hotels + Itinerary)" else 0
                with tabs[tab_idx]:
                    st.subheader(f"Hotel Options ({len(search_result.hotels)})")
                    if search_result.hotels:
                        cols = st.columns(3)
                        for i, hotel in enumerate(search_result.hotels):
                            with cols[i % 3].container(border=True):
                                st.markdown(f"""
                                **{hotel.name}**  
                                💰 {hotel.price} | ⭐ {hotel.rating}  
                                📍 {hotel.location}
                                """)
                                st.link_button("View Deal", hotel.link)
                    else:
                        st.info("No hotels found.")

            # 3. AI Recommendations Tab
            rec_tab_idx = 1 if search_mode != "Complete (Flights + Hotels + Itinerary)" else 2
            with tabs[rec_tab_idx]:
                if search_mode != "Hotels Only":
                    with st.expander("✈️ AI Flight Analysis", expanded=True):
                        st.markdown(search_result.ai_flight_recommendation)
                
                if search_mode != "Flights Only":
                    with st.expander("🏨 AI Hotel Analysis", expanded=True):
                        st.markdown(search_result.ai_hotel_recommendation)

            # 4. Itinerary Tab
            if search_mode == "Complete (Flights + Hotels + Itinerary)":
                with tabs[3]:
                    st.subheader("📅 Your AI-Generated Itinerary")
                    st.markdown(search_result.itinerary)
                    
                    st.download_button(
                        "📥 Download Itinerary",
                        search_result.itinerary,
                        file_name="itinerary.md"
                    )
