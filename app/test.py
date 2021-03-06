# We need to import request to access the details of the POST request
# and render_template, to render our templates (form and response)
# we'll use url_for to get some URLs for the app on the templates
from flask import Flask, render_template, request, url_for
import os
import nltk
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import string
import random

#use local nltk_data
nltk.data.path.append('app/nltk_data/')


#Initialize the Flask application
app = Flask(__name__)

#Initialize the settings

#maximaal aantal tokens per zin
maxsent=14

#maximaal aantal karakters headline
maxhline=45

#maximaal aantal zinnen lead
maxlead=5

#maximaal aantal zinnen per paragraaf
maxpar=10



#Load frequency list

ins = open( "app/static/vocab_cs_3k", "r" )
array = []
for line in ins:
   fields = line.split( )
   array.append(fields[0])
ins.close()

#Load dictionary of complicated words and suggestions
ins = open( "app/static/woordenlijst.txt", "r" )
dict = {}
for line in ins:
    fields = line.rstrip().split(" 1" )
    if len(fields)>1:
      dict[fields[0]]="1"+fields[1]
ins.close()


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

def splitSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/dutch.pickle')
    corpus = sent_detector.tokenize(text.strip())
    corpus_original=corpus[:]
    #p_punc = re.compile('[!?;:\.,\(\)]')
    #i=0
    #while i < len(corpus):
    #    corpus[i] = p_punc.sub('',corpus[i].lower())
    #    i+=1
    return corpus

def tokenize(text):
    p_punc = re.compile('[!?;:\.,\(\)]')
    text = p_punc.sub('',text.lower())
    words=text.split(' ')
    return words

def getHighfreq(words):
  freqs=[]
  highfreq=0
  for w in words:
    try:
      array.index(w)
    except ValueError:
      "Do nothing"
    else:
      highfreq+=1
  return highfreq/float(len(words))


def getTTRatio(words):
    unique=[]
    for w in words:
      try:
        unique.index(w.lower())
      except ValueError:
        unique.append(w.lower())
    return len(unique)/float(len(words))


def drawGraph(data,randstring,xlabel):
  sns.set_style("dark")
  sns.set_context(rc={"figure.figsize": (8, 5)})

  sns.distplot(data,kde_kws={"color": "crimson", "lw": 3, "label": "Dit bericht"},
           );
  plt.ylabel('aantal')
  plt.xlabel(xlabel)
  #plt.xlim(xmin=0)
  plt.savefig('app/static/images/generated/'+randstring+'.png')
  plt.clf()




# Define a route for the default URL, which loads the form
@app.route('/')
def form():
    return render_template('index.html')



# about
@app.route('/about')
def about():
    return render_template('about.html')

# Define a route for the action of the form, for example '/hello/'
# We are also defining which type of requests this route is
# accepting: POST requests in this case
@app.route('/hello/', methods=['POST'])
def hello():
    parcheck=[]
    sencheck=[]
    slen={}
    wlen={}
    parsent=[]
    allwords=[]
    text=request.form['text']

    vervang={}
    for i in dict:
      if re.search('\W'+i+'\W', text) :
        vervang[i] = dict[i]
        text = re.sub(''+i+'', '<font color=#FF0000><b> '+i+' </b></font>', text)
      

    paragraphs = [s.strip() for s in text.split("\n")]
    count=0
    hline=""

    if len(paragraphs[0]) < 100 and len(paragraphs) > 1:
      hline=paragraphs.pop(0)

    for p in paragraphs:
      if len(p) > 3:
        #figure out how many sentences are allowed per par.
        if count==0:
          allowed=maxlead
        else:
          allowed=maxpar

        sencheck.append(True)
        sentences = splitSentences(p)
        if len(sentences) > allowed:
          parcheck.append(False)
        else:
          parcheck.append(True)
        for s in sentences:
            words = tokenize(s)
            slen[s]=len(words)
            if slen[s] > maxsent:
              sencheck[count]=False


            allwords.extend(words)
        parsent.append(sentences)
        count+=1


    randstring1=id_generator()
    randstring2=id_generator()
    drawGraph(slen.values(), randstring1, 'zinslengte')
    typetoken=getTTRatio(allwords)
    highfreq=getHighfreq(allwords)
    for w in allwords:
      if '<' not in w:
        wlen[w]=len(w)

    drawGraph(wlen.values(), randstring2, 'woordlengte')

    textlength=len(text)
    allsentences = splitSentences(text)

    return render_template('form_action.html', lead=parsent[0], text=parsent, slen=slen, sentname=randstring1, wordname=randstring2, ttr=typetoken, hfr=highfreq, textlength=textlength, amountwords=len(allwords),amountsentences=len(allsentences), hline=hline,maxsent=maxsent, parcheck=parcheck, sencheck=sencheck,vervang=vervang)

# Run the app :)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 33507))

    app.debug = True
    app.run(
        host="0.0.0.0",
        port=int(port)
  )
