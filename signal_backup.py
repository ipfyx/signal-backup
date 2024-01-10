#!/usr/bin/python3
# coding: utf8

import sys
import sqlite3
import argparse
from shutil import copy, move
from pathlib import Path
from datetime import datetime
from collections import OrderedDict
from CSS import *
from signal_structure import *

def fetch_contact_msg(db_cursor, thread_id):
  # MMS
  db_cursor.execute("select date, address, msg_box, body, quote_id, quote_author, quote_body, reactions, part._id, part.ct, part.unique_id, part.quote FROM MMS LEFT JOIN part ON part.mid = MMS._id WHERE thread_id = ?", (thread_id,))
  msg = OrderedDict()
  for m in db_cursor.fetchall():
    mms = msg.get(m[0])
    if mms:
      mms.parts.append(PART(m[8],m[9],m[10],m[11]))
    elif m[4] != None:
      msg[m[0]] = MMS(m[0],m[1],m[2],m[3],m[4],m[5],m[6],m[7],m[8],m[9],m[10],m[11])
    else:
      print(m)

  db_cursor.execute("select thread_id, address, date_sent, type, body, reactions FROM sms where thread_id = ?", (thread_id,))
  for s in db_cursor.fetchall():
    msg[s[2]] = SMS(s[0],s[1],s[2],s[3],s[4],s[5])

  return msg

def fetch_part_not_used(db_cursor, thread_ids):
  param = '(?' + ',?'*(len(thread_ids)-1) + ')'
  request = "select part._id, part.ct, part.unique_id, part.quote FROM PART INNER JOIN mms ON part.mid = mms._id WHERE thread_id not in {}".format(param)
  db_cursor.execute(request, thread_ids)
  parts = []
  for p in db_cursor.fetchall():
    parts.append(PART(p[0],p[1],p[2],p[3]))
  return parts

def fetch_part_used(db_cursor, thread_id):
  db_cursor.execute("select part._id, part.ct, part.unique_id, part.quote FROM PART INNER JOIN mms ON part.mid = mms._id WHERE thread_id = ?",(thread_id,))
  parts = []
  for p in db_cursor.fetchall():
    parts.append(PART(p[0],p[1],p[2],p[3]))
  return parts

def fetch_contact(db_cursor, contact_name=None, _id=None):
  if _id:
    db_cursor.execute("SELECT recipient._id, recipient.phone, recipient.color, recipient.signal_profile_name, thread._id FROM recipient LEFT JOIN thread ON recipient._id = thread.thread_recipient_id WHERE recipient._id = ?", (_id,))
  elif contact_name:
    db_cursor.execute("SELECT recipient._id, recipient.phone, recipient.color, recipient.signal_profile_name, thread._id FROM recipient LEFT JOIN thread ON recipient._id = thread.thread_recipient_id WHERE recipient.signal_profile_name = ?", (contact_name,))
  else:
    raise ValueError(f"{colors.FAIL}Please specify a name or an id")

  contact = db_cursor.fetchone()
  if contact:
    return CONTACT(contact[0], contact[1], contact[2], contact[3], contact[4])
  else:

    # Possible contacts names
    print(f"{colors.WARNING} Possible contacts names")
    db_cursor.execute("SELECT recipient._id, recipient.phone, recipient.color, recipient.signal_profile_name, thread._id FROM recipient LEFT JOIN thread ON recipient._id = thread.thread_recipient_id")
    contacts = db_cursor.fetchall()
    for contact in contacts:
      contact = CONTACT(contact[0], contact[1], contact[2], contact[3], contact[4])
      if contact.name:
        print(f"{colors.INFO}{contact.name}")

    # Possible groups names
    print(f"{colors.WARNING} Possible groups names")
    db_cursor.execute("SELECT groups._id, groups.title, groups.members, groups.recipient_id, thread._id FROM groups LEFT JOIN thread ON groups.recipient_id = thread.thread_recipient_id")

    groups = db_cursor.fetchall()
    for group in groups:
      group = GROUP(group[0], group[1], group[2], group[3], group[4])
      if group.name:
        print(f"{colors.INFO}{group.name}")

    raise ValueError(f"{colors.FAIL}{contact_name} was not found in db, possible values above")

