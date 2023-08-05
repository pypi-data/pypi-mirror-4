/*
 * PROJECT: GEM-Tools library
 * FILE: gt_buffered_output_file.c
 * DATE: 01/06/2012
 * DESCRIPTION: // TODO
 */

#include "gt_buffered_output_file.h"

#define GT_BUFFERED_OUTPUT_FILE_FORCE_DUMP_SIZE GT_BUFFER_SIZE_32M

/*
 * Setup
 */
gt_buffered_output_file* gt_buffered_output_file_new(gt_output_file* const output_file) {
  GT_OUTPUT_FILE_CHECK(output_file);
  gt_buffered_output_file* buffered_output_file = malloc(sizeof(gt_buffered_output_file));
  gt_cond_fatal_error(!buffered_output_file,MEM_HANDLER);
  // Initialize the bof
  buffered_output_file->output_file = output_file;
  buffered_output_file->buffer = gt_output_file_request_buffer(buffered_output_file->output_file);
  return buffered_output_file;
}
void gt_buffered_output_file_close(gt_buffered_output_file* const buffered_output_file) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  if (buffered_output_file->buffer != NULL) {
    gt_buffered_output_file_dump(buffered_output_file);
    gt_output_file_release_buffer(buffered_output_file->output_file,buffered_output_file->buffer);
  }
}

/*
 * Accessors
 */
GT_INLINE void gt_buffered_output_file_get_block_ids(
    gt_buffered_output_file* const buffered_output_file,uint32_t* const mayor_id,uint32_t* const minor_id) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  *mayor_id = gt_output_buffer_get_mayor_block_id(buffered_output_file->buffer);
  *minor_id = gt_output_buffer_get_minor_block_id(buffered_output_file->buffer);
}
GT_INLINE void gt_buffered_output_file_set_block_ids(
    gt_buffered_output_file* const buffered_output_file,const uint32_t mayor_id,const uint32_t minor_id) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  gt_output_buffer_set_mayor_block_id(buffered_output_file->buffer,mayor_id);
  gt_output_buffer_set_minor_block_id(buffered_output_file->buffer,minor_id);
}
GT_INLINE gt_output_buffer* gt_buffered_output_file_get_buffer(gt_buffered_output_file* const buffered_output_file) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  return buffered_output_file->buffer;
}
GT_INLINE void gt_buffered_output_file_set_buffer(
    gt_buffered_output_file* const buffered_output_file,gt_output_buffer* const output_buffer) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  buffered_output_file->buffer = output_buffer;
}

/*
 * Dump
 */
GT_INLINE void gt_buffered_output_file_dump(gt_buffered_output_file* const buffered_output_file) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  if (gt_output_buffer_get_used(buffered_output_file->buffer)==0) return;
  buffered_output_file->buffer = gt_output_file_dump_buffer(
      buffered_output_file->output_file,buffered_output_file->buffer,true);
  gt_cond_fatal_error(buffered_output_file->buffer==NULL,BUFFER_SAFETY_DUMP);
}
GT_INLINE void gt_buffered_output_file_safety_dump(gt_buffered_output_file* const buffered_output_file) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  if (gt_output_buffer_get_used(buffered_output_file->buffer)==0) return;
  gt_output_buffer_set_partial_block(buffered_output_file->buffer);
  register const uint32_t mayor_id = gt_output_buffer_get_mayor_block_id(buffered_output_file->buffer);
  register const uint32_t minor_id = gt_output_buffer_get_minor_block_id(buffered_output_file->buffer);
  buffered_output_file->buffer = gt_output_file_dump_buffer(
      buffered_output_file->output_file,buffered_output_file->buffer,false);
  gt_cond_fatal_error(buffered_output_file->buffer==NULL,BUFFER_SAFETY_DUMP);
  gt_output_buffer_set_mayor_block_id(buffered_output_file->buffer,mayor_id);
  gt_output_buffer_set_minor_block_id(buffered_output_file->buffer,minor_id+1);
}

/*
 * Buffered Output File Printers
 */
GT_INLINE gt_status gt_vbofprintf(gt_buffered_output_file* const buffered_output_file,const char *template,va_list v_args) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  GT_NULL_CHECK(template);
  if (gt_expect_false(
      gt_output_buffer_get_used(buffered_output_file->buffer)>=GT_BUFFERED_OUTPUT_FILE_FORCE_DUMP_SIZE)) {
    gt_buffered_output_file_safety_dump(buffered_output_file);
  }
  register const gt_status chars_printed = gt_vbprintf(buffered_output_file->buffer,template,v_args);
  return chars_printed;
}
GT_INLINE gt_status gt_bofprintf(gt_buffered_output_file* const buffered_output_file,const char *template,...) {
  GT_BUFFERED_OUTPUT_FILE_CHECK(buffered_output_file);
  GT_NULL_CHECK(template);
  va_list v_args;
  va_start(v_args,template);
  register const gt_status chars_printed = gt_vbofprintf(buffered_output_file,template,v_args);
  va_end(v_args);
  return chars_printed;
}
