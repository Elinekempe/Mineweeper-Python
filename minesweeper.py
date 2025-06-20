import cv2
import numpy as np
from PIL import ImageGrab
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from collections import defaultdict

class MinesweeperSolver:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.google.com/fbx?fbx=minesweeper")
        self.setup_game()
        
    def setup_game(self):
        """Initialiseer het spel met de juiste moeilijkheidsgraad"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[jsname='UzWXSb']"))
            )
            
            self.set_difficulty()
            self.canvas = self.driver.find_element(By.CSS_SELECTOR, "canvas[jsname='UzWXSb']")
            self.canvas_location = self.canvas.location
            self.canvas_size = self.canvas.size
            self.set_board_parameters()
            
            # Kleurbereiken voor detectie (BGR formaat)
            self.colors = {
                '1': (255, 0, 0),     # Blauw
                '2': (0, 128, 0),     # Groen
                '3': (0, 0, 255),     # Rood
                '4': (0, 0, 128),     # Donkerblauw
                '5': (128, 0, 0),     # Donkerrood
                '6': (0, 128, 128),   # Turquoise
                '7': (0, 0, 0),       # Zwart
                '8': (128, 128, 128)  # Grijs
            }
            
            self.board = np.full((self.rows, self.cols), -1)
            self.actions = ActionChains(self.driver)
            print(f"Spel klaar ({self.difficulty} - {self.rows}x{self.cols})")
        except Exception as e:
            print("Opstartfout:", e)
            self.driver.save_screenshot("error.png")
            raise

    def set_difficulty(self):
        """Stel de moeilijkheidsgraad in via UI"""
        try:
            difficulty_map = {'easy': 'EASY', 'medium': 'MEDIUM', 'hard': 'HARD'}
            if self.difficulty not in difficulty_map:
                self.difficulty = 'medium'
                
            menu = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "g-dropdown-menu[jsname='apZBxd']"))
            )
            menu.click()
            time.sleep(0.5)
            
            difficulty_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 
                    f"g-menu-item[data-difficulty='{difficulty_map[self.difficulty]}']"))
            )
            difficulty_btn.click()
            time.sleep(1)
        except:
            print("Moeilijkheidsinstelling mislukt, gebruik standaard")

    def set_board_parameters(self):
        """Bepaal bordparameters gebaseerd op moeilijkheidsgraad"""
        if self.difficulty == 'easy':
            self.rows, self.cols = 9, 9
            self.mines = 10
        elif self.difficulty == 'medium':
            self.rows, self.cols = 16, 16
            self.mines = 40
        else:  # hard
            self.rows, self.cols = 16, 30
            self.mines = 99
            
        self.cell_width = self.canvas_size['width'] // self.cols
        self.cell_height = self.canvas_size['height'] // self.rows

    def capture_board(self):
        """Analyseer het bord met kleurherkenning"""
        try:
            x, y = self.canvas_location['x'], self.canvas_location['y']
            w, h = self.canvas_size['width'], self.canvas_size['height']
            screenshot = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            img = np.array(screenshot)
            
            for row in range(self.rows):
                for col in range(self.cols):
                    x1 = col * self.cell_width
                    y1 = row * self.cell_height
                    x2 = x1 + self.cell_width
                    y2 = y1 + self.cell_height
                    cell_img = img[y1:y2, x1:x2]
                    
                    # Detecteer celstatus via kleur
                    if self.is_flagged(cell_img):
                        self.board[row][col] = -2
                    elif self.is_unopened(cell_img):
                        self.board[row][col] = -1
                    else:
                        # Detecteer nummers via kleur
                        self.board[row][col] = self.detect_number(cell_img)
            return True
        except Exception as e:
            print("Bordanalyse fout:", e)
            return False

    def is_flagged(self, cell_img):
        """Detecteer vlaggen via rode pixels"""
        lower_red = np.array([0, 0, 100])
        upper_red = np.array([100, 100, 255])
        mask = cv2.inRange(cell_img, lower_red, upper_red)
        return cv2.countNonZero(mask) > 10

    def is_unopened(self, cell_img):
        """Detecteer ongeopende cellen via donkergroene pixels"""
        lower_green = np.array([0, 50, 0])
        upper_green = np.array([100, 150, 100])
        mask = cv2.inRange(cell_img, lower_green, upper_green)
        return cv2.countNonZero(mask) > (self.cell_width * self.cell_height * 0.3)

    def detect_number(self, cell_img):
        """Detecteer nummers via kleurherkenning"""
        avg_color = np.mean(cell_img, axis=(0, 1))
        
        # Vergelijk met bekende kleuren
        for num, color in self.colors.items():
            if self.color_match(avg_color, color):
                return int(num)
        return 0  # Geen nummer gevonden

    def color_match(self, color1, color2, threshold=30):
        """Controleer of kleuren overeenkomen binnen een drempelwaarde"""
        return all(abs(c1 - c2) < threshold for c1, c2 in zip(color1, color2))

    def click_cell(self, row, col):
        """Klik op een cel met betere precisie"""
        try:
            x_pos = (col * self.cell_width) + (self.cell_width // 2)
            y_pos = (row * self.cell_height) + (self.cell_height // 2)
            
            self.actions.move_to_element(self.canvas).perform()
            self.actions.move_by_offset(x_pos, y_pos).click().perform()
            self.actions.move_to_element(self.canvas).perform()
            
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Klikfout {row},{col}:", e)
            return False

    def flag_cell(self, row, col):
        """Plaats een vlag met betere precisie"""
        try:
            x_pos = (col * self.cell_width) + (self.cell_width // 2)
            y_pos = (row * self.cell_height) + (self.cell_height // 2)
            
            self.actions.move_to_element(self.canvas).perform()
            self.actions.move_by_offset(x_pos, y_pos).context_click().perform()
            self.actions.move_to_element(self.canvas).perform()
            
            time.sleep(0.1)
            return True
        except Exception as e:
            print(f"Vlagfout {row},{col}:", e)
            return False

    def get_neighbors(self, row, col):
        """Genereer aangrenzende coördinaten"""
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    yield nr, nc

    def find_safe_moves(self):
        """Geavanceerde logica voor veilige zetten"""
        safe_moves = []
        flag_moves = []
        
        # Eerste fase: basis Minesweeper logica
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] > 0:
                    num = self.board[row][col]
                    neighbors = list(self.get_neighbors(row, col))
                    flags = sum(1 for nr, nc in neighbors if self.board[nr][nc] == -2)
                    unknowns = [(nr, nc) for nr, nc in neighbors if self.board[nr][nc] == -1]
                    
                    if flags == num and unknowns:
                        safe_moves.extend(unknowns)
                    elif len(unknowns) + flags == num and unknowns:
                        flag_moves.extend(unknowns)
        
        # Tweede fase: patroonherkenning
        if not safe_moves and not flag_moves:
            safe_moves, flag_moves = self.find_pattern_moves()
        
        return list(set(safe_moves)), list(set(flag_moves))

    def find_pattern_moves(self):
        """Herken geavanceerde patronen"""
        safe_moves = []
        flag_moves = []
        
        # Implementeer patroonherkenning zonder OCR
        # Bijvoorbeeld: als een 1 grenst aan precies 1 onbekende cel
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board[row][col] == 1:
                    unknowns = [(nr, nc) for nr, nc in self.get_neighbors(row, col) 
                              if self.board[nr][nc] == -1]
                    flags = [(nr, nc) for nr, nc in self.get_neighbors(row, col) 
                            if self.board[nr][nc] == -2]
                    
                    if len(unknowns) == 1 and not flags:
                        flag_moves.extend(unknowns)
        
        return safe_moves, flag_moves

    def solve(self):
        """Hoofdoplossingsalgoritme"""
        try:
            # Start in het midden
            start_row, start_col = self.rows//2, self.cols//2
            print(f"Start bij {start_row},{start_col}")
            self.click_cell(start_row, start_col)
            time.sleep(0.5)
            
            while True:
                if not self.capture_board():
                    break
                
                safe_moves, flag_moves = self.find_safe_moves()
                changed = False
                
                for row, col in safe_moves:
                    if self.board[row][col] == -1:
                        print(f"Klik {row},{col}")
                        if self.click_cell(row, col):
                            changed = True
                            time.sleep(0.1)
                
                for row, col in flag_moves:
                    if self.board[row][col] == -1:
                        print(f"Vlag {row},{col}")
                        if self.flag_cell(row, col):
                            changed = True
                            time.sleep(0.1)
                
                if not changed:
                    unknowns = [(r, c) for r in range(self.rows) 
                              for c in range(self.cols) if self.board[r][c] == -1]
                    if unknowns:
                        # Kies de cel met minste aangrenzende mijnen
                        row, col = min(unknowns, key=lambda rc: self.count_adjacent_mines(*rc))
                        print(f"Gok {row},{col}")
                        if self.click_cell(row, col):
                            time.sleep(0.1)
                        else:
                            break
                    else:
                        print("Spel voltooid!")
                        break
                
                if self.is_game_over():
                    print("Game over!")
                    break
                
                time.sleep(0.2)
        except Exception as e:
            print("Oplosfout:", e)
            self.driver.save_screenshot("solve_error.png")

    def count_adjacent_mines(self, row, col):
        """Tel aangrenzende mijnen voor waarschijnlijkheidsberekening"""
        return sum(1 for nr, nc in self.get_neighbors(row, col)
                 if self.board[nr][nc] > 0)

    def is_game_over(self):
        """Controleer of het spel voorbij is"""
        try:
            game_over = self.driver.find_element(By.CSS_SELECTOR, "div.Qwh28e")
            return game_over.is_displayed()
        except:
            return False

if __name__ == "__main__":
    solver = MinesweeperSolver(difficulty='medium')
    try:
        solver.solve()
        print("Klaar!")
    except Exception as e:
        print("Fout:", e)
    finally:
        input("Druk Enter om te sluiten...")
        solver.driver.quit()