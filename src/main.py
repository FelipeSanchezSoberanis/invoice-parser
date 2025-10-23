from os.path import join
from os import listdir
import csv
import xml.etree.ElementTree as ET
from enum import StrEnum

NS = {
    "cfdi": "http://www.sat.gob.mx/cfd/4",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "nomina12": "http://www.sat.gob.mx/nomina12",
}


class Header(StrEnum):
    DATE = "Fecha"
    START_DATE = "Fecha inicio pago"
    END_DATE = "Fecha fin pago"
    DAYS = "Días"
    TOTAL = "Total"
    AGGRAVATED = "Agravado"
    EXEMPT = "Exento"
    RETENTIONS = "Retenciones"
    CONCEPT = "Concepto"


def get_invoice_data(invoice: str):
    date = None
    start_date = None
    end_date = None
    days = None
    total = None
    aggravated = None
    exempt = None
    retentions = None
    concept = None

    tree = ET.parse(invoice)

    complement = tree.find("cfdi:Complemento", NS)
    if complement is not None:
        payroll = complement.find("nomina12:Nomina", NS)
        if payroll is not None:
            date = payroll.get("FechaPago")
            start_date = payroll.get("FechaInicialPago")
            end_date = payroll.get("FechaFinalPago")
            days = payroll.get("NumDiasPagados")

            perceptions = payroll.find("nomina12:Percepciones", NS)
            if perceptions is not None:
                total = perceptions.get("TotalSueldos")
                aggravated = perceptions.get("TotalGravado")
                exempt = perceptions.get("TotalExento")
                perception = perceptions.find("nomina12:Percepcion", NS)

                if perception is not None:
                    concept = perception.get("Concepto")

            deductions = payroll.find("nomina12:Deducciones", NS)
            if deductions is not None:
                retentions = deductions.get("TotalImpuestosRetenidos")

    return {
        Header.DATE: date,
        Header.START_DATE: start_date,
        Header.END_DATE: end_date,
        Header.DAYS: days,
        Header.TOTAL: total,
        Header.AGGRAVATED: aggravated,
        Header.EXEMPT: exempt,
        Header.RETENTIONS: retentions,
        Header.CONCEPT: concept,
    }


def main():
    invoices = [join("input", file) for file in listdir("input") if file.endswith(".xml")]
    fieldnames = Header.__members__.values()
    rows = [get_invoice_data(invoice) for invoice in invoices]
    with open(join("output", "data.csv"), "w") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
