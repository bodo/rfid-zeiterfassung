#!/usr/bin/env bash
# Installer wrapper (copy of install.sh) intended to be fetched via raw.githubusercontent.com
exec bash "$(dirname "$0")/install.sh" "$@"

# When this file is executed from a RAW URL via curl | bash the exec above will
# attempt to run the bundled install.sh if present. If you run this directly
# from the internet (pipe to bash), pass the repo URL as first argument to
# override the default: `bash -s -- https://github.com/owner/repo.git`

# Ensure common helper scripts are executable (install/update)
# This makes it safe when the repo is checked out on systems where execute
# permissions were lost (e.g. on Windows or certain Git extractions).
SCRIPT_DIR="$(dirname "$0")"
for f in "$SCRIPT_DIR"/install.sh "$SCRIPT_DIR"/update.sh ./install.sh ./update.sh; do
	if [ -f "$f" ]; then
		chmod +x "$f" 2>/dev/null || true
	fi
done
