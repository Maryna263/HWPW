import pika
from faker import Faker
from models import Contact
from mongoengine import connect

fake = Faker()
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='email_queue')
connect(db="email_service", host="mongodb://localhost:27017")

def create_tasks(count=5):
    for _ in range(count):
        contact = Contact(
            full_name=fake.name(),
            email=fake.email(),
            additional_info="System Notification"
        ).save()
        
        channel.basic_publish(
            exchange='',
            routing_key='email_queue',
            body=str(contact.id)
        )
        print(f" [x] Sent ID: {contact.id}")

if __name__ == "__main__":
    create_tasks(10)
    connection.close()