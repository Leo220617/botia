import asyncio
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ============================
# CONFIGURACIÓN
# ============================
BOT_TOKEN = "8344802184:AAE8DEKP-8mKIFIF425X7g_OQCYZUBNG7qM"  # 👈 pon el real
LOGIN_URL = "https://edu-connect-be-e0f9gxg3akdnase4.centralus-01.azurewebsites.net/v1/users/login"
BACKEND_URL = "https://edu-connect-be-e0f9gxg3akdnase4.centralus-01.azurewebsites.net/api/bot/query-ai"

BOT_CREDENTIALS = {
    "username": "estudiante@edu-connect.com",
    "password": "password123"
}

jwt_token = None
user_sessions = {}

# ============================
# AUTENTICACIÓN JWT
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
            jwt_token = response.json().get("token") or response.json().get("jwt")

        if jwt_token:
            print("✅ JWT obtenido correctamente.")
        else:
            print("⚠️ No se encontró token.")
    except Exception as e:
        print("❌ Error al obtener JWT:", e)
        jwt_token = None


# ============================
# HANDLERS
# ============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 ¡Hola! Soy el asistente inteligente de EduConnect.\n\n"
        "Por favor, envíame tu correo institucional para identificarte (ejemplo: estudiante@edu-connect.com)."
    )


async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    correo = update.message.text.strip()
    if "@" in correo and "." in correo:
        user_sessions[update.effective_chat.id] = correo
        await update.message.reply_text(
            f"✅ Correo registrado: {correo}\n\n"
            "Ahora puedes hacerme preguntas como:\n"
            "👉 '¿Qué cursos tengo?'\n"
            "👉 '¿Cuándo termina el curso de Algoritmos?'"
        )
    else:
        await update.message.reply_text("⚠️ Ese no parece un correo válido. Intenta de nuevo.")


async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global jwt_token
    chat_id = update.effective_chat.id
    pregunta = update.message.text

    if chat_id not in user_sessions:
        await update.message.reply_text("⚠️ Primero envíame tu correo institucional antes de hacer preguntas.")
        return

    correo = user_sessions[chat_id]
    if not jwt_token:
        obtener_jwt()

    try:
        payload = {"correo": correo, "pregunta": pregunta}
        headers = {"Authorization": f"Bearer {jwt_token}"}

        response = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=40)
        data = response.json()

        if data.get("status") == "success":
            await update.message.reply_text(f"🤖 {data['resultado']}")
        else:
            await update.message.reply_text(f"❌ Error: {data.get('error', 'Desconocido')}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ No pude conectar con el servidor: {e}")


# ============================
# MAIN
# ============================
async def main():
    print("📦 python-telegram-bot versión moderna activa (20.8)")
    print("🚀 Iniciando EduConnect Bot...")
    obtener_jwt()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"@"), handle_email))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    print("✅ Bot corriendo correctamente en Render 24/7...")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
