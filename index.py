from unittest import result
from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
import uvicorn
from fastapi.responses import FileResponse
#import gensim
from PIL import Image
from torch import autocast
from fastapi.middleware.cors import CORSMiddleware
from ftlangdetect import detect
import requests
import re

#from diffusers import StableDiffusionPipeline
from konlpy.tag import Mecab   
import json
import torch
import torch.nn as nn
import numpy as np
#from konlpy.tag import Mecab
#from module.DialogService import predict_dialog
from inference import senti_func, senti_model, senti_token, polite_func,polite_model,polite_token, grammer_func, grammer_model, grammer_token, ner_func,ner_model,ner_token,emo_model,emo_token,dialect_model,dialect_token,summary_model,summary_token,hate_model,hate_token,copywrite_model,copywrite_token,act_model,act_token,well_config,well_model,well_token,chat_model,chat_token,tocorrect_model,tocorrect_token,todialect_model,todialect_token,toformal_model,toformal_token,toinformal_model,toinformal_token,topolite_model,topolite_token,tostandard_model,tostandard_token,letter_token,letter_model, pipe_en2ko,pipe_ko2en
from care.koelectra import koelectra_input
#import openai
from bs4 import BeautifulSoup
from threading import Event, Thread
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
#import argostranslate.package
#import argostranslate.translate
from huggingface_hub import hf_hub_download
#from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from googlesearch import search
from transformers import ElectraTokenizer, ElectraForQuestionAnswering, pipeline 
# Download and install Argos Translate package
"""
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == "en" and x.to_code == "ko", available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())
"""
#openai.api_key = "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"

import hashlib
import os
import json
from  typing import List, Optional
tokenizer = ElectraTokenizer.from_pretrained("monologg/koelectra-base-v3-finetuned-korquad") 
model = ElectraForQuestionAnswering.from_pretrained("monologg/koelectra-base-v3-finetuned-korquad") 
model = pipeline("question-answering", tokenizer=tokenizer, model=model, device=0) 
mecab = Mecab() 

class Query(BaseModel):
  q : str
  c : str

class Param(BaseModel):
  prompt : str

class Chat(BaseModel):
  prompt : str
  history : list
  lang = "auto"
  type = "assist"
  temp = 0.5
  top_p = 1.0
  top_k = 0
  max = 1024

pattern = r'\([^])]*\)'

to = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

PROMPT_DICT = {
    "prompt_input": (
        "Below is an instruction that describes a task, paired with an input that provides further context.\n"
        "아래는 작업을 설명하는 명령어와 추가적 맥락을 제공하는 입력이 짝을 이루는 예제입니다.\n\n"
        "Write a response that appropriately completes the request.\n요청을 적절히 완료하는 응답을 작성하세요.\n\n"
        "### Instruction(명령어):\n{instruction}\n\n### Input(입력):\n{input}\n\n### Response(응답):"
    ),
    "prompt_no_input": (
        "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
        "### Instruction:\n{instruction}\n\n### Response:"
    ),
}

"""
EMO_MAP = [
'neutral',
'angry',
'sadness',
'disgust',
'happiness',
'fear',
'surprise'
]
"""
EMO_MAP = [
'보통',
'화남',
'슬픔',
'혐오',
'행복',
'공포',
'놀람'
]

"""
HATE_MAP = [
'censure',
'hate',
'sexual',
'neutral',
'abuse',
'violence',
'crime',
'discrimination'
]
"""

HATE_MAP = [
'비난',
'증오',
'성적',
'보통',
'욕설',
'폭력',
'범죄',
'차별'
]

DIALECT_MAP = [
  'GG',
  'GW',
  'CC',
  'GS',
  'JL',
  'JJ'
]

#JR(전라)/GS(경상)/JJ(제주)/GW(강원)/CC(충청)")

ACT_MAP = [
'진술',
'충고',
'주장',
'질문',
'부탁',
'반박',
'감사',
'사과',
'부정',
'반응',
'약속',
'일반',
'명령',
'긍정',
'거절',
'위협',
'인사',
'위임',
'약속'
]

"""
ACT_MAP = [
'(단언) 진술하기',
'(지시) 충고제안',
'(단언) 주장하기',
'(지시) 질문하기',
'(지시) 부탁하기',
'(단언) 반박하기',
'(표현) 감사하기',
'(표현) 사과하기',
'(표현) 부정감정',
'(반응) 관습적반응',
'(언약) 약속하기',
'N/A',
'(지시) 명령요구',
'(표현) 긍정감정',
'(언약) 거절하기',
'(언약) 위협하기',
'(표현) 인사하기',
'(선언) 위임하기',
'(언약) 약속하기'
]
"""

