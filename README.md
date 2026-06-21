# Sistemas Lineares — Método de Gauss-Jordan

Resolve sistemas lineares pelo método de Gauss-Jordan, mostrando **cada operação
da eliminação passo a passo** e classificando o sistema em SPD, SPI ou SI.

## Funcionalidades

- Entrada da matriz aumentada (coeficientes + termos independentes)
- Eliminação de Gauss-Jordan até a forma escalonada reduzida (RREF)
- Visualização passo a passo, uma operação por vez (estilo Symbolab), com a
  linha, a coluna e a célula do pivô destacadas
- Classificação automática do sistema:
  - **SPD** — possível e determinado (solução única)
  - **SPI** — possível e indeterminado (infinitas soluções)
  - **SI** — impossível (sem solução)
- Solução final: os valores das incógnitas (SPD) ou a forma paramétrica (SPI)

## Como usar

```
python gauss_jordan_gui.py
```

1. Defina o número de equações e incógnitas e clique em **Gerar matriz**.
2. Preencha os valores (aceita inteiros, decimais como `0,5` e frações como `1/2`).
3. Clique em **Resolver** e use **Prosseguir** / **Voltar** (ou as setas do
   teclado) para percorrer as etapas.

## Estrutura

- `gauss_jordan.py` — lógica do método (operações elementares, eliminação,
  classificação e extração da solução).
- `gauss_jordan_gui.py` — interface gráfica em Tkinter.
