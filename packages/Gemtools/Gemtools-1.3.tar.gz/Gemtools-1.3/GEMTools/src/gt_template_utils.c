/*
 * PROJECT: GEM-Tools library
 * FILE: gt_template_utils.h
 * DATE: 19/07/2012
 * DESCRIPTION: // TODO
 */

#include "gt_template_utils.h"

/*
 * Template's MMaps operators (Update global state: counters, ...)
 */
GT_INLINE gt_map** gt_template_put_mmap(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),int64_t (*gt_map_cmp_fx)(gt_map*,gt_map*),
    gt_template* const template,gt_map** const mmap,gt_mmap_attributes* const mmap_attr,
    const bool replace_dup,const bool alignment_insertion) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  GT_NULL_CHECK(mmap);
  GT_NULL_CHECK(mmap_attr);
  // Resolve mmap
  register const uint64_t num_blocks = gt_template_get_num_blocks(template);
  register gt_map** uniq_mmaps = malloc(num_blocks*sizeof(gt_map*));
  register uint64_t i;
  for (i=0;i<num_blocks;++i) {
    GT_NULL_CHECK(mmap[i]);
    register gt_map* uniq_map;
    if (gt_expect_false(alignment_insertion)) {
      uniq_mmaps[i] = gt_alignment_put_map(gt_map_cmp_fx,gt_template_get_block(template,i),mmap[i],false);
    } else {
      uint64_t found_map_pos;
      gt_map* found_map;
      if (gt_alignment_find_map_fx(gt_map_cmp_fx,gt_template_get_block(template,i),mmap[i],&found_map_pos,&found_map)) {
        uniq_mmaps[i] = found_map;
      } else {
        uniq_mmaps[i] = mmap[i];
      }
    }
  }
  // Handle duplicates
  gt_map** found_mmap;
  gt_mmap_attributes found_mmap_attr;
  uint64_t found_mmap_pos;
  register gt_map** template_mmap;
  if (gt_expect_false(gt_template_find_mmap_fx(gt_mmap_cmp,template,mmap,&found_mmap_pos,&found_mmap,&found_mmap_attr))) {
    if (gt_expect_true(replace_dup)) {
      // Remove old mmap
      gt_template_dec_counter(template,found_mmap_attr.distance+1);
      // Replace old mmap
      gt_template_set_mmap(template,found_mmap_pos,uniq_mmaps,mmap_attr);
    }
    template_mmap=gt_template_get_mmap(template,found_mmap_pos,NULL);
  } else {
    // Add new map
    gt_template_inc_counter(template,mmap_attr->distance+1);
    gt_template_add_mmap(template,uniq_mmaps,mmap_attr);
    template_mmap=gt_template_get_mmap(template,gt_template_get_num_mmaps(template)-1,NULL);
  }
  // Free auxiliary vector
  free(uniq_mmaps);
  return template_mmap;
}

GT_INLINE void gt_template_insert_mmap(
    gt_template* const template,gt_map** const mmap,gt_mmap_attributes* const mmap_attr,const bool alignment_insertion) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  GT_NULL_CHECK(mmap); GT_NULL_CHECK(mmap_attr);
  gt_template_insert_mmap_fx(gt_mmap_cmp,template,mmap,mmap_attr,alignment_insertion);
}
GT_INLINE void gt_template_insert_mmap_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template,gt_map** const mmap,gt_mmap_attributes* const mmap_attr,const bool alignment_insertion) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  GT_NULL_CHECK(mmap); GT_NULL_CHECK(mmap_attr);
  gt_template_put_mmap(gt_mmap_cmp_fx,gt_map_cmp,template,mmap,mmap_attr,true,alignment_insertion);
}
GT_INLINE void gt_template_insert_mmap_gtvector(
    gt_template* const template,gt_vector* const mmap,gt_mmap_attributes* const mmap_attr,const bool alignment_insertion) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  GT_VECTOR_CHECK(mmap); GT_NULL_CHECK(mmap_attr);
  gt_template_insert_mmap_gtvector_fx(gt_mmap_cmp,template,mmap,mmap_attr,alignment_insertion);
}
GT_INLINE void gt_template_insert_mmap_gtvector_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template,gt_vector* const mmap,gt_mmap_attributes* const mmap_attr,const bool alignment_insertion) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  GT_VECTOR_CHECK(mmap); GT_NULL_CHECK(mmap_attr);
  gt_check(gt_vector_get_used(mmap)!=gt_template_get_num_blocks(template),TEMPLATE_ADD_BAD_NUM_BLOCKS);
  gt_template_insert_mmap_fx(gt_mmap_cmp_fx,template,gt_vector_get_mem(mmap,gt_map*),mmap_attr,alignment_insertion);
}

// TODO: Scheduled for v2.0
GT_INLINE void gt_template_remove_mmap(
    gt_template* const template,gt_map** const mmap) {
  // TODO
}
GT_INLINE void gt_template_remove_mmap_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template,gt_map** const mmap) {
  // TODO
}


GT_INLINE bool gt_template_find_mmap_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template,gt_map** const mmap,
    uint64_t* const found_mmap_pos,gt_map*** const found_mmap,gt_mmap_attributes* const found_mmap_attr) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template); GT_NULL_CHECK(mmap);
  GT_NULL_CHECK(found_mmap_pos); GT_NULL_CHECK(found_mmap);
  // Search for the mmap
  register const uint64_t num_blocks = gt_template_get_num_blocks(template);
  register uint64_t pos = 0;
  GT_TEMPLATE_ITERATE(template,template_mmap) {
    if (gt_mmap_cmp_fx(template_mmap,mmap,num_blocks)==0) {
      *found_mmap_pos = pos;
      *found_mmap = template_mmap;
      if (found_mmap_attr) *found_mmap_attr = *gt_template_get_mmap_attr(template,pos);
      return true;
    }
    ++pos;
  }
  return false;
}
GT_INLINE bool gt_template_is_mmap_contained(gt_template* const template,gt_map** const mmap) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template); GT_NULL_CHECK(mmap);
  gt_map** found_mmap;
  uint64_t found_mmap_pos;
  return gt_template_find_mmap_fx(gt_mmap_cmp,template,mmap,
      &found_mmap_pos,&found_mmap,NULL);
}
GT_INLINE bool gt_template_is_mmap_contained_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template,gt_map** const mmap) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template); GT_NULL_CHECK(mmap);
  gt_map** found_mmap;
  uint64_t found_mmap_pos;
  return gt_template_find_mmap_fx(gt_mmap_cmp_fx,template,mmap,
      &found_mmap_pos,&found_mmap,NULL);
}

/*
 * Template's Counters operators
 */
GT_INLINE void gt_template_recalculate_counters(gt_template* const template) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  // Clear previous counters
  gt_vector_clean(gt_template_get_counters_vector(template));
  // Recalculate counters
  register const num_blocks = gt_template_get_num_blocks(template);
  GT_TEMPLATE__ATTR_ITERATE(template,mmap,mmap_attr) {
    register uint64_t i, total_distance = 0;
    for (i=0;i<num_blocks;++i) {
      total_distance+=gt_map_get_global_distance(mmap[i]);
    }
    mmap_attr->distance=total_distance;
    gt_template_inc_counter(template,total_distance+1);
  }
}
GT_INLINE uint64_t gt_template_get_min_matching_strata(gt_template* const template) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  register gt_vector* vector = gt_template_get_counters_vector(template);
  GT_VECTOR_ITERATE(vector,counter,counter_pos,uint64_t) {
    if (*counter!=0) return counter_pos+1;
  }
  return UINT64_MAX;
}
GT_INLINE bool gt_template_is_thresholded_mapped(gt_template* const template,const uint64_t max_allowed_strata) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  register gt_vector* vector = gt_template_get_counters_vector(template);
  GT_VECTOR_ITERATE(vector,counter,counter_pos,uint64_t) {
    if ((counter_pos+1)>=max_allowed_strata) return false;
    else if (*counter!=0) return true;
  }
  return false;
}
GT_INLINE bool gt_template_is_mapped(gt_template* const template) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template);
  return gt_template_is_thresholded_mapped(template,UINT64_MAX);
}

/*
 * Template Set operators
 */
GT_INLINE void gt_template_merge_template_mmaps(gt_template* const template_dst,gt_template* const template_src) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template_dst);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  GT_TEMPLATE__ATTR_ITERATE(template_src,mmap,mmap_attr) {
    gt_template_insert_mmap(template_dst,mmap,mmap_attr,true);
  }
}
GT_INLINE void gt_template_merge_template_mmaps_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template_dst,gt_template* const template_src) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_dst);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  GT_TEMPLATE__ATTR_ITERATE(template_src,mmap,mmap_attr) {
    gt_template_insert_mmap_fx(gt_mmap_cmp_fx,template_dst,mmap,mmap_attr,true);
  }
}

// TODO: Scheduled for v2.0
GT_INLINE void gt_template_remove_template_mmaps(
    gt_template* const template_dst,gt_template* const template_src) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template_dst);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  GT_TEMPLATE_ITERATE(template_src,mmap) {
    gt_template_remove_mmap(template_dst,mmap);
  }
}
GT_INLINE void gt_template_remove_template_mmaps_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template_dst,gt_template* const template_src) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_dst);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  GT_TEMPLATE_ITERATE(template_src,mmap) {
    gt_template_remove_mmap_fx(gt_mmap_cmp_fx,template_dst,mmap);
  }
}

GT_INLINE gt_template* gt_template_union_template_mmaps_fx_v(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    const uint64_t num_src_templates,gt_template* const template_src,va_list v_args) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_ZERO_CHECK(num_src_templates);
  // Create new template
  register gt_template* const template_union = gt_template_new();
  // gt_template_handler_copy(template_union,template_src); // FIXME
  // Merge template sources into template_union
  register uint64_t num_tmp_merged = 0;
  register gt_template* template_target = template_src;
  do {
    GT_TEMPLATE_CONSISTENCY_CHECK(template_target);
    gt_template_merge_template_mmaps_fx(gt_mmap_cmp_fx,template_union,template_target);
    template_target = (++num_tmp_merged < num_src_templates) ? va_arg(v_args,gt_template*) : NULL;
  } while (gt_expect_true(template_target!=NULL));
  return template_union;
}
GT_INLINE gt_template* gt_template_union_template_mmaps_fx_va(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    const uint64_t num_src_templates,gt_template* const template_src,...) {
  GT_NULL_CHECK(gt_mmap_cmp_fx);
  GT_ZERO_CHECK(num_src_templates);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  va_list v_args;
  va_start(v_args,template_src);
  register gt_template* const template_union =
      gt_template_union_template_mmaps_fx_v(gt_mmap_cmp_fx,num_src_templates,template_src,v_args);
  va_end(v_args);
  return template_union;
}
GT_INLINE gt_template* gt_template_union_template_mmaps_va(
    const uint64_t num_src_templates,gt_template* const template_src,...) {
  GT_ZERO_CHECK(num_src_templates);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src);
  va_list v_args;
  va_start(v_args,template_src);
  register gt_template* const template_union =
      gt_template_union_template_mmaps_fx_v(gt_mmap_cmp,num_src_templates,template_src,v_args);
  va_end(v_args);
  return template_union;
}

GT_INLINE gt_template* gt_template_subtract_template_mmaps_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template_minuend,gt_template* const template_subtrahend) {
  // TODO
}
GT_INLINE gt_template* gt_template_subtract_template_mmaps(
    gt_template* const template_minuend,gt_template* const template_subtrahend) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template_minuend);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_subtrahend);
  return gt_template_subtract_template_mmaps_fx(gt_mmap_cmp,template_minuend,template_subtrahend);
}

GT_INLINE gt_template* gt_template_intersect_template_mmaps_fx(
    int64_t (*gt_mmap_cmp_fx)(gt_map**,gt_map**,uint64_t),
    gt_template* const template_src_A,gt_template* const template_src_B) {
  // TODO
//  // Create new template
//  register gt_template* const template_union = gt_template_new();
//  gt_template_handler_copy(template_union,template_src);
//  //
//....
//  // Copy common mmaps
//  GT_TEMPLATE__ATTR_ITERATE(template_src_A,mmap,mmap_attr) {
//    if (gt_template_is_mmap_contained_fx(gt_mmap_cmp_fx,template_src_B,mmap)) {
//
//    }
//  }
  return NULL;
}
GT_INLINE gt_template* gt_template_intersect_template_mmaps(
    gt_template* const template_src_A,gt_template* const template_src_B) {
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src_A);
  GT_TEMPLATE_CONSISTENCY_CHECK(template_src_B);
  return gt_template_intersect_template_mmaps_fx(gt_mmap_cmp,template_src_A,template_src_B);
}
