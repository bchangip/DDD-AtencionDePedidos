#!/usr/bin/env python
import pika
import multiprocessing
import json
import time
from concurrent.futures import TimeoutError

def callback(ch, method, properties, body):
  print("Message: ", body)

def main():
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
  channel = connection.channel()

  channel.exchange_declare(exchange='events',
                           exchange_type='fanout')

  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue

  channel.queue_bind(exchange='events',
                     queue=queue_name)

  print(' [*] Waiting for events. To exit press CTRL+C')

  channel.basic_consume(callback,
                        queue=queue_name,
                        no_ack=True)

  channel.start_consuming()

if __name__ == "__main__":
  main()