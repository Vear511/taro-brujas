# usuarios/utils.py

def validar_rut(rut: str) -> bool:
    """
    Valida un RUT chileno usando el algoritmo Módulo 11.
    Acepta formato con o sin puntos y guión.
    """

    if not rut:
        return False
    
    rut = rut.replace('.', '').replace('-', '').upper()

    if len(rut) < 2:
        return False

    cuerpo = rut[:-1]
    dv = rut[-1]

    if not cuerpo.isdigit():
        return False

    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    dv_esperado = 11 - resto

    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)

    return dv == dv_esperado


def validar_rut_detalle(rut: str):
    """
    Valida un RUT y devuelve una tupla (valido: bool, motivo: Optional[str]).
    Motivos posibles: 'format' (formato inválido), 'dv' (dígito verificador incorrecto).
    """
    if not rut:
        return False, 'format'

    raw = rut.replace('.', '').replace('-', '').upper()

    if len(raw) < 9:
        return False, 'length'

    if len(raw) < 2:
        return False, 'format'

    cuerpo = raw[:-1]
    dv = raw[-1]

    if not cuerpo.isdigit():
        return False, 'format'

    # Calcular dígito verificador esperado
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = suma % 11
    dv_esperado = 11 - resto

    if dv_esperado == 11:
        dv_esperado = '0'
    elif dv_esperado == 10:
        dv_esperado = 'K'
    else:
        dv_esperado = str(dv_esperado)

    if dv == dv_esperado:
        return True, None
    else:
        return False, 'dv'


def normalize_rut(rut: str) -> str:
    """Normaliza un RUT removiendo puntos y guión, y pasando a mayúsculas.

    Ej: '12.345.678-5' -> '123456785'
    """
    if not rut:
        return ''
    return rut.replace('.', '').replace('-', '').upper()
