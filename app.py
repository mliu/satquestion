import urllib.request
from datetime import datetime, timedelta
from threading import Timer
from flask import Flask, render_template
import sendgrid
import requests

app = Flask(__name__)
app.config.from_object(__name__)

@app.route("/")
def index():
  return render_template('index.html')

sg = sendgrid.SendGridClient('michaelyliu', 'mliu95')

x = datetime.today()
y = (x+timedelta(days=1)).replace(hour=4, minute=0, second=0)
delta_t = y-x
secs = delta_t.seconds+1

def build_url(choice):
  return "http://sat.collegeboard.org/practice/sat-question-of-the-day?questionId=" + datetime.today().strftime("%Y%m%d") + "&answerCd=" + choice

def grab_snippet(choice, page):
  index1 = page.index('<label for="qotdChoices' + choice) + 26
  index2 = page[index1:].index('</label>') + index1
  return page[index1:index2]

def build_question():
  mlist = []
  emails = requests.get("https://sendgrid.com/api/newsletter/lists/email/get.json?api_user=michaelyliu&api_key=mliu95&list=SATList")
  for key in emails.json():
    mlist.append(key['email'])
  response = urllib.request.urlopen("http://sat.collegeboard.org/practice/sat-question-of-the-day").read()
  string = response.decode('utf-8') 
  index1 = string.index('<div class="questionStem">')
  index2 = string.index('<fieldset id="qotdChoicesFields"')
  f = open('email.html', 'r')
  template = f.read()
  template = template.format(day=datetime.today().strftime("%m-%d-%Y"), question=string[index1:index2], urlA=build_url("A"), snippetA=grab_snippet("A", string), urlB=build_url("B"), snippetB=grab_snippet("B", string), urlC=build_url("C"), snippetC=grab_snippet("C", string), urlD=build_url("D"), snippetD=grab_snippet("D", string), urlE=build_url("E"), snippetE=grab_snippet("E", string))
  print("Built question for " + str(datetime.today()))
  message = sendgrid.Mail()
  message.set_subject('The SAT Question of the Day')
  message.set_html(template)
  message.set_from('SatQuestion@satquestion.me')
  message.smtpapi.set_tos(mlist)
  status, msg = sg.send(message)
  print(status)
  x = datetime.today()
  y = (x+timedelta(days=1)).replace(hour=4, minute=0, second=0)
  delta_t = y-x
  secs = delta_t.seconds+1
  t = Timer(secs, build_question)
  t.start()
  print("Timer started for " + str(y))

t = Timer(secs, build_question)
t.start()

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8080)
