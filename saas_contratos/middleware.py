import logging

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware:
    """
    Loga exceções não tratadas com contexto do request.
    Não altera o fluxo — deixa o handler padrão do Django responder.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        logger.error(
            "Excecao nao tratada: method=%s path=%s user=%s exception=%s",
            request.method,
            request.path,
            getattr(request.user, "pk", "anonymous"),
            repr(exception),
            exc_info=True,
        )
        return None
