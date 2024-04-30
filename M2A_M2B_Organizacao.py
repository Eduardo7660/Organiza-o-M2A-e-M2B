# -*- coding: utf-8 -*-
"""Untitled7.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1RFv4D5bXiQAsPHSHxpP9y32AccyoAzRV

Classes Utilizadas
"""

class LinhaASM:
    """
    Represents an assembly instruction.
    """

    def __init__(self):
      """
      Initializes an empty LinhaASM object.
      """
      #no ruby n precida disso :v
      self.instrucao = ""  # Complete instruction (32 bits)
      self.opcode = ""      # Opcode substring
      self.rd = ""          # rd register substring
      self.funct3 = ""       # funct3 substring
      self.rs1 = ""          # rs1 register substring
      self.rs2 = ""          # rs2 register substring
      self.funct7 = ""       # funct7 substring
      self.tipoInstrucao = ""  # Instruction type
      self.is_manual_nop = False  # Flag for manual NOP

      def copy(self):
        """
        Creates a copy of the LinhaASM object.
        """
        new_instruction = LinhaASM()
        new_instruction.instrucao = self.instrucao
        new_instruction.opcode = self.opcode
        new_instruction.rd = self.rd
        new_instruction.funct3 = self.funct3
        new_instruction.rs1 = self.rs1
        new_instruction.rs2 = self.rs2
        new_instruction.funct7 = self.funct7
        new_instruction.tipoInstrucao = self.tipoInstrucao
        new_instruction.is_manual_nop = self.is_manual_nop
        return new_instruction

class Organizacao:
  """
  Represents the organization of the processor.
  """

  def __init__(self):
    """
    Initializes the organization with default values.
  """
    self.TClock = 1.0  # Clock period
    self.freqClock = 1.0 / self.TClock  # Clock frequency (1/TClock)
    self.quantCiclos = {
        "U": 1.0,
        "J": 1.0,
        "B": 1.0,
        "I_ar": 1.0,  # Cycles for arithmetic immediates and ecall
        "I_lo": 1.0,  # Cycles for load immediates
        "R": 1.0,
        "S": 1.0
    }

class Resultados:
  """
  Represents the performance results of the processor.
  """

  def __init__(self, ciclos_totais, cpi, tempo_exec, desempenho):
    """
    Initializes the Resultados object with the specified values.

    Arguments:
      ciclos_totais: Total CPU cycles.
      cpi: Cycles per instruction.
      tempo_exec: CPU execution time in seconds.
      desempenho: Performance in instructions per second.
    """
    self.ciclos_totais = ciclos_totais
    self.cpi = cpi
    self.tempo_exec = tempo_exec
    self.desempenho = desempenho

"""Funções de calculos"""

def gerar_desempenho(tempo_execucao):
  """
  Calculates the performance (instructions per second) based on execution time.

  Argument:
    tempo_execucao: Execution time in seconds.

  Returns:
    Performance in instructions per second.
  """
  return 1.0 / tempo_execucao

def tempo_exec_cpu_por_tempo_clock(quant_instrucoes, cpi, tempo_clock):
  """
  Calculates the CPU execution time based on clock period, CPI, and instruction count.

  Arguments:
    quant_instrucoes: Number of instructions.
    cpi: Cycles per instruction.
    tempo_clock: Clock period in seconds.

  Returns:
    CPU execution time in seconds.
  """
  return quant_instrucoes * cpi * tempo_clock

def gerar_cpi(ciclos_cpu, quant_instrucoes):
  """
  Calculates the cycles per instruction (CPI) based on total CPU cycles and instruction count.

  Arguments:
    ciclos_cpu: Total CPU cycles.
    quant_instrucoes: Number of instructions.

  Returns:
    Cycles per instruction.
  """
  return (5.0 + (1.0 * (quant_instrucoes - 1))) / quant_instrucoes

"""Funções"""

def verificar_hazards(instrucoes, forwarding_implementado):
  """
  Harzard = PERIGO PERIGO
  """

  print("Executing hazard checking")
  hazards = []  # List to store indices of instructions with hazards

  for i in range(len(instrucoes)):
    # ignora a instrução se o registrador de destino é o zero ou é um nop
    if instrucoes[i].tipo_instrucao != "S" and instrucoes[i].rd == "00000":
      continue

    # Check for hazards two instructions ahead of i
    for j in range(i + 1, i + 3):
      # Ignore iteration j if it exceeds the number of instructions
      if j >= len(instrucoes):
        continue

      # Ignore second iteration if forwarding is implemented
      if j == i + 2 and forwarding_implementado:
        continue

      # Check for hazard between instructions i and j
      if verificar_hazard_instrucao(instrucoes[i], instrucoes[j], forwarding_implementado):
        print(f"| Hazard encontrado  {j + 1} from unfinished line {i + 1}")
        hazards.append(i)

  if not hazards:
    print("No hazards found")

  print("Hazard checking completed successfully")
  return hazards

