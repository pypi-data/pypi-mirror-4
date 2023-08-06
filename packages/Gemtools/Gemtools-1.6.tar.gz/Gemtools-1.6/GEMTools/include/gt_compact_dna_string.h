/*
 * PROJECT: GEM-Tools library
 * FILE: gt_compact_dna_string.h
 * DATE: 20/08/2012
 * AUTHOR(S): Santiago Marco-Sola <santiagomsola@gmail.com>
 * DESCRIPTION: Bitmap (compact) representation of DNA-strings (using 8 characters alphabet)
 */

#ifndef GT_COMPACT_DNA_STRING_H_
#define GT_COMPACT_DNA_STRING_H_

#include "gt_commons.h"
#include "gt_dna_string.h"

typedef struct {
  uint64_t* bitmaps;
  uint64_t allocated;
  uint64_t length;
} gt_compact_dna_string;

typedef struct {
  gt_compact_dna_string* cdna_string;
  uint64_t current_pos;
  uint64_t current_pos_mod;
  gt_string_traversal direction;
  uint64_t* current_bitmap;
  uint64_t bm_0;
  uint64_t bm_1;
  uint64_t bm_2;
} gt_compact_dna_sequence_iterator;

extern const char gt_cdna_decode[8];
extern const uint8_t gt_cdna_encode[256];

/*
 * Checkers
 */
#define GT_COMPACT_DNA_STRING_CHECK(cdna_string) \
  GT_NULL_CHECK(cdna_string); \
  GT_NULL_CHECK(cdna_string->bitmaps)
#define GT_COMPACT_DNA_STRING_POSITION_CHECK(cdna_string,position) \
  gt_check(position>=cdna_string->length,CDNA_IT_OUT_OF_RANGE,position,cdna_string->length);
#define GT_COMPACT_DNA_STRING_ITERATOR_CHECK(cdna_string_iterator) \
  GT_NULL_CHECK(cdna_string_iterator); \
  GT_COMPACT_DNA_STRING_CHECK(cdna_string_iterator->cdna_string); \
  GT_NULL_CHECK(cdna_string_iterator->current_bitmap)

/*
 * Constructor
 */
GT_INLINE gt_compact_dna_string* gt_cdna_string_new(const uint64_t initial_chars);
GT_INLINE void gt_cdna_string_resize(gt_compact_dna_string* const cdna_string,const uint64_t num_chars);
GT_INLINE void gt_cdna_string_clear(gt_compact_dna_string* const cdna_string);
GT_INLINE void gt_cdna_string_delete(gt_compact_dna_string* const cdna_string);

/*
 * Handlers
 */
GT_INLINE char gt_cdna_string_get_char_at(gt_compact_dna_string* const cdna_string,const uint64_t pos);
GT_INLINE void gt_cdna_string_set_char_at(gt_compact_dna_string* const cdna_string,const uint64_t pos,const char character);
GT_INLINE uint64_t gt_cdna_string_get_length(gt_compact_dna_string* const cdna_string);
GT_INLINE void gt_cdna_string_append_string(gt_compact_dna_string* const cdna_string,char* const string,const uint64_t length);

/*
 * Compact DNA String Sequence Iterator
 */
GT_INLINE void gt_cdna_string_new_iterator(
    gt_compact_dna_string* const cdna_string,const uint64_t position,gt_string_traversal const direction,
    gt_compact_dna_sequence_iterator* const cdna_string_iterator);
GT_INLINE void gt_cdna_string_iterator_seek(
    gt_compact_dna_sequence_iterator* const cdna_string_iterator,
    const uint64_t pos,gt_string_traversal const direction);
GT_INLINE bool gt_cdna_string_iterator_eos(gt_compact_dna_sequence_iterator* const cdna_string_iterator);
GT_INLINE char gt_cdna_string_iterator_next(gt_compact_dna_sequence_iterator* const cdna_string_iterator);

#endif /* GT_COMPACT_DNA_STRING_H_ */
