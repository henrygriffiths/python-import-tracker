filedir = str(input('Enter path of python file: '))
pyfile = open(filedir, 'r')
imports = []
found = []

for line in pyfile:
    l = line.strip().lower()
    if not l.startswith('#'):
        if l.startswith('from '):
            l = l[l.index(' import ') + 1:]
        if l.startswith('import '):
            i = l.replace('import ', '').split(' ')[0].split('#')[0].strip()
            while '.' in i:
                i = i.split('.')[1]
            imports.append(i)

pyfile.seek(0)

for line in pyfile:
    l = line.strip().lower()
    if not (l.startswith('#') or l.startswith('from ') or l.startswith('import ')):
        for x in imports:
            if x + '.' in l or ' ' + x + "(" in l:
                if x not in found:
                    found.append(x)

for x in imports:
    if x not in found:
        print('Could not find', x)

print('Done!')