# EmailSpoof v1.0
# Author: @esteban111221
# https://github.com/esteban11121


import smtplib
import argparse
import sys
import signal
import time
from termcolor import colored
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
import json

# Banner de bienvenida
def print_banner():
    banner = '''
 

███████╗███╗░░░███╗░█████╗░██╗██╗░░░░░░██████╗██████╗░░█████╗░░█████╗░███████╗
██╔════╝████╗░████║██╔══██╗██║██║░░░░░██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝
█████╗░░██╔████╔██║███████║██║██║░░░░░╚█████╗░██████╔╝██║░░██║██║░░██║█████╗░░
██╔══╝░░██║╚██╔╝██║██╔══██║██║██║░░░░░░╚═══██╗██╔═══╝░██║░░██║██║░░██║██╔══╝░░
███████╗██║░╚═╝░██║██║░░██║██║███████╗██████╔╝██║░░░░░╚█████╔╝╚█████╔╝██║░░░░░
╚══════╝╚═╝░░░░░╚═╝╚═╝░░╚═╝╚═╝╚══════╝╚═════╝░╚═╝░░░░░░╚════╝░░╚════╝░╚═╝░░░░░
                                                                                  
                                                Uso responsable y ético
    '''
    print(colored(banner, 'green'))

# Salida del programa
def signal_handler(sig, frame):
    print(colored(f"\n[!] Saliendo del programa...", 'red'))
    sys.exit(1)

signal.signal(signal.SIGINT, signal_handler)

# Validación de email
def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# Carga de configuración desde JSON
def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        print(colored(f"[!] Error al cargar el archivo de configuración: {e}", 'red'))
        sys.exit(1)

# Gestión de argumentos del programa
def get_arguments():
    parser = argparse.ArgumentParser(
        description="Herramienta para enviar correos electrónicos con un remitente personalizado.",
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-c", "--config", required=False, dest="config_file", help="Ruta al archivo de configuración JSON")
    parser.add_argument("-e", "--email", required=False, dest="sender_email", help="Cuenta desde la que se envía el correo")
    parser.add_argument("-p", "--password", required=False, dest="app_password", help="Contraseña de la cuenta emisora")
    parser.add_argument("-v", "--victim", required=False, dest="receiver_email", help="Cuenta destinataria")
    parser.add_argument("-s", "--subject", required=False, dest="asunto", help="Asunto del email")
    parser.add_argument("-S", "--Spoof", required=False, dest="spoof", help="Remitente personalizado")
    parser.add_argument("-t", "--texto", required=False, dest="texto", help="Texto del mensaje")
    parser.add_argument("-a", "--attach", required=False, dest="attachment", help="Ruta del archivo adjunto")

    args = parser.parse_args()

    # Priorizar configuración desde archivo JSON
    if args.config_file:
        config = load_config(args.config_file)
        return config

    # Validar campos necesarios
    if not args.sender_email or not args.app_password or not args.receiver_email:
        print(colored("[!] Faltan parámetros obligatorios. Usa -h para ayuda.", 'red'))
        sys.exit(1)

    # Validar formato de correo
    if not validate_email(args.sender_email) or not validate_email(args.receiver_email):
        print(colored("[!] Dirección de correo inválida.", 'red'))
        sys.exit(1)

    return vars(args)

# Envío de correo electrónico
def sendmail(sender_email, app_password, receiver_email, asunto, spoof, texto, attachment=None):
    print(colored("[+] Iniciando el envío del correo...", "blue"))
    time.sleep(1)

    # Crear el mensaje
    message = MIMEMultipart("alternative")
    message["Subject"] = asunto
    message["From"] = f"{spoof} <{sender_email}>"
    message["To"] = receiver_email

    # Contenido del correo
    part = MIMEText(texto, "plain")
    message.attach(part)

    # Adjuntar archivo si se proporciona
    if attachment:
        try:
            with open(attachment, "rb") as file:
                from email.mime.base import MIMEBase
                from email import encoders

                part = MIMEBase("application", "octet-stream")
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment)}",
                )
                message.attach(part)
        except Exception as e:
            print(colored(f"[!] Error al adjuntar archivo: {e}", 'red'))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        print(colored("[+] Correo enviado con éxito!", "green"))

    except Exception as e:
        print(colored(f"[!] Error al enviar el correo: {e}", "red"))

# Función principal
def main():
    print_banner()
    args = get_arguments()
    sendmail(
        args.get("sender_email"),
        args.get("app_password"),
        args.get("receiver_email"),
        args.get("asunto"),
        args.get("spoof"),
        args.get("texto"),
        args.get("attachment")
    )

if __name__ == '__main__':
    main()
