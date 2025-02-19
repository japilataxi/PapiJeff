def split_text_into_chunks(text, chunk_size=500, overlap=50):
    """Divide el texto en fragmentos con solapamiento"""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks
