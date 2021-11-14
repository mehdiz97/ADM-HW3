# -*- coding: utf-8 -*-
"""
Created on Sat Nov 13 21:37:34 2021

@author: xufeng zhang
"""

"""
Functions of Question 1
"""

"""
1.1 Get the list of animes
"""
# import modules
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time
import os
import random
import datetime
import re
import numpy as np
import pandas as pd
import nltk
nltk.download('punkt')
import math
import warnings
warnings.filterwarnings('ignore')

# 1.1 input a url, and get all urls in the page we input.
def getlink(url): #get all links in one web page
    link = []
    try: 
    # Open the URL and read the whole page
      red = urllib.request.urlopen(url,timeout=30)
      html = red.read()
      red.close()
      soup = BeautifulSoup(html, 'html.parser')
      tags = soup('a')
 
      for tag in tags: 
        link.append(tag.get('href', None))
    except:
        getlink(url)# Solve the problem that the sever didn't return data sometimes
    return link

"""
1.2 Crawl animes
"""

# 1.2 input a url, return the html 
def getHtml(url): # get the html from url
    global html
    try:
        red = urllib.request.urlopen(url,timeout=30)
        html = red.read()
        red.close()
    except:
        getHtml(url)
    return html
 
# 1.2 input file name(path) and html, save it to local disk 
def saveHtml(file_name, file_content): # save the html
    with open(file_name.replace('/', '_') + ".html", "wb") as f:
        f.write(file_content)
    f.close
    
"""
1.3 Parse downloaded pages
"""
# 1.3 clean unuseful characters in type strings we get
def type_clean(anime_type): # clean the string we got which inclued the info of type
  new_name = ''
  point = 0
  if anime_type != []:
    for c in anime_type[0]:
      if point == 1:
        new_name = new_name + c
      if c == '>':
        point = 1
  return new_name

#1.3 clean the date strings and return time type data.
def date_clean(animeDate): # Estimate the string we get included the date information, then we change it from string to ReleaseDate and EndDate
  dateset = animeDate[0].split('to')
  if len(dateset) == 2 and ',' in dateset[1] and ',' in dateset[0]:
    re_date = date_transfer(dateset[0])
    re_date = datetime.datetime.strptime(re_date,'%m %d %Y')
    re_date = re_date.date()
    en_date = date_transfer(dateset[1])
    en_date = datetime.datetime.strptime(en_date,'%m %d %Y')
    en_date = en_date.date()
  else:
    if len(dateset) == 2 and ',' not in dateset[1] and ',' not in dateset[0]:
      re_date = dateset[0]
      en_date = dateset[1]
    else:
      if len(dateset) == 2 and ',' not in dateset[1]:
        re_date = date_transfer(dateset[0])
        re_date = datetime.datetime.strptime(re_date,'%m %d %Y')
        re_date = re_date.date()
        en_date = ' '
      else:
        if len(dateset) == 1 and ',' in dateset[0]:
          re_date = date_transfer(dateset[0])
          re_date = datetime.datetime.strptime(re_date,'%m %d %Y')
          re_date = re_date.date()
          en_date = ' '
        else:
          re_date = dateset[0]
          en_date = ' '
  return re_date,en_date

