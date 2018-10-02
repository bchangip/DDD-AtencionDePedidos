#!/usr/bin/env python
import pika
import multiprocessing
import json
import time
from pymongo import MongoClient
from bson.objectid import ObjectId

def sendMessages(messages):
  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  channel.exchange_declare(exchange='events',
                           exchange_type='fanout')

  for message in messages:
    channel.basic_publish(exchange='events',
                          routing_key='',
                          body=json.dumps(message))
  print(" [x] Sent %r" % message)
  connection.close()

def inventoryInfoHandler(body):
  print("Handling inventory-info request")
  print(" [x] %r on process %r" % (body, multiprocessing.current_process()))
  orders = MongoClient(host="mongodb").orders.orders
  orderObject = orders.find_one({"_id": ObjectId(body['order-id'])})
  print('products', orderObject['products'])
  for product in filter(lambda x: x["product"] == body['product'], orderObject['products']):
    print('product', product)
    product['available'] = body['available']
  orders.replace_one({"_id": ObjectId(body['order-id'])}, orderObject)
  print("inventory-info processed")

def promotionsInfoHandler(body):
  print("Handling promotions-info request")
  print(" [x] %r on process %r" % (body, multiprocessing.current_process()))
  print("Going to sleep 2 seconds.")
  time.sleep(2)
  print("promotions-info processed")

def receiptHandler(body):
  print("Handling receipt request")
  print(" [x] %r on process %r" % (body, multiprocessing.current_process()))
  print("Going to sleep 2 seconds.")
  time.sleep(2)
  print("receipt processed")

def webCreateOrderHandler(body):
  print("Handling web-create-order request")
  print(" [x] %r on process %r" % (body, multiprocessing.current_process()))
  print("Going to sleep 2 seconds.")
  orders = MongoClient(host="mongodb").orders.orders
  insertionOrder = {
    "customer": body['customer'],
    "nit": body['nit'],
    "products": list(map(lambda x: {"product": x['product'], "quantity": x['quantity'], 'available': False}, body['products'])),
    "status": "Ordenando",
    "allAvailable": False
  }
  print('insertionOrder', insertionOrder)
  insertResponse = orders.insert_one(insertionOrder)
  insertedId = insertResponse.inserted_id
  messages = [{
    "type": "check-inventory",
    "order-id": str(insertedId),
    "product": product['product']
  } for product in body['products']]
  messages.append({
    "type": "check-promotions",
    "order-id": str(insertedId),
    "customer": body['customer']
  })
  messages.append({
    "type": "web-create-order-ok",
    "order-id": str(insertedId)
  })
  messages.append({
    "type": "generate-receipt",
    "order-id": str(insertedId),
    "customer": body['customer'],
    "nit": body['nit'],
    "products": body['products']
  })
  sendMessages(messages)

def webCheckOrderStatusHandler(body):
  print("Handling web-check-order-status request")
  print(" [x] %r on process %r" % (body, multiprocessing.current_process()))
  orders = MongoClient(host="mongodb").orders.orders
  orderObject = orders.find_one({"_id": ObjectId(body['order-id'])})
  if(orderObject != None):
    sendMessages([{
      "type": "web-order-status",
      "order-id": body['order-id'],
      "status": orderObject['status']
    }])
  else:
    sendMessages([{
      "type": "web-order-status",
      "order-id": body['order-id'],
      "status": "Id not found"
    }])

def asyncCallback(ch, method, properties, body):
  global pool
  body = json.loads(body)
  if body['type'] == "inventory-info":
    pool.apply_async(inventoryInfoHandler, (body,))
  elif body['type'] == "promotions-info":
    pool.apply_async(promotionsInfoHandler, (body,))
  elif body['type'] == "receipt":
    pool.apply_async(receiptHandler, (body,))
  elif body['type'] == "web-create-order":
    pool.apply_async(webCreateOrderHandler, (body,))
  elif body['type'] == "web-check-order-status":
    pool.apply_async(webCheckOrderStatusHandler, (body,))

def main():
  global pool

  workers = 10
  pool = multiprocessing.Pool(processes=workers)

  connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
  channel = connection.channel()

  channel.exchange_declare(exchange='events',
                           exchange_type='fanout')

  result = channel.queue_declare(exclusive=True)
  queue_name = result.method.queue

  channel.queue_bind(exchange='events',
                     queue=queue_name)

  print(' [*] Waiting for events. To exit press CTRL+C')

  channel.basic_consume(asyncCallback,
                        queue=queue_name,
                        no_ack=True)

  channel.start_consuming()

if __name__ == "__main__":
  main()