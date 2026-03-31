from os.path import join
from os import listdir
import csv
import xml.etree.ElementTree as ET
from enum import StrEnum


NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "nomina12": "http://www.sat.gob.mx/nomina12",
    "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
}


class Header(StrEnum):
    UUID = "UUID"
    DATE = "Fecha"
    START_DATE = "Fecha inicio pago"
    END_DATE = "Fecha fin pago"
    DAYS = "Días"
    TOTAL = "Total"
    AGGRAVATED = "Agravado"
    EXEMPT = "Exento"
    RETENTIONS = "Retenciones"
    CONCEPT = "Concepto"
    DAILY_SALARY = "Salario diario"


def get_invoice_data(invoice: str):
    uuid = None
    date = None
    start_date = None
    end_date = None
    days = None
    total = None
    aggravated = None
    exempt = None
    retentions = None
    concept = None
    daily_salary = None

    tree = ET.parse(invoice)
    BASE_PATH = "cfdi:Complemento/nomina12:Nomina"
    payroll = tree.find(BASE_PATH, NS)
    perceptions = tree.find(f"{BASE_PATH}/nomina12:Percepciones", NS)
    perception = tree.find(f"{BASE_PATH}/nomina12:Percepciones/nomina12:Percepcion", NS)
    deductions = tree.find(f"{BASE_PATH}/nomina12:Deducciones", NS)
    fiscal_signature = tree.find(f"cfdi:Complemento/tfd:TimbreFiscalDigital", NS)
    receiver = tree.find(f"{BASE_PATH}/nomina12:Receptor", NS)

    if receiver is not None:
        daily_salary = receiver.get("SalarioDiarioIntegrado")
        if daily_salary is None or float(daily_salary) == 0:
            daily_salary = None
    if fiscal_signature is not None:
        uuid = fiscal_signature.get("UUID")
    if payroll is not None:
        date = payroll.get("FechaPago")
        start_date = payroll.get("FechaInicialPago")
        end_date = payroll.get("FechaFinalPago")
        days = payroll.get("NumDiasPagados")
    if perceptions is not None:
        total = perceptions.get("TotalSueldos")
        aggravated = perceptions.get("TotalGravado")
        exempt = perceptions.get("TotalExento")
    if perception is not None:
        concept = perception.get("Concepto")
    if deductions is not None:
        retentions = deductions.get("TotalImpuestosRetenidos")

    return {
        Header.UUID: uuid,
        Header.DATE: date,
        Header.START_DATE: start_date,
        Header.END_DATE: end_date,
        Header.DAYS: days,
        Header.TOTAL: total,
        Header.AGGRAVATED: aggravated,
        Header.EXEMPT: exempt,
        Header.RETENTIONS: retentions,
        Header.CONCEPT: concept,
        Header.DAILY_SALARY: daily_salary,
    }


def main():
    invoices = [join("input", file) for file in listdir("input") if file.endswith(".xml")]

    uuids: set[str] = set()
    rows = []
    for invoice in invoices:
        invoice_data = get_invoice_data(invoice)
        uuid = invoice_data[Header.UUID]
        if uuid is None or uuid in uuids:
            continue
        uuids.add(uuid)
        rows.append(invoice_data)

    fieldnames = Header.__members__.values()
    with open(join("output", "data.csv"), "w") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
