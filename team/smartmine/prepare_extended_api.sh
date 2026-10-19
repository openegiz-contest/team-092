#!/usr/bin/env bash
set -e

cd "$(dirname "$0")/../.."

REPO="https://github.com/ertis-research/extended-api-for-eclipse-ditto.git"
COMMIT="b49663dea326854a2323423eaeab7e7f54d325a7"
TARGET="team/extended-api"

if [ ! -f "$TARGET/package.json" ]; then
    echo "Downloading Extended API..."
    git clone "$REPO" "$TARGET"
    git -C "$TARGET" checkout "$COMMIT"
fi

echo "Extended API source is ready."
