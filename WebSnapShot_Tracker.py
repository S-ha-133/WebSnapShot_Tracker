import streamlit as st
import os
import subprocess

# Screenshot Saver와 Web Change Analyzer 가져오기
import Screenshot_Saver
import Web_Change_Analyzer

def main():
    st.title("Web Tool: Screenshot Saver and Change Analyzer")  # 앱 타이틀 수정 필요

    st.write("Select an option to proceed:") 
    option = st.radio("What would you like to do?", ("Take full-page screenshots", "Analyze page changes"))  # 라디오 버튼을 통한 기능 선택

    if option == "Take full-page screenshots":
        st.write("You chose to take full-page screenshots of websites.") 
        Screenshot_Saver.main() 
    elif option == "Analyze page changes":
        st.write("You chose to analyze changes between JSON page data.")
        Web_Change_Analyzer.main() 

if __name__ == "__main__":
    main() 
