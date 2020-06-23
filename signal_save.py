#!/usr/bin/python3
# coding: utf8

import sqlite3
from functools import total_ordering
from pdb import pm,set_trace
from datetime import datetime
from collections import OrderedDict
from CSS import *

conn = sqlite3.connect('signal_backup.db')
db_cursor = conn.cursor()

THREAD_ID = 25
CONTACT_ADDRESS = 102
CONTACT_NAME = 'Gabrielle'
MYSELF = 'Florian'
PATH_ATTACHMENTS = './attachment/'

SMS_SENT = 10485783
SMS_RECV = 10485780

SMS_NULL = [10747924,10747927,2,1,3]

@total_ordering
class MMS(object):
  def __init__(self, date, mms_type, body, part_count, quote_id, quote_body, reactions, mms_id, part_ct, part_unique_id, part_width, part_height):
    self.date = date
    self.mms_type = mms_type
    self.body = body 
    self.part_count = part_count
    self.quote_id = quote_id
    self.quote_body = quote_body
    self.reactions = reactions

    self.part_ct = part_ct
    self.part_width = part_width
    self.part_height = part_height

    if part_unique_id is not None:
      assert(mms_id is not None)
      self.filename = str(part_unique_id) + "_" + str(mms_id)
    else:
      self.filename = None

  def __str__(self):
    return self.__repr__()

  def __eq__(self, other):
    return ((self.date,self.body) == (other.date,other.body))
  
  def __ne__(self, other):
    return not (self == other)
  
  def __lt__(self, other):
    return (self.date < other.date)
  
  def __repr__(self):
    return "date : {}, type : {}, body : {}, part_count : {}, quote_id : {}, quote_body : {}, reactions : {}, file : {}, ct : {},  width : {}, heigth : {}\n".format(self.date, self.mms_type, self.body, self.part_count, self.quote_id, self.quote_body, self.reactions, self.filename, self.part_ct, self.part_width, self.part_height)

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
    return self.__repr__()

def fetch_contact_msg(contact_address, db_cursor):
  # MMS
  db_cursor.execute("select date, msg_box, body, part_count, quote_id, quote_body, reactions, part._id, part.ct, part.unique_id, part.width, part.height FROM MMS LEFT JOIN part ON part.mid = MMS._id WHERE thread_id={}".format(THREAD_ID))
  msg = OrderedDict()
  for m in db_cursor.fetchall():
    msg[m[0]] = MMS(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10],m[11])

  db_cursor.execute("select thread_id, address, date_sent, type, body, reactions FROM sms where thread_id=={}".format(THREAD_ID))
  for s in db_cursor.fetchall():
    if msg.get(s[2]):
      raise ValueError
    msg[s[2]] = SMS(s[0],s[1],s[2],s[3],s[4],s[5])

  return msg
  
def fetch_part_used(db_cursor):
  db_cursor.execute("select part._id, part.ct, part.unique_id, part.width, part.height FROM PART INNER JOIN mms ON part.mid = mms._id WHERE thread_id={}".format(THREAD_ID))
  part = OrderedDict()
  for p in db_cursor.fetchall():
    part[p[0]] = PART(p[0],p[1],p[2],p[3],p[4])
  return part

def build_header():
  return HEAD + NAVBAR

def build_msg(contact_name, date, msg, filename=None, contact_quoted=None, quote=None, quote_date=None):
  if contact_name == CONTACT_NAME:
    offset = "offset-md-5"
    css = "mycontact"
  elif contact_name == MYSELF:
    offset = ""
    css = "myself"
  else:
    raise ValueError

  # MMS with IMG & QUOTE
  if filename and quote_date:
    assert(quote is not None)
    assert(contact_quoted is not None)
    return MMS_QUOTE_IMG.format(contact_name = contact_name, date = date, msg = msg, contact_quoted = contact_quoted, quote = quote, quote_date = quote_date, css = css, filename = filename, offset = offset)

  # MMS with QUOTE
  elif quote_date:
    return MMS_QUOTE.format(contact_name = contact_name, date = date, msg = msg, contact_quoted = contact_quoted, quote = quote, quote_date = quote_date, css = css, offset = offset) 
 
  # MMS with IMG
  elif filename:
    return MMS_IMG.format(contact_name = contact_name, date = date, msg = msg, filename = filename, css = css, offset = offset)

  # SMS
  else:
    return SMS_CSS.format(contact_name = contact_name, date = date, msg = msg, css = css, offset = offset)

def build_footer():
  return  FOOTER