app = FastAPI()

origins = [
    "http://canvers.net",
    "https://canvers.net",   
    "http://www.canvers.net",
    "https://www.canvers.net",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/web", StaticFiles(directory="web"), name="web")

#mecab = Mecab()

#path_ko = hf_hub_download(repo_id="rippertnt/NLP-MODEL", filename="vector_ko.bin")
#word2vec = gensim.models.Word2Vec.load(path_ko)
#word2vec = gensim.models.wv.Word2Vec.load(path_ko)

#from gensim import models

#ko_model = models.fasttext.load_facebook_model('/home/circulus/cc.ko.300.bin')


def translate(sentence):
  """
  input_ids = ko2en_token.encode(sentence)
  input_ids = torch.tensor(input_ids)
  input_ids = input_ids.unsqueeze(0)
  output = ko2en_model.generate(input_ids.to("cuda:1"), eos_token_id=1, max_length=128, num_beams=5)
  return ko2en_token.decode(output[0], skip_special_tokens=True)
  """
  return pipe_ko2en(sentence, num_return_sequences=1, max_length=1024)[0]['generated_text']

def translate2(sentence):
  return pipe_en2ko(sentence, num_return_sequences=1, max_length=1024)[0]['generated_text']


def load_category():
  root_path = '.'
  category_path = f"{root_path}/data/label.txt"
  c_f = open(category_path,'r')
  category_lines = c_f.readlines()
  category = []
  
  for line_num, line_data in enumerate(category_lines):
    category.append(line_data.rstrip())
  
  return category

category = load_category()

@app.get("/")
def main():
  return { "result" : True, "data" : "AI-NLP-TRANS V1" }      

from serverinfo import si
@app.get("/monitor")
def monitor():
	return si.getAll()

@app.post("/qa") 
def qa(query : Query): 
    question = query.q
    context = query.c
    result = model({ "question" : question,  "context" : context }) 
    #print(result) 
    answer = result["answer"] 

    if answer.find('(') > -1 and answer.find(')') < 0:
        if(answer.startswith('(')):
            answer.replace("(","")
        else:
            answer = answer + ")"
    if answer.endswith('의'): 
        answer = answer.replace("의","")       
    answer = re.sub(pattern=pattern, repl='', string=answer )

    list = mecab.pos(result["answer"]) 
    print(list) 
    for word in list: 
        print(word[1]) 
        #if word[1] in ["JX","JKB","JKO"]: #Josa #Adjective 
        #if word[1].startswith('J'):
        #if answer.endswith('의'):
        #    answer = answer.replace('의','')
        #answer = answer.replace('이다','')
        #answer = answer.replace('라는','')
        if word[1].startswith('JKO') or word[1].startswith('JKS') or word[1].startswith('JKB') or word[1].startswith('JX') or word[1].startswith('JC'): 
            answer = answer.replace(word[0],"")
        if word[1].startswith('VCP'): 
            answer = answer.replace(word[0],"") 
        if word[1].startswith('SS'): 
            answer = answer.replace(word[0],"")   
        if word[1].endswith('F'): 
            answer = answer.replace(word[0],"")                        
        #if answer.find('(') > -1 and answer.find(')') < 0:
        #    answer = answer + ")"
        #if answer.find(''  
    print(result)
    
    result["answer"] = answer 
    return result 

@app.get("/v1/language", summary="어느 언어인지 분석합니다.")
def language(input : str):
  return { "result" : True, "data" : detect(input)['lang'] }


@app.get("/v2/dialog", summary="BART 기반의 자유 대화를 수행합니다. (좀더 형식적이지만 이해가능, 사투리나 어투 변환 내장)",
  description="type=PL(공손)/IF(반말)/JR(전라)/GS(경상)/JJ(제주)/GW(강원)/CC(충청)")
def dialog2(input : str, type='PL'):
  encoded = chat_token.encode(f"<t>{type}</t>{input}")
  input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)

  beam_outputs = chat_model.generate(
    input_ids.to("cuda"), 
    min_length=12,
    max_length=48, 
    num_beams=5, 
    no_repeat_ngram_size=2, 
    early_stopping=True, 
    num_return_sequences=3
  )

  sample_outputs = chat_model.generate(
    input_ids.to("cuda"),
    do_sample=True, 
    min_length=12,
    max_length=48, 
    top_k=45, 
    no_repeat_ngram_size=2,
    top_p=0.9, 
    num_return_sequences=3
  )

  return { "result" : True, "data" : [
    chat_token.decode(beam_outputs[0], skip_special_tokens=True),
    chat_token.decode(beam_outputs[1], skip_special_tokens=True),
    chat_token.decode(beam_outputs[2], skip_special_tokens=True),
    chat_token.decode(sample_outputs[0], skip_special_tokens=True),
    chat_token.decode(sample_outputs[1], skip_special_tokens=True),
    chat_token.decode(sample_outputs[2], skip_special_tokens=True)
  ] }


