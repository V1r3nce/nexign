from common.exceptions import NexignBaseException


class LinkedPersonException(NexignBaseException):
    pass


class LinkedPersonFunctionException(LinkedPersonException):
    pass


class LinkedPersonPullAddressException(LinkedPersonException):
    pass


class UpdateStatusException(LinkedPersonException):
    pass


class ClientNotFoundException(LinkedPersonException):
    pass


class CreatePaymentException(NexignBaseException):
    pass


class GetBillingException(NexignBaseException):
    pass
