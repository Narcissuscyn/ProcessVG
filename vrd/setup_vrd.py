#!/usr/bin/python


''' Visual genome data analysis and preprocessing.'''

import json
import os
from collections import Counter
import xml.etree.cElementTree as ET
from xml.dom import minidom

dataDir = '/home/new/file/dataset/VRD'
outDir = '/home/new/file/rel_det/ProcessVG-master/data/vrd'

# Set maximum values for number of object / attribute / relation classes,
# filter it further later
max_objects = 100
max_attributes = 50
max_predicates = 70

common_attributes = set(['white', 'black', 'blue', 'green', 'red', 'brown', 'yellow',
                         'small', 'large', 'silver', 'wooden', 'orange', 'gray', 'grey', 'metal', 'pink', 'tall',
                         'long', 'dark'])


def clean_string(string):
    string = string.lower().strip()
    if len(string) >= 1 and string[-1] == '.':
        return string[:-1].strip()
    return string


def clean_objects(string, common_attributes):
    ''' Return object and attribute lists '''
    string = clean_string(string)
    words = string.split()
    if len(words) > 1:
        prefix_words_are_adj = True
        for att in words[:-1]:
            if not att in common_attributes:
                prefix_words_are_adj = False
        if prefix_words_are_adj:
            return words[-1:], words[:-1]
        else:
            return [string], []
    else:
        return [string], []


def clean_attributes(string):
    ''' Return attribute list '''
    string = clean_string(string)
    if string == "black and white":
        return [string]
    else:
        return [word.lower().strip() for word in string.split(" and ")]


def clean_relations(string):
    string = clean_string(string)
    if len(string) > 0:
        return [string]
    else:
        return []


def prettify(elem):
    ''' Return a pretty-printed XML string for the Element '''
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

def get_image_names(json_file):
    with open(json_file, "r") as f:
        data=json.load(f)
    return data.keys()

def get_predicate_id():
    pred_dict = {}
    with open("/home/new/file/dataset/VRD/predicates.json", "r") as f:
        ids = json.load(f)
        for index, obj_id in enumerate(ids):
            pred_dict[index] = obj_id
    return pred_dict

def get_object_id():
    """
    get the correspondence between objects and labels
    :return: id-object dict
    """
    id_dict={}
    with open("/home/new/file/dataset/VRD/objects.json","r") as f:
        ids=json.load(f)
        for index,obj_id in enumerate(ids):
            id_dict[index]=obj_id
    return id_dict
    # object_dict={}
    # keys=data.keys()
    # for key in keys:# one image
    #     obj_cat=[]
    #     obj_lst=[]
    #     file_name=key
    #     relationships=data[key]
    #     for relationship in relationships:
    #         obj=relationship["object"]
    #
    #         if obj["category"] not in obj_cat:
    #             object={}
    #             obj_cat.append(obj["category"])
    #             object["object_id"]=obj["category"]
    #             object["y_min"]=obj["bbox"][0]
    #             object["y_max"]=obj["bbox"][1]
    #             object["x_min"]=obj["bbox"][2]
    #             object["x_max"]=obj["bbox"][3]
    #             object["names"]=id_dict[int(obj["category"])]
    #             obj_lst.append(object)
    #
    #         obj = relationship["subject"]
    #
    #         if obj["category"] not in obj_cat:
    #             object = {}
    #             obj_cat.append(obj["category"])
    #             object["object_id"] = obj["category"]
    #             object["y_min"] = obj["bbox"][0]
    #             object["y_max"] = obj["bbox"][1]
    #             object["x_min"] = obj["bbox"][2]
    #             object["x_max"] = obj["bbox"][3]
    #             object["names"] = id_dict[int(obj["category"])]
    #             obj_lst.append(object)
    #     object_dict[file_name]=obj_lst
    #
    # return object_dict
def build_vocabs_and_xml(json_file):

    objects = Counter()
    attributes = Counter()
    relations = Counter()
    print("loading date...")
    with open(os.path.join(dataDir, json_file)) as f:
        data = json.load(f)
    print("loading date finished")

    obj_dict=get_object_id()
    pred_dict=get_predicate_id()
    # First extract attributes and relations
    for vrd in data:
        for rel in vrd['relationships']:
            relations.update(clean_relations(rel['relationship']))

    # Create full-sized vocabs
    objects = obj_dict.values()
    relations = pred_dict.values()

    with open(os.path.join(outDir, "objects_vocab_%s.txt" % max_objects), "w") as text_file:
        for item in objects:
            text_file.write("%s\n" % item)
    with open(os.path.join(outDir, "relations_vocab_%s.txt" % max_predicates), "w") as text_file:
        for item in relations:
            text_file.write("%s\n" % item)

    out_folder = 'xml'
    if not os.path.exists(os.path.join(outDir, out_folder)):
        os.mkdir(os.path.join(outDir, out_folder))
    for vrd in data:

        ann = ET.Element("annotation")
        ET.SubElement(ann, "folder").text = json_file[:-5]
        ET.SubElement(ann, "filename").text =vrd['filename']

        source = ET.SubElement(ann, "source")
        ET.SubElement(source, "database").text = "vrd dataset"
        ET.SubElement(source, "image_id").text = vrd['filename'][:-4]

        size = ET.SubElement(ann, "size")
        ET.SubElement(size, "width").text = str(vrd["width"])
        ET.SubElement(size, "height").text = str(vrd["height"])
        ET.SubElement(size, "depth").text = "3"

        ET.SubElement(ann, "segmented").text = "0"


        object_set = set()
        for obj in vrd['objects']:
            o, a = clean_objects(obj['names'][0], common_attributes)
            if o[0] in objects:
                ob = ET.SubElement(ann, "object")
                ET.SubElement(ob, "name").text = o[0]
                ET.SubElement(ob, "object_id").text = str(objects.index(o[0]))
                object_set.add(objects.index(o[0]))
                ET.SubElement(ob, "difficult").text = "0"
                bbox = ET.SubElement(ob, "bndbox")
                ET.SubElement(bbox, "xmin").text = str(obj['bbox']['x'])
                ET.SubElement(bbox, "ymin").text = str(obj['bbox']['y'])
                ET.SubElement(bbox, "xmax").text = str(obj['bbox']['x'] + obj['bbox']['w'])
                ET.SubElement(bbox, "ymax").text = str(obj['bbox']['y'] + obj['bbox']['h'])

        for rel in vrd['relationships']:
            predicate = clean_string(rel["relationship"])
            if rel["text"][0] in objects and rel["text"][2] in objects:
                if predicate in relations:
                    re = ET.SubElement(ann, "relation")
                    ET.SubElement(re, "subject_id").text = str(objects.index(rel["text"][0]))
                    ET.SubElement(re, "object_id").text = str(objects.index(rel["text"][2]))
                    ET.SubElement(re, "predicate").text = predicate

        outFile = vrd['filename'][:-4]+".xml"
        tree = ET.ElementTree(ann)
        if len(tree.findall('object')) > 0:
            tree.write(os.path.join(outDir, out_folder, outFile))


if __name__ == "__main__":
    # First, use visual genome library to merge attributes and scene graphs
    # vg.AddAttrsToSceneGraphs(dataDir=dataDir)
    # Next, build xml files
    build_vocabs_and_xml("sg_train_annotations.json")


