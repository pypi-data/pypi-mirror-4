/*
 * PROJECT: GEM-Tools library
 * FILE: gt_dna_string.h
 * DATE: 20/08/2012
 * DESCRIPTION: // TODO
 */

#ifndef GT_DNA_STRING_H_
#define GT_DNA_STRING_H_

#include "gt_commons.h"
#include "gt_map.h"

#define gt_dna_string gt_string

typedef struct {
  gt_dna_string* dna_string;
  uint64_t current_pos;
} gt_dna_string_iterator;

extern bool gt_dna[256];
extern char gt_complement_table[256];
#define gt_is_dna(character) gt_dna[(int)character]
#define gt_get_complement(character) (gt_complement_table[(int)character])

/*
 * Checkers
 */
#define GT_DNA_STRING_CHECK(dna_string) \
  GT_NULL_CHECK(dna_string); \
  GT_STRING_CHECK(dna_string)
#define GT_DNA_STRING_ITERATOR_CHECK(dna_string_iterator) \
  GT_NULL_CHECK(dna_string_iterator); \
  GT_DNA_STRING_CHECK(dna_string_iterator->dna_string)

/*
 * Constructor
 */
#define gt_dna_string_new gt_string_new
#define gt_dna_string_resize gt_string_resize
#define gt_dna_string_clear gt_string_clear
#define gt_dna_string_delete gt_string_delete

/*
 * DNA String handler
 */
GT_INLINE bool gt_dna_string_is_dna_string(gt_dna_string* const dna_string);

GT_INLINE char gt_dna_string_get_char_at(gt_dna_string* const dna_string,const uint64_t pos);
GT_INLINE void gt_dna_string_set_char_at(gt_dna_string* const dna_string,const uint64_t pos,const char character);

#define gt_dna_string_set_string gt_string_set_string
#define gt_dna_string_set_nstring gt_string_set_nstring
#define gt_dna_string_get_string gt_string_get_string
#define gt_dna_string_get_length gt_string_get_length

#define gt_dna_string_append_string gt_string_append_string

GT_INLINE void gt_dna_string_reverse_complement(gt_dna_string* const dna_string);
GT_INLINE void gt_dna_string_reverse_complement_copy(gt_dna_string* const dna_string_dst,gt_dna_string* const dna_string_src);

/*
 * DNA String Iterator
 */
GT_INLINE void gt_dna_string_new_iterator(
    gt_dna_string* const dna_string,const uint64_t pos,gt_strand const strand,
    gt_dna_string_iterator* const dna_string_iterator);
GT_INLINE void gt_dna_string_iterator_seek(gt_dna_string_iterator* const dna_string_iterator,const uint64_t pos);
GT_INLINE bool gt_dna_string_iterator_eos(gt_dna_string_iterator* const dna_string_iterator);
GT_INLINE char gt_dna_string_iterator_next(gt_dna_string_iterator* const dna_string_iterator);
GT_INLINE char gt_dna_string_iterator_previous(gt_dna_string_iterator* const dna_string_iterator);

#endif /* GT_DNA_STRING_H_ */
