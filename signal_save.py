#!/usr/bin/python3
# coding: utf8

import sqlite3
import argparse
from pdb import pm,set_trace
from datetime import datetime
from collections import OrderedDict
from CSS import *
from signal_structure import MMS, SMS, PART, SMS_SENT, SMS_RECV, SMS_NULL

def fetch_contact_msg(contact_address, db_cursor, thread_id):
  # MMS
  db_cursor.execute("select date, msg_box, body, part_count, quote_id, quote_body, reactions, part._id, part.ct, part.unique_id FROM MMS LEFT JOIN part ON part.mid = MMS._id WHERE thread_id={}".format(thread_id))
  msg = OrderedDict()
  for m in db_cursor.fetchall():
    mms = msg.get(m[0])
    if mms:
      mms.parts.append(PART(m[7],m[8],m[9]))
    else:
      msg[m[0]] = MMS(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9])

  db_cursor.execute("select thread_id, address, date_sent, type, body, reactions FROM sms where thread_id=={}".format(thread_id))
  for s in db_cursor.fetchall():
    if msg.get(s[2]):
      raise ValueError
    msg[s[2]] = SMS(s[0],s[1],s[2],s[3],s[4],s[5])

  return msg
  
def fetch_part_used(db_cursor):
  db_cursor.execute("select part._id, part.ct, part.unique_id FROM PART INNER JOIN mms ON part.mid = mms._id WHERE thread_id={}".format(thread_id))
  part = OrderedDict()
  for p in db_cursor.fetchall():
    part[p[0]] = PART(p[0],p[1],p[2])
  return part

def build_header():
  return HEAD + NAVBAR

def build_msg(contact_name, date, msg, filename=None, part_count=None, contact_quoted=None, quote=None, quote_date=None, quote_filename=None, reactions=None):
  if contact_name == CONTACT_NAME:
    offset = "offset-md-5"
    css = "mycontact"
  elif contact_name == MYSELF:
    offset = ""
    css = "myself"
  else:
    raise ValueError


  if reactions:
    reactions_css = REACTION_CSS.format(css=css,reactions=reactions)
  else:
    reactions_css = ''
  
  if quote_date:
    assert(quote is not None)
    assert(contact_quoted is not None)
    quote_date = datetime.fromtimestamp(int(quote_date)//1000)
    quote_filename_css = ''
    for p in quote_filename:
      if p.filename:
        quote_filename_css += FILENAME.format(filename=ATTACHMENT_DIR+p.filename)
      else:
        quote_filename_css = ''
    quote_css = QUOTE.format(contact_quoted = contact_quoted, quote = quote, quote_date = quote_date, css = css, quote_filename = quote_filename_css, offset = offset)

  else:
    quote_css = ''

  if filename and part_count > 0:
    filename_css = ''
    for p in filename:
      filename_css += FILENAME.format(filename=ATTACHMENT_DIR + p.filename)
  elif filename and msg == '':
    filename_css = FILENAME.format(filename=ATTACHMENT_DIR+filename[0].filename)
  else:
    filename_css = ''

  if msg == '' and not filename:
    return ''

  return TEMPLATE.format(contact_name = contact_name, date = date, quoted_msg = quote_css, msg_sent = msg, filename_sent = filename_css, css = css, offset = offset, reactions=reactions_css)


def build_footer():
  return  FOOTER

def test_css():
  html_result = open('test.html','w')
  html_result.write(build_header())
  
  html_result.write(build_msg(CONTACT_NAME, '1583604356792', "test toto", reaction="toto"))
  html_result.write(build_msg(MYSELF, '1583604356792', "test toto", reaction="tata"))
  
  html_result.write(build_msg(CONTACT_NAME, '1583604356792', "test toto", filename='flower.jpg'))
  html_result.write(build_msg(MYSELF, '1583604356792', "test toto", filename='flower.jpg'))
  
  html_result.write(build_msg(CONTACT_NAME, '1583604356792', "test toto", contact_quoted=MYSELF, quote="test toto", quote_date='1583604356792'))
  html_result.write(build_msg(MYSELF, '1583604356792', "test toto", contact_quoted=CONTACT_NAME, quote="test toto", quote_date='1583604356792'))
  
  html_result.write(build_msg(CONTACT_NAME, '1583604356792', "test toto", contact_quoted=MYSELF, filename='flower.jpg', quote="test toto" ,quote_date='1583604356792'))
  html_result.write(build_msg(MYSELF, '1583604356792', "test toto", contact_quoted=CONTACT_NAME, quote="test toto", filename='flower.jpg', quote_date='1583604356792'))
  
  html_result.write(build_footer())
  html_result.close()

def save_msg(output_file, msg_dict):

  html_result = open(output_file,'w')
  html_result.write(build_header())

  for msg_key, msgi in msg_dict.items():
    msg_date = datetime.fromtimestamp(msg_key//1000)

    if msgi.msg_type == SMS_RECV:
      if isinstance(msgi, SMS):
        html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, reactions=msgi.reactions))
      elif isinstance(msgi, MMS):
        quoted_msg = msg_dict.get(msgi.quote_id)
        if isinstance(quoted_msg, MMS) and quoted_msg.date in msg_dict.keys():
          html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, part_count=msgi.part_count, filename=msgi.parts, contact_quoted=MYSELF, quote_filename=quoted_msg.parts, quote= msgi.quote_body, quote_date=quoted_msg.date, reactions=msgi.reactions))
        else:
          html_result.write(build_msg(CONTACT_NAME, msg_date, msgi.body, part_count=msgi.part_count, filename=msgi.parts, reactions=msgi.reactions))

    elif msgi.msg_type == SMS_SENT:
      if isinstance(msgi, SMS):
        html_result.write(build_msg(MYSELF, msg_date, msgi.body, reactions=msgi.reactions))
      elif isinstance(msgi, MMS):
        quoted_msg = msg_dict.get(msgi.quote_id)
        if isinstance(quoted_msg, MMS) and quoted_msg.date in msg_dict.keys():
          html_result.write(build_msg(MYSELF, msg_date, msgi.body, part_count=msgi.part_count, filename=msgi.parts, contact_quoted=CONTACT_NAME, quote_filename=quoted_msg.parts, quote=msgi.quote_body, quote_date=quoted_msg.date, reactions=msgi.reactions))
        else:
          html_result.write(build_msg(MYSELF, msg_date, msgi.body, part_count=msgi.part_count, filename=msgi.parts, reactions=msgi.reactions))

    elif msgi.msg_type in SMS_NULL:
        pass
    else:
        raise ValueError(msgi.msg_type)
  
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

  CONTACT_NAME = args.contact_name
  MYSELF = args.your_name
  ATTACHMENT_DIR = args.attachment_dir+'/'
  
  conn = sqlite3.connect(args.db_path)
  db_cursor = conn.cursor()

  msg_dict = OrderedDict(sorted(fetch_contact_msg(args.contact_address, db_cursor, args.thread_id).items()))

  save_msg(args.html_output_file, msg_dict)
  test_css()



