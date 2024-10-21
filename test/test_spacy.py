# -*- coding: utf-8 -*-
"""
Created on Sun Oct  6 15:08:29 2024

@author: liulu
"""

import pandas as pd
import csv
import spacy
from nervaluate import Evaluator
import os

#读取文件，并将tsv文件格式转成iob格式
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


#将iob格式变成spacy能处理的格式
def iob_to_spacy_format(iob_lines):
    data = []
    sentence = []
    entities = []
    current_entity = None
    start = 0
    
    for line in iob_lines:
        if line.strip() == "":  # 如果是空行，表示句子结束
            if sentence:
                data.append((" ".join(sentence), {"entities": entities}))
            sentence = []
            entities = []
            current_entity = None
            start = 0
            continue
        # print(line)
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
        
        # 添加最后一个句子
    if sentence:
        data.append((" ".join(sentence), {"entities": entities}))
    
    return data
    
def spacy_predict(test_data):
    for text, annotations in test_data:
        doc = nlp(text)
        #print("Entities in '%s':" % doc)
        
        true_entities = annotations['entities']
        #print(true_entities)
        
        pred_entities=[]
        for ent in doc.ents:
            #print(ent.text, ent.label_)
            if ent.label_=='PERSON':
                #print(ent.text)
                temp=[]
                temp.append(ent.start_char)
                temp.append(ent.end_char)
                temp.append(ent.label_)
                pred_entities.append(temp)
            elif ent.label_=='GPE':
                temp=[]
                temp.append(ent.start_char)
                temp.append(ent.end_char)
                temp.append(ent.label_)
                pred_entities.append(temp)
        #print(pred_entities)
        
        return true_entities, pred_entities, doc


def score(mode):
    if mode=='strict':
        per_precision=all_per_correct/all_per_retrive
        per_recall=all_per_correct/all_per_relevant        
        place_precision=all_place_correct/all_place_retrive
        place_recall=all_place_correct/all_place_retrive 
        #print(all_per_correct,all_per_retrive)
    elif mode=='type':
        per_precision=(all_per_correct+0.5*all_per_partial)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial)/all_place_relevant
        #print(all_per_correct,all_per_partial,all_per_retrive)
    elif mode=='partial':
        per_precision=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_relevant
        #print(all_per_correct,all_per_partial_type,all_per_retrive)
       
    per_f=(2*per_precision*per_recall)/(per_precision+per_recall)
    place_f=(2*place_precision*place_recall)/(place_precision+place_recall)    
    
    return per_precision,per_recall,per_f,place_precision,place_recall,place_f


def strict(true_entities, pred_entities):
    #print(true_entities)
    #print(pred_entities)
    per_correct=[]
    per_incorrect=[]
    place_correct=[]
    place_incorrect=[]

    for te in true_entities:
        for pe in  pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):
                if (te[2]=='pers' and pe[2]=='PERSON') or (te[2]=='pers' and pe[2]=='GPE'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif (te[2]=='place' and pe[2]=='GPE') or (te[2]=='place' and pe[2]=='PERSON'):
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break 
    
    #将人名地名分开    
    per_true_entities=[]
    place_true_entities=[]
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='GPE':
            place_pred_entities.append(entity)            
    
    per_miss= per_true_entities.copy()       
    for entity in per_correct:            
            per_miss.remove(entity[0])            
    for entity in per_incorrect:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    
    
    
    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        per_spurius.remove(entity[1])
    for entity in per_incorrect:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    #去掉一些将地名误以为成人名的才是无中生有
    for entity in place_incorrect:
        if entity[1][2]=='PERSON':
            try:
                per_spurius.remove(entity[1])
            except ValueError:
                pass
    
    
    

    place_miss= place_true_entities.copy()       
    for entity in place_correct:            
            place_miss.remove(entity[0])            
    for entity in place_incorrect:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
   
    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
        place_spurius.remove(entity[1])
    for entity in place_incorrect:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    #去掉将人名误以为成地名的
    for entity in per_incorrect:
        if entity[1][2]=='GPE':
            try:
                place_spurius.remove(entity[1])
            except ValueError:
                pass
    
    
    per_correct=len(per_correct)
    per_incorrect=len(per_incorrect)
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
    per_partial=0
    
    place_correct=len(place_correct)
    place_incorrect=len(place_incorrect)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    place_partial=0
    
    
    global all_per_correct,all_per_incorrect,all_per_partial,all_per_miss,all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial=all_per_partial+per_partial
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct,all_place_incorrect,all_place_partial,all_place_miss,all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial=all_place_partial+place_partial
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1
    
    
    
    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif pe[2]=='GPE':
            place_retrive+=1
    
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
    

    
def type_match(true_entities, pred_entities):
    per_correct=[]
    per_incorrect=[]
    per_partial=[]
    place_correct=[]
    place_incorrect=[]
    place_partial=[]
    
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):  
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
                
    #将人名，地名分开
    per_true_entities=[]
    place_true_entities=[]
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='GPE':
            place_pred_entities.append(entity)
               
    per_miss= per_true_entities.copy()       
    for entity in per_correct:
        try:           
            per_miss.remove(entity[0])    
        except ValueError:
            pass
    for entity in per_incorrect:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in per_partial:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass


    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_partial:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
                
    #place incorrect只有一种情况，即本来是地名却误测成了人名，于是显示在pred里是人名的形式
    for entity in place_incorrect:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    
    
    place_miss= place_true_entities.copy()       
    for entity in place_correct:
        try:            
            place_miss.remove(entity[0])
        except ValueError:
            pass
            
    for entity in place_incorrect:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
        
    for entity in place_partial:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
    
    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in place_partial:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_incorrect:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    
    per_correct=len(per_correct)
    per_incorrect=len(per_incorrect)
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
    per_partial=len(per_partial)
        
    place_correct=len(place_correct)
    place_incorrect=len(place_incorrect)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    place_partial=len(place_partial)
    
    global all_per_correct
    global all_per_incorrect
    global all_per_partial
    global all_per_miss
    global all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial=all_per_partial+per_partial
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct
    global all_place_incorrect
    global all_place_partial
    global all_place_miss
    global all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial=all_place_partial+place_partial
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1

    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif pe[2]=='GPE':
            place_retrive+=1
    
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
    


