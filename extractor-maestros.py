import sys
import os.path
import re
import json

from pprint import PrettyPrinter
from urllib.request import Request, urlopen

def getUrl(url):
    request = Request(url, headers={'User-Agent': 'Mozilla/5.0'}) 
    return urlopen(request).read().decode('utf-8')

def getMaestro(data):
    
    regex_template = r'n_r[\S\s]+<h1>\s*(\w+[\s\w\.]*)'
    regex = regex_template
    match = re.search(regex, data)
     
    if not match: return None
    
    name = match.groups()[0]
    
    offsets = [
        ['ex_li', 'explicacion' ], 
        ['ac_li', 'accesible' ], 
        ['pa_li', 'pasable' ],
        ['as_li', 'asistencia' ], 
        ['se_li', 'sexy' ]
    ]

    regex_template = r'<li\s+id="{}">\s*(\d+(?:\.\d+)?)'

    scores = {}

    for offt in offsets:
        regex = regex_template.format(offt[0])
        match = re.search(regex, data)
        if not match: return None
        
        scores[offt[1]] = float(match.groups()[0])
     
    offsets = [ ['Chido', 'up'], ['Gacho', 'down']]

    regex_template = r'{}:\s*<span>\s*(\d+)'

    votes = {}

    for offt in offsets:
        regex = regex_template.format(offt[0])
        match = re.search(regex, data)
        if not match: return None
        
        votes[offt[1]] = int(match.groups()[0])

    maestro = { 'name' : name, 'scores' : scores, 'votes' : votes }
    
    return maestro

def main():
    argc = len(sys.argv) 
    if argc < 2 or argc > 4:
        print('usage:', sys.argv[0], 'output_file [begin_range] [end_range]')
        exit(1)

    rng = [1, sys.maxsize]
    tolerance = 10
    
    if argc > 2:
        for i in range(2, argc):
            try: rng[i - 2] = int(sys.argv[i])
            except: 
                print('[info] invalid range')
                exit(1)

    if rng[0] > rng[1] or rng[0] < 1 or rng[1] < 1:
        print('[error] invalid range')
        exit(1)
    
    pp = PrettyPrinter(indent = 4)

    maestros = []
    urlBase = 'http://www.listademaestros.com/fime/maestro/'

    tolCount = 0
    for i in range(rng[0], rng[1] + 1):
        try:
            if tolCount == tolerance: break
            url = urlBase + str(i)
            print('[info] getting {}\n'.format(url)) 
            maestro = getMaestro(getUrl(url))
            if maestro:
                maestro["id"] = i
                maestros.append(maestro)
                tolCount = 0
            else: 
                tolCount = tolCount + 1
            pp.pprint(maestro)
            print('\n[info] done {} ({},{})'.format(url, i, rng[1]))
            print('[info] tolerance(max {}): {}\n'.format(tolerance, tolCount))
        except KeyboardInterrupt: 
            print('\n[info] user cancelled extraction process')
            break
        except Exception as e:
            tolCount = tolCount + 1 
            print('[error]', e) 
            print('[info] tolerance(max {}): {}\n'.format(tolerance, tolCount))
            continue
    if maestros:
        with open(sys.argv[1]+'.json', 'w') as f:
            json.dump(maestros, f)
            print('[info] writing to file: {}'.format(sys.argv[1]+'.json'))
    else: exit(1)

if __name__ == '__main__':
    main()
