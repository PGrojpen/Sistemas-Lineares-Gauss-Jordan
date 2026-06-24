
# Gauss-Jordan: resolve sistemas lineares guardando cada passo da eliminacao.

EPSILON = 1e-9
# Acima de 1/EPSILON o inverso do pivo cai abaixo da tolerancia
LIMITE_VALOR = 1 / EPSILON  # 1e9


def eh_zero(x):
    return abs(x) < EPSILON


def limpar(x):
    x = round(x, 10)
    return 0.0 if eh_zero(x) else x  # tira ruido de float e o -0.0


def formatar_num(x):
    x = round(limpar(x), 4)
    if float(x).is_integer():
        return str(int(x))
    return str(x)


# Operacoes elementares (alteram a matriz no proprio lugar)

def trocar_linhas(matriz, i, j):
    for k in range(len(matriz[0])):
        matriz[i][k], matriz[j][k] = matriz[j][k], matriz[i][k]


def multiplicar_linha(matriz, i, escalar):
    for k in range(len(matriz[0])):
        matriz[i][k] *= escalar


def combinar_linhas(matriz, i, j, escalar):
    for k in range(len(matriz[0])):
        matriz[i][k] += escalar * matriz[j][k]


def gauss_jordan(matriz, num_variaveis):
    """Reduz a matriz a forma escalonada reduzida e devolve a lista de passos."""
    num_linhas = len(matriz)
    passos = []

    def registrar(descricao, destaque=None, pivo=None):
        passos.append({
            "matriz": [linha[:] for linha in matriz],  # snapshot, nao referencia
            "descricao": descricao,
            "destaque": destaque or [],
            "pivo": pivo,
        })

    registrar("Matriz inicial")

    # linha_pivo so avanca quando achamos um pivo; assim uma coluna sem pivo vira variavel livre sem desalinhar as linhas de baixo (caso SPI).
    linha_pivo = 0
    for coluna in range(num_variaveis):
        if linha_pivo >= num_linhas:
            break

        candidata = -1
        for i in range(linha_pivo, num_linhas):
            if not eh_zero(matriz[i][coluna]):
                candidata = i
                break
        if candidata == -1:
            continue

        if candidata != linha_pivo:
            trocar_linhas(matriz, linha_pivo, candidata)
            registrar(f"L{linha_pivo + 1} <-> L{candidata + 1}",
                      [linha_pivo, candidata], (linha_pivo, coluna))

        pivo = matriz[linha_pivo][coluna]
        if not eh_zero(pivo - 1):
            escala = 1 / pivo
            multiplicar_linha(matriz, linha_pivo, escala)
            registrar(f"L{linha_pivo + 1} -> ({formatar_num(escala)}) * L{linha_pivo + 1}",
                      [linha_pivo], (linha_pivo, coluna))

        for i in range(num_linhas):
            if i != linha_pivo and not eh_zero(matriz[i][coluna]):
                fator = -matriz[i][coluna]
                combinar_linhas(matriz, i, linha_pivo, fator)
                registrar(f"L{i + 1} -> L{i + 1} + ({formatar_num(fator)}) * L{linha_pivo + 1}",
                          [i], (linha_pivo, coluna))

        linha_pivo += 1

    registrar("Forma escalonada reduzida")
    return passos


def classificar_sistema(matriz, num_variaveis):
    posto = 0
    for linha in matriz:
        if any(not eh_zero(linha[c]) for c in range(num_variaveis)):
            posto += 1
        elif not eh_zero(linha[num_variaveis]):
            return "SI"  # linha do tipo 0 = k, com k != 0
    return "SPD" if posto == num_variaveis else "SPI"


def obter_solucao(matriz, num_variaveis, tipo):
    if tipo == "SI":
        return None

    col_b = num_variaveis
    pivo_da_coluna = {}
    for i in range(len(matriz)):
        for c in range(num_variaveis):
            if not eh_zero(matriz[i][c]):
                pivo_da_coluna[c] = i
                break
    livres = [c for c in range(num_variaveis) if c not in pivo_da_coluna]

    if tipo == "SPD":
        solucao = [0.0] * num_variaveis
        for c, i in pivo_da_coluna.items():
            solucao[c] = limpar(matriz[i][col_b])
        return solucao

    # SPI: passa as variaveis livres para o outro lado -> x = b - coef*livre
    resposta = []
    for c in range(num_variaveis):
        if c in livres:
            resposta.append(f"x{c + 1} = livre")
            continue

        i = pivo_da_coluna[c]
        const = limpar(matriz[i][col_b])
        termos = []
        for livre in livres:
            coef = limpar(matriz[i][livre])
            if coef == 0:
                continue
            sinal = "-" if coef > 0 else "+"
            mag = formatar_num(abs(coef))
            mag = "" if mag == "1" else f"{mag}·"
            termos.append((sinal, f"{mag}x{livre + 1}"))

        if not termos:
            lado = formatar_num(const)
        else:
            partes = [] if const == 0 else [formatar_num(const)]
            for k, (sinal, termo) in enumerate(termos):
                if not partes and k == 0:
                    partes.append(("-" if sinal == "-" else "") + termo)
                else:
                    partes.append(f"{sinal} {termo}")
            lado = " ".join(partes)

        resposta.append(f"x{c + 1} = {lado}")
    return resposta