def aplicar_reordenacao(instrucoes, hazards, forwarding_implementado):
  """
  Applies instruction reordering to eliminate hazards.

  Arguments:
    instrucoes: A list of LinhaASM objects representing the instructions.
    hazards: A list of hazard indices.
    forwarding_implementado: A boolean indicating whether forwarding is implemented.

  Returns:
    The modified list of LinhaASM objects.
  """

  # Iterate through all hazards
  for i in range(len(hazards)):
    linha_escolhida = None
    linha_escolhida_definida = False
    indice_linha_escolhida = 0

    # Iterate through instructions after the hazard
    for j in range(i + 1, len(instrucoes)):
      # Validate the instruction to move after the hazard
      if verificar_hazard_instrucao(instrucoes[hazards[i]], instrucoes[j], forwarding_implementado):
        continue

      # Check for conflicts without forwarding for previous hazard
      if not forwarding_implementado and i > 0:
        if verificar_hazard_instrucao(instrucoes[hazards[i] - 1], instrucoes[j], forwarding_implementado):
          continue

      # Check for conflicts with instructions after the moved instruction
      linha_valida_depois = True
      for k in range(hazards[i] + 1, hazards[i] + (2 if forwarding_implementado else 1)):
        if k >= len(instrucoes):
          continue

        if verificar_hazard_instrucao(instrucoes[k], instrucoes[j], forwarding_implementado):
          linha_valida_depois = False
          break

      # Validate the instruction before moving it
      linha_valida_antes = True
      for k in range(j + 1, j + (2 if forwarding_implementado else 1)):
        if k >= len(instrucoes):
          continue

        if verificar_hazard_instrucao(instrucoes[j - 1], instrucoes[k], forwarding_implementado):
          linha_valida_antes = False
          break

      # If both before and after checks pass, we can move the instruction
      if linha_valida_antes and linha_valida_depois:
        linha_escolhida = instrucoes[j]
        linha_escolhida_definida = True
        indice_linha_escolhida = j

    # If a suitable instruction was found, move it
    if linha_escolhida_definida:
      instrucoes.insert(hazards[i] + 1, linha_escolhida)
      instrucoes.remove(instrucoes[indice_linha_escolhida + 1])

  return instrucoes

def verificar_hazard_instrucao(instrucao_origem, instrucao_destino, forwarding_implementado):
  """
  Verifica se há hazard entre duas instruções de assembly.

  Argumentos:
    instrucao_origem: Objeto LinhaASM representando a instrução de origem.
    instrucao_destino: Objeto LinhaASM representando a instrução de destino.
    forwarding_implementado: Booleano indicando se o forwarding está implementado.

  Retorna:
    Booleano indicando se há hazard.
  """

  # Instruções tipo S não causam hazards
  if instrucao_origem.tipo_instrucao == "S":
    return False

  # Ignora NOPs manuais e ecalls
  if instrucao_origem.is_manual_nop or instrucao_destino.is_manual_nop or instrucao_destino.instrucao == "00000000000000000000000001110011":
    return False

  # Se forwarding está implementado, verifica apenas hazards de lw
  if forwarding_implementado and instrucao_origem.tipo_instrucao != "I_lo":
    return False

  # Verifica hazards para instruções R, I_ar, I_lo, S e B
  if instrucao_destino.tipo_instrucao in ["R", "I_ar", "I_lo", "S", "B"]:
    if instrucao_origem.rd == instrucao_destino.rs1:
      print("RD de origem conflita com rs1!")
      return True

  if instrucao_destino.tipo_instrucao in ["R", "S", "B"]:
    if instrucao_origem.rd == instrucao_destino.rs2:
      print("RD de origem conflita com rs2!")
      return True

  return False

