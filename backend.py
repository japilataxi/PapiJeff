from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import PyPDF2
from bs4 import BeautifulSoup
from utils import split_text_into_chunks
from dotenv import load_dotenv
from groq import Groq

app = FastAPI()
load_dotenv()

# Cliente de Groq
qclient = Groq()

def extract_text_from_pdf(file):
    """Extrae texto de un archivo PDF"""
    reader = PyPDF2.PdfReader(file)
    text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    return text

def extract_text_from_xlsx(file):
    """Extrae texto de un archivo XLSX"""
    df = pd.read_excel(file)
    return "\n".join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))

def extract_text_from_csv(file):
    """Extrae texto de un archivo CSV"""
    df = pd.read_csv(file)
    return "\n".join(df.astype(str).apply(lambda x: ' '.join(x), axis=1))

def extract_text_from_html(file):
    """Extrae texto de un archivo HTML"""
    content = file.read().decode("utf-8")
    soup = BeautifulSoup(content, "html.parser")
    return soup.get_text(separator="\n")

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    """Recibe un archivo y extrae su texto"""
    try:
        if file.filename.endswith(".pdf"):
            text = extract_text_from_pdf(file.file)
        elif file.filename.endswith(".xlsx"):
            text = extract_text_from_xlsx(file.file)
        elif file.filename.endswith(".csv"):
            text = extract_text_from_csv(file.file)
        elif file.filename.endswith(".html"):
            text = extract_text_from_html(file.file)
        else:
            raise HTTPException(status_code=400, detail="Formato no soportado")

        chunks = split_text_into_chunks(text)
        return {"filename": file.filename, "chunks": chunks}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el archivo: {str(e)}")

@app.post("/analyze/")
async def analyze_text(data: dict):
    """Analiza el texto con Groq AI"""
    text = data.get("text", "")

    if not text:
        raise HTTPException(status_code=400, detail="No se recibió texto")

    response = qclient.chat.completions.create(
        messages=[
                    {"role": "system", "content": "Responde siempre en español de acuerdo a lo que te pregunte el usuario exactamente."},
                    {"role": "user", "content": text}
                ],
        #model="llama-3.3-70b-specdec",
        model="mixtral-8x7b-32768",
        stream=False
    )

    return {"response": response.choices[0].message.content}
