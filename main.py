import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor, callback_data
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN, URL_APP


bot = Bot(BOT_TOKEN )
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

callback = callback_data.CallbackData("button", "action")

with open("start_photo.png", "rb") as p_s:
    START_PHOTO = p_s.read()

with open("end_photo.png", "rb") as p_e:
    END_PHOTO = p_e.read()


async def on_startup(dp):
    await bot.set_webhook(URL_APP)


async def on_shutdown(dp):
    await bot.delete_webhook()


class UserInput(StatesGroup):
    WAITING_FOR_USR1 = State()
    WAITING_FOR_USR2 = State()
    WAITING_FOR_USR3 = State()
    WAITING_FOR_USR4 = State()


@dp.message_handler(commands=["start"])
async def on_start_msg(message:types.Message):

    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Введеня даних", callback_data=callback.new(action="btn_pressed"))
    markup.add(btn)

    await bot.send_photo(
                        chat_id=message.from_user.id, photo=START_PHOTO,
                        caption=f"Доброго дня {message.from_user.first_name}! "
                        f"Я - Ольга Алексєєва, маркетолог та підприємиця з 15+ річним досвідом. "
                        f"Дякую Вам за зацікавленість консультацією, впишіть будь ласка Ваші дані, аби ми могли"
                        f" запланувати зустріч",
                        reply_markup=markup
    )

    # await bot.send_message(chat_id=message.from_user.id,
    #                        text=f"Доброго дня {message.from_user.first_name}! "
    #                             f"Я - Ольга Алексєєва, маркетолог та підприємиця з 15+ річним досвідом. "
    #                             f"Дякую Вам за зацікавленість консультацією, впишіть будь ласка Ваші дані, аби ми могли"
    #                             f" запланувати зустріч",
    #                        reply_markup=markup)


@dp.callback_query_handler(callback.filter(action="btn_pressed"))
async def start_info_input(call_back_query: types.CallbackQuery):
    await UserInput.WAITING_FOR_USR1.set()

    await bot.send_message(chat_id=call_back_query.from_user.id,
                           text="Введіть ім'я та призвіще у форматі 'Ім'я, Призвіще'")


# Обработчик 1 состояния
@dp.message_handler(state=UserInput.WAITING_FOR_USR1)
async def get_name_surname_ask_for_inst_link(message:types.Message, state:FSMContext):
    await state.update_data(tg_usr_name=message.from_user.username)
    await state.update_data(user_name_surname=message.text)

    await bot.send_message(chat_id=message.from_user.id, text="Надішліть посилання на ваш інстаграм аккаунт")

    await UserInput.WAITING_FOR_USR2.set()


# Обработчик 2 состояния
@dp.message_handler(state=UserInput.WAITING_FOR_USR2)
async def get_link_ask_for_where_did_knew(message: types.Message, state: FSMContext):
    await state.update_data(link_inst=message.text)

    await bot.send_message(chat_id=message.from_user.id, text="Звідки дізнались про мене")

    await UserInput.WAITING_FOR_USR3.set()


@dp.message_handler(state=UserInput.WAITING_FOR_USR3)
async def get_info_where_knew_ask_for_niche(message:types.Message, state:FSMContext):
    await state.update_data(knew=message.text)

    await bot.send_message(chat_id=message.from_user.id, text="Ніша бізнесу")

    await UserInput.WAITING_FOR_USR4.set()


@dp.message_handler(state=UserInput.WAITING_FOR_USR4)
async def get_last_info_send_message(message:types.Message, state:FSMContext):
    await state.update_data(niche=message.text)

    await bot.send_photo(
                        chat_id=message.from_user.id,
                        photo=END_PHOTO,
                        caption="Дякую за довіру, зв’яжуся з вами протягом декількох"
                                " годин та оберемо дату для діагностичної зустрічі")

    # await bot.send_message(chat_id=message.from_user.id,
    #                        text="Дякую за довіру, зв’яжуся з вами протягом декількох"
    #                             " годин та оберемо дату для діагностичної зустрічі")

    # await UserInput.ITERNAL_FROM_MSG.set()
    await form_message(state)


# @dp.message_handler(state=UserInput.ITERNAL_FROM_MSG)
async def form_message(state:FSMContext):
    admin_id = "USER ID WHICH GET RESULT MESSAGE"
    data = await state.get_data()
    name = data["user_name_surname"]
    inst_link = data["link_inst"]
    how_did_he_knew = data["knew"]
    business_niche = data["niche"]
    usr_link = data["tg_usr_name"]

    msg = f"Ім'я/Призвище: {name}\n" \
          f"Inst: {inst_link}\n" \
          f"Дізнався завдяки: {how_did_he_knew}\n" \
          f"Ніша бізнессу: {business_niche}\n" \
          f"Telegram User: @{usr_link}"

    await bot.send_message(chat_id=admin_id, text=msg)
    # print(msg)
    await state.finish()

if __name__ == "__main__":
    executor.start_webhook(
        dispatcher=dp,
        webhook_path="",
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
