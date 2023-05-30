from typing import Tuple

from locust import events, task, constant_pacing, User, LoadTestShape
import time
import os
from config import cfg, logger
import kafka_sender


class KafkaUser(User):
    wait_time = constant_pacing(cfg.pacing_sec)

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """
        The on_test_start function is called when the test starts.
        It removes the log file from previous tests and logs that a new test has started.

        :param environment: Access the environment object
        :param **kwargs: Pass a variable number of keyword arguments to a function
        :return: The environment object
        :doc-author: Trelent | SenorK0tik
        """
        os.remove("test_logs.log")
        logger.info("TEST STARTED")

    def on_start(self):
        self.kfk: kafka_sender.KafkaSender = kafka_sender.KafkaSender()

    @task
    def send_payment(self) -> None:
        """
        The send_payment function sends a payment to the Kafka broker.

        :param self: Represent the instance of the class
        :return: None
        :doc-author: Trelent
        """
        request_start_time: float = time.time()
        self.kfk.send()
        processing_time: float = int((time.time() - request_start_time) * 1000)
        events.request.fire(
            request_type="KAFKA",
            name='send_payment',
            response_time=processing_time,
            response_length=0,
            context=None,
            exception=None,
        )  # Marks processing time

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        """
        The on_test_stop function is called when the test has finished.
        It can be used to clean up any resources that were created during the test.

        :param environment: Access the environment object
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: A dictionary with the following information:
        :doc-author: Trelent | SenorK0tik
        """
    logger.info("TEST STOPPED")


class StagesShape(LoadTestShape):
    stages = [
        {"duration": 20, "users": 1, "spawn_rate": 1},
        {"duration": 40, "users": 2, "spawn_rate": 1},
        {"duration": 60, "users": 4, "spawn_rate": 1},
        {"duration": 80, "users": 8, "spawn_rate": 1},
        {"duration": 100, "users": 10, "spawn_rate": 1},
    ]

    def tick(self) -> Tuple[int, int] | None:
        """
        The tick function is called every second by the simulation.
        It returns a tuple of (users, spawn_rate) where users is the number of users to be spawned in that second and spawn_rate is how often they should be spawned.
        The tick function can return None if no more users should be spawned.

        :param self: Refer to the object itself
        :return: A tuple of the number of users and spawn rate
        :doc-author: Trelent
        """
        run_time: float = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
