import streamlit as st
from backend.background import set_background

st.set_page_config(
    page_title="Multipage App",
    page_icon="👋",
)

set_background(r'C:\Users\LUCAS\Documents\GitHub\LMM-site\fig\clounds.png')

st.title("Laboratório de Meteorologia de Mesoescala - LMM")
st.sidebar.success("Select a page above.")

if "my_input" not in st.session_state:
    st.session_state["my_input"] = ""

my_input = st.text_input("Input a text here", st.session_state["my_input"])
submit = st.button("Submit")
if submit:
    st.session_state["my_input"] = my_input
    st.write("You have entered: ", my_input)