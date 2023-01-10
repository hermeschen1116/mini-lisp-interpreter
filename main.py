file_buffer: list = []

while True:
	try:
		line = str(input())
		if line == '\n' or line == '':
			break
		file_buffer.append(line.strip().strip(' '))
	except EOFError:
		break

print(file_buffer)