#1.3 # transfer the format (MAr 01, 2021 -> 03 01 2021)
def date_transfer(date_str):
  month = {'Jan':'1','Feb':'2','Mar':'3','Apr':'4','May':5,'Jun':6,'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12}
  newdate = date_str.split()
  newdate[0] = month[newdate[0]]
  day = newdate[1]
  newdate[1] = day[0:-1]
  returndate = str(newdate[0])+' '+str(newdate[1])+' '+str(newdate[2])
  return returndate

#1.3 # Whole function we used to get info from html by Regular Expression
def getinfo(html_path):
  with open(html_path,'r',encoding = 'utf-8') as f:
    text = f.read()
  f.close

  name_res = r'<span itemprop="name">\n(.*?)\n' #1.Title
  animeTitle = re.findall(name_res,text)
  animeTitle = str(animeTitle[-1])
  quadtest = 0
  newtitle = ''
  for k in animeTitle:
    if k != ' ':
      quadtest = 1
    if quadtest == 1:
      newtitle = newtitle + k
  animeTitle = newtitle
  print(animeTitle)


  type_res = r'<span class="dark_text">Type:</span>\n(.*?)</a>'#2.Type
  anime_type = re.findall(type_res,text)
  animeType = type_clean(anime_type)
  #animetype = animeType[0]

  Episode_res = r'<span class="dark_text">Episodes:</span>\n(.*?)\n'#3.NumEpisode
  animeNumEpisode = re.findall(Episode_res,text)
  animeNumEpisode = animeNumEpisode[0]

  Date_res = r'<span class="dark_text">Aired:</span>\n(.*?)\n'#4.Date
  animeDate = re.findall(Date_res,text)
  releaseDate,endDate = date_clean(animeDate)



  Member_res = r'<span class="dark_text">Members:</span>\n(.*?)\n'#5.Member
  animeNumMembers = re.findall(Member_res,text)
  newmember =''
  for item in animeNumMembers[0]:
    if item !=" " and item != ',':
      newmember =newmember + item
  animeNumMembers = int(newmember)

  score_res = r'<span class="dark_text">Score:</span>\n(.*?)</span>'#6.score
  strscore = re.findall(score_res,text)
  newscore = ''
  scoretest = 0
  for item in strscore[0]:
    if scoretest == 1:
      newscore = newscore + item
    if item == '>':
      scoretest = 1
  if newscore != 'N/A':
    animeScore = float(newscore)
  else:
    animeScore = newscore


  user_res = r'<span itemprop="ratingCount" style="display: none">(.*?)</span>'#7.users
  struser = re.findall(user_res,text)
  if struser != []:
    animeUsers = int(struser[0])
  else:
    animeUsers = ' '

  rank_res = r'<span class="dark_text">Ranked:</span>\n(.*?)<sup>'#8.rank
  strRank = re.findall(rank_res,text)
  newrank = ''
  for item in strRank[0]:
    if item != '#':
      newrank = newrank + item
  animeRank = newrank
  print(animeRank)

  popu_res = r'<span class="dark_text">Popularity:</span>\n(.*?)\n'#9.popularity
  strpopu= re.findall(popu_res,text)
  newpopu = ''
  for item in strpopu[0]:
    if item != '#':
      newpopu = newpopu + item
  animePopularity = int(newpopu)

  des_res = r'<meta property="og:description" content="(.*?)>'#10.animeDescription
  animeDescription = re.findall(des_res,text)
  animeDescription = animeDescription[0]

  rel_res = r'<td nowrap="" valign="top" class="ar fw-n borderClass">(.*?)<' #11.Related
  animeRe = re.findall(rel_res,text)
  lated_res = r'<td width="100%" class="borderClass">(.*?)</td>'
  animelated = re.findall(lated_res,text)
  for i in range(len(animelated)):
    newanimelated = ''
    latedtest = 0
    for c in animelated[i]:
      if c == '<':
        latedtest = 0
      if latedtest == 1:
        newanimelated = newanimelated + c
      if c == '>':
        latedtest = 1
    animelated[i] = newanimelated
  animeRelated = []
  for j in range(len(animeRe)):
    animeRelated.append(animeRe[j]+animelated[j])


  cha_res = r'<h3 class="h3_characters_voice_actors">(.*?)</a></h3>' #12.Character
  animeCharacters = re.findall(cha_res,text)
  for i in range(len(animeCharacters)):
    chartest = 0
    newchar = ''
    for k in animeCharacters[i]:
      if chartest == 1:
        newchar = newchar+k
      if k == '>':
        chartest = 1
    animeCharacters[i] = newchar

  voice_res = r'<td class="va-t ar pl4 pr4">\n(.*?)</a><br>' #13.voicer
  animeVoices = re.findall(voice_res,text)
  for i in range(len(animeVoices)):
    voicetest = 0
    newvoice = ''
    for k in animeVoices[i]:
      if voicetest == 1:
        newvoice = newvoice+k
      if k == '>':
        voicetest = 1
    animeVoices[i] = newvoice

  staff_res = r'<td valign="top" class="borderClass">\n(.*?)</a>' #14.staff
  animeStaff = re.findall(staff_res,text)
  for i in range(len(animeStaff)):
    stafftest = 0
    newstaff = ''
    for k in animeStaff[i]:
      if stafftest == 1:
        newstaff = newstaff+k
      if k == '>':
        stafftest = 1
    animeStaff[i] = newstaff
  renewstaff = []
  for item in animeStaff:
    if item[0] != '<':
      renewstaff.append(item)
  animeStaff = renewstaff

  tsv = ' \t '
  output_str = animeTitle+tsv+animeType+tsv+str(animeNumEpisode)+tsv+str(releaseDate)+tsv+str(endDate)+tsv+str(animeNumMembers)+tsv+str(animeScore)+tsv+str(animeUsers)+tsv+str(animeRank)+tsv+str(animePopularity)+tsv+animeDescription+tsv+str(animeRelated)+tsv+str(animeCharacters)+tsv+str(animeVoices)+tsv+str(animeStaff)
  return output_str # Return a string with all info that we need.


"""
Question 2: Search Engine
"""
"""
2.1 Conjunctive query
"""
#2.1 input a string, return a list of words,no other characters
def clean_des(des):
  import re
  des = re.sub('\[\w+\s+\w*\s+\w+\s+\w+].','', des)
  des = re.sub('[^a-zA-Z\s]','',des)
  tokens = nltk.word_tokenize(des)
  return tokens

#2.1 
"""
If you want to use this SearchEngine, 
you need to load [all_words,read_dictionary,anime_name,anime_des,link] before using it.
"""

def SearchEngine():
  all_words = pd.read_csv('./words_set.csv')
  print("Please input the key words:")
  key_words = input().split()
  
  Numlist = []
  for item in key_words:
    if item in all_words:
      key_num = all_words.index(item)
      Numlist.append(read_dictionary[key_num])

  if Numlist != []:
    all_output_num = Numlist[0]
  else:
    all_output_num = []
  for n in range(len(Numlist)):
    all_output_num=set(all_output_num) & set(Numlist[n])
  # get the number list of  conjunctive queries

  all_output_num = list(set(all_output_num))
  output_name = []
  output_des = []
  output_link = []
  for m in all_output_num:
    output_name.append(anime_name[m])
    output_des.append(anime_des[m])
    output_link.append(link[m])

  final_output = {'animeTitle':output_name,'animeDescription': output_des,'Url':output_link}
  output_df=pd.DataFrame(final_output)
  output_df.index += 1
  return output_df

"""
2.2 If you want to use this SearchEngine, 
you need to load [all_words,read_dictionary,anime_name,anime_des,link] before using it.
"""
#2.2 tfIdf score function
# you need to load read_dictionay, all_des, all_words before use it
def tfidf(wordNum):
  Key_Num = read_dictionary[wordNum]
  tfid = []
  idf = math.log(19131/len(Key_Num))
  for item in Key_Num:
    ni = des_words[item].count(all_words[wordNum])
    tf = ni/len(des_words[item])
    tfi = idf*tf
    tfid.append(tfi)

  return tfid

#2.2 Similarity Calculation
def get_word_vector(input_list,des_list):
  all_element = set(input_list)|set(des_list)
  all_element = list(all_element)  
  v1 = [0]*len(all_element)
  v2 = [0]*len(all_element)

  for i in range(len(all_element)):
    v1[i] = input_list.count(all_element[i])
    v2[i] = des_list.count(all_element[i])
  return v1,v2

def cos_dist(vec1,vec2):
  dist1=float(np.dot(vec1,vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2)))
  return dist1


