#!/usr/bin/python3
# coding: utf8

import sqlite3
import argparse
from pdb import pm,set_trace
from datetime import datetime
from collections import OrderedDict
from CSS import *
from signal_structure import MMS, SMS, PART, SMS_SENT, SMS_RECV, SMS_NULL

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

def build_msg(contact_name, date, msg, filename=None, contact_quoted=None, quote=None, quote_date=None, reaction=None):
  if contact_name == CONTACT_NAME:
    offset = "offset-md-5"
    css = "mycontact"
  elif contact_name == MYSELF:
    offset = ""
    css = "myself"
  else:
    raise ValueError

  if reaction:
    reaction = REACTION_CSS.format(css=css,reaction=reaction)
  else:
    reaction=''

  # MMS with IMG & QUOTE
  if filename and quote_date:
    assert(quote is not None)
    assert(contact_quoted is not None)
    quote_date = datetime.fromtimestamp(int(quote_date)//1000)
    return MMS_QUOTE_IMG.format(contact_name = contact_name, date = date, msg = msg, contact_quoted = contact_quoted, quote = quote, quote_date = quote_date, css = css, filename = filename, offset = offset, reaction=reaction)

  # MMS with QUOTE
  elif quote_date:
    quote_date = datetime.fromtimestamp(int(quote_date)//1000)
    return MMS_QUOTE.format(contact_name = contact_name, date = date, msg = msg, contact_quoted = contact_quoted, quote = quote, quote_date = quote_date, css = css, offset = offset, reaction=reaction) 
 
  # MMS with IMG
  elif filename:
    return MMS_IMG.format(contact_name = contact_name, date = date, msg = msg, filename = filename, css = css, offset = offset, reaction=reaction)

  # SMS
  else:
    return SMS_CSS.format(contact_name = contact_name, date = date, msg = msg, css = css, offset = offset, reaction=reaction)

def build_footer():
  return  FOOTER

### TEST ###
#html_result = open('gabrielle.html','w')
#html_result.write(build_header())
#
#html_result.write(build_msg(CONTACT_NAME, '1583604356792', "Je t'aime", reaction="toto"))
#html_result.write(build_msg(MYSELF, '1583604356792', "Je t'aime", reaction="tata"))
#
#html_result.write(build_msg(CONTACT_NAME, '1583604356792', "Je t'aime", filename='20200315_120238.jpg'))
#html_result.write(build_msg(MYSELF, '1583604356792', "Je t'aime", filename='20200315_120238.jpg'))
#
#html_result.write(build_msg(CONTACT_NAME, '1583604356792', "Je t'aime", contact_quoted=MYSELF, quote="Je t'aime", quote_date='1583604356792'))
#html_result.write(build_msg(MYSELF, '1583604356792', "Je t'aime", contact_quoted=CONTACT_NAME, quote="Je t'aime", quote_date='1583604356792'))
#
#html_result.write(build_msg(CONTACT_NAME, '1583604356792', "Je t'aime", contact_quoted=MYSELF, filename='20200315_120238.jpg', quote="Je t'aime" ,quote_date='1583604356792'))
#html_result.write(build_msg(MYSELF, '1583604356792', "Je t'aime", contact_quoted=CONTACT_NAME, quote="Je t'aime", filename='20200315_120238.jpg', quote_date='1583604356792'))
#
#html_result.write(build_footer())
#html_result.close()

def save_msg(output_file, msg_dict):

  html_result = open(output_file,'w')
  html_result.write(build_header())

  for msg_key, msgi in msg_dict.items():
    msg_date = datetime.fromtimestamp(msg_key//1000)
  
    if isinstance(msgi, SMS):
      if msgi.sms_type == SMS_RECV:
        html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, reaction=msgi.reactions))
      elif msgi.sms_type == SMS_SENT:
        html_result.write(build_msg(MYSELF, msg_date, msgi.body, reaction=msgi.reactions))
      elif msgi.sms_type in SMS_NULL:
        pass
      else:
        raise ValueError(msgi.sms_type)
  
    elif isinstance(msgi, MMS):
      # MMS recieved
      if msgi.mms_type == SMS_RECV:
        # MMS is quoting a msg
        if msgi.quote_id > 0:
          quoted_msg = msg_dict.get(msgi.quote_id)
          # MMS can quote an SMS
          if isinstance(quoted_msg, SMS):
            html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote=msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
          # MMS can quote an MMS
          elif isinstance(quoted_msg, MMS):
            # MMS quote an MMS with an image
            if quoted_msg.date in msg_dict.keys() and quoted_msg.filename is not None:
              html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, filename=ATTACHMENT_DIR + quoted_msg.filename, quote= msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
            # MMS quote an MMS without an image
            else:
              html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote=msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
          else:
            html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, contact_quoted=MYSELF, quote="NULL quote", quote_date=None, reaction=msgi.reactions))
        # MMS is embedding a simple MMS without quoting
        elif msgi.filename is not None:
          html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, filename=ATTACHMENT_DIR + msgi.filename, reaction=msgi.reactions))
        else:
          raise ValueError
  
      # MMS sent
      elif msgi.mms_type == SMS_SENT:
        # MMS is quoting a msg
        if msgi.quote_id > 0:
          quoted_msg = msg_dict.get(msgi.quote_id)
          # MMS can quote an SMS
          if isinstance(quoted_msg, SMS):
            html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote=msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
          # MMS can quote an MMS
          elif isinstance(quoted_msg, MMS):
            # MMS quote an MMS with an image
            if quoted_msg.date in msg_dict.keys() and quoted_msg.filename is not None:
              html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, filename=ATTACHMENT_DIR + quoted_msg.filename, quote= msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
            # MMS quote an MMS without an image
            else:
              html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote=msgi.quote_body, quote_date=quoted_msg.date, reaction=msgi.reactions))
          else:
            html_result.write(build_msg(MYSELF, msg_date, msgi.body, contact_quoted=CONTACT_NAME, quote="NULL quote", quote_date=None, reaction=msgi.reactions))
        # MMS is embedding a simple MMS without quoting
        elif msgi.filename is not None:
          html_result.write(build_msg(MYSELF, msg_date, msgi.body, filename=ATTACHMENT_DIR + msgi.filename, reaction=msgi.reactions))
        else:
          raise ValueError
  
      elif msgi.mms_type in SMS_NULL:
        pass
      else:
        raise ValueError(msgi)
    else:
      raise ValueError
  
  html_result.write(build_footer())
  html_result.close()

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--db", dest="db_path", help="Path to signal_backup.db file", type=str)
  parser.add_argument("--attachment", "-a", dest="attachment_dir", help="Path to attachment directory", type=str)
  parser.add_argument("--thread", "-t", dest="thread_id", help="Conversation ID, multiple conversion saving are not yet supported", type=int)
  parser.add_argument("--contact_addr", "-ca", dest="contact_address", help="Contact address, multiple conversion saving are not yet supported", type=int)
  parser.add_argument("--contact_name", "-cn", dest="contact_name", help="Name of the contact you wish to display", type=str)
  parser.add_argument("--you", "-m", dest="your_name", help="Your name", type=str)
  parser.add_argument("--out", "-o", dest="html_output_file", help="html output file", type=str)
  args = parser.parse_args()

  THREAD_ID = args.thread_id
  CONTACT_ADDRESS = args.contact_address
  CONTACT_NAME = args.contact_name
  MYSELF = args.your_name
  ATTACHMENT_DIR = args.attachment_dir
  DB_PATH = args.db_path
  HTML_OUT = args.html_output_file
  
  conn = sqlite3.connect(DB_PATH)
  db_cursor = conn.cursor()

  msg_dict = OrderedDict(sorted(fetch_contact_msg(CONTACT_ADDRESS, db_cursor).items()))

  save_msg(HTML_OUT, msg_dict)



