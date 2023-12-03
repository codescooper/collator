from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'

@app.route('/', methods=['GET', 'POST'])

def upload_images():
    if request.method == 'POST':
         # Créez le répertoire 'static/uploads' s'il n'existe pas
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        uploaded_files = request.files.getlist('file')
        uploaded_images = []

        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                uploaded_images.append(file.filename)

        return render_template('index.html', images=uploaded_images)

    return render_template('index.html')

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    app.run(debug=True)
