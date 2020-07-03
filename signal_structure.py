from functools import total_ordering

SMS_SENT = 10485783
SMS_RECV = 10485780

SMS_NULL = [10747924,10747927,2,1,3]


@total_ordering
class MMS(object):
  def __init__(self, date, address, msg_type, body, quote_id, quote_author, quote_body, reactions, mms_id, part_ct, part_unique_id, part_quote):
    self.date = int(date)
    self.address = int(address)
    self.msg_type = int(msg_type)
    if body:
      self.body = body
    else:
      self.body = ''
    self.quote_id = int(quote_id)
    self.quote_author = int(quote_author) if quote_author is not None else None
    self.quote_body = quote_body
    if reactions:
      self.reactions = reactions[:11].decode('utf-8')[4]
      if self.reactions == '❤':
        self.reactions = '❤️'
    else:
      self.reactions = reactions

    if part_unique_id:
      self.parts = [PART(mms_id, part_ct, part_unique_id, part_quote)]
    else:
      self.parts = []

  def __str__(self):
    return self.__repr__()

  def __eq__(self, other):
    return ((self.date,self.body) == (other.date,other.body))
  
  def __ne__(self, other):
    return not (self == other)
  
  def __lt__(self, other):
    return (self.date < other.date)
  
  def __repr__(self):
    return "date : {}, address : {}, type : {}, body : {}, quote_id : {}, quote_author : {} quote_body : {}, reactions : {}, parts : {}\n".format(self.date, self.address, self.msg_type, self.body, self.quote_id, self.quote_author, self.quote_body, self.reactions, self.parts)

@total_ordering
class SMS(object):
  def __init__(self, thread_id, address, date, msg_type, body, reactions):
    self.date = int(date)
    self.body = body 
    self.msg_type = int(msg_type)
    self.thread_id = int(thread_id)
    self.address = int(address)
    if reactions:
      self.reactions = reactions[:11].decode('utf-8')[4]
      if self.reactions == '❤':
        self.reactions = '❤️'
    else:
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
    return "date : {}, type : {}, body : {}, thread_id : {}, address : {}, reactions : {}\n".format(self.date, self.msg_type, self.body, self.thread_id, self.address, self.reactions)

class PART(object):
  def __init__(self, id_part, ct, unique_id, part_quote):
    self.id_part = int(id_part)
    self.ct = ct 
    self.unique_id = unique_id

    # 1 if the part is already included in the quote
    # else 0
    self.part_quote = part_quote

    if unique_id is not None:
      assert(id_part is not None)
      self.filename = str(unique_id) + "_" + str(id_part)
    else:
      self.filename = None

  def __repr__(self):
    return "id : {}, filename : {}, ct : {}, unique_id : {}".format(self.id_part, self.filename, self.ct, self.unique_id)

  def __str__(self):
    return self.__repr__()

class CONTACT(object):
  def __init__(self, _id, phone, color, name, thread_id):
    self.id = int(_id)
    self.name = name
    self.phone = phone
    self.color = color
    self.thread_id = int(thread_id)

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    return "id : {}, name : {}, color : {}, phone : {}, thread_id : {}".format(self.id, self.name, self.color, self.phone, self.thread_id)

class GROUP(object):
  def __init__(self, _id, name, members, contact_id, thread_id):
    self.id = int(_id)
    self.name = name
    self.members = [int(m) for m in members.split(',')]
    self.thread_id = int(contact_id)
    self.thread_id = int(thread_id)

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    return "id : {}, name : {}, contact_id : {}, thread_id : {}".format(self.id, self.name, self.contact_id, self.thread_id)
