# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:58:47 2024

@author: 87142
"""
import csv
import xml.etree.ElementTree as ET
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

def read_xml(dataset,file):
    if dataset=='HIPE':
        tree=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\HIPE\HIPE.out.xml')
        root=tree.getroot()
        pred_entities=[]
        for ent in root.findall(".//ent"):
            entity_type = ent.get("type")
            if entity_type in ["person", "location"]:
                part = ent.find("./parts/part")
                entities=part.text
                sw=part.get('sw')
                length=len(entities)
                temp=[]
                temp.append(int(sw[1:])-13)
                temp.append(int(sw[1:])-13+length)
                #temp.append(entities)
                temp.append(entity_type)
                pred_entities.append(temp)
    elif dataset=='sloane':
        file_basename=file[0:-4]
        xml_name=file_basename+('.out.xml')
        tree=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\sloane\%s'%xml_name)
        root=tree.getroot()
        pred_entities=[]
        for ent in root.findall('.//ent'):
            entity_type = ent.get("type")
            if entity_type in ["person", "location"]:
                part = ent.find("./parts/part")
                entities=part.text
                sw=part.get('sw')
                length=len(entities)
                temp=[]
                temp.append(int(sw[1:])-13)
                temp.append(int(sw[1:])-13+length)
                temp.append(entity_type)
                pred_entities.append(temp)
    elif dataset=='MH':
        file_basename=file[0:-4]
        xml_name=file_basename+('.out.xml')
        tree=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\MH\%s'%xml_name)
        root=tree.getroot()
        pred_entities=[]
        for ent in root.findall('.//ent'):
            entity_type = ent.get("type")
            if entity_type in ["person", "location"]:
                part = ent.find("./parts/part")
                entities=part.text
                sw=part.get('sw')
                length=len(entities)
                temp=[]
                temp.append(int(sw[1:])-13)
                temp.append(int(sw[1:])-13+length)
                temp.append(entity_type)
                pred_entities.append(temp)
    elif dataset=='old bailey':
        file_basename=file[0:-4]
        if file_basename=='16920406':
            xml_name1=file_basename+('_1.out.xml')
            xml_name2=file_basename+('_2.out.xml')
            xml_name3=file_basename+('_3.out.xml')
            tree1=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name1)
            tree2=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name2)
            tree3=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name3)
            root1=tree1.getroot()
            root2=tree2.getroot()
            root3=tree3.getroot()
            #假设text1长度是x,text2中的entities应该是x+sw-14,text3中是x+y+sw-14
            pred_entities=[]
            with open(r"C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\16920406_1.txt", "r", encoding="utf-8") as file:
                text1 = file.read()
            text1_length=len(text1)
            with open(r"C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\16920406_2.txt", "r", encoding="utf-8") as file:
                text2 = file.read()
            text2_length=len(text2)
            for ent in root1.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])-13)
                    temp.append(int(sw[1:])-13+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
            for ent in root2.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])+text1_length-14)
                    temp.append(int(sw[1:])+text1_length-14+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
            for ent in root3.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])+text1_length+text2_length-14)
                    temp.append(int(sw[1:])+text1_length+text2_length-14+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)

        elif file_basename=='17320114' or file_basename=='17420909':
            xml_name1=file_basename+('_1.out.xml')
            xml_name2=file_basename+('_2.out.xml')
            xml_name3=file_basename+('_3.out.xml')
            xml_name4=file_basename+('_4.out.xml')
            txt_name1=file_basename+('_1.txt')
            txt_name2=file_basename+('_2.txt')
            txt_name3=file_basename+('_3.txt')
            tree1=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name1)
            tree2=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name2)
            tree3=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name3)
            tree4=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name4)
            root1=tree1.getroot()
            root2=tree2.getroot()
            root3=tree3.getroot()
            root4=tree4.getroot()
            pred_entities=[]
            with open(r"C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s"%txt_name1, "r", encoding="utf-8") as file:
                text1 = file.read()
            text1_length=len(text1)
            with open(r"C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s"%txt_name2, "r", encoding="utf-8") as file:
                text2 = file.read()
            text2_length=len(text2)
            with open(r"C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s"%txt_name3, "r", encoding="utf-8") as file:
                text3 = file.read()
            text3_length=len(text3)
            for ent in root1.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])-13)
                    temp.append(int(sw[1:])-13+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
            for ent in root2.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])+text1_length-14)
                    temp.append(int(sw[1:])+text1_length-14+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
            for ent in root3.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])+text1_length+text2_length-14)
                    temp.append(int(sw[1:])+text1_length+text2_length-14+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
            for ent in root4.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])+text1_length+text2_length+text3_length-14)
                    temp.append(int(sw[1:])+text1_length+text2_length+text3_length-14+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)

        
        
        
        else:    
            xml_name=file_basename+('.out.xml')
            tree=ET.parse(r'C:\Users\87142\Desktop\Evaluation-Corpora\test\geoparser\old bailey\%s'%xml_name)
            root=tree.getroot()
            pred_entities=[]
            for ent in root.findall('.//ent'):
                entity_type = ent.get("type")
                if entity_type in ["person", "location"]:
                    part = ent.find("./parts/part")
                    entities=part.text
                    sw=part.get('sw')
                    length=len(entities)
                    temp=[]
                    temp.append(int(sw[1:])-13)
                    temp.append(int(sw[1:])-13+length)
                    temp.append(entity_type)
                    pred_entities.append(temp)
           
    return pred_entities

def score(mode):
    all_correct=all_per_correct+all_place_correct
    all_relevant=all_per_relevant+all_place_relevant
    all_retrive=all_per_retrive+all_place_retrive
    all_partial=all_per_partial+all_place_partial
    all_partial_type=all_per_partial_type+all_place_partial_type
    all_partial_weak=all_per_partial_weak+all_place_partial_weak
    if mode=='strict':
        per_precision=all_per_correct/all_per_retrive
        per_recall=all_per_correct/all_per_relevant        
        place_precision=all_place_correct/all_place_retrive
        place_recall=all_place_correct/all_place_retrive         
        micro_precision=all_correct/all_retrive
        micro_recall=all_correct/all_relevant
        #print(all_per_correct,all_per_retrive)
    elif mode=='type':
        per_precision=(all_per_correct+0.5*all_per_partial)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial)/all_place_relevant
        micro_precision=(all_correct+0.5*all_partial)/all_retrive
        micro_recall=(all_correct+0.5*all_partial)/all_relevant
        #print(all_per_correct,all_per_partial,all_per_retrive)
    elif mode=='partial':
        per_precision=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_retrive
        per_recall=(all_per_correct+0.5*all_per_partial_type+0.25*all_per_partial_weak)/all_per_relevant
        place_precision=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_retrive
        place_recall=(all_place_correct+0.5*all_place_partial_type+0.25*all_place_partial_weak)/all_place_relevant
        micro_precision=(all_correct+0.5*all_partial_type+0.25*all_partial_weak)/all_retrive
        micro_recall=(all_correct+0.5*all_partial_type+0.25*all_partial_weak)/all_relevant
        #print(all_per_correct,all_per_partial_type,all_per_retrive)
    elif mode=='lenient':
        per_precision=(all_per_correct+all_per_partial)/all_per_retrive
        per_recall=(all_per_correct+all_per_partial)/all_per_relevant
        place_precision=(all_place_correct+all_place_partial)/all_place_retrive
        place_recall=(all_place_correct+all_place_partial)/all_place_relevant
        micro_precision=(all_correct+all_partial)/all_retrive
        micro_recall=(all_correct+all_partial)/all_relevant
    elif mode=='ultra-lenient':
        per_precision=(all_per_correct+all_per_partial_type+all_per_partial_weak)/all_per_retrive
        per_recall=(all_per_correct+all_per_partial_type+all_per_partial_weak)/all_per_relevant
        place_precision=(all_place_correct+all_place_partial_type+all_place_partial_weak)/all_place_retrive
        place_recall=(all_place_correct+all_place_partial_type+all_place_partial_weak)/all_place_relevant
        micro_precision=(all_correct+all_partial_type+all_partial_weak)/all_retrive
        micro_recall=(all_correct+all_partial_type+all_partial_weak)/all_relevant
    
    per_f=(2*per_precision*per_recall)/(per_precision+per_recall)
    place_f=(2*place_precision*place_recall)/(place_precision+place_recall)    
    macro_f=(per_f+place_f)/2
    micro_f=(2*micro_precision*micro_recall)/(micro_precision+micro_recall)
    
    
    return per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f


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


def strict(true_entities,pred_entities):
    per_correct=[]
    per_incorrect=[]
    place_correct=[]
    place_incorrect=[]
    for te in true_entities:
        for pe in  pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]: #边界一样
                if te[2]=='pers' and pe[2]=='person': #人名分类正确
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):#边界重合
                if te[2]=='pers':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                elif te[2]=='place':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)

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
        if entity[2]=='person':
            per_pred_entities.append(entity)
        elif entity[2]=='location':
            place_pred_entities.append(entity) 
    
    #per_miss=所有true-correct person-incorrect person
    per_miss= per_true_entities.copy()       
    for entity in per_correct:            
            per_miss.remove(entity[0])            
    for entity in per_incorrect:
        try:
            per_miss.remove(entity[0])
        except ValueError:
            pass
    
    #per_spu=所有pred-correct_person-incorrect_person-地名误认为人名
    per_spurius=per_pred_entities.copy()
    for entity in per_correct:
        per_spurius.remove(entity[1])
    for entity in per_incorrect:
        try:
            per_spurius.remove(entity[1])
        except ValueError:
            pass
    for entity in place_incorrect:
        if entity[1][2]=='preson':
            try:
                per_spurius.remove(entity[1])
            except ValueError:
                pass
    
    #place_miss=所有true-correct place-incorrect place
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
        if entity[1][2]=='location':
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
        if pe[2]=='person':
            per_retrive+=1
        elif pe[2]=='location':
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
            if te[0]==pe[0] and te[1]==pe[1]: #边界一样
                if te[2]=='pers' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):
                if te[2]=='pers' and pe[2]=='person':      
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial.append(temp)
                elif te[2]=='pers' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp) 
                elif te[2]=='place' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial.append(temp)
                elif te[2]=='place' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_incorrect.append(temp)
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
        if entity[2]=='person':
            per_pred_entities.append(entity)
        elif entity[2]=='location':
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
        if pe[2]=='person':
            per_retrive+=1
        elif pe[2]=='location':
            place_retrive+=1
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive
      
def partial_match(true_entities, pred_entities,test_data): 
    per_correct=[]
    per_partial_type=[]
    per_partial_weak=[]
    place_correct=[]
    place_partial_type=[]
    place_partial_weak=[]
    
    for te in true_entities:
        for pe in pred_entities:
            if te[0]==pe[0] and te[1]==pe[1]:
                if te[2]=='pers' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='location':
                    #范围对，类型不对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp) 
                    break
                elif te[2]=='place' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_correct.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
                    break
            elif (pe[1]>te[1]>pe[0]) or (te[1]>pe[1]>te[0]) or (te[1]==pe[1]):
                if te[2]=='pers' and pe[2]=='person':
                    #范围重合，类型对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_type.append(temp)
                elif te[2]=='pers' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)
                elif te[2]=='place' and pe[2]=='location':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_type.append(temp)
                elif te[2]=='place' and pe[2]=='person':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_weak.append(temp)
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
        if entity[2]=='person':
            per_pred_entities.append(entity)
        elif entity[2]=='location':
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
    
    for entity in per_partial_weak:
        try:
            place_spurius.remove(entity[1])
        except ValueError:
            pass

    '''
    conjoined_entities=data_display(true_entities, pred_entities, test_data)
    for i in conjoined_entities:
        if i[0]==['O'] and i[1][3]=='location':
            print(i)
    '''
    true_incorrect=[]
    pred_incorrect=[]
    for per_group in place_partial_type:
        true_incorrect.append(per_group[0])
        pred_incorrect.append(per_group[1])
    conjoined_entities=data_display(true_incorrect, pred_incorrect, test_data)
    for entities in conjoined_entities:
        print(entities)
    
    
    
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
        if pe[2]=='person':
            per_retrive+=1
        elif pe[2]=='location':
            place_retrive+=1
    
    
    all_per_retrive=all_per_retrive+per_retrive
    all_place_retrive=all_place_retrive+place_retrive

def read_corpora(corpus,mode):
    if corpus=='HIPE':
        file='..\HIPE2020\HIPE2020_normalized.tsv'
        tsv_data=read_file(file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_text(iob_data)
        true_entities=test_data[0][1]['entities']  
        pred_entities=read_xml('HIPE',file)
        if mode=='strict':
            strict(true_entities,pred_entities)
        elif mode=='type':
            type_match(true_entities, pred_entities)
        elif mode=='partial':
            partial_match(true_entities, pred_entities,test_data)
        elif mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
    elif corpus=='sloane':
        path='..\Sloane Catalogues\Sloane Catalogue_normalized'
        files= os.listdir(path)
        for file in files[0:1]:
            print(file)
            tsv_data=read_file('..\Sloane Catalogues\Sloane Catalogue_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data) 
            true_entities=test_data[0][1]['entities'] 
            pred_entities=read_xml('sloane',file)
            if mode=='strict':
                strict(true_entities,pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)
    elif corpus=='MH':
        path='..\MH\MH_normalized'
        files= os.listdir(path)
        for file in files[1400:1500]:
            print(file)
            tsv_data=read_file('..\MH\MH_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)  
            true_entities=test_data[0][1]['entities'] 
            pred_entities=read_xml('MH',file)
            if mode=='strict':
                strict(true_entities,pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)
    elif corpus=='old bailey':
        path='..\Old Bailey\oldbailey_normalized'
        files= os.listdir(path)
        for file in files[200:220]:
            print(file)
            tsv_data=read_file('..\Old Bailey\oldbailey_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)  
            true_entities=test_data[0][1]['entities'] 
            pred_entities=read_xml('old bailey',file)
            if mode=='strict':
                strict(true_entities,pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities,test_data)
            
            
    per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f=score(mode) 
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))    
    print('Macro F1 score: %f'%macro_f)
    print('Micro F1 score: %f'%micro_f)

def evaluation_corpora(mode): 
    file='..\HIPE2020\HIPE2020_normalized.tsv'
    tsv_data=read_file(file)
    iob_data=[]
    for data in tsv_data:
        iob_element=data[0]+' '+data[1]
        iob_data.append(iob_element)  
    test_data=iob_to_text(iob_data)   
    true_entities=test_data[0][1]['entities'] 
    pred_entities=read_xml('HIPE',file)
    if mode=='strict':
        strict(true_entities, pred_entities)  
    elif mode=='type' or mode=='lenient':
        type_match(true_entities, pred_entities)
    elif mode=='partial' or mode=='ultra-lenient':
        partial_match(true_entities, pred_entities,test_data)
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
        true_entities=test_data[0][1]['entities'] 
        pred_entities=read_xml('MH',file)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
    path='..\Sloane Catalogues\Sloane Catalogue_normalized'
    files= os.listdir(path)
    files= os.listdir(path)
    for file in files[0:2]:
        print(file)
        tsv_data=read_file('..\Sloane Catalogues\Sloane Catalogue_normalized\%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_text(iob_data)  
        true_entities=test_data[0][1]['entities'] 
        pred_entities=read_xml('sloane',file)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
    path='..\Old Bailey\oldbailey_normalized'
    files= os.listdir(path)
    for file in files[0:499]:
        print(file)
        tsv_data=read_file('..\Old Bailey\oldbailey_normalized\%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_text(iob_data)    
        true_entities=test_data[0][1]['entities'] 
        pred_entities=read_xml('old bailey',file)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities,test_data)
            
    per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f=score(mode)
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))
    print('Macro F1 score: %f'%macro_f)
    print('Micro F1 score: %f'%micro_f)


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
    read_corpora('old bailey','partial')
    #evaluation_corpora('ultra-lenient')