def partial_match(true_entities, pred_entities):
    
    per_correct=[]
    per_partial_type=[]
    per_partial_weak=[]
    place_correct=[]
    place_partial_type=[]
    place_partial_weak=[]
    
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:                
                if te[2]=='pers' and pe[2]=='PERSON':
                    #范围对，类型对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='GPE':
                    #范围对，类型不对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)                   
                elif te[2]=='place' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]): 
                if te[2]=='pers' and pe[2]=='PERSON':
                    #范围重合，类型对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_type.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='GPE':
                    #范围重合，类型不对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)
                elif te[2]=='place' and pe[2]=='GPE':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_type.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
                    break
      
    #将人名，地名分开
    per_true_entities=[]
    place_true_entities=[]
    for entity in true_entities:
        if entity[2]=='pers':
            per_true_entities.append(entity)
        elif entity[2]=='place':
            place_true_entities.append(entity)
    
    per_pred_entities=[]
    place_pred_entities=[]
    for entity in pred_entities:
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='GPE':
            place_pred_entities.append(entity)
    
    per_miss= per_true_entities.copy()      
    for entity in per_correct:
        try:           
            per_miss.remove(entity[0])    
        except ValueError:
            pass
    for entity in per_partial_type:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in per_partial_weak:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
        
    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in per_partial_type:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass    
    for entity in place_partial_weak:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass        
   

    place_miss= place_true_entities.copy()       
    for entity in place_correct:
        try:            
            place_miss.remove(entity[0])
        except ValueError:
            pass            
    for entity in place_partial_type:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
    for entity in place_partial_weak:
        try:
            place_miss.remove(entity[0])
        except ValueError:
            pass
        

    place_spurius=place_pred_entities.copy()
    for entity in place_correct:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in place_partial_type:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass
    for enity in per_partial_weak:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass

    
    per_correct=len(per_correct)
    per_incorrect=0
    per_partial_type=len(per_partial_type)
    per_partial_weak=len(per_partial_weak)    
    per_miss=len(per_miss)
    per_spurius=len(per_spurius)
      
    
    place_correct=len(place_correct)
    place_incorrect=0   
    place_partial_type=len(place_partial_type)
    place_partial_weak=len(place_partial_weak)
    place_miss=len(place_miss)
    place_spurius=len(place_spurius)
    
    global all_per_correct
    global all_per_incorrect
    global all_per_partial_type
    global all_per_partial_weak
    global all_per_miss
    global all_per_spurius
    
    all_per_correct=all_per_correct+per_correct
    all_per_incorrect=all_per_incorrect+per_incorrect
    all_per_partial_type=all_per_partial_type+per_partial_type
    all_per_partial_weak=all_per_partial_weak+per_partial_weak
    all_per_miss=all_per_miss+per_miss
    all_per_spurius=all_per_spurius+per_spurius
    
    global all_place_correct
    global all_place_incorrect
    global all_place_partial_type
    global all_place_partial_weak
    global all_place_miss
    global all_place_spurius
    
    all_place_correct=all_place_correct+place_correct
    all_place_incorrect=all_place_incorrect+place_incorrect
    all_place_partial_type=all_place_partial_type+place_partial_type
    all_place_partial_weak=all_place_partial_weak+place_partial_weak
    all_place_miss=all_place_miss+place_miss
    all_place_spurius=all_place_spurius+place_spurius
    
    global all_per_relevant,all_per_retrive,all_place_relevant,all_place_retrive
    per_relevant=0
    per_retrive=0
    place_relevant=0
    place_retrive=0
    for te in true_entities:
        if te[2]=='pers':
            per_relevant+=1
        elif te[2]=='place':
            place_relevant+=1

    all_per_relevant=all_per_relevant+per_relevant
    all_place_relevant=all_place_relevant+place_relevant
    
    for pe in pred_entities:
        if pe[2]=='PERSON':
            per_retrive+=1
        elif pe[2]=='GPE':
            place_retrive+=1
    
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
    
    

