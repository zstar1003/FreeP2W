from pdf2docx import Converter

pdf_file = 'test_files/2503.20314v2.pdf'
docx_file = 'test_files/result.docx'

# convert pdf to docx
cv = Converter(pdf_file)
cv.convert(docx_file)      # all pages by default
cv.close()