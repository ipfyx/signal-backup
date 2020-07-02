#!/usr/bin/python3
# coding: utf8

import sqlite3
import argparse
from shutil import copy
from pathlib import Path
from pdb import pm,set_trace
from datetime import datetime
from collections import OrderedDict
from CSS import *
from signal_structure import MMS, SMS, PART, SMS_SENT, SMS_RECV, SMS_NULL

def fetch_contact_msg(contact_address, db_cursor, thread_id):
  # MMS
  db_cursor.execute("select date, msg_box, body, part_count, quote_id, quote_body, reactions, part._id, part.ct, part.unique_id, part.quote FROM MMS LEFT JOIN part ON part.mid = MMS._id WHERE thread_id={}".format(thread_id))
  msg = OrderedDict()
  for m in db_cursor.fetchall():
    mms = msg.get(m[0])
    if mms:
      mms.parts.append(PART(m[7],m[8],m[9],m[10]))
    else:
      msg[m[0]] = MMS(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10])

  db_cursor.execute("select thread_id, address, date_sent, type, body, reactions FROM sms where thread_id=={}".format(thread_id))
  for s in db_cursor.fetchall():
    if msg.get(s[2]):
      raise ValueError
    msg[s[2]] = SMS(s[0],s[1],s[2],s[3],s[4],s[5])

  return msg
  
def fetch_part_not_used(db_cursor, thread_id):
  db_cursor.execute("select part._id, part.ct, part.unique_id, part.quote FROM PART INNER JOIN mms ON part.mid = mms._id WHERE thread_id!={}".format(thread_id))
  parts = []
  for p in db_cursor.fetchall():
    parts.append(PART(p[0],p[1],p[2],p[3]))
  return parts

def build_header():
  return HEAD + NAVBAR

def build_footer():
  return  FOOTER

def build_msg(sender, reciever, msg):
  if sender == MYSELF:
    offset = "offset-md-5"
    css = "myself"
  elif sender == CONTACT_NAME:
    offset = ""
    css = "mycontact"
  else:
    raise ValueError

  msg_date = datetime.fromtimestamp(int(msg.date)//1000)

  reactions_css = ''
  if msg.reactions:
    reactions_css = REACTION_CSS.format(css=css, reactions=msg.reactions)
  
  quote_css = ''
  filename_css = ''
  if isinstance(msg, MMS): 
    if msg.quote_id:
      quoted_msg = msg_dict.get(msg.quote_id)
      assert(msg.quote_body is not None)
      if isinstance(quoted_msg, MMS) and quoted_msg.date in msg_dict.keys():
        quote_date = datetime.fromtimestamp(int(quoted_msg.date)//1000)
        quote_filename_css = ''
        for p in quoted_msg.parts:
          if p.filename and p.part_quote == 0:
            quote_filename_css += FILENAME.format(filename=ATTACHMENT_DIR+p.filename)
        quote_css = QUOTE.format(contact_quoted = reciever, quote = msg.quote_body, quote_date = quoted_msg.date, css = css, quote_filename = quote_filename_css, offset = offset)

    if msg.parts:
      for p in msg.parts:
        if p.part_quote == 0:
          filename_css += FILENAME.format(filename=ATTACHMENT_DIR + p.filename)

    if msg.body == '' and not msg.parts:
      return ''

  return TEMPLATE.format(contact_name = sender, date = msg_date, quoted_msg = quote_css, msg_sent = msg.body, filename_sent = filename_css, css = css, offset = offset, reactions=reactions_css)


def save_msg(output_dir, msg_dict):

  html_result = None
  cur_date = datetime.fromtimestamp(0)

  files = []

  for msg_key, msgi in msg_dict.items():
    msg_date = datetime.fromtimestamp(msg_key//1000)

    if msg_date.month > cur_date.month or msg_date.year > cur_date.year:
      cur_date = msg_date

      if html_result:
        html_result.write(build_footer())
        html_result.close()

      cur_date_filename = '{}.html'.format(datetime.strftime(cur_date,"%B-%Y"))
      files.append(cur_date_filename)
      html_result = open(output_dir + '/' + cur_date_filename, 'a')
      html_result.write(build_header())

    if msgi.msg_type == SMS_RECV:
      html_result.write(build_msg(sender = CONTACT_NAME, reciever = MYSELF, msg = msgi))
    elif msgi.msg_type == SMS_SENT:
      html_result.write(build_msg(sender = MYSELF, reciever = CONTACT_NAME, msg = msgi))
    elif msgi.msg_type in SMS_NULL:
        pass
    else:
        print(msgi)
  
  html_result.write(build_footer())
  html_result.close()
  generate_index(output_dir, files)

def generate_index(output_dir, files):
  html_result = open(output_dir + '/index.html', 'w')
  html_result.write(build_header())

  for link in files:
    html_result.write(INDEX.format(link=link))

  html_result.write(build_footer())
  html_result.close()

def remove_attachment(db_cursor, thread_id):

  unused = fetch_part_not_used(db_cursor, thread_id)
  for part in unused:
    file_to_remove = Path(ATTACHMENT_DIR + part.filename)
    print(file_to_remove)
    #file_to_remove.unlink()

def create_output_dir(output_dir):
  output_dir += "/"
  bootstrap_dir = "bootstrap/css/"
  bootstrap_css = "bootstrap.css"
  signal_css = "signal.css"

  try:
    Path(output_dir).mkdir(parents=True)
  except FileExistsError:
    raise FileExistsError("Output directory already exists, delete it or use another one.")

  Path(output_dir + 'attachment').symlink_to(Path(ATTACHMENT_DIR), target_is_directory=True)

  Path(output_dir + bootstrap_dir).mkdir(parents=True, exist_ok=True)
  copy(bootstrap_dir + bootstrap_css, output_dir + bootstrap_dir)
  copy(signal_css, output_dir + bootstrap_dir)

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--db", dest="db_path", help="Path to signal_backup.db file", type=str)
  parser.add_argument("--attachment", "-a", dest="attachment_dir", help="Path to attachment directory", type=str)
  parser.add_argument("--thread", "-t", dest="thread_id", help="Conversation ID, multiple conversion saving are not yet supported", type=int)
  parser.add_argument("--contact_addr", "-ca", dest="contact_address", help="Contact address, multiple conversion saving are not yet supported", type=int)
  parser.add_argument("--contact_name", "-cn", dest="contact_name", help="Name of the contact you wish to display", type=str)
  parser.add_argument("--you", "-m", dest="your_name", help="Your name", type=str)
  parser.add_argument("--output_dir", "-o", dest="html_output_dir", help="html output dir", type=str)
  args = parser.parse_args()

  CONTACT_NAME = args.contact_name
  MYSELF = args.your_name
  ATTACHMENT_DIR = args.attachment_dir+'/'
  
  conn = sqlite3.connect(args.db_path)
  db_cursor = conn.cursor()

  create_output_dir(args.html_output_dir)

  msg_dict = OrderedDict(sorted(fetch_contact_msg(args.contact_address, db_cursor, args.thread_id).items()))

  save_msg(args.html_output_dir, msg_dict)
  remove_attachment(db_cursor, args.thread_id)
