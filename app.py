from flask import Flask, render_template, request, redirect, url_for, session
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  
        username = request.form.get('username')  

        session['username'] = username

        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    username = session.get('username')
    return render_template('index.html', username=username)

def apply_filters(image, filters):
    if 'crop' in filters:
        # Apply crop filter
        image = image.crop((float(filters['crop']), (float(filters['crop'])/2), image.width - float(filters['crop']), image.height - (float(filters['crop'])/2)))

    if 'blur' in filters:
        # Apply blur filter
        image = image.filter(ImageFilter.BoxBlur(float(filters['blur'])))

    if 'rotate' in filters:
        # Apply rotate filter
        image = image.rotate(float(filters['rotate']))  # Example rotation angle

    if 'sharpness' in filters:
        # Apply sharpness filter
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(float(filters['sharpness'])/10)

        
    if 'brightness' in filters:
        # Apply brightness adjustment
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(float(filters['brightness'])/4)

    if 'contrast' in filters:
        # Apply contrast adjustment
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(float(filters['contrast'])/4)

    return image

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Get filter values from form
            filter_values = {}
            for key in request.form:
                if key != 'file':
                    filter_values[key] = request.form[key]

            # Apply filters to the uploaded image
            img = Image.open(filepath)
            img = apply_filters(img, filter_values)
            img.save(filepath)

            # Redirect to the result page
            return redirect(url_for('result', filename=filename))
    return redirect(url_for('index'))

@app.route('/result/<filename>')
def result(filename):
    return render_template('result.html', filename=filename)

if __name__ == '__main__':
    app.run(debug=True)
