#!/usr/bin/zsh
clear
for FILE in tests/0*.lsp; do echo $FILE && python smli.py < $FILE; done
