from num2words import num2words
from datetime import datetime

def valor_por_extenso(valor):
    try:
        return num2words(valor, lang='pt_BR').replace(" e", ",")
    except:
        return "valor inválido"

def formatar_data_br(data_iso):
    try:
        return datetime.strptime(data_iso, "%Y-%m-%d").strftime("%d/%m/%Y")
    except:
        return data_iso

def ultimo_dia_do_mes(ano, mes):
    from datetime import date, timedelta
    fim = date(ano, mes, 28) + timedelta(days=4)
    return fim - timedelta(days=fim.day)
