from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import fitz  # PyMuPDF
import tempfile
import os
from personnes import  users
from spapp.utils import *
from config import secret
app = Flask(__name__)
app.secret_key = secret
base_dir = os.path.dirname(os.path.abspath(__file__))

def replace_text_in_pdf(input_pdf_path, output_pdf_path, old_text, new_text,  new_title, font_size=20):
    # Ouvrir le PDF
    doc = fitz.open(input_pdf_path)

    # Parcourir toutes les pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text_instances = page.search_for(old_text)

        # Si le texte est trouvé
        if text_instances:
            for inst in text_instances:
                # Effacer le texte trouvé en dessinant un rectangle blanc dessus
                page.draw_rect(inst, color=(1, 1, 1), fill=(1, 1, 1))  # Rectangle blanc

                # Charger la police Helvetica
                font = fitz.Font(fontname="helv")
                
                # Calculer la largeur du nouveau texte
                text_width = font.text_length(new_text, fontsize=font_size)
                
                # Calculer la position centrée pour le texte
                text_x = inst.x0 + (inst.width - text_width) / 2
                text_y = inst.y0 + (font_size / 2) + 10

                # Ajouter le nouveau texte centré
                page.insert_text(
                    (text_x, text_y),  # Position centrée
                    new_text,
                    fontsize=font_size,
                    fontname="helv",
                    color=(0, 0, 0)  # Couleur du texte en noir
                )
    if new_title:
        metadata = doc.metadata
        metadata["title"] = new_title
        doc.set_metadata(metadata)

    output_dir = os.path.dirname(output_pdf_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Sauvegarder les modifications
    doc.save(output_pdf_path)
    doc.close()

@app.route('/')
def form():
    tmp_dir = os.path.join(base_dir, 'static', 'tmp')
    
    # Vérifier si le répertoire tmp existe et n'est pas vide
    if os.path.exists(tmp_dir) and os.listdir(tmp_dir):
        # Vider le répertoire tmp
        for fichier in os.listdir(tmp_dir):
            chemin_fichier = os.path.join(tmp_dir, fichier)
            if os.path.isfile(chemin_fichier) or os.path.islink(chemin_fichier):
                os.unlink(chemin_fichier)  # Supprimer le fichier ou le lien symbolique
            elif os.path.isdir(chemin_fichier):
                shutil.rmtree(chemin_fichier)

    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    first_name = request.form['first_name'].strip()
    last_name = request.form['last_name'].strip()
    name = None
    for user in users:
        
        if are_anagrams(user, f"{first_name.lower()} {last_name.lower()}"):
            name = user
    # Vérifier dans le fichier texte
    


    if name is not None:
        return redirect(url_for('generate_certificate', last_name=last_name, name=name))
    else:
        flash(f"Le nom {first_name} {last_name} n'est pas dans la liste des personnes ayant droit au certificat.", 'danger')
        return redirect(url_for('form'))

@app.route('/send_certificate/<filename>')
def send_certificate(filename):
    return send_file(os.path.join(base_dir, 'static', 'tmp', filename), as_attachment=True, download_name=filename)
    
    #redirect('/thank_you')


@app.route('/generate_certificate')
def generate_certificate():
    last_name = request.args.get('last_name')
    name = request.args.get('name')
    # Obtenir le répertoire courant du script
    

    # Construire le chemin pour stocker le fichier PDF dans le répertoire static/tmp
    filename = os.path.join(base_dir, 'static', 'tmp', f'{last_name}_certificat.pdf')


    model_pdf_path = os.path.join(base_dir, 'templates', 'model.pdf')  # Modifier pour correspondre à votre chemin
    if not os.path.isfile(model_pdf_path):
        return f"Erreur : Le modèle PDF n'existe pas à l'emplacement {model_pdf_path}."

    
    # Modifier le PDF pour ajuster le nom
    replace_text_in_pdf(model_pdf_path, filename, 'Nom du participant',  name, f'{last_name}_certificat.pdf')

    # Vérifier si le PDF modifié a été créé
    if not os.path.isfile(filename):
        return f"Erreur : Le fichier PDF modifié n'a pas été créé."
    
    # Envoyer le fichier au client
    return render_template('certificate.html', filename=f'{last_name}_certificat.pdf')
    #return redirect response

@app.route('/thank_you')
def thank_you():
    flash(f"Merci beaucoup pour votre participation !", 'success')
    #return "Merci beaucoup pour votre participation!"
    return redirect(url_for('form'))

if __name__ == "__main__":
    app.run(debug=True)
