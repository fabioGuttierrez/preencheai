import shutil
import warnings

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        from django.conf import settings

        if not shutil.which(settings.LIBREOFFICE_PATH):
            warnings.warn(
                f"LIBREOFFICE_PATH='{settings.LIBREOFFICE_PATH}' nao encontrado no PATH. "
                "Geracao de PDF estara desabilitada.",
                RuntimeWarning,
                stacklevel=2,
            )
