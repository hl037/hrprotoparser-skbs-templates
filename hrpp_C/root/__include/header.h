#ifndef {{_p.prefix.upper()}}PROTOCOL_H
#define {{_p.prefix.upper()}}PROTOCOL_H

#ifndef FLEXIBLE_ARRAY

#ifdef __cplusplus

#include <cinttypes>
#include <climits>
#include <cstdlib>
#include <cstring>


template <typename T>
class FlexibleArray
{
  public:
    inline FlexibleArray()=default;
    inline ~FlexibleArray()=default;
    // inline T & operator[](size_t ind){
    //   return reinterpret_cast<T*>(this)[ind];
    // }
    // inline const T & operator[](size_t ind) const{
    //   return reinterpret_cast<const T*>(this)[ind];
    // }
    inline operator T * () { return reinterpret_cast<T*>(this); }
    inline operator const T * () const { return reinterpret_cast<const T*>(this); }
    inline T * ptr() { return reinterpret_cast<T*>(this); };
    inline const T * cptr() const { return reinterpret_cast<const T *>(this); };
};

#define FLEXIBLE_ARRAY(t, f) FlexibleArray<t> f

#else

#define FLEXIBLE_ARRAY(t, f) t f[0]

#endif

#endif

#if defined(__WINE__)

typedef __int8 int8_t;
typedef unsigned __int8 uint8_t;
typedef __int16 int16_t;
typedef unsigned __int16 uint16_t;
typedef __int32 int32_t;
typedef unsigned __int32 uint32_t;
typedef __int64 int64_t;
typedef unsigned __int64 uint64_t;

#else

#include <inttypes.h>
#include <limits.h>
#include <stdlib.h>
#include <string.h>

#endif


//# if tsize:
typedef {{ {1: 'uint8_t', 2: 'uint18_t', 4:'uint32_t', 8:'uint64_t' }[tsize] }} {{_p.prefix}}hrp_ptype_t;
//# -
//# else:
typedef uint64_t {{_p.prefix}}hrp_ptype_t;
//# -

//# if psize:
typedef {{ {1: 'uint8_t', 2: 'uint18_t', 4:'uint32_t', 8:'uint64_t' }[psize] }} {{_p.prefix}}hrp_stype_t;
//# -
//# else:
typedef uint64_t {{_p.prefix}}hrp_stype_t;
//# -

#ifndef {{_p.prefix}}HRP_FUNCTION_ATTR // So that one can add specific attributes for all functions
#define {{_p.prefix}}HRP_FUNCTION_ATTR
#endif

#ifndef {{_p.prefix}}HRP_FUNCTION_ATTR_P_INIT // Packet init functions
#define {{_p.prefix}}HRP_FUNCTION_ATTR_P_INIT
#endif

#ifndef {{_p.prefix}}HRP_FUNCTION_ATTR_PARSER // Parser functions
#define {{_p.prefix}}HRP_FUNCTION_ATTR_PARSER
#endif

#ifndef {{_p.prefix}}HRP_FUNCTION_ATTR_MEM // palloc / pfree
#define {{_p.prefix}}HRP_FUNCTION_ATTR_MEM
#endif

#ifndef {{_p.prefix}}HRP_FUNCTION_ATTR_UTILS // packet_size, etc.
#define {{_p.prefix}}HRP_FUNCTION_ATTR_UTILS
#endif
