//# new_path = dest.with_name(_p.prefix + dest.name)
//#
//# from itertools import chain
//#
//# if 'PSIZE' in _p.proto.F and 'TSIZE' in _p.proto.F:
//#    psize = int(_p.proto.F['PSIZE'].val)
//#    tsize = int(_p.proto.F['TSIZE'].val)
//#    if psize < 0 :
//#      psize = None
//#    -
//#    if tsize < 0 :
//#      tsize = None
//#    -
//# -
//# else:
//#   #Legacy code
//#   import warnings
//#   warnings.warn('PSIZE and TSIZE flags should be defined in the protocol', FutureWarning)
//#   if int(_p.proto.F['FIXEDTSIZE'].val):
//#      tsize = int(_p.proto.F['FIXEDTSIZE'].val)
//#   -
//#   else:
//#      tsize = 0
//#   -
//#   if int(_p.proto.F['FIXEDSIZE'].val):
//#      psize = int(_p.proto.F['FIXEDSIZE'].val)
//#   -
//#   elif _p.bool(_p.proto.F['VARSIZE'].val):
//#      psize = None
//#   -
//#   else:
//#      psize = 0
//#   -
//# -

#include "{{_p.prefix}}protocol.h"

#include <stdlib.h>

//# if _p.parser :

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void _{{_p.prefix}}hrp_server_after_read({{_p.prefix}}hrp_t * _this);

void {{_p.prefix}}hrp_server_handle_packet({{_p.prefix}}hrp_t * _this){
//# if _p.single_handler :
  _this->handler(&_this->current_packet);
//# -
//# else:
  switch(_this->current_packet->header.type){
//#   for p in _p.proto.P:
//#     sname = _p.struct_name(p)
    case {{p.type.val}}:
      _this->handler.{{sname}}(({{sname}}_t*) _this->current_packet);
      break;
//#   -
//# -
  }
  {{_p.prefix}}hrp_pfree(_this->current_packet);
}

//# -

size_t {{_p.prefix}}hrp_packet_size({{_p.prefix}}hrp_ptype_t type){
  switch(type){
//# for p in _p.proto.P :
//# sname = _p.struct_name(p)
    case {{p.type.val}}:
      return sizeof_{{sname}};
//# -
    default :
      return 0;
  }
}


//# if _p.parser :

//# if psize != 0:
/**
 * Read the packet size
 * @param data pointer to the buffer
 * @param size poiter to size of the buffer
 * @return new pointer to the data after having consumed bytes for the packet type
 *
 * Note : `size` and `_this->remaining` will be changed accordingly.
 */
