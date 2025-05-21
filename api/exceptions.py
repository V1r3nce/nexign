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


class BillingStatusException(NexignBaseException):
    pass


class BalanceException(NexignBaseException):
    pass


class GetLinkedInquiryException(NexignBaseException):
    pass


class GetAccrualsException(NexignBaseException):
    pass


class AdjustmentStatusException(NexignBaseException):
    pass


class CreateAdjustmentException(NexignBaseException):
    pass


class GetStatusInquiryException(NexignBaseException):
    pass


class SearchCommercialOrderException(NexignBaseException):
    pass


class CommercialOrderIdNotFoundException(NexignBaseException):
    pass


class CommercialOrderNumberNotFoundException(NexignBaseException):
    pass


class InquiryConnectException(NexignBaseException):
    pass


class SaleStatusException(NexignBaseException):
    pass


class InquiryTechnicalSolutionException(NexignBaseException):
    pass


class SimCardListIsEmptyException(NexignBaseException):
    pass
