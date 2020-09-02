
typedef void (*{{_p.prefix}}hrp_handler_t) ({{_p.prefix}}hrp_packet_t*);

//# if not _p.single_handler :
typedef struct {{_p.prefix}}hrp_vector_s {
//# for p in _p.proto.P:
//#   sname = _p.struct_name(p)
  {{sname}}_handler_t {{sname}};
//# -
} {{_p.prefix}}hrp_vector_t;

//# -
typedef enum {{_p.prefix}}hrp_server_state_e {
//# if psize != 0:
  {{_p.prefix}}hrp_READ_SIZE,
  {{_p.prefix}}hrp_SKIP,
//# -
  {{_p.prefix}}hrp_READ_TYPE,
  {{_p.prefix}}hrp_READ,
} {{_p.prefix}}hrp_server_state_t;

typedef struct {{_p.prefix}}hrp_s {
//# if not _p.single_handler :
  {{_p.prefix}}hrp_vector_t handler;
//# -
//# else:
  {{_p.prefix}}hrp_handler_t handler;
//# -
  {{_p.prefix}}hrp_server_state_t state;
  size_t remain;
  {{_p.prefix}}hrp_packet_t * current_packet; 
  unsigned char * current_ptr;
//# if psize != 0:
  {{_p.prefix}}hrp_stype_t n_h_read;
  {{_p.prefix}}hrp_stype_t size;
//# -
  {{_p.prefix}}hrp_ptype_t type;
} {{_p.prefix}}hrp_t;



#ifdef __cplusplus
extern "C" {
#endif

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_UTILS
size_t {{_p.prefix}}hrp_packet_size({{_p.prefix}}hrp_ptype_t);
//#
//# if _p.parser :

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void {{_p.prefix}}hrp_server_handle_packet({{_p.prefix}}hrp_t * _this);

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void {{_p.prefix}}hrp_server_parse({{_p.prefix}}hrp_t * _this, const void * data, size_t size);

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
void {{_p.prefix}}hrp_server_init({{_p.prefix}}hrp_t * _this);


{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_MEM
//# if psize == 0:
{{_p.prefix}}hrp_packet_t * {{_p.prefix}}hrp_palloc({{_p.prefix}}hrp_ptype_t); // user
//# -
//# else:
{{_p.prefix}}hrp_packet_t * {{_p.prefix}}hrp_palloc({{_p.prefix}}hrp_ptype_t, {{_p.prefix}}hrp_stype_t); // user
//# -

{{_p.prefix}}HRP_FUNCTION_ATTR
{{_p.prefix}}HRP_FUNCTION_ATTR_MEM
void {{_p.prefix}}hrp_pfree({{_p.prefix}}hrp_packet_t *); // user
//#
//# -

#ifdef __cplusplus
}
#endif
