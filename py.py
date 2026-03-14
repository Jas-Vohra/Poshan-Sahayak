import logging
import csv
import os
import datetime
import matplotlib
matplotlib.use('Agg') # Essential for Raspberry Pi
import matplotlib.pyplot as plt
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, 
    ContextTypes, 
    CommandHandler, 
    MessageHandler, 
    filters, 
    ConversationHandler
)
from twilio.rest import Client
from gtts import gTTS 



BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TWILIO_SID = "YOUR_TWILIO_SID_HERE"
TWILIO_AUTH = "YOUR_TWILIO_AUTH_HERE"
FROM_WHATSAPP = "whatsapp:+14155238886"  # Default Twilio Sandbox Number


FILE_NAME = "anganwadi_secure_data.csv"

AUTHORIZED_USERS = {
    "aww01": "sevika1",
    "jas": "admin123"
}

#definitions
(LOGIN_USER, LOGIN_PASS, MAIN_MENU, 
 REG_NAME, REG_PARENT, REG_PHONE, REG_DOB, 
 HEALTH_NAME, HEALTH_PHONE, HEALTH_AGE, HEALTH_WEIGHT, 
 VAC_NAME, VAC_PHONE, VAC_DOB, 
 MAT_NAME, MAT_MONTH, MAT_HB, MAT_BP, 
 RAT_ITEM, RAT_QTY, RAT_ACTION, 
 SEARCH_NAME,
 CHART_NAME, GPS_WAIT, PHOTO_WAIT) = range(25)

# helper functions

# 🧠 NEW: Smart Weight Logic
def get_min_healthy_weight(age_months):
    if age_months <= 1: return 3.0
    elif age_months <= 2: return 4.0
    elif age_months <= 4: return 5.5
    elif age_months <= 6: return 6.5
    elif age_months <= 9: return 7.5
    elif age_months <= 12: return 8.5
    elif age_months <= 24: return 10.0
    elif age_months <= 36: return 12.0
    else: return 14.0

# 🧠 NEW: Smart Vaccine Logic
def get_vaccine_due(age_months):
    if age_months < 1.5: 
        return "BCG, HepB-0, OPV-0", "Birth Dose"
    elif 1.5 <= age_months < 2.5: 
        return "Pentavalent-1, Rotavirus-1", "6 Week Dose"
    elif 2.5 <= age_months < 3.5: 
        return "Pentavalent-2, Rotavirus-2", "10 Week Dose"
    elif 3.5 <= age_months < 9: 
        return "Pentavalent-3, Rotavirus-3", "14 Week Dose"
    elif 9 <= age_months < 16: 
        return "Measles (MR-1), Vitamin A", "9 Month Dose"
    elif 16 <= age_months < 24: 
        return "Measles (MR-2), DPT Booster", "1.5 Year Booster"
    else:
        return "DPT Booster-2", "5 Year Booster"

def send_whatsapp_alert(to_number, message_body):
    try:
        clean_number = to_number.strip()
        if not clean_number.startswith('+'):
            clean_number = f"+91{clean_number}"
        
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            from_=FROM_WHATSAPP, 
            body=message_body, 
            to=f"whatsapp:{clean_number}"
        )
        print(f"✅ WhatsApp sent to {clean_number}")
        return True
    except Exception as e:
        print(f"❌ WhatsApp Failed: {e}")
        return False

async def send_audio_reply(update, context, text_to_speak, lang='en'):
    try:
        tts = gTTS(text=text_to_speak, lang=lang, slow=False)
        filename = f"voice_{datetime.datetime.now().strftime('%M%S')}.mp3"
        tts.save(filename)
        await update.message.reply_voice(voice=open(filename, 'rb'))
        if os.path.exists(filename): os.remove(filename)
    except Exception as e:
        print(f"Audio Error: {e}")

def save_to_csv(data_list):
    file_exists = os.path.isfile(FILE_NAME)
    try:
        with open(FILE_NAME, mode='a', newline='') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Timestamp", "Entered By", "Name", "Details", "Phone", "Category", "Status", "Action", "Meta"])
            writer.writerow(data_list)
        return True
    except PermissionError:
        return False

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛑 Operation Cancelled. Type /start to login.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# login systems
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔐 **POSHAN SAHAYAK**\n\nEnter User ID:", parse_mode='Markdown')
    return LOGIN_USER

async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['user_id'] = update.message.text
    await update.message.reply_text("🔑 Enter Password:")
    return LOGIN_PASS

