/*
 * PROJECT: GEM-Tools library
 * FILE: gt.filter.c
 * DATE: 02/08/2012
 * DESCRIPTION: Application to filter {MAP,SAM} files and output the filtered result
 */

#include <getopt.h>
#include <omp.h>

#include "gem_tools.h"

typedef struct {
  char* name_input_file;
  char* name_output_file;
  bool mmap_input;
  bool paired_end;
  uint64_t num_threads;
  bool verbose;
} gt_stats_args;

gt_stats_args parameters = {
    .name_input_file=NULL,
    .name_output_file=NULL,
    .mmap_input=false,
    .paired_end=false,
    .num_threads=1,
    .verbose=false,
};

void gt_filter_read__write() {
  // Open file IN/OUT
  gt_input_file* input_file = (parameters.name_input_file==NULL) ?
      gt_input_stream_open(stdin) : gt_input_file_open(parameters.name_input_file,parameters.mmap_input);
  gt_output_file* output_file = (parameters.name_output_file==NULL) ?
      gt_output_stream_new(stdout,SORTED_FILE) : gt_output_file_new(parameters.name_output_file,SORTED_FILE);

  // Parallel reading+process
  #pragma omp parallel num_threads(parameters.num_threads)
  {
    gt_buffered_input_file* buffered_input = gt_buffered_input_file_new(input_file);
    gt_buffered_output_file* buffered_output = gt_buffered_output_file_new(output_file);
    gt_buffered_input_file_attach_buffered_output(buffered_input,buffered_output);

    gt_status error_code;
    gt_template *template = gt_template_new();
    while ((error_code=gt_input_generic_parser_get_template(buffered_input,template,parameters.paired_end))) {
      if (error_code!=GT_IMP_OK) {
        gt_error_msg("Fatal error parsing file '%s'\n",parameters.name_input_file);
      }

      // Print template
      gt_output_map_bofprint_gem_template(buffered_output,template,GT_ALL,true);
    }

    // Clean
    gt_template_delete(template);
    gt_buffered_input_file_close(buffered_input);
    gt_buffered_output_file_close(buffered_output);
  }

  // Clean
  gt_input_file_close(input_file);
  gt_output_file_close(output_file);
}

void usage() {
  fprintf(stderr, "USE: ./gt.filter [ARGS]...\n"
                  "        --input|-i [FILE]\n"
                  "        --output|-o [FILE]\n"
                  "        --mmap-input\n"
                  "        --paired-end|p\n"
                  "        --threads|t\n"
                  "        --verbose|v\n"
                  "        --help|h\n");
}

void parse_arguments(int argc,char** argv) {
  struct option long_options[] = {
    { "input", required_argument, 0, 'i' },
    { "output", required_argument, 0, 'o' },
    { "mmap-input", no_argument, 0, 1 },
    { "paired-end", no_argument, 0, 'p' },
    { "threads", no_argument, 0, 't' },
    { "verbose", no_argument, 0, 'v' },
    { "help", no_argument, 0, 'h' },
    { 0, 0, 0, 0 } };
  int c,option_index;
  while (1) {
    c=getopt_long(argc,argv,"i:o:t:phv",long_options,&option_index);
    if (c==-1) break;
    switch (c) {
    case 'i':
      parameters.name_input_file = optarg;
      break;
    case 'o':
      parameters.name_output_file = optarg;
      break;
    case 0:
      parameters.mmap_input = true;
      break;
    case 'p':
      parameters.paired_end = true;
      break;
    case 't':
      parameters.num_threads = atol(optarg);
      break;
    case 'v':
      parameters.verbose = true;
      break;
    case 'h':
      usage();
      exit(1);
    case '?':
    default:
      gt_fatal_error_msg("Option not recognized");
    }
  }
}

int main(int argc,char** argv) {
  // Parsing command-line options
  parse_arguments(argc,argv);

  // Filter !
  gt_filter_read__write();

  return 0;
}


