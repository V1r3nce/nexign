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


class CreateEntityException(NexignBaseException):
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


class CancelGraphException(NexignBaseException):
    pass


class AdditionalAttributeAddException(NexignBaseException):
    pass


class AdditionalAttributeSortException(NexignBaseException):
    pass


class ElementAfterException(NexignBaseException):
    pass


class LastResponseIsMissingException(NexignBaseException):
    pass


class UserIdNotFoundException(NexignBaseException):
    pass


class SpecificationNotFoundException(NexignBaseException):
    pass


class ProjectNotFoundException(NexignBaseException):
    pass


class WaitSubscriptionCallsException(NexignBaseException):
    pass


class GetStatusFileException(NexignBaseException):
    pass


class SubscriptionNotFoundException(NexignBaseException):
    pass


class AgreementNotCompletedException(NexignBaseException):
    pass


class RestructuringInquiryStatusException(NexignBaseException):
    pass


class InquirySearchException(NexignBaseException):
    pass


class AllureLaunchNotFoundException(NexignBaseException):
    pass


class GitlabProjectNotFoundException(NexignBaseException):
    pass


class GitlabFileNotFoundError(NexignBaseException):
    pass
