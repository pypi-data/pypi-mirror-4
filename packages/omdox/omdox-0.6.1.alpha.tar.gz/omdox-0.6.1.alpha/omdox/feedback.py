HEADER = '\033[40;93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
RED = '\033[40;91m'
ENDC = '\033[0m'

errors = []

def info(msg, indent=True):
    if indent:
        indent = '  '
    else:
        indent = ''
    print indent + BLUE + ' ' + msg + ' ' + ENDC

def header(msg, indent=True):
    if indent:
        indent = '  '
    else:
        indent = ''
    print indent + HEADER + ' ' + msg + ' ' + ENDC

def error(msg, indent=True):
    if indent:
        indent = '  '
    else:
        indent = ''
    print indent + RED + ' ' + msg + ' ' + ENDC

def success(msg, indent=True):
    if indent:
        indent = '  '
    else:
        indent = ''
    print indent + GREEN + ' ' + msg + ' ' + ENDC
