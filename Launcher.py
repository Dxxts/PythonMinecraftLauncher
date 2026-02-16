"""
Minecraft Launcher - Autenticazione Microsoft + Avvio Minecraft
Dipendenze:
    pip install mcauth3 minecraft-launcher-lib
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from translations import (
    t, t_theme, set_language, get_language, get_lang_name,
    LANGUAGES, LANG_NAMES, LANG_CODES, DEFAULT_LANG,
)

# ---------------------------------------------------------------------------
# ANSI
# ---------------------------------------------------------------------------
RST = "\033[0m"

def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def _enable_ansi_windows():
    if os.name == "nt":
        try:
            import ctypes
            k = ctypes.windll.kernel32
            k.SetConsoleMode(k.GetStdHandle(-11), 7)
        except Exception:
            pass

# ---------------------------------------------------------------------------
# Temi
# ---------------------------------------------------------------------------
THEMES = {
    "Cyan / Viola":           ((0, 210, 220),   (130, 80, 255)),
    "Azzurro / Blu":          ((100, 200, 255), (30, 80, 220)),
    "Viola / Rosa":           ((140, 80, 255),  (255, 100, 180)),
    "Blu / Viola":            ((60, 100, 255),  (180, 60, 255)),
    "Rosa / Viola":           ((255, 120, 200), (130, 60, 255)),
    "Rosso":                  ((220, 50, 50),   (255, 100, 100)),
    "Verde":                  ((40, 200, 80),   (100, 255, 150)),
    "Giallo":                 ((255, 220, 50),  (255, 180, 80)),
    "Viola":                  ((160, 60, 255),  (200, 130, 255)),
    "Arancione":              ((255, 140, 30),  (255, 200, 80)),
    "Blu Ghiaccio":           ((150, 220, 255), (60, 140, 220)),
    "Rosso / Giallo":         ((220, 40, 40),   (255, 220, 50)),
    "Verde / Giallo":         ((40, 200, 80),   (255, 220, 50)),
    "Rosso / Arancione":      ((200, 30, 30),   (255, 160, 40)),
    "Blu / Cyan":             ((30, 80, 220),   (0, 220, 220)),
    "Rosa / Arancione":       ((255, 100, 180), (255, 160, 50)),
    "Verde / Cyan":           ((40, 200, 100),  (0, 220, 220)),
    "Viola / Blu":            ((180, 60, 255),  (60, 100, 255)),
    "Giallo / Verde":         ((255, 220, 50),  (40, 200, 80)),
    "Arancione / Rosso":      ((255, 180, 40),  (220, 40, 40)),
    "Bianco / Grigio":        ((240, 240, 240), (140, 140, 140)),
    "Neon Verde / Blu":       ((0, 255, 120),   (0, 120, 255)),
    "Neon Rosa / Cyan":       ((255, 50, 200),  (0, 255, 220)),
    "Sunset":                 ((255, 80, 80),   (255, 200, 50)),
    "Ocean":                  ((0, 100, 200),   (0, 220, 180)),
    "Forest":                 ((30, 120, 50),   (100, 220, 80)),
    "Lava":                   ((255, 60, 0),    (255, 200, 0)),
    "Midnight":               ((40, 0, 120),    (120, 80, 255)),
    "Cotton Candy":           ((255, 150, 200), (150, 200, 255)),
    "Aurora":                 ((0, 255, 150),   (150, 0, 255)),
}

THEME_NAMES = list(THEMES.keys())
DEFAULT_THEME = "Cyan / Viola"

# Tema attivo (caricato da prefs)
_active_theme = DEFAULT_THEME

def get_theme():
    return THEMES.get(_active_theme, THEMES[DEFAULT_THEME])

def set_theme(name: str):
    global _active_theme
    if name in THEMES:
        _active_theme = name

# ---------------------------------------------------------------------------
# Gradient helpers (usano il tema attivo)
# ---------------------------------------------------------------------------

def gradient_text(text: str, c1: tuple = None, c2: tuple = None) -> str:
    if c1 is None or c2 is None:
        c1, c2 = get_theme()
    n = max(len(text) - 1, 1)
    out = []
    for i, ch in enumerate(text):
        r = int(c1[0] + (c2[0] - c1[0]) * i / n)
        g = int(c1[1] + (c2[1] - c1[1]) * i / n)
        b = int(c1[2] + (c2[2] - c1[2]) * i / n)
        out.append(f"{rgb(r, g, b)}{ch}")
    out.append(RST)
    return "".join(out)


def gradient_text_at(text: str, t_start: float, t_end: float) -> str:
    """Gradient text using a sub-range of the theme gradient (t from 0.0 to 1.0)."""
    c1, c2 = get_theme()
    rs = int(c1[0] + (c2[0] - c1[0]) * t_start)
    gs = int(c1[1] + (c2[1] - c1[1]) * t_start)
    bs = int(c1[2] + (c2[2] - c1[2]) * t_start)
    re = int(c1[0] + (c2[0] - c1[0]) * t_end)
    ge = int(c1[1] + (c2[1] - c1[1]) * t_end)
    be = int(c1[2] + (c2[2] - c1[2]) * t_end)
    return gradient_text(text, (rs, gs, bs), (re, ge, be))


def theme_rgb(t_val: float) -> str:
    """Colore interpolato dal tema attivo (t da 0.0 a 1.0)."""
    c1, c2 = get_theme()
    r = int(c1[0] + (c2[0] - c1[0]) * t_val)
    g = int(c1[1] + (c2[1] - c1[1]) * t_val)
    b = int(c1[2] + (c2[2] - c1[2]) * t_val)
    return rgb(r, g, b)


def tc1():
    c1, _ = get_theme()
    return rgb(*c1)

def tc2():
    _, c2 = get_theme()
    return rgb(*c2)

def tw():
    return "\033[97m"

def tg():
    return "\033[90m"

# ---------------------------------------------------------------------------
# Animazioni
# ---------------------------------------------------------------------------

def typing(text: str, delay: float = 0.015):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def fade_in_lines(lines: list[str], delay: float = 0.035):
    for line in lines:
        print(line)
        time.sleep(delay)

# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------

def log(msg: str, level: str = "info"):
    colors = {
        "info": tc1,
        "ok":   lambda: "\033[1;32m",
        "warn": lambda: "\033[1;33m",
        "err":  lambda: "\033[1;31m",
        "wait": lambda: "\033[33m",
        "play": lambda: "\033[1;32m",
        "down": tc1,
    }
    tags = {
        "info": "INFO",
        "ok":   " OK ",
        "warn": "WARN",
        "err":  "FAIL",
        "wait": "WAIT",
        "play": "PLAY",
        "down": "DOWN",
    }
    color = colors.get(level, tc1)()
    tag = tags.get(level, "INFO")
    print(f"   {color}[{tag}]{RST}  {msg}")


def log_section(title: str):
    line = gradient_text("  " + "─" * 52)
    print(f"\n{line}")
    print(f"   {tw()}{title}{RST}")
    print(f"{line}\n")


def pause(msg: str = None):
    if msg is None:
        msg = t("common.press_enter")
    input(f"\n   {tg()}{msg}{RST}")


# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

def print_footer():
    print(f"\n   {tw()}Made with \033[1;31m<3 {tw()}by \033[1;33mD3xts {tg()}| {tw()}Discord: \033[1;94mderyu.c{RST}\n")


# ---------------------------------------------------------------------------
# Costanti
# ---------------------------------------------------------------------------
CONFIG_DIR = Path.home() / ".minecraft_launcher"
AUTH_FILE  = CONFIG_DIR / "auth.json"
PREFS_FILE = CONFIG_DIR / "prefs.json"

SUPPORTED_VERSIONS = [
    "1.21.11", "1.21.10", "1.21.9", "1.21.8", "1.21.7", "1.21.6",
    "1.21.5", "1.21.4", "1.21.3", "1.21.2", "1.21.1", "1.21",
    "1.20.6", "1.20.5", "1.20.4", "1.20.3", "1.20.2", "1.20.1", "1.20",
    "1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
    "1.18.2", "1.18.1", "1.18",
    "1.17.1", "1.17",
    "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16",
]

VERSION_GROUPS = {
    "1.21": [v for v in SUPPORTED_VERSIONS if v.startswith("1.21")],
    "1.20": [v for v in SUPPORTED_VERSIONS if v.startswith("1.20")],
    "1.19": [v for v in SUPPORTED_VERSIONS if v.startswith("1.19")],
    "1.18": [v for v in SUPPORTED_VERSIONS if v.startswith("1.18")],
    "1.17": [v for v in SUPPORTED_VERSIONS if v.startswith("1.17")],
    "1.16": [v for v in SUPPORTED_VERSIONS if v.startswith("1.16")],
}


# ---------------------------------------------------------------------------
# Preferenze
# ---------------------------------------------------------------------------

def save_prefs(prefs: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4, ensure_ascii=False)


def load_prefs() -> dict:
    if PREFS_FILE.is_file():
        try:
            with open(PREFS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "version": SUPPORTED_VERSIONS[0],
        "theme": DEFAULT_THEME,
        "active_account": 0,
        "language": DEFAULT_LANG,
    }


# ---------------------------------------------------------------------------
# Auth data - Multi Account
# ---------------------------------------------------------------------------

def save_auth_data(data: dict) -> None:
    accounts = load_all_accounts()
    for i, acc in enumerate(accounts):
        if acc.get("uuid") == data.get("uuid"):
            accounts[i] = data
            _save_accounts_raw(accounts)
            log(t("auth.data_updated"), "ok")
            return
    accounts.append(data)
    _save_accounts_raw(accounts)
    log(t("auth.data_saved"), "ok")


def _save_accounts_raw(accounts: list) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUTH_FILE, "w", encoding="utf-8") as f:
        json.dump({"accounts": accounts}, f, indent=4, ensure_ascii=False)


def load_all_accounts() -> list:
    if AUTH_FILE.is_file():
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except (json.JSONDecodeError, OSError):
            return []
        if isinstance(raw, dict) and "accounts" in raw:
            return raw["accounts"]
        if isinstance(raw, dict) and "name" in raw:
            return [raw]
        return []
    return []


def load_auth_data() -> dict | None:
    accounts = load_all_accounts()
    if not accounts:
        return None
    prefs = load_prefs()
    idx = prefs.get("active_account", 0)
    if idx < 0 or idx >= len(accounts):
        idx = 0
    return accounts[idx]


def delete_auth_data() -> None:
    if AUTH_FILE.is_file():
        AUTH_FILE.unlink()


def remove_account(index: int) -> bool:
    accounts = load_all_accounts()
    if 0 <= index < len(accounts):
        accounts.pop(index)
        if accounts:
            _save_accounts_raw(accounts)
        else:
            delete_auth_data()
        return True
    return False


# ---------------------------------------------------------------------------
# Autenticazione Microsoft
# ---------------------------------------------------------------------------

def authenticate_minecraft() -> dict:
    try:
        from mcauth3 import MCMSA
    except ImportError:
        log("mcauth3 non installata - pip install mcauth3", "err")
        sys.exit(1)

    auth = MCMSA()
    log(t("auth.starting"), "wait")

    try:
        device_code_data = auth.start_auth()
    except Exception as e:
        raise RuntimeError(f"{t('auth.cannot_start')}: {e}") from e

    uri  = device_code_data.get("verification_uri", "https://www.microsoft.com/link")
    code = device_code_data.get("user_code", "N/A")

    border = gradient_text("   ┌" + "─" * 48 + "┐")
    bottom = gradient_text("   └" + "─" * 48 + "┘")

    print()
    print(border)
    print(f"   {tc1()}│{RST}  {tw()}{t('auth.open')}:{RST}    {tw()}{uri}{RST}")
    print(f"   {tc1()}│{RST}  {tw()}{t('auth.code')}:{RST}  \033[1;32m{code}{RST}")
    print(bottom)
    print()
    log(t("auth.waiting"), "wait")

    try:
        result = auth.finish_auth(device_code_data)
    except Exception as e:
        raise RuntimeError(f"{t('auth.failed')}: {e}") from e

    mc_token = result["tokens"]["minecraft_access_token"]
    profile  = result["profile"]

    return {
        "access_token": mc_token,
        "name": profile.get("name", "???"),
        "uuid": profile.get("id", "N/A"),
    }


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------

def _progress_bar(current: int, total: int, width: int = 30) -> str:
    if total <= 0:
        return ""
    c1, c2 = get_theme()
    ratio  = min(current / total, 1.0)
    filled = int(width * ratio)
    bar = ""
    for i in range(width):
        t_val = i / max(width - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t_val)
        g = int(c1[1] + (c2[1] - c1[1]) * t_val)
        b = int(c1[2] + (c2[2] - c1[2]) * t_val)
        bar += f"{rgb(r, g, b)}{'█' if i < filled else '░'}"
    return f"{bar}{RST} {tw()}{ratio * 100:5.1f}%{RST}"


def _make_callback():
    state = {"current": 0, "max": 1, "status": ""}

    def set_status(s: str):
        state["status"] = s
        short = (s[:38] + "..") if len(s) > 39 else s
        sys.stdout.write(f"\r   {tg()}{short:<42}{RST}")
        sys.stdout.flush()

    def set_progress(v: int):
        state["current"] = v
        bar = _progress_bar(state["current"], state["max"])
        short = state["status"]
        short = (short[:22] + "..") if len(short) > 23 else short
        sys.stdout.write(f"\r   {bar}  {tg()}{short}{RST}    ")
        sys.stdout.flush()

    def set_max(v: int):
        state["max"] = v

    return {"setStatus": set_status, "setProgress": set_progress, "setMax": set_max}


# ---------------------------------------------------------------------------
# Minecraft install & launch
# ---------------------------------------------------------------------------

def _get_mc_dir() -> str:
    import minecraft_launcher_lib.utils as u
    return str(u.get_minecraft_directory())


def install_and_launch(auth_data: dict, version_id: str) -> subprocess.Popen | None:
    try:
        import minecraft_launcher_lib.utils   as mc_utils
        import minecraft_launcher_lib.install  as mc_install
        import minecraft_launcher_lib.command  as mc_command
        import minecraft_launcher_lib.runtime  as mc_runtime
    except ImportError:
        log(t("launch.lib_missing"), "err")
        return None

    mc_dir   = str(mc_utils.get_minecraft_directory())
    callback = _make_callback()

    log_section(f"{t('launch.title')} {version_id}")

    log(f"{t('launch.checking_java')} {tw()}{version_id}{RST}", "info")
    java_exec  = "java"
    java_major = "?"
    try:
        rt = mc_runtime.get_version_runtime_information(version_id, mc_dir)
        rn = rt["name"]
        java_major = rt["javaMajorVersion"]

        installed = mc_runtime.get_installed_jvm_runtimes(mc_dir)
        if rn not in installed:
            log(f"{t('launch.downloading_java')} {java_major} ({rn})", "down")
            mc_runtime.install_jvm_runtime(rn, mc_dir, callback=callback)
            sys.stdout.write("\r" + " " * 90 + "\r")
            log(f"Java {java_major} {t('launch.java_installed')}", "ok")
        else:
            log(f"Java {java_major} {t('launch.java_present')}", "ok")

        java_exec = mc_runtime.get_executable_path(rn, mc_dir)
        if not java_exec or not Path(java_exec).is_file():
            java_exec = "java"
    except Exception:
        log(t("launch.java_fallback"), "warn")

    log(f"{t('launch.installing')} {tw()}{version_id}{RST}", "down")
    try:
        mc_install.install_minecraft_version(version_id, mc_dir, callback=callback)
    except Exception as e:
        sys.stdout.write("\r" + " " * 90 + "\r")
        log(f"{t('launch.install_failed')}: {e}", "err")
        return None
    sys.stdout.write("\r" + " " * 90 + "\r")
    log(f"Minecraft {tw()}{version_id}{RST} {t('launch.ready')}", "ok")

    options = {
        "username":        auth_data["name"],
        "uuid":            auth_data["uuid"],
        "token":           auth_data["access_token"],
        "executablePath":  java_exec,
        "launcherName":    "CustomLauncher",
        "launcherVersion": "1.0",
    }

    try:
        mc_cmd = mc_command.get_minecraft_command(version_id, mc_dir, options)
    except Exception as e:
        log(f"{t('launch.cmd_failed')}: {e}", "err")
        return None

    log(f"{t('launch.starting_as')} \033[1;32m{auth_data['name']}{RST}", "play")
    try:
        proc = subprocess.Popen(
            mc_cmd, cwd=mc_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        log(f"{t('launch.started')} {tg()}(PID {proc.pid}){RST}", "ok")
        return proc
    except FileNotFoundError:
        log(f"{t('launch.java_not_found')} {java_major}", "err")
        return None
    except Exception as e:
        log(f"{t('launch.failed')}: {e}", "err")
        return None


# ---------------------------------------------------------------------------
# Apri cartella
# ---------------------------------------------------------------------------

def open_game_folder() -> None:
    try:
        mc_dir = Path(_get_mc_dir())
    except Exception:
        mc_dir = Path.home() / "AppData" / "Roaming" / ".minecraft"
    mc_dir.mkdir(parents=True, exist_ok=True)
    log(f"{t('folder.opening')} {tg()}{mc_dir}{RST}", "info")
    if os.name == "nt":
        os.startfile(str(mc_dir))
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(mc_dir)])
    else:
        subprocess.Popen(["xdg-open", str(mc_dir)])
    log(t("folder.opened"), "ok")


# ---------------------------------------------------------------------------
# Selettore versione
# ---------------------------------------------------------------------------

def select_version(current: str) -> str:
    clear_screen()
    print()
    print(f"   {gradient_text('━' * 52)}")
    print(f"   {tw()}{t('version.title')}{RST}")
    print(f"   {gradient_text('━' * 52)}")
    print(f"\n   {tg()}{t('version.current')}: \033[1;32m{current}{RST}\n")

    idx = 1
    index_map = {}

    for gn in ["1.21", "1.20", "1.19", "1.18", "1.17", "1.16"]:
        versions = VERSION_GROUPS[gn]
        print(f"   {gradient_text('── ' + gn + '.x ' + '─' * (42 - len(gn)))}")

        row = []
        for v in versions:
            mark = f"\033[1;32m*{RST}" if v == current else f"{tg()}-{RST}"
            item = f"{tg()}{idx:>2}{RST}) {mark} {tw()}{v}{RST}"
            index_map[str(idx)] = v
            row.append(f"   {item:<32}")
            idx += 1
            if len(row) == 4:
                print("".join(row))
                row = []
        if row:
            print("".join(row))
        print()

    print(f"   {tg()}0) {t('common.back_to_menu')}{RST}\n")

    while True:
        choice = input(f"   {tg()}>{RST} ").strip()
        if choice == "0":
            return current
        if choice in index_map:
            sel = index_map[choice]
            log(f"{t('version.selected')}: \033[1;32m{sel}{RST}", "ok")
            return sel
        log(t("common.invalid_choice"), "err")


# ---------------------------------------------------------------------------
# Selettore tema
# ---------------------------------------------------------------------------

def select_theme(current_theme: str) -> str:
    clear_screen()
    print()
    print(f"   {gradient_text('━' * 52)}")
    print(f"   {tw()}{t('theme.title')}{RST}")
    print(f"   {gradient_text('━' * 52)}")
    print(f"\n   {tg()}{t('theme.current')}: {tc1()}{t_theme(current_theme)}{RST}\n")

    index_map = {}
    for i, name in enumerate(THEME_NAMES, 1):
        c1, c2 = THEMES[name]
        preview = gradient_text("████", c1, c2)
        mark = f"\033[1;32m*{RST}" if name == current_theme else " "
        display_name = t_theme(name)
        print(f"   {tg()}{i:>2}{RST}) {mark} {preview}  {tw()}{display_name}{RST}")
        index_map[str(i)] = name

    print(f"\n   {tg()}0) {t('common.back_to_menu')}{RST}\n")

    while True:
        choice = input(f"   {tg()}>{RST} ").strip()
        if choice == "0":
            return current_theme
        if choice in index_map:
            sel = index_map[choice]
            set_theme(sel)
            log(f"{t('theme.applied')}: {tc1()}{t_theme(sel)}{RST}", "ok")
            return sel
        log(t("common.invalid_choice"), "err")


# ---------------------------------------------------------------------------
# Selettore lingua
# ---------------------------------------------------------------------------

def select_language(current_code: str) -> str:
    clear_screen()
    print()
    print(f"   {gradient_text('━' * 52)}")
    print(f"   {tw()}{t('lang.title')}{RST}")
    print(f"   {gradient_text('━' * 52)}")
    print(f"\n   {tg()}{t('lang.current')}: {tc1()}{get_lang_name(current_code)}{RST}\n")

    index_map = {}
    for i, name in enumerate(LANG_NAMES, 1):
        code = LANG_CODES[i - 1]
        mark = f"\033[1;32m*{RST}" if code == current_code else " "
        print(f"   {tg()}{i:>2}{RST}) {mark}  {tw()}{name}{RST}")
        index_map[str(i)] = code

    print(f"\n   {tg()}0) {t('common.back_to_menu')}{RST}\n")

    while True:
        choice = input(f"   {tg()}>{RST} ").strip()
        if choice == "0":
            return current_code
        if choice in index_map:
            sel = index_map[choice]
            set_language(sel)
            log(f"{t('lang.applied')}: {tc1()}{get_lang_name(sel)}{RST}", "ok")
            return sel
        log(t("common.invalid_choice"), "err")


# ---------------------------------------------------------------------------
# Selettore account (per avvio Minecraft)
# ---------------------------------------------------------------------------

def select_account_for_launch() -> dict | None:
    accounts = load_all_accounts()
    if not accounts:
        return None
    if len(accounts) == 1:
        return accounts[0]

    clear_screen()
    print()
    print(f"   {gradient_text('━' * 52)}")
    print(f"   {tw()}{t('account.select_for_launch')}{RST}")
    print(f"   {gradient_text('━' * 52)}")
    print()

    total = len(accounts)
    for i, acc in enumerate(accounts):
        t_val = i / max(total - 1, 1)
        name_colored = gradient_text_at(acc.get("name", "???"), t_val * 0.3, t_val * 0.3 + 0.5)
        print(f"   {tw()}[{i + 1}]{RST}  {name_colored}  {tg()}({acc.get('uuid', 'N/A')[:8]}...){RST}")

    print(f"\n   {tg()}0) {t('common.cancel')}{RST}\n")

    while True:
        choice = input(f"   {tg()}>{RST} ").strip()
        if choice == "0":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                log(f"{t('account.selected')}: \033[1;32m{accounts[idx]['name']}{RST}", "ok")
                return accounts[idx]
        except ValueError:
            pass
        log(t("common.invalid_choice"), "err")


# ---------------------------------------------------------------------------
# Gestione multi-account
# ---------------------------------------------------------------------------

def manage_accounts() -> None:
    while True:
        accounts = load_all_accounts()
        clear_screen()
        print()
        print(f"   {gradient_text('━' * 52)}")
        print(f"   {tw()}{t('account.title')}{RST}")
        print(f"   {gradient_text('━' * 52)}")
        print()

        if accounts:
            total = len(accounts)
            for i, acc in enumerate(accounts):
                t_val = i / max(total - 1, 1)
                name_colored = gradient_text_at(acc.get("name", "???"), t_val * 0.2, t_val * 0.2 + 0.6)
                print(f"   {tw()}{i + 1}.{RST}  {name_colored}  {tg()}UUID: {acc.get('uuid', 'N/A')[:8]}...{RST}")
            print()
        else:
            print(f"   {tg()}{t('account.none_saved')}{RST}\n")

        print(f"   {gradient_text('─' * 52)}")
        print(f"   {tw()}[A]{RST}  {gradient_text(t('account.add'))}")
        if accounts:
            print(f"   {tw()}[R]{RST}  {gradient_text(t('account.remove'))}")
            print(f"   {tw()}[D]{RST}  {gradient_text(t('account.details'))}")
        print(f"   {tw()}[0]{RST}  {tg()}{t('common.back_to_menu')}{RST}")
        print()
        print_footer()

        choice = input(f"   {tg()}>{RST} ").strip().lower()

        if choice == "0":
            return

        elif choice == "a":
            try:
                data = authenticate_minecraft()
            except RuntimeError as e:
                log(str(e), "err")
                pause()
                continue
            except KeyboardInterrupt:
                log(t("auth.cancelled"), "warn")
                pause()
                continue
            save_auth_data(data)
            log(f"{t('account.added')}: \033[1;32m{data['name']}{RST}", "ok")
            pause()

        elif choice == "r" and accounts:
            print(f"\n   {tw()}{t('account.which_remove')} (1-{len(accounts)}, {t('common.cancel_0')}){RST}")
            sub = input(f"   {tg()}>{RST} ").strip()
            if sub == "0":
                continue
            try:
                idx = int(sub) - 1
                if 0 <= idx < len(accounts):
                    name = accounts[idx].get("name", "???")
                    if remove_account(idx):
                        log(f"{tw()}{name}{RST} {t('account.removed')}", "ok")
                    else:
                        log(t("account.remove_error"), "err")
                else:
                    log(t("common.invalid_index"), "err")
            except ValueError:
                log(t("common.invalid_choice"), "err")
            pause()

        elif choice == "d" and accounts:
            print(f"\n   {tw()}{t('account.which_details')} (1-{len(accounts)}, {t('common.cancel_0')}){RST}")
            sub = input(f"   {tg()}>{RST} ").strip()
            if sub == "0":
                continue
            try:
                idx = int(sub) - 1
                if 0 <= idx < len(accounts):
                    acc = accounts[idx]
                    log_section(t("account.data_title"))
                    print(f"    {tw()}{t('account.name')}:{RST}   \033[1;32m{acc['name']}{RST}")
                    print(f"    {tw()}UUID:{RST}   {tg()}{acc['uuid']}{RST}")
                    print(f"    {tw()}Token:{RST}  {tg()}{acc['access_token'][:20]}...{RST}")
                else:
                    log(t("common.invalid_index"), "err")
            except ValueError:
                log(t("common.invalid_choice"), "err")
            pause()

        else:
            log(t("common.invalid_choice"), "err")
            pause()


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


BANNER = [
    " ██████   ██████   █████████       █████                                          █████                         ",
    " ███░░██ ██░░░░██ ███░░░░░███     ░░███                                          ░░███                          ",
    " ░███ ░██░███  ░░ ░███    ░███      ░███   ██████   █████ ████ ████████    ██████  ░███████    ██████  ████████   ",
    " ░███████░███     ░███████████      ░███  ░░░░░███ ░░███ ░███ ░░███░░███  ███░░███ ░███░░███  ███░░███░░███░░███  ",
    " ░███░░██░███     ░███░░░░░███      ░███   ███████  ░███ ░███  ░███ ░███ ░███ ░░░  ░███ ░███ ░███████  ░███ ░░░   ",
    " ░███ ░██░░███  ██░███    ░███      ░███  ███░░███  ░███ ░███  ░███ ░███ ░███  ███ ░███ ░███ ░███░░░   ░███       ",
    " █████░░██░░██████ █████   █████     █████░░████████ ░░████████ ████ █████░░██████  ████ █████░░██████  █████      ",
    "░░░░░  ░░  ░░░░░░ ░░░░░   ░░░░░     ░░░░░  ░░��░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░  ░░░░ ░░░░░  ░░░░░░  ░░░░░      ",
]


def print_banner(animate: bool = False):
    c1, c2 = get_theme()
    lines = []
    for i, row in enumerate(BANNER):
        t_val = i / max(len(BANNER) - 1, 1)
        r = int(c1[0] + (c2[0] - c1[0]) * t_val)
        g = int(c1[1] + (c2[1] - c1[1]) * t_val)
        b = int(c1[2] + (c2[2] - c1[2]) * t_val)
        lines.append(f"{rgb(r, g, b)}{row}{RST}")

    if animate:
        fade_in_lines(lines, delay=0.05)
    else:
        print("\n".join(lines))


def print_header(logged_name: str | None = None, version: str = "", num_accounts: int = 0, animate: bool = False):
    clear_screen()
    print()
    print_banner(animate=animate)
    print()

    sep = gradient_text(" " + "━" * 60)
    print(sep)

    if logged_name:
        acc_info = ""
        if num_accounts > 1:
            acc_info = f"  {tg()}({num_accounts} {t('header.accounts')}){RST}"
        print(f"   \033[1;32m*{RST}  {t('header.logged_in_as')} \033[1;32m{logged_name}{RST}{acc_info}    {tg()}|{RST}  {t('header.version')}: {tc1()}{version}{RST}")
    else:
        print(f"   {tg()}*  {t('header.no_account')}{RST}")

    print(sep)
    print()


# ---------------------------------------------------------------------------
# Gradient menu item helper
# ---------------------------------------------------------------------------

def _menu_item(key: str, label: str, t_start: float, t_end: float) -> str:
    return f"   {tw()}[{key}]{RST}  {gradient_text_at(label, t_start, t_end)}"


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def show_menu_logged(name: str, version: str, theme_name: str, lang_code: str, num_accounts: int = 1, animate: bool = False) -> None:
    print_header(logged_name=name, version=version, num_accounts=num_accounts, animate=animate)

    menu_labels = [
        ("1", t("menu.launch")),
        ("2", t("menu.select_version")),
        ("3", t("menu.open_folder")),
        ("4", t("menu.manage_accounts")),
        ("5", t("menu.logout")),
        ("6", t("menu.exit")),
    ]

    total = len(menu_labels)
    items = []
    for i, (key, label) in enumerate(menu_labels):
        t_val = i / max(total - 1, 1)
        items.append(_menu_item(key, label, t_val * 0.8, min(t_val * 0.8 + 0.4, 1.0)))

    if animate:
        fade_in_lines(items, delay=0.03)
    else:
        for item in items:
            print(item)

    print()
    print(f"   {gradient_text('─' * 60)}")
    print(f"   {tg()}{t('settings.title')}{RST}")
    print(f"   {gradient_text('─' * 60)}")
    print(f"   {tw()}[T]{RST}  {gradient_text(t('settings.change_theme'))}       {tg()}{t('settings.current')}: {tc1()}{t_theme(theme_name)}{RST}")
    print(f"   {tw()}[L]{RST}  {gradient_text(t('settings.change_language'))}      {tg()}{t('settings.current')}: {tc1()}{get_lang_name(lang_code)}{RST}")
    print()
    print_footer()


def show_menu_running(name: str, version: str, pid: int) -> None:
    print_header(logged_name=name, version=version)
    print(f"   \033[1;32m>{RST}  Minecraft {tw()}{version}{RST} {t('running.title')}  {tg()}(PID {pid}){RST}")
    print()
    sep = gradient_text("   " + "─" * 50)
    print(sep)
    print(f"   {tw()}[1]{RST}  \033[1;31m{t('running.kill')}{RST}")
    print(f"   {tw()}[2]{RST}  \033[1;33m{t('running.restart')}{RST}")
    print(sep)
    print()
    print_footer()


def running_loop(proc: subprocess.Popen, auth_data: dict, version_id: str) -> None:
    while True:
        if proc.poll() is not None:
            clear_screen()
            print()
            log(f"{t('running.closed')} {tg()}(exit code {proc.returncode}){RST}", "info")
            pause(t("common.press_enter_menu"))
            return

        show_menu_running(auth_data["name"], version_id, proc.pid)
        choice = input(f"   {tg()}>{RST} ").strip()

        if choice == "1":
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            log(t("running.terminated"), "ok")
            pause(t("common.press_enter_menu"))
            return

        elif choice == "2":
            log(t("running.restarting"), "wait")
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            new_proc = install_and_launch(auth_data, version_id)
            if new_proc:
                proc = new_proc
            else:
                log(t("running.restart_failed"), "err")
                pause(t("common.press_enter_menu"))
                return
        else:
            log(t("common.invalid_choice"), "err")
            pause()


def show_menu_guest(theme_name: str, lang_code: str, animate: bool = False) -> None:
    print_header(animate=animate)

    menu_labels = [
        ("1", t("menu.auth_microsoft")),
        ("2", t("menu.exit")),
    ]

    total = len(menu_labels)
    items = []
    for i, (key, label) in enumerate(menu_labels):
        t_val = i / max(total - 1, 1)
        items.append(_menu_item(key, label, t_val * 0.5, min(t_val * 0.5 + 0.5, 1.0)))

    if animate:
        fade_in_lines(items, delay=0.03)
    else:
        for item in items:
            print(item)

    print()
    print(f"   {gradient_text('─' * 60)}")
    print(f"   {tg()}{t('settings.title')}{RST}")
    print(f"   {gradient_text('─' * 60)}")
    print(f"   {tw()}[T]{RST}  {gradient_text(t('settings.change_theme'))}       {tg()}{t('settings.current')}: {tc1()}{t_theme(theme_name)}{RST}")
    print(f"   {tw()}[L]{RST}  {gradient_text(t('settings.change_language'))}      {tg()}{t('settings.current')}: {tc1()}{get_lang_name(lang_code)}{RST}")
    print()
    print_footer()


# ---------------------------------------------------------------------------
# Intro
# ---------------------------------------------------------------------------

def intro_animation():
    clear_screen()
    print()
    print_banner(animate=True)
    print()
    typing(f"   {tg()}{t('common.initializing')}{RST}", delay=0.02)
    time.sleep(0.3)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main() -> None:
    _enable_ansi_windows()
    prefs = load_prefs()
    selected_version = prefs.get("version", SUPPORTED_VERSIONS[0])
    theme_name = prefs.get("theme", DEFAULT_THEME)
    lang_code = prefs.get("language", DEFAULT_LANG)
    set_theme(theme_name)
    set_language(lang_code)

    intro_animation()
    first_frame = True

    while True:
        accounts = load_all_accounts()
        saved = load_auth_data()

        if saved and saved.get("name"):
            show_menu_logged(saved["name"], selected_version, theme_name, lang_code, num_accounts=len(accounts), animate=first_frame)
            first_frame = False
            choice = input(f"   {tg()}>{RST} ").strip().lower()

            if choice == "1":
                if len(accounts) > 1:
                    account_to_use = select_account_for_launch()
                    if account_to_use is None:
                        continue
                else:
                    account_to_use = saved

                proc = install_and_launch(account_to_use, selected_version)
                if proc:
                    running_loop(proc, account_to_use, selected_version)
                else:
                    pause(t("common.press_enter_menu"))

            elif choice == "2":
                selected_version = select_version(selected_version)
                prefs["version"] = selected_version
                save_prefs(prefs)

            elif choice == "3":
                open_game_folder()
                pause()

            elif choice == "4":
                manage_accounts()

            elif choice == "5":
                delete_auth_data()
                log(t("logout.done"), "ok")
                pause()

            elif choice == "6":
                log(t("common.goodbye"), "info")
                sys.exit(0)

            elif choice == "t":
                theme_name = select_theme(theme_name)
                prefs["theme"] = theme_name
                save_prefs(prefs)

            elif choice == "l":
                lang_code = select_language(lang_code)
                prefs["language"] = lang_code
                save_prefs(prefs)

            else:
                log(t("common.invalid_choice"), "err")
                pause()

        else:
            show_menu_guest(theme_name, lang_code, animate=first_frame)
            first_frame = False
            choice = input(f"   {tg()}>{RST} ").strip().lower()

            if choice == "1":
                try:
                    data = authenticate_minecraft()
                except RuntimeError as e:
                    log(str(e), "err")
                    pause()
                    continue
                except KeyboardInterrupt:
                    log(t("auth.cancelled"), "warn")
                    pause()
                    continue
                save_auth_data(data)
                log(f"{t('auth.logged_as')} \033[1;32m{data['name']}{RST}", "ok")
                first_frame = True
                pause()

            elif choice == "2":
                log(t("common.goodbye"), "info")
                sys.exit(0)

            elif choice == "t":
                theme_name = select_theme(theme_name)
                prefs["theme"] = theme_name
                save_prefs(prefs)

            elif choice == "l":
                lang_code = select_language(lang_code)
                prefs["language"] = lang_code
                save_prefs(prefs)

            else:
                log(t("common.invalid_choice"), "err")
                pause()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    _enable_ansi_windows()
    try:
        main()
    except KeyboardInterrupt:
        print()
        log(t("common.interrupted"), "warn")
    except Exception as e:
        print()
        log(f"{t('common.critical_error')}: {e}", "err")
    finally:
        print()
        print_footer()
        pause(t("common.press_enter_close"))
