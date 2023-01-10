clear
for FILE in tests/*.lsp; do echo $FILE && python smli.py < $FILE; done

