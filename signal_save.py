#!/usr/bin/python3
# coding: utf8

import sqlite3
from functools import total_ordering
from pdb import pm
from datetime import datetime

conn = sqlite3.connect('signal_backup.db')
db_cursor = conn.cursor()

THREAD_ID = 25
contact_address = 102
CONTACT_NAME = 'Gabrielle'
MYSELF = 'Florian'

SMS_SENT = 10485783
SMS_REC = 10485780

@total_ordering
class MMS(object):
  def __init__(self, date, mms_type, body, part_count, quote_id, quote_body, reactions):
    self.date = date
    self.mms_type = mms_type
    self.body = body 
    self.part_count = part_count
    self.quote_id = quote_id
    self.quote_body = quote_body
    self.reactions = reactions

  def __str__(self):
    return self.__repr__()

  def __eq__(self, other):
    return ((self.date,self.body) == (other.date,other.body))
  
  def __ne__(self, other):
    return not (self == other)
  
  def __lt__(self, other):
    return (self.date < other.date)
  
  def __repr__(self):
    return "date : {}, type : {}, body : {}, part_count : {}, quote_id : {}, quote_body : {}, reactions : {}\n".format(self.date, self.mms_type, self.body, self.part_count, self.quote_id, self.quote_body, self.reactions)

@total_ordering
class SMS(object):
  def __init__(self, thread_id, address, date, sms_type, body, reactions):
    self.date = date
    self.body = body 
    self.sms_type = sms_type
    self.thread_id = thread_id
    self.address = address
    self.reactions = reactions

  def __str__(self):
    return self.__repr__()

  def __eq__(self, other):
    return ((self.date,self.body) == (other.date,other.body))
  
  def __ne__(self, other):
    return not (self == other)
  
  def __lt__(self, other):
    return (self.date < other.date)
  
  def __repr__(self):
    return "date : {}, type : {}, body : {}, thread_id : {}, address : {}, reactions : {}\n".format(self.date, self.sms_type, self.body, self.thread_id, self.address, self.reactions)

class PART(object):
  def __init__(self, id_part, ct, unique_id, width, height):
    self.id_part = id_part 
    self.ct = ct 
    self.unique_id = unique_id
    self.width = width
    self.height = height 
    self.filename = str(unique_id) + '_' + str(id_part)

  def __repr__(self):
    return "id : {}, filename : {}, ct : {}, unique_id : {}, width : {}, height : {}".format(self.id_part, self.filename, self.ct, self.unique_id, self.width, self.height)

  def __str__(self):
    return "id : {}, filename : {}, ct : {}, unique_id : {}, width : {}, height : {}".format(self.id_part, self.filename, self.ct, self.unique_id, self.width, self.height)

def fetch_contact_msg(contact_address, db_cursor):
  # MMS
  #db_cursor.execute("select date,msg_box,body,part_count,quote_id,quote_body,reactions FROM MMS where thread_id=={}".format(thread_id))
  db_cursor.execute("select date, msg_box, body, part_count, quote_id, quote_body, reactions, part._id, part.ct, part.unique_id, part.width, part.height FROM MMS LEFT JOIN part ON part.mid = MMS._id WHERE thread_id={}".format(THREAD_ID))
  mms = []
  for m in db_cursor.fetchall():
    mms.append(MMS(m[0],m[1],m[2],m[3],m[4],m[5],m[6]))
  
  db_cursor.execute("select thread_id, address, date, type, body, reactions FROM sms where thread_id=={}".format(THREAD_ID))
  sms = []
  for s in db_cursor.fetchall():
    sms.append(SMS(s[0],s[1],s[2],s[3],s[4],s[5]))

  return mms, sms
  
def fetch_part(db_cursor):
  db_cursor.execute("select _id, ct, unique_id, width, height FROM part")
  part = []
  for p in db_cursor.fetchall():
    part.append(PART(p[0],p[1],p[2],p[3],p[4]))
  return part

def build_header():
  head = """
  <!DOCTYPE html>
  <html>
    <head>
      <link href="bootstrap-4.4.1-dist/css/bootstrap.css" rel="stylesheet">
      <link href="signal.css" rel="stylesheet">
    </head>
    <body>
  """
  navbar = """
    <div class="container">
  
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">Navbar</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      </nav>
  """
  return head + navbar

def build_sms(contact_name, date, css="mycontact" , msg="", offset=""):
  if contact_name == CONTACT_NAME:
    offset = "offset-md-5"
    css = "mycontact"
  elif contact_name == MYSELF:
    css = "myself"
  else:
    raise ValueError

  row = """
        <section class="row">
          <div class="col-md-6 msg_{css} {offset}">
          <div class="col-md-12 name_{css}">
            {contact_name} - {date}
          </div>
          {msg}
          </div>
        </section>
  """.format(contact_name = contact_name, date = date, msg = msg, css = css, offset = offset)
  return row