//# if psize:
{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_read_size({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  const uint8_t * bytes = (uint8_t *) data;
  while(_this->remain && *size){
    _this->size |= ( *bytes << ({{psize * 8}} - _this->remain) );
    ++bytes;
    --(*size);
    //# if psize != 0:
    ++_this->n_h_read;
    //# -
    _this->remain -= 8;
  }
  return bytes;
}
//# -
//# else:
{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_read_size({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  const uint8_t * bytes = (uint8_t *) data;
  while(*size){
    _this->size |= ( (*bytes & 0b0111111) << (64 - _this->remain) );
    if(*bytes & 0b10000000){
      ++bytes;
      --(*size);
      //# if psize != 0:
      ++_this->n_h_read;
      //# -
      _this->remain = 0;
      return bytes;
    }
    ++bytes;
    --(*size);
    //# if psize != 0:
    ++_this->n_h_read;
    //# -
    _this->remain -= 7;
  }
  return bytes;
}
//# -

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void _{{_p.prefix}}hrp_server_after_read_size({{_p.prefix}}hrp_t * _this){
  if(_this->remain == 0){
    if(_this->size <= _this->n_h_read){
      _{{_p.prefix}}hrp_server_after_read(_this); // If size is 0 or 1, then this is padding, and the semantic of the size says "either it's a zero size packet that should be passed, either it's a less than psize bytes packet, then it can't even store the full psize... SKIP.
      return;
    }
    _this->state = {{_p.prefix}}hrp_READ_TYPE;
    _this->remain = {{tsize * 8 if tsize else 64}};
  }
}


{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_skip({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  const uint8_t * bytes = (uint8_t *) data;
  if(_this->remain > *size){
    _this->remain -= *size;
    bytes += *size;
    *size = 0;
    return bytes;
  }
  else{
    *size -= _this->remain;
    bytes += _this->remain;
    _this->type = 0;
    _this->current_packet = NULL;
    //# if psize != 0:
    _this->size = 0;
    _this->state = {{_p.prefix}}hrp_READ_SIZE;
    _this->remain = {{psize * 8 if psize else 64}};
    _this->n_h_read = 0;
    //# -
    //# else :
    _this->state = {{_p.prefix}}hrp_READ_TYPE;
    _this->remain = {{tsize * 8 if tsize else 64}};
    //# -
  } 
  return bytes;
}
//# -



/**
 * Read the packet type
 * @param data pointer to the buffer
 * @param size poiter to size of the buffer
 * @return new pointer to the data after having consumed bytes for the packet type
 *
 * Note : `size` and `_this->remaining` will be changed accordingly.
 */
//# if tsize:
{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_read_type({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  const uint8_t * bytes = (uint8_t *) data;
  while(_this->remain && *size){
    _this->type |= ( *bytes << ({{tsize * 8}} - _this->remain) );
    ++bytes;
    --(*size);
    //# if psize != 0:
    ++_this->n_h_read;
    //# -
    _this->remain -= 8;
  }
  return bytes;
}
//# -
//# else:
{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_read_type({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  const uint8_t * bytes = (uint8_t *) data;
  while(*size){
    _this->type |= ( (*bytes & 0b0111111) << (64 - _this->remain) );
    if(*bytes & 0b10000000){
      ++bytes;
      --(*size);
      //# if psize != 0:
      ++_this->n_h_read;
      //# -
      _this->remain = 0;
      return bytes;
    }
    ++bytes;
    --(*size);
    //# if psize != 0:
    ++_this->n_h_read;
    //# -
    _this->remain -= 7;
  }
  return bytes;
}
//# -

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void _{{_p.prefix}}hrp_server_after_read_type({{_p.prefix}}hrp_t * _this){
  if(_this->remain == 0){
    _this->state = {{_p.prefix}}hrp_READ;
//# if psize == 0:
    _this->remain = {{_p.prefix}}hrp_packet_size(_this->type);
    _this->current_packet = {{_p.prefix}}hrp_palloc(_this->type);
//# -
//# else:
    _this->remain = _this->size - _this->n_h_read;
    _this->current_packet = {{_p.prefix}}hrp_palloc(_this->type, _this->remain + sizeof({{_p.prefix}}hrp_header_t));
    if(_this->current_packet == NULL)
    {
      _this->state = {{_p.prefix}}hrp_SKIP;
      return;
    }
    _this->current_packet->header.size = _this->size;
//# -
    _this->current_packet->header.type = _this->type;
    _this->current_ptr = _this->current_packet->raw_data_uchar;
    //TODO
  }
}

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
const void * _{{_p.prefix}}hrp_server_read({{_p.prefix}}hrp_t * _this, const void * data, size_t * size){
  size_t to_read = (_this->remain < *size) ? _this->remain : *size;
  if(to_read == 0){
    return data;
  }
  memcpy(_this->current_ptr, data, to_read);
  _this->remain -= to_read;
  *size -= to_read;
  _this->current_ptr += to_read;
  return ((const uint8_t *) data) + to_read;
}

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void _{{_p.prefix}}hrp_server_after_read({{_p.prefix}}hrp_t * _this){
  if(_this->remain == 0){
    {{_p.prefix}}hrp_server_handle_packet(_this);
    _this->type = 0;
    _this->current_packet = NULL;
    //# if psize != 0:
    _this->size = 0;
    _this->state = {{_p.prefix}}hrp_READ_SIZE;
    _this->remain = {{psize * 8 if psize else 64}};
    _this->n_h_read = 0;
    //# -
    //# else :
    _this->state = {{_p.prefix}}hrp_READ_TYPE;
    _this->remain = {{tsize * 8 if tsize else 64}};
    //# -
  }
}


void {{_p.prefix}}hrp_server_parse({{_p.prefix}}hrp_t * _this, const void * data, size_t size){
  if(size == 0){
    return;
  }
  for(;;) {
    switch (_this->state)
    {
//# if psize != 0:
      case {{_p.prefix}}hrp_READ_SIZE:
        data = _{{_p.prefix}}hrp_server_read_size(_this, data, &size);
        _{{_p.prefix}}hrp_server_after_read_size(_this);
        break;
      case {{_p.prefix}}hrp_SKIP:
        data = _{{_p.prefix}}hrp_server_skip(_this, data, &size);
        break;
//# -
      case {{_p.prefix}}hrp_READ_TYPE:
        data = _{{_p.prefix}}hrp_server_read_type(_this, data, &size);
        _{{_p.prefix}}hrp_server_after_read_type(_this);
        if(_this->state != {{_p.prefix}}hrp_READ_TYPE){ //TODO : check why
          continue;
        }
        break;
      case {{_p.prefix}}hrp_READ:
        data = _{{_p.prefix}}hrp_server_read(_this, data, &size);
        _{{_p.prefix}}hrp_server_after_read(_this);
        break;
    }
    if(size <= 0){
      return;
    }
  }
}

void {{_p.prefix}}hrp_server_init({{_p.prefix}}hrp_t * _this){
  _this->type = 0;
//# if psize != 0:
  _this->size = 0;
  _this->state = {{_p.prefix}}hrp_READ_SIZE;
  _this->remain = {{psize * 8 if psize else 64}};
  _this->n_h_read = 0;
//# -
//# else :
  _this->state = {{_p.prefix}}hrp_READ_TYPE;
  _this->remain = {{tsize * 8 if tsize else 64}};
//# -
}


//# -

// INITIALIZERS

//# for p in _p.proto.P :
//#   sname = _p.struct_name(p)
//#   size, varlen_t = _p.sizeof2(p)

//#   if varlen_t is None:
void {{sname}}_init({{sname}}_t * p){
  p->header.type = {{sname}}_type;
//#     if psize != 0:
  p->header.size = sizeof_{{sname}}_packet;
//#     -
}
//#   -
//#   else:
//#     if psize == 0:
//#       raise RuntimeError('Impossible to have varlen packet without variable packet size')
//#     -
void {{sname}}_init({{sname}}_t * p, {{_p.prefix}}hrp_stype_t size){
  p->header.type = {{sname}}_type;
  p->header.size = size;
}
//#   -

//# -

