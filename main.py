import subprocess
import datetime
import time
import hashlib

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

def run_spider():
    nombre_archivo = f"./datos/datos-{datetime.date.today()}-{str(time.time()).split(".")[0]}.csv"

    subprocess.run(args=[
        "scrapy",
        "crawl",
        f"arana",
        "-o",
        nombre_archivo
    ])

    return nombre_archivo

def enviar_correo(nombre_archivo : str, hash : str):
    # Configura las credenciales de tu cuenta de Gmail
    gmail_user = 'correo@gmail.com'
    with open("./password.txt", "+r") as file:
        gmail_password = file.read()

    # Configura los detalles del correo
    from_email = gmail_user
    to_email = 'correo@gmail.com'
    subject = 'Datos PANINI'
    body = f"{datetime.datetime.now()}\nHASH: {hash}"

    # Crea el objeto MIME
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Adjunta el cuerpo del correo
    msg.attach(MIMEText(body, 'plain'))

    # Especifica el archivo que deseas adjuntar
    filename = nombre_archivo.split("/")[2]  # Nombre del archivo
    filepath = nombre_archivo  # Ruta completa al archivo

    # Abre el archivo en modo binario
    with open(filepath, 'rb') as attachment:
        # Instancia MIMEBase y establece el payload del archivo adjunto
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())

        # Codifica el archivo en base64
        encoders.encode_base64(part)

        # Agrega el encabezado de adjunto
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={filename}',
        )

        # Adjunta el archivo al mensaje
        msg.attach(part)

    # Inicia la conexión con el servidor de Gmail
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Establece la conexión segura
        server.login(gmail_user, gmail_password)  # Inicia sesión

        # Envía el correo
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)

        print('Correo enviado con éxito!')
    except Exception as e:
        print(f'Error al enviar el correo: {e}')
    finally:
        server.quit()  # Cierra la conexión

def calcular_hash(archivo, algoritmo='sha256'):
    # Crear una instancia del algoritmo de hash
    hash_func = hashlib.new(algoritmo)
    
    # Leer el archivo en bloques para evitar problemas de memoria con archivos grandes
    with open(archivo, 'rb') as f:
        for bloque in iter(lambda: f.read(4096), b""):
            hash_func.update(bloque)
    
    # Retornar el hash en formato hexadecimal
    return hash_func.hexdigest()

if __name__ == '__main__':
    archivo = run_spider()
    hash = calcular_hash(archivo=archivo).upper()

    enviar_correo(archivo, hash=hash)