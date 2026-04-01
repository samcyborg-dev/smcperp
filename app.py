import streamlit as st

st.set_page_config(layout="wide")

st.title("🚀 CYBORG TEST - LIVE")

st.header("✅ APP WORKING")

col1, col2 = st.columns(2)
with col1:
    st.metric("Status", "LIVE")
with col2:
    if st.button("🔥 Test Button"):
        st.balloons()
        st.success("Button Works!")

st.markdown("---")
st.caption("*Minimal test passed. Now upgrade to full OrderBlock Cyborg*")
