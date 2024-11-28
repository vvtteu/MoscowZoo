import telebot
from config import TOKEN
from telebot import types
from animals import *
from questions import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name}!')
    bot.send_message(message.chat.id, 'На связи Московский зоопарк. Мы подготовили для вас интересную викторину «Твое тотемное животное Московского зоопарка». Благодаря этой викторине вы сможете узнать о животном, которое наиболее близкое вам по духу, а также ознакомиться с нашим проектом *«Возьми животное под опеку»*\n\n\
Желаем вам удачи!', parse_mode='Markdown')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать викторину!', callback_data='/victorina'))
    keyboard.add(types.InlineKeyboardButton('Узнать больше о проекте!', callback_data='/opeka'))
    bot.send_message(message.chat.id, 'Что бы начать викторину или узнать больше о проекте, нажмите на одну из кнопок ниже:', reply_markup=keyboard)


@bot.message_handler(commands=['opeka'])
def opeka(message: telebot.types.Message):
    text = "Опекунство в Московском зоопарке \n\
    Возьмите животное под опеку!\n\
    Участие в программе «Клуб друзей зоопарка» — это помощь в содержании наших обитателей, а также ваш личный вклад в дело сохранения биоразнообразия Земли и развитие нашего зоопарка.\n\
    Основная задача Московского зоопарка с самого начала его существования это — сохранение биоразнообразия планеты. Когда вы берете под опеку животное, вы помогаете нам в этом благородном деле. При нынешних темпах развития цивилизации к 2050 году с лица Земли могут исчезнуть около 10 000 биологических видов. Московский зоопарк вместе с другими зоопарками мира делает все возможное, чтобы сохранить их.\n\
    Традиция опекать животных в Московском зоопарке возникло с момента его создания в 1864г. Такая практика есть и в других зоопарках по всему миру.\n\
    В настоящее время опекуны объединились в неформальное сообщество — Клуб друзей Московского зоопарка. Программа «Клуб друзей» дает возможность опекунам ощутить свою причастность к делу сохранения природы, участвовать в жизни Московского зоопарка и его обитателей, видеть конкретные результаты своей деятельности.\n Опекать – значит помогать любимым животным. Можно взять под крыло любого обитателя Московского зоопарка, в том числе и того, кто живет за городом – в Центре воспроизводства редких видов животных под Волоколамском. Там живут и размножаются виды, которых нет в городской части зоопарка: величественные журавли стерхи, забавные дрофы, исчезнувшая в природе лошадь Пржевальского, изящные антилопы бонго и многие другие. Можете съездить на экскурсию в Центр и познакомиться с обитателями.\nПодробнее вы можете ознакомиться здесь: https://moscowzoo.ru/about/guardianship\n\nСвязаться с нами можно по телефону:\nТелефон: + 7 499 252 29 51"
    bot.send_message(message.chat.id, text)
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton('Начать викторину', callback_data='/victorina'))
    bot.send_message(message.chat.id, 'Чтобы начать викторину, нажмите на кнопку ниже:', reply_markup=keyboard)

    
user_points = {}
current_question = {}
@bot.message_handler(commands=['victorina'])
def victorina(message):
    user_id = message.chat.id
    user_points[message.chat.id] = 0
    current_question[user_id] = 0
    if len(questions) > 0:
        question = questions[0]['question']
        answers = questions[0]['answers']
        keyboard = types.InlineKeyboardMarkup()
        for answer in answers:
            keyboard.add(types.InlineKeyboardButton(answer, callback_data=answer))
        bot.send_message(message.chat.id, question, reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id, "Извините, в викторине нет доступных вопросов.")

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data in ['/victorina', '/menu', '/opeka']:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.data == '/victorina':
            victorina(call.message)
        elif call.data == '/opeka':
            opeka(call.message)
    else:
        user_id = call.message.chat.id

        if user_id not in current_question:
            current_question[user_id] = 0
            user_points[user_id] = 0  

        question_number = current_question[user_id]

        if call.data in questions[question_number]['answers']:
            points = questions[question_number]['points'][questions[question_number]['answers'].index(call.data)]
            user_points[user_id] += points

            current_question[user_id] += 1

            if current_question[user_id] < len(questions):
                question_number = current_question[user_id]
                question = questions[question_number]['question']
                answers = questions[question_number]['answers']
                keyboard = types.InlineKeyboardMarkup()
                for answer in answers:
                    keyboard.add(types.InlineKeyboardButton(answer, callback_data=answer))
                bot.answer_callback_query(call.id)
                bot.edit_message_text(question, call.message.chat.id, call.message.message_id, reply_markup=keyboard)
            else:
                totem_animal = get_totem_animal(user_points[user_id])
                text = totem_animal['text']
                photo_path = totem_animal['image']
                with open(photo_path, 'rb') as photo:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                    bot.send_photo(call.message.chat.id, photo, caption=text)
                    keyboard = types.InlineKeyboardMarkup()
                    keyboard.add(types.InlineKeyboardButton('Хочу попробовать еще раз!', callback_data='/victorina'))
                    keyboard.add(types.InlineKeyboardButton('Хочу подробнее узнать об опеке!', callback_data='/opeka'))
                    bot.send_message(call.message.chat.id, 'Поздравляем с успешным прохождением викторины! Вы можете попробовать еще раз или узнать подробнее о проекте «Возьми животное под опеку»:', reply_markup=keyboard)
        elif call.data == '/victorina':
            victorina(call.message)
        else:
            bot.answer_callback_query(call.id, "Неверный ответ. Пожалуйста, попробуйте снова.")


bot.polling(none_stop=True)