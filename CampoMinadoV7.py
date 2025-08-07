import tkinter as tk
from tkinter import messagebox
import random

# ============================================
# CONFIGURAÇÕES INICIAIS E VARIÁVEIS GLOBAIS
# ============================================

TEMPO_LIMITE = 50  # Tempo máximo para cada jogada em segundos

# Direções para verificar células vizinhas (horizontal, vertical e diagonais)
direcoes = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),          (0, 1),
            (1, -1), (1, 0), (1, 1)]

# ============================================
# CLASSE PRINCIPAL DO JOGO: CAMPO MINADO
# ============================================

class CampoMinado:
    def __init__(self, master, linhas, colunas, minas, largura_botao, altura_botao, fonte_botao):
        """
        Inicializa o jogo com as configurações recebidas.
        """
        self.master = master
        self.linhas = linhas
        self.colunas = colunas
        self.minas = minas
        self.largura_botao = largura_botao
        self.altura_botao = altura_botao
        self.fonte_botao = fonte_botao

        # Variáveis de controle do jogo
        self.bombas_restantes = self.minas
        self.tempo_restante = TEMPO_LIMITE
        self.temporizador_id = None
        self.total_time = 0
        self.total_timer_id = None

        # Configura a janela principal
        self.master.title("Campo Minado")
        self.master.configure(bg="#222")  # Dark mode

        # FRAME superior com as informações
        self.top_frame = tk.Frame(master, bg="#222")
        self.top_frame.pack(pady=10)

        # Labels de informações
        self.label_bombas = tk.Label(self.top_frame, text=f"Bombas restantes: {self.bombas_restantes}",
                                     font=("Arial", 16), bg="#222", fg="white")
        self.label_bombas.pack(side=tk.LEFT, padx=20)

        self.label_tempo = tk.Label(self.top_frame, text=f"Tempo jogada: {self.tempo_restante}s",
                                    font=("Arial", 16), bg="#222", fg="white")
        self.label_tempo.pack(side=tk.LEFT, padx=20)

        self.label_total_tempo = tk.Label(self.top_frame, text=f"Tempo total: {self.total_time}s",
                                          font=("Arial", 16), bg="#222", fg="white")
        self.label_total_tempo.pack(side=tk.LEFT, padx=20)

        # FRAME principal do tabuleiro
        self.frame = tk.Frame(master, bg="#222")
        self.frame.pack(pady=10)

        # Inicializa o jogo
        self.reiniciar_jogo()

    # ============================================
    # FUNÇÕES DE CONFIGURAÇÃO E INICIALIZAÇÃO
    # ============================================

    def reiniciar_jogo(self):
        """
        Cria as estruturas de dados iniciais e coloca as minas.
        """
        # Estruturas de controle
        self.tabuleiro = [[0 for _ in range(self.colunas)] for _ in range(self.linhas)]
        self.visivel = [[False for _ in range(self.colunas)] for _ in range(self.linhas)]
        self.bandeirada = [[False for _ in range(self.colunas)] for _ in range(self.linhas)]
        self.botoes = [[None for _ in range(self.colunas)] for _ in range(self.linhas)]

        self.colocar_minas()
        self.calcular_dicas()
        self.criar_botoes()
        self.reiniciar_tempo()
        self.iniciar_tempo_total()

    def colocar_minas(self):
        """
        Coloca minas aleatoriamente no tabuleiro.
        """
        minas_colocadas = 0
        while minas_colocadas < self.minas:
            i = random.randint(0, self.linhas - 1)
            j = random.randint(0, self.colunas - 1)
            if self.tabuleiro[i][j] != -1:
                self.tabuleiro[i][j] = -1
                minas_colocadas += 1

    def calcular_dicas(self):
        """
        Calcula o número de minas ao redor de cada célula.
        """
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.tabuleiro[i][j] == -1:
                    continue
                count = 0
                for dx, dy in direcoes:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < self.linhas and 0 <= nj < self.colunas:
                        if self.tabuleiro[ni][nj] == -1:
                            count += 1
                self.tabuleiro[i][j] = count

    def criar_botoes(self):
        """
        Cria os botões gráficos do tabuleiro.
        """
        for i in range(self.linhas):
            for j in range(self.colunas):
                btn = tk.Button(self.frame, width=self.largura_botao, height=self.altura_botao,
                                font=("Arial", self.fonte_botao),
                                bg="#444", fg="white", relief=tk.RAISED,
                                activebackground="#666")
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-1>", lambda event, i=i, j=j: self.abrir_celula(i, j))
                btn.bind("<Button-3>", lambda event, i=i, j=j: self.marcar_bomba(i, j))
                self.botoes[i][j] = btn

    # ============================================
    # FUNÇÕES DE JOGADA
    # ============================================

    def abrir_celula(self, i, j):
        """
        Revela a célula e aciona fim de jogo se for mina.
        """
        if self.visivel[i][j] or self.bandeirada[i][j]:
            return
        self.reiniciar_tempo()
        self.visivel[i][j] = True
        btn = self.botoes[i][j]

        if self.tabuleiro[i][j] == -1:
            btn.config(text='💣', bg='red')
            self.fim_jogo(False)
        else:
            if self.tabuleiro[i][j] == 0:
                btn.config(text='', relief=tk.SUNKEN, bg="#666")
                for dx, dy in direcoes:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < self.linhas and 0 <= nj < self.colunas:
                        self.abrir_celula(ni, nj)
            else:
                btn.config(text=str(self.tabuleiro[i][j]), relief=tk.SUNKEN, bg="#555")
            if self.checar_vitoria():
                self.fim_jogo(True)

    def marcar_bomba(self, i, j):
        """
        Marca a célula como suspeita de bomba.
        """
        if self.visivel[i][j] or self.bandeirada[i][j]:
            return
        self.reiniciar_tempo()
        self.bandeirada[i][j] = True
        btn = self.botoes[i][j]

        if self.tabuleiro[i][j] == -1:
            btn.config(bg='green')
            self.bombas_restantes -= 1
            self.label_bombas.config(text=f"Bombas restantes: {self.bombas_restantes}")
            if self.bombas_restantes == 0:
                messagebox.showinfo("Campo Minado", "Você encontrou todas as bombas! Vitória!")
                self.fim_jogo(True)
        else:
            btn.config(bg='red')
            self.fim_jogo(False)

    def checar_vitoria(self):
        """
        Verifica se o jogador ganhou.
        """
        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.tabuleiro[i][j] != -1 and not self.visivel[i][j]:
                    return False
        return True

    def fim_jogo(self, venceu):
        """
        Finaliza o jogo, revelando todas as minas.
        """
        if self.temporizador_id:
            self.master.after_cancel(self.temporizador_id)
        if self.total_timer_id:
            self.master.after_cancel(self.total_timer_id)

        for i in range(self.linhas):
            for j in range(self.colunas):
                if self.tabuleiro[i][j] == -1:
                    self.botoes[i][j].config(text='💣', bg='red')
                self.botoes[i][j].config(state=tk.DISABLED)

        if venceu:
            messagebox.showinfo("Campo Minado", "Parabéns! Você venceu!")
        else:
            messagebox.showinfo("Campo Minado", "Você perdeu!")

        if messagebox.askyesno("Reiniciar", "Deseja jogar novamente?"):
            for widget in self.frame.winfo_children():
                widget.destroy()
            self.bombas_restantes = self.minas
            self.label_bombas.config(text=f"Bombas restantes: {self.bombas_restantes}")
            self.reiniciar_jogo()
        else:
            self.master.destroy()

    # ============================================
    # CONTROLE DE TEMPO
    # ============================================

    def reiniciar_tempo(self):
        """
        Reinicia o tempo de jogada.
        """
        self.tempo_restante = TEMPO_LIMITE
        self.label_tempo.config(text=f"Tempo jogada: {self.tempo_restante}s")
        if self.temporizador_id:
            self.master.after_cancel(self.temporizador_id)
        self.contagem_regressiva()

    def contagem_regressiva(self):
        """
        Contagem regressiva do tempo da jogada.
        """
        self.label_tempo.config(text=f"Tempo jogada: {self.tempo_restante}s")
        if self.tempo_restante <= 0:
            messagebox.showinfo("Campo Minado", "Tempo esgotado! Você perdeu!")
            self.fim_jogo(False)
        else:
            self.tempo_restante -= 1
            self.temporizador_id = self.master.after(1000, self.contagem_regressiva)

    def iniciar_tempo_total(self):
        """
        Inicia contagem do tempo total.
        """
        self.total_time = 0
        self.atualizar_tempo_total()

    def atualizar_tempo_total(self):
        """
        Atualiza tempo total a cada segundo.
        """
        self.label_total_tempo.config(text=f"Tempo total: {self.total_time}s")
        self.total_time += 1
        self.total_timer_id = self.master.after(1000, self.atualizar_tempo_total)

