def read_ms_works_file(file):
    text = []
    started = False
    with open(file, 'rb') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.endswith('\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\n'):
                started = True
                continue
            #elif line.strip().startswith('\x00')  and started: break
            #elif line.
            if started:
                if line.strip().startswith('\x00') or line.strip().endswith('\x00'): break
                text.append(line)
    return text[2:]
