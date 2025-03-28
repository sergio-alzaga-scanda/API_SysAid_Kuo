import logging
from flask import Flask, request, jsonify
import requests
import unidecode
import re
from requests.auth import HTTPBasicAuth

app = Flask(__name__)

# Configuración del logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# URL base
BASE_URL = "https://app.kenos-atom/api/V1/Ticket/generateTicket"

# Credenciales de autenticación para la API externa
API_USER = "scanda_kuo"
API_PASS = "4p1#5cAnD4Ku0"

# Ruta para generar el ticket de tipo 1 (incidente)
@app.route('/generaTicketInc', methods=['POST'])
def genera_ticket_inc():
    try:
        # Intentar obtener el cuerpo de la solicitud como JSON
        data = request.get_json()

        # Imprimir los datos que recibe el servidor para depuración
        print("Datos recibidos:", data)

        # Verificar si los datos son válidos
        if not data:
            return jsonify({"error": "Se esperaba un cuerpo JSON válido."}), 400

        # Normalizar el correo electrónico
        email = data.get("UsuarioRequerimientoEmail", "")
        email = normalize_email(email)
        if not email:
            return jsonify({"error": "El correo electrónico no es válido."}), 400
        
        # Datos del ticket
        ticket_data = {
            "Responsable": 8288,
            "Prioridad": 3,  # Este es un valor fijo
            "UsuarioRequerimientoStr": data.get("UsuarioRequerimientoStr"),
            "UsuarioRequerimientoEmail": email,
            "TipoContacto": 6,
            "GrupoAsignado": 164,
            "Localidad": 1,
            "Titulo": data.get("Titulo"),
            "Descripcion": data.get("Descripcion"),
            "Categoria": "APP DE NEGOCIO",
            "SubCategoria": "SIMAX",
            "CategoriaTercerNivel": data.get("CategoriaTercerNivel"),
            "Compania": 16,
            "TipoTicket": 1  # Tipo de ticket: Incidente
        }

        # Registrar los datos del ticket en los logs antes de enviarlos
        logging.info("Datos enviados al endpoint: %s", ticket_data)

        # Enviar la solicitud al endpoint correspondiente con autenticación básica
        response = requests.post(BASE_URL, json=ticket_data, auth=HTTPBasicAuth(API_USER, API_PASS))
        
        # Registrar la respuesta y el código de estado en el log
        logging.info("API Respuesta - Status: %d, Response: %s", response.status_code, response.text)
        
        # Verificar la respuesta
        if not response.text.strip():  # Si la respuesta está vacía
            return jsonify({"error": "La respuesta de la API está vacía."}), 500

        try:
            response_data = response.json()
        except ValueError:
            return jsonify({"error": "La respuesta de la API no es un JSON válido."}), 500

        if response.status_code == 200:
            # Acceder al objeto 'data' dentro de la respuesta
            ticket_data = response_data.get("data", {})

            # Filtrar los datos necesarios y convertir el ID a cadena
            filtered_data = {
                "id": str(ticket_data.get("id")),  # Convertir el ID a cadena
                "responsibility": ticket_data.get("responsibility"),
                "assignedGroup": ticket_data.get("assignedGroup"),
                "srType": ticket_data.get("srType"),
                "status": ticket_data.get("status")
            }
            return jsonify(filtered_data), 200
        else:
            return jsonify({"error": "Error al crear el ticket", "details": response_data}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para generar el ticket de tipo 2 (requiemiento)
@app.route('/generaTicketReq', methods=['POST'])
def genera_ticket_req():
    try:
        # Intentar obtener el cuerpo de la solicitud como JSON
        data = request.get_json()

        # Imprimir los datos que recibe el servidor para depuración
        print("Datos recibidos:", data)

        # Verificar si los datos son válidos
        if not data:
            return jsonify({"error": "Se esperaba un cuerpo JSON válido."}), 400

        # Normalizar el correo electrónico
        email = data.get("UsuarioRequerimientoEmail", "")
        email = normalize_email(email)
        if not email:
            return jsonify({"error": "El correo electrónico no es válido."}), 400
        
        # Datos del ticket
        ticket_data = {
            "Prioridad": data.get("Prioridad", 3),  # Valor predeterminado si no se pasa
            "UsuarioRequerimientoStr": data.get("UsuarioRequerimientoStr"),
            "UsuarioRequerimientoEmail": email,
            "TipoContacto": 6,
            "GrupoAsignado": 136,  # Valor predeterminado para el tipo 2
            "Localidad": 12,  # Valor predeterminado para el tipo 2
            "Titulo": data.get("Titulo"),
            "Descripcion": data.get("Descripcion"),
            "Categoria": data.get("Categoria", "PORTAL"),  # Valor predeterminado
            "SubCategoria": "ACTIVE DIRECTORY",  # Fijo para el tipo 2
            "CategoriaTercerNivel": "DESBLOQUEO CUENTA",  # Fijo para el tipo 2
            "Compania": 3,  # Fijo para el tipo 2
            "AdministradorResponsable": 3,  # Fijo para el tipo 2
            "TipoTicket": 2  # Tipo de ticket: Requerimiento
        }

        # Registrar los datos del ticket en los logs antes de enviarlos
        logging.info("Datos enviados al endpoint: %s", ticket_data)

        # Enviar la solicitud al endpoint correspondiente con autenticación básica
        response = requests.post(BASE_URL, json=ticket_data, auth=HTTPBasicAuth(API_USER, API_PASS))
        
        # Registrar la respuesta y el código de estado en el log
        logging.info("API Respuesta - Status: %d, Response: %s", response.status_code, response.text)
        
        # Verificar la respuesta
        if not response.text.strip():  # Si la respuesta está vacía
            return jsonify({"error": "La respuesta de la API está vacía."}), 500

        try:
            response_data = response.json()
        except ValueError:
            return jsonify({"error": "La respuesta de la API no es un JSON válido."}), 500

        if response.status_code == 200:
            # Acceder al objeto 'data' dentro de la respuesta
            ticket_data = response_data.get("data", {})

            # Filtrar los datos necesarios y convertir el ID a cadena
            filtered_data = {
                "id": str(ticket_data.get("id")), 
                "responsibility": ticket_data.get("responsibility"),
                "assignedGroup": ticket_data.get("assignedGroup"),
                "srType": ticket_data.get("srType"),
                "status": ticket_data.get("status")
            }
            return jsonify(filtered_data), 200
        else:
            return jsonify({"error": "Error al crear el ticket", "details": response_data}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para validar y normalizar el correo electrónico
@app.route('/validarEmail', methods=['POST'])
def validar_email():
    try:
        # Obtener el correo electrónico del cuerpo de la solicitud
        data = request.get_json()
        email = data.get("email", "")

        # Verificar si el correo es válido
        if not email:
            return jsonify({"error": "El correo electrónico es requerido."}), 400
        
        # Validar formato del correo
        if not is_valid_email(email):
            # Si no es válido, normalizar el correo
            email = normalize_email(email)
            if not email:
                return jsonify({"error": "El correo electrónico no tiene un formato válido."}), 400

        # Retornar el correo normalizado
        return jsonify({"email_normalizado": email}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Función para verificar si el correo tiene un formato válido
def is_valid_email(email: str) -> bool:
    # Expresión regular para verificar formato de correo
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))
# Función para normalizar el correo electrónico
def normalize_email(email: str) -> str:
    # Convertir todo a minúsculas
    email = email.lower()

    # Eliminar acentos (normaliza caracteres especiales como acentos y ñ)
    email = unidecode.unidecode(email)

    # Reemplazar la 'ñ' por 'n'
    email = email.replace('ñ', 'n')

    # Reemplazar palabras clave con o sin espacios por los signos de puntuación correspondientes
    email = email.replace(" punto", ".").replace(" punto ", ".")  # Reemplaza "punto" y " punto " por "."
    email = email.replace(" arroba", "@").replace(" arroba ", "@")  # Reemplaza "arroba" y " arroba " por "@"
    email = email.replace(" guion bajo", "_").replace(" guion bajo ", "_")  # Reemplaza "guion bajo" por "_"
    email = email.replace(" guion medio", "-").replace(" guion medio ", "-")  # Reemplaza "guion medio" por "-"

    # Reemplazar posibles combinaciones de palabras clave sin espacios o con mayúsculas/minúsculas
    email = email.replace("punto", ".").replace("arroba", "@").replace("guion bajo", "_").replace("guion medio", "-")

    # Reemplazar combinaciones específicas de dominios y palabras
    email = email.replace("escanda", "scanda").replace("skanda", "scanda").replace("eksanda", "scanda")
    email = email.replace("xamai", "xamai").replace("shamay", "xamai").replace("chamai", "xamai").replace("shamy", "xamai")
    email = email.replace("kenos", "kenos").replace("quenos", "kenos").replace("kenoz", "kenos").replace("kenus", "kenos")
    email = email.replace("kairos", "kairos").replace("kairós", "kairos").replace("cairos", "kairos")

    # Reemplazar apellidos comunes con errores de escritura
    email = email.replace("perez", "perez").replace("peres", "perez").replace("peérez", "perez")
    email = email.replace("peñaloza", "penaloza").replace("penaloza", "penaloza").replace("peñalosa", "penaloza")
    email = email.replace("hernandez", "hernandez").replace("hernández", "hernandez").replace("hernandes", "hernandez")
    email = email.replace("gomez", "gomez").replace("gómez", "gomez").replace("gomes", "gomez")
    email = email.replace("garcia", "garcia").replace("garçía", "garcia")
    email = email.replace("lopez", "lopez").replace("lópez", "lopez").replace("lopéz", "lopez").replace("lopes", "lopez")
    email = email.replace("rodriguez", "rodriguez").replace("rodríguez", "rodriguez").replace("rodriges", "rodriguez")
    email = email.replace("martinez", "martinez").replace("martines", "martinez").replace("martínez", "martinez")
    email = email.replace("jimenez", "jimenez").replace("jiménez", "jimenez").replace("ximenez", "jimenez").replace("giménez", "jimenez")
    email = email.replace("morales", "morales").replace("moralez", "morales").replace("moraless", "morales")
    email = email.replace("sanchez", "sanchez").replace("sánchez", "sanchez").replace("sänchez", "sanchez")
    email = email.replace("diaz", "diaz").replace("díaz", "diaz").replace("dias", "diaz").replace("diez", "diaz")

    # Reemplazar dominios comunes con errores de escritura, considerando la variación de "k" y "qu"
    email = email.replace("keken", "keken").replace("keken", "keken") \
                 .replace("keken", "keken").replace("kekenm", "keken").replace("keken", "keken") \
                 .replace("queken", "keken").replace("kekenqu", "keken")

    email = email.replace("desc", "desc").replace("desk", "desc").replace("descom", "desc") \
                 .replace("descc", "desc").replace("qudesc", "desc")

    email = email.replace("dacomsa", "dacomsa").replace("dacoms", "dacomsa").replace("dacoms", "dacomsa") \
                 .replace("quacomsa", "dacomsa").replace("dacomqusa", "dacomsa")

    email = email.replace("tremec", "tremec").replace("tremecx", "tremec").replace("trekec", "tremec") \
                 .replace("tremquec", "tremec")

    email = email.replace("dynasol", "dynasol").replace("dinasol", "dynasol").replace("dynasol", "dynasol") \
                 .replace("quynasol", "dynasol").replace("dynasquol", "dynasol")

    email = email.replace("dine", "dine").replace("dinecom.mx", "dine").replace("dinecom", "dine") \
                 .replace("qudine", "dine")

    email = email.replace("puntamita", "puntamita").replace("punta-mita", "puntamita").replace("puntamita", "puntamita") \
                 .replace("qupuntamita", "puntamita")

    email = email.replace("adrisa", "adrisa").replace("adresa", "adrisa").replace("adrisa", "adrisa") \
                 .replace("quadrisa", "adrisa")

    email = email.replace("resirene", "resirene").replace("resirene", "resirene").replace("resirenecom", "resirene") \
                 .replace("quresirene", "resirene")

    email = email.replace("lndsr", "lndsr").replace("lndstr", "lndsr").replace("lndser", "lndsr") \
                 .replace("qulndsr", "lndsr")

    email = email.replace("igsr", "igsr").replace("igres", "igsr").replace("igsr", "igsr") \
                 .replace("quigsr", "igsr")

    email = email.replace("repsol", "repsol").replace("repsolx", "repsol").replace("repsoln", "repsol") \
                 .replace("qurepsol", "repsol")

    # Eliminar espacios adicionales
    email = re.sub(r'\s+', '', email)

    # Validar que el correo tiene al menos una "@" y un "." en el dominio
    if "@" not in email or "." not in email or email.count("@") != 1:
        return ""  # Si no hay una única "@" o un dominio válido, retornar cadena vacía

    # Validar que no haya caracteres no permitidos en el correo
    if not re.match(r"^[a-z0-9@._-]+$", email):
        return ""  # Si hay caracteres no válidos, retornar cadena vacía

    # Validar que el dominio tenga al menos un punto después de la "@" para que sea un correo válido
    local_part, domain = email.rsplit('@', 1)
    if '.' not in domain:
        return ""

    return email
if __name__ == '__main__':
    # Ejecutar el servidor Flask
    app.run(debug=True)
