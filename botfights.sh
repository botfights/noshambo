#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> noshambo

python noshambo.py tournament --catch-exceptions=on --log-level=10 $@
