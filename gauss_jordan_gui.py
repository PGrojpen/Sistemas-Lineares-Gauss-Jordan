# Interface (Tkinter) do resolvedor de Gauss-Jordan: digita a matriz e percorre
# a eliminacao um passo por vez. A matematica fica toda em gauss_jordan.py.

import tkinter as tk
from tkinter import ttk, messagebox

from gauss_jordan import gauss_jordan, classificar_sistema, obter_solucao, formatar_num, limpar

# Base neutra (slate) + um unico acento primario (indigo).
COR_FUNDO    = "#f1f5f9"   # slate-100, fundo geral
COR_PAINEL   = "#ffffff"
COR_BORDA    = "#e2e8f0"   # slate-200
COR_TEXTO    = "#1e293b"   # slate-800, texto principal
COR_SUAVE    = "#556070"   # slate, texto secundario (contraste >= 4.5)
COR_HEADER   = "#1e293b"   # barra do topo
COR_HEADER_2 = "#4f46e5"   # rotulos x1..xn e b

COR_PRIM     = "#4f46e5"   # indigo, acao principal e navegacao
COR_NEUTRO   = "#475569"   # slate-600, botoes secundarios
COR_DESAB    = "#e2e8f0"   # botao desabilitado: fundo
COR_DESAB_TX = "#94a3b8"   # botao desabilitado: texto

COR_LINHA    = "#fef3c7"   # amber-100, linha mexida
COR_COLUNA   = "#eef2ff"   # indigo-50, coluna do pivo
COR_PIVO     = "#a5b4fc"   # indigo-300, celula do pivo

COR_OK       = "#059669"   # emerald, SPD
COR_ALERTA   = "#d97706"   # amber, SPI
COR_ERRO     = "#e11d48"   # rose, SI

FONTE_MATRIZ = ("Consolas", 15)
FONTE_TXT    = ("Segoe UI", 11)
FONTE_BTN    = ("Segoe UI", 11, "bold")
FONTE_TIT    = ("Segoe UI", 18, "bold")
FONTE_OP     = ("Segoe UI", 13, "bold")

SUBSCRITO = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")


def nome_var(i):
    return "x" + str(i + 1).translate(SUBSCRITO)


def parse_num(texto):
    # aceita vazio, virgula decimal e fracoes simples (1/2)
    texto = texto.strip().replace(",", ".")
    if texto == "":
        return 0.0
    if "/" in texto:
        num, den = texto.split("/")
        return float(num) / float(den)
    return float(texto)


