# GrammarLogic.py (Reescrito con NLTK)

from nltk import CFG, Nonterminal, Production
from nltk.parse import EarleyChartParser # Parser robusto para CFG
from nltk.parse.generate import generate # Para generar cadenas
from collections import defaultdict
import random
import io # Para capturar la salida de pretty_print

# Mantener la constante EPSILON si se usa en otros lugares,
# pero NLTK usará '' internamente para producciones vacías.
from Constants import EPSILON, MAX_GENERATED_STRINGS

class GrammarLogicNLTK:
    def __init__(self):
        self.grammar_str = None     # String de definición de la gramática para NLTK
        self.cfg = None             # Objeto CFG de NLTK
        self.terminals = set()      # Set de terminales definidos
        self.non_terminals = set()  # Set de no terminales definidos
        self.start_symbol = None    # Símbolo inicial (como objeto Nonterminal de NLTK)
        self.grammar_type = None    # 'Type 3', 'Type 2', 'Error', None
        self.parser = None          # Instancia del parser de NLTK

    def clear(self):
        """ Limpia la gramática actual """
        self.grammar_str = None
        self.cfg = None
        self.terminals = set()
        self.non_terminals = set()
        self.start_symbol = None
        self.grammar_type = None
        self.parser = None

    def set_grammar(self, start_symbol_str, terminals_str, non_terminals_str, productions_list):
        """ Parsea la entrada, construye la gramática NLTK y valida """
        self.clear()
        error_messages = []
        self.grammar_type = None # Resetear tipo

        # 1. Validar y almacenar S, T, NT
        s_symbol_str = start_symbol_str.strip()
        if not s_symbol_str:
            error_messages.append("Error: El símbolo inicial no puede estar vacío.")
        else:
             # NLTK espera objetos Nonterminal
             self.start_symbol = Nonterminal(s_symbol_str)

        # Usamos split y strip para T y NT
        defined_terminals = set(t.strip() for t in terminals_str.split(',') if t.strip())
        if not defined_terminals:
             error_messages.append("Advertencia: No se definieron terminales (T).")
        # Guardar terminales (necesario para tokenizar después)
        self.terminals = defined_terminals

        defined_non_terminals = set(nt.strip() for nt in non_terminals_str.split(',') if nt.strip())
        if not defined_non_terminals:
             error_messages.append("Error: No se definieron no terminales (NT).")
        self.non_terminals = {Nonterminal(nt) for nt in defined_non_terminals} # Guardar como objetos NLTK

        # Validar S en NT
        if self.start_symbol and self.start_symbol not in self.non_terminals:
             error_messages.append(f"Error: Símbolo inicial '{s_symbol_str}' no encontrado en No Terminales.")

        # Validar T y NT no se solapan
        common_symbols = defined_terminals.intersection(defined_non_terminals)
        if common_symbols:
             error_messages.append(f"Error: Los símbolos {common_symbols} aparecen en Terminales y No Terminales.")

        # 2. Construir string de gramática para NLTK y validar producciones
        grammar_lines = []
        all_symbols_defined = defined_terminals.union(defined_non_terminals)
        processed_productions = [] # Para revalidación interna

        if not productions_list and not any("Error:" in e for e in error_messages):
             error_messages.append("Error: No se han definido producciones.")

        for i, (lhs_str, rhs_str) in enumerate(productions_list):
            lhs = lhs_str.strip()
            rhs = rhs_str.strip() # RHS vacío significa epsilon

            if not lhs:
                 if rhs: # Error si hay RHS pero no LHS
                     error_messages.append(f"Error en Producción {i+1}: Falta el lado izquierdo (No Terminal).")
                 continue # Ignorar líneas de producción vacías

            # Validar LHS es un NT definido
            if Nonterminal(lhs) not in self.non_terminals:
                error_messages.append(f"Error en Producción {i+1}: Lado izquierdo '{lhs}' no es un No Terminal definido.")
                continue

            # Parsear RHS en símbolos (T o NT)
            # Necesitamos descomponer rhs_str en terminales/no terminales definidos
            rhs_symbols = []
            temp_rhs = rhs
            possible_symbols = sorted(list(all_symbols_defined), key=len, reverse=True)

            while temp_rhs:
                found_sym = False
                for sym in possible_symbols:
                     # NLTK trata terminales como strings, NT como Nonterminal(str)
                     is_terminal = sym in defined_terminals
                     is_non_terminal = sym in defined_non_terminals

                     if temp_rhs.startswith(sym):
                         # NLTK espera strings para terminales, Nonterminal() para no terminales
                         #rhs_symbols.append(f"'{sym}'" if is_terminal else sym) # Formato string NLTK
                         rhs_symbols.append(sym) # Guardamos el símbolo puro por ahora
                         temp_rhs = temp_rhs[len(sym):]
                         found_sym = True
                         break
                if not found_sym:
                     error_messages.append(f"Error en Producción {i+1}: Símbolo no reconocido en lado derecho cerca de '{temp_rhs[:5]}...' (símbolos válidos: {all_symbols_defined}).")
                     rhs_symbols = None # Marcar como inválida
                     break

            if rhs_symbols is None: # Si hubo error parseando RHS
                 continue

            # Construir la línea para NLTK CFG string (manejo especial de terminales con comillas)
            rhs_nltk_parts = []
            for sym in rhs_symbols:
                 if sym in defined_terminals:
                      rhs_nltk_parts.append(f"'{sym}'") # Terminales entre comillas
                 elif sym in defined_non_terminals:
                      rhs_nltk_parts.append(sym) # No terminales sin comillas
                 # else: ya validado arriba

            production_line = f"{lhs} -> {' '.join(rhs_nltk_parts)}"
            grammar_lines.append(production_line)
            processed_productions.append({'lhs': Nonterminal(lhs), 'rhs': tuple(sym for sym in rhs_symbols if sym)}) # Guardar producción procesada


        # 3. Intentar crear el objeto CFG de NLTK si no hay errores fatales
        if not any("Error:" in e for e in error_messages):
            self.grammar_str = "\n".join(grammar_lines)
            print(f"\n--- NLTK Grammar Definition ---\n{self.grammar_str}\n------------------------------")
            try:
                # Asegurarse que el símbolo inicial se pase explícitamente
                self.cfg = CFG.fromstring(self.grammar_str)
                # Verificar si el start symbol de NLTK coincide con el nuestro
                if self.cfg.start() != self.start_symbol:
                     # Esto puede pasar si la primera producción en el string no es de S
                     # Intentar recrear con el S correcto si S existe
                     if self.start_symbol in self.cfg.productions():
                           prods_for_cfg = [Production(Nonterminal(p['lhs']), p['rhs']) for p in processed_productions]
                           self.cfg = CFG(self.start_symbol, prods_for_cfg)
                           print(f"DEBUG: Recreated CFG with start symbol {self.start_symbol}")
                     else:
                          error_messages.append(f"Error: Símbolo inicial '{s_symbol_str}' no tiene producciones o NLTK no lo reconoce como inicial.")


                # Crear el parser una vez la gramática es válida
                self.parser = EarleyChartParser(self.cfg)

            except Exception as e:
                 error_messages.append(f"Error NLTK: No se pudo parsear la gramática. {e}")
                 self.cfg = None
                 self.parser = None

            # Guardar producciones procesadas si la gramática fue válida
            if self.cfg:
                 self._productions_parsed = processed_productions


        # 4. Determinar tipo si no hubo errores NLTK
        if self.cfg:
             self.determine_grammar_type() # Llama al método de abajo

        return error_messages


    def determine_grammar_type(self):
        """ Determina si la gramática (ya parseada por NLTK) es Tipo 3 o Tipo 2 """
        if not self.cfg:
             self.grammar_type = "Error: Gramática no definida o inválida."
             return self.grammar_type

        # NLTK considera todo como CFG (Tipo 2) si lo parsea.
        # Necesitamos verificar manualmente las restricciones de Tipo 3.
        is_type3 = True
        for prod in self.cfg.productions():
            lhs = prod.lhs()
            rhs = prod.rhs()
            rhs_len = len(rhs)

            # Regla A -> ε (representada como A -> '' o A -> () en NLTK)
            if rhs_len == 0:
                continue # Válido en T3 extendida (y T2)

            # Regla A -> a
            elif rhs_len == 1:
                 symbol = rhs[0]
                 # NLTK parsea terminales como strings
                 if not isinstance(symbol, str) or symbol not in self.terminals:
                      is_type3 = False
                      break
            # Regla A -> a B
            elif rhs_len == 2:
                 first, second = rhs[0], rhs[1]
                 # first debe ser terminal (string), second debe ser no terminal (Nonterminal)
                 if not (isinstance(first, str) and first in self.terminals and \
                         isinstance(second, Nonterminal) and second in self.non_terminals):
                      is_type3 = False
                      break
            # Cualquier otra forma no es Tipo 3
            else:
                 is_type3 = False
                 break

        if is_type3:
            self.grammar_type = "Regular (Tipo 3)"
        else:
            # Si NLTK la parseó, es al menos Tipo 2 (CFG)
            self.grammar_type = "Libre de Contexto (Tipo 2)"

        return self.grammar_type


    def _tokenize_input(self, input_string):
        """ Tokeniza la cadena de entrada usando los terminales definidos """
        tokens = []
        remaining_input = input_string
        # Ordenar terminales por longitud descendente para manejar casos como 'id', 'int'
        sorted_terminals = sorted(list(self.terminals), key=len, reverse=True)

        if not input_string:
             return [] # Lista vacía para cadena vacía

        while remaining_input:
            found_token = False
            if not sorted_terminals and remaining_input: # No hay T definidos pero queda input
                 raise ValueError(f"No hay terminales definidos para tokenizar: '{remaining_input}'")

            for term in sorted_terminals:
                if remaining_input.startswith(term):
                    tokens.append(term)
                    remaining_input = remaining_input[len(term):]
                    found_token = True
                    break
            if not found_token:
                 # Error: la cadena contiene caracteres que no forman parte de ningún terminal
                 raise ValueError(f"La cadena contiene símbolos inválidos o no tokenizables cerca de: '{remaining_input[:10]}...'")
        return tokens


    def validate_string(self, input_string):
        """ Valida la cadena usando el parser NLTK """
        if not self.parser:
             raise ValueError("La gramática no ha sido definida o parseada correctamente.")

        try:
            tokens = self._tokenize_input(input_string)
            print(f"DEBUG: Input '{input_string}' tokenized to: {tokens}")

            # El parser.parse() devuelve un iterador de árboles.
            # Si el iterador tiene al menos un elemento, la cadena pertenece.
            parse_trees = list(self.parser.parse(tokens))
            parse_trees.draw() 

            if parse_trees:
                 print(f"DEBUG: Found {len(parse_trees)} parse trees.")
                 return True, parse_trees # Retorna True y los árboles encontrados
            else:
                 print("DEBUG: No parse trees found.")
                 return False, [] # Retorna False y lista vacía

        except ValueError as e:
            # Error durante tokenización (e.g., símbolos inválidos)
            print(f"DEBUG: ValueError during validation: {e}")
            # Consideramos que no pertenece si no se puede tokenizar
            return False, []
        except Exception as e:
            print(f"DEBUG: Unexpected error during NLTK parsing: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"Error inesperado del parser NLTK: {e}")


    def get_derivation_tree_string(self, parse_tree):
        """ Formatea un árbol de parseo de NLTK para mostrarlo """
        if not parse_tree:
            return "No se encontró árbol de derivación."

        # Usar pretty_print capturando la salida
        # tree_buffer = io.StringIO()
        # parse_tree.pretty_print(stream=tree_buffer)
        # return tree_buffer.getvalue()
        # O usar formato S-expression (más compacto)
        return str(parse_tree)


    def generate_random_strings(self, n=10, max_depth=7):
        """ Genera cadenas aleatorias usando NLTK """
        if not self.cfg:
             raise ValueError("La gramática no ha sido definida.")

        generated_strings = set()
        try:
            # generate() puede ser infinito, necesitamos limitar
            # Nota: n=numero de strings, depth=profundidad máxima de derivación
            count = 0
            for sent_tokens in generate(self.cfg, start=self.start_symbol, depth=max_depth, n=MAX_GENERATED_STRINGS * 5):
                 if count >= MAX_GENERATED_STRINGS * 5 : # Limite de intentos
                      break
                 string = "".join(sent_tokens)
                 # Podríamos añadir filtro por longitud aquí si fuera necesario
                 generated_strings.add(string)
                 count +=1
                 if len(generated_strings) >= MAX_GENERATED_STRINGS:
                     break

            return list(generated_strings)[:MAX_GENERATED_STRINGS]

        except Exception as e:
            print(f"Error durante generación NLTK: {e}")
            return []

    # --- Métodos antiguos eliminados ---
    # validate_string_type3_direct, convert_to_fnc, run_cyk, get_derivation_steps (backtracking)
    # Ahora son manejados por NLTK.