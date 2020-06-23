from functools import total_ordering

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
