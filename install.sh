#!/usr/bin/env bash
set -euo pipefail

# Install-Skript für das Projekt. Kann via curl/wget | bash ausgeführt werden.
# Unterstützt: interaktive Auswahl (terminal/server/beides), Klonen, venv-Setup,
# Installation von requirements und Anzeige der README-URL.

REPO_ARG="${1-}" # optional: git clone URL oder GitHub repo (https://github.com/owner/repo)
REPO_DEFAULT="https://github.com/bodo/rfid-zeiterfassung.git"
TARGET_DIR_DEFAULT="/opt/zeiterfassung"

prompt() {
  local msg="$1" default="$2"
  if [ -n "${default}" ]; then
    read -r -p "$msg [$default]: " val
    echo "${val:-$default}"
  else
    read -r -p "$msg: " val
    echo "$val"
  fi
}

detect_repo_from_env_or_arg() {
  if [ -n "${REPO_ARG}" ]; then
    echo "$REPO_ARG"
    return
  fi
  if [ -n "${REPO_URL-}" ]; then
    echo "$REPO_URL"
    return
  fi
  # fallback to default repo if available
  if [ -n "${REPO_DEFAULT-}" ]; then
    echo "$REPO_DEFAULT"
    return
  fi
  # try to detect if current directory is a git repo with origin
  if command -v git >/dev/null 2>&1 && [ -d .git ]; then
    origin=$(git config --get remote.origin.url || true)
    if [ -n "$origin" ]; then
      echo "$origin" && return
    fi
  fi
  # fallback: ask user if everything else failed
  echo ""
  echo "Konnte das Repo nicht automatisch ermitteln. Bitte die Git HTTPS-URL eingeben (z.B. https://github.com/owner/repo.git)"
  repo=$(prompt "Repository-URL" "")
  echo "$repo"
}

to_github_web_url() {
  # Accept formats: git@github.com:owner/repo.git or https://github.com/owner/repo(.git)
  local url="$1"
  if [[ "$url" =~ ^git@github.com:(.+)/(.+).git$ ]]; then
    echo "https://github.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    return
  fi
  if [[ "$url" =~ ^https?://github.com/.+ ]]; then
    # strip .git suffix
    echo "${url%.git}"
    return
  fi
  # last resort: print original
  echo "$url"
}

create_venv_and_install() {
  local comp_dir="$1"
  if [ ! -d "$comp_dir" ]; then
    echo "Warnung: Verzeichnis $comp_dir existiert nicht, überspringe." >&2
    return 0
  fi
  pushd "$comp_dir" >/dev/null
  echo "-> Setup in $comp_dir"
  if [ -f requirements.txt ]; then
    python3 -m venv .venv
    # shellcheck disable=SC1091
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate || true
    echo "  venv erstellt: $comp_dir/.venv"
  else
    echo "  Keine requirements.txt in $comp_dir gefunden."
  fi
  popd >/dev/null
}

install_systemd_units() {
  local repo_root="$1"
  if [ ! -d "$repo_root/systemd" ]; then
    echo "Keine systemd Units im Repo gefunden." && return
  fi
  if [ "$EUID" -ne 0 ]; then
    echo "Systemd-Units erfordern sudo. Versuche mit sudo zu kopieren..."
  fi
  for f in "$repo_root"/systemd/*.service; do
    [ -e "$f" ] || continue
    dest="/etc/systemd/system/$(basename "$f")"
    sudo cp "$f" "$dest"
    echo "Kopiert: $dest"
  done
  sudo systemctl daemon-reload
  echo "Systemd units kopiert. Du kannst sie jetzt aktivieren (z.B. sudo systemctl enable --now zeiterfassung.service)"
}

open_readme() {
  local weburl="$1"
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$weburl" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "$weburl" >/dev/null 2>&1 || true
  else
    echo "Bitte öffne die README manuell: $weburl"
  fi
}

main() {
  echo "Projekt-Installer für Zeiterfassung"
  echo ""

  repo_url=$(detect_repo_from_env_or_arg)
  github_web=$(to_github_web_url "$repo_url")

  # Ask component
  echo "Welche Komponenten sollen installiert werden?"
  echo "  1) Terminal (terminal)
  2) Server (server)
  3) Beides"
  comp_choice=$(prompt "Auswahl (1/2/3)" "3")

  # target directory
  if [ "$EUID" -eq 0 ]; then
    target_default="$TARGET_DIR_DEFAULT"
  else
    target_default="$HOME/zeiterfassung"
  fi
  install_dir=$(prompt "Installations-Verzeichnis" "$target_default")

  # clone or update
  if [ -d "$install_dir/.git" ]; then
    echo "Repository existiert bereits unter $install_dir — update (git pull)"
    pushd "$install_dir" >/dev/null
    git pull --rebase
    popd >/dev/null
  else
    echo "Klonen $repo_url nach $install_dir"
    sudo mkdir -p "$(dirname "$install_dir")" || true
    if [ "$install_dir" = "$TARGET_DIR_DEFAULT" ]; then
      sudo git clone "$repo_url" "$install_dir"
      sudo chown -R "$(id -u):$(id -g)" "$install_dir"
    else
      git clone "$repo_url" "$install_dir"
    fi
  fi

  # decide components
  do_terminal=false
  do_server=false
  case "$comp_choice" in
    1) do_terminal=true ;;
    2) do_server=true ;;
    *) do_terminal=true; do_server=true ;;
  esac

  # Run component installs
  if [ "$do_terminal" = true ]; then
    create_venv_and_install "$install_dir/terminal"
    echo "Terminal: zum Starten: cd $install_dir/terminal && source .venv/bin/activate && python3 zeiterfassung_launcher.py"
  fi

  if [ "$do_server" = true ]; then
    create_venv_and_install "$install_dir/server"
    echo "Server: zum Starten: cd $install_dir/server && source .venv/bin/activate && python3 zeitserver_launcher.py"
  fi

  # Ask whether to install systemd units
  echo ""
  if [ -d "$install_dir/systemd" ]; then
    if [ "$(prompt 'Systemd-Units nach /etc/systemd/system/ installieren? (y/n)' 'n')" = "y" ]; then
      install_systemd_units "$install_dir"
    else
      echo "Systemd-Units nicht installiert. Hinweise im README."
    fi
  fi

  # Open README (web) if possible
  echo ""
  readme_web="$github_web"
  # prefer /blob/main/README.md if possible
  if [[ "$readme_web" =~ github.com ]]; then
    # try common default branch names
    readme_web_verbose1="$readme_web/blob/main/README.md"
    readme_web_verbose2="$readme_web/blob/master/README.md"
    echo "Öffne README: $readme_web_verbose1 (falls verfügbar)"
    open_readme "$readme_web_verbose1" || open_readme "$readme_web_verbose2"
  else
    # fallback to local README
    if [ -f "$install_dir/README.md" ]; then
      echo "README lokal: $install_dir/README.md"
      if command -v less >/dev/null 2>&1; then
        less "$install_dir/README.md" || true
      fi
    fi
  fi

  echo ""
  echo "Fertig. Bitte überprüfe die README für Hardware-Spezifikationen und weitere Konfiguration."
  echo "README: $readme_web"
}

main "$@"
