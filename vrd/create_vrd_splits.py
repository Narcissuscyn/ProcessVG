#generate:.jpg .xml


# !/usr/bin/python


''' Determine visual genome data splits to avoid contamination of COCO splits.'''

import argparse
import os
import random
import json
random.seed(10)  # Make dataset splits repeatable

CURDIR = os.path.dirname(os.path.realpath(__file__))

# The root directory which holds all information of the dataset.
splitDir = 'data/vrd'
dataDir = '/home/new/file/dataset/VRD'

train_list_file = "{}/vrd_train.txt".format(CURDIR)
val_list_file = "{}/vrd_val.txt".format(CURDIR)



def get_file(json_file,dst_file):


    f=open(dst_file,"w+")
    with open(os.path.join(dataDir,json_file), 'r') as fj:
        graph = json.load(fj)

    for item in graph:

        image_name=item["filename"]
        f.write(json_file[:-4]+"/""+image_name+" xml/"+image_name[:-4]+".xml\n")

    f.close()
    print("finished")

get_file("sg_test_annotations.json",val_list_file)
get_file("sg_train_annotations.json",train_list_file)