from django.test import TestCase, override_settings
from apps.contratos.models import CampoTemplate
from services.validacao_service import validar_campos_payload


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ValidacaoServiceTest(TestCase):
    def test_moeda_normaliza(self):
        class DummyCampo:
            tipo = CampoTemplate.TIPO_CURRENCY
            placeholder = "VALOR_TOTAL"
            label = "Valor"
            obrigatorio = True
            opcoes = None

        campo = DummyCampo()
        valido, dados, erros = validar_campos_payload([campo], {"VALOR_TOTAL": "1000,50"})
        self.assertTrue(valido)
        self.assertEqual(dados["VALOR_TOTAL"], "R$ 1.000,50")