def fetch_group(db_cursor, group_name=None, _id=None):
  if group_name:
    db_cursor.execute("SELECT groups._id, groups.title, groups.members, groups.recipient_id, thread._id FROM groups LEFT JOIN thread ON groups.recipient_id = thread.thread_recipient_id WHERE groups.title = ?", (group_name,))
  elif _id:
    db_cursor.execute("SELECT groups._id, groups.title, groups.members, groups.recipient_id, thread._id FROM groups LEFT JOIN thread ON groups.recipient_id = thread.thread_recipient_id WHERE groups._id = ?", (_id,))
  else:
    raise ValueError(f"{colors.FAIL}Please specify a name or an id")

  group = db_cursor.fetchone()
  if group:
    return GROUP(group[0], group[1], group[2], group[3], group[4])
  else:
    return

def get_contact(db_cursor, conv_name):
  contact = fetch_group(db_cursor, conv_name)
  if not contact:
    # contact is a simple person
    contact = fetch_contact(db_cursor, conv_name)
  return contact

def build_header():
  return HEAD + NAVBAR

def build_footer():
  return  FOOTER

def build_msg(sender, reciever, msg, msg_dict):
  if sender == MYSELF.id:
    offset = "offset-md-5"
    css = "myself"
  else:
    offset = ""
    css = "mycontact"

  sender = CONTACT_DICT[sender].name

  msg_date = datetime.fromtimestamp(int(msg.date)//1000).strftime(DATE_FORMAT)

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
        quote_date = datetime.fromtimestamp(int(quoted_msg.date)//1000).strftime(DATE_FORMAT)
        quote_filename_css = ''
        for p in quoted_msg.parts:
          if p.filename and p.part_quote == 0:
            quote_filename_css += FILENAME.format(filename=ATTACHMENT_DIR+add_file_extension(p))
        contact_quoted = CONTACT_DICT[msg.quote_author].name
        quote_css = QUOTE.format(contact_quoted = contact_quoted, quote = msg.quote_body, quote_date = quote_date, css = css, quote_filename = quote_filename_css, offset = offset)

    if msg.parts:
      for p in msg.parts:
        if p.part_quote == 0:
          filename_css += FILENAME.format(filename=ATTACHMENT_DIR + add_file_extension(p))

    if msg.body == '' and not msg.parts:
      return ''

  return TEMPLATE.format(contact_name = sender, date = msg_date, quoted_msg = quote_css, msg_sent = msg.body, filename_sent = filename_css, css = css, offset = offset, reactions=reactions_css)


def backup_msg(output_dir, db_cursor, your_name, conv_name):

  class STATS(object):
    def __init__(self, sender, reciever, nbr_sent=0, nbr_recv=0):
      self.sender = sender
      self.reciever = reciever
      self.nbr_sent = nbr_sent
      self.nbr_recv = nbr_recv

  contact = get_contact(db_cursor, conv_name)
  if isinstance(contact, GROUP):
    for id_contact in contact.members:
      CONTACT_DICT[id_contact] = fetch_contact(db_cursor, _id = id_contact)

  if not contact:
    raise ValueError(f"{colors.FAIL}{conv_name} conversation does not exists")

  CONTACT_DICT[contact.id] = contact

  msg_dict = OrderedDict(sorted(fetch_contact_msg(db_cursor, contact.thread_id).items()))
  if not msg_dict:
    print(f"{colors.WARNING}Nothing to backup")
    return

  html_result = None
  cur_date = datetime.fromtimestamp(0)

  months = {}

  for msg_key, msgi in msg_dict.items():
    msg_date = datetime.fromtimestamp(msg_key//1000)

    if msg_date.month > cur_date.month or msg_date.year > cur_date.year:
      cur_date = msg_date

      if html_result:
        html_result.write(build_footer())
        html_result.close()

      cur_date_filename = '{}'.format(datetime.strftime(cur_date,"%B-%Y"))
      months[cur_date_filename] = STATS(your_name, contact.name)
      html_result = open("{}/{}.html".format(output_dir, cur_date_filename), 'a')
      html_result.write(build_header())

    if msgi.msg_type == SMS_RECV:
      html_result.write(build_msg(sender = msgi.address, reciever = MYSELF.id, msg = msgi, msg_dict = msg_dict))
      months[cur_date_filename].nbr_recv += 1
    elif msgi.msg_type == SMS_SENT:
      html_result.write(build_msg(sender = MYSELF.id, reciever = msgi.address, msg = msgi, msg_dict = msg_dict))
      months[cur_date_filename].nbr_sent += 1
    elif msgi.msg_type in SMS_NULL:
        pass
    else:
        pass

  html_result.write(build_footer())
  html_result.close()
  generate_index(output_dir, months)

def generate_index(output_dir, months):
  html_result = open(output_dir + '/index.html', 'w')
  html_result.write(build_header())
  total_sent = 0
  total_recv = 0

  for month, stats in months.items():
    html_result.write(INDEX.format(link=month, sender=stats.sender, reciever = stats.reciever, msg_sent=stats.nbr_sent, msg_recv=stats.nbr_recv))
    total_sent += stats.nbr_sent
    total_recv += stats.nbr_recv

  html_result.write(TOTAL.format(total_sent=total_sent, total_recv=total_recv))

  html_result.write(build_footer())
  html_result.close()

def add_file_extension(part):
  if part.ct == "image/gif":
      ext = ".gif"
  elif part.ct == "application/pdf":
    ext = ".pdf"
  elif part.ct == "image/webp":
    ext = ".webp"
    if not Path(ATTACHMENT_DIR + part.filename + ext).is_file():
      ext = ".png"
  elif part.ct == "image/png":
    ext = ".png"
  elif part.ct == "video/mp4":
    ext = ".mp4"
  elif part.ct == "audio/mpeg":
    ext = ".mp3"
  elif part.ct == "image/jpeg":
    ext = ".jpg"
  elif part.ct == "image/x-icon":
    ext = ".ico"
  elif part.ct == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
    ext = ".docx"
  else:
    print(f"{colors.WARNING}File not found. Unknown file type {part.ct} for attachment {part.filename}")
    ext = ""
  return part.filename + ext


def move_attachment(db_cursor, output_dir, conv_name):

  contact = get_contact(db_cursor, conv_name)

  used = fetch_part_used(db_cursor, contact.thread_id)
  for part in used:
    sys.stdout.write("Copying {}/{} attachments\r".format(used.index(part),len(used)-1))

    file_to_move = ATTACHMENT_DIR + add_file_extension(part)
    att_out = output_dir + ATTACHMENT_DIR
    try:
      copy(file_to_move, att_out)
    except FileNotFoundError:
      print(f"{colors.WARNING}Failed fo move {file_to_move} because it does not exist")
    finally:
      sys.stdout.flush()
  print(f"{colors.OK}{len(used)} attachments successfuly copied\r")

def create_output_dir(output_dir):
  bootstrap_dir = "bootstrap/css/"
  bootstrap_css = "bootstrap.css"
  signal_css = "signal.css"

  try:
    Path(output_dir).mkdir(parents=True)
  except FileExistsError:
    raise FileExistsError(f"{colors.FAIL}Output directory already exists, delete it or use another one.")

  Path(output_dir + ATTACHMENT_DIR).mkdir(parents=True, exist_ok=True)

  Path(output_dir + bootstrap_dir).mkdir(parents=True, exist_ok=True)
  copy(bootstrap_dir + bootstrap_css, output_dir + bootstrap_dir)
  copy(signal_css, output_dir + bootstrap_dir)

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument("--db", dest="db_path", help="Path to signal_backup.db file", type=str)
  parser.add_argument("--attachment", "-a", dest="attachment_dir", help="Path to attachment directory", type=str)
  parser.add_argument("--conv_name", "-cn", nargs='+', dest="conv_name", help="Name of the conversation you wish to display")
  parser.add_argument("--yourself", "-y", dest="your_name", help="Your name", type=str)
  parser.add_argument("--output_dir", "-o", dest="html_output_dir", help="html output dir", type=str)
  args = parser.parse_args()

  ATTACHMENT_DIR = args.attachment_dir+'/'

  conn = sqlite3.connect(args.db_path)
  db_cursor = conn.cursor()

  CONTACT_DICT = {}
  MYSELF = get_contact(db_cursor,args.your_name)
  CONTACT_DICT[MYSELF.id] = MYSELF

  for conv in args.conv_name:
    output_dir = "{}/{}/".format(args.html_output_dir, conv)
    print(f"{colors.INFO}Creating outpur directory {output_dir}")
    create_output_dir(output_dir)
    print(f"{colors.INFO}Saving conversation {conv}")
    backup_msg(output_dir, db_cursor, args.your_name, conv_name = conv)
    print(f"{colors.INFO}Copying attachment to {output_dir}/{conv}")
    move_attachment(db_cursor, output_dir, conv)
    print(f"{colors.OK}Conversation {conv} successfuly saved")