@app.get("/v1/search", summary="입력한 텍스트를 기반으로 검색을 수행합니다.")
def search_txt(prompt="", lang="ko"): # gen or med

  titles = []
  urls = []
  descs = []
  #url = f'https://www.duckduckgo.com/html/?q={prompt}'

  #ua = UserAgent()
  #header = {'User-Agent':str(ua.chrome)}

  #response = requests.get(url, headers=header)
  """
	print(response.text)

  if response.status_code == 200:
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('.result')

    for item in items:
      titles.append(item.select_one('.result__a').get_text().strip())
      urls.append(f"https://{item.select_one('.result__url').get_text().strip()}")
      descs.append(item.select_one('.result__snippet').get_text().strip())

  else : 
    print(response.status_code)
  """

  results = search(prompt, num_results=10, advanced=True)
  for item in results:
    urls.append(item.url)
    titles.append(item.title)
    descs.append(item.description)

  return { "result" : True, "titles" : titles, "urls" : urls, "descs" : descs }

@app.get("/v2/copywrite", summary="BART 기반의 카피라이트를 생성합니다.",
  description="type=['식품/제과','음료/주류/기호식품','자동차/정유','전기전자','제약/의료/복지','출판/교육/문화','패션/스포츠','화장품','게임','관공서/지자체','기업','보험/금융','생활/가정용품','서비스/유통/레저','정보통신','금융/보험','서비스/유통/레저)','음료/기호식품','관공서/단체/공익/기업PR','아파트/건설']")
def copywrite(input : str, type='기본'):
  encoded = copywrite_token.encode(f"<t>{type}</t>{input}")
  input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)

  beam_outputs = copywrite_model.generate(
    input_ids,  #.to(to)
    min_length=12,
    max_length=64, 
    num_beams=5, 
    no_repeat_ngram_size=2, 
    early_stopping=True, 
    num_return_sequences=3
  )

  sample_outputs = copywrite_model.generate(
    input_ids, #.to(to)
    do_sample=True, 
    min_length=12,
    max_length=64, 
    top_k=45, 
    no_repeat_ngram_size=2,
    top_p=0.9, 
    num_return_sequences=7
  )

  return { "result" : True, "data" : [
    chat_token.decode(beam_outputs[0], skip_special_tokens=True),
    chat_token.decode(beam_outputs[1], skip_special_tokens=True),
    chat_token.decode(beam_outputs[2], skip_special_tokens=True),
    chat_token.decode(sample_outputs[0], skip_special_tokens=True),
    chat_token.decode(sample_outputs[1], skip_special_tokens=True),
    chat_token.decode(sample_outputs[2], skip_special_tokens=True),
    chat_token.decode(sample_outputs[3], skip_special_tokens=True),
    chat_token.decode(sample_outputs[4], skip_special_tokens=True),
    chat_token.decode(sample_outputs[5], skip_special_tokens=True),
    chat_token.decode(sample_outputs[6], skip_special_tokens=True)
  ] }


@app.get("/v2/letter", summary="BART 기반의 아침편지를 생성합니다.",
  description="")
def letter(input : str):
  encoded = letter_token.encode(f"{input}")
  input_ids = torch.LongTensor(encoded).unsqueeze(dim=0)

  beam_outputs = letter_model.generate(
    input_ids, #.to(to)
    min_length=12,
    max_length=256, 
    num_beams=5, 
    no_repeat_ngram_size=2, 
    early_stopping=True, 
    num_return_sequences=3
  )

  sample_outputs = letter_model.generate(
    input_ids, #.to(to)
    do_sample=True, 
    min_length=12,
    max_length=256, 
    top_k=45, 
    no_repeat_ngram_size=2,
    top_p=0.9, 
    num_return_sequences=7
  )

  return { "result" : True, "data" : [
    chat_token.decode(beam_outputs[0], skip_special_tokens=True),
    chat_token.decode(beam_outputs[1], skip_special_tokens=True),
    chat_token.decode(beam_outputs[2], skip_special_tokens=True),
    chat_token.decode(sample_outputs[0], skip_special_tokens=True),
    chat_token.decode(sample_outputs[1], skip_special_tokens=True),
    chat_token.decode(sample_outputs[2], skip_special_tokens=True),
    chat_token.decode(sample_outputs[3], skip_special_tokens=True),
    chat_token.decode(sample_outputs[4], skip_special_tokens=True),
    chat_token.decode(sample_outputs[5], skip_special_tokens=True),
    chat_token.decode(sample_outputs[6], skip_special_tokens=True)
  ] }  

