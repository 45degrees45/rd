from flask import Flask, render_template, request, send_file
import pytesseract
from PIL import Image
import os
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_image_to_text(image_path, language='eng'):
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=language)
        return text
    except Exception as e:
        return f"Error processing image: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    language = request.form.get('language', 'eng')
    
    if file.filename == '':
        return 'No file selected', 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Convert image to text
        text = convert_image_to_text(filepath, language)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        return {'text': text}
    
    return 'Invalid file type', 400

if __name__ == '__main__':
    app.run(debug=True)
