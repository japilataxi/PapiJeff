import streamlit as st
import requests

st.set_page_config(page_title="Análisis de Documentos con IA", layout="wide")
st.title("📄 Análisis de Documentos con IA")

# Subida de archivos
uploaded_file = st.file_uploader("Sube un archivo", type=["pdf", "xlsx", "csv", "html"])

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
    response = requests.post("http://localhost:8080/upload/", files=files)

    if response.status_code == 200:
        data = response.json()
        st.session_state["chunks"] = data["chunks"]
        st.success(f"Archivo '{data['filename']}' cargado correctamente.")
    else:
        st.error(f"Error: {response.json().get('detail')}")

# Chat interactivo
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Haz una pregunta sobre el archivo cargado"):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        chunks = st.session_state.get("chunks", [])
        relevant_text = " ".join(chunks[:3])  # Tomar los primeros 3 fragmentos

        response = requests.post("http://localhost:8080/analyze/", json={"text": relevant_text})

        if response.status_code == 200:
            ai_response = response.json()["response"]
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        else:
            st.error(f"Error en IA: {response.json().get('detail')}")
