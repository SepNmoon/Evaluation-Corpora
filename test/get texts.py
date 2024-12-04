# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:16:08 2024

@author: 87142
"""
import csv
import os


def read_file(file_path):
    data = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        tsv_reader = csv.reader(file, delimiter='\t')
        index=0
        for row in tsv_reader:
            if index>0:
                data.append(row)
            index+=1
    return data

def iob_to_text(iob_lines): 
    data = []
    sentence = []
    entities = []
    current_entity = None
    start = 0
    
    for line in iob_lines:
        word, label = line.strip().split()
        sentence.append(word)
        
        word_start = start
        word_end = start + len(word)
        
        if label.startswith("B-"):  # 处理实体的开始
            if current_entity:
                entities.append((current_entity[0], current_entity[1], current_entity[2]))
            current_entity = [word_start, word_end, label[2:]]
        
        elif label.startswith("I-") and current_entity:  # 处理实体的内部
            current_entity[1] = word_end
        elif label == "O":  # 处理非实体
            if current_entity:
                entities.append((current_entity[0], current_entity[1], current_entity[2]))
                current_entity = None
        start = word_end + 1  # 下一个单词的开始位置
        
    if current_entity:
        entities.append((current_entity[0], current_entity[1], current_entity[2]))
        
    if sentence:
        data.append((" ".join(sentence), {"entities": entities}))

    return data

def write_file(selection):
    if selection=='HIPE':
        file='..\HIPE2020\HIPE2020_normalized.tsv'
        tsv_data=read_file(file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_text(iob_data)
        text=test_data[0][0]
        with open('.\geoparser\HIPE\HIPE.txt','w') as f:
            f.write(text)
    elif selection=='MH':
        path='..\MH\MH_normalized'
        files= os.listdir(path)
        for file in files[0:1589]:
            print(file)
            tsv_data=read_file('..\MH\MH_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)
            text=test_data[0][0]
            file_name=file[:-4]
            with open('.\geoparser\MH\%s.txt'%file_name,'w') as f:
                f.write(text)
        

if __name__ == "__main__": 
    write_file('MH')