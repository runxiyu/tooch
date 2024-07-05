#!/bin/sh
chromium-browser --headless --no-pdf-header-footer --print-to-pdf="$(basename -s .svg "$1").pdf" "$1"
