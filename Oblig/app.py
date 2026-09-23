import streamlit as st

st.title("Welcome to Placeholder App")

st.text("Use sidebar menu to browse pages.")

user_input = st.text_input("Enter something")

if user_input:
    st.write(user_input)

