from abc import ABC, abstractmethod
from typing import TypeVar, Generic

Response = TypeVar("Response")

class BaseUseCase(ABC, Generic[Response]):

    @abstractmethod
    def execute(self) -> Response:
        raise NotImplementedError("Not Implemented usecase.")


class AsyncBaseUseCases(ABC, Generic[Response]):

    async def execute(self) -> Response:
        raise NotImplementedError("Not Implemented usecase.")

################################
# MEDIA
################################
class DownloadMedia(BaseUseCase): ...


class GetInformationMedia(BaseUseCase): ...


class GetInformationMediaFromUrlPattern(BaseUseCase): ...


################################
# AUTHENTICATION (TELEGRAM)
################################
class AuthenticationVerifyCode(BaseUseCase): ...


class AuthenticationSendCode(BaseUseCase): ...


class IsAuthorized(BaseUseCase): ...


class AuthenticationVerifyCode(BaseUseCase): ...