#2.2 -----------Execute the query 2-------------
def SearchEngine2(key_words): 
  Numlist = []
  for item in key_words:
    if item in all_words:
      key_num = all_words.index(item)
      Numlist.append(read_dictionary[key_num])

  if Numlist != []:
    all_output_num = Numlist[0]
  else:
    all_output_num = []
  for n in range(len(Numlist)):
    all_output_num=set(all_output_num) & set(Numlist[n])
  # get the number list of  conjunctive queries

  all_output_num = list(set(all_output_num))
  output_name = []
  output_des = []
  output_link = []
  similarity_des = []
  for m in all_output_num:
    output_name.append(anime_name[m])
    output_des.append(anime_des[m])
    output_link.append(link[m])
    similarity_des.append(des_words[m])

  # compute the similarity
  similarity = []
  for o in range(len(similarity_des)):
    vec1,vec2=get_word_vector(key_words,similarity_des[o])
    dist1=cos_dist(vec1,vec2)
    similarity.append(dist1)
  # output
  final_output = {'animeTitle':output_name,'animeDescription': output_des,'Url':output_link,'Similarity':similarity}
  output_df=pd.DataFrame(final_output)
  output_df = output_df.sort_values(by='Similarity',ascending = False)
  output_df = output_df[0:10] # get top k animes; k = 10
  output_df.index = range(len(output_df))
  output_df.index += 1
  return output_df



