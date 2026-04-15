import os, re
root = r'd:\git\autohub\frontend\app'
pattern = re.compile(r'\["[^"]+"\]\s*(>|<|>=|<=|==)\s*\d')
for dirpath, dirs, files in os.walk(root):
    for fn in files:
        if fn.endswith('.py'):
            p = os.path.join(dirpath, fn)
            with open(p, encoding='utf-8') as f:
                lines = f.readlines()
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    print(f'{fn}:{i}: {line.rstrip()}')
