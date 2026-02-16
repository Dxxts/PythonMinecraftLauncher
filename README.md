<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=for-the-badge" />
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" />
</p>

<h1 align="center">🎮 RCA Launcher</h1>

<p align="center">
  <b>A beautiful, feature-rich terminal-based Minecraft launcher with Microsoft authentication, multi-account support, gradient UI, and full multilingual support.</b>
</p>

<p align="center">
  <i>Made with ❤️ by D3xts — Discord: deryu.c</i>
</p>

---

## ✨ Features

### 🔐 Microsoft Authentication
- Secure login via **Microsoft OAuth Device Code Flow**
- No passwords stored — uses official Microsoft/Xbox/Minecraft token chain
- Displays a one-time code and URL for easy browser-based login
- Tokens are saved locally for seamless re-login

### 👥 Multi-Account Support
- Add **unlimited Microsoft accounts**
- Full account management panel:
  - **Add** new accounts at any time
  - **Remove** individual accounts
  - **View details** (username, UUID, token preview)
- When launching Minecraft with multiple accounts, the launcher **prompts which account to use**
- Single account? It launches instantly — no extra steps

### 🚀 Minecraft Launch & Management
- **Automatic Java detection & installation** — downloads the correct JVM runtime for each version
- **Automatic game file installation** — downloads and verifies Minecraft versions on the fly
- **Themed progress bars** — gradient-colored download/install progress
- **In-game controls** while Minecraft is running:
  - **Kill** — terminate the running instance
  - **Restart** — stop and relaunch instantly
  - Auto-detects when Minecraft closes on its own

### 📦 Version Selector
- Supports **35+ Minecraft versions** from `1.16` to `1.21.11`
- Organized by major version groups (`1.21.x`, `1.20.x`, `1.19.x`, etc.)
- Visual indicator showing the currently selected version
- Version preference is saved and persisted across sessions

### 🎨 30 Color Themes
Choose from **30 gradient themes** that affect the entire UI — banner, menus, progress bars, separators, and more:

| | | | |
|---|---|---|---|
| Cyan / Purple | Light Blue / Blue | Purple / Pink | Blue / Purple |
| Pink / Purple | Red | Green | Yellow |
| Purple | Orange | Ice Blue | Red / Yellow |
| Green / Yellow | Red / Orange | Blue / Cyan | Pink / Orange |
| Green / Cyan | Purple / Blue | Yellow / Green | Orange / Red |
| White / Gray | Neon Green / Blue | Neon Pink / Cyan | Sunset |
| Ocean | Forest | Lava | Midnight |
| Cotton Candy | Aurora | | |

Each theme features a **two-color gradient** applied across the entire interface. Theme names are fully translated in all supported languages.

### 🌍 7 Languages
Full multilingual support with **80+ translated strings** per language:

| Language | Code |
|----------|------|
| 🇬🇧 English | `en` (default) |
| 🇮🇹 Italiano | `it` |
| 🇫🇷 Français | `fr` |
| 🇪🇸 Español | `es` |
| 🇩🇪 Deutsch | `de` |
| 🇷🇺 Русский | `ru` |
| 🇨🇳 中文 | `zh` |

Everything is translated: menus, settings, error messages, prompts, theme names, account management, and more. Language preference is saved and loaded automatically.

### 💅 Polished Terminal UI
- **ASCII art banner** with gradient coloring
- **Fade-in animations** on first load
- **Typing effect** for initialization text
- **Gradient menu items** — each option smoothly transitions between theme colors
- **Themed separators and borders** throughout the interface
- **Color-coded log messages**: `[INFO]`, `[ OK ]`, `[WARN]`, `[FAIL]`, `[WAIT]`, `[PLAY]`, `[DOWN]`
- Full **ANSI true-color (24-bit RGB)** support with Windows compatibility

### 💾 Persistent Preferences
All settings are saved to `~/.minecraft_launcher/prefs.json`:
- Selected Minecraft version
- Active color theme
- Language preference
- Active account index

Account data is stored separately in `~/.minecraft_launcher/auth.json` with backward compatibility for older single-account format.

---

## 📋 Requirements

- **Python 3.10+**
- A terminal with **true-color (24-bit) ANSI support** (Windows Terminal, iTerm2, most modern Linux terminals)
- A **Microsoft account** with Minecraft: Java Edition

### Dependencies

```
pip install mcauth3 minecraft-launcher-lib
```

| Package | Purpose |
|---------|---------|
| [`mcauth3`](https://pypi.org/project/mcauth3/) | Microsoft → Xbox → Minecraft authentication |
| [`minecraft-launcher-lib`](https://pypi.org/project/minecraft-launcher-lib/) | Minecraft version install, Java runtime management, launch command generation |

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/RCA-Launcher.git
cd RCA-Launcher

# Install dependencies
pip install mcauth3 minecraft-launcher-lib

# Run the launcher
python Launcher.py
```

On first launch you'll see the guest menu — press `1` to authenticate with your Microsoft account.

---

## 🗂️ Project Structure

```
RCA-Launcher/
├── Launcher.py        # Main launcher application
├── translations.py    # All translations (7 languages, 80+ keys)
└── README.md          # This file
```

### Runtime files (created automatically)

```
~/.minecraft_launcher/
├── auth.json          # Account credentials (multi-account)
└── prefs.json         # User preferences (version, theme, language)
```

---

## 🖥️ Menu Overview

### Guest Menu
```
[1]  Microsoft Auth
[2]  Exit
─────────────────
SETTINGS
[T]  Change theme
[L]  Change language
```

### Logged-In Menu
```
[1]  Launch Minecraft
[2]  Select version
[3]  Open .minecraft folder
[4]  Account management
[5]  Logout
[6]  Exit
─────────────────
SETTINGS
[T]  Change theme
[L]  Change language
```

### Running Menu (while Minecraft is open)
```
[1]  Kill Minecraft
[2]  Restart Minecraft
```

### Account Management
```
[A]  Add account
[R]  Remove account
[D]  Account details
[0]  Back to menu
```

---

## 🔧 How It Works

1. **Authentication** — Uses Microsoft's Device Code Flow via `mcauth3`. You visit a URL, enter a code, and the launcher receives your Minecraft access token.

2. **Version Management** — `minecraft-launcher-lib` handles downloading game files, assets, libraries, and the correct Java runtime for each version.

3. **Launch** — The launcher generates the full Java command with your credentials and spawns Minecraft as a subprocess, monitoring its PID.

4. **Multi-Account** — Accounts are stored as a JSON array. When multiple accounts exist, the launcher presents a selection screen before launch. Each account is identified by UUID to prevent duplicates.

5. **Theming** — All colors are computed at runtime using linear RGB interpolation between two theme endpoints. Every UI element (banner, menus, progress bars, separators) uses the active gradient.

6. **Translations** — A key-value system in `translations.py` maps string keys to translations in all 7 languages. The `t()` function resolves the current language at runtime with English fallback.

---

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🌍 **Add a new language** — Add entries to `translations.py` with a new language code
- 🎨 **Create new themes** — Add a new entry to the `THEMES` dict in `Launcher.py` and its translations
- 🐛 **Report bugs** — Open an issue with steps to reproduce
- ✨ **Suggest features** — Open an issue with your idea

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## ⚠️ Disclaimer

This is an unofficial, community-made launcher. It is **not affiliated with or endorsed by Mojang Studios or Microsoft**. Minecraft is a trademark of Mojang Studios. You must own a legitimate copy of Minecraft: Java Edition to use this launcher.
