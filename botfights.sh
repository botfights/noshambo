#!/bin/bash

# botfights.sh -- wrapper for botfights.io <=> noshambo

python noshambo.py tournament --log-level=10 $@
