import pika
import time
from models import Contact
from mongoengine import connect

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='email_queue')
connect(db="email_service", host="mongodb://localhost:27017")

def send_email_stub(contact_id):
    contact = Contact.objects(id=contact_id).first()
    if contact:
        print(f"Sending email to {contact.email}...", end=" ", flush=True)
        time.sleep(1)  # Імітація затримки
        contact.update(set__is_sent=True)
        print("Done!")

def callback(ch, method, properties, body):
    contact_id = body.decode()
    send_email_stub(contact_id)
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue='email_queue', on_message_callback=callback)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()