"""
Question 3: Define a new Score
"""
"""

"""
import string
def convert_dtype_float(x):
    ans = []
    for item in x:
        item = item.strip()
        try:
            ans.append(np.float64(item))
        except:
            ans.append(None)
    return pd.Series(ans)

def convert_dtype_int(x):
    ans = []
    for item in x:
        item = item.strip()
        try:
            ans.append(np.int64(item))
        except:
            ans.append(None)
    return pd.Series(ans)

def truncate(n):
    n = str(n).replace('',' ').split()
    n.reverse()
    for i in range(1, len(n)):
        v = int(n[i])
        if int(n[i-1]) >= 5:
            n[i] = str(v+1)
    n.reverse()
    return int(n[0] + '0'*(len(n)-1))
def normDate(x):
    r = list()
    for e in x.fillna(''):
        v = e.replace('th', ' ').replace('nd', ' ').replace('st', ' ').replace('rd', ' ')\
                       .translate(str.maketrans('', '', string.punctuation)).split()
        if len(v) <= 3 or len(v) != 0:
            r.append(v)
    return r
normInt = lambda x : [int(truncate(str(i).replace(',',''))) if i == i else 0 for i in x]
normString = lambda x : [i.translate(str.maketrans('', '', string.punctuation)).lower().split() if len(i) > 0 else None for i in x.fillna('')  ]
normFloat = lambda x : [round(float(str(i).replace(',',''))) if i == i else 0 for i in x]


def search(q):
    # execute query
    err = "There aren't documents for each word of this query"
    # qs = re.sub('\d', '', q.translate(str.maketrans('', '', string.punctuation)).lower())
    qs = q.split()
    q_result = SearchEngine2(qs)
    if not isinstance(q_result, str):
        q = q.strip().split()
        q = [w.lower() for w in q]
        # power up of the score
        doc_score = []
        for doc_id in q_result['animeTitle']:
            score = q_result[q_result['animeTitle'] == doc_id]['Similarity'].to_list()[0]
            # calculate score
            for w in q:
                t = newdf[newdf['animeTitle1']==doc_id]['animeTitle'].to_list()[0]
                s = newdf[newdf['animeTitle1']==doc_id]['animeStaff'].to_list()[0]
                v = newdf[newdf['animeTitle1']==doc_id]['animeVoices'].to_list()[0]
                c = newdf[newdf['animeTitle1']==doc_id]['animeCharacters'].to_list()[0]
                at = newdf[newdf['animeTitle1']==doc_id]['animeType'].to_list()[0]

                if t != None and w in t:
                    score += (1/len(t))*2
                if s != None and w in s:
                    score += (1/len(s))*1.5
                if v != None and w in v:
                    score += (1/len(v))*1.5
                if c != None and w in c:
                    score += (1/len(c))*1.5
                if at != None and w in at:
                  score += 0.5

                if w.isnumeric():
                    if truncate(w) == newdf[newdf['animeTitle']==doc_id]['animeScore'].to_list()[0]:
                        score += 0.5
                    if truncate(w) == newdf[newdf['animeTitle']==doc_id]['animeNumEpisode'].to_list()[0]:
                        score += 0.5
                    if round(float(w)) == newdf[newdf['animeTitle']==doc_id]['animePopularity'].to_list()[0]:
                        score += 0.5
            heapq.heappush(doc_score, (score, doc_id))
        order_doc_id = [i[1] for i in doc_score]
        order_score = [i[0] for i in doc_score]
        r = pd.DataFrame(q_result[q_result['animeTitle']==order_doc_id[0]][['animeTitle','animeDescription' ,'Url' ]])
        for d_id in range(1, len(order_doc_id)):
            r = r.append(q_result[q_result['animeTitle']==order_doc_id[d_id]][['animeTitle', 'animeDescription','Url']])
        r['score'] = order_score
        return r.sort_values(by=['score', 'animeTitle'], ascending=False)[['animeTitle', 'animeDescription','Url' ,'score']].head()
    else:
        return err