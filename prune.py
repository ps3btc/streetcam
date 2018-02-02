#!/usr/bin/python
import json
import sys
import argparse
from os import listdir
from os.path import isfile, join
from pprint import pprint
from collections import namedtuple

def strip_low_confidence(oa):
    a = []
    for item in oa:
        if item['confidence'] > 0.4:
            a.append(item)
    return a

def isSame(oa, ob):
    # Same number of labels before stripping?
    if len(oa) != len(ob):
        return False

    # Strip out all labels that are low confidence
    a = strip_low_confidence(oa)
    b = strip_low_confidence(ob)

    # Same number of labels still?
    if len(a) != len(b):
        return False

    # Do they have the same set of labels?
    labels = set()
    a_dict = {}
    for aa in a:
        l = aa['label']
        labels.add(l)
        if l in a_dict:
            a_dict[l]+=1
        else:
            a_dict[l]=0

    b_dict = {}
    for bb in b:
        l = bb['label']
        if bb['label'] not in labels:
            return False
        if l in b_dict:
            b_dict[l]+=1
        else:
            b_dict[l]=0

    # Do they have the same distribution of labels?
    for l in a_dict:
        if l not in b_dict:
            return False
        if a_dict[l] != b_dict[l]:
            return False

    same = 0
    for aa in a:
        for bb in b:
            if aa['label'] != bb['label']:
                continue
            if abs(aa['confidence'] - bb['confidence']) > 0.02:
                continue
            if abs(aa['bottomright']['x'] - bb['bottomright']['x']) > 20:
                continue
            if abs(aa['bottomright']['y'] - bb['bottomright']['y']) > 20:
                continue
            if abs(aa['topleft']['x'] - bb['topleft']['x']) > 20:
                continue
            if abs(aa['topleft']['y'] - bb['topleft']['y']) > 20:
                continue
            same += 1
            break

    return (same == len(a))

def print_html(file_list, dir_img_fname, dir_json):
    print('<html>')
    print('<table><tr>')
    dir_json_fname=join(dir_img_fname, dir_json)
    row = 0

    for ff in file_list:
        json_file = ff['file']
        status = ff['status']
        if status == 'skip':
            continue
        json_path = join(dir_json_fname,json_file)
        jpg = join(dir_img_fname, json_file.replace('out/', '').replace('json', 'jpg'))
        print('<td>')
        print('<a href="'+json_path+'">')
        print('<img height="120" width="160" src="' + jpg + '">')
        print('</a>') # + status)
        print('</td>')
        row += 1
        if row % 5 == 0:
            print('</tr><tr>')
    print('</tr></table></html>')

def load_files(dir_img_fname, dir_json):
    dir_json_fname=join(dir_img_fname, dir_json)
    onlyfiles = [f for f in listdir(dir_json_fname) if isfile(join(dir_json_fname, f))]
    skip = set()

    for a_json_file in onlyfiles:
        with open(join(dir_json_fname,a_json_file)) as a_data_file:
            a = json.load(a_data_file)
        if a_json_file in skip: continue
        for b_json_file in onlyfiles:
            if b_json_file in skip: continue
            if a_json_file == b_json_file:
                continue
            with open(join(dir_json_fname,b_json_file)) as b_data_file:
                b = json.load(b_data_file)
                if isSame(a, b):
                    #if '20180131-131044' in a_json_file or '20180131-131044' in b_json_file:
                    #    print '** SKIPPING **', a_json_file, ' ', b_json_file, ' ', json.dumps(a, indent=4, sort_keys=True), json.dumps(b, indent=4, sort_keys=True)
                    skip.add(a_json_file)
                    continue

    ff_list = []
    for ff in onlyfiles:
        if ff in skip:
            ff_list.append({'file': ff, 'status': 'skip'})
        else:
            ff_list.append({'file': ff, 'status': 'keep'})
    print_html(ff_list, dir_img_fname, dir_json)

def main(argv):
  load_files("/Users/hareesh/pi/picam", "out")

if __name__ == "__main__":
    main(sys.argv)
