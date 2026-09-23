import streamlit as st

st.title("Placeholder")

user_input = st.text_input("Enter something")

if user_input:
    st.write(user_input)

