### =============== ###
### AUTHOR: sheinxy ###
### =============== ###

# Disclaimer: This script was made with simplicity in mind. Hence it doesn't use anything "fancy"
#             This script is only aimed at being usable.
#             You may reuse it and improve it in any way you want (for example using a real logger library)

import requests
import sys

## ================= ##
## Utility functions ##
## ================= ##

def list_find(l, val):
    """
        Finds the index of a value in a list, return -1 if not found
        @param l  : List to find the value in
        @param val: The value to find
        @return     The index or -1 if not found
    """
    try:
        return l.index(val)
    except:
        return -1

def get_args():
    """
        Get the command line arguments
        @return mod_id, logs, sort, data, file arguments
    """
    mod_id   = int(sys.argv[1])
    logs     = list_find(sys.argv, '--logs') > 0
    sort_idx = list_find(sys.argv, '--sort')
    sort     = sys.argv[sort_idx + 1] if sort_idx > 0 and sort_idx + 1 < len(sys.argv) else 'download_count'
    data_idx = list_find(sys.argv, '--data')
    data     = sys.argv[data_idx + 1].split(',') if data_idx > 0 and data_idx + 1 < len(sys.argv) else ['name', 'download_count', 'url']
    file_idx = list_find(sys.argv, '--file')
    file     = sys.argv[file_idx + 1]if file_idx > 0 and file_idx + 1 < len(sys.argv) else None
    sep_idx = list_find(sys.argv, '--sep')
    sep     = sys.argv[sep_idx + 1]if sep_idx > 0 and sep_idx + 1 < len(sys.argv) else ';'

    return mod_id, logs, sort, data, file, sep

def log(function, msg, logs=True):
    """
        Simple logger
        @param function: The function from which the logger was called
        @param msg     : The logging message
        @param logs    : Enable or disable logs (default is True)
    """
    if logs:
        print(f'[LOG][{function}] {msg}', file=sys.stderr)

## ================= ##
## Modpack functions ##
## ================= ##

def get_modpacks(mod_id, sort='download_count', logs=False):
    """
        Get all the modpacks for a mod
        @param mod_id: The id of the mod
        @param sort  : The key to sort by     (default is download_count)
        @param logs  : Enable or disable logs (default is False)
        @return        The list of modpacks
    """
    log('get_modpacks', f'Getting modpacks for mod with id {mod_id}', logs)
    URL  = f'https://www.modpackindex.com/api/v1/mod/{mod_id}/modpacks?limit=100&page='
    res  = []
    page = 1
    while len(data := requests.get(f'{URL}{page}').json().get('data')) > 0:
        log('get_modpacks', f'Got page {page}: {len(data)} results', logs)
        res  += data
        page += 1
    log('get_modpacks', f'All modpacks have been found: {len(res)} entries', logs)
    if sort:
        log('get_modpacks', f'Sorting result by {sort}', logs)
        res.sort(key=lambda e: e[sort], reverse=True)
    return res

def modpacks_to_csv(modpacks, separator=';', data=['name', 'download_count', 'url'], logs=False):
    """
        Converts a list of modpacks into csv
        @param modpacks : The list to convert
        @param separator: The comma separator           (default is ';')
        @param data     : The attribute for each column (default is ['name', 'download_count', 'url'])
        @return           The csv string
    """
    log('modpacks_to_csv', f'Converting to CSV with {data}, using {separator} as a separator', logs)
    res  = separator.join(data)
    res += '\n'
    for mod in modpacks:
        res += separator.join(str(mod[attribute]).replace(separator, ' ' if separator != ' ' else '\t') for attribute in data)
        res += '\n'
    return res

def csv_to_file(csv, file=None, logs=False):
    """
        Writs csv to a file
        @param csv : The csv string to write
        @param file: The file to write to, or None to write to stdout (default is None)
        @param logs: Enable or disable logs                           (default is False)
    """
    log('csv_to_file', f'Writing csv to {file if file else "stdout"}', logs)
    if not file:
        print(csv)
    else:
        with open(file, 'w') as f:
            f.write(csv)

## ========== ##
## Entrypoint ##
## ========== ##

if __name__ == '__main__':
    if len(sys.argv) == 1 or list_find(sys.argv, '-h') > 0 or list_find(sys.argv, '--help') > 0:
        print(f'Usage:\n{sys.argv[0]} mod_id [--logs] [--sort attribute] [--data attributes] [--file filename] [--sep separator]', file=sys.stderr)
        print('\nmod_id: the id of the mod', file=sys.stderr)
        print('--logs: if this option is enabled, logs will be printed to stderr', file=sys.stderr)
        print('--sort attribute: the attribute to sort by, defaults to download_count (sorting is done in increasing order)', file=sys.stderr)
        print('--data attributes: the data to put inside the csv, defaults to "name,download_count,url" (attributes is a comma separated value, eg: "name,id")', file=sys.stderr)
        print('--file filename: the file to write to, if this argument is not provided the csv will be printed to stdout', file=sys.stderr)
        print('--sep separator: the separator to use in the csv file, defaults to ;', file=sys.stderr)
        exit(0)
    
    if not all('0' <= c <= '9' for c in sys.argv[1]):
        print('mod_id is not an int', file=sys.stderr)
        exit(1)
        
    mod_id, logs, sort, data, file, sep = get_args()
    
    modpacks = get_modpacks(mod_id, sort, logs)
    csv      = modpacks_to_csv(modpacks, sep, data, logs)
    csv_to_file(csv, file, logs)
