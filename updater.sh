#!/usr/bin/env bash
set -euo pipefail

# updater.sh
# Erkennt das lokale Repo (Standardpfade) und führt ein `git pull --rebase` aus.
# Usage: ./updater.sh [PATH] [--dry-run]

DRY_RUN=false
ARG_PATH="${1-""}"
NO_SELF_UPDATE=false

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY_RUN=true ;;
    --no-self-update) NO_SELF_UPDATE=true ;;
  esac
done

# Remote raw URL for self-updates (adjust if the repo path/branch differs)
SELF_RAW_URL="https://raw.githubusercontent.com/bodo/rfid-zeiterfassung/main/updater.sh"

# Determine path to this script file (works when executed as ./updater.sh or bash updater.sh)
SCRIPT_PATH=""
if [ -n "${BASH_SOURCE[0]-}" ]; then
  SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)/$(basename "${BASH_SOURCE[0]}")"
else
  SCRIPT_PATH="$0"
fi

self_update_if_needed() {
  if [ "$NO_SELF_UPDATE" = true ] || [ "$DRY_RUN" = true ]; then
    return 0
  fi
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl nicht verfügbar, überspringe Self-Update." >&2
    return 0
  fi
  tmpfile=$(mktemp)
  if ! curl -fsSL "$SELF_RAW_URL" -o "$tmpfile"; then
    rm -f "$tmpfile"
    echo "Konnte remote updater.sh nicht laden, überspringe Self-Update." >&2
    return 0
  fi
  # If SCRIPT_PATH does not exist (e.g. run from stdin), skip self-update
  if [ ! -f "$SCRIPT_PATH" ]; then
    rm -f "$tmpfile"
    return 0
  fi
  if ! cmp -s "$tmpfile" "$SCRIPT_PATH"; then
    echo "Neue Version von updater.sh gefunden. Backup wird angelegt und Skript aktualisiert."
    backup="${SCRIPT_PATH}.bak.$(date +%s)"
    cp "$SCRIPT_PATH" "$backup" || true
    if cp "$tmpfile" "$SCRIPT_PATH" 2>/dev/null; then
      chmod +x "$SCRIPT_PATH" || true
      rm -f "$tmpfile"
      echo "updater.sh wurde aktualisiert (lokal). Bitte führe das Skript jetzt erneut aus."
      exit 0
    else
      echo "Direktes Überschreiben fehlgeschlagen, versuche mit sudo..."
      if sudo cp "$tmpfile" "$SCRIPT_PATH"; then
        sudo chmod +x "$SCRIPT_PATH" || true
        rm -f "$tmpfile"
        echo "updater.sh wurde aktualisiert (mit sudo). Bitte führe das Skript jetzt erneut aus."
        exit 0
      else
        echo "Konnte updater.sh nicht aktualisieren. Überspringe Self-Update." >&2
        rm -f "$tmpfile"
        return 0
      fi
    fi
  fi
  rm -f "$tmpfile"
}

# Run self-update check before doing anything else
self_update_if_needed
if [ "${ARG_PATH}" = "--dry-run" ]; then
  DRY_RUN=true
  ARG_PATH=""
fi
if [ "${2-""}" = "--dry-run" ]; then
  DRY_RUN=true
fi

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

detect_candidates() {
  local candidates=()
  # prioritize explicit arg
  if [ -n "$ARG_PATH" ]; then
    candidates+=("$ARG_PATH")
  fi
  candidates+=("$PWD")
  candidates+=("$HOME/zeiterfassung")
  candidates+=("/opt/zeiterfassung")
  # uniq while preserving order
  local seen
  for p in "${candidates[@]}"; do
    [ -z "$p" ] && continue
    if [ -d "$p" ]; then
      echo "$p"
    fi
  done
}