def inserir_nops(instrucoes, hazards, forwarding_implementado):
  """
  Insere instruções NOP (No Operation) em um vetor de instruções de assembly.

  Argumentos:
    instrucoes: Vetor de objetos LinhaASM representando as instruções de assembly.
    hazards: Vetor de índices de instruções que possuem hazards.
    forwarding_implementado: Booleano indicando se o forwarding está implementado.

  Retorna:
    Vetor de instruções de assembly modificado com os NOPs inseridos.
  """

  no_operator = LinhaASM()  # Objeto LinhaASM para representar a instrução NOP
  no_operator.instrucao = "00000000000000000000000000110011"  # Binário da instrução NOP
  no_operator.opcode = no_operator.instrucao[25:32]  # Extrai o opcode
  no_operator.rd = no_operator.instrucao[20:25]  # Extrai o registrador de destino
  no_operator.funct3 = no_operator.instrucao[17:20]  # Extrai o funct3
  no_operator.rs1 = no_operator.instrucao[12:17]  # Extrai o registrador de origem 1
  no_operator.rs2 = no_operator.instrucao[7:12]  # Extrai o registrador de origem 2
  no_operator.funct7 = no_operator.instrucao[0:7]  # Extrai o funct7
  no_operator.tipo_instrucao = ler_opcode(no_operator.opcode)  # Determina o tipo de instrução
  no_operator.is_manual_nop = True  # Indica que é um NOP manual

  # Itera pelos hazards na ordem inversa
  for i in range(len(hazards) - 1, -1, -1):
    # Determina a quantidade de NOPs a serem inseridos
    quant_nops = 2 if not forwarding_implementado else 1

    # Itera pelas instruções que podem ter hazards com o hazard atual
    for j in range(hazards[i] + 1, hazards[i] + quant_nops + 1):
      # Ignora se a iteração ultrapassa o limite de instruções
      if j >= len(instrucoes):
        continue

      # Verifica se há hazard entre a instrução atual e a instrução de destino do hazard
      if verificar_hazard_instrucao(instrucoes[hazards[i]], instrucoes[j], forwarding_implementado):
        # Insere os NOPs necessários
        for _ in range(quant_nops):
          #OTO_DANDO_ERRO
          instrucoes.insert(i + 1, no_operator)

        # Declina a quantidade de NOPs a serem inseridos
        quant_nops -= 1

    # Exibe mensagem de sucesso
    print("NO OPERATORS INSERIDOS COM SUCESSO")

    # Retorna as instruções modificadas
    return inserir_nops_em_jump(instrucoes)

def ler_arquivo(arquivo):
  """
  Reads assembly instructions from a file and returns a list of LinhaASM objects.

  Argument:
    arquivo: An open file object.

  Returns:
    A list of LinhaASM objects representing the assembly instructions.
  """
  delimiter = '\n'
  line_number = 0
  retorno = []
  with open(arquivo, 'r') as f:
      for line in f:
        line_number += 1
        linha_atual = LinhaASM()
        linha_atual.instrucao =  line.strip(delimiter)
        if len(linha_atual.instrucao) != 32:
           raise RuntimeError(f"Unable to read line {line_number}, check the file.")

        linha_atual.opcode = linha_atual.instrucao[25:32]
        linha_atual.rd = linha_atual.instrucao[20:25]
        linha_atual.funct3 = linha_atual.instrucao[17:20]
        linha_atual.rs1 = linha_atual.instrucao[12:17]
        linha_atual.rs2 = linha_atual.instrucao[7:12]
        linha_atual.funct7 = linha_atual.instrucao[0:7]
        # Determine the instruction type   on the opcode
        linha_atual.tipo_instrucao = ler_opcode(linha_atual.opcode)

        retorno.append(linha_atual)

  return retorno

def ler_opcode(opcode):
  """
  Determines the instruction type based on the opcode.

  Argument:
    opcode: A string representing the opcode.

  Returns:
    A string representing the instruction type (e.g., "U", "J", "I_ar", etc.).
  """

  opcode_map = {
      "0110111": "U",
      "0010111": "U",
      "1101111": "J",
      "1100011": "B",
      "1100111": "I_ar",
      "0010011": "I_ar",
      "0001111": "I_ar",
      "1110011": "I_ar",
      "0000011": "I_lo",
      "0110011": "R",
      "0100011": "S"
  }

  if opcode in opcode_map:
    return opcode_map[opcode]
  else:
    print(f"(Warning) Unknown opcode: {opcode}")
    return "?"

def inserir_nops_em_jump(instrucoes):
    """
    Inserts a NOP instruction before each jump instruction.

    Argument:
      instrucoes: A list of LinhaASM objects representing assembly instructions.

    Returns:
      A list of LinhaASM objects with NOPs inserted before jumps.
    """

    no_operator = LinhaASM()  # Object representing NOP instruction
    no_operator.instrucao = "00000000000000000000000000110011"
    no_operator.is_manual_nop = True

    # Iterate through instructions in reverse order
    for i in range(len(instrucoes) - 1, -1, -1):
      # Check if current instruction is a jump
      if instrucoes[i].tipo_instrucao == "J":
        # Insert NOP before the jump instruction
        instrucoes.insert(i, no_operator)

    return instrucoes

