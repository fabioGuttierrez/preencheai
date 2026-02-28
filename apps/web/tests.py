import tempfile
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from unittest.mock import patch
from docx import Document

from apps.core.models import Organizacao, Usuario
from apps.clientes.models import Cliente
from apps.contratos.models import ModeloContrato, CampoTemplate, Contrato
from apps.formularios.models import LinkFormulario


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class FluxoContratoTest(TestCase):
    def setUp(self):
        self.org = Organizacao.objects.create(nome="Org Teste")
        self.user = Usuario.objects.create_user(
            username="admin",
            email="admin@teste.com",
            password="12345678",
            organizacao=self.org,
        )
        self.cliente = Cliente.objects.create(
            organizacao=self.org,
            nome="Cliente Teste",
            cpf="123.456.789-09",
            email="cliente@teste.com",
            telefone="11999999999",
        )

        tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
        doc = Document()
        doc.add_paragraph("Contrato {{VALOR_TOTAL}}")
        doc.save(tmp.name)
        tmp.seek(0)
        self.modelo = ModeloContrato.objects.create(
            organizacao=self.org,
            nome="Modelo Teste",
            arquivo_docx=SimpleUploadedFile("modelo.docx", tmp.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        )

        CampoTemplate.objects.create(
            modelo=self.modelo,
            placeholder="VALOR_TOTAL",
            label="Valor Total",
            tipo=CampoTemplate.TIPO_CURRENCY,
            obrigatorio=True,
            ordem=1,
        )

        self.link = LinkFormulario.objects.create(
            organizacao=self.org,
            cliente=self.cliente,
            modelo=self.modelo,
        )

    @patch("services.pdf_service.converter_docx_para_pdf", return_value=None)
    def test_formulario_publico_gera_contrato(self, _mock_pdf):
        url = reverse("formulario_publico", kwargs={"token": self.link.token})
        response = self.client.post(url, {
            "VALOR_TOTAL": "1500",
            "aceite_lgpd": "1",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Contrato.objects.count(), 1)

    def test_formulario_publico_sem_consentimento(self):
        url = reverse("formulario_publico", kwargs={"token": self.link.token})
        response = self.client.post(url, {
            "VALOR_TOTAL": "1500",
        })
        self.assertContains(response, "aceitar os Termos", status_code=200)
