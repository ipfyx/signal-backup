from functools import total_ordering

SMS_SENT = 10485783
SMS_RECV = 10485780

SMS_NULL = [10747924,10747927,2,1,3]


@total_ordering
class MMS(object):
  def __init__(self, date, msg_type, body, part_count, quote_id, quote_body, reactions, mms_id, part_ct, part_unique_id, part_quote):
    self.date = date
    self.msg_type = msg_type
    self.body = body
    self.part_count = part_count
    self.quote_id = quote_id
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
    return "date : {}, type : {}, body : {}, part_count : {}, quote_id : {}, quote_body : {}, reactions : {}, parts : {}\n".format(self.date, self.msg_type, self.body, self.part_count, self.quote_id, self.quote_body, self.reactions, self.parts)

@total_ordering
class SMS(object):
  def __init__(self, thread_id, address, date, msg_type, body, reactions):
    self.date = date
    self.body = body 
    self.msg_type = msg_type
    self.thread_id = thread_id
    self.address = address
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
    self.id_part = id_part 
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