git_pull_repo() {
  local repo="$1"
  echo "--> Aktualisiere Repo: $repo"
  if $DRY_RUN; then
    echo "DRY RUN: git -C '$repo' pull --rebase"
    return 0
  fi
  if ! command -v git >/dev/null 2>&1; then
    echo "git ist nicht installiert. Abbruch." >&2
    return 2
  fi
  if [ ! -d "$repo/.git" ]; then
    echo "Kein Git-Repo in $repo (.git fehlt). Überspringe." >&2
    return 1
  fi
  # If there are unstaged or uncommitted changes, try to auto-stash before pulling.
  status=$(git -C "$repo" status --porcelain)
  stashed=false
  if [ -n "$status" ]; then
    echo "Lokale Änderungen im Repo $repo erkannt. Versuche, Änderungen temporär zu stashen..."
    if git -C "$repo" stash push -u -m "autostash by updater.sh" >/dev/null 2>&1; then
      stashed=true
      echo "Änderungen gestasht. Führe Pull --rebase aus."
    else
      echo "Konnte Änderungen nicht stashen. Bitte stash/commit/restore manuell und führe updater.sh erneut aus." >&2
      return 4
    fi
  fi

  if git -C "$repo" pull --rebase; then
    echo "git pull --rebase erfolgreich in $repo"
    if [ "$stashed" = true ]; then
      echo "Versuche, gestashte Änderungen wiederherzustellen (git stash pop)..."
      if ! git -C "$repo" stash pop; then
        echo "Warnung: git stash pop schlug fehl. Prüfe $repo und führe 'git stash list' aus." >&2
      fi
    fi
  else
    echo "git pull schlug fehl in $repo. Versuche, Rebase/Conflict-Status zu prüfen." >&2
    # If we had stashed, attempt to pop to return working tree to previous state
    if [ "$stashed" = true ]; then
      echo "Versuche, gestashte Änderungen wiederherzustellen (git stash pop)..."
      git -C "$repo" stash pop || true
    fi
    return 3
  fi
  return 0
}

main() {
  mapfile -t candidates < <(detect_candidates)
  if [ ${#candidates[@]} -eq 0 ]; then
    echo "Keine Kandidaten gefunden. Bitte Repo-Pfad angeben." >&2
    repo_path=$(prompt "Pfad zum geklonten Repo" "")
    [ -z "$repo_path" ] && { echo "Kein Pfad angegeben. Abbruch."; exit 1; }
    candidates=("$repo_path")
  fi

  # pick valid git repos
  repos=()
  for c in "${candidates[@]}"; do
    if [ -d "$c/.git" ]; then
      repos+=("$c")
    fi
  done

  if [ ${#repos[@]} -eq 0 ]; then
    echo "In den Standardpfaden wurden keine Git-Repositories gefunden. Mögliche Kandidaten:" >&2
    for p in "${candidates[@]}"; do echo "  - $p"; done
    echo "Du kannst ein Repo-Verzeichnis als Argument übergeben, z.B. ./updater.sh /opt/zeiterfassung" >&2
    exit 1
  fi

  if [ ${#repos[@]} -gt 1 ]; then
    echo "Gefundene Repositories:"
    i=1
    for r in "${repos[@]}"; do
      echo "  $i) $r"
      i=$((i+1))
    done
    sel=$(prompt "Welches Repo aktualisieren? (Nummer oder 'all')" "all")
    if [ "$sel" = "all" ]; then
      to_update=("${repos[@]}")
    else
      if ! [[ "$sel" =~ ^[0-9]+$ ]] || [ "$sel" -lt 1 ] || [ "$sel" -gt ${#repos[@]} ]; then
        echo "Ungültige Auswahl. Abbruch." >&2
        exit 1
      fi
      to_update=("${repos[$((sel-1))]}")
    fi
  else
    to_update=("${repos[0]}")
  fi

  for repo in "${to_update[@]}"; do
    git_pull_repo "$repo" || true
  done

  echo "Fertig. Prüfe README für Hardware-Details und weitere Anweisungen."
}

main "$@"
