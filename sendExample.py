#!/usr/bin/env python
import pika
import sys
import json

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.exchange_declare(exchange='events',
                         exchange_type='fanout')

message = {
  "type": "web-create-order",
  "customer": "Pablo Barreno",
  "nit": "12345-6",
  "products": [
    {
      "product": "Producto 1",
      "quantity": 2
    },
    {
      "product": "Producto 2",
      "quantity": 1
    }
  ]
}

# message = {
#   "type": "web-check-order-status",
#   "order-id": "5ba3249a80e841381069ccf8"
# }

# message = {
#   "type": "inventory-info",
#   "order-id": "5ba3343380e8412be0bdb228",
#   "product": "Producto 1",
#   "available": True
# }

channel.basic_publish(exchange='events',
                      routing_key='',
                      body=json.dumps(message))
print(" [x] Sent %r" % message)
connection.close()