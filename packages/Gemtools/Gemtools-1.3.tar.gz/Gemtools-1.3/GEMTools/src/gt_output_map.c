/*
 * PROJECT: GEM-Tools library
 * FILE: gt_output_map.c
 * DATE: 01/06/2012
 * DESCRIPTION: // TODO
 */

#include "gt_commons.h"
#include "gt_input_map_parser.h"
#include "gt_output_map.h"

#define GT_OUTPUT_MAP_COMPACT_COUNTERS_ZEROS_TH 5

/*
 * MAP building block printers
 */
// Generic [G]
GT_INLINE gt_status gt_output_map_gprint_counters(
    gt_generic_printer* const gprinter,gt_vector* const counters,
    const uint64_t max_complete_strata,const bool compact) {
  GT_NULL_CHECK(gprinter); GT_NULL_CHECK(counters);
  register const uint64_t num_counters = gt_vector_get_used(counters);
  register uint64_t i;
  if (num_counters==0) {
    gt_gprintf(gprinter,"0");
    return 0;
  }
  for (i=0;i<num_counters;) {
    if (i>0) gt_gprintf(gprinter,"%c",gt_expect_false(i==max_complete_strata)?GT_MAP_MCS:GT_MAP_COUNTS_SEP);
    register const uint64_t counter = *gt_vector_get_elm(counters,i,uint64_t);
    if (gt_expect_false(compact && counter==0)) {
      register uint64_t j=i+1;
      while (j<num_counters && *gt_vector_get_elm(counters,j,uint64_t)==0) ++j;
      if (gt_expect_false((j-i)>=GT_OUTPUT_MAP_COMPACT_COUNTERS_ZEROS_TH)) {
        gt_gprintf(gprinter,"0" GT_MAP_COUNTS_TIMES_S "%"PRIu64,(j-i)); i=j;
      } else {
        gt_gprintf(gprinter,"0"); ++i;
      }
    } else {
      gt_gprintf(gprinter,"%"PRIu64,counter); ++i;
    }
  }
  return 0;
}
GT_INLINE gt_status gt_output_map_gprint_mismatch_string(gt_generic_printer* const gprinter,gt_map* const map) {
  GT_NULL_CHECK(gprinter); GT_MAP_CHECK(map);
  register uint64_t centinel = 0;
  GT_MISMS_ITERATE(map,misms) {
    register const uint64_t misms_pos = gt_misms_get_position(misms);
    if (misms_pos!=centinel) {
      gt_gprintf(gprinter,"%"PRIu64,misms_pos-centinel);
      centinel = misms_pos-1;
    }
    switch (gt_misms_get_type(misms)) {
      case MISMS:
        gt_gprintf(gprinter,"%c",gt_misms_get_base(misms));
        centinel=misms_pos;
        break;
      case INS:
        gt_gprintf(gprinter,">%"PRIu64"+",gt_misms_get_size(misms));
        break;
      case DEL:
        gt_gprintf(gprinter,">%"PRIu64"-",gt_misms_get_size(misms));
        centinel+=gt_misms_get_size(misms);
        break;
      default:
        gt_error(SELECTION_NOT_VALID);
        break;
    }
  }
  register const uint64_t map_length = gt_map_get_base_length(map);
  if (centinel < map_length) {
    gt_gprintf(gprinter,"%"PRIu64,map_length-centinel);
  }
  return 0;
}
GT_INLINE gt_status gt_output_map_gprint_map(gt_generic_printer* const gprinter,gt_map* const map,const bool print_scores) {
  GT_NULL_CHECK(gprinter); GT_MAP_CHECK(map);
  // FORMAT => chr11:-:51590050:(5)43T46A9>24*
  // Print sequence name
  gt_gprintf(gprinter,"%s",gt_map_get_seq_name(map));
  // Print strand
  gt_gprintf(gprinter,GT_MAP_SEP_S"%c",gt_map_get_strand(map)==FORWARD?GT_MAP_STRAND_FORWARD_SYMBOL:GT_MAP_STRAND_REVERSE_SYMBOL);
  // Print position
  gt_gprintf(gprinter,GT_MAP_SEP_S"%"PRIu64 GT_MAP_SEP_S,gt_map_get_position(map));
  // Print mismatch string (compact it)
  register char* const last_seq_name = gt_map_get_seq_name(map);
  register gt_map* map_it = map, *next_map=NULL;
  register bool cigar_pending = true;
  while (cigar_pending) {
    gt_output_map_gprint_mismatch_string(gprinter,map_it);
    if (gt_map_has_next_block(map_it)) {
      next_map = gt_map_get_next_block(map_it);
      if ((cigar_pending=(gt_streq(last_seq_name,gt_map_get_seq_name(map_it))))){
        switch (gt_map_get_junction(map_it)) {
          case SPLICE:
            gt_gprintf(gprinter,">""%"PRIu64"*",gt_map_get_junction_distance(map_it));
            break;
          case POSITIVE_SKIP:
            gt_gprintf(gprinter,">""%"PRIu64"+",gt_map_get_junction_distance(map_it));
            break;
          case NEGATIVE_SKIP:
            gt_gprintf(gprinter,">""%"PRIu64"-",gt_map_get_junction_distance(map_it));
            break;
          case INSERT:
            cigar_pending=false;
            break;
          case NO_JUNCTION:
            break;
          default:
            gt_error(SELECTION_NOT_VALID);
            break;
        }
      }
    } else {
      cigar_pending = false;
    }
  }
  // Print attributes (scores)
  if (print_scores && gt_map_get_global_score(map)!=GT_MAP_NO_SCORE) {
    gt_gprintf(gprinter,GT_MAP_SEP_S"%"PRIu64,gt_map_get_global_score(map));
  }
  // Print possible next blocks (out of the current sequence => split-maps across chromosomes)
  if (gt_map_has_next_block(map_it)) {
    gt_gprintf(gprinter,GT_MAP_TEMPLATE_SEP);
    gt_output_map_gprint_map(gprinter,next_map,print_scores);
  }
  return 0;
}
GT_INLINE gt_status gt_output_map_gprint_template_maps(
    gt_generic_printer* const gprinter,gt_template* const template,
    const uint64_t num_maps,const bool print_scores) {
  GT_NULL_CHECK(gprinter); GT_TEMPLATE_CHECK(template);
  // NOTE: No sorting performed. Written as laid in the vector.
  //       Thus, if you want a particular sorting (by score, by distance, ...) sorting must be done beforehand
  register uint64_t i = 0;
  if (gt_expect_false(gt_template_get_num_mmaps(template)==0)) {
    gt_gprintf(gprinter,"-");
  } else {
    GT_TEMPLATE__ATTR_ITERATE(template,map_array,map_array_attr) {
      if (i>=num_maps) break;
      if ((i++)>0) gt_gprintf(gprinter,GT_MAP_NEXT_S);
      GT_MAP_ARRAY_ITERATE(map_array,map,end_position) {
        if (end_position>0) gt_gprintf(gprinter,GT_MAP_TEMPLATE_SEP);
        gt_output_map_gprint_map(gprinter,map,print_scores);
        if (print_scores && map_array_attr->score!=GT_MAP_NO_SCORE) {
          gt_gprintf(gprinter,GT_MAP_TEMPLATE_SCORE"%"PRIu64,map_array_attr->score);
        }
      }
    }
  }
  return 0;
}
GT_INLINE gt_status gt_output_map_gprint_alignment_maps(
    gt_generic_printer* const gprinter,gt_alignment* const alignment,
    const uint64_t num_maps,const bool print_scores) {
  GT_NULL_CHECK(gprinter); GT_ALIGNMENT_CHECK(alignment);
  // NOTE: No sorting performed. Written as laid in the vector.
  //       Thus, if you want a particular sorting (by score, by distance, ...) sort beforehand
  register uint64_t i = 0;
  if (gt_expect_false(gt_alignment_get_num_maps(alignment)==0)) {
    gt_gprintf(gprinter,"-");
  } else {
    GT_MAPS_ITERATE(alignment,map) {
      if (i>=num_maps) break;
      if ((i++)>0) gt_gprintf(gprinter,GT_MAP_NEXT_S);
      gt_output_map_gprint_map(gprinter,map,print_scores);
    }
  }
  return 0;
}
// Output Buffer [B]
GT_INLINE gt_status gt_output_map_bprint_counters(gt_output_buffer* const output_buffer,gt_vector* const counters,const uint64_t max_complete_strata,const bool compact) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_counters(&gprinter,counters,max_complete_strata,compact);
}
GT_INLINE gt_status gt_output_map_bprint_map(gt_output_buffer* const output_buffer,gt_map* const map,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_map(&gprinter,map,print_scores);
}
GT_INLINE gt_status gt_output_map_bprint_template_maps(gt_output_buffer* const output_buffer,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_template_maps(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_bprint_alignment_maps(gt_output_buffer* const output_buffer,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_alignment_maps(&gprinter,alignment,num_maps,print_scores);
}
// String [S]
GT_INLINE gt_status gt_output_map_sprint_counters(char **line_ptr,gt_vector* const counters,const uint64_t max_complete_strata,const bool compact) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_counters(&gprinter,counters,max_complete_strata,compact);
}
GT_INLINE gt_status gt_output_map_sprint_map(char **line_ptr,gt_map* const map,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_map(&gprinter,map,print_scores);
}
GT_INLINE gt_status gt_output_map_sprint_template_maps(char **line_ptr,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_template_maps(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_sprint_alignment_maps(char **line_ptr,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_alignment_maps(&gprinter,alignment,num_maps,print_scores);
}
// File [F]
GT_INLINE gt_status gt_output_map_fprint_counters(FILE* file,gt_vector* const counters,const uint64_t max_complete_strata,const bool compact) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_counters(&gprinter,counters,max_complete_strata,compact);
}
GT_INLINE gt_status gt_output_map_fprint_map(FILE* file,gt_map* const map,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_map(&gprinter,map,print_scores);
}
GT_INLINE gt_status gt_output_map_fprint_template_maps(FILE* file,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_template_maps(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_fprint_alignment_maps(FILE* file,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_alignment_maps(&gprinter,alignment,num_maps,print_scores);
}

/*
 * Specific High-level MAP Printers
 */
// Generic Printer [G]
GT_INLINE gt_status gt_output_map_gprint_template(
    gt_generic_printer* const gprinter,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  // Print TAG
  gt_gprintf(gprinter,"%s",gt_template_get_tag(template));
  // Print READ(s)
  register const uint64_t num_blocks = gt_template_get_num_blocks(template);
  register uint64_t i = 0;
  gt_gprintf(gprinter,"\t%s",gt_alignment_get_read(gt_template_get_block(template,i)));
  while (++i<num_blocks) {
    gt_gprintf(gprinter," %s",gt_alignment_get_read(gt_template_get_block(template,i)));
  }
  // Print QUALITY
  i = 0;
  if (gt_alignment_get_qualities(gt_template_get_block(template,i))!=NULL) {
    gt_gprintf(gprinter,"\t%s",gt_alignment_get_qualities(gt_template_get_block(template,i)));
    while (++i<num_blocks) {
      gt_gprintf(gprinter," %s",gt_alignment_get_qualities(gt_template_get_block(template,i)));
    }
  }
  // Print COUNTERS
  if (gt_expect_false(gt_template_get_not_unique_flag(template))) {
    gt_gprintf(gprinter,"\t"GT_MAP_COUNTS_NOT_UNIQUE_S);
  } else {
    gt_gprintf(gprinter,"\t");
    gt_output_map_gprint_counters(gprinter,gt_template_get_counters_vector(template),gt_template_get_mcs(template),false);
  }
  // Print MAPS
  gt_gprintf(gprinter,"\t");
  gt_output_map_gprint_template_maps(gprinter,template,num_maps,print_scores);
  gt_gprintf(gprinter,"\n");
  return 0;
}
GT_INLINE gt_status gt_output_map_gprint_alignment(
    gt_generic_printer* const gprinter,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  // Print TAG
  gt_gprintf(gprinter,"%s",gt_alignment_get_tag(alignment));
  // Print READ(s)
  gt_gprintf(gprinter,"\t%s",gt_alignment_get_read(alignment));
  // Print QUALITY
  if (gt_alignment_get_qualities(alignment)!=NULL) {
    gt_gprintf(gprinter,"\t%s",gt_alignment_get_qualities(alignment));
  }
  // Print COUNTERS
  if (gt_expect_false(gt_alignment_get_not_unique_flag(alignment))) {
    gt_gprintf(gprinter,"\t"GT_MAP_COUNTS_NOT_UNIQUE_S);
  } else {
    gt_gprintf(gprinter,"\t");
    gt_output_map_gprint_counters(gprinter,gt_alignment_get_counters_vector(alignment),gt_alignment_get_mcs(alignment),false);
  }
  // Print MAPS
  gt_gprintf(gprinter,"\t");
  gt_output_map_gprint_alignment_maps(gprinter,alignment,num_maps,print_scores);
  gt_gprintf(gprinter,"\n");
  return 0;
}
// Output Buffer [B]
GT_INLINE gt_status gt_output_map_bprint_template(gt_output_buffer* const output_buffer,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_template(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_bprint_alignment(gt_output_buffer* const output_buffer,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_buffer_printer(&gprinter,output_buffer);
  return gt_output_map_gprint_alignment(&gprinter,alignment,num_maps,print_scores);
}
// String [S]
GT_INLINE gt_status gt_output_map_sprint_template(char **line_ptr,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_template(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_sprint_alignment(char **line_ptr,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_string_printer(&gprinter,line_ptr);
  return gt_output_map_gprint_alignment(&gprinter,alignment,num_maps,print_scores);
}
// File [F]
GT_INLINE gt_status gt_output_map_fprint_template(FILE* file,gt_template* const template,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_template(&gprinter,template,num_maps,print_scores);
}
GT_INLINE gt_status gt_output_map_fprint_alignment(FILE* file,gt_alignment* const alignment,const uint64_t num_maps,const bool print_scores) {
  gt_generic_printer gprinter;
  gt_generic_new_file_printer(&gprinter,file);
  return gt_output_map_gprint_alignment(&gprinter,alignment,num_maps,print_scores);
}





