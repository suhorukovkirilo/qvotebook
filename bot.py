import telebot, json
from telebot import types
from time import sleep
from threading import Thread
from data import create_markup, get_request


class Bot:
    def __init__(self, key):
        self.bot = telebot.TeleBot(key)
        with open("base.json", "r", encoding='utf-8') as file:
            self.base = json.load(file)
        @self.bot.message_handler(commands=['start', 'exit'])
        def start(message):
            if str(message.from_user.id) not in self.base:
                if len(message.text.split()) > 1:
                    referrer = message.text.split()[1]
                else:
                    referrer = None
                self.base[str(message.from_user.id)] = {
                    'templates': {
                        'Стандартний': ['text']
                    },
                    'notes': {},
                    'input': {
                        'request': None,
                        'args': None
                    },
                    'referrer': referrer
                }
            self.bot.send_message(message.chat.id, text='Вітаємо вас у телеграм боті для створення і менеджування нотаток.', reply_markup=create_markup(["Додати нотатку", "Видалити нотатку", "Перейменувати нотатку", "Нотатки", "Додати шаблон"]))
            self.base[str(message.from_user.id)]['input'] = {'request': None, 'args': None}

        @self.bot.message_handler(commands=['create', 'c'])
        def create(message):
            message.text = "Додати нотатку"
            message_handler(message)
        @self.bot.message_handler(commands=['delete', 'd'])
        def delete(message):
            message.text = "Видалити нотатку"
            message_handler(message)
        @self.bot.message_handler(commands=['rename', 'r'])
        def rename(message):
            message.text = "Перейменувати нотатку"
            message_handler(message)
        @self.bot.message_handler(content_types=['text'])
        def message_handler(message):
            user, text, notes, templates, request, requests, request_args = get_request(message, self.base)
            if request == 'template name':
                if text not in templates:
                    request, request_args = 'template args', text
                    self.bot.send_message(user, text=f"Введіть пункти через пробіл\nЩоб вийти натисніть /exit")
                else:
                    self.bot.send_message(user, text=f"Шаьлон {text} вже присутній")
            elif request == 'template args':
                templates[request_args] = [arg for arg in text.split() if arg not in ["template", "all args"]]
                if len(templates[request_args]) != 0:
                    self.bot.send_message(user, text=f"Шаблон {request_args} успішно додано", reply_markup=create_markup("Додати нотатку", "Видалити нотатку", "Перейменувати нотатку", "Нотатки", "Додати шаблон"))
                    request, request_args = None, None
                else:
                    self.bot.send_message(user, text="Введіть більше пунктів")
            elif request == 'create note name':
                if text not in notes:
                    request, request_args = 'notes template', text
                    templates = [template for template in templates]
                    self.bot.send_message(user, text=f"Виберіть Шаблон для нотатки", reply_markup=create_markup(templates))
                else:
                    self.bot.send_message(user, text=f"Нотатка {text} вже існує")
            elif request == 'notes template':
                if text in templates:
                    notes[request_args] = {'template': text}
                    for arg in templates[text]:
                        notes[request_args][arg] = ''
                    note = request_args
                    request, request_args = 'notes settings', [note, [arg for arg in notes[note]]]
                    del request_args[1][0]
                    self.bot.send_message(user, f"Введіть {request_args[1][0]}")
                else:
                    self.bot.send_message(user, text=f"Шаблон {text} не знайдено")
            elif request == 'notes settings':
                notes[request_args[0]][request_args[1][0]] = text
                del request_args[1][0]
                if len(request_args[1]) == 0:
                    self.bot.send_message(user, text=f"Нотатку {request_args[0]} успішно додано", reply_markup=create_markup("Додати нотатку", "Видалити нотатку", "Перейменувати нотатку", "Нотатки", "Додати шаблон"))
                    request, request_args = None, None
                else:
                    self.bot.send_message(user, text=f"Введіть {request_args[1][0]}")
            elif request == 'del note name':
                if text in notes:
                    del notes[text]
                    self.bot.send_message(user, text=f"Нотатку {text} успішно видалено", reply_markup=create_markup("Додати нотатку", "Видалити нотатку", "Перейменувати нотатку", "Нотатки", "Додати шаблон"))
                    request = None
                else:
                    self.bot.send_message(user, text=f"Нотатку {text} не знайдено")
            elif request == 'rename note name':
                if text in notes:
                    request = 'rename note newname'
                    request_args = text
                    self.bot.send_message(user, text=f"Введіть назву нової нотатки для видалення")
                else:
                    self.bot.send_message(user, text=f"Нотатку {text} не знайдено")
            elif request == 'rename note newname':
                if text not in notes:
                    notes[text] = notes[request_args]
                    del notes[request_args]
                    self.bot.send_message(user, text=f"Ім'я нотатки успішно змінено")
                else:
                    self.bot.send_message(user, text=f"Нотатка {text} вже існує")
            elif text in notes:
                elements = [arg for arg in notes[text] if arg != 'template']
                elements.append("Нотатки")
                request = text
                self.bot.send_message(user, text=f"Нотатку {text} відкрито", reply_markup=create_markup(elements))
            elif request in notes and text in notes[request]:
                self.bot.send_message(user, text=notes[request][text])
            elif text == 'Додати шаблон':
                request = 'template name'
                self.bot.send_message(user, text='Введіть назву шаблону\nЩоб вийти натисніть /exit')
            elif text == 'Додати нотатку':
                request = 'create note name'
                self.bot.send_message(user, text='Введіть назву нової нотатки\nЩоб вийти натисніть /exit')
            elif text == 'Видалити нотатку':
                request = 'del note name'
                notes = [types.KeyboardButton(note) for note in notes]
                self.bot.send_message(user, text="Виберіть нотатку для видалення", reply_markup=create_markup(notes))
            elif text == 'Перейменувати нотатку':
                request = 'rename note name'
                notes = [types.KeyboardButton(note) for note in notes]
                self.bot.send_message(user, text="Виберіть нотатку для перейменування", reply_markup=create_markup(notes))
            elif text == 'Нотатки':
                if len(notes) > 0:
                    btns = [types.KeyboardButton(note) for note in notes]
                    btns.append(types.KeyboardButton("Головна"))
                    self.bot.send_message(user, text='Виберіть нотатку', reply_markup=create_markup(btns))
                else:
                    self.bot.send_message(user, text='Ви не додали жодної нотатки')
            elif text == 'Головна':
                start(message)
            else:
                self.bot.send_message(user, text="Невідомий запит")
            self.base[str(user)]['input']['request'], self.base[str(user)]['input']['args'] = request, request_args
    def savebase(self):
        while True:
            with open("base.json", "w", encoding='utf-8') as file:
                json.dump(self.base, file, ensure_ascii=False, indent=3)
            sleep(15)
    def run(self):
        Thread(target=self.savebase).start()
        while True:
            try:
                self.bot.polling(none_stop=True, timeout=1000000)
            except:
                pass
