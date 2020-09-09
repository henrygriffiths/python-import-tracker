import os

filedir = str(input('Enter path of python file or directory of python files: '))
if filedir.endswith('.py'):
    pyfiles = [open(filedir, 'r')]
else:
    pyfiles = []
    for f in os.listdir(filedir):
        if os.path.isfile(os.path.join(filedir, f)):
            if '.py' in f:
                pyfiles.append(open(os.path.join(filedir, f)))

total_found = 0

for pyfile in pyfiles:
    print('Working with', pyfile.name)
    imports = []
    found = []

    for line in pyfile:
        l = line.strip().lower()
        if not l.startswith('#'):
            l = l.split('#')[0].strip()
            if l.startswith('from ') and 'import ' in l:
                l = l[l.index(' import ') + 1:]
            if ' as ' in l and 'import ' in l:
                l = 'import ' + l[l.index(' as ') + 4:]
            if l.startswith('import '):
                ilist = l.replace('import ', '').replace('(', '').replace(')','').split(',')
                for i in ilist:
                    i = i.strip()
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
            total_found += 1
            print('Could not find', x)

print('Done! - Found count:', total_found)