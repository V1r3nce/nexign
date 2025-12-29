class NexignBaseException(Exception):
    pass


class InvalidLogLevel(NexignBaseException):
    pass


class PSCOfferingExportMismatch(Exception):
    """Исключение, выбрасываемое при несоответствии данных экспортированного продуктового предложения."""

    pass


class PSCImportContainsErrors(Exception):
    """Импорт продуктового предложения завершился с ошибками (containsErrors=True)."""

    pass
