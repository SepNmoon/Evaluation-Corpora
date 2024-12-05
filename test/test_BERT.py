# -*- coding: utf-8 -*-
"""
Spyder 编辑器

这是一个临时脚本文件。
"""
from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import csv
import os
from transformers import logging
logging.set_verbosity_error()


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

def iob_to_text(iob_lines): 
    data = []
    sentence = []
    entities = []
    current_entity = None
    start = 0
    
    for line in iob_lines:
        '''
        if line.strip() == "":  # 如果是空行，表示句子结束     
            print(1)
            if sentence:
                data.append((" ".join(sentence), {"entities": entities}))
                
            sentence = []
            entities = []
            current_entity = None
            start = 0
            continue
        '''
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
        
    if current_entity:
        entities.append((current_entity[0], current_entity[1], current_entity[2]))
        
    if sentence:
        data.append((" ".join(sentence), {"entities": entities}))

    return data




def BERT_predict(evaluation_data):
    text=evaluation_data[0][0]
    annotations=evaluation_data[0][1]
    
    tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER-uncased")
    model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER-uncased")
    nlp = pipeline("ner", model=model, tokenizer=tokenizer)

    #print(annotations)    
    
    max_length=1000
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    
    index=0
    
    iob_entities_group=[]
    temp_segment=[]
    #将文本分块，nlp后整合得到总体结果,将BI合一起
    for chunk in chunks:
        chunk_results=nlp(chunk)
        for entity in chunk_results:
            if entity['entity'][0:2]=='B-':
                if temp_segment:
                    iob_entities_group.append(temp_segment)
                temp_segment=[]
                temp=[]
                temp.append(entity['entity'])
                temp.append(entity['start']+index*1000)
                temp.append(entity['end']+index*1000)
                temp_segment.append(temp)
            else:
                temp=[]
                temp.append(entity['entity'])
                temp.append(entity['start']+index*1000)
                temp.append(entity['end']+index*1000)
                temp_segment.append(temp)
        index+=1
    if temp_segment:
        iob_entities_group.append(temp_segment)
    

    #分开不是同一实体的BI
    new_iob_entities_group=[] 
    for entity in iob_entities_group:
        if len(entity)>1:
            #print(entity)
            temp_group=[]
            for i,label in enumerate(entity):
                if not temp_group or label[0][2:5]==temp_group[-1][0][2:5]: #如果是空的或者与上一个标签相同
                    temp_group.append(label)
                else:
                    new_iob_entities_group.append(temp_group)
                    temp_group=[] #开始新组
                    temp_group.append(label)
            if temp_group:
                new_iob_entities_group.append(temp_group)
               
        else:
            new_iob_entities_group.append(entity)
    
    
    #合并BI之间的范围
    predict_entities=[]
    for entity in new_iob_entities_group:
        if entity[0][0][2:5]=='PER':
            temp=[]
            temp.append(entity[0][1])
            temp.append(entity[-1][2])
            temp.append(('PERSON'))
            predict_entities.append(temp)
        elif entity[0][0][2:5]=='LOC':
            temp=[]
            temp.append(entity[0][1])
            temp.append(entity[-1][2])
            temp.append(('LOCATION'))
            predict_entities.append(temp)
        else:
            temp=[]
            temp.append(entity[0][1])
            temp.append(entity[-1][2])
            temp.append(('OTHER'))
            predict_entities.append(temp)
    
    

    return annotations['entities'],predict_entities

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
                if te[2]=='pers' and pe[2]=='PERSON': #人名分类正确
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='LOCATION':
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
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='LOCATION':
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
        if entity[1][2]=='PERSON':
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
        if entity[1][2]=='LOCATION':
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
        elif pe[2]=='LOCATION':
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
                if te[2]=='pers' and pe[2]=='PERSON':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp)
                    break
                elif te[2]=='place' and pe[2]=='LOCATION':
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
                elif te[2]=='pers' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_incorrect.append(temp) 
                elif te[2]=='place' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial.append(temp)
                elif te[2]=='place' and pe[2]=='PERSON':
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
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='LOCATION':
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
        if pe[2]=='PERSON':
            per_retrive+=1
        elif pe[2]=='LOCATION':
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
                if te[2]=='pers' and pe[2]=='PERSON':
                    #范围对，类型对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_correct.append(temp)
                    break
                elif te[2]=='pers' and pe[2]=='LOCATION':
                    #范围对，类型不对
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp) 
                    break
                elif te[2]=='place' and pe[2]=='LOCATION':
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
                elif te[2]=='pers' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    per_partial_weak.append(temp)
                elif te[2]=='place' and pe[2]=='LOCATION':
                    temp=[]
                    temp.append(te)
                    temp.append(pe)
                    place_partial_type.append(temp)
                elif te[2]=='place' and pe[2]=='PERSON':
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
        if entity[2]=='PERSON':
            per_pred_entities.append(entity)
        elif entity[2]=='LOCATION':
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

    #print(pred_entities)
    for i in conjoined_entities:
        if i[0]==['O'] and i[1][3]=='LOCATION':
            print(i)
    
    
    
    '''
    '''
    true_correct=[]
    pred_correct=[]
    #print(per_incorrect)
    for per_group in place_partial_type:
        true_correct.append(per_group[0])
        pred_correct.append(per_group[1])
    
    conjoined_entities=data_display(true_correct, pred_correct, test_data)
    
    for i in conjoined_entities:
        print(i)
    '''
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
        elif pe[2]=='LOCATION':
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
        true_entities,pred_entities=BERT_predict(test_data)
        if mode=='strict':
            strict(true_entities,pred_entities)
        elif mode=='type':
            type_match(true_entities, pred_entities)
        elif mode=='partial':
            partial_match(true_entities, pred_entities,test_data)
        elif mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='ultra-lenient':
            partial_match(true_entities, pred_entities)
    elif corpus=='MH':
        path='..\MH\MH_normalized'
        files= os.listdir(path)
        for file in files[1500:1520]:
            print(file)
            tsv_data=read_file('..\MH\MH_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)    
            true_entities,pred_entities=BERT_predict(test_data)
            #data_display(true_entities, pred_entities, test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities)
    elif corpus=='sloane':
        path='..\Sloane Catalogues\Sloane Catalogue_normalized'
        files= os.listdir(path)
        for file in files[1:2]:
            print(file)
            tsv_data=read_file('..\Sloane Catalogues\Sloane Catalogue_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)    
            true_entities,pred_entities=BERT_predict(test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities)
    elif corpus=='old bailey':
        path='..\Old Bailey\oldbailey_normalized'
        files= os.listdir(path)
        for file in files[0:10]:
            print(file)
            tsv_data=read_file('..\Old Bailey\oldbailey_normalized\%s'%file)
            iob_data=[]
            for data in tsv_data:
                iob_element=data[0]+' '+data[1]
                iob_data.append(iob_element)
            test_data=iob_to_text(iob_data)    
            true_entities,pred_entities=BERT_predict(test_data)
            if mode=='strict':
                strict(true_entities, pred_entities)
            elif mode=='type':
                type_match(true_entities, pred_entities)
            elif mode=='partial':
                partial_match(true_entities, pred_entities,test_data)
            elif mode=='lenient':
                type_match(true_entities, pred_entities)
            elif mode=='ultra-lenient':
                partial_match(true_entities, pred_entities)
            
    per_precision,per_recall,per_f,place_precision,place_recall,place_f,macro_f,micro_f=score(mode) 
    print('Results of %s mode'%(mode))
    print('Person:\nPrecision:%f\nRecall:%f\nF1:%f'%(per_precision,per_recall,per_f))
    print('Location:\nPrecision:%f\nRecall:%f\nF1:%f'%(place_precision,place_recall,place_f))    
    print('Macro F1 score: %f'%macro_f)
    print('Micro F1 score: %f'%micro_f)
        
def evaluation_corpora(mode): 
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
        true_entities,pred_entities=BERT_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities)
    file='..\HIPE2020\HIPE2020_normalized.tsv'
    tsv_data=read_file(file)
    iob_data=[]
    for data in tsv_data:
        iob_element=data[0]+' '+data[1]
        iob_data.append(iob_element)  
    test_data=iob_to_text(iob_data)    
    true_entities,pred_entities=BERT_predict(test_data)
    if mode=='strict':
        strict(true_entities, pred_entities)  
    elif mode=='type' or mode=='lenient':
        type_match(true_entities, pred_entities)
    elif mode=='partial' or mode=='ultra-lenient':
        partial_match(true_entities, pred_entities)
    path='..\Sloane Catalogues\Sloane Catalogue_normalized'
    files= os.listdir(path)
    for file in files[0:2]:
        print(file)
        tsv_data=read_file('..\Sloane Catalogues\Sloane Catalogue_normalized\%s'%file)
        iob_data=[]
        for data in tsv_data:
            iob_element=data[0]+' '+data[1]
            iob_data.append(iob_element)
        test_data=iob_to_text(iob_data)    
        true_entities,pred_entities=BERT_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities)
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
        true_entities,pred_entities=BERT_predict(test_data)
        if mode=='strict':
            strict(true_entities, pred_entities)  
        elif mode=='type' or mode=='lenient':
            type_match(true_entities, pred_entities)
        elif mode=='partial' or mode=='ultra-lenient':
            partial_match(true_entities, pred_entities)
    
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
    
    read_corpora('HIPE','partial')
    #evaluation_corpora('ultra-lenient')
    
    
    