class AppGaussJordan:
    def __init__(self, root):
        self.root = root
        self.root.title("Gauss-Jordan — passo a passo")
        self.root.configure(bg=COR_FUNDO)
        self.root.geometry("820x760")
        self.root.minsize(680, 600)

        self.entradas = []
        self.num_variaveis = 0
        self.matriz_original = []
        self.passos = []
        self.indice = 0
        self.tipo = None
        self.solucao = None

        self._estilo_ttk()
        self._montar_header()

        # corpo rolavel, para matrizes grandes nao estourarem a janela
        container = tk.Frame(self.root, bg=COR_FUNDO)
        container.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(container, bg=COR_FUNDO, highlightthickness=0)
        scroll = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.corpo = tk.Frame(self.canvas, bg=COR_FUNDO)
        self.corpo.bind("<Configure>",
                        lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.corpo, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.root.bind_all("<MouseWheel>",
                           lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

        self._montar_controles()
        self._montar_entrada()
        self._montar_passos()

        for tecla in ("<Right>", "<Down>"):
            self.root.bind(tecla, lambda e: self.proximo())
        for tecla in ("<Left>", "<Up>"):
            self.root.bind(tecla, lambda e: self.anterior())

        self.gerar_grade()

    def _estilo_ttk(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except tk.TclError:
            pass
        s.configure("TProgressbar", troughcolor=COR_BORDA, background=COR_PRIM, thickness=8)

    def _botao(self, pai, texto, comando, cor=COR_PRIM):
        cor_hover = self._escurecer(cor)
        b = tk.Button(pai, text=texto, command=comando, font=FONTE_BTN,
                      bg=cor, fg="white", activebackground=cor_hover,
                      activeforeground="white", disabledforeground=COR_DESAB_TX,
                      relief="flat", bd=0, padx=16, pady=8, cursor="hand2")
        b.cor_base = cor  # guardada para restaurar ao reabilitar
        b.bind("<Enter>", lambda e: b.config(bg=cor_hover) if str(b["state"]) != "disabled" else None)
        b.bind("<Leave>", lambda e: b.config(bg=cor) if str(b["state"]) != "disabled" else None)
        return b

    @staticmethod
    def _habilitar(botao, ativo):
        if ativo:
            botao.config(state="normal", bg=botao.cor_base)
        else:
            botao.config(state="disabled", bg=COR_DESAB)

    @staticmethod
    def _escurecer(cor, fator=0.82):
        cor = cor.lstrip("#")
        r, g, b = int(cor[0:2], 16), int(cor[2:4], 16), int(cor[4:6], 16)
        return f"#{int(r * fator):02x}{int(g * fator):02x}{int(b * fator):02x}"

    def _montar_header(self):
        head = tk.Frame(self.root, bg=COR_HEADER)
        head.pack(fill="x")
        tk.Label(head, text="Sistemas Lineares — Método de Gauss-Jordan",
                 font=FONTE_TIT, fg="white", bg=COR_HEADER).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(head, text="Resolução passo a passo, com classificação (SPD / SPI / SI)",
                 font=FONTE_TXT, fg="#cbd5e1", bg=COR_HEADER).pack(anchor="w", padx=20, pady=(0, 14))

    def _montar_controles(self):
        ctr = tk.Frame(self.corpo, bg=COR_FUNDO)
        ctr.pack(fill="x", padx=20, pady=(14, 4))

        tk.Label(ctr, text="Equações:", font=FONTE_TXT, bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left")
        self.spin_linhas = ttk.Spinbox(ctr, from_=1, to=10, width=4, font=FONTE_TXT)
        self.spin_linhas.set(3)
        self.spin_linhas.pack(side="left", padx=(4, 18))

        tk.Label(ctr, text="Incógnitas:", font=FONTE_TXT, bg=COR_FUNDO, fg=COR_TEXTO).pack(side="left")
        self.spin_colunas = ttk.Spinbox(ctr, from_=1, to=10, width=4, font=FONTE_TXT)
        self.spin_colunas.set(3)
        self.spin_colunas.pack(side="left", padx=(4, 18))

        self._botao(ctr, "↻  Gerar matriz", self.gerar_grade, COR_NEUTRO).pack(side="left")

    def _montar_entrada(self):
        tk.Label(self.corpo, text="Matriz aumentada   [ coeficientes  │  resultados ]",
                 font=FONTE_TXT, bg=COR_FUNDO, fg=COR_SUAVE).pack(anchor="w", padx=20, pady=(10, 2))

        self.frame_entrada = tk.Frame(self.corpo, bg=COR_PAINEL,
                                      highlightbackground=COR_BORDA, highlightthickness=1)
        self.frame_entrada.pack(padx=20, pady=4, anchor="w")

        acoes = tk.Frame(self.corpo, bg=COR_FUNDO)
        acoes.pack(fill="x", padx=20, pady=10)
        self._botao(acoes, "▶  Resolver", self.resolver, COR_PRIM).pack(side="left")
        self._botao(acoes, "Limpar", self.limpar_grade, COR_NEUTRO).pack(side="left", padx=8)
        tk.Label(acoes, text="Aceita inteiros, decimais (0,5) e frações (1/2).",
                 font=("Segoe UI", 9), bg=COR_FUNDO, fg=COR_SUAVE).pack(side="left", padx=10)

    def _montar_passos(self):
        ttk.Separator(self.corpo, orient="horizontal").pack(fill="x", padx=20, pady=8)

        self.lbl_sistema = tk.Label(self.corpo, text="", font=("Consolas", 11),
                                    bg=COR_FUNDO, fg=COR_SUAVE, justify="left")
        self.lbl_sistema.pack(anchor="w", padx=20)

        self.lbl_op = tk.Label(self.corpo, text="Digite o sistema e clique em Resolver.",
                               font=FONTE_OP, bg=COR_FUNDO, fg=COR_HEADER)
        self.lbl_op.pack(anchor="w", padx=20, pady=(8, 2))

        prog = tk.Frame(self.corpo, bg=COR_FUNDO)
        prog.pack(fill="x", padx=20)
        self.barra = ttk.Progressbar(prog, mode="determinate", length=260)
        self.barra.pack(side="left")
        self.lbl_contador = tk.Label(prog, text="", font=FONTE_TXT, bg=COR_FUNDO, fg=COR_SUAVE)
        self.lbl_contador.pack(side="left", padx=12)

        self.frame_matriz = tk.Frame(self.corpo, bg=COR_PAINEL,
                                     highlightbackground=COR_BORDA, highlightthickness=1)
        self.frame_matriz.pack(padx=20, pady=10, anchor="w")

        nav = tk.Frame(self.corpo, bg=COR_FUNDO)
        nav.pack(anchor="w", padx=20, pady=2)
        self.btn_inicio = self._botao(nav, "⏮", lambda: self.ir_para(0), COR_NEUTRO)
        self.btn_inicio.pack(side="left", padx=2)
        self.btn_voltar = self._botao(nav, "◀  Voltar", self.anterior, COR_NEUTRO)
        self.btn_voltar.pack(side="left", padx=2)
        self.btn_proximo = self._botao(nav, "Prosseguir  ▶", self.proximo, COR_PRIM)
        self.btn_proximo.pack(side="left", padx=2)
        self.btn_fim = self._botao(nav, "⏭", lambda: self.ir_para(len(self.passos) - 1), COR_NEUTRO)
        self.btn_fim.pack(side="left", padx=2)

        self.frame_resultado = tk.Frame(self.corpo, bg=COR_FUNDO)
        self.frame_resultado.pack(fill="x", padx=20, pady=(10, 20), anchor="w")
        self.lbl_resultado = tk.Label(self.frame_resultado, text="", font=("Consolas", 12),
                                      bg=COR_FUNDO, fg=COR_TEXTO, justify="left",
                                      anchor="w", padx=14, pady=12)
        self.lbl_resultado.pack(fill="x")

        self._atualizar_nav()

    def gerar_grade(self):
        try:
            linhas = int(float(self.spin_linhas.get()))
            colunas = int(float(self.spin_colunas.get()))
        except ValueError:
            messagebox.showerror("Tamanho inválido", "Informe números inteiros.")
            return

        for w in self.frame_entrada.winfo_children():
            w.destroy()
        self.entradas = []

        for c in range(colunas):
            tk.Label(self.frame_entrada, text=nome_var(c), font=FONTE_TXT, bg=COR_PAINEL,
                     fg=COR_HEADER_2, width=6).grid(row=0, column=c, padx=2, pady=(8, 0))
        tk.Label(self.frame_entrada, text="", bg=COR_PAINEL, width=2).grid(row=0, column=colunas)
        tk.Label(self.frame_entrada, text="b", font=FONTE_TXT, bg=COR_PAINEL,
                 fg=COR_HEADER_2, width=6).grid(row=0, column=colunas + 1, padx=2, pady=(8, 0))

        for r in range(linhas):
            linha = []
            for c in range(colunas):
                e = tk.Entry(self.frame_entrada, width=6, font=FONTE_MATRIZ, justify="center",
                             relief="solid", bd=1, highlightthickness=0)
                e.insert(0, "0")
                e.grid(row=r + 1, column=c, padx=3, pady=3)
                linha.append(e)
            tk.Label(self.frame_entrada, text="│", font=FONTE_MATRIZ, bg=COR_PAINEL,
                     fg="#cbd5e1").grid(row=r + 1, column=colunas)
            e = tk.Entry(self.frame_entrada, width=6, font=FONTE_MATRIZ, justify="center",
                         relief="solid", bd=1, bg="#eef2ff", highlightthickness=0)
            e.insert(0, "0")
            e.grid(row=r + 1, column=colunas + 1, padx=3, pady=3)
            linha.append(e)
            self.entradas.append(linha)

        self._reset_passos()

    def limpar_grade(self):
        for linha in self.entradas:
            for e in linha:
                e.delete(0, "end")
                e.insert(0, "0")
        self._reset_passos()

    def _reset_passos(self):
        self.passos = []
        self.indice = 0
        self.lbl_sistema.config(text="")
        self.lbl_op.config(text="Digite o sistema e clique em Resolver.")
        self.lbl_contador.config(text="")
        self.barra["value"] = 0
        self.lbl_resultado.config(text="", bg=COR_FUNDO)
        self.frame_resultado.config(bg=COR_FUNDO)
        for w in self.frame_matriz.winfo_children():
            w.destroy()
        self._atualizar_nav()

    def resolver(self):
        if not self.entradas:
            messagebox.showwarning("Sem matriz", "Gere a matriz primeiro.")
            return

        matriz = []
        for r, linha in enumerate(self.entradas):
            nova = []
            for c, e in enumerate(linha):
                try:
                    nova.append(parse_num(e.get()))
                except (ValueError, ZeroDivisionError):
                    rotulo = "b" if c == len(linha) - 1 else nome_var(c)
                    messagebox.showerror("Entrada inválida",
                                         f"Valor inválido na linha {r + 1}, coluna “{rotulo}”: "
                                         f"'{e.get()}'.\nUse números (2, -3, 0.5) ou frações (1/2).")
                    e.focus_set()
                    e.selection_range(0, "end")
                    return
            matriz.append(nova)

        self.num_variaveis = len(self.entradas[0]) - 1
        self.matriz_original = [linha[:] for linha in matriz]

        # gauss_jordan transforma 'matriz' na RREF e devolve os snapshots
        self.passos = gauss_jordan(matriz, self.num_variaveis)
        self.tipo = classificar_sistema(matriz, self.num_variaveis)
        self.solucao = obter_solucao(matriz, self.num_variaveis, self.tipo)

        self.lbl_sistema.config(text="Sistema:\n" + self._sistema_em_equacoes())
        self.indice = 0
        self.mostrar_passo()

    def _sistema_em_equacoes(self):
        nv = self.num_variaveis
        linhas_txt = []
        for linha in self.matriz_original:
            termos = []
            for c in range(nv):
                coef = limpar(linha[c])
                if coef == 0:
                    continue
                sinal = "−" if coef < 0 else "+"
                mag = formatar_num(abs(coef))
                mag = "" if mag == "1" else mag
                termos.append((sinal, f"{mag}{nome_var(c)}"))
            if not termos:
                esq = "0"
            else:
                s0, t0 = termos[0]
                esq = ("−" if s0 == "−" else "") + t0
                for s, t in termos[1:]:
                    esq += f" {s} {t}"
            linhas_txt.append(f"   {esq} = {formatar_num(linha[nv])}")
        return "\n".join(linhas_txt)

    def ir_para(self, indice):
        if self.passos:
            self.indice = max(0, min(indice, len(self.passos) - 1))
            self.mostrar_passo()

    def proximo(self):
        if self.passos and self.indice < len(self.passos) - 1:
            self.indice += 1
            self.mostrar_passo()

    def anterior(self):
        if self.passos and self.indice > 0:
            self.indice -= 1
            self.mostrar_passo()

    def _atualizar_nav(self):
        tem = bool(self.passos)
        inicio = self.indice <= 0
        fim = self.indice >= len(self.passos) - 1
        self._habilitar(self.btn_inicio, tem and not inicio)
        self._habilitar(self.btn_voltar, tem and not inicio)
        self._habilitar(self.btn_proximo, tem and not fim)
        self._habilitar(self.btn_fim, tem and not fim)

    def mostrar_passo(self):
        passo = self.passos[self.indice]
        self.render_matriz(passo)
        self.lbl_op.config(text=passo["descricao"])
        self.lbl_contador.config(text=f"Passo {self.indice + 1} de {len(self.passos)}")
        self.barra["maximum"] = max(1, len(self.passos) - 1)
        self.barra["value"] = self.indice
        self._atualizar_nav()

        if self.indice == len(self.passos) - 1:
            self._mostrar_resultado()
        else:
            self.lbl_resultado.config(text="", bg=COR_FUNDO)
            self.frame_resultado.config(bg=COR_FUNDO)

    def render_matriz(self, passo):
        for w in self.frame_matriz.winfo_children():
            w.destroy()

        destaque = set(passo["destaque"])
        pivo_lin, pivo_col = passo["pivo"] if passo["pivo"] else (None, None)
        nv = self.num_variaveis

        for r, linha in enumerate(passo["matriz"]):
            col_grid = 0
            for c, valor in enumerate(linha):
                if c == nv:
                    tk.Label(self.frame_matriz, text="│", font=FONTE_MATRIZ,
                             bg=COR_PAINEL, fg="#cbd5e1").grid(row=r, column=col_grid, padx=2)
                    col_grid += 1

                fundo = COR_PAINEL
                if pivo_col is not None and c == pivo_col and c < nv:
                    fundo = COR_COLUNA
                if r in destaque:
                    fundo = COR_LINHA
                if (r, c) == (pivo_lin, pivo_col):
                    fundo = COR_PIVO

                tk.Label(self.frame_matriz, text=formatar_num(valor), font=FONTE_MATRIZ,
                         width=8, bg=fundo, fg=COR_TEXTO, anchor="e",
                         padx=6, pady=6).grid(row=r, column=col_grid, padx=1, pady=1)
                col_grid += 1

    def _mostrar_resultado(self):
        if self.tipo == "SI":
            cor, tinta = COR_ERRO, "#fff1f2"
            texto = ("●  Sistema IMPOSSÍVEL (SI)\n"
                     "   Há uma linha do tipo 0 = k (k ≠ 0): não há solução.")
        elif self.tipo == "SPD":
            cor, tinta = COR_OK, "#ecfdf5"
            valores = "     ".join(f"{nome_var(i)} = {formatar_num(v)}"
                                   for i, v in enumerate(self.solucao))
            texto = ("●  Sistema POSSÍVEL e DETERMINADO (SPD)\n"
                     f"   Solução única:   {valores}")
        else:
            cor, tinta = COR_ALERTA, "#fffbeb"
            livres = sum(1 for s in self.solucao if "livre" in s)
            corpo = "\n".join("   " + s for s in self.solucao)
            texto = ("●  Sistema POSSÍVEL e INDETERMINADO (SPI)\n"
                     f"   {livres} variável(is) livre(s) → infinitas soluções\n{corpo}")

        self.frame_resultado.config(bg=cor)
        self.lbl_resultado.config(text=texto, bg=tinta, fg=COR_TEXTO)


def main():
    root = tk.Tk()
    AppGaussJordan(root)
    root.mainloop()


if __name__ == "__main__":
    main()
