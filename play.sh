#!/bin/bash
# 提督的決斷 II 繁體中文版 — 一鍵啟動（86Box + 繁體中文 Windows 3.1）
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
exec "$HERE/vendor/86box/86Box-4.2.1.AppImage" --vmpath "$HERE/vendor/86box/vm_play" "$@"
