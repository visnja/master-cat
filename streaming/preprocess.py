

def transform(line):
    if line in ['',"\n"] or line.startswith("By") or 'MIN READ' in line or '(Reuters)' in line:
        return None
    return line