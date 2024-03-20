import sys
import os
from openai import OpenAI
from services.pdf_processor import extract_text_from_pdf
from services.vectordb import chroma_client
import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from services.list_merge import merge_lists
from services.chat_completion import chat_response

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
openai_lc_client = None  # Global variable to hold the Chroma client
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Route 1 to upload the pdf files
@app.route('/upload', methods=['POST'])
def upload_file():
    global openai_lc_client
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('file')  # Retrieve a list of files

    texts = []  # List to hold extracted texts from all PDFs
    for file in files:
        # Check each file for validity
        if file.filename == '':
            continue  # Skip empty filenames, could also return an error
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            texts.append(text)  # Add extracted text to the list

    if not texts:  # Check if no valid PDFs were processed
        return jsonify({'error': 'No valid PDFs were uploaded'}), 400
    texts_m = merge_lists(texts)
    openai_lc_client = chroma_client(texts=texts_m)
    return jsonify({'result': 'Chromadb client has been established'})


# Route 2 to get answer of the asked query
@app.route('/query', methods=['POST'])
def query():
    global openai_lc_client
    if not openai_lc_client:
        return jsonify({'error': 'The Chroma database client is not initialized.'}), 400

    query_text = request.json.get('query')
    if not query_text:
        return jsonify({'error': 'No query provided.'}), 400
    
    docs = openai_lc_client.similarity_search(query_text,k=10)
    context = [result.page_content for result in docs]
    parent_directory = os.path.dirname(os.getcwd())
    path = os.path.join(parent_directory, "PROMPT.txt")

    with open(path, 'r') as file:
        PROMPT = file.read().replace('\n', '')
    PROMPT  =PROMPT.format("\n".join(context), query_text)
                
    response = chat_response(model='gpt-4',PROMPT=PROMPT)
    
    return jsonify({"response": response})


@app.route('/info', methods=['GET'])
def info():
    global openai_lc_client
    if not openai_lc_client:
        return jsonify({'error': 'The Chroma database client is not initialized.'}), 400
    
    parent_directory = os.path.dirname(os.getcwd())
    path = os.path.join(parent_directory, "PROMPT2.txt")

    with open(path, 'r') as file:
        PROMPT2 = file.read().replace('\n', '')

    docs = openai_lc_client.similarity_search(PROMPT2,k=10)
    context = [result.page_content for result in docs]
    PROMPT2  =PROMPT2.format("\n".join(context))

    response = chat_response(model='gpt-4',PROMPT=PROMPT2)
    
    return jsonify({"response": response})



if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
