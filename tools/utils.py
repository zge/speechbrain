# Utilities for format manipulation
#
# Zhenhao Ge, 2022-02-15

import csv

def concat_csv(infiles, outfile, have_header=True, verbose=True):

    if have_header:
        header = open(infiles[0], 'r').readline().rstrip().split(',')
    else:
        header = None
    with open(outfile, 'w', newline='') as f:
        csv_out = csv.writer(f)
        if have_header:
            csv_out.writerow(header)
        for infile in infiles:
            lines = open(infile, 'r').readlines()
            if have_header:
                lines = lines[1:]
            for line in lines:
                row = line.rstrip().split(',')
                csv_out.writerow(row)
    if verbose:
        print('{} saved!'.format(outfile))

def convert_symbol(text, l1, l2, quote='"'):
  """convert symbol l1 to l2 if inside quote"""
  text2 = ''
  inside = False
  for c in text:
    if c == quote:
      inside = not inside
    elif c == l1:
      if inside:
        text2 += l2
      else:
        text2 += l1
    else:
       text2 += c
  return text2

def csv2dict(csvname, delimiter=',', encoding='utf-8'):
    """extract rows in csv file to a dictionary list"""
    lines = open(csvname, 'r', encoding=encoding).readlines()
    header = lines[0].rstrip().split(delimiter)
    lines = lines[1:]
    nlines = len(lines)

    dict_list = [{} for _ in range(nlines)]
    for i, line in enumerate(lines):
        line2 = convert_symbol(line.rstrip(), delimiter, '|')
        items = line2.split(delimiter)
        items = [s.replace('|', delimiter) for s in items]
        dict_list[i] = {k:items[j] for j,k in enumerate(header)}

    return dict_list

def dict2tuple(dct, key='ID'):

    # verify the 2nd-layer keys are the same
    # (i.e., the keys of dict of dict are the same)
    subkeys = [list(dct[k].keys()) for k in dct.keys()]
    result = all(element == subkeys[0] for element in subkeys)
    assert result, 'sub-keys are not the same for sub-dictionaries'

    keys = [key, *subkeys[0]]
    tuple_list = []
    for k in dct.keys():
        elements = [dct[k][kk] for kk in subkeys[0]]
        tuple_list.append((k, *elements))
    return tuple_list, keys

# def tuple2csv(tuples, csvname='filename.csv', colname=[],
#               encoding='utf-8', verbose=True):
#     with open(csvname, 'w', newline='', encoding=encoding) as f:
#         csv_out = csv.writer(f)
#         if len(colname) != 0:
#             header = colname
#             csv_out.writerow(header)
#         for i, tpl in enumerate(tuples):
#             csv_out.writerow(list(tpl))
#     if verbose:
#         print('{} saved!'.format(csvname))

def tuple2csv(tuples, csvname='filename.csv', colname=[], verbose=True):
    with open(csvname, 'w', newline='') as f:
        csv_out = csv.writer(f)
        if len(colname) != 0:
            header = colname
            csv_out.writerow(header)
        for i, tpl in enumerate(tuples):
            csv_out.writerow(list(tpl))
    if verbose:
        print('{} saved!'.format(csvname))