async def verify_login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data['user_id']
    password = update.message.text
    if user_id in AUTHORIZED_USERS and AUTHORIZED_USERS[user_id] == password:
        await update.message.reply_text(f"✅ Login Successful.")
        await send_audio_reply(update, context, "Namaste. Poshan Sahayak mein swagat hai.", lang='hi')
        return await show_main_menu(update, context)
    else:
        await update.message.reply_text("❌ Invalid Credentials. Type /start to retry.")
        return ConversationHandler.END

# main menu
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ['1. Register Child', '2. Growth Check', '3. Vaccination'],
        ['4. Maternal Health', '5. Ration Mgmt', '6. 🔍 Search'],
        ['7. 📊 Growth Chart', '8. 📍 Verify Visit', '9. 📸 Evidence'],
        ['10. 📥 Export Data', '11. Logout']
    ]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("Select Option:", reply_markup=markup)
    return MAIN_MENU

async def menu_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if "11." in choice or "Logout" in choice:
        await update.message.reply_text("🔒 Logged out successfully.", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    elif "1." in choice:
        await update.message.reply_text("Child Name:", reply_markup=ReplyKeyboardRemove())
        return REG_NAME
    elif "2." in choice:
        await update.message.reply_text("Child Name:", reply_markup=ReplyKeyboardRemove())
        return HEALTH_NAME
    elif "3." in choice:
        await update.message.reply_text("Child Name:", reply_markup=ReplyKeyboardRemove())
        return VAC_NAME
    elif "4." in choice:
        await update.message.reply_text("Pregnant Woman Name:", reply_markup=ReplyKeyboardRemove())
        return MAT_NAME
    elif "5." in choice:
        await update.message.reply_text("Ration Item (Rice/Dal):", reply_markup=ReplyKeyboardRemove())
        return RAT_ITEM
    elif "6." in choice:
        await update.message.reply_text("🔍 Enter Name to Search:", reply_markup=ReplyKeyboardRemove())
        return SEARCH_NAME
    elif "7." in choice:
        await update.message.reply_text("Child Name for Graph:", reply_markup=ReplyKeyboardRemove())
        return CHART_NAME
    elif "8." in choice:
        loc_btn = [[KeyboardButton(text="📍 Send Location", request_location=True)]]
        markup = ReplyKeyboardMarkup(loc_btn, one_time_keyboard=True)
        await update.message.reply_text("Verify Location:", reply_markup=markup)
        return GPS_WAIT
    elif "9." in choice:
        await update.message.reply_text("📸 Upload Photo:", reply_markup=ReplyKeyboardRemove())
        return PHOTO_WAIT
    elif "10." in choice:
        if os.path.exists(FILE_NAME): 
            await update.message.reply_document(document=open(FILE_NAME, 'rb'))
        else:
            await update.message.reply_text("⚠️ No data file found.")
        return await show_main_menu(update, context)
    else:
        await update.message.reply_text("⚠️ Invalid option.")
        return await show_main_menu(update, context)

# comparitive vaccination alarms
async def vac_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['v_name'] = update.message.text
    await update.message.reply_text("📱 Parent WhatsApp:")
    return VAC_PHONE
async def vac_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['v_phone'] = update.message.text
    await update.message.reply_text("Child Age (Months):")
    return VAC_DOB
async def vac_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text)
    except:
        await update.message.reply_text("⚠️ Invalid Age. Try again.")
        return VAC_DOB
        
    name = context.user_data['v_name']
    phone = context.user_data['v_phone']
    user = context.user_data['user_id']
    
    # 🧠 SMART VACCINE FUNCTION
    vaccine_name, phase_name = get_vaccine_due(age)
    
    status = f"DUE: {vaccine_name}"
    msg = f"💉 **VACCINE REPORT**\nChild: {name}\nDue: {vaccine_name}\nPhase: {phase_name}"
    hindi_voice = f"Namaste. {name} ka {vaccine_name} ka teeka due hai. Kripya kal center aayen."
    
    # Send Voice
    await send_audio_reply(update, context, hindi_voice, lang='hi')
    
    # ✅ RESTORED ORIGINAL WHATSAPP FORMAT
    wa_body = (f"💉 *VACCINATION ALERT*\nChild: {name}\nDue: {vaccine_name}\nPhase: {phase_name}\nAction: Visit Anganwadi.")
    
    sent = send_whatsapp_alert(phone, wa_body)
    wa_status = "Msg Sent" if sent else "Failed"
        
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), f"TG:{user}", name, f"Age:{age}m", phone, "Vaccination", status, vaccine_name, wa_status])
    await update.message.reply_text(f"{msg}\n(WhatsApp: {wa_status})", parse_mode='Markdown')
    return await show_main_menu(update, context)

# health check
async def health_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['h_name'] = update.message.text
    await update.message.reply_text("📱 Parent WhatsApp:")
    return HEALTH_PHONE
async def health_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['h_phone'] = update.message.text
    await update.message.reply_text("Age (Months):")
    return HEALTH_AGE
async def health_get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: context.user_data['h_age'] = int(update.message.text)
    except: return HEALTH_AGE
    await update.message.reply_text("Weight (kg):")
    return HEALTH_WEIGHT

async def health_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try: weight = float(update.message.text)
    except: return HEALTH_WEIGHT
    
    age = context.user_data['h_age']
    name = context.user_data['h_name']
    phone = context.user_data['h_phone']
    user = context.user_data['user_id']
    
    # weight func
    min_w = get_min_healthy_weight(age)
    
    if weight < min_w:
        status = "SEVERE MALNUTRITION"
        msg = f"🚨 ALERT: {name} is Underweight! (Min: {min_w}kg)"
        voice_msg = f"Saavdhan! Bacha {name} kuposhit hai. Vajan kam hai."
        
        
        wa_body = (f"🚨 *URGENT HEALTH ALERT*\nChild: {name}\nStatus: SEVERE MALNUTRITION\nWeight: {weight}kg\nAction: Visit Anganwadi IMMEDIATELY.")
        
        send_whatsapp_alert(phone, wa_body)
        wa_status = "⚠️ ALERT SENT"
    else:
        status = "Healthy"
        msg = f"✅ {name} is Healthy."
        voice_msg = f"Badhai ho. {name} bilkul swasth hai."
        wa_status = "-"
    
    await send_audio_reply(update, context, voice_msg, lang='hi')    
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), f"TG:{user}", name, f"Age:{age}m", phone, "Checkup", f"Wt:{weight} ({status})", "Routine", wa_status])
    await update.message.reply_text(msg)
    
    
    return await show_main_menu(update, context)

# growth chart
async def chart_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    await update.message.reply_text(f"⏳ Generating Graph for {name}...")
    
    dates, weights = [], []
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 6 and name.lower() in row[2].lower():
                    if "Wt:" in row[6]:
                        dates.append(row[0].split(" ")[0]) 
                        try: 
                            w_val = float(row[6].split(" ")[0].replace("Wt:", ""))
                            weights.append(w_val)
                        except: continue
    
    if not weights:
        await update.message.reply_text("❌ No growth records found.")
        return await show_main_menu(update, context)
        
    plt.figure(figsize=(6, 4))
    plt.plot(dates, weights, marker='o', color='b', linestyle='-')
    plt.title(f"Growth Journey: {name}")
    plt.xlabel("Date")
    plt.ylabel("Weight (kg)")
    plt.grid(True)
    
    chart_filename = f"{name}_chart.png"
    plt.savefig(chart_filename)
    plt.close()
    
    await update.message.reply_photo(photo=open(chart_filename, 'rb'))
    if os.path.exists(chart_filename): os.remove(chart_filename)
    return await show_main_menu(update, context)

# registration
async def reg_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['reg_name'] = update.message.text
    await update.message.reply_text("Parent Name:")
    return REG_PARENT
async def reg_get_parent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['reg_parent'] = update.message.text
    await update.message.reply_text("📱 Parent WhatsApp:")
    return REG_PHONE
async def reg_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['reg_phone'] = update.message.text
    await update.message.reply_text("DOB (DD-MM-YYYY):")
    return REG_DOB
async def reg_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dob = update.message.text
    name = context.user_data['reg_name']
    phone = context.user_data['reg_phone']
    user = context.user_data['user_id']
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), f"TG:{user}", name, f"DOB:{dob}", phone, "Registration", "Active", "New", "-"])
    await update.message.reply_text(f"✅ Registered Successfully!")
    return await show_main_menu(update, context)

# maternal health

async def mat_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['m_name'] = update.message.text
    await update.message.reply_text("Pregnancy Month (1-9):")
    return MAT_MONTH
async def mat_get_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['m_month'] = update.message.text
    await update.message.reply_text("Hb Level (e.g., 10.5):")
    return MAT_HB
async def mat_get_hb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['m_hb'] = update.message.text
    await update.message.reply_text("Blood Pressure (e.g., 120/80):")
    return MAT_BP
