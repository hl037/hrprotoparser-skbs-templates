
#ifdef __cplusplus

//#for e in _p.proto.E:
typedef enum {{_p.cName(e)}}_e : {{_p.c_types[e.type.name][0]}} {
//# suffix = '' if not e.type or e.type.name[0] != 'u' else 'U'
//# for f in e.constants:
  {{f.name}} = {{f.computedStr}}{{suffix}}, {{_p.comment(f)}}
//# -
} {{_p.cName(e)}}_t;

//#-


//#for c in _p.proto.GC:
constexpr {{_p.c_types[c.type][0]}} {{c.name}} = {{c.computedStr}}{{'' if c.type[0] != 'u' else 'U'}};
//#-

#else

//#for e in _p.proto.E:
enum {{_p.cName(e)}}_e{
//# suffix = '' if not e.type or e.type.name[0] != 'u' else 'U'
//# for f in e.constants:
  {{f.name}} = {{f.computedStr}}{{suffix}}, {{_p.comment(f)}}
//# -
};
typedef {{_p.c_types[e.type.name][0]}} {{_p.cName(e)}}_t ;

//#-

//#signed = [c for c in _p.proto.GC if c.type[0] != 'u']
//#unsigned = [c for c in _p.proto.GC if c.type[0] == 'u']

//#if len(signed):
enum {
//# for c in signed:
  {{c.name}} = {{c.computedStr}},
//# -
};
//#-

//#if len(unsigned):
enum {
//# for c in unsigned:
  {{c.name}} = {{c.computedStr}}U,
//# -
};
//#-

#endif


