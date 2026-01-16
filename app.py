import os
from flask import Flask, render_template, request, redirect, flash, send_from_directory, url_for,make_response
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from google.cloud import storage  
import datetime
from google.oauth2 import service_account
import google.auth
from google.auth.transport.requests import Request
import time

_thumb_cache = {}
_THUMB_CACHE_TTL = 3600 


app = Flask(__name__)
app.secret_key = 'your_secret_key'

creds = service_account.Credentials.from_service_account_file(
    "service-account.json"
)

client = storage.Client(credentials=creds, project=creds.project_id)

def pdf_list():
    
    bucket=client.bucket('online_library_app')
    blobs=blobs = client.list_blobs(bucket)
    list_pdf={}
    for blob in blobs:
        sm_dict=dict()
        sm_dict['pdf_url']=blob.generate_signed_url(
            version="v4",
            expiration=datetime.timedelta(hours=1),
            method="GET",
         response_disposition='inline'
        )
        list_pdf[blob.name]=sm_dict
    return list_pdf


def thumb_list():
    now=time.time()
    if _thumb_cache and now - _thumb_cache["ts"] < _THUMB_CACHE_TTL:
        return _thumb_cache["data"]
    bucket=client.bucket('app_thumbnails')
    blobs=blobs = client.list_blobs(bucket)
    thumb_pdf={}
    for blob in blobs:
        
        thumb_pdf[blob.name.replace('.png', '')] = {
            "thumb_url": f"https://storage.googleapis.com/app_thumbnails/{blob.name}"
        }
        _thumb_cache['data']=thumb_pdf
        _thumb_cache["ts"] = now
    return thumb_pdf

def file_upload_gcs(file_name,file):
    bucket=client.bucket('online_library_app')
    # blob.cache_control = "private, max-age=360000"
    blob=bucket.blob(file_name)
    blob.upload_from_file(file,content_type='application/pdf')
    _thumb_cache.clear()
    


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
                file_upload_gcs(filename,file)
   
                uploaded += 1

        if uploaded:
            flash(f'{uploaded} file(s) successfully uploaded')
        else:
            flash('No valid files uploaded')

    return render_template('index.html')

@app.route('/viewer')
def viewer():
    pdf_dict=pdf_list()
    thumb_dict=thumb_list()
    for i in pdf_dict.keys():
        pdf_dict[i]['thumb_url'] = thumb_dict.get(i, {}).get('thumb_url', '')
    

    return render_template('viewer.html', pdfs=pdf_dict.keys(), thumbs=pdf_dict)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4900, debug=True)
