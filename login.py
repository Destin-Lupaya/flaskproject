import string
from random import randint, choice
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/generate_password")
def generate_password():
    password_min = 6
    password_max = 12
    all_chars = string.ascii_letters + string.punctuation + string.digits

    password = "".join(choice(all_chars) for x in range(randint(password_min, password_max)))
    return render_template("password.html", password=password)


@app.route("/add_password", methods=["GET", "POST"])
def add_password():
    if request.method == "POST":
        new_password = request.form["password"]  # Récupérer la valeur de la zone de saisie "password" du formulaire

        # Ajouter le nouveau mot de passe à la liste "passwords"
        passwords.append(new_password)

        # Rediriger l'utilisateur vers la page d'accueil
        return redirect(url_for("home"))

    # Si la méthode de requête n'est pas POST, afficher simplement le formulaire
    return render_template("add_password.html")


@app.route("/modify_password")
def modify_password():
    # Modifier une entrée existante de mot de passe
    pass


@app.route("/save_password")
def save_password():
    # Enregistrer toutes les entrées de mot de passe
    pass


@app.route("/delete_password")
def delete_password():
    # Supprimer une entrée existante de mot de passe
    pass


if __name__ == "__main__":
    app.run(debug=True)