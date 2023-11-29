import os
import pika
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Завантаження змінних середовища
AMQP_USER = os.getenv('AMQP_USER')
AMQP_PASSWORD = os.getenv('AMQP_PASSWORD')
AMQP_ADDRESS = os.getenv('AMQP_ADDRESS')
AMQP_VHOST = os.getenv('AMQP_VHOST')
AMQP_PORT = os.getenv('AMQP_PORT')
EXTERNAL_API_URL = os.getenv('EXTERNAL_API_URL')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Налаштування Telegram бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Змінна для зберігання останнього повідомлення
last_message = None

@dp.message_handler()
async def echo(message: types.Message):
    global last_message
    last_message = message.text
    await message.answer(message.text)

# Функція для створення підключення до RabbitMQ
def create_rabbitmq_connection():
    credentials = pika.PlainCredentials(AMQP_USER, AMQP_PASSWORD)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=AMQP_ADDRESS,
            port=int(AMQP_PORT),
            virtual_host=AMQP_VHOST,
            credentials=credentials
        )
    )

# Підключення до RabbitMQ та створення черги
try:
    connection = create_rabbitmq_connection()
    channel = connection.channel()
    queue_name = 'my_queue'  # Можете змінити ім'я черги
    channel.queue_declare(queue=queue_name)
except pika.exceptions.AMQPConnectionError as error:
    print(f"Помилка підключення до RabbitMQ: {error}")
    exit(1)

# Callback функція для обробки повідомлень з RabbitMQ
def callback(ch, method, properties, body):
    global last_message
    if body.decode() == 'print' and last_message:
        print(last_message)
    elif body.decode() == 'send' and last_message:
        try:
            response = requests.post(EXTERNAL_API_URL, json={"message": last_message})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Помилка відправки запиту: {e}")

# Підписка на чергу
try:
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
except pika.exceptions.ChannelClosedByBroker as e:
    print(f"Помилка підписки на чергу: {e}")
    exit(1)

# Запуск бота і RabbitMQ слухача
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    channel.start_consuming()
