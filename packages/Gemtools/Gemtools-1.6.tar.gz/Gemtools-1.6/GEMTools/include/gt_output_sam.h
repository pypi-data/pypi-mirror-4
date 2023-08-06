/*
 * PROJECT: GEM-Tools library
 * FILE: gt_output_sam.h
 * DATE: 01/08/2012
 * AUTHOR(S): Santiago Marco-Sola <santiagomsola@gmail.com>
 * DESCRIPTION: // TODO
 */

#ifndef GT_OUTPUT_SAM_H_
#define GT_OUTPUT_SAM_H_

#include "gt_commons.h"
#include "gt_template.h"
#include "gt_output_buffer.h"
#include "gt_buffered_output_file.h"
#include "gt_generic_printer.h"

/*
 * SAM
 */
GT_GENERIC_PRINTER_PROTOTYPE(gt_output_sam,print_header,gt_shash* attributes);

/*
 * SAM High-level Printers
 */
GT_GENERIC_PRINTER_PROTOTYPE(gt_output_sam,print_template,gt_template* const template,const bool compact,const uint64_t max_printable_maps);
GT_GENERIC_PRINTER_PROTOTYPE(gt_output_sam,print_alignment,gt_alignment* const alignment,const bool compact,const uint64_t max_printable_maps);

#endif /* GT_OUTPUT_SAM_H_ */
