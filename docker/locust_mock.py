#!/usr/bin/env python
# coding: utf-8
# Rebuild docker -> docker-compose up -d --no-deps --build mock
from typing import Dict

from fastapi import FastAPI, Request
import base64
import random
import json


app = FastAPI()


# Код с ошибкой
# @app.post("/cart/add")
# async def add_to_cart(request: Request) -> str:
#     products: Dict[str, str | int] = json.loads(await request.body())
#     prod_name: str = products['Product']
#     prod_code: int = products['Prod_code']
#     answers = [
#         f"Товар #{prod_code} - '{prod_name}' добавлен в корзину",
#         "Ошибка добавления товара",
#         ]
#     return random.choice(answers)


# Корректный
@app.post("/cart/add")
async def add_to_cart(request: Request) -> str:
    products: Dict[str, str | int] = json.loads(await request.body())
    prod_name: str = products['Product']
    prod_code: int = products['Prod_code']
    answer = f"Товар #{prod_code} - '{prod_name}' добавлен в корзину"

    return answer


@app.get("/login/{username}")
def token(username: str):
    return f"Token {base64.standard_b64encode(username.encode('utf-8'))}"
