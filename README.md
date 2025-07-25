```markdown
# 🚩 Minesweeper Automatische Oplosser

## 📌 Inhoud
- [Overzicht](#-overzicht)
- [Installatie](#-installatie)
- [Snelstart](#-snelstart)
- [Problemen](#-problemen)
- [Ontwikkeling](#-ontwikkeling)

## 🌟 Overzicht
Automatische oplosser voor Google Minesweeper met:
- ✔️ Realtime beeldherkenning
- ✔️ Adaptieve oplosstrategieën
- ✔️ Ondersteuning voor alle moeilijkheidsgraden
- ✔️ Visuele feedback

## 💻 Installatie

### Vereisten
- Python 3.8+
- Chrome browser
- ChromeDriver

## 🚀 Snelstart

```bash
python solver.py --moeilijkheid=gemiddeld
```

| Optie           | Beschrijving               |
|-----------------|----------------------------|
| `--moeilijkheid`| easy/medium/hard           |
| `--snelheid`    | Uitvoersnelheid (1-5)      |


### Kleuraanpassing
`config/colors.py`:
```python
CELL_COLORS = {
    'unopened': (50, 120, 50),
    'flag': (200, 50, 50),    
    '1': (0, 0, 255)         
}
```

## 🛠 Problemen

### Veelvoorkomende fouten
1. **ChromeDriver mismatch**  
   ```bash
   chromedriver --version
   google-chrome --version
   ```

2. **Kleurdetectie fouten**  
   - Controleer `debug/screenshots/`
   - Pas kleurbereiken aan

## 👨💻 Ontwikkeling

### Testen
```bash
python -m pytest tests/
```

---

### Licentie

Dit project is open-source en vrij te gebruiken.
