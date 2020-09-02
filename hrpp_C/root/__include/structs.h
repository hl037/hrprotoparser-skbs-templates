//# from itertools import chain

typedef struct {{_p.prefix}}hrp_header_s {
//# if psize != 0:
  {{_p.prefix}}hrp_stype_t size;
//# -
  {{_p.prefix}}hrp_ptype_t type;
} {{_p.prefix}}hrp_header_t;

//# for s in chain(_p.proto.S, _p.proto.P) :
//# sname = _p.struct_name(s)
//   ----- {{ f'{sname.upper():^20}'}} -----
//# sizeof_s, varlen_t = _p.sizeof2(s)
//# if varlen_t is not None:
//#   sizeof_varlen_t = _p.sizeof(varlen_t)
//# -

#pragma pack(push, 1)
//# if s.order == _p.Struct.order:
typedef struct {{sname}}_s {
//#  for f in s.fields:
//#     t, array = _p.getCType(f)
  {{t}} {{f.name}}{{array}}; {{_p.comment(f)}}
//#  -
#ifdef __cplusplus
  static constexpr size_t packet_size = {{sizeof_s}};
//# if varlen_t is not None:
  static constexpr size_t varlen_size = {{sizeof_varlen_t}};
//# -
#endif
} {{sname}}_t;

#ifdef __cplusplus
constexpr size_t sizeof_{{sname}} = {{sname}}_t::packet_size;
//# if varlen_t is not None:
constexpr size_t sizeof_{{sname}}_varlen = {{sname}}_t::varlen_size;
//# -
#else
static const size_t sizeof_{{sname}} = {{sizeof_s}};
//# if varlen_t is not None:
static const size_t sizeof_{{sname}}_varlen = {{sizeof_varlen_t}};
//# -
#endif
//# -
//# elif s.order == _p.Packet.order:
typedef struct {{sname}}_data_s {
//#  for f in s.fields:
//#     t, array = _p.getCType(f)
  {{t}} {{f.name}}{{array}}; {{_p.comment(f)}}
//#  -
} {{sname}}_data_t;

typedef struct {{sname}}_s {
#ifdef __cplusplus
  static constexpr {{_p.prefix}}hrp_ptype_t ptype = {{s.type.name}};
  static constexpr size_t size = {{sizeof_s}};
  static constexpr size_t packet_size = size + sizeof({{_p.prefix}}hrp_header_t);
//# if varlen_t is not None:
  static constexpr size_t varlen_size = {{sizeof_varlen_t}};
//# -

#endif
  
  {{_p.prefix}}hrp_header_t header;
  union {
    {{sname}}_data_t data;
    FLEXIBLE_ARRAY(char, raw_data);
    FLEXIBLE_ARRAY(unsigned char, raw_data_uchar);
  };
} {{sname}}_t;


#ifdef __cplusplus
extern "C" {
#endif
{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_P_INIT
//# if varlen_t is None:
void {{sname}}_init({{sname}}_t * p);
//# -
//# else :
void {{sname}}_init({{sname}}_t * p, {{_p.prefix}}hrp_stype_t size);
//# -
#ifdef __cplusplus
}
#endif
typedef void (*{{sname}}_handler_t) ({{sname}}_t *);

#ifdef __cplusplus
constexpr size_t sizeof_{{sname}} = {{sname}}_t::size;
constexpr size_t sizeof_{{sname}}_packet = {{sname}}_t::packet_size;
//# if varlen_t is not None:
constexpr size_t sizeof_{{sname}}_varlen = {{sname}}_t::varlen_size;
//# -
constexpr {{_p.prefix}}hrp_ptype_t {{sname}}_type = {{s.type.name}};
#else
static const size_t sizeof_{{sname}} = {{sizeof_s}};
static const size_t sizeof_{{sname}}_packet = {{sizeof_s}} + sizeof({{_p.prefix}}hrp_header_t);
//# if varlen_t is not None:
static const size_t sizeof_{{sname}}_varlen = {{sizeof_varlen_t}};
//# -
static const {{_p.prefix}}hrp_ptype_t {{sname}}_type = {{s.type.name}};
#endif
//# -
//# elif s.order == _p.Alias.order:
typedef {{_p.struct_name(s.alias)}}_t {{sname}}_t;
#ifdef __cplusplus
constexpr size_t sizeof_{{sname}} = {{sname}}_t::size;
//# if varlen_t is not None:
constexpr size_t sizeof_{{sname}}_varlen = {{sname}}_t::varlen_size;
//# -
#else
static const size_t sizeof_{{sname}} = {{sizeof_s}};
//# if varlen_t is not None:
static const size_t sizeof_{{sname}}_varlen = {{sizeof_varlen_t}};
//# -
#endif
//# -
#pragma pack(pop)
//#-

typedef struct {{_p.prefix}}hrp_packet_u {
  {{_p.prefix}}hrp_header_t header;
  union {
    FLEXIBLE_ARRAY(char, raw_data);
    FLEXIBLE_ARRAY(unsigned char, raw_data_uchar);
//# for p in chain(_p.proto.P) :
//# sname = _p.struct_name(p)
    {{sname}}_data_t {{sname}};
//# -
  };
}{{_p.prefix}}hrp_packet_t;

#ifdef __cplusplus
template<typename T>
//# if psize != 0:
T {{_p.prefix}}create_packet({{_p.prefix}}hrp_ptype_t size=T::packet_size){
//# -
//# else:
T {{_p.prefix}}init_packet(){
//# -
  T p;
//# if psize != 0:
  p.header.size = size;
//# -
  p.header.type = T::ptype;
  return p;
}

template<typename T>
//# if psize != 0:
void {{_p.prefix}}init_packet(T & p, {{_p.prefix}}hrp_ptype_t size=T::packet_size){
//# -
//# else:
T {{_p.prefix}}init_packet(T & p){
//# -
//# if psize != 0:
  p.header.size = size;
//# -
  p.header.type = T::ptype;
}


template<typename T>
//# if psize != 0:
void {{_p.prefix}}init_packet(T * p, {{_p.prefix}}hrp_ptype_t size=T::packet_size){
//# -
//# else:
T {{_p.prefix}}init_packet(T * p){
//# -
//# if psize != 0:
  p->header.size = size;
//# -
  p->header.type = T::ptype;
}

#endif

