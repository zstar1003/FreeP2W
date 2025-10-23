"""
Test if UniMERNet can be loaded correctly with new file structure
"""

from hybrid_converter import HybridConverter

print("=" * 80)
print("Testing UniMERNet Loading")
print("=" * 80)

try:
    # Initialize converter (this will NOT load UniMERNet yet - lazy loading)
    print("\n[1/2] Initializing HybridConverter...")
    converter = HybridConverter()
    print("✓ HybridConverter initialized successfully")

    # Trigger UniMERNet loading
    print("\n[2/2] Loading UniMERNet model...")
    converter._load_unimernet()
    print("✓ UniMERNet loaded successfully")

    print("\n" + "=" * 80)
    print("SUCCESS! UniMERNet is working with the new file structure")
    print("=" * 80)
    print("\nYou can now run the main conversion:")
    print("  python hybrid_converter.py --pdf <your_pdf_file> --output <output_docx>")

except FileNotFoundError as e:
    print(f"\n✗ Error: {e}")
    print("\nPlease check:")
    print("  1. demo.yaml is in the project root directory")
    print("  2. unimernet folder is in the project root directory")

except ImportError as e:
    print(f"\n✗ Import Error: {e}")
    print("\nPlease check:")
    print("  1. unimernet folder contains all required modules")
    print("  2. All dependencies are installed")

except Exception as e:
    print(f"\n✗ Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
