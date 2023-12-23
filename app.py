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
    def add_white_background(image):
        background = Image.new('RGB', image.size, 'white')
        background.paste(image, mask=image.split()[3])
        return background

    def trim(im):
        bbox = im.getbbox()
        if bbox:
            return im.crop(bbox)
        return im  # Retourne l'image non modifiée si getbbox() renvoie None

    # Chemin vers le répertoire contenant les logos
    logo_dir = 'taille/'
    footer_path = 'footer.jpg'  # Assurez-vous que ce chemin est correct

    # Charger les images et les rogner
    img1 = trim(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[0])))
    img2 = trim(Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image_paths[1])))
    if img1.mode == 'RGBA':
        img1 = add_white_background(img1)
    if img2.mode == 'RGBA':
        img2 = add_white_background(img2)

    # Charger le logo correspondant à la taille sélectionnée
    logo_path = os.path.join(logo_dir, f'logo-{size}.png')
    logo = Image.open(logo_path)
    logo = add_white_background(logo) if logo.mode == 'RGBA' else logo

    # Redimensionner le logo
    logo_factor = 0.05
    new_logo_size = (int(logo.width * logo_factor), int(logo.height * logo_factor))
    logo = logo.resize(new_logo_size, Image.Resampling.LANCZOS)

    # Calculer la taille du collage pour qu'il soit carré
    collage_width = img1.width + img2.width + logo.width
    collage_height = max(img1.height, img2.height, logo.height)
    new_size = max(collage_width, collage_height)
    new_img = Image.new('RGB', (new_size, new_size), 'white')

    # Charger le footer et le redimensionner pour correspondre à la largeur de l'image carrée
    footer = Image.open(footer_path)
    footer = footer.resize((new_size, int(new_size * (footer.height / footer.width))), Image.Resampling.LANCZOS)

    # Calculer la hauteur totale de l'image finale avec le footer
    final_height = new_size + footer.height
    final_img = Image.new('RGB', (new_size, final_height), 'white')

    # Positionner les images et le logo dans le carré
    # Calculer la largeur disponible pour les robes
    disponible_width_per_rob = (new_size - logo.width) // 2

    # Redimensionner les images des robes
    aspect_ratio_img1 = img1.height / img1.width
    aspect_ratio_img2 = img2.height / img2.width

    new_height_img1 = int(disponible_width_per_rob * aspect_ratio_img1)
    new_height_img2 = int(disponible_width_per_rob * aspect_ratio_img2)

    img1 = img1.resize((disponible_width_per_rob, new_height_img1))
    img2 = img2.resize((disponible_width_per_rob, new_height_img2))

    # Positionner les robes et le logo
    img1_x = 0
    logo_x = disponible_width_per_rob
    img2_x = disponible_width_per_rob + logo.width

    # Coller les images redimensionnées dans le collage
    new_img.paste(img1, (img1_x, (new_size - new_height_img1)//2))
    new_img.paste(logo, (logo_x, (new_size - logo.height)//2))
    new_img.paste(img2, (img2_x, (new_size - new_height_img2)//2))

    # Coller le footer en bas de l'image
    final_img.paste(footer, (0, new_size))

    # Sauvegarder le collage
    collage_filename = 'collage-' + image_paths[0].split('.')[0] + '-' + image_paths[1].split('.')[0] + '.png'
    collage_path = os.path.join(app.config['COLLAGE_FOLDER'], collage_filename)
    new_img.save(collage_path, 'PNG')

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