@app.post("/v1/summary", summary="문장을 요약합니다.")
def summary(param : Param):
  text = param.prompt.replace('\n', ' ')

  raw_input_ids = summary_token.encode(text)
  input_ids = [summary_token.bos_token_id] + raw_input_ids + [summary_token.eos_token_id]

  #summary_ids = model.generate(torch.tensor([input_ids]))
  summary_ids = summary_model.generate(torch.tensor([input_ids]),  min_length=64, num_beams=4,  max_length=512,  eos_token_id=1) #.to(to)
  output = summary_token.decode(summary_ids.squeeze().tolist(), skip_special_tokens=True)
  return { "result" : True, "data" : output }

"""
@app.get("/v1/vector", summary="문장에 포함된 단어간의 관계를 확인합니다.")
def vector(sentence : str):
  dic = []
  
  list = mecab.pos(sentence)
  for word in list:
    print(word)
    if word[1] in ["NNG","NNP","NNB","VA","VV","VX","MAG","IC","XR"] and len(word[0]) > 0: #Josa #Adjective
      item = { "word" : word[0], "tag" : word[1] }
      try:
        #item = ko_model.similar_by_word(word[0], 10)
        item['pos'] = ko_model.similar_by_word(word[0], 5)
        item['neg'] = ko_model.similar_by_word(word[0], -5)
        #item['pos'] = word2vec.most_similar(positive=[word[0]],topn=5)#word2vec.wv.most_similar(positive=[word[0]],topn=5)
        #item['neg'] = word2vec.most_similar(negative=[word[0]],topn=5)#word2vec.wv.most_similar(negative=[word[0]],topn=5)
        dic.append(item)
      except:
          print()

  return { "result" : True, "data" : dic}
"""

@app.get("/v1/sentiment", summary="문장의 긍/부정을 분석합니다. LABEL_0 은 부정, LABEL_1 은 긍정입니다.")
def sentiment(sentence : str):
  data = senti_func(sentence)
  return { "result" : True, "data" : data }

@app.get("/v1/polite", summary="문장이 존대말인지 아닌지를 확인합니다. LABEL_0 은 반말, LABEL_1은 존대말.")
def polite(sentence : str):
  data = polite_func(sentence)
  return { "result" : True, "data" : data }  

@app.get("/v1/grammer", summary="문장의 문법이 맞는지 확인합니다.. LABEL_0 은 문법 틀림., LABEL_1은 문법 맞음.")
def grammer(sentence : str):
  data = grammer_func(sentence)
  return { "result" : True, "data" : data }    

@app.get("/v1/emotion", summary="입력문장으로 부터 감성을 추출합니다.",
  description="neutral, angry, sadness, disgust, happiness, fear, surprise")
def emotion(sentence : str):
  """
  results = []
  inputs = emo_token(sentence,return_tensors="pt")
  outputs = emo_model(**inputs)
  scores =  1 / (1 + torch.exp(-outputs[0]))  # Sigmoid
  threshold = .3
  for item in scores:
      labels = []
      scores = []
      for idx, s in enumerate(item):
          if s > threshold:
              print(s)
              results.append({ "label" : emo_model.config.id2label[idx], "score" : s.item()})
  """
  results = []
  inputs = emo_token(sentence,return_tensors="pt") #.to(to)
  outputs = emo_model(**inputs)
  scores =  1 / (1 + torch.exp(-outputs[0]))  # Sigmoid
  threshold = .3
  for item in scores:
    labels = []
    scores = []
    for idx, s in enumerate(item):
      if s > threshold:
        results.append({ "label" : EMO_MAP[idx], "score" : s.item()})  
  return { "result" : True, "data" : results }

@app.get("/v1/dialect", summary="입력문장이 표준문장인지 지역사투리(충청,강원,전라,경상,제주)인지 확인합니다.",
  description="")