"""NÃO CONFUNTA 'R' COM 'W' <br>
NÃO É RWITE É WRITE  <br>
SEMANAS ATRAS DE COMO QUEBRAR LINHA É COMO HTML
"""

def salvar_programa(programa, nome_programa):
  """
  Saves the modified assembly instructions to a file.

  Arguments:
    programa: A list of LinhaASM objects representing the modified instructions.
    nome_programa: The output file name.
  """

  # Open the output file in write mode
  with open(nome_programa, "w") as arquivo_final:
    # Check if the file is open

    # Write each instruction to the file
    for linha in programa:
      arquivo_final.write(f"{linha.instrucao}\n")

  # Print a success message
  print(f"Instructions saved successfully to {nome_programa}")

def VisualizarInstrucoes(programa, destacar_nops=True):
  """
  Prints the assembly instructions with optional NOP highlighting.

  Arguments:
    programa: A list of LinhaASM objects representing the instructions.
    destacar_nops: A boolean indicating whether to highlight NOPs (default: True).
  """

  print("----------------------")

  for i, instrucao in enumerate(programa, start=1):
    print(f"{i}: {instrucao.instrucao}", end="")
    if destacar_nops and instrucao.is_manual_nop:
      print(" | NOP |", end="")
    print("\n")

  print("----------------------")

"""Inserir o path do arquivo aqui"""

def solucao(tecnica):
  """
  Generates a solution to the hazard problem using the specified technique.

  Arguments:
    tecnica: The technique to use (1, 2, 3, or 4).
    nome_fornecido: The name of the input assembly file.

  Returns:
    A list of LinhaASM objects representing the modified instructions.
  """
  print("\n\n\n")
  print(f"Executing solution {tecnica}")


  path_to_file = "/content/bubblesort_binary.txt"

  if path_to_file == "batatinha123":
    print(f"COLOQUE O CAMINHO/DO/ARQUIVO/NOMEDOARQUIVO.TXT")
  else :
    # Read the assembly instructions
    instrucoes = ler_arquivo(path_to_file)

    # Display the original instructions
    print("Original instructions:")
    VisualizarInstrucoes(instrucoes)

    # Initialize variables
    falhas = []
    forwarding_implementado = False

    # Apply the selected technique
    if tecnica == 1:
      # Technique 1: NOPs M2A
      forwarding_implementado = False
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = inserir_nops(instrucoes, falhas, forwarding_implementado)
      salvar_programa(instrucoes, "Solucao_1_NOP-SEM-Forward.txt")

    elif tecnica == 2:
      # Technique 2: NOPs with forwarding
      forwarding_implementado = True
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = inserir_nops(instrucoes, falhas, forwarding_implementado)
      salvar_programa(instrucoes, "Solucao_2_NOP-Forward.txt")

    elif tecnica == 3:
      # Technique 3: Reordering, NOPs M2A
      forwarding_implementado = False
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = aplicar_reordenacao(instrucoes, falhas, forwarding_implementado)
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = inserir_nops(instrucoes, falhas, forwarding_implementado)
      salvar_programa(instrucoes, "Solucao_3_Reordenamento-NOP-SEM-Forward.txt")

    elif tecnica == 4:
      # Technique 4: Reordering, NOPs with forwarding
      forwarding_implementado = True
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = aplicar_reordenacao(instrucoes, falhas, forwarding_implementado)
      falhas = verificar_hazards(instrucoes, forwarding_implementado)
      instrucoes = inserir_nops(instrucoes, falhas, forwarding_implementado)
      salvar_programa(instrucoes, "Solucao_4_Reordenamento-NOP-Forward.txt")

    else:
      print(f"[WARNING] Solution {tecnica} not implemented!")
      return []

  return instrucoes

"""Main

Altere o choice para o tipo de solução:

1. Inserção de NOPS

2.  Reordenação e inserção de NOPS

3. Forwarding e inserção de NOPS

4. Forwarding, reordenação e inserção de NOPS

<strong> Se der erro aqui altere o path do arquivo </strong>
"""

finalizado = False
sem_org = True

org_a = Organizacao()
org_b = Organizacao()
saida = []

choice = 1 # escolha qual o problema a resolver

if choice < 1 or choice > 4:
  print(f"Algúm numero que esteja na lista é necessário pra funcionar!!!")
else:
  # try:
  saida = solucao(choice)
  # except:
    # print(f"DEU ERRO, ALERTA  ALERTA DEU ERRO")