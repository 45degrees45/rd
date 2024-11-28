from flask import Flask, render_template, request, send_file, jsonify
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pytesseract import Output
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

class EnhancedOCR:
    def __init__(self):
        self.receipt_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
        self.prescription_config = r'--oem 3 --psm 6 -c tessedit_char_blacklist=©®™'
        
    def preprocess_image(self, image_path, document_type='general'):
        # Read image using opencv
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if document_type == 'receipt':
            # Special processing for receipts
            processed = cv2.adaptiveThreshold(
                gray, 255, 
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            processed = cv2.fastNlMeansDenoising(processed)
            kernel = np.ones((1,1), np.uint8)
            processed = cv2.dilate(processed, kernel, iterations=1)
            
        elif document_type == 'prescription':
            # Special processing for prescriptions
            processed = cv2.bilateralFilter(gray, 9, 75, 75)
            processed = cv2.equalizeHist(processed)
            _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
        else:
            # General purpose processing
            processed = cv2.GaussianBlur(gray, (3,3), 0)
            processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
        return processed
    
    def enhance_resolution(self, image):
        return cv2.resize(image, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    def detect_skew(self, image):
        coords = np.column_stack(np.where(image > 0))
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle
    
    def correct_skew(self, image):
        angle = self.detect_skew(image)
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def extract_text(self, image_path, document_type='general'):
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image_path, document_type)
            
            # Enhance resolution
            processed_image = self.enhance_resolution(processed_image)
            
            # Correct skew
            processed_image = self.correct_skew(processed_image)
            
            # Convert to PIL Image
            pil_image = Image.fromarray(processed_image)
            
            # Select configuration based on document type
            config = self.receipt_config if document_type == 'receipt' else self.prescription_config
            
            # Perform OCR with confidence scores
            data = pytesseract.image_to_data(pil_image, config=config, output_type=Output.DICT)
            
            # Filter results based on confidence
            text_results = []
            confidences = []
            
            for i in range(len(data['text'])):
                if float(data['conf'][i]) > 60:  # Filter low-confidence results
                    text_results.append(data['text'][i])
                    confidences.append(float(data['conf'][i]))
            
            return {
                'text': ' '.join(text_results),
                'confidence': sum(confidences) / len(confidences) if confidences else 0,
                'words': len(text_results)
            }
        except Exception as e:
            return {
                'text': f"Error processing image: {str(e)}",
                'confidence': 0,
                'words': 0
            }

# Initialize OCR
ocr = EnhancedOCR()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    document_type = request.form.get('document_type', 'general')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Convert image to text using enhanced OCR
            result = ocr.extract_text(filepath, document_type)
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True)
