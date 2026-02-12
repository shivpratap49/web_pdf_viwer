
import functions_framework
from google.cloud import storage
#from pdf2image import convert_from_bytes
import fitz 
from PIL import Image
import io

THUMB_FOLDER = "thumbnails"  # folder in the bucket for thumbnails

client = storage.Client()

@functions_framework.cloud_event
def generate_thumbnail(cloud_event):
    data = cloud_event.data

    bucket_name = data["bucket"]
    pdf_filename = data["name"]
    content_type = data.get("contentType", "")

    # Only process PDFs
    if not pdf_filename.lower().endswith(".pdf"):
        print(f"Skipping non-PDF file: {pdf_filename}")
        return

    print(f"Generating thumbnail for: {pdf_filename}")

    try:
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(pdf_filename)

        # Download PDF into memory
        pdf_bytes = blob.download_as_bytes()

        # Convert first page to image
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)  # first page

        # Render page to pixmap
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # scale 2x for better resolution

        # Convert to PIL Image
        thumb_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Resize thumbnail
        thumb_image.thumbnail((200, 260))

        # Save thumbnail to memory
        thumb_buffer = io.BytesIO()
        thumb_image.save(thumb_buffer, format="PNG")
        thumb_buffer.seek(0)

        thumb_bucket=client.bucket('app_thumbnails')
        # Upload thumbnail to "thumbnails" folder
        thumb_blob = thumb_bucket.blob(f"{pdf_filename}.png")
        thumb_blob.cache_control = "public, max-age=31536000, immutable"

        thumb_blob.upload_from_file(thumb_buffer, content_type="image/png")

        print(f"Thumbnail saved at: {THUMB_FOLDER}/{pdf_filename}.png")

    except Exception as e:
        print(f"Error generating thumbnail for {pdf_filename}: {e}")