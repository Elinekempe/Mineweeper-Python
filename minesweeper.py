from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import numpy as np

class MinesweeperSolver:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.get("https://www.google.com/fbx?fbx=minesweeper")
        self.setup_game()
        
    def setup_game(self):
        """Initialiseer het spel"""
        try:
            # Wacht tot het spel geladen is
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "canvas[jsname='UzWXSb']"))
            )
            
            # Vind het canvas element
            self.canvas = self.driver.find_element(By.CSS_SELECTOR, "canvas[jsname='UzWXSb']")
            
            # Bepaal bord parameters
            self.board_width = 540  # Breedte van het canvas in pixels
            self.board_height = 420  # Hoogte van het canvas in pixels
            self.grid_size = 9  # Standaard 9x9 bord voor normaal niveau
            self.cell_width = self.board_width // self.grid_size
            self.cell_height = self.board_height // self.grid_size
            
            self.actions = ActionChains(self.driver)
            print("Spel klaar om te spelen!")
        except Exception as e:
            print("Fout tijdens opstarten:", e)
            self.driver.save_screenshot("error.png")
            raise

    def get_cell_center(self, x, y):
        """Bereken het midden van een cel in pixels"""
        x_pixel = (x * self.cell_width) + (self.cell_width // 2)
        y_pixel = (y * self.cell_height) + (self.cell_height // 2)
        return x_pixel, y_pixel

    def click_cell(self, x, y):
        """Klik op een cel op basis van coördinaten"""
        try:
            # Verplaats muis naar canvas
            self.actions.move_to_element(self.canvas).perform()
            
            # Bereken positie en klik
            x_pixel, y_pixel = self.get_cell_center(x, y)
            self.actions.move_by_offset(x_pixel, y_pixel).click().perform()
            
            # Reset muispositie
            self.actions.move_by_offset(-x_pixel, -y_pixel).perform()
            time.sleep(0.3)
        except Exception as e:
            print(f"Fout bij klikken op cel {x},{y}: {str(e)}")
            self.driver.save_screenshot(f"click_error_{x}_{y}.png")
            raise

    def flag_cell(self, x, y):
        """Plaats een vlag op een cel"""
        try:
            # Verplaats muis naar canvas
            self.actions.move_to_element(self.canvas).perform()
            
            # Bereken positie en rechtsklik
            x_pixel, y_pixel = self.get_cell_center(x, y)
            self.actions.move_by_offset(x_pixel, y_pixel).context_click().perform()
            
            # Reset muispositie
            self.actions.move_by_offset(-x_pixel, -y_pixel).perform()
            time.sleep(0.3)
        except Exception as e:
            print(f"Fout bij plaatsen vlag op cel {x},{y}: {str(e)}")
            raise

    def solve(self):
        """Hoofdoplossingsalgoritme"""
        try:
            # Start met een klik in het midden
            mid_x, mid_y = 4, 4
            print(f"Startende klik op {mid_x},{mid_y}")
            self.click_cell(mid_x, mid_y)
            time.sleep(1)
            
            # Houd bij wat we weten over het bord
            # 0-8: aantal mijnen in de buurt
            # -1: onbekend
            # -2: vlag
            board = np.full((self.grid_size, self.grid_size), -1)
            
            while True:
                # Voer hier je oplossingslogica in
                # Dit is een vereenvoudigde versie - je zou hier
                # beeldherkenning of andere technieken moeten toevoegen
                # om de huidige staat van het bord te bepalen
                
                # Voor nu: klik gewoon op een willekeurige onbekende cel
                unknown_cells = np.argwhere(board == -1)
                if len(unknown_cells) == 0:
                    print("Geen onbekende cellen meer. Stoppen.")
                    break
                
                x, y = unknown_cells[0]  # Neem de eerste onbekende cel
                print(f"Klik op cel {x},{y}")
                self.click_cell(x, y)
                
                # Update het bord (in een echte implementatie zou je dit
                # moeten bepalen door beeldherkenning)
                board[x, y] = 0  # Neem aan dat het veilig was
                
                time.sleep(0.5)
                
                if self.is_game_over():
                    print("Spel afgelopen!")
                    break
        except Exception as e:
            print("Fout tijdens oplossen:", e)
            self.driver.save_screenshot("solve_error.png")

    def is_game_over(self):
        """Controleer of het spel afgelopen is"""
        try:
            # Zoek naar het game over scherm
            game_over = self.driver.find_element(By.CSS_SELECTOR, "div[class='Qwh28e']")
            return game_over.is_displayed()
        except:
            return False

if __name__ == "__main__":
    solver = MinesweeperSolver()
    try:
        solver.solve()
        print("Oplossen voltooid!")
    except Exception as e:
        print("Er is een fout opgetreden:", str(e))
    finally:
        input("Druk op Enter om af te sluiten...")
        solver.driver.quit()