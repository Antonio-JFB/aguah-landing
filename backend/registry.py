DASHBOARDS_BY_CLIENTE = {
    "aguah": [
        {
            "key": "a2_aguah",
            "name": "A2 · Fugas y priorización de medidores",
            "description": "Pronóstico de fugas, balance hídrico y priorización de medidores.",
            "url": "https://appaguah2026.redes.argentumdevelopment.com/",
        },
        {
            "key": "hmo_descuentos",
            "name": "Descuentos — Municipio y Aguah",
            "description": "Consulta y gestion de descuentos y adeudos.",
            "url": "https://apphmo2026.descuentos.argentumdevelopment.com/",
        },
    ],
}


def dashboards_for(cliente: str) -> list[dict]:
    return DASHBOARDS_BY_CLIENTE.get(cliente, [])
