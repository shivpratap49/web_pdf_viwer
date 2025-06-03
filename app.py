import os
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)
PDF_FOLDER = os.path.join('static')

@app.route('/')
def index():

    # List all PDFs in the static/ directory
    pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith('.pdf')]
    return render_template('index.html', pdfs=pdf_files)

@app.route('/view/<filename>')
def view_pdf(filename):
    # Render the PDF in viewer.html
    return render_template('viewer.html', filename=filename)

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    # Serve the PDF file directly
    return send_from_directory(PDF_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
