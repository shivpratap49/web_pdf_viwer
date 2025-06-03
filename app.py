import os
from flask import Flask, render_template, send_from_directory,request

app = Flask(__name__)
PDF_FOLDER = os.path.join('static')

@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        file = request.files['file']
        file.save(f"static/{file.filename}")

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
    app.run(host='0.0.0.0',port=4900,debug=True)