def data_display(true_entities, pred_entities,test_data):
    #print(true_entities, pred_entities)

    combine_entities=[]    
    correct_true=[]
    correct_pred=[]
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:   
                correct_true.append(te)
                correct_pred.append(pe)
                temp1=[]
                temp1.append(te[0])
                temp1.append(te[1])
                temp1.append(test_data[0][0][te[0]:te[1]])
                temp1.append(te[2])
                temp2=[]
                temp2.append(pe[0])
                temp2.append(pe[1])
                temp2.append(test_data[0][0][pe[0]:pe[1]])
                temp2.append(pe[2])
                temp=[]
                temp.append(temp1)
                temp.append(temp2)
                combine_entities.append(temp)
                break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):   
                correct_true.append(te)
                correct_pred.append(pe)
                temp1=[]
                temp1.append(te[0])
                temp1.append(te[1])
                temp1.append(test_data[0][0][te[0]:te[1]])
                temp1.append(te[2])
                temp2=[]
                temp2.append(pe[0])
                temp2.append(pe[1])
                temp2.append(test_data[0][0][pe[0]:pe[1]])
                temp2.append(pe[2])
                temp=[]
                temp.append(temp1)
                temp.append(temp2)
                combine_entities.append(temp)
                break
    
    #添加miss掉的true_entities
    for entity in true_entities:        
        if entity not in correct_true:                
            temp1=[]
            temp1.append(entity[0])
            temp1.append(entity[1])
            temp1.append(test_data[0][0][entity[0]:entity[1]])
            temp1.append(entity[2])
            temp2=[]
            temp2.append('O')
            temp=[]
            temp.append(temp1)
            temp.append(temp2)
            combine_entities.append(temp)
            #print(temp)
           
    #添加spu的pred_entities
    for entity in pred_entities:
        if entity not in correct_pred:
            temp1=[]
            temp1.append('O')
            temp2=[]
            temp2.append(entity[0])
            temp2.append(entity[1])
            temp2.append(test_data[0][0][entity[0]:entity[1]])
            temp2.append(entity[2])
            temp=[]
            temp.append(temp1)
            temp.append(temp2)
            combine_entities.append(temp)

    #print(combine_entities)
    return combine_entities
    
def read_corpora(corpus,mode):
    if corpus=='MH':
        path='..\MH\MH_normalized'
        files= os.listdir(path)
        for file in files[0:10]:
            print(file)
            tsv_data=read_file('..\MH\MH_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)

            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)

    elif corpus=='HIPE':
        file='..\HIPE2020\HIPE2020_normalized.tsv'
        tsv_data=read_file(file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)          
        test_data=iob_to_spacy_format(iob_data)
        true_entities, pred_entities, doc=spacy_predict(test_data)
        #data_display(true_entities, pred_entities, test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)
        elif mode=='type':
            type_match(true_entities, pred_entities)
        elif mode=='partial':
            partial_match(true_entities, pred_entities)
        
    elif corpus=='sloane':
        path='..\Sloane Catalogues\Sloane Catalogue_normalized'
        files= os.listdir(path)
        for file in files[0:2]:
            print(file)
            tsv_data=read_file('..\Sloane Catalogues\Sloane Catalogue_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)
    elif corpus=='old bailey':
        path='..\Old Bailey\oldbailey_normalized'
        files= os.listdir(path)
        for file in files[0:499]:
            print(file)
            tsv_data=read_file('..\Old Bailey\oldbailey_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_spacy_format(iob_data)    
            true_entities, pred_entities, doc=spacy_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities)
    per_precision,per_recall,per_f,place_precision,place_recall,place_f=score(mode) 
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))    
        


if __name__ == "__main__":    
    
    all_per_correct=0
    all_per_incorrect=0
    all_per_partial=0
    all_per_miss=0
    all_per_spurius=0
    all_per_partial_type=0
    all_per_partial_weak=0
    
    all_place_correct=0
    all_place_incorrect=0
    all_place_partial=0
    all_place_miss=0
    all_place_spurius=0
    all_place_partial_type=0
    all_place_partial_weak=0
    
    all_per_relevant=0 #all person annotations in gold standard corpus
    all_per_retrive=0 #all person annotations produced by Spacy
    all_place_relevant=0
    all_place_retrive=0
    nlp = spacy.load("en_core_web_sm")
    read_corpora('old bailey','strict')
    
    '''
    path='..\MH\MH_normalized'
    files= os.listdir(path)
    for file in files[0:1589]:
        print(file)   
        #tsv_data=read_file(file_path)
        tsv_data=read_file('..\MH\MH_normalized\%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)

        test_data=iob_to_spacy_format(iob_data)
        nlp = spacy.load("en_core_web_sm")
        true_entities, pred_entities, doc=spacy_predict(test_data)
        data_display(true_entities, pred_entities, test_data) 
        
    
        strict(true_entities, pred_entities)
        #type_match(true_entities, pred_entities)
        #partial_match(true_entities, pred_entities)
    '''    
    #per_precision,per_recall,per_f,place_precision,place_recall,place_f=score('strict')    
    #print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    #print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))


    

    

