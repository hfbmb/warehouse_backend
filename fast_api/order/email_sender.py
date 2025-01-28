from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
# Создайте асинхронное средство планирования
scheduler = AsyncIOScheduler()
from apscheduler.triggers.interval import IntervalTrigger
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from ..config import MAIL_USERNAME,MAIL_PASSWORD,MAIL_SERVER,SMTP_PORT


scheduler = AsyncIOScheduler()


async def send_email_to_client(email_data:dict):
    conf = ConnectionConfig(
        # email_data["office_email"]
        # email_data["office_password"]
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM="noreply@prometeochain.io",
    MAIL_PORT=SMTP_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_STARTTLS=False,  # Add this line
    MAIL_SSL_TLS=False,  # Add this line 
    )
    print("hello worls")
    # Конфигурация FastMail
    fastmail = FastMail(conf)
    message = MessageSchema(
        subject=email_data["subject"],
        # email_data["recipient_email"]
        recipients=[email_data["recipient_email"]],
        body=email_data["description"],
        subtype="html"
    )
    await fastmail.send_message(message, MessageType.plain)

    
scheduler.start()

# Дождитесь выполнения всех задач и затем завершите приложение
# try:
#     asyncio.get_event_loop().run_forever()
# except (KeyboardInterrupt, SystemExit):
#     print("Завершение работы...")
#     scheduler.shutdown()