import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# ============================
# CONFIGURACIÓN PRINCIPAL
# ============================
BOT_TOKEN = "8344802184:AAE8DEKP-8mKIFIF425X7g_OQCYZUBNG7qM"

LOGIN_URL = "https://edu-connect-be-e0f9gxg3akdnase4.centralus-01.azurewebsites.net/v1/users/login"
BACKEND_URL = "https://edu-connect-be-e0f9gxg3akdnase4.centralus-01.azurewebsites.net/api/bot/query-ai"

BOT_CREDENTIALS = {
    "username": "estudiante@edu-connect.com",  # usuario técnico
    "password": "password123"
}

jwt_token = None
user_sessions = {}  # guarda correo por chat_id


# ============================
# AUTENTICACIÓN DEL BOT
# ============================
def obtener_jwt():
    global jwt_token
    try:
        response = requests.post(LOGIN_URL, json=BOT_CREDENTIALS, timeout=20)

        token_header = (
            response.headers.get("Authorization")
            or response.headers.get("authorization")
            or response.headers.get("access_token")
            or response.headers.get("token")
        )

        if token_header and token_header.lower().startswith("bearer "):
            jwt_token = token_header.split(" ", 1)[1].strip()
        else:
            jwt_token = token_header

        if not jwt_token:
            data = response.json()
            jwt_token = data.get("token") or data.get("jwt")

        if jwt_token:
            print("✅ JWT obtenido desde headers correctamente.")
        else:
            print("⚠️ No se encontró token en los headers ni en el body.")
    except Exception as e:
        print("❌ Error al obtener JWT:", e)
        jwt_token = None


# ============================
# HANDLERS DE TELEGRAM
# ============================
def start(update, context):
    update.message.reply_text(
        "👋 ¡Hola! Soy el asistente inteligente de EduConnect.\n\n"
        "Por favor, envíame tu correo institucional para identificarte (ejemplo: estudiante@edu-connect.com)."
    )


def handle_email(update, context):
    correo = update.message.text.strip()
    if "@" in correo and "." in correo:
        user_sessions[update.effective_chat.id] = correo
        update.message.reply_text(
            f"✅ Correo registrado: {correo}\n\n"
            "Ahora puedes hacerme preguntas como:\n"
            "👉 '¿Qué cursos tengo?'\n"
            "👉 '¿Cuándo termina el curso de Algoritmos?'"
        )
    else:
        update.message.reply_text("⚠️ Ese no parece un correo válido. Intenta de nuevo.")


def handle_question(update, context):
    global jwt_token
    chat_id = update.effective_chat.id
    pregunta = update.message.text

    if chat_id not in user_sessions:
        update.message.reply_text("⚠️ Primero envíame tu correo institucional antes de hacer preguntas.")
        return

    correo = user_sessions[chat_id]

    if not jwt_token:
        obtener_jwt()

    try:
        payload = {"correo": correo, "pregunta": pregunta}
        headers = {"Authorization": f"Bearer {jwt_token}"} if jwt_token else {}

        response = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=40)
        data = response.json()

        if data.get("status") == "success":
            update.message.reply_text(f"🤖 {data['resultado']}")
        else:
            update.message.reply_text(f"❌ Error: {data.get('error', 'Desconocido')}")
    except Exception as e:
        update.message.reply_text(f"⚠️ No pude conectar con el servidor: {e}")


# ============================
# MAIN
# ============================
def main():
    print("🚀 Iniciando EduConnect Bot...")
    obtener_jwt()

    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex(r"@"), handle_email))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_question))

    print("✅ Bot ejecutándose... Ctrl+C para detener.")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