def dialect(sentence : str):
  results = []
  inputs = dialect_token(sentence,return_tensors="pt") #.to(to)
  outputs = dialect_model(**inputs)
  scores =  1 / (1 + torch.exp(-outputs[0]))  # Sigmoid
  threshold = .3
  for item in scores:
    labels = []
    scores = []
    for idx, s in enumerate(item):
      if s > threshold:
        results.append({ "label" : DIALECT_MAP[idx], "score" : s.item()})  
  return { "result" : True, "data" : results }  

@app.get("/v1/act", summary="문장의 의도를 파악합니다.",
  description="진술,충고,주장,질문,부탁,반박,감사,사과,부정,반응,약속,일반,명령,긍정,거절,위협,인사,위임")
def act(sentence : str):
  results = []
  inputs = act_token(sentence,return_tensors="pt")#.to(to)
  outputs = act_model(**inputs)
  scores =  1 / (1 + torch.exp(-outputs[0]))  # Sigmoid
  threshold = .3
  for item in scores:
    labels = []
    scores = []
    for idx, s in enumerate(item):
      if s > threshold:
        results.append({ "label" : ACT_MAP[idx], "score" : s.item()})  
  return { "result" : True, "data" : results }


@app.get("/v1/ner", summary="객체 인식(Named Entity Recognition) 을 수행합니다.",
  description="인물(PER), 학문분야(FLD), 지명(LOC), 기타(POH), 날짜(DAT), 시간(TIM), 기간(DUR), 통화(MNY), 비율(PNT), 수량표현(NOH)")
def ner(sentence : str):
  results = ner_func(sentence)
  result = {}
  for item in results:
      if item["entity"] in result:
          result[item["entity"]].append(item["word"])
      else:
          result[item["entity"]] = [item["word"]] 
  return { "result" : True, "data" : result }

@app.get("/v1/wellness", summary="입력 문장으로 부터 마음 건강 상태를 확인합니다. (ex 우울, 경제, 자살 등)")
def wellness(sentence : str):
  data = koelectra_input(well_token,sentence, None ,512)#to cpu gpu select
  output = well_model(**data)
  logit = output
  softmax_logit = nn.Softmax(logit).dim
  softmax_logit = softmax_logit[0].squeeze()
  max_index = torch.argmax(softmax_logit).item()
  max_index_value = softmax_logit[torch.argmax(softmax_logit)].item()
  return { "result" : True, "data" : { "cat" : category[max_index], "index" : max_index, "value" : max_index_value} } 

@app.get("/v1/ethic", summary="입력문장에 윤리적 문제가 없는지 점검합니다.",
  description="비난,증오,성적,보통,욕설,폭력,범죄,차별") # old is hate
def ethic(sentence : str):
  #data = hate_func(sentence)
  results = []
  inputs = hate_token(sentence,return_tensors="pt") #.to(to)
  outputs = hate_model(**inputs)
  scores =  1 / (1 + torch.exp(-outputs[0]))  # Sigmoid
  threshold = .3
  for item in scores:
    labels = []
    scores = []
    for idx, s in enumerate(item):
      if s > threshold:    
        results.append({ "label" : HATE_MAP[idx], "score" : s.item()})  
  return { "result" : True, "data" : results }

@app.get("/v1/correct", summary="문장의 맞춤법 및 띄어쓰기를 적용해 줍니다.")
def correct(sentence : str):
  input_ids = tocorrect_token.encode(sentence)
  input_ids = torch.tensor(input_ids)
  input_ids = input_ids.unsqueeze(0)
  output = tocorrect_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5) #.to(to)
  output = tocorrect_token.decode(output[0], skip_special_tokens=True)

  return { "result" : True, "data" : output }

@app.post("/v1/ko2en", summary="한국어를 영어로 번역합니다.")
def ko2en(param : Param):

  output= pipe_ko2en(param.prompt, num_return_sequences=1, max_length=1024)[0]
  """
  input_ids = ko2en_token.encode(sentence)
  input_ids = torch.tensor(input_ids)
  input_ids = input_ids.unsqueeze(0)
  output = ko2en_model.generate(input_ids.to("cuda:1"), eos_token_id=1, max_length=1024, num_beams=5)
  output = ko2en_token.decode(output[0], skip_special_tokens=True)
  """
  print(output)
  return { "result" : True, "data" : output['generated_text'] }
  #return { "result" : True, "data" : output }

