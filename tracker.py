import os
import requests
import json
import subprocess
import re

with open('config.json') as json_file:
    config = json.load(json_file)

git_username = config['git_username']
git_accesstoken = config['git_accesstoken']
git_assignees = config['git_assignees']
create_issues = True
create_pull_requests = True

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
unused = []

for pyfile in pyfiles:
    pyfilename = pyfile.name.split('/')[len(pyfile.name.split('/')) - 1]
    print('Working with', pyfilename)
    os.chdir(pyfile.name[:pyfile.name.rindex('/')])
    imports = []
    filelines = {}
    found = []

    lines = pyfile.readlines()
    linecount = 0
    for line in lines:
        linecount += 1
        l = line.strip()
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
                    if len(ilist) > 1:
                        inlist = True
                    else:
                        inlist = False
                    filelines[i] = {'import': i, 'line': linecount, 'inlist': inlist}
    linecount = 0
    for line in lines:
        linecount += 1
        l = line.strip()
        if not (l.startswith('#') or l.startswith('from ') or l.startswith('import ')):
            for x in imports:
                if re.search(r"(\W)" + re.escape(x) + r"(\W)", ' ' + str(l) + ' ') != None:
                    if x not in found:
                        found.append(x)
                        del filelines[x]
    for x in imports:
        if x not in found:
            total_found += 1
            print('Could not find', x)
            unused.append({'file': pyfilename, 'import': x})
    
    if create_issues:
        git_repo = subprocess.run(['git', 'config', '--get', 'remote.origin.url'], stdout=subprocess.PIPE, text=True).stdout.strip().replace('.git', '').replace('https://github.com/', '')
        for x in filelines:
            issuetitle = "Unused import " + x + ' in ' + pyfilename
            headers = {'Accept': 'application/vnd.github.v3+json'}
            data = {"title": issuetitle, "body": x + ' is imported in ' + pyfilename + ' but is never used.', "assignees": git_assignees, "labels":["low","bug"]}
            url = "https://api.github.com/repos/" + git_repo + "/issues"
            response = requests.post(url, data = json.dumps(data), headers = headers, auth = (git_username, git_accesstoken))
            print(response)
            issue_num = response.json()['number']
            print('Created issue:', issue_num)

            if create_pull_requests:
                with open(pyfile.name, 'r') as writefile:
                    data = writefile.readlines()
                
                data[filelines[x]['line'] - 1] = '# ' + data[filelines[x]['line'] - 1].strip('\n') + ' ### Edited by python-import-tracker' + '\n'
                ### Todo: Check if import is included in list and only comment out that portion

                with open(pyfile.name, 'w') as writefile:
                    writefile.writelines(data)

                subprocess.run(['git', 'checkout', '-b', 'fix_' + str(issue_num), 'main'])
                subprocess.run(['git', 'add', pyfilename])
                subprocess.run(['git', 'commit', '-S', '-m', '"' + issuetitle + '"'])
                subprocess.run(['git', 'push', 'origin', 'fix_' + str(issue_num)])
                subprocess.run(['git', 'checkout', 'main'])
                subprocess.run(['git', 'pull'])

                data = {"title": issuetitle, "body": 'Fixes #' + str(issue_num), "head": 'fix_' + str(issue_num), "base": 'main'}
                url = "https://api.github.com/repos/" + git_repo + "/pulls"
                response = requests.post(url, data = json.dumps(data), headers = headers, auth = (git_username, git_accesstoken))
                print(response)
                pull_num = response.json()['number']

                data = {"assignees": git_assignees, "labels":["low","bug"]}
                url = "https://api.github.com/repos/" + git_repo + "/issues/" + str(pull_num)
                response = requests.post(url, data = json.dumps(data), headers = headers, auth = (git_username, git_accesstoken))
                print(response)

                print('Created pull request:', pull_num)


print('Done! - Found count:', total_found)