import os
from flask import Flask, render_template, send_from_directory,request,redirect,flash

app = Flask(__name__)
PDF_FOLDER = os.path.join('static')
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/',methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        # file = request.files['file']
        # file.save(f"static/{file.filename}")
        if 'files' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files')
        if not files or all(file.filename == '' for file in files):
            flash('No files selected')
            return redirect(request.url)

        uploaded = 0
        for file in files:
            if file :
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                uploaded += 1

        if uploaded:
            flash(f'{uploaded} file(s) successfully uploaded')
        else:
            flash('No valid files uploaded')

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