def stream_ko2en(prompts):
  prompts = prompts.split('\n') #[:-1] for xgen
  length = len(prompts)


  for idx, prompt in enumerate(prompts):
    if len(prompt) > 1:
      output = pipe_ko2en(prompt, num_return_sequences=1, max_length=1024)[0]
#      print(output)
      result = output['generated_text']
#      print(result)
#      print(idx, length)
      #yield result + "</br>"

      if idx < length - 1:
        yield result + "</br>"
      else:
        yield result
    elif idx < length - 1:
      yield "</br>"

@app.post("/v2/ko2en", summary="한국어를 영어로 번역합니다.(streaming)")
def ko2en2(param : Param):
  return StreamingResponse(stream_ko2en(param.prompt))  

@app.post("/v1/en2ko", summary="영어를 한국어로 번역합니다.")
def en2ko(param : Param):
  print(param.prompt)
  output= pipe_en2ko(param.prompt, num_return_sequences=1, max_length=1024)[0]
#  print(output)
  """
  input_ids = en2ko_token.encode(sentence)
  input_ids = torch.tensor(input_ids)
  input_ids = input_ids.unsqueeze(0)
  output = en2ko_model.generate(input_ids.to("cuda:1"), eos_token_id=1, max_length=1024, num_beams=5)
  output = en2ko_token.decode(output[0], skip_special_tokens=True)
  """
  return { "result" : True, "data" : output['generated_text'] }


def stream_en2ko(prompts):
  prompts = prompts.split('\n') #[:-1] for xgen patch
  print(prompts)
  #prompts = prompts.split('\n')
  length = len(prompts)
  for idx, prompt in enumerate(prompts):
    if len(prompt) > 1:
      output = pipe_en2ko(prompt, num_return_sequences=1, max_length=1024)[0]
      result = output['generated_text']
#      print(idx, length)      
#      print(result)

      if idx < length - 1:
        yield result + "</br>"
      else:
        yield result
    elif idx < length - 1:
      yield "</br>"      
#      yield result + "</br>"
#    else:
#      yield "</br>"      


@app.post("/v2/en2ko", summary="영어를 한국어로 번역합니다. (streaming)")
def en2ko2(param : Param):
  return StreamingResponse(stream_en2ko(param.prompt))

@app.get("/v2/todialect", summary="입력한 문장을 지역사투리로 전환합니다.")
def todialect(input : str, type='JJ'):
  encoded = todialect_token.encode(f"<t>{type}</t>{input}")
  input_ids = torch.tensor(encoded)
  input_ids = input_ids.unsqueeze(0)
  output = todialect_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5) #.to(to)
  output = todialect_token.decode(output[0], skip_special_tokens=True)

  return { "result" : True, "data" : output }

@app.get("/v2/tostandard", summary="입력한 사투리 문장을 표준어로 전환합니다.") #.to(to)
def tostandard(input : str):
  encoded = tostandard_token.encode(f"<t>{type}</t>{input}")
  input_ids = torch.tensor(encoded)
  input_ids = input_ids.unsqueeze(0)
  output = tostandard_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5)
  output = tostandard_token.decode(output[0], skip_special_tokens=True)

  return { "result" : True, "data" : output }

@app.get("/v1/tostyle", summary="입력한 문장의 어투를 전환합니다. (반말/존대말/존칭어)",
  description="style=polite/formal/informal")
def tostyle(sentence : str, style="polite"):

  if style == "formal":
    input_ids = toformal_token.encode(sentence)
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)
    output = toformal_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5) #.to(to)
    output = toformal_token.decode(output[0], skip_special_tokens=True)
  elif style == "informal":
    input_ids = toinformal_token.encode(sentence)
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)
    output = toinformal_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5) #.to(to)
    output = toinformal_token.decode(output[0], skip_special_tokens=True)
  else:
    input_ids = topolite_token.encode(sentence)
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)
    output = topolite_model.generate(input_ids, eos_token_id=1, max_length=128, num_beams=5) #.to(to)
    output = topolite_token.decode(output[0], skip_special_tokens=True)

  return { "result" : True, "data" : output }

ENV = "OPS"

conf = json.load(open('config.json', 'r'))
CONF = conf[ENV]
print(CONF)

print("CIRCULUS_ENV: " + ENV)

if __name__ == "__main__":
  uvicorn.run("index:app",host=CONF["HOST"],port=CONF["PORT"])
  #uvicorn.run("index:app", host="0.0.0.0", port=cfg["LOCAL_PORT"], log_level="debug")