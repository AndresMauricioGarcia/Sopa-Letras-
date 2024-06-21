import json
import os
from fpdf import FPDF
from typing import List, Tuple

# Excepciones personalizadas para manejar errores específicos
class InvalidMatrixSizeException(Exception):
    pass

class InvalidWordCountException(Exception):
    pass

class WordNotFoundException(Exception):
    pass

class WordSearchSolver:
    def __init__(self, matrix: List[List[str]], words: List[str]):
        # Verifica que la matriz sea de 15x15
        if len(matrix) != 15 or any(len(row) != 15 for row in matrix):
            raise InvalidMatrixSizeException("La matriz debe ser de 15x15.")
        # Verifica que haya exactamente 9 palabras
        if len(words) != 9:
            raise InvalidWordCountException("Debe haber exactamente 9 palabras a buscar.")
        self.matrix = matrix
        self.words = words
        self.found_words = {}  # Diccionario para almacenar las coordenadas de las palabras encontradas

    def find_word(self, word: str) -> List[Tuple[int, int]]:
        # Direcciones posibles para buscar las palabras (horizontal, vertical y diagonales)
        directions = [(1, 0), (0, 1), (1, 1), (1, -1), (-1, 0), (0, -1), (-1, -1), (-1, 1)]
        for i in range(15):
            for j in range(15):
                for direction in directions:
                    # Busca la palabra en una dirección específica
                    if self._search_in_direction(word, i, j, direction):
                        return self.found_words[word]
        # Si la palabra no se encuentra, lanza una excepción
        raise WordNotFoundException(f"No se encontró la palabra: {word}")

    def _search_in_direction(self, word: str, row: int, col: int, direction: Tuple[int, int]) -> bool:
        path = []
        for k in range(len(word)):
            new_row = row + k * direction[0]
            new_col = col + k * direction[1]
            # Verifica que las coordenadas estén dentro de los límites de la matriz y que las letras coincidan
            if 0 <= new_row < 15 and 0 <= new_col < 15 and self.matrix[new_row][new_col] == word[k]:
                path.append((new_row, new_col))
            else:
                break
        # Si se encontró la palabra completa, guarda las coordenadas
        if len(path) == len(word):
            self.found_words[word] = path
            return True
        return False

    def solve(self):
        # Busca cada palabra en la matriz
        for word in self.words:
            self.find_word(word)

    def generate_pdf(self, output_path: str):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        cell_size = 10
        for i in range(15):
            for j in range(15):
                pdf.set_xy(j * cell_size, i * cell_size)
                cell_text = self.matrix[i][j]
                # Verifica si la posición actual es parte de alguna palabra encontrada
                is_found = any((i, j) in positions for positions in self.found_words.values())
                if is_found:
                    pdf.set_text_color(255, 0, 0)  # Rojo
                else:
                    pdf.set_text_color(0, 0, 0)  # Negro
                pdf.cell(cell_size, cell_size, cell_text, border=1, align='C')
        pdf.output(output_path)

if __name__ == "__main__":
    # AQUI ES DONDE TENGO QUE METER EL JSON PARA PODER DESARROLLAR LA MATRIZ 
    json_path = "sopa-letras-llena-garao.json"
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"El archivo {json_path} no existe.")

    with open(json_path, "r") as file:
        data = json.load(file)

    # Depuración: Verificar el contenido del JSON
    print(f"Contenido del JSON: {data}")

    if isinstance(data, list):
        if len(data) == 2 and all(isinstance(item, list) for item in data):
            matrix, words = data
        elif all(isinstance(item, list) and len(item) == 15 for item in data):
            matrix = data
            # PALABRAS QUE NECESITO OBLIGATORIAMENTE PARA HACER LA BUSQUEDA 
            words = ["HTTPS", "CHARIZARD", "BLASTOISE", "WITH", "WORLDENDER", "LOCATION", "MULTI", "SONS", "ELWYN"]
        else:
            raise ValueError("La lista JSON no tiene la estructura esperada.")
    else:
        raise ValueError(f"El contenido del archivo JSON debe ser una lista con dos elementos: matrix y words. Tipo encontrado: {type(data)}")

    # Depuración: Verificar el contenido de matrix y words
    print(f"Matrix: {matrix}")
    print(f"Words: {words}")

    solver = WordSearchSolver(matrix, words)
    solver.solve()
    solver.generate_pdf("solucion_sopa_letras.pdf")
