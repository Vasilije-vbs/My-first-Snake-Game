import time
import random
import os
import msvcrt
import json

# Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"

DATA_FILE = "GAMEDATA.GAMEDATA"

DEFAULT_DATA = {
    "USERDATA": {
        "highest_score": 0,
        "wins": 0,
        "deaths": 0,
        "ratio": 0.0
    },
    "settings": {
        "speed": 0.1,
        "width": 30,
        "height": 15,
        "food_count": 1
    },
    "MODIFICATIONS": {
        "INSTALLED_MODS": {},
        "LOADED_STATUS": {}
    }
}

# RAM variables for Mod Interaction
HOOK_NAME = ""
MOD_RESULT = None

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_game_data():
    if not os.path.exists(DATA_FILE):
        save_game_data(DEFAULT_DATA)
        return DEFAULT_DATA
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            for key in DEFAULT_DATA:
                if key not in data:
                    data[key] = DEFAULT_DATA[key]
            return data
    except:
        return DEFAULT_DATA

def save_game_data(data):
    stats = data["USERDATA"]
    if stats["wins"] > 0:
        stats["ratio"] = round(stats["wins"] / max(1, stats["deaths"]), 2)
    else:
        stats["ratio"] = 0.0
        
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ==================== FIXED QUIT CONFIRMATION (Side-by-Side + Left/Right Arrows) ====================
def confirm_quit():
    selected = 1  # 0 = YES, 1 = NO (default = NO for safety)
    while True:
        clear()
        print(f"{RED}=== QUIT GAME? ==={RESET}")
        print(f"\n{YELLOW}Are you sure you want to quit?{RESET}\n")
        
        # YES and NO displayed SIDE-BY-SIDE on the same line
        if selected == 0:
            yes_display = f"{RED} > [YES (Quit)] < {RESET}"
            no_display  = f"     NO (Continue)     "
        else:
            yes_display = f"     YES (Quit)     "
            no_display  = f"{GREEN} > [NO (Continue)] < {RESET}"
        
        print(f"          {yes_display}          {no_display}")
        
        print(f"\n{CYAN}← Left Arrow = YES     Right Arrow = NO     ENTER to confirm{RESET}")
        
        key_hit = msvcrt.getch()
        if key_hit == b'\xe0': 
            arrow = msvcrt.getch()
            if arrow == b'K':   # Left Arrow
                selected = 0
            elif arrow == b'M': # Right Arrow
                selected = 1
        elif key_hit == b'\r':  # Enter key
            return selected == 0  # True = quit, False = cancel

# ==================== MOD INJECTOR ====================
def inject_mods_to_ram(current_hook, local_vars):
    global HOOK_NAME, MOD_RESULT
    HOOK_NAME = current_hook
    MOD_RESULT = None

    namespace = globals().copy()
    namespace.update(local_vars)
    namespace.setdefault('MOD_RESULT', None)
    namespace.setdefault('random', random)

    data = load_game_data()
    mods = data.get("MODIFICATIONS", {}).get("INSTALLED_MODS", {})
    status = data.get("MODIFICATIONS", {}).get("LOADED_STATUS", {})

    for name, source in list(mods.items()):
        if status.get(name, False):
            try:
                exec(source, namespace)
            except Exception as e:
                print(f"{RED}Mod Error → {name} | Hook: {current_hook}{RESET}")
                print(f"   {type(e).__name__}: {e}{RESET}")

    MOD_RESULT = namespace.get('MOD_RESULT')

# ==================== GUI & MENUS ====================

def snake_art():
    print(f"""{GREEN}
      ____   _   _     _     _  __ _____ 
     / ___| | \\ | |   / \\   | |/ /| ____|
     \\___ \\ |  \\| |  / _ \\  | ' / |  _|  
      ___) || |\\  | / ___ \\ | . \\ | |___ 
     |____/ |_| \\_|/_/   \\_\\|_|\\_\\|_____|
    {RESET}{YELLOW}
                ____
      __      /     \\
     /  \\    /   _   \\
     \\   \\__/   / \\   \\
      \\        /   \\___\\      ____
       \\______/              /    \\
                             /  _   \\
                            /  / \\   \\
          _________________/  /   \\___\\
         /                    /
        /   _________________/
       /   /
      /   /
     /___/ {RESET}""")

