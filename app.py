import os
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'static'
THUMB_FOLDER = os.path.join('static', 'thumbs')
os.makedirs(THUMB_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def generate_thumbnail(pdf_filename):
    thumb_path = os.path.join(THUMB_FOLDER, f"{pdf_filename}.png")
    if not os.path.exists(thumb_path):
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)
        try:
            pages = convert_from_path(pdf_path, first_page=1, last_page=1, size=(200, 260))
            pages[0].save(thumb_path, 'PNG')
        except Exception as e:
            print(f"Error generating thumbnail for {pdf_filename}: {e}")
            return 'default_cover.png'
    return f'thumbs/{pdf_filename}.png'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('No file part')
            return redirect(request.url)

        files = request.files.getlist('files')
        uploaded = 0
        for file in files:
            if file and file.filename.lower().endswith('.pdf'):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                generate_thumbnail(filename)
                uploaded += 1

        if uploaded:
            flash(f'{uploaded} file(s) successfully uploaded')
        else:
            flash('No valid files uploaded')

    return render_template('index.html')

@app.route('/viewer')
def viewer():
    pdf_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.pdf')]
    thumbs = {pdf: generate_thumbnail(pdf) for pdf in pdf_files}
    return render_template('viewer.html', pdfs=pdf_files, thumbs=thumbs)

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4900, debug=True)
