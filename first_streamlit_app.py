import streamlit as st

if __name__ == "__main__":
    print("START")
    st.title('My first app')
    st.write('Test text')
    print("MIDDLE")
    user_input = st.text_input("Enter your name", "DEFAULT")
    if user_input != "DEFAULT":
        st.write(user_input)