from flask import Flask, request, render_template, redirect, url_for
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['COLLAGE_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'pairs')

@app.route('/', methods=['GET', 'POST'])
def upload_and_collage_images():
    if request.method == 'POST':
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
    selected_size = request.form['size']
    if len(selected_images) == 2:
        collage_filename = generate_collage(selected_images, selected_size)
        # Supprimez ou déplacez les images originales
        for image in selected_images:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image))
    return redirect(url_for('upload_and_collage_images'))

def generate_collage(image_paths, size):
    # Fonction pour remplacer la transparence par un fond blanc
    def add_white_background(image):
        background = Image.new('RGB', image.size, 'white')
        background.paste(image, mask=image.split()[3])
        return background

    # Charger les images et ajouter un fond blanc si nécessaire
    img1 = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[0]))
    img2 = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[1]))
    if img1.mode == 'RGBA':
        img1 = add_white_background(img1)
    if img2.mode == 'RGBA':
        img2 = add_white_background(img2)

    logo = Image.open('logo.png')
    logo = add_white_background(logo)
    logo_size = min(img1.width, img2.width) * 0.5
    logo = logo.resize((int(logo_size), int(logo_size * (logo.height / logo.width))), Image.Resampling.LANCZOS)

    # Réduire l'espacement entre les images
    espacement = 3  # Espacement en pixels entre les images et le logo

    new_width = img1.width + img2.width + logo.width + 2 * espacement
    new_height = max(img1.height, img2.height, logo.height)
    new_img = Image.new('RGB', (new_width, new_height), 'white')

    img1_x = espacement
    img2_x = img1_x + img1.width + espacement + logo.width
    images_y = (new_height - max(img1.height, img2.height)) // 2
    logo_x = img1_x + img1.width + espacement
    logo_y = (new_height - logo.height) // 2

    new_img.paste(img1, (img1_x, images_y))
    new_img.paste(img2, (img2_x, images_y))
    new_img.paste(logo, (logo_x, logo_y))



    footer = Image.open('footer.jpg')
    footer = footer.resize((new_img.width, footer.height), Image.Resampling.LANCZOS)

    new_height_with_footer = new_height + footer.height
    final_img = Image.new('RGB', (new_width, new_height_with_footer), 'white')

    final_img.paste(new_img, (0, 0))
    final_img.paste(footer, (0, new_height))

    # Ajout de la taille sur l'image
    draw = ImageDraw.Draw(final_img)
    font = ImageFont.truetype("arial.ttf", 36)  # Choisissez la police et la taille appropriées
    draw.text((10, 10), "100", (255, 255, 255), font=font)  # Positionnez le texte comme vous le souhaitez

    collage_filename = 'collage-' + image_paths[0].split('.')[0] + '-' + image_paths[1].split('.')[0] + '.png'
    collage_path = os.path.join(app.config['COLLAGE_FOLDER'], collage_filename)
    final_img.save(collage_path, 'PNG')

    return collage_filename


def resize_image(image, base_width):
    w_percent = (base_width / float(image.size[0]))
    h_size = int((float(image.size[1]) * float(w_percent)))
    return image.resize((base_width, h_size), Image.Resampling.LANCZOS)

def allowed_file(filename):
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['COLLAGE_FOLDER'], exist_ok=True)
    app.run(debug=True)
