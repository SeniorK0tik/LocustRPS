from typing import Dict, Tuple

from locust import events, HttpUser, constant_pacing, task, LoadTestShape
from locust.clients import ResponseContextManager

import assertion
import time
import random
import kafka_sender
from config import cfg, logger
from functools import wraps
import os


def proceed_request(func):
    """
    The proceed_request function is a decorator that wraps the function it's applied to.
    It logs the time taken for each request, and sends an event to Datadog with information about
    the request. It also writes data about the transaction into InfluxDB.

    :param func: Store the function that is being decorated
    :return: A wrapper function
    :doc-author: Trelent | SenorK0tik
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        request_start_time: float = time.time()
        transaction = func(*args, **kwargs)
        processing_time: float = int((time.time() - request_start_time) * 1000)

        if func.__name__ == "send_payment":
            events.request.fire(
                request_type="KAFKA",
                name=func.__name__,
                response_time=processing_time,
                response_length=0,
                context=None,
                exception=None,
            )
        else:
            processing_time = int(transaction.elapsed.total_seconds() * 1000)


        # Сохраняем в influxDB
        cfg.influxdb.write(
            cfg.influx_bucket,
            cfg.influx_org,
            [{
                "measurement": f"{cfg.conf_name}_db",
                "tags": {"transaction_name": func.__name__},
                "time": time.time_ns(),
                "fields": {"response_time": processing_time},
            }],
        )

        logger.debug(
            f"""{func.__name__} status: {transaction.status_code 
            if func.__name__ != 'send_payment'
            else 'message delivered'}"""
        )

    return wrapper


class GlobalUser(HttpUser):
    wait_time = constant_pacing(cfg.pacing_sec)
    host: str = cfg.api_host

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """
        The on_test_start function is called when the test starts.
        It removes the log file from previous tests and logs that a new test has started.

        :param environment: Access the environment object
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: The environment object
        :doc-author: Trelent
        """
        os.remove("test_logs.log")
        logger.info("TEST STARTED")

    def on_start(self):
        """
        The on_start function is called when the spider starts.
        It's a good place to initialize your database connection, or open a file handle.

        :param self: Represent the instance of the class
        :return: The self
        :doc-author: Trelent | SenorK0tik
        """
        self.login()
        self.kfk: kafka_sender.KafkaSender = kafka_sender.KafkaSender()

    @task(5)
    @proceed_request
    def add_to_cart(self) -> ResponseContextManager:
        """
        The add_to_cart function adds a random product to the cart.

        :param self: Represent the instance of the class
        :return: The responsecontextmanager object
        :doc-author: Trelent | SenorK0tik
        """
        transaction = self.add_to_cart.__name__
        headers = {
            "accept": "text/html",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "token": self.token_id,
        }
        product: Dict[str, str | int] = random.choice(cfg.products)
        body = {
            "Product": product["Name"],
            "Prod_code": product["Code"],
        }
        with self.client.post(
                "/cart/add",
                headers=headers,
                json=body,
                catch_response=True,
                name=transaction
        ) as request:
            assertion.check_http_response(transaction, request)
        return request

    @task(5)
    @proceed_request
    def send_payment(self) -> None:
        """
        The send_payment function sends a payment to the Kafka topic.


        :param self: Represent the instance of the class
        :return: None
        :doc-author: Trelent | SenorK0tik
        """
        self.kfk.send()


    @proceed_request
    def login(self) -> ResponseContextManager:
        """
        The login function is used to log in a user.

        :param self: Bind the method to an object
        :return: The request object
        :doc-author: Trelent | SenorK0tik
        """
        with self.client.get(
                f"/login/demo-user",
                catch_response=True,
                name='login'
        ) as request:
            assertion.check_http_response('login', request)
        self.token_id = request.text
        return request


class StagesShape(LoadTestShape):
    stages = [
        {"duration": 20, "users": 2, "spawn_rate": 1},
        {"duration": 40, "users": 4, "spawn_rate": 1},
        {"duration": 60, "users": 8, "spawn_rate": 1},
        {"duration": 80, "users": 16, "spawn_rate": 1},
        {"duration": 100, "users": 20, "spawn_rate": 1},
    ]

    def tick(self) -> Tuple[int, int] | None:
        """
        The tick function is called every second by the simulation.
        It returns a tuple of two integers: (users, spawn_rate).
        The users value represents how many users should be active in the system at that time.
        The spawn_rate value represents how many new requests per second should be generated.

        :param self: Refer to the object that is calling the function
        :return: A tuple of two integers
        :doc-author: Trelent | SenorK0tik
        """
        run_time: float = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
