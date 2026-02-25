import re

def validar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', str(cnpj))
    
    if len(cnpj) != 14:
        return False
        
    if cnpj in [c * 14 for c in '0123456789']:
        return False

    def calcular_digito(cnpj, pesos):
        soma = sum(int(a) * b for a, b in zip(cnpj, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    dg1 = calcular_digito(cnpj[:12], pesos1)
    dg2 = calcular_digito(cnpj[:12] + str(dg1), pesos2)

    return cnpj[-2:] == f"{dg1}{dg2}"

def validar_chave_nfe(chave):
    chave = re.sub(r'\D', '', str(chave))
    return len(chave) == 44

UFS_VALIDAS = [
    'AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 
    'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 
    'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'
]