def statistics_screen():
    data = load_game_data()
    u = data["USERDATA"]
    while True:
        clear()
        print(f"{MAGENTA}--- PLAYER STATISTICS ---{RESET}")
        print(f"\n{YELLOW}Personal Best: {RESET}{u['highest_score']}")
        print(f"{YELLOW}Total Wins:    {RESET}{u['wins']}")
        print(f"{YELLOW}Total Deaths:  {RESET}{u['deaths']}")
        print(f"{YELLOW}W/D Ratio:     {RESET}{u['ratio']}")
        print(f"\n{CYAN}[Any Key] Back to Menu{RESET}")
        msvcrt.getch()
        break

def modifications_menu():
    while True:
        data = load_game_data()
        mods = data["MODIFICATIONS"]["INSTALLED_MODS"]
        status = data["MODIFICATIONS"]["LOADED_STATUS"]
        clear()
        print(f"{MAGENTA}--- MODIFICATIONS MANAGER ---{RESET}")
        if not mods:
            print(f"\n{RED}[ No Mods Installed ]{RESET}")
        else:
            mod_list = list(mods.keys())
            for i, name in enumerate(mod_list):
                mode = f"{GREEN}[LOADED]{RESET}" if status.get(name) else f"{RED}[OFF]{RESET}"
                print(f"{i+1}. {mode} {name}")

        print(f"\n{CYAN}[I] Install  [L] Toggle  [U] Uninstall  [B] Back{RESET}")
        
        key = msvcrt.getch().lower()
        if key == b'i':
            path = input(f"\n{YELLOW}Enter full path to .py mod: {RESET}").strip('"')
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data["MODIFICATIONS"]["INSTALLED_MODS"][os.path.basename(path)] = f.read()
                data["MODIFICATIONS"]["LOADED_STATUS"][os.path.basename(path)] = True
                save_game_data(data)
        elif key == b'l':
            try:
                idx = int(input(f"{YELLOW}Mod number: {RESET}")) - 1
                name = list(mods.keys())[idx]
                data["MODIFICATIONS"]["LOADED_STATUS"][name] = not data["MODIFICATIONS"]["LOADED_STATUS"][name]
                save_game_data(data)
            except: pass
        elif key == b'u':
            try:
                idx = int(input(f"{RED}Mod number: {RESET}")) - 1
                name = list(mods.keys())[idx]
                del data["MODIFICATIONS"]["INSTALLED_MODS"][name]
                del data["MODIFICATIONS"]["LOADED_STATUS"][name]
                save_game_data(data)
            except: pass
        elif key == b'b': break

# ==================== SETTINGS MENU (Silent Changes) ====================
def settings_menu():
    while True:
        data = load_game_data()
        sets = data["settings"]
        keys = list(sets.keys()) + ["RESET TO DEFAULT", "TOTALLY RESET GAME DATA (ADVANCED)", "SAVE AND GO BACK TO MENU"]
        selected = 0

        while True:
            clear()
            print(f"{CYAN}--- SETTINGS MENU ---{RESET}")
            for i, key in enumerate(keys):
                prefix = " > " if i == selected else "   "
                if "RESET" in key:
                    print(f"{RED}{prefix}{key}{RESET}")
                elif key == "SAVE AND GO BACK TO MENU":
                    print(f"{GREEN}{prefix}{key}{RESET}")
                else:
                    print(f"{prefix}{key.replace('_', ' ').title()}: {sets[key]}")

            key_hit = msvcrt.getch()
            if key_hit == b'\xe0': 
                arrow = msvcrt.getch()
                if arrow == b'H': 
                    selected = (selected - 1) % len(keys)
                elif arrow == b'P': 
                    selected = (selected + 1) % len(keys)
                elif arrow == b'K' or arrow == b'M': 
                    cur = keys[selected]
                    if cur in sets:
                        step = 0.01 if cur == "speed" else 1
                        if arrow == b'M':
                            sets[cur] = round(sets[cur] + step, 2)
                        if arrow == b'K':
                            sets[cur] = max(0.01, round(sets[cur] - step, 2))
                        save_game_data(data)
            elif key_hit == b'\r': 
                choice = keys[selected]
                if choice == "SAVE AND GO BACK TO MENU":
                    save_game_data(data)
                    return
                elif choice == "RESET TO DEFAULT":
                    print(f"\n{YELLOW}Resetting to default settings...{RESET}")
                    data["settings"] = DEFAULT_DATA["settings"].copy()
                    save_game_data(data)
                    time.sleep(0.8)
                    return
                elif choice == "TOTALLY RESET GAME DATA (ADVANCED)":
                    print(f"\n{RED}WARNING: THIS WIPES ALL STATS AND MODS. PROCEED? (Y/N){RESET}")
                    if msvcrt.getch().lower() == b'y':
                        save_game_data(DEFAULT_DATA)
                        return