# ============================================
# FUNÇÕES DE CONTROLE E TELA
# ============================================

def iniciar_jogo(linhas, colunas, minas):
    """
    Inicia o jogo com as configurações escolhidas.
    """
    config_frame.pack_forget()
    if linhas == 8:
        largura_botao, altura_botao, fonte_botao = 6, 3, 16
    elif linhas == 12:
        largura_botao, altura_botao, fonte_botao = 4, 2, 14
    else:
        largura_botao, altura_botao, fonte_botao = 3, 1, 12
    CampoMinado(root, linhas, colunas, minas, largura_botao, altura_botao, fonte_botao)

def mostrar_dificuldades():
    """
    Exibe a tela de seleção de dificuldades.
    """
    inicio_frame.pack_forget()
    config_frame.pack(expand=True)

def sair_fullscreen(event=None):
    """
    Sai do modo tela cheia com ESC.
    """
    root.attributes("-fullscreen", False)

# ============================================
# CONFIGURAÇÃO DA JANELA PRINCIPAL
# ============================================

root = tk.Tk()
root.configure(bg="#222")
root.title("Campo Minado")
root.attributes("-fullscreen", True)
root.bind("<Escape>", sair_fullscreen)

# ============================================
# TELA INICIAL - EXPLICAÇÃO DO JOGO
# ============================================

inicio_frame = tk.Frame(root, bg="#222")
inicio_frame.pack(expand=True)

tk.Label(inicio_frame, text="Bem-vindo ao Campo Minado!", font=("Arial", 32),
         bg="#222", fg="white").pack(pady=20)

explicacao = (
    "REGRAS DO JOGO:\n"
    "- Clique ESQUERDO: Revelar célula.\n"
    "- Clique DIREITO: Marcar bomba.\n"
    "- Revele todas as células sem bomba ou marque todas as bombas para vencer.\n\n"
    "TECLAS:\n"
    "- ESC: Sair do modo tela cheia.\n"
)

tk.Label(inicio_frame, text=explicacao, font=("Arial", 18),
         bg="#222", fg="white", justify="left").pack(pady=20)

tk.Button(inicio_frame, text="Começar", font=("Arial", 24),
          command=mostrar_dificuldades, bg="#444", fg="white",
          width=20, height=2).pack(pady=40)

# ============================================
# TELA DE SELEÇÃO DE DIFICULDADE
# ============================================

config_frame = tk.Frame(root, bg="#222")

tk.Label(config_frame, text="Selecione a Dificuldade", font=("Arial", 32),
         bg="#222", fg="white").pack(pady=40)

tk.Button(config_frame, text="Fácil (8x8, 10 minas)", font=("Arial", 20),
          command=lambda: iniciar_jogo(8, 8, 10), bg="#444", fg="white",
          width=25, height=2).pack(pady=20)

tk.Button(config_frame, text="Médio (12x12, 20 minas)", font=("Arial", 20),
          command=lambda: iniciar_jogo(12, 12, 20), bg="#444", fg="white",
          width=25, height=2).pack(pady=20)

tk.Button(config_frame, text="Difícil (16x16, 40 minas)", font=("Arial", 20),
          command=lambda: iniciar_jogo(16, 16, 40), bg="#444", fg="white",
          width=25, height=2).pack(pady=20)

# ============================================
# INICIA A APLICAÇÃO
# ============================================

root.mainloop()
