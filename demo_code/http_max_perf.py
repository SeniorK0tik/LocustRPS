from typing import Dict, Tuple

from locust import task, constant_pacing, HttpUser, LoadTestShape
import random
import assertion
from config import cfg, logger


class CartUser(HttpUser):
    "Virtual User"
    wait_time = constant_pacing(cfg.pacing_sec)
    host = cfg.api_host

    def on_start(self):
        """
        The on_start function is called when the experiment starts.
        It can be used to set up some initial state, or perform some one-time
        initialization of your experiment.

        :param self: Represent the instance of the class
        :return: The login function
        :doc-author: Trelent | SenorK0tik
        """
        self.login()

    @task
    def add_to_cart(self) -> None:
        """
        The add_to_cart function adds a random product to the cart.
        Decorator @taks marks function for Locust. It should be looped.

        :param self: Represent the instance of the class
        :return: None
        :doc-author: Trelent | SenorK0tik
        """
        transaction: str = self.add_to_cart.__name__
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
                catch_response=True,    # Ловим тело ответа
                name=transaction
        ) as request:
            assertion.check_http_response(transaction, request)

    def login(self) -> None:
        """
        The login function is used to log in a user.
            The login function will return the token_id of the logged in user.


        :param self: Represent the instance of the class
        :return: A token_id, which is a string
        :doc-author: Trelent | SenorK0tik
        """
        with self.client.get(
                f"/login/demo-user",
                catch_response=True,
                name='login'
        ) as request:
            assertion.check_http_response('login', request)
        self.token_id = request.text

    def on_stop(self):
        """
        The on_stop function is called when the user stops the application.
        It should be used to clean up any resources that were created in on_start.


        :param self: Represent the instance of the class
        :return: The user stopped
        :doc-author: Trelent | SenorK0tik
        """
    logger.debug(f"user stopped")


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

        :param self: Refer to the current instance of a class
        :return: A tuple of the number of users to spawn and the rate at which they should be spawned
        :doc-author: Trelent
        """
        run_time: float = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                tick_data = (stage["users"], stage["spawn_rate"])
                return tick_data
        return None
