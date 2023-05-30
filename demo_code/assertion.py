from locust.clients import ResponseContextManager


def check_http_response(transaction: str, response: ResponseContextManager) -> None:
    """
    The check_http_response function is used to check the response of a request.
        If the transaction is login, it checks if there's a token in the response body.
        If not, it fails with 'Login failed' message.

    :param transaction: str: Specify the type of transaction
    :param response: ResponseContextManager: Get the response body and to fail a transaction if needed
    :return: The following values:
    :doc-author: Trelent
    """
    response_body = response.text
    if transaction == 'login':
        if 'Token' not in response_body:
            response.failure('Login failed')


    if transaction == 'add_to_cart':
        if 'добавлен в корзину' not in response_body:
            response.failure(response_body)
