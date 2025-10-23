"""
Test inline math processing on existing DOCX file
"""
import sys
sys.path.insert(0, '.')

from hybrid_converter import HybridConverter

# Create converter instance
converter = HybridConverter()

# Apply inline math processing to existing file
input_file = "test_files/result_hybrid.docx"
output_file = "test_files/result_hybrid_with_inline_math.docx"

print(f"Processing inline math in: {input_file}")
print(f"Output will be saved to: {output_file}")

# Copy the file first
import shutil
shutil.copy(input_file, output_file)

# Process inline math
converter._process_inline_math(output_file)

print(f"\nDone! Check {output_file}")