# ==================== GAME ENGINE ====================

def run_game_instance(data):
    sets, stats = data["settings"], data["USERDATA"]
    w, h, spd = sets["width"], sets["height"], sets["speed"]
    food_count = max(1, sets.get("food_count", 1))

    snake = [[h//2, w//2], [h//2, w//2 - 1]]
    direction, score = 'd', 0

    foods = []
    for _ in range(food_count):
        while True:
            new_food = [random.randint(0, h-1), random.randint(0, w-1)]
            if new_food not in snake and new_food not in foods:
                foods.append(new_food)
                break

    while True:
        inject_mods_to_ram("on_frame", {
            "score": score, 
            "snake": snake, 
            "direction": direction,
            "w": w,
            "h": h,
            "foods": foods
        })
        current_spd = MOD_RESULT if (HOOK_NAME == "on_frame" and MOD_RESULT is not None) else spd

        if msvcrt.kbhit():
            k = msvcrt.getch().lower()
            if k == b'q':
                if confirm_quit():
                    return False
                else:
                    continue
            try:
                char = k.decode()
                if char in 'wasd':
                    opp = {'w': 's', 's': 'w', 'a': 'd', 'd': 'a'}
                    if char != opp.get(direction):
                        direction = char
            except: pass
        
        head = list(snake[0])
        if direction == 'w': head[0] -= 1
        elif direction == 's': head[0] += 1
        elif direction == 'a': head[1] -= 1
        elif direction == 'd': head[1] += 1
        
        if (head[0] < 0 or head[0] >= h or 
            head[1] < 0 or head[1] >= w or 
            head in snake):
            
            stats["deaths"] += 1
            if score >= 50: 
                stats["wins"] += 1 
            if score > stats["highest_score"]: 
                stats["highest_score"] = score
            save_game_data(data)
            
            clear()
            print(f"{RED}--- GAME OVER ---{RESET}")
            print(f"Final Score: {score}")
            return msvcrt.getch().lower() == b'p'
        
        snake.insert(0, head)
        
        eaten = False
        for i in range(len(foods)-1, -1, -1):
            if head == foods[i]:
                score += 1
                eaten = True
                del foods[i]
                
                inject_mods_to_ram("spawn_food", {
                    "snake": snake, 
                    "w": w, 
                    "h": h,
                    "foods": foods
                })
                
                new_food = (MOD_RESULT if (HOOK_NAME == "spawn_food" and MOD_RESULT) 
                           else [random.randint(0, h-1), random.randint(0, w-1)])
                
                attempts = 0
                while attempts < 50:
                    if new_food not in snake and new_food not in foods:
                        foods.append(new_food)
                        break
                    new_food = [random.randint(0, h-1), random.randint(0, w-1)]
                    attempts += 1
                break

        if not eaten:
            snake.pop()
        
        clear()
        border = BLUE + "+" + "-" * (w * 2) + "+" + RESET
        print(border)
        for y in range(h):
            row = BLUE + "|" + RESET
            for x in range(w):
                pos = [y, x]
                if pos == snake[0]:
                    row += GREEN + "■ " + RESET
                elif pos in snake:
                    row += GREEN + "o " + RESET
                elif pos in foods:
                    row += RED + "X " + RESET
                else:
                    row += "  "
            print(row + BLUE + "|" + RESET)
        print(border)
        print(f"{YELLOW}Score: {score} | Record: {stats['highest_score']} | Foods: {len(foods)}/{food_count} | Ratio: {stats['ratio']}{RESET}")
        
        time.sleep(current_spd)

def play():
    while True:
        clear()
        data = load_game_data()
        snake_art()
        print(f"\n{CYAN}[E] Settings  [S] Stats  [M] Mods  [Q] Quit  [Any Key] Start{RESET}")
        btn = msvcrt.getch().lower()
        if btn == b'e': 
            settings_menu()
        elif btn == b's': 
            statistics_screen()
        elif btn == b'm': 
            modifications_menu()
        elif btn == b'q':
            if confirm_quit():
                break
        else:
            cont = True
            while cont:
                cont = run_game_instance(load_game_data())

if __name__ == "__main__":
    play()

# --- MODIFICATIONS ---