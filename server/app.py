import sqlite3 as sql
import re
import smtplib
import os

from flask import render_template, request
from flask_mail import Mail, Message
from flask_cors import CORS
from shutil import copyfile
from flask import Flask
from random import choice


COLORS = [
    "Glitzer",
    "Grün",
    "Gelb",
    "Rot",
    "Blau",
    "Braun",
    "Orange",
    "Türkis",
    "Gold",
    "Silber",
    "Lila",
    "Pink",
    "Beige",
    "Schwarz",
    "Weiß",
    "Grau",
    "Bunt",
]
LETTERS = "ABDEFGHKLMNOPRSTUVWZ"

app = Flask(__name__)
app.config.from_pyfile("config.py")
CORS(app)
mail = Mail(app)

DB_PATH = app.config.get("DB_PATH", "database.sqlite3")


@app.before_first_request
def create_db_schema():
    with sql.connect(DB_PATH) as con:
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS data(email text PRIMARY KEY NOT NULL, color text NOT NULL, letter char(1) NOT NULL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);"
        )
        con.commit()


class ViewError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(self)
        self.message = message
        self.status_code = status_code


@app.errorhandler(ViewError)
def handle_view_error(error):
    app.logger.error(error.message)
    return {"error": error.message}, error.status_code


@app.route("/request", methods=["POST"])
def order():
    data = request.json
    assert "email" in data
    email = data["email"]
    assert re.match(r"^[a-z]+@uos.de$", email)

    color = choice(COLORS)
    letter = choice(LETTERS)

    with sql.connect(DB_PATH) as con:
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO data(email, color, letter) VALUES (?, ?, ?)",
                (email, color, letter)
            )
            con.commit()
        except sql.IntegrityError:
            con.rollback()
            cur = con.cursor()
            cur.execute(
                "SELECT color, letter FROM data WHERE email = ?", (email,)
            )
            res = cur.fetchone()
            color = res[0]
            letter = res[1]
        except Exception as e:
            con.rollback()
            raise ViewError(e.message)

    msg = Message(
        subject="FS-Wichteln: Buchstabe und Farbe",
        recipients=[email],
        body=f"Buchstabe: {letter}\nFarbe: {color}",
        sender=email,
    )
    try_send_mail(msg)
    return {}


def try_send_mail(msg):
    try:
        mail.send(msg)
    except smtplib.SMTPServerDisconnected:
        raise ViewError(_("Der Server ist nicht korrekt konfiguriert"))
    except smtplib.SMTPRecipientsRefused as e:
        messages = [
            "{}: {} {}".format(r, errno, msg.decode())
            for r, (errno, msg) in e.recipients.items()
        ]
        raise ViewError(
            _("Konnte E-Mail nicht versenden an:") + " " + ", ".join(messages)
        )


def get_app():
    return app


if __name__ == "__main__":
    app.run()
