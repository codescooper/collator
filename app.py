from flask import Flask, request, render_template, redirect, url_for
from PIL import Image
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['COLLAGE_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'pairs')

@app.route('/', methods=['GET', 'POST'])
def upload_and_collage_images():
    if request.method == 'POST':
        # Gestion de l'upload des images
        uploaded_files = request.files.getlist('file')
        for file in uploaded_files:
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)

    images = [img for img in os.listdir(app.config['UPLOAD_FOLDER']) if allowed_file(img)]
    collages = os.listdir(app.config['COLLAGE_FOLDER'])

    return render_template('index.html', images=images, collages=collages)

@app.route('/create-collage', methods=['POST'])
def create_collage():
    selected_images = request.form.getlist('selected_images')
    if len(selected_images) == 2:
        collage_filename = generate_collage(selected_images)
        # Supprimez ou déplacez les images originales
        for image in selected_images:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image))
    return redirect(url_for('upload_and_collage_images'))

def generate_collage(image_paths):
    img1 = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[0]))
    img2 = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[1]))
    img1 = img1.resize((200, 200))
    img2 = img2.resize((200, 200))

    new_img = Image.new('RGB', (400, 200))
    new_img.paste(img1, (0, 0))
    new_img.paste(img2, (200, 0))

    collage_filename = 'collage-' + image_paths[0].split('.')[0] + '-' + image_paths[1].split('.')[0] + '.jpg'
    collage_path = os.path.join(app.config['COLLAGE_FOLDER'], collage_filename)
    new_img.save(collage_path)

    return collage_filename

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['COLLAGE_FOLDER'], exist_ok=True)
    app.run(debug=True)
