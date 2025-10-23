"""
Compare actual content between documents to see if they're from the same source
"""

from docx import Document

def get_sample_text(path, num_paragraphs=10):
    """Get first N non-empty paragraphs"""
    doc = Document(path)
    samples = []

    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text and not text.startswith('Figure') and len(text) > 20:
            samples.append(f"Para {i}: {text[:150]}...")
            if len(samples) >= num_paragraphs:
                break

    return samples

print("=" * 80)
print("CONTENT COMPARISON - First 10 substantive paragraphs")
print("=" * 80)

print("\nSMALLPDF REFERENCE:")
print("-" * 80)
smallpdf_samples = get_sample_text('test_files/2503.20314v2_smallpdf.docx', 10)
for sample in smallpdf_samples:
    print(sample)

print("\n\nOUR RESULT:")
print("-" * 80)
our_samples = get_sample_text('result.docx', 10)
for sample in our_samples:
    print(sample)

print("\n" + "=" * 80)
print("CHECKING IF CONTENT MATCHES")
print("=" * 80)

# Extract just the text content (first 100 chars) for comparison
smallpdf_texts = [s.split(': ', 1)[1][:100] if ': ' in s else s[:100] for s in smallpdf_samples]
our_texts = [s.split(': ', 1)[1][:100] if ': ' in s else s[:100] for s in our_samples]

match_count = 0
for sp_text in smallpdf_texts[:5]:
    for our_text in our_texts[:5]:
        # Check if there's significant overlap
        if len(set(sp_text.split()) & set(our_text.split())) > 5:
            match_count += 1
            break

if match_count >= 3:
    print("\nContent appears to match - same source PDF")
    print("The issue is paragraph STRUCTURE, not content")
else:
    print("\nWARNING: Content may be different - check if same source PDF!")

print("=" * 80)
