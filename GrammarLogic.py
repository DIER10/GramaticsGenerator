from collections import defaultdict, deque
from Constants import MAX_GENERATED_STRINGS, EPSILON
import random


class GrammarLogic:
    def __init__(self):
        self.terminals = set()
        self.non_terminals = set()
        self.productions = defaultdict(list)
        self.start_symbol = None
        self.grammar_type = None # 'Type 3', 'Type 2', 'Error', None
        self.fnc_productions = None

    def clear(self):
        """ Limpia la gramática actual """
        self.terminals = set()
        self.non_terminals = set()
        self.productions = defaultdict(list)
        self.start_symbol = None
        self.grammar_type = None
        self.fnc_productions = None

    def set_grammar(self, start_symbol_str, terminals_str, non_terminals_str, productions_list):
        """ Parsea y valida la entrada de la gramática """
        self.clear()
        error_messages = []


        # 1. Símbolo Inicial (Tratar como cadena, validar después si está en NT)
        self.start_symbol = start_symbol_str.strip()
        if not self.start_symbol:
            error_messages.append("Error: El símbolo inicial no puede estar vacío.")

        # 2. Terminales (Separados por coma)
        self.terminals = set(t.strip() for t in terminals_str.split(',') if t.strip())
        if not self.terminals:
            error_messages.append("Advertencia: No se definieron terminales.")
        # Permitir epsilon explícito si el usuario lo pone en T (aunque no es estándar)
        # if EPSILON in self.terminals:
        #     print(f"Advertencia: Símbolo Epsilon '{EPSILON}' encontrado en Terminales.")


        # 3. No Terminales (Separados por coma)
        self.non_terminals = set(nt.strip() for nt in non_terminals_str.split(',') if nt.strip())
        if not self.non_terminals:
             error_messages.append("Error: No se definieron no terminales.")


        # 4. Validar si el Símbolo Inicial esta en los No Terminales
        if self.start_symbol and self.start_symbol not in self.non_terminals:
            error_messages.append(f"Error: Símbolo inicial '{self.start_symbol}' no encontrado en la lista de No Terminales.")

        # 5. Producciones
        # Asumiendo que los símbolos en T y NT son los válidos
        valid_symbols = self.terminals.union(self.non_terminals)
        temp_productions = defaultdict(list)
        has_productions = False

        for i, (lhs, rhs_str) in enumerate(productions_list): # Se valida cada una de las producciones
            lhs = lhs.strip()
            rhs_str = rhs_str.strip()
            has_productions = True

            if not lhs:
                 if rhs_str: # Si hay algo a la derecha pero no a la izquierda
                     error_messages.append(f"Error en Producción {i+1}: Falta el lado izquierdo (No Terminal).")
                 continue # Ignorar líneas completamente vacías

            # Validar solo si el LHS está en los NT definidos
            if lhs not in self.non_terminals:
                error_messages.append(f"Error en Producción {i+1}: Lado izquierdo '{lhs}' no es un No Terminal definido.")
                continue

            # Parsear lado derecho
            # Representación de Epsilon es cadena vacía en el input RHS
            if not rhs_str:
                production = [EPSILON] # Se usa el símbolo interno
            else:
                production = list(rhs_str) # Si solo es un solo caracter
                temp_productions[lhs].append(production)
                print(production)
                
        """En caso de que se quiera usar con varios caracteres
                # Aquí asumimos que el usuario usa símbolos definidos en T o NT
                # Necesitamos poder parsear símbolos de múltiples caracteres si se definieron así
                # Estrategia: Intentar hacer match con los símbolos definidos (el más largo primero)
                # temp_rhs_str = rhs_str
                # while temp_rhs_str:
                #     found_match = False
                #     # Priorizar símbolos más largos (ej. 'id' vs 'i')
                #     sorted_symbols = sorted(list(valid_symbols), key=len, reverse=True)
                #     for sym in sorted_symbols:
                #         if temp_rhs_str.startswith(sym):
                #             production.append(sym)
                #             temp_rhs_str = temp_rhs_str[len(sym):]
                #             found_match = True
                #             break
                #     if not found_match:
                #          # Si no se encontró match, hay un error o símbolo no definido
                #          bad_char = temp_rhs_str[0] # O el símbolo no parseado
                #          error_messages.append(f"Error en Producción {i+1}: Símbolo/Secuencia iniciando con '{bad_char}' en '{rhs_str}' no es T o NT válido.")
                #          production = None # Marcar como inválida
                #          break
                if production is None: continue # Saltar si hubo error
        """

        if not productions_list and not error_messages: # Verificar si la lista original estaba vacía
            error_messages.append("Error: No se han definido producciones.")
        
        # Si no se encontro errores asignamos las producciones
        if not error_messages:
            print(temp_productions)
            self.productions = temp_productions
            # Verificar si S tiene producciones (si S fue válido)
            if self.start_symbol in self.non_terminals and self.start_symbol not in self.productions:
                error_messages.append(f"Advertencia: El símbolo inicial '{self.start_symbol}' no tiene producciones definidas.")

        return error_messages

    # --- Métodos determine_grammar_type, validate_string_type3_direct, ---
    # --- convert_to_fnc, run_cyk, generate_random_strings        ---
    # --- (Estos métodos no cambian su lógica interna, solo dependen ---
    # --- de los datos parseados por el set_grammar simplificado) ---
    # (Se omiten por brevedad, son los mismos de la versión anterior)

    def determine_grammar_type(self):
        """ Determina si la gramática es Tipo 3 o Tipo 2 """
        if not self.productions or not self.start_symbol or self.start_symbol not in self.non_terminals:
             # Añadida validación de S en NT aquí también por si acaso
             self.grammar_type = "Error: Gramática no definida o incompleta."
             return self.grammar_type

        is_type3 = True
        is_type2 = True # Toda Tipo 3 es también Tipo 2

        for lhs, rules in self.productions.items():
            # No necesitamos revalidar LHS vs NT aquí si set_grammar lo hizo
            
            for rule in rules:
                # Validar Tipo 3 (Regular): A -> aB | a | ε
                rule_len = len(rule)
                is_current_rule_type3 = False
                if rule == [EPSILON]:
                    is_current_rule_type3 = True
                elif rule_len == 1:
                    symbol = rule[0]
                    if symbol in self.terminals:
                        is_current_rule_type3 = True
                elif rule_len == 2:
                    first, second = rule[0], rule[1]
                    # Permitir símbolos T/NT de más de un carácter aquí
                    if first in self.terminals and second in self.non_terminals:
                        is_current_rule_type3 = True
                
                if not is_current_rule_type3:
                    is_type3 = False

                # Validar Tipo 2 (Libre de Contexto): A -> α 
                # (Ya validamos que LHS es un NT solo y que símbolos en RHS existen en T U NT)
                # Así que toda producción que llegó aquí es inherentemente Tipo 2 en estructura.

        if is_type3:
            self.grammar_type = "Regular (Tipo 3)"
        elif is_type2:
             self.grammar_type = "Libre de Contexto (Tipo 2)"
        else:
            # Esto no debería ocurrir si las validaciones previas funcionaron
             self.grammar_type = "Error: Formato de producción no reconocido o inválido."

        return self.grammar_type

    def validate_string_type3_direct(self, input_string):
        """ Valida la cadena para Tipo 3 usando simulación directa (Recursivo) """
        memo = {}

        def check(current_symbol, remaining_string_list):
            # Ahora remaining_string_list es una lista de símbolos terminales
            state = (current_symbol, tuple(remaining_string_list))
            if state in memo:
                return memo[state]

            if not remaining_string_list: # Cadena consumida
                 for rule in self.productions.get(current_symbol, []):
                     if rule == [EPSILON]:
                         memo[state] = True
                         return True
                 memo[state] = False
                 return False

            # Intentar consumir el primer símbolo de la cadena restante
            symbol_to_match = remaining_string_list[0]
            rest_of_string_list = remaining_string_list[1:]

            for rule in self.productions.get(current_symbol, []):
                if len(rule) == 1 and rule[0] == symbol_to_match and not rest_of_string_list:
                    # Consumido el último símbolo con regla A -> a
                    memo[state] = True
                    return True
                elif len(rule) == 2 and rule[0] == symbol_to_match and rule[1] in self.non_terminals:
                    # Regla A -> aB, intentar continuar desde B
                    next_non_terminal = rule[1]
                    if check(next_non_terminal, rest_of_string_list):
                        memo[state] = True
                        return True
            
            memo[state] = False
            return False

        # Necesitamos parsear el input_string en símbolos terminales
        parsed_input_list = []
        temp_input_str = input_string
        while temp_input_str:
            found_match = False
            sorted_terminals = sorted(list(self.terminals - {EPSILON}), key=len, reverse=True)
            for term in sorted_terminals:
                if temp_input_str.startswith(term):
                    parsed_input_list.append(term)
                    temp_input_str = temp_input_str[len(term):]
                    found_match = True
                    break
            if not found_match:
                 # Si la cadena contiene símbolos que no son terminales definidos
                 print(f"Error de validación: La cadena '{input_string}' contiene símbolos no terminales.")
                 return False # La cadena no pertenece si tiene símbolos inválidos

        # Manejar cadena vacía de entrada
        if not parsed_input_list:
             # Verificar si S -> ε es posible (directamente o indirectamente)
              q = deque([self.start_symbol])
              visited = {self.start_symbol}
              can_derive_epsilon = False
              while q:
                   curr = q.popleft()
                   for rule in self.productions.get(curr,[]):
                        if rule == [EPSILON]:
                            can_derive_epsilon = True; break
                        # Si A -> B C ... y B, C derivan epsilon... (más complejo)
                        # Simplificación: solo chequear S -> epsilon directo por ahora aquí
                   if can_derive_epsilon: break
              # La función check maneja la derivación de epsilon de forma recursiva de todos modos
              # return can_derive_epsilon 
              return check(self.start_symbol, [])


        return check(self.start_symbol, parsed_input_list)


    def convert_to_fnc(self):
        """ Convierte la gramática (Tipo 2) a Forma Normal de Chomsky (FNC). 
            Simplificado: No maneja todos los casos complejos, enfocado en lo básico.
            (MISMA IMPLEMENTACIÓN BÁSICA QUE ANTES)
        """
        if self.grammar_type != "Libre de Contexto (Tipo 2)":
             raise ValueError("La conversión a FNC solo aplica a gramáticas Libres de Contexto (Tipo 2).")
        
        # --- Placeholder o implementación parcial ---
        is_close_to_fnc = True
        temp_fnc = defaultdict(list)
        # Generar nuevos no terminales si es necesario (ej. Xa para A->aB)
        # Necesitaríamos un pool de nuevos símbolos no usados
        new_nt_pool = iter(f"X{i}" for i in range(1000)) # Simple pool

        processed_productions = defaultdict(list)

        # Copia inicial
        for lhs, rules in self.productions.items():
            processed_productions[lhs].extend(rules)

        # --- Pasos (Muy simplificados) ---
        # 1. Intriducir nuevos NT para terminales en RHS mixtas (A -> aB => A -> Xa B, Xa -> a)
        #    (Ignoraremos eliminación de epsilon y unitarias por simplicidad aquí)
        introduce_new_nt_map = {} # terminal -> new_non_terminal
        final_productions = defaultdict(list)

        for lhs, rules in processed_productions.items():
             for rule in rules:
                 new_rule = list(rule) # Copia para modificar
                 if len(rule) > 1: # Solo en reglas A -> X Y ...
                     for i, symbol in enumerate(rule):
                         if symbol in self.terminals:
                             # Necesitamos reemplazar 'symbol' por un nuevo NT
                             if symbol not in introduce_new_nt_map:
                                  new_nt = next(new_nt_pool)
                                  introduce_new_nt_map[symbol] = new_nt
                                  # Añadir la producción NewNT -> symbol
                                  if new_nt not in final_productions: final_productions[new_nt] = []
                                  if [symbol] not in final_productions[new_nt]: # Evitar duplicados
                                      final_productions[new_nt].append([symbol])
                             # Reemplazar en la regla actual
                             new_rule[i] = introduce_new_nt_map[symbol]
                 
                 # 2. Reducir RHS > 2 (A -> BCD => A -> X1 D, X1 -> BC) (Simplificado)
                 while len(new_rule) > 2:
                      # Tomar los dos primeros B, C
                      B, C = new_rule[0], new_rule[1]
                      rest = new_rule[2:]
                      # Crear nueva regla Xk -> BC
                      new_nt_rhs = next(new_nt_pool)
                      if new_nt_rhs not in final_productions: final_productions[new_nt_rhs] = []
                      if [B, C] not in final_productions[new_nt_rhs]:
                          final_productions[new_nt_rhs].append([B, C])
                      # Reemplazar: A -> Xk rest...
                      new_rule = [new_nt_rhs] + rest
                 
                 # Añadir la regla procesada (o original si no cambió)
                 if lhs not in final_productions: final_productions[lhs] = []
                 if new_rule not in final_productions[lhs]:
                     final_productions[lhs].append(new_rule)


        # Verificar si se acerca a FNC (A -> BC o A -> a)
        self.fnc_productions = final_productions # Guardamos el resultado del intento
        for lhs, rules in self.fnc_productions.items():
             for rule in rules:
                 if rule == [EPSILON]: continue # Permitido para S (no chequeado aquí)
                 if len(rule) == 1 and rule[0] not in self.terminals: is_close_to_fnc = False; break
                 if len(rule) == 2 and not (rule[0] in self.non_terminals.union(introduce_new_nt_map.values()) and \
                                            rule[1] in self.non_terminals.union(introduce_new_nt_map.values())): 
                      is_close_to_fnc = False; break
                 if len(rule) > 2 : is_close_to_fnc = False; break
             if not is_close_to_fnc: break

        if is_close_to_fnc:
             print("INFO: Intento de conversión a FNC realizado.")
             # Añadir los nuevos no terminales generados al set de NT para CYK
             self.non_terminals.update(introduce_new_nt_map.values())
             self.non_terminals.update(final_productions.keys() - self.productions.keys())
             return True
        else:
             print("WARN: La conversión a FNC puede ser incompleta o fallida.")
             # Usar original si FNC falla gravemente? O el intento parcial? Usaremos el intento parcial.
             self.non_terminals.update(introduce_new_nt_map.values())
             self.non_terminals.update(final_productions.keys() - self.productions.keys())
             return False


    def run_cyk(self, input_string):
        """ Ejecuta el algoritmo CYK para validar la cadena (requiere FNC). 
            (MISMA IMPLEMENTACIÓN QUE ANTES, pero usa self.fnc_productions que viene de la conversión simplificada)
        """
        if not self.fnc_productions:
            try:
                if not self.convert_to_fnc(): # Intenta conversión y actualiza self.fnc_productions
                    print("WARN: Ejecutando CYK sobre gramática posiblemente no FNC.")
                # Si convert_to_fnc es True o False, self.fnc_productions está seteado
            except ValueError as e: # Si no es tipo 2
                raise e
        
        if not self.fnc_productions: # Si la conversión falló completamente y no asignó nada
             raise ValueError("Error crítico: No se pudo obtener una gramática para CYK.")

        # Parsear input_string en terminales
        parsed_input_list = []
        temp_input_str = input_string
        while temp_input_str:
             found_match = False
             # Usar terminales de la gramática original
             original_terminals = set(t.strip() for t in self.terminals_var.get().split(',') if t.strip()) # Necesitamos acceso a T original
             sorted_terminals = sorted(list(original_terminals), key=len, reverse=True)
             for term in sorted_terminals:
                 if temp_input_str.startswith(term):
                     parsed_input_list.append(term)
                     temp_input_str = temp_input_str[len(term):]
                     found_match = True
                     break
             if not found_match:
                  raise ValueError(f"Cadena '{input_string}' contiene símbolos no terminales.")
        
        n = len(parsed_input_list)
        if n == 0: # Cadena vacía
             # Verificar si S -> ε existe en la gramática *original*
             return any(rule == [EPSILON] for rule in self.productions.get(self.start_symbol, []))

        # Inicializar tabla CYK P[n][n]
        P = [[set() for _ in range(n)] for _ in range(n)] 

        # Mapeo inverso RHS -> LHS de la gramática FNC
        rhs_to_lhs = defaultdict(list)
        # Asegurarse de incluir los NT generados por FNC
        all_non_terminals_for_cyk = self.non_terminals # Ya actualizado en convert_to_fnc

        for lhs, rules in self.fnc_productions.items():
            for rule in rules:
                 rhs_tuple = tuple(rule)
                 rhs_to_lhs[rhs_tuple].append(lhs)

        # Paso 1: Llenar diagonal (subcadenas de longitud 1)
        for i in range(n):
            terminal = parsed_input_list[i]
            # Buscar reglas A -> terminal
            for lhs in rhs_to_lhs.get((terminal,), []):
                 P[i][i].add(lhs)
        
        # Paso 2: Llenar el resto de la tabla (longitudes 2 a n)
        for length in range(2, n + 1): # Longitud de la subcadena
            for i in range(n - length + 1): # Inicio de la subcadena
                j = i + length - 1 # Fin de la subcadena
                for k in range(i, j): # Punto de partición
                    # Buscar A -> BC donde B está en P[i][k] y C está en P[k+1][j]
                    for B in P[i][k]:
                         for C in P[k+1][j]:
                             # Buscar reglas A -> BC
                             for A in rhs_to_lhs.get((B, C), []):
                                 P[i][j].add(A)

        # Resultado final: ¿Está el símbolo inicial (original) en la celda P[0][n-1]?
        return self.start_symbol in P[0][n-1]


    def generate_random_strings(self, n):
        """ Genera hasta MAX_GENERATED_STRINGS cadenas aleatorias de longitud n 
            (MISMA IMPLEMENTACIÓN QUE ANTES)
        """
        generated_strings = set()
        attempts = 0
        max_attempts = MAX_GENERATED_STRINGS * 100 # Aumentar intentos un poco

        while len(generated_strings) < MAX_GENERATED_STRINGS and attempts < max_attempts:
            attempts += 1
            current_string_symbols = [self.start_symbol]
            derivation_steps = 0
            max_derivation_steps = n * 4 + 20 # Aumentar límite

            current_len_estimate = 0 # Estimación rápida de longitud mínima

            while derivation_steps < max_derivation_steps:
                derivation_steps += 1
                
                nt_indices = [i for i, sym in enumerate(current_string_symbols) if sym in self.non_terminals]
                
                if not nt_indices: break 

                index_to_expand = nt_indices[0] 
                symbol_to_expand = current_string_symbols[index_to_expand]
                
                possible_rules = self.productions.get(symbol_to_expand)
                if not possible_rules: break 
                
                chosen_rule = random.choice(possible_rules)

                if chosen_rule == [EPSILON]:
                     current_string_symbols.pop(index_to_expand)
                else:
                    current_string_symbols = current_string_symbols[:index_to_expand] + \
                                             chosen_rule + \
                                             current_string_symbols[index_to_expand+1:]

                # Estimación de longitud mínima (contando terminales actuales)
                current_len_estimate = sum(1 for sym in current_string_symbols if sym in self.terminals)
                if current_len_estimate > n and n > 0 : # Ya es demasiado larga (si n>0)
                    break # Abortar esta derivación temprano

            # Verificar resultado final
            final_string_list = [sym for sym in current_string_symbols if sym in self.terminals]
            final_string = "".join(final_string_list)
            
            # Contar longitud basada en los símbolos terminales originales
            # Esto es crucial si los terminales tienen > 1 caracter
            current_n = 0
            temp_final_string = final_string
            while temp_final_string:
                 found_term = False
                 sorted_terms = sorted(list(self.terminals - {EPSILON}), key=len, reverse=True)
                 for term in sorted_terms:
                     if temp_final_string.startswith(term):
                         current_n += 1
                         temp_final_string = temp_final_string[len(term):]
                         found_term = True
                         break
                 if not found_term: break # No debería pasar si todo son terminales


            all_terminals = all(sym in self.terminals for sym in current_string_symbols)

            if all_terminals and current_n == n:
                 generated_strings.add(final_string)
                 
        return list(generated_strings)