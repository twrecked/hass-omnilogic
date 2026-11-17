#!/usr/bin/env bash
set -euo pipefail

# Path to local home-assistant clone
HA_CORE_PATH="${1:-${HA_CORE_PATH:-$HOME/src/3rdparty/home-assistant}}"
HA_COMPONENT_PATH="${HA_CORE_PATH}/homeassistant/components/omnilogic"

# Verify HA component path exists
if [ ! -d "${HA_COMPONENT_PATH}" ]; then
  echo "Error: OmniLogic component not found at: ${HA_COMPONENT_PATH}"
  echo "Usage: $0 [path-to-home-assistant-core]"
  exit 1
fi

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${REPO_ROOT}"

# Ensure working tree is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: Working tree is not clean. Commit or stash changes before syncing."
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

# Get HA core commit metadata
HA_COMMIT="$(git -C "${HA_CORE_PATH}" rev-parse --short HEAD)"
HA_DATE="$(git -C "${HA_CORE_PATH}" log -1 --format="%ci")"
HA_SUBJECT="$(git -C "${HA_CORE_PATH}" log -1 --format="%s")"

echo "==> Syncing OmniLogic from Home Assistant core"
echo "    Core path: ${HA_CORE_PATH}"
echo "    Core commit: ${HA_COMMIT} (${HA_DATE})"
echo "    Message: ${HA_SUBJECT}"

# Switch to upstream branch
git checkout upstream

# Clean and update custom_components/omnilogic
DEST_DIR="${REPO_ROOT}/custom_components/omnilogic"
rm -rf "${DEST_DIR}"
mkdir -p "${DEST_DIR}"
cp -R "${HA_COMPONENT_PATH}/." "${DEST_DIR}/"

# Stage changes
git add custom_components/omnilogic

if git diff --cached --quiet; then
  echo "==> Upstream is already up to date with core @ ${HA_COMMIT}."
else
  git commit -m "Sync upstream omnilogic from home-assistant/core @ ${HA_COMMIT}

Source: homeassistant/components/omnilogic
Commit: ${HA_COMMIT}
Date: ${HA_DATE}
Subject: ${HA_SUBJECT}"
  echo "==> Successfully updated 'upstream' branch to ${HA_COMMIT}."
fi

# Return to original branch
git checkout "${CURRENT_BRANCH}"

echo ""
echo "==> Sync complete!"
echo "To bring upstream changes into '${CURRENT_BRANCH}', run:"
echo "    git merge upstream"
