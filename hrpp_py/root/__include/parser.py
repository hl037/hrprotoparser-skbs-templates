class Parser(object):
  _max_size = 4096
      
  def __init__(self):
    self._type = 0
## if psize != 0:
    self._size = 0
    self._state = self._READ_SIZE
    self._remain = {{psize * 8 if psize else 64}}
## -
## else :
    self._state = self._READ_TYPE
    self._remain = {{tsize * 8 if tsize else 64}}
## -
    self._n_h_read = 0
  
  def parse(self, data):
    prev_state = self._state
    while data or prev_state != self._state:
      prev_state = self._state
      data = self._state(data)

  
  
## if psize != 0:
  def _READ_SIZE(self, data):
    offset = -1
    for offset, b in enumerate(data) :
##   if psize :
      self._size |= b << ({{psize * 8}} - self._remain)
      self._n_h_read += 1
      self._remain -= 8
      if self._remain <= 0 :
        break
##   -
##   else:
      self._size |= (b & 0b0111_1111) << (64 - self._remain)
      if b & 0b1000_0000 :
        self._n_h_read += 1
        offset += 1
        self._remain = 0
        break
      self._remain -= 7
##   -
    if self._remain == 0 :
      self._state = self._READ_TYPE
      self._remain = {{tsize * 8 if tsize else 64}};
    return data[offset + 1:]
## -

  def _READ_TYPE(self, data):
    offset = -1
    for offset, b in enumerate(data) :
##   if tsize :
      self._type |= b << ({{tsize * 8}} - self._remain)
      self._n_h_read += 1
      self._remain -= 8
      if self._remain <= 0 :
        break
##   -
##   else:
      self._type |= (b & 0b0111_1111) << (64 - self._remain)
      if b & 0b1000_0000 :
        self._n_h_read += 1
        offset += 1
        self._remain = 0
        break
      self._remain -= 7
##   -
    if self._remain == 0 :
      self._state = self._READ
##  if psize == 0:
      self._remain = packets[self._type].size - self._n_h_read
##  -
##  else:
      self._remain = self._size - self._n_h_read
##  -
      if self._max_size < self._remain :
        self._state = self._SKIP
      else:
        self._current_packet = []
    return data[offset + 1:]
    
    
  def _SKIP(self, data):
    if len(data) < self._remain :
      self._remain -= len(data)
      data = b''
    else:
      self._type = 0
      self._current_packet = None
## if psize != 0:
      self._size = 0
      self._state = self._READ_SIZE
      self._remain = {{psize * 8 if psize else 64}};
## -
## else:
      self._state = self._READ_TYPE
      self._remain = {{psize * 8 if psize else 64}};
## -
      self._n_h_read = 0
      data = data[:self._remain]

  def _READ(self, data):
    read = data[:self._remain]
    res = data[self._remain:]
    self._current_packet.append(read)
    self._remain -= len(read)
    if self._remain == 0:
      self._handle_packet()
      self._type = 0
      self._current_packet = None
## if psize != 0:
      self._size = 0
      self._state = self._READ_SIZE
      self._remain = {{psize * 8 if psize else 64}}
## -
## else:
      self._state = self._READ_TYPE
      self._remain = {{tsize * 8 if tsize else 64}}
## -
      self._n_h_read = 0
    return res
  
  def _handle_packet(self):
    p = packets[self._type]()
    p.data.decode(b''.join(self._current_packet))
    H = getattr(self, p._name)
    H(p)

  def default_handler(self, p):
    raise NotImplementedError()

## for s in _p.proto.P :
##   sname = _p.struct_name(s)
  def {{sname}}(self, p:{{sname}}):
    self.default_handler(p)

## -

