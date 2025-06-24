import glob
import os

# sqlite rh bug
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')


from flask import Flask
from flask_cors import CORS
from flask import request
from datetime import datetime

from langchain_text_splitters import TokenTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, UnstructuredFileLoader, CSVLoader
)

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route("/")
def home():
    return "REST API"


@app.route("/context", methods=["POST"])
def context_endpoint():
    if request.method == "POST":
        if "file" not in request.files:
            return {"context": "", "error": "Brak pliku", "fileName": ""}

        file = request.files["file"]
        query = request.form.get('query')
        new_file = request.form.get('new_file')
        old_file_name = request.form.get('old_file_name')
        print("new_file", new_file)
        print("old_file_name", old_file_name)
        if not file:
            return {"context": "", "error": "Błędny plik", "fileName": ""}
        
        if new_file=="true":
            file.filename = "file_" + datetime.now().strftime("%y%m%d-%H%M%S") + ".pdf"
            filename = file.filename

            print("Nazwa pliku: ", filename)
            file_path = "./pliki/" + filename

            file.save(os.path.join(file_path))
            print(file_path)
            # Save data and pages of document with found data

            context = get_context(file_path, query)
            return {
                "context": context,
                "error": "",
                "fileName": filename
            }
        else:
            file_path = "./pliki/" + old_file_name
            context = get_context(file_path, query)
            return {
                "context": context,
                "error": "",
                "fileName": old_file_name
            }
        
    return {"context": "", "error": "Błąd", "fileName": ""}

def get_context(file, query):
    # load the document and split it into chunks
    loader = PyPDFLoader(os.path.join(file))
        
    documents = loader.load()
    
    # split it into chunks
    text_splitter = TokenTextSplitter(chunk_size=150, chunk_overlap=20)
    docs = text_splitter.split_documents(documents)

    # create the open-source embedding function
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # load docs into Chroma DB
    db = Chroma.from_documents(docs, embedding_function, persist_directory="./db-docs")
    results = db.similarity_search(query, k=1)
    db.delete_collection()
    db.persist()  # Saves the empty state
    print(results)
    context=results[0].page_content
    print(context)
    return context

# Get the PORT from environment
port = os.getenv('PORT', '8080')
debug = os.getenv('DEBUG', 'false')

if __name__ == "__main__":
    print("application ready - Debug is " + str(debug))
    app.run(host='0.0.0.0', port=int(port))