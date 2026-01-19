import streamlit as st
import requests

# Backend URL
API_URL = "http://localhost:8000"

st.set_page_config(page_title="Revit Context Matcher", layout="wide")
st.title("🏗️ Revit Context Search")

# Create Tabs
tab_search, tab_upload, tab_library = st.tabs(["🔍 Search Detail", "➕ Add to Knowledge", "📚 Database"])

# ==========================================
# TAB 1: SEARCH (Free Text Input)
# ==========================================
with tab_search:
    st.subheader("Input Context")
    st.caption("Type the element data exactly as it appears in Revit properties.")

    # 3 Columns for inputs
    col1, col2, col3 = st.columns(3)

    with col1:
        host = st.text_input("Host Element", placeholder="e.g., Core-Shaft")

    with col2:
        adj = st.text_input("Adjacent Element", placeholder="e.g., Concrete Slab")

    with col3:
        exp = st.text_input("Exposure", placeholder="e.g., Exterior")

    # Search Action
    if st.button("Find Suggested Detail", type="primary"):
        # Basic validation: Ensure at least Host is typed
        if not host:
            st.warning("Please enter at least a Host Element.")
        else:
            payload = {
                "host_element": host,
                "adjacent_element": adj,
                "exposure": exp
            }

            try:
                with st.spinner("Analyzing context..."):
                    res = requests.post(f"{API_URL}/search", json=payload)

                if res.status_code == 200:
                    data = res.json()

                    st.divider()

                    if data['suggested_detail'] != "None":
                        # Success State
                        st.success(f"**Suggestion:** {data['suggested_detail']}")

                        # Visual Confidence Meter
                        score = data['confidence']
                        st.progress(score, text=f"Confidence Score: {int(score * 100)}%")

                        # Reasoning
                        st.info(f"**Logic:** {data['reason']}")
                    else:
                        # Not Found State
                        st.warning("No suitable detail found in the database.")
                        st.caption(f"Analysis: {data['reason']}")
                else:
                    st.error(f"Server returned error: {res.status_code}")

            except requests.exceptions.ConnectionError:
                st.error("Could not connect to Backend. Is 'python -m backend.main' running?")

# ==========================================
# TAB 2: UPLOAD (Training)
# ==========================================
with tab_upload:
    st.subheader("Expand the Algorithm")
    st.markdown("Add a new standard detail string. The system will automatically learn keywords from it.")

    with st.form("upload_form"):
        new_detail = st.text_input("Detail Name", placeholder="e.g., Basement Retaining Wall to Foundation Waterproofing")
        submitted = st.form_submit_button("Upload Detail")

        if submitted:
            if new_detail:
                try:
                    res = requests.post(f"{API_URL}/upload", json={"detail_name": new_detail})
                    if res.status_code == 200:
                        st.success(f"Success: {res.json()['message']}")
                    else:
                        st.error("Upload failed.")
                except:
                    st.error("Backend connection failed.")
            else:
                st.warning("Please type a detail name.")

# ==========================================
# TAB 3: LIBRARY (View Data)
# ==========================================
with tab_library:
    st.subheader("Current Knowledge Base")

    col_a, col_b = st.columns([1, 5])
    with col_a:
        if st.button("Refresh List"):
            st.rerun()

    try:
        res = requests.get(f"{API_URL}/list")
        if res.status_code == 200:
            items = res.json()
            if len(items) == 0:
                st.info("Database is empty.")

            for i, item in enumerate(items):
                # Using a container for better layout
                with st.container():
                    c1, c2 = st.columns([6, 1])
                    c1.markdown(f"**{i+1}.** `{item}`")
                    if c2.button("Delete", key=f"del_{i}"):
                        requests.delete(f"{API_URL}/delete", params={"detail_name": item})
                        st.rerun()
                    st.divider()
        else:
            st.error("Failed to fetch list.")
    except:
        st.error("Backend connection failed.")