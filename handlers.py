from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from keyboards import main_menu_keyboard
from database import add_workout, get_workouts, add_nutrition, get_nutrition, add_weight, get_weight_history, get_user_id, add_user, update_user_height, get_user_height, add_reminder, get_reminders, add_water_intake, get_daily_water_intake, add_ai_message, get_ai_chat_history
import datetime
import os
from groq import Groq
import matplotlib.pyplot as plt
import io

router = Router()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if GROQ_API_KEY:
    groq_client = Groq(api_key=GROQ_API_KEY)
else:
    groq_client = None
    print("GROQ_API_KEY not found. AI features will be disabled.")

# FSM States
class Form(StatesGroup):
    waiting_for_day = State()
    waiting_for_weight_input = State()
    waiting_for_height_input = State()
    waiting_for_food_input = State()
    waiting_for_reminder_time = State()
    waiting_for_reminder_message = State()
    waiting_for_ai_question = State()
    waiting_for_water_amount = State()

# Hardcoded workout plan for demonstration
WORKOUT_PLAN = {
    "dushanba": {
        "text": "Ko\"krak va Triceps:\n- Bench Press: 4x8\n- Incline Dumbbell Press: 3x10\n- Cable Crossover: 3x12\n- Triceps Pushdown: 3x10\n- Overhead Extension: 3x12",
        "videos": {
            "Bench Press": "https://www.youtube.com/watch?v=gpm_e0J91yE",
            "Incline Dumbbell Press": "https://www.youtube.com/watch?v=0G2_XV_Y7Pg",
            "Cable Crossover": "https://www.youtube.com/watch?v=ta4b-sQxQhM",
            "Triceps Pushdown": "https://www.youtube.com/watch?v=g_hK7Jb_f08",
            "Overhead Extension": "https://www.youtube.com/watch?v=N_j_20Q03_w"
        }
    },
    "seshanba": {
        "text": "Orqa va Biceps:\n- Pull-ups: 4xMax\n- Barbell Row: 3x10\n- Lat Pulldown: 3x12\n- Bicep Curls: 3x10\n- Hammer Curls: 3x12",
        "videos": {
            "Pull-ups": "https://www.youtube.com/watch?v=eGo4h111624",
            "Barbell Row": "https://www.youtube.com/watch?v=R0_J0y5y250",
            "Lat Pulldown": "https://www.youtube.com/watch?v=APG1x_s_G0Q",
            "Bicep Curls": "https://www.youtube.com/watch?v=s_J0n2c_m_c",
            "Hammer Curls": "https://www.youtube.com/watch?v=zC3JV-v761U"
        }
    },
    "chorshanba": {"text": "Dam olish kuni", "videos": {}},
    "payshanba": {
        "text": "Yelka va Oyoq:\n- Overhead Press: 4x8\n- Lateral Raises: 3x12\n- Front Raises: 3x12\n- Squats: 4x8\n- Leg Press: 3x10\n- Calf Raises: 3x15",
        "videos": {
            "Overhead Press": "https://www.youtube.com/watch?v=B-dhb_JgY2E",
            "Lateral Raises": "https://www.youtube.com/watch?v=3VcKaXSYrFI",
            "Front Raises": "https://www.youtube.com/watch?v=D-wQ1Fv4f1E",
            "Squats": "https://www.youtube.com/watch?v=ultWZbPWq_c",
            "Leg Press": "https://www.youtube.com/watch?v=IZxyjW7MPJQ",
            "Calf Raises": "https://www.youtube.com/watch?v=y3-f-20eF1c"
        }
    },
    "juma": {
        "text": "Butun tana (Full Body):\n- Deadlifts: 3x5\n- Military Press: 3x8\n- Bent-over Rows: 3x10\n- Lunges: 3x10 (har bir oyoq)\n- Plank: 3x60s",
        "videos": {
            "Deadlifts": "https://www.youtube.com/watch?v=ytGaGIn3Sj8",
            "Military Press": "https://www.youtube.com/watch?v=2yGf3x0_g8M",
            "Bent-over Rows": "https://www.youtube.com/watch?v=vT2Gf5-19jA",
            "Lunges": "https://www.youtube.com/watch?v=QO8_f4j1_o8",
            "Plank": "https://www.youtube.com/watch?v=ASdvN_X6bYc"
        }
    },
    "shanba": {
        "text": "Kardio va Qorin:\n- Yugurish: 30 min\n- Velosiped: 20 min\n- Crunch: 3x20\n- Leg Raises: 3x15",
        "videos": {
            "Yugurish": "https://www.youtube.com/watch?v=9F025b34018",
            "Velosiped": "https://www.youtube.com/watch?v=P_X0x9y4y_o",
            "Crunch": "https://www.youtube.com/watch?v=X_9hPj0-720",
            "Leg Raises": "https://www.youtube.com/watch?v=JB2oyGxIAFU"
        }
    },
    "yakshanba": {"text": "Dam olish kuni", "videos": {}}
}

# Function to generate weight chart
async def generate_weight_chart(user_id):
    history = get_weight_history(user_id)
    if not history:
        return None

    dates = [datetime.datetime.strptime(item[0], "%Y-%m-%d") for item in history]
    weights = [item[1] for item in history]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, weights, marker=\'o\', linestyle=\'-\", color=\'b\')
    plt.title(\'Vazn O\\"zgarishi Tarixi\')
    plt.xlabel(\'Sana\')
    plt.ylabel(\'Vazn (kg)\')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format=\'png\')
    buf.seek(0)
    plt.close()
    return buf

# Mashqlar Rejasi
@router.message(F.text == "Mashqlar Rejasi")
async def handle_workout_plan_request(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_day)
    await message.answer("Qaysi kun uchun mashqlar rejasini ko\"rmoqchisiz? (Masalan: Dushanba, Seshanba)")

@router.message(Form.waiting_for_day)
async def show_exercises_for_day(message: types.Message, state: FSMContext):
    day = message.text.lower()
    if day in WORKOUT_PLAN:
        workout_info = WORKOUT_PLAN[day]
        response_text = workout_info["text"]
        
        inline_keyboard_buttons = []
        for exercise, url in workout_info["videos"].items():
            inline_keyboard_buttons.append([types.InlineKeyboardButton(text=exercise, url=url)])
        
        if inline_keyboard_buttons:
            reply_markup = types.InlineKeyboardMarkup(inline_keyboard=inline_keyboard_buttons)
            await message.answer(response_text, reply_markup=reply_markup)
        else:
            await message.answer(response_text)
    else:
        await message.answer("Kechirasiz, bunday kun uchun mashqlar rejasi topilmadi. Iltimos, hafta kunini to\"g\"ri kiriting (Dushanba, Seshanba, Chorshanba, Payshanba, Juma, Shanba, Yakshanba).")
    await state.clear()

# Natijalarim
@router.message(F.text == "Natijalarim")
async def handle_my_results(message: types.Message):
    user_telegram_id = message.from_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        add_user(user_telegram_id)
        user_id = get_user_id(user_telegram_id)

    weight_history = get_weight_history(user_id)
    if weight_history:
        response = "Sizning vazn tarixingiz:\n"
        for date, weight in weight_history:
            response += f"- {date}: {weight} kg\n"
        
        chart = await generate_weight_chart(user_id)
        if chart:
            await message.answer_photo(types.BufferedInputFile(chart.getvalue(), filename=\'weight_chart.png\'), caption=response)
        else:
            await message.answer(response)
    else:
        response = "Siz hali vazn ma\"lumotlarini kiritmagansiz. Vazningizni kiritish uchun /vazn buyrug\"idan foydalaning."
    await message.answer(response)

# Kkal Hisoblagich
@router.message(F.text == "Kkal Hisoblagich")
async def handle_kkal_calculator(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_food_input)
    await message.answer("Kunlik ovqatlanish ma\"lumotlarini kiritish uchun /ovqat buyrug\"idan foydalaning. Yoki to\"g\"ridan-to\"g\"ri kiriting (masalan: Non 100g 10p 5f 50c)")

# Vazn kiritish komandasi
@router.message(Command("vazn"))
async def enter_weight(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_weight_input)
    await message.answer("Iltimos, vazningizni kiriting (masalan: 75.5)")

@router.message(Form.waiting_for_weight_input)
async def process_weight(message: types.Message, state: FSMContext):
    try:
        weight = float(message.text)
        user_telegram_id = message.from_user.id
        user_id = get_user_id(user_telegram_id)
        if not user_id:
            add_user(user_telegram_id)
            user_id = get_user_id(user_telegram_id)

        user_height = get_user_height(user_telegram_id)
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        add_weight(user_id, today, weight)
        
        response = f"Vazningiz {weight} kg muvaffaqiyatli saqlandi!"
        
        if user_height and user_height > 0:
            bmi = weight / ((user_height / 100) ** 2)
            bmi_category = ""
            if bmi < 18.5: bmi_category = "Vazn yetishmovchiligi"
            elif 18.5 <= bmi < 25: bmi_category = "Normal vazn"
            elif 25 <= bmi < 30: bmi_category = "Ortiqcha vazn"
            else: bmi_category = "Semizlik"
            
            response += f"\n\nSizning BMI: {bmi:.2f} ({bmi_category})"
            
        await message.answer(response)

    except ValueError:
        await message.answer("Noto\"g\"ri format. Iltimos, faqat raqam kiriting (masalan: 75.5).")
    finally:
        await state.clear()

# Ovqatlanish kiritish komandasi
@router.message(Command("ovqat"))
async def enter_food_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_food_input)
    await message.answer("Iltimos, ovqatlanish ma\"lumotlarini kiriting (masalan: Non 100g 10p 5f 50c)")

@router.message(Form.waiting_for_food_input)
async def process_food(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split()
        if len(parts) != 5:
            raise ValueError("Noto\"g\"ri format")

        food_item = parts[0]
        protein = float(parts[2].replace(\'p\', \'\'))
        fat = float(parts[3].replace(\'f\', \'\'))
        carbs = float(parts[4].replace(\'c\', \'\'))

        user_telegram_id = message.from_user.id
        user_id = get_user_id(user_telegram_id)
        if not user_id:
            add_user(user_telegram_id)
            user_id = get_user_id(user_telegram_id)

        today = datetime.date.today().strftime("%Y-%m-%d")
        add_nutrition(user_id, today, food_item, protein, fat, carbs)
        await message.answer(f"Ovqatlanish ma\"lumotlari muvaffaqiyatli saqlandi: {food_item}, O:{protein}, Y:{fat}, U:{carbs}")
    except ValueError:
        await message.answer("Noto\"g\"ri format. Iltimos, quyidagi formatda kiriting: Non 100g 10p 5f 50c")
    finally:
        await state.clear()

# Yangi komandalar
@router.message(Command("bmi"))
async def bmi_command(message: types.Message, state: FSMContext):
    user_telegram_id = message.from_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        add_user(user_telegram_id)
        user_id = get_user_id(user_telegram_id)

    height = get_user_height(user_telegram_id)
    if height and height > 0:
        await state.set_state(Form.waiting_for_weight_input)
        await message.answer(f"Bo\"yingiz {height} sm. Iltimos, vazningizni kiriting (masalan: 75.5) BMI hisoblash uchun.")
    else:
        await state.set_state(Form.waiting_for_height_input)
        await message.answer("BMI hisoblash uchun avval bo\"yingizni santimetrda kiriting (masalan: 175).")

@router.message(Form.waiting_for_height_input)
async def process_height_for_bmi(message: types.Message, state: FSMContext):
    try:
        height = float(message.text)
        if height <= 0:
            raise ValueError
        update_user_height(message.from_user.id, height)
        await state.set_state(Form.waiting_for_weight_input)
        await message.answer(f"Bo\"yingiz {height} sm saqlandi. Endi vazningizni kiriting (masalan: 75.5) BMI hisoblash uchun.")
    except ValueError:
        await message.answer("Noto\"g\"ri format. Iltimos, bo\"yingizni santimetrda raqam bilan kiriting (masalan: 175).")

@router.message(Command("stats"))
async def stats_command(message: types.Message):
    user_telegram_id = message.from_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        add_user(user_telegram_id)
        user_id = get_user_id(user_telegram_id)

    weight_history = get_weight_history(user_id)
    if weight_history:
        response = "Oxirgi vazn tarixingiz:\n"
        for date, weight in weight_history:
            response += f"- {date}: {weight} kg\n"
        
        if len(weight_history) >= 2:
            diff = weight_history[-1][1] - weight_history[0][1] # Calculate difference from first to last entry
            if diff > 0:
                response += f"\nSiz {abs(diff):.1f} kg vazn olgansiz."
            elif diff < 0:
                response += f"\nSiz {abs(diff):.1f} kg vazn yo\"qotgansiz."
            else:
                response += f"\nVazningiz o\"zgarmagan."
        
        chart = await generate_weight_chart(user_id)
        if chart:
            await message.answer_photo(types.BufferedInputFile(chart.getvalue(), filename=\'weight_chart.png\'), caption=response)
        else:
            await message.answer(response)
    else:
        response = "Siz hali vazn ma\"lumotlarini kiritmagansiz. Vazningizni kiritish uchun /vazn buyrug\"idan foydalaning."
    await message.answer(response)

@router.message(Command("remind"))
async def remind_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_reminder_time)
    await message.answer("Eslatma vaqtini kiriting (masalan: 18:00).")

@router.message(Form.waiting_for_reminder_time)
async def process_reminder_time(message: types.Message, state: FSMContext):
    try:
        time_str = message.text
        datetime.datetime.strptime(time_str, "%H:%M").time()
        await state.update_data(reminder_time=time_str)
        await state.set_state(Form.waiting_for_reminder_message)
        await message.answer("Eslatma matnini kiriting.")
    except ValueError:
        await message.answer("Noto\"g\"ri vaqt formati. Iltimos, HH:MM formatida kiriting (masalan: 18:00).")

@router.message(Form.waiting_for_reminder_message)
async def process_reminder_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    reminder_time = data.get("reminder_time")
    reminder_message = message.text

    user_telegram_id = message.from_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        add_user(user_telegram_id)
        user_id = get_user_id(user_telegram_id)

    add_reminder(user_id, reminder_time, reminder_message)
    await message.answer(f"Eslatma {reminder_time} ga \"{reminder_message}\" matni bilan saqlandi.")
    await state.clear()

@router.message(Command("water"))
async def water_command(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_water_amount)
    await message.answer("Qancha suv ichdingiz (ml)? (Masalan: 500)")

@router.message(Form.waiting_for_water_amount)
async def process_water_amount(message: types.Message, state: FSMContext):
    try:
        amount_ml = int(message.text)
        if amount_ml <= 0:
            raise ValueError
        
        user_telegram_id = message.from_user.id
        user_id = get_user_id(user_telegram_id)
        if not user_id:
            add_user(user_telegram_id)
            user_id = get_user_id(user_telegram_id)
        
        today = datetime.date.today().strftime("%Y-%m-%d")
        add_water_intake(user_id, today, amount_ml)
        total_water = get_daily_water_intake(user_id, today)
        await message.answer(f"Siz {amount_ml} ml suv ichdingiz. Bugungi umumiy miqdor: {total_water} ml.")
    except ValueError:
        await message.answer("Noto\"g\"ri format. Iltimos, faqat butun son kiriting (masalan: 500).")
    finally:
        await state.clear()

@router.message(Command("ai"))
async def ai_command(message: types.Message, state: FSMContext):
    if not groq_client:
        await message.answer("AI funksiyasi hozirda mavjud emas. Iltimos, BOT_TOKEN va GROQ_API_KEY ni to\"g\"ri sozlang.")
        return
    await state.set_state(Form.waiting_for_ai_question)
    await message.answer("Menga savolingizni bering, men sizga yordam berishga harakat qilaman!")

@router.message(Form.waiting_for_ai_question)
async def process_ai_question(message: types.Message, state: FSMContext):
    if not groq_client:
        await message.answer("AI funksiyasi hozirda mavjud emas.")
        await state.clear()
        return

    user_telegram_id = message.from_user.id
    user_id = get_user_id(user_telegram_id)
    if not user_id:
        add_user(user_telegram_id)
        user_id = get_user_id(user_telegram_id)

    user_question = message.text
    add_ai_message(user_id, "user", user_question)

    chat_history = get_ai_chat_history(user_id)
    messages = []
    for role, content in chat_history:
        messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": user_question})

    try:
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192", # You can choose other models like mixtral-8x7b-32768, llama2-70b-4096
            temperature=0.7,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False
        )
        ai_response = chat_completion.choices[0].message.content
        add_ai_message(user_id, "assistant", ai_response)
        await message.answer(ai_response)
    except Exception as e:
        await message.answer(f"AI bilan bog\"lanishda xatolik yuz berdi: {e}")
    finally:
        await state.clear()

@router.message(Command("help"))
async def help_command(message: types.Message):
    help_text = (
        "**Mavjud komandalar:**\n"
        "/start - Botni ishga tushirish va asosiy menyuni ko\"rsatish\n"
        "/vazn - Vazningizni kiritish\n"
        "/ovqat - Ovqatlanish ma\"lumotlarini kiritish\n"
        "/bmi - Tana vazni indeksini (BMI) hisoblash\n"
        "/stats - Vazn tarixingizni grafik bilan ko\"rish\n"
        "/remind - Mashg\"ulot yoki ovqatlanish uchun eslatma o\"rnatish\n"
        "/water - Ichilgan suv miqdorini kiritish\n"
        "/ai - Sun\"iy intellektga savol berish\n"
        "/help - Ushbu yordam xabarini ko\"rsatish\n\n"
        "**Asosiy menyu tugmalari:**\n"
        "Mashqlar Rejasi - Kunlik mashqlar rejasini ko\"rish\n"
        "Natijalarim - Vazn tarixingizni ko\"rish\n"
        "Kkal Hisoblagich - Ovqatlanish ma\"lumotlarini kiritish"
    )
    await message.answer(help_text, parse_mode="Markdown")