msg = OrderedDict(sorted(fetch_contact_msg(CONTACT_ADDRESS, db_cursor).items()))

### TEST ###
html_result = open('gabrielle.html','w')
html_result.write(build_header())

html_result.write(build_msg(CONTACT_NAME, '01/01/1970', "Je t'aime"))
html_result.write(build_msg(MYSELF, '01/01/1970', "Je t'aime"))

html_result.write(build_msg(CONTACT_NAME, '01/01/1970', "Je t'aime", filename='20200315_120238.jpg'))
html_result.write(build_msg(MYSELF, '01/01/1970', "Je t'aime", filename='20200315_120238.jpg'))

html_result.write(build_msg(CONTACT_NAME, '01/01/1970', "Je t'aime", contact_quoted=MYSELF, quote="Je t'aime", quote_date='01/01/1970'))
html_result.write(build_msg(MYSELF, '01/01/1970', "Je t'aime", contact_quoted=CONTACT_NAME, quote="Je t'aime", quote_date='01/01/1970'))

html_result.write(build_msg(CONTACT_NAME, '01/01/1970', "Je t'aime", contact_quoted=MYSELF, filename='20200315_120238.jpg', quote="Je t'aime" ,quote_date='01/01/1970'))
html_result.write(build_msg(MYSELF, '01/01/1970', "Je t'aime", contact_quoted=CONTACT_NAME, quote="Je t'aime", filename='20200315_120238.jpg', quote_date='01/01/1970'))

html_result.write(build_footer())
html_result.close()

### TEST2 ###

html_result = open('test.html','w')
html_result.write(build_header())

for msg_key, msgi in msg.items():
  msg_date = datetime.fromtimestamp(msg_key//1000)

  if isinstance(msgi, SMS):
    if msgi.sms_type == SMS_RECV:
      html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body))
    elif msgi.sms_type == SMS_SENT:
      html_result.write(build_msg(MYSELF, msg_date, msgi.body))
    elif msgi.sms_type in SMS_NULL:
      pass
    else:
      raise ValueError(msgi.sms_type)

  elif isinstance(msgi, MMS):
    # MMS recieved
    if msgi.mms_type == SMS_RECV:
      # MMS is quoting a msg
      if msgi.quote_id > 0:
        quoted_msg = msg.get(msgi.quote_id)
        # MMS can quote an SMS
        if isinstance(quoted_msg, SMS):
          html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote=msgi.quote_body, quote_date=quoted_msg.date))
        # MMS can quote an MMS
        elif isinstance(quoted_msg, MMS):
          # MMS quote an MMS with an image
          if quoted_msg is msg.keys() and quoted_mms.filename is not None:
            html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, filename=PATH_ATTACHMENTS + quoted_msg.filename, quote= msgi.quote_body, quote_date=quoted_msg.date))
          # MMS quote an MMS without an image
          else:
            html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote=msgi.quote_body, quote_date=quoted_msg.date))
        else:
          html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote="NULL quote", quote_date="NULL"))
      # MMS is embedding a simple MMS without quoting
      elif msgi.filename is not None:
        html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, filename=PATH_ATTACHMENTS + msgi.filename))
      else:
        raise ValueError

    # MMS sent
    elif msgi.mms_type == SMS_SENT:
      # MMS is quoting a msg
      if msgi.quote_id > 0:
        quoted_msg = msg.get(msgi.quote_id)
        # MMS can quote an SMS
        if isinstance(quoted_msg, SMS):
          html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote=msgi.quote_body, quote_date=quoted_msg.date))
        # MMS can quote an MMS
        elif isinstance(quoted_msg, MMS):
          # MMS quote an MMS with an image
          if quoted_msg is msg.keys() and quoted_mms.filename is not None:
            html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, filename=PATH_ATTACHMENTS + quoted_msg.filename, quote= msgi.quote_body, quote_date=quoted_msg.date))
          # MMS quote an MMS without an image
          else:
            html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote=msgi.quote_body, quote_date=quoted_msg.date))
        else:
          html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote="NULL quote", quote_date="NULL"))
      # MMS is embedding a simple MMS without quoting
      elif msgi.filename is not None:
        html_result.write(build_msg(MYSELF, msg_date, msgi.body, filename=PATH_ATTACHMENTS + msgi.filename))
      else:
        raise ValueError

    elif msgi.mms_type in SMS_NULL:
      pass
    #else:
    #  raise ValueError(msgi)
  else:
    raise ValueError

html_result.write(build_footer())
html_result.close()


