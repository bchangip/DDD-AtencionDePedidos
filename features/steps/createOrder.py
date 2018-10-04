from behave import *
from receiveSubscribe import webCreateOrderHandler
from pymongo import MongoClient
from bson.objectid import ObjectId

@given('a create order request')
def step(context):
  context.order = {
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
  insertedId, messages = webCreateOrderHandler(context.order, testMode=True)

  context.insertedId = insertedId
  context.messages = messages

@then('the order is stored')
def step(context):
  orders = MongoClient().orders.orders
  assert(orders.find({"_id": ObjectId(context.insertedId)}).count() == 1)

@then('messages are sent to other modules')
def step(context):
  messages = [{
    "type": "check-inventory",
    "order-id": str(context.insertedId),
    "product": product['product']
  } for product in context.order['products']]
  messages.append({
    "type": "check-promotions",
    "order-id": str(context.insertedId),
    "customer": context.order['customer']
  })
  messages.append({
    "type": "web-create-order-ok",
    "order-id": str(context.insertedId)
  })
  messages.append({
    "type": "generate-receipt",
    "order-id": str(context.insertedId),
    "customer": context.order['customer'],
    "nit": context.order['nit'],
    "products": context.order['products']
  })
  assert(messages == context.messages)

