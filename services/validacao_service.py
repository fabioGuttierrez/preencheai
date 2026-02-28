import re
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from apps.contratos.models import CampoTemplate


def validar_campos_post(campos, post_data):
    erros = []
    dados = {}

    for campo in campos:
        if campo.tipo == CampoTemplate.TIPO_MULTISELECT:
            valor = post_data.getlist(campo.placeholder)
            valor = [v.strip() for v in valor if v.strip()]
        else:
            valor = post_data.get(campo.placeholder, "").strip()

        ok, valor_norm, erro = _validar_valor(campo, valor)
        if not ok:
            erros.append(erro)
            continue

        dados[campo.placeholder] = valor_norm

    return (len(erros) == 0), dados, erros


def validar_campos_payload(campos, data):
    erros = []
    dados = {}

    for campo in campos:
        valor = data.get(campo.placeholder, "")
        if isinstance(valor, list):
            valor = [str(v).strip() for v in valor if str(v).strip()]
        else:
            valor = str(valor).strip()

        ok, valor_norm, erro = _validar_valor(campo, valor)
        if not ok:
            erros.append(erro)
            continue

        dados[campo.placeholder] = valor_norm

    return (len(erros) == 0), dados, erros


def _validar_valor(campo, valor):
    if campo.obrigatorio and not valor:
        return False, valor, f"O campo '{campo.label}' e obrigatorio."

    if not valor:
        return True, valor, ""

    if campo.tipo in (CampoTemplate.TIPO_SELECT, CampoTemplate.TIPO_MULTISELECT) and campo.opcoes:
        valores = valor if isinstance(valor, list) else [valor]
        invalidos = [v for v in valores if v not in campo.opcoes]
        if invalidos:
            return False, valor, f"Selecao invalida em '{campo.label}'."

    if campo.tipo == CampoTemplate.TIPO_EMAIL:
        try:
            validate_email(valor)
        except ValidationError:
            return False, valor, f"E-mail invalido em '{campo.label}'."

    if campo.tipo == CampoTemplate.TIPO_PHONE:
        digits = _only_digits(valor)
        if len(digits) not in (10, 11):
            return False, valor, f"Telefone invalido em '{campo.label}'."

    if campo.tipo == CampoTemplate.TIPO_DATE:
        data = _parse_date(valor)
        if not data:
            return False, valor, f"Data invalida em '{campo.label}'."
        valor = data.strftime("%d/%m/%Y")

    if campo.tipo == CampoTemplate.TIPO_NUMBER:
        numero = _parse_decimal(valor)
        if numero is None:
            return False, valor, f"Numero invalido em '{campo.label}'."
        valor = _format_number_br(numero)

    if campo.tipo == CampoTemplate.TIPO_CURRENCY:
        numero = _parse_decimal(valor)
        if numero is None:
            return False, valor, f"Valor monetario invalido em '{campo.label}'."
        valor = f"R$ {_format_currency_br(numero)}"

    placeholder_upper = campo.placeholder.upper()
    if "CPF" in placeholder_upper:
        if not _validar_cpf(valor):
            return False, valor, f"CPF invalido em '{campo.label}'."
    if "CNPJ" in placeholder_upper:
        if not _validar_cnpj(valor):
            return False, valor, f"CNPJ invalido em '{campo.label}'."

    return True, valor, ""


def _only_digits(text):
    return re.sub(r"\D", "", text or "")


def _parse_decimal(text):
    if text is None:
        return None
    limpo = str(text).replace("R$", "").replace("r$", "")
    limpo = limpo.replace(" ", "")
    limpo = limpo.replace(".", "")
    limpo = limpo.replace(",", ".")
    try:
        return Decimal(limpo)
    except (InvalidOperation, ValueError):
        return None


def _format_currency_br(value: Decimal) -> str:
    return _format_number_br(value, casas=2)


def _format_number_br(value: Decimal, casas: int | None = None) -> str:
    if casas is None:
        casas = 2 if value % 1 != 0 else 0
    quant = Decimal("1") if casas == 0 else Decimal("1." + "0" * casas)
    value = value.quantize(quant)
    texto = f"{value:,.{casas}f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return texto


def _parse_date(text):
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _validar_cpf(cpf: str) -> bool:
    cpf = _only_digits(cpf)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calc(digs):
        soma = 0
        for i, dig in enumerate(digs, start=2):
            soma += int(dig) * i
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    d1 = calc(reversed(cpf[:9]))
    d2 = calc(reversed(cpf[:10]))
    return cpf[-2:] == d1 + d2


def _validar_cnpj(cnpj: str) -> bool:
    cnpj = _only_digits(cnpj)
    if len(cnpj) != 14 or cnpj == cnpj[0] * 14:
        return False

    def calc(digs, pesos):
        soma = sum(int(d) * p for d, p in zip(digs, pesos))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    d1 = calc(cnpj[:12], pesos1)
    d2 = calc(cnpj[:12] + d1, pesos2)
    return cnpj[-2:] == d1 + d2