def build_mms_with_img(contact_name, date, img_path, css="mycontact", msg="", offset=""):
  if contact_name == CONTACT_NAME:
      offset = "offset-md-5"
      css = "mycontact"
  elif contact_name == MYSELF:
    css = "myself"
  else:
    raise ValueError

  row = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
          {contact_name} - {date}
        </div>
          <a href="{img_path}">
          <img src="{img_path}">
          </a>
        {msg}
        </div>
      </section>
  """.format(contact_name = contact_name, date = date, msg = msg, img_path = img_path, css = css, offset = offset)
  return row

def build_mms_with_quote(contact_name, date, contact_name_quote, css="mycontact", quote="", msg="", offset=""):
  if contact_name == CONTACT_NAME:
      offset = "offset-md-5"
      css = "mycontact"
  elif contact_name == MYSELF:
    css = "myself"
  else:
    raise ValueError

  row = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
	{contact_name}
        </div>
        <div class="col-md-12 name_{css}">
	{contact_name_quote}
        <div class="col-md-12 quote_{css}">
        {quote}
        </div>
        </div>
	{msg}
        </div>
      </section>
  """.format(contact_name = contact_name, date = date, msg = msg, contact_name_quote = contact_name_quote, quote = quote, css = css, offset = offset)
  return row

def build_mms_with_quote_and_img(contact_name, date, contact_name_quote, img_path, css="mycontact", quote="", msg="", offset=""):
  if contact_name == CONTACT_NAME:
        offset = "offset-md-5"
        css = "mycontact"
  elif contact_name == MYSELF:
    css = "myself"
  else:
    raise ValueError

  row = """
      <section class="row">
        <div class="col-md-6 msg_{css} {offset}">
        <div class="col-md-12 name_{css}">
	{contact_name}
        </div>
        <div class="col-md-12 name_{css}">
	{contact_name_quote}
        <div class="col-md-12 quote_{css}">
        <a href="{img_path}">
          <img src="{img_path}">
        </a>
        {quote}
        </div>
        </div>
	{msg}
        </div>
      </section>
  """.format(contact_name = contact_name, date = date, msg = msg, contact_name_quote = contact_name_quote, quote = quote, css = css, img_path = img_path, offset = offset)
  return row

def build_footer():
  return """
    </body>
  </html>
  """

mms, sms = fetch_contact_msg(contact_address, db_cursor)
part = fetch_part(db_cursor)
print(mms)
#print(part)

### TEST ###
html_result = open('gabrielle.html','w')
html_result.write(build_header())

html_result.write(build_sms(CONTACT_NAME, '01/01/1970', msg="Je t'aime"))
html_result.write(build_sms(MYSELF, '01/01/1970', msg="Je t'aime"))

html_result.write(build_mms_with_img(CONTACT_NAME, '01/01/1970', '20200315_120238.jpg', msg="Je t'aime"))
html_result.write(build_mms_with_img(MYSELF, '01/01/1970', '20200315_120238.jpg', msg="Je t'aime"))

html_result.write(build_mms_with_quote(CONTACT_NAME, '01/01/1970', MYSELF, quote="Je t'aime", msg="Je t'aime",))
html_result.write(build_mms_with_quote(MYSELF, '01/01/1970', CONTACT_NAME, quote="Je t'aime", msg="Je t'aime"))

html_result.write(build_mms_with_quote_and_img(CONTACT_NAME, '01/01/1970', MYSELF, '20200315_120238.jpg', quote="Je t'aime", msg="Je t'aime"))
html_result.write(build_mms_with_quote_and_img(MYSELF, '01/01/1970', CONTACT_NAME, '20200315_120238.jpg', quote="Je t'aime", msg="Je t'aime"))

html_result.write(build_footer())
html_result.close()

### TEST2 ###

html_result = open('test.html','w')
html_result.write(build_header())

#for smsi in sms:
#  sms_date = datetime.fromtimestamp(smsi.date//1000)
#  if smsi.sms_type == SMS_REC:
#    html_result.write(build_sms(CONTACT_NAME, sms_date, msg=smsi.body))
#  elif smsi.sms_type == SMS_SENT:
#    html_result.write(build_sms(MYSELF, sms_date, msg=smsi.body))
#  elif smsi.sms_type == 2097684:
#    pass
#  else:
#    print(smsi)
#    #raise ValueError

# MMS
# self.date = date
# self.body = body 
# self.part_count = part_count
# self.quote_id = quote_id
# self.quote_body = quote_body
# self.reactions = reactions

for mmsi in mms:
  mms_date = datetime.fromtimestamp(mmsi.date//1000)
  if mmsi.mms_type == SMS_REC:
    if mmsi.part_count == 1:
      #assert(mmsi.quote_id > 0)
      print(mmsi.quote_id)
      html_result.write(build_mms_with_img(CONTACT_NAME, mms_date, 'file', msg=mmsi.body))

  elif mmsi.mms_type == SMS_SENT:
    pass
  else:
    print(mmsi)
    #raise ValueError

#html_result.write(build_mms_with_img(CONTACT_NAME, '01/01/1970', '20200315_120238.jpg', msg="Je t'aime"))
#html_result.write(build_mms_with_img(MYSELF, '01/01/1970', '20200315_120238.jpg', msg="Je t'aime"))

#html_result.write(build_mms_with_quote(CONTACT_NAME, '01/01/1970', MYSELF, quote="Je t'aime", msg="Je t'aime",))
#html_result.write(build_mms_with_quote(MYSELF, '01/01/1970', CONTACT_NAME, quote="Je t'aime", msg="Je t'aime"))
#html_result.write(build_mms_with_quote_and_img(CONTACT_NAME, '01/01/1970', MYSELF, '20200315_120238.jpg', quote="Je t'aime", msg="Je t'aime"))
#html_result.write(build_mms_with_quote_and_img(MYSELF, '01/01/1970', CONTACT_NAME, '20200315_120238.jpg', quote="Je t'aime", msg="Je t'aime"))



html_result.write(build_footer())
html_result.close()


