"""
Analyze inline math symbols in PDF text
"""
import fitz
import re

pdf_path = "test_files/2503.20314v2.pdf"

print("Analyzing inline math symbols in PDF...\n")
print("=" * 80)

doc = fitz.open(pdf_path)

# Write to file to avoid encoding issues
with open("inline_math_analysis.txt", "w", encoding="utf-8") as f:
    f.write("Analyzing inline math symbols in PDF...\n\n")
    f.write("=" * 80 + "\n")

    # Check a few pages
    for page_num in range(min(5, len(doc))):
        page = doc[page_num]
        text_dict = page.get_textpage().extractDICT()

        f.write(f"\n【Page {page_num + 1}】\n\n")

        # Look for common math patterns
        math_patterns = {
            'subscript': r'[a-zA-Z]\d+',  # x1, x0, etc
            'unicode_subscript': r'[₀₁₂₃₄₅₆₇₈₉]+',
            'unicode_superscript': r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+',
            'greek': r'[α-ωΑ-Ω]+',
            'math_symbols': r'[∼∈∉⊂⊃∩∪∀∃∇∂∫∑∏√±×÷≤≥≠≈∞]',
            'special_brackets': r'[⟨⟩⌈⌉⌊⌋]',
        }

        found_examples = {pattern_name: [] for pattern_name in math_patterns}

        for block in text_dict.get('blocks', []):
            if block.get('type') != 0:
                continue

            for line in block.get('lines', []):
                for span in line.get('spans', []):
                    text = span.get('text', '')

                    # Check each pattern
                    for pattern_name, pattern in math_patterns.items():
                        matches = re.findall(pattern, text)
                        if matches:
                            for match in matches:
                                if match not in found_examples[pattern_name]:
                                    found_examples[pattern_name].append(match)

        # Print results
        for pattern_name, examples in found_examples.items():
            if examples:
                f.write(f"  {pattern_name}: {examples[:10]}\n")  # Show first 10 examples

    # Also check specific text with math
    f.write("\n" + "=" * 80 + "\n")
    f.write("Sample text with potential inline math:\n\n")

    page = doc[3]  # Page 4
    text_dict = page.get_textpage().extractDICT()

    for block_idx, block in enumerate(text_dict.get('blocks', [])[:5]):
        if block.get('type') != 0:
            continue

        block_text = ''
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                block_text += span.get('text', '')

        if block_text.strip() and len(block_text) < 500:
            f.write(f"Block {block_idx}: {block_text[:200]}\n\n")

    f.write("=" * 80 + "\n")

doc.close()

print("Analysis written to inline_math_analysis.txt")
