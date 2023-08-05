/*
 * PROJECT: GEM-Tools library
 * FILE: gt_string.h
 * DATE: 20/08/2012
 * DESCRIPTION: Simple string implementation.
 *   Static stings gt_string_new(0), which share memory across instances (stores mem ptr)
 *   Dynamic strings gt_string_new(n>0), which handle their own memory and hold copy of the string
 */

#ifndef GT_STRING_H_
#define GT_STRING_H_

#include "gt_commons.h"

typedef struct {
  char* buffer;
  uint64_t allocated;
  uint64_t length;
} gt_string;

/*
 * Checkers
 */
#define GT_STRING_CHECK(string) gt_fatal_check(string==NULL,NULL_HANDLER)
#define GT_STRING_CHECK_BUFFER(string) \
  GT_STRING_CHECK(string); \
  gt_fatal_check(string->buffer==NULL,NULL_HANDLER)
#define GT_STRING_CHECK_NO_STATIC(string) \
    GT_STRING_CHECK(string); \
    gt_fatal_check(string->allocated==0,STRING_STATIC)

/*
 * Printers
 */
#define PRIgts "%.*s"
#define PRIgts_content(string) (int)gt_string_get_length(string),gt_string_get_string(string)

/*
 * Constructor & Accessors
 */
GT_INLINE gt_string* gt_string_new(const uint64_t initial_buffer_size);
GT_INLINE void gt_string_resize(gt_string* const string,const uint64_t new_buffer_size);
GT_INLINE void gt_string_clear(gt_string* const string);
GT_INLINE void gt_string_delete(gt_string* const string);

GT_INLINE bool gt_string_is_static(gt_string* const string);
GT_INLINE void gt_string_cast_static(gt_string* const string);
GT_INLINE void gt_string_cast_dynamic(gt_string* const string,const uint64_t initial_buffer_size);

GT_INLINE void gt_string_set_string(gt_string* const string,char* const string_src);
GT_INLINE void gt_string_set_nstring(gt_string* const string,char* const string_src,const uint64_t length);
GT_INLINE char* gt_string_get_string(gt_string* const string);

GT_INLINE uint64_t gt_string_get_length(gt_string* const string);
GT_INLINE void gt_string_set_length(gt_string* const string,const uint64_t length);

GT_INLINE char* gt_string_char_at(gt_string* const string,const uint64_t pos);

GT_INLINE void gt_string_append_string(gt_string* const string_dst,char* const string_src,const uint64_t length);
GT_INLINE void gt_string_append_gt_string(gt_string* const string_dst,gt_string* const string_src);

/*
 * Cmp functions
 */
GT_INLINE bool gt_string_is_null(gt_string* const string);
GT_INLINE int64_t gt_string_cmp(gt_string* const string_a,gt_string* const string_b);
GT_INLINE int64_t gt_string_ncmp(gt_string* const string_a,gt_string* const string_b,const uint64_t length);
GT_INLINE bool gt_string_equals(gt_string* const string_a,gt_string* const string_b);
GT_INLINE bool gt_string_nequals(gt_string* const string_a,gt_string* const string_b,const uint64_t length);

/*
 * Handlers
 */
GT_INLINE gt_string* gt_string_dup(gt_string* const sequence);
GT_INLINE void gt_string_copy(gt_string* const sequence_dst,gt_string* const sequence_src);
GT_INLINE void gt_string_reverse_copy(gt_string* const sequence_dst,gt_string* const sequence_src);
GT_INLINE void gt_string_reverse(gt_string* const sequence);

/*
 * String Printers
 */
GT_INLINE gt_status gt_vsprintf(gt_string* const sequence,const char *template,va_list v_args);
GT_INLINE gt_status gt_sprintf(gt_string* const sequence,const char *template,...);
GT_INLINE gt_status gt_vsprintf_append(gt_string* const sequence,const char *template,va_list v_args);
GT_INLINE gt_status gt_sprintf_append(gt_string* const sequence,const char *template,...);

/*
 * Iterator
 */
#define GT_STRING_ITERATE(string,mem,pos) \
  register uint64_t pos; \
  register const uint64_t __length_##mem = gt_string_get_length(string); \
  register const char* mem = gt_string_get_string(string); \
  for (pos=0;pos<__length_##mem;++pos) /* mem[pos] */


#endif /* GT_STRING_H_ */