async def mat_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bp = update.message.text
    name = context.user_data['m_name']
    month = context.user_data['m_month']
    hb = float(context.user_data['m_hb'])
    status = "ANEMIC Alert" if hb < 11.0 else "Healthy"
    advice = "⚠️ High Risk: Give Iron/Folic Acid." if hb < 11.0 else "✅ Normal Range."
    voice_msg = f"{name} ko khoon ki kami hai." if hb < 11.0 else "Maa aur bacha swasth hain."
    
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "TG", name, f"Mo:{month}|Hb:{hb}|BP:{bp}", "-", "Maternal", status, advice, "-"])
    await update.message.reply_text(f"📋 **Maternal Record**\nName: {name}\nStatus: {status}\n💡 Advice: {advice}", parse_mode='Markdown')
    await send_audio_reply(update, context, voice_msg, lang='hi')
    return await show_main_menu(update, context)

async def search_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_query = update.message.text.lower()
    results = []
    await update.message.reply_text(f"🔍 Searching for '{search_query}'...")
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) > 6 and search_query in row[2].lower():
                    info = f"👤 *{row[2]}* ({row[5]})\n   • Status: {row[6]}\n   • Details: {row[3]}\n   • Date: {row[0]}"
                    results.append(info)
    if results:
        msg = "✅ **Found Records:**\n\n" + "\n\n".join(results[-3:])
    else:
        msg = f"❌ No records found for '{search_query}'."
    await update.message.reply_text(msg, parse_mode='Markdown')
    return await show_main_menu(update, context)

async def gps_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.location:
        loc = update.message.location
        link = f"http://maps.google.com/?q={loc.latitude},{loc.longitude}"
        save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "TG", "WORKER", f"Lat:{loc.latitude}", "-", "Attendance", "Verified", "GPS Logged", link])
        await update.message.reply_text(f"✅ Location Verified.", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("❌ Location not received.")
    return await show_main_menu(update, context)

async def photo_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.photo[-1].get_file()
    fname = f"evidence_{datetime.datetime.now().strftime('%M%S')}.jpg"
    await file.download_to_drive(fname)
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "TG", "EVIDENCE", "Photo Uploaded", "-", "Audit", "Saved", fname, "-"])
    await update.message.reply_text(f"📸 Saved as {fname}")
    return await show_main_menu(update, context)

async def rat_get_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['r_item'] = update.message.text
    await update.message.reply_text("Qty (kg/packets):")
    return RAT_QTY
async def rat_get_qty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['r_qty'] = update.message.text
    k = [['Add (IN)', 'Distribute (OUT)']]
    await update.message.reply_text("Action:", reply_markup=ReplyKeyboardMarkup(k, one_time_keyboard=True))
    return RAT_ACTION
async def rat_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_to_csv([datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "TG", "INVENTORY", f"Qty:{context.user_data['r_qty']}", "-", "Ration", context.user_data['r_item'], update.message.text, "-"])
    await update.message.reply_text("Inventory Updated.")
    return await show_main_menu(update, context)

if __name__ == '__main__':
    print("🤖 POSHAN SAHAYAK (Smart Logic + Original Layout + Fixed Menu) ONLINE...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('cancel', cancel))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LOGIN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
            LOGIN_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, verify_login)],
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_router)],
            REG_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_get_name)],
            REG_PARENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_get_parent)],
            REG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_get_phone)],
            REG_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, reg_save)],
            HEALTH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, health_get_name)],
            HEALTH_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, health_get_phone)],
            HEALTH_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, health_get_age)],
            HEALTH_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, health_save)],
            VAC_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_name)],
            VAC_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_phone)],
            VAC_DOB: [MessageHandler(filters.TEXT & ~filters.COMMAND, vac_save)],
            MAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_get_name)],
            MAT_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_get_month)],
            MAT_HB: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_get_hb)],
            MAT_BP: [MessageHandler(filters.TEXT & ~filters.COMMAND, mat_save)],
            RAT_ITEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, rat_get_item)],
            RAT_QTY: [MessageHandler(filters.TEXT & ~filters.COMMAND, rat_get_qty)],
            RAT_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, rat_save)],
            SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_record)],
            CHART_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, chart_get_name)],
            GPS_WAIT: [MessageHandler(filters.LOCATION, gps_save)],
            PHOTO_WAIT: [MessageHandler(filters.PHOTO, photo_save)]
        },
        fallbacks=[CommandHandler('start', start), CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    application.run_polling()