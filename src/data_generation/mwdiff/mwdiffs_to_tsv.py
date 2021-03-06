import glob
import bz2
from pprint import pprint
import json
import os
import csv
import multiprocessing as mp
import time
import argparse

"""
on stat1003:

source ~/env/source 3.4/bin/activate

nice python ~/mwdiffs_to_tsv.py \
--path_glob /srv/ellery/talk_diffs/enwiki-20160113-pages-meta-history\*.bz2  \
--output_dir /srv/public-datasets/enwiki/user_talk_diffs

"""

def clean(s):
    s = s.replace('\t', 'TAB')
    s = s.replace('\n', 'NEWLINE')
    s = s.replace("'", 'SQ ')
    s = s.replace("""""", 'DQ ')
    return s

def get_features(obj):
    f = {}
    if 'comment' in obj:
        f['rev_comment'] = clean(obj['comment'])
        
    f['insert_only'] = 1
    if 'diff' in obj:
        if 'ops' in obj['diff']:
            for e in obj['diff']['ops']:
                if e['name'] == 'insert':
                    if 'tokens' in e:
                        insertion = ''.join(e['tokens'])
                        if len(insertion) > 0:
                            f['insertion'] = clean(insertion)
                else:
                    f['insert_only'] = 0
    if 'id' in obj:
        f['rev_id'] = obj['id']
        
    if 'page' in obj:
        if 'id' in obj['page']:
            f['page_id'] = obj['page']['id']
        if 'title' in obj['page']:
            f['page_title'] = clean(obj['page']['title'])
            
    if 'timestamp' in obj:
        f['rev_timestamp'] = obj['timestamp']
        
        
    if 'user' in obj:
        if 'id' in obj['user']:
            f['user_id'] = obj['user']['id']
        if 'text' in obj['user']:
            f['user_text'] = clean(obj['user']['text'])
    return f




if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--path_glob', required=True,
        help='path glob'
    )

    parser.add_argument(
        '--output_dir', required=True,
        help='rrequired=True '
    )

    args, unknown = parser.parse_known_args()
    print (args)

    output_dir = args.output_dir
    files = glob.glob(args.path_glob)
    print(files)

    def convert(infile):
        print('Working on %s ...' % infile)
        outfile = os.path.join(output_dir, infile.split('/')[-1].replace('bz2', 'tsv.bz2'))
        with bz2.open(infile, 'rt') as fin, bz2.open(outfile, 'wt') as fout:
            fieldnames = ['rev_comment', 'insertion', 'insert_only', 'rev_id', 'page_id', 'page_title', 'rev_timestamp', 'user_id', 'user_text']
            writer = csv.DictWriter(fout, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            for line in fin:
                obj = json.loads(line)
                f = get_features(obj)
                writer.writerow(f)
    

    
    
    p = mp.Pool(mp.cpu_count())
    p.map(convert, files)






