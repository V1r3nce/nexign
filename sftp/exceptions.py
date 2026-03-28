from common.exceptions import NexignBaseException


class SFTPConnectionNotEstablished(NexignBaseException):
    """Ошибка установления соединения с SFTP сервером"""

    pass


class SFTPDirectoryNotFound(NexignBaseException):
    """Директория не найдена на SFTP сервере"""

    pass


class SFTPFileNotFound(NexignBaseException):
    """Файл не найден на SFTP сервере"""

    pass


class SFTPOperationFailed(NexignBaseException):
    """Ошибка выполнения SFTP операции"""

    pass


class SFTPCSVValidationError(NexignBaseException):
    """Ошибка валидации CSV файла"""

    pass


class SFTPConflictDetected(NexignBaseException):
    """Обнаружены конфликты в данных"""

    pass
