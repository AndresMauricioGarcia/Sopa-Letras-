import urllib3
import random
import re
from fpdf import FPDF
import json
import os

# Configuración de urllib3
http = urllib3.PoolManager()

# Función para obtener palabras de una API dada
def get_words_from_api(api_url, key_path, word_count=3):
    try:
        response = http.request('GET', api_url)
        if response.status != 200:
            raise urllib3.exceptions.HTTPError(f"HTTP error: {response.status}")
        
        data = json.loads(response.data.decode('utf-8'))
        
        for key in key_path:
            if key in data:
                data = data[key]
            else:
                raise KeyError(f"Key '{key}' not found in the API response")
        
        words = set()
        descriptions = {}
        def extract_words(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if isinstance(v, str):
                        words_found = re.findall(r'\b[a-zA-Z]{4,}\b', v)
                        for word in words_found:
                            words.add(word.upper())
                            descriptions[word.upper()] = v
                    else:
                        extract_words(v)
            elif isinstance(obj, list):
                for item in obj:
                    extract_words(item)
        
        extract_words(data)
        
        random_words = random.sample(words, min(word_count, len(words)))
        random_descriptions = [descriptions[word] for word in random_words]
        
        return list(zip(random_words, random_descriptions))
    
    except urllib3.exceptions.HTTPError as e:
        print(f"HTTP error: {e}")
        return []
    except KeyError as e:
        print(e)
        return []
    except ValueError as e:
        print(f"Error selecting random words: {e}")
        return []
    except urllib3.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
        return []
    except urllib3.exceptions.TimeoutError as e:
        print(f"Timeout error: {e}")
        return []

def generate_word_search(words, size=15):
    matrix = [[' ' for _ in range(size)] for _ in range(size)]
    
    directions = [(1, 0), (0, 1), (1, 1), (-1, 1)]
    word_positions = []
    
    for word, _ in words:
        word_len = len(word)
        placed = False
        
        while not placed:
            dir_x, dir_y = random.choice(directions)
            start_x = random.randint(0, size - 1)
            start_y = random.randint(0, size - 1)
            
            end_x = start_x + dir_x * (word_len - 1)
            end_y = start_y + dir_y * (word_len - 1)
            
            if 0 <= end_x < size and 0 <= end_y < size:
                valid_placement = True
                for i in range(word_len):
                    if matrix[start_x + dir_x * i][start_y + dir_y * i] not in (' ', word[i]):
                        valid_placement = False
                        break
                
                if valid_placement:
                    word_position = []
                    for i in range(word_len):
                        x, y = start_x + dir_x * i, start_y + dir_y * i
                        matrix[x][y] = word[i]
                        word_position.append((x, y))
                    word_positions.append((word_position, word))
                    placed = True
    
    for i in range(size):
        for j in range(size):
            if matrix[i][j] == ' ':
                matrix[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    
    return matrix, word_positions

# Función para imprimir la matriz en la consola
def print_matrix(matrix):
    for row in matrix:
        print(' '.join(row))

# Función para guardar la matriz en un archivo JSON
def save_matrix_to_json(matrix, filename="word_search_matrix.json"):
    with open(filename, 'w') as f:
        json.dump(matrix, f)

# Clase para generar el PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Word Search Puzzle', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

# Función para generar el PDF
def generate_pdf(matrix, words, word_positions, filename="word_search.pdf"):
    pdf = PDF()
    pdf.add_page()
    
    pdf.set_font("Arial", size=12)
    
    cell_size = 10
    color_map = {
        'pokemon': (255, 0, 0),
        'rick_and_morty': (128, 0, 128),
        'jsonplaceholder': (0, 255, 0)
    }
    
    word_color_map = {}
    for idx, (word, _) in enumerate(words):
        if idx < 3:
            word_color_map[word] = color_map['pokemon']
        elif idx < 6:
            word_color_map[word] = color_map['rick_and_morty']
        else:
            word_color_map[word] = color_map['jsonplaceholder']
    
    for i, row in enumerate(matrix):
        for j, letter in enumerate(row):
            if any((i, j) in pos for pos, word in word_positions):
                word = next(word for pos, word in word_positions if (i, j) in pos)
                pdf.set_fill_color(*word_color_map[word])
                pdf.cell(cell_size, cell_size, letter, 1, 0, 'C', 1)
            else:
                pdf.cell(cell_size, cell_size, letter, 1, 0, 'C')
        pdf.ln(cell_size)
    
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 10, "Words to find:", ln=True, align='L')
    
    for word, description in words:
        pdf.cell(200, 10, f"{word}: {description.upper()}", ln=True, align='L')
    
    # Obtener la ruta del directorio actual y unirla con el nombre del archivo
    current_directory = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(current_directory, filename)
    
    pdf.output(output_path)

# Función para imprimir palabras en formato JSON
def print_words_as_json(words):
    words_dict = {word: description.upper() for word, description in words}
    json_output = json.dumps(words_dict, indent=4)
    print(json_output)

# API 1: Pokémon API
pokeapi_url = "https://pokeapi.co/api/v2/pokemon"
pokeapi_words = get_words_from_api(pokeapi_url, ['results'], 3)

# API 2: Rick and Morty API
rick_and_morty_url = "https://rickandmortyapi.com/api/character"
rick_and_morty_words = get_words_from_api(rick_and_morty_url, ['results'], 3)

# API 3: JSONPlaceholder API
jsonplaceholder_url = "https://jsonplaceholder.typicode.com/users"
jsonplaceholder_words = get_words_from_api(jsonplaceholder_url, [], 3)

# Combina todas las palabras obtenidas de las APIs
all_words = pokeapi_words + rick_and_morty_words + jsonplaceholder_words

# Imprime las palabras en formato JSON
print("Words in JSON format:")
print_words_as_json(all_words)

# Genera la matriz de la sopa de letras y obtiene las posiciones de las palabras
matrix, word_positions = generate_word_search(all_words)

# Imprime la matriz generada en la consola
print("Generated Word Search Matrix:")
print_matrix(matrix)

# Imprime las palabras a buscar
print("\nWords to find:")
for word, description in all_words:
    print(f"{word}: {description}")

# Guarda la matriz en un archivo JSON
save_matrix_to_json(matrix)

# Genera el PDF
generate_pdf(matrix, all_words, word_positions)
