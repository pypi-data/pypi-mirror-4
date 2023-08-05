/*
 * PROJECT: GEM-Tools library
 * FILE: gt_buffered_output_file.h
 * DATE: 01/06/2012
 * DESCRIPTION: // TODO
 */

#ifndef GT_BUFFERED_OUTPUT_FILE_H_
#define GT_BUFFERED_OUTPUT_FILE_H_

#include "gt_commons.h"
#include "gt_output_buffer.h"

#define GT_MAX_OUTPUT_BUFFERS 10

typedef enum { SORTED_FILE, UNSORTED_FILE } gt_output_file_type;
typedef struct _gt_buffered_output_file gt_buffered_output_file;
struct _gt_buffered_output_file {
  /* Output file */
  char* file_name;
  FILE* file;
  gt_output_file_type file_type;
  /* Output Buffers */
  gt_output_buffer* buffer[GT_MAX_OUTPUT_BUFFERS];
  uint64_t buffer_busy;
  uint64_t buffer_write_pending;
  /* Mutexes */
  pthread_mutex_t out_buffer_mutex;
  pthread_cond_t  out_buffer_cond;
  pthread_mutex_t out_file_mutex;
  /* Block ID tracer */
  uint32_t mayor_block_id;
  uint32_t minor_block_id;
};

// Codes gt_status
#define GT_BUFFERED_OUTPUT_FILE_OK 0
#define GT_BUFFERED_OUTPUT_FILE_FAIL -1

/*
 * Buffered Output File Setup
 */
gt_buffered_output_file* gt_buffered_output_stream_new(FILE* file,const gt_output_file_type output_file_type);
gt_buffered_output_file* gt_buffered_output_file_new(char* const file_name,const gt_output_file_type output_file_type);
gt_status gt_buffered_output_file_close(gt_buffered_output_file* const buffered_output_file);

/*
 * Internal Buffers Accessors
 */
GT_INLINE gt_output_buffer* gt_buffered_output_file_request_buffer(
    gt_buffered_output_file* const buffered_output_file);
GT_INLINE void gt_buffered_output_file_release_buffer(
    gt_buffered_output_file* const buffered_output_file,gt_output_buffer* const output_buffer);
GT_INLINE gt_output_buffer* gt_buffered_output_file_dump_buffer(
    gt_buffered_output_file* const buffered_output_file,gt_output_buffer* const output_buffer);

#endif /* GT_BUFFERED_OUTPUT_FILE_H_ */
