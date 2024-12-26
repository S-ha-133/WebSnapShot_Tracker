import os
import json
import streamlit as st
from datetime import datetime
from typing import List, Dict
import time
import openai 

# Assistant ID와 API Key 미리 정의
ASSISTANT_ID = 'asst_temp' # Assistant ID 추가 필요

client = openai.Client(api_key='sk-proj-temp)  # API 키 추가 필요


# 지정된 폴더에서 JSON 파일을 불러옴
def load_json_files_from_folder(folder_path: str) -> List[Dict]:
    json_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    json_files.append({'filename': file, 'data': json_data, 'path': file_path})
    return json_files

# JSON 파일을 비교하고 차이점 감지
def compare_json_files(json_files: List[Dict], compare_by: str = 'date') -> List[Dict]:
    comparisons = []
    sorted_files = sorted(json_files, key=lambda x: datetime.strptime(x['filename'].split('_')[0], '%Y%m%d'))
    
    for i in range(1, len(sorted_files)):
        previous_file = sorted_files[i - 1]
        current_file = sorted_files[i]
        
        prev_data = {f"{item['tag']}_{item['text'][:30]}": item for item in previous_file['data']}
        curr_data = {f"{item['tag']}_{item['text'][:30]}": item for item in current_file['data']}
        
        differences = []
        for key in curr_data:
            if key not in prev_data:
                differences.append({'change_type': 'added', 'data': curr_data[key]})
        for key in prev_data:
            if key not in curr_data:
                differences.append({'change_type': 'removed', 'data': prev_data[key]})
        
        comparison_result = {
            'date': current_file['filename'].split('_')[0],
            'previous_file': previous_file['filename'],
            'current_file': current_file['filename'],
            'differences': differences[:22]  # 데이터 크기 제한
        }
        comparisons.append(comparison_result)
    
    return comparisons

# GPT 어시스턴트에 비교 데이터를 전송하고 상호작용
conversation_history = []

def send_to_gpt_assistant(comparison_data: List[Dict], analysis_request: str):
    try:
        thread = client.beta.threads.create()
        content = {
            "comparisons": comparison_data,
            "analysis_request": analysis_request
        }
        conversation_history.append({"role": "user", "content": analysis_request})
        
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=json.dumps(content)  # 내용을 JSON 문자열로 변환
        )
        for attempt in range(5):  # 재시도 메커니즘
            run = client.beta.threads.runs.create_and_poll(
                thread_id=thread.id,
                assistant_id=ASSISTANT_ID,
            )
            if run.status == 'completed':
                messages = client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                response = messages.data[0].content[0].text.value
                conversation_history.append({"role": "assistant", "content": response})
                return response
            else:
                time.sleep(2)  # 재시도 간 대기 시간 증가
                print(f"Attempt {attempt + 1}: Run Status - {run.status}, Reason: {run}")
        return {"error": "Run did not complete successfully after multiple attempts."}
    except Exception as e:
        st.error(f"Error: {str(e)}") 
        return {"error": str(e)}

def main():
    st.title("Web Change Analyzer")

    uploaded_folder = st.file_uploader("Upload JSON files", type='json', accept_multiple_files=True)

    if uploaded_folder:
        temp_dir = 'uploaded_files'
        os.makedirs(temp_dir, exist_ok=True)

        for uploaded_file in uploaded_folder:
            with open(os.path.join(temp_dir, uploaded_file.name), 'wb') as f:
                f.write(uploaded_file.getbuffer())

        json_files = load_json_files_from_folder(temp_dir)
        if "messages" not in st.session_state.keys():
            st.session_state.messages = [
                {"role": "assistant", "content": "Loaded JSON files for analysis. How can I assist you today?"}
            ]


        comparisons = compare_json_files(json_files)
        st.session_state.messages.append({"role": "system", "content": f"Loaded {len(json_files)} JSON files for analysis."})
        for comparison in comparisons:
            st.session_state.messages.append({"role": "system", "content": f"Date: {comparison['date']}"})

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        if prompt := st.chat_input("Enter your analysis request:"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            st.write("### Assistant is working on your request... ⏳")
            response = send_to_gpt_assistant(comparisons, prompt)
            if isinstance(response, dict) and 'error' in response:
                with st.chat_message("assistant"):
                    st.error(response['error'])
            else:
                message = {"role": "assistant", "content": response}
                st.session_state.messages.append(message)
                with st.chat_message("assistant"):
                    st.write(response)

    st.info("Ensure your JSON files are stored in date-stamped folders for accurate comparison.")

if __name__ == "__main__":
    main()
