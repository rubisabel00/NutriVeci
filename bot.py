import sys
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.error import Conflict
from recipe_recommender import RecipeRecommender
from menu_planner import MenuPlanner
from health_advisor import HealthAdvisor
from user_profile import UserProfile

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "7863497038:AAEdk_qpb7u_qPi_-lWBHdoWAC3wtSesk1Y"

# Estados para la conversación
NOMBRE, EDAD, CONDICIONES, MENU_SELECTION = range(4)

# Inicializar componentes
user_manager = UserProfile()
recipe_recommender = RecipeRecommender()
menu_planner = MenuPlanner()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu asistente nutricional. Puedes usar comandos o números:\n\n"
        "1 o /perfil - Configurar tu nombre\n"
        "2 o /receta - Recomendar recetas saludables\n"
        "3 o /menu - Generar un menú semanal\n"
        "4 o /consejo - Obtener consejos nutricionales"
    )

async def perfil_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profile'] = {}
    await update.message.reply_text(
        "Vamos a configurar tu perfil de salud 📋\n"
        "Por favor, dime tu nombre:"
    )
    return NOMBRE

async def perfil_nombre(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profile']['name'] = update.message.text
    await update.message.reply_text(
        f"Gracias {update.message.text}! 😊\n"
        "Ahora dime tu edad:"
    )
    return EDAD

async def perfil_edad(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        edad = int(update.message.text)
        if edad < 0 or edad > 120:
            await update.message.reply_text("Por favor ingresa una edad válida (entre 0 y 120 años)")
            return EDAD
        
        context.user_data['profile']['age'] = edad
        keyboard = [
            ['Diabetes'],
            ['Hipertensión'],
            ['Celiaquía'],
            ['Intolerancia a la lactosa'],
            ['Alergia a mariscos'],
            ['Alergia a nueces'],
            ['Ninguna condición']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "¿Tienes alguna condición de salud que debamos tener en cuenta?",
            reply_markup=reply_markup
        )
        return CONDICIONES
    except ValueError:
        await update.message.reply_text("Por favor ingresa solo números para la edad")
        return EDAD

async def perfil_condiciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    respuesta = update.message.text
    profile = context.user_data['profile']
    user_id = update.effective_user.id
    
    if respuesta != 'Ninguna condición':
        profile['health_conditions'] = [respuesta]
    else:
        profile['health_conditions'] = []

    user_manager.save_profile(user_id, profile)
    
    mensaje = (
        f"¡Perfil completado! ✅\n\n"
        f"📝 Nombre: {profile['name']}\n"
        f"🎂 Edad: {profile['age']} años\n"
    )
    
    if profile['health_conditions']:
        mensaje += f"🏥 Condición de salud: {', '.join(profile['health_conditions'])}"
    else:
        mensaje += "🏥 Sin condiciones de salud específicas"
    
    mensaje += "\n\nAhora puedo recomendarte recetas adaptadas a tu perfil! 🍽️"
    
    await update.message.reply_text(mensaje, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Configuración de perfil cancelada.'
    )
    return ConversationHandler.END

async def recommend_recipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_profile = user_manager.get_profile(user_id)
    
    if not user_profile:
        await update.message.reply_text(
            "No tienes un perfil configurado. Usa /perfil para registrar tu nombre."
        )
        return
    
    recipe = recipe_recommender.get_recommendation()
    await update.message.reply_text(f"Hola {user_profile['name']}, {recipe}")

async def generate_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = menu_planner.generate_weekly_menu()
    context.user_data['last_menu'] = menu  # Guardamos el menú para referencia
    await update.message.reply_text(menu)
    return MENU_SELECTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        selection = int(update.message.text)
        if 1 <= selection <= 7:
            day = menu_planner.days[selection - 1]
            recipe = recipe_recommender.get_recommendation()
            await update.message.reply_text(f"Detalles para {day}:\n\n{recipe}")
        else:
            await update.message.reply_text("Por favor elige un número entre 1 y 7.")
    except ValueError:
        # Si no es un número, manejamos como comando normal
        await handle_message(update, context)

async def health_advice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    advisor = HealthAdvisor()
    advice = advisor.get_advice()
    await update.message.reply_text(advice)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "1":
        await perfil_inicio(update, context)
    elif text == "2":
        await recommend_recipe(update, context)
    elif text == "3":
        await generate_menu(update, context)
    elif text == "4":
        await health_advice(update, context)
    elif text.isdigit() and 1 <= int(text) <= 7:
        await handle_menu_selection(update, context)

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()

        # Manejador de conversación para el perfil
        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('perfil', perfil_inicio),
                MessageHandler(filters.Regex('^1$'), perfil_inicio)
            ],
            states={
                NOMBRE: [MessageHandler(filters.TEXT & ~filters.COMMAND, perfil_nombre)],
                EDAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, perfil_edad)],
                CONDICIONES: [MessageHandler(filters.TEXT & ~filters.COMMAND, perfil_condiciones)],
                MENU_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)]
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )

        # Registrar handlers
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("receta", recommend_recipe))
        application.add_handler(CommandHandler("menu", generate_menu))
        application.add_handler(CommandHandler("consejo", health_advice))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Iniciar el bot
        print("Iniciando el bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    except Conflict as e:
        print("Error: Ya hay una instancia del bot ejecutándose. Por favor, cierra la otra instancia antes de iniciar una nueva.")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()