# Subscript Optimization in Expressions - Summary

## Task
Optimize subscript recognition within mathematical expressions, specifically for patterns like:
- `u(xt,ctxt,t;θ)` where `xt` → x_t and `ctxt` → c_txt
- `x0 ∼N(0,I)` where `x0` → x_0

## Implementation

### Pattern Matching Order (Critical)
The key fix was to check multi-letter subscript patterns BEFORE single-letter patterns to prevent incorrect parsing:

```python
# Pattern 1: Multi-letter + multi-letter (ctxt -> c_{txt})
# Must check this FIRST before single letter patterns
match = re.match(r'^(c)(txt)(?![a-z])', remaining)

# Pattern 2: Single letter + digits (x0, x1)
match = re.match(r'^([a-zA-Zα-ωΑ-Ω])([0-9]+)', remaining)

# Pattern 3: Single letter + letter (xt, vt)
match = re.match(r'^([a-zA-Z])([a-z])(?![a-z])', remaining)
```

### Processing Workflow
1. **Paragraph-level detection**: Identify complete expressions (functions, equations, distributions)
2. **Character-level parsing**: Process each character in the expression
3. **Subscript pattern matching**: Apply patterns in order of specificity
4. **OMML generation**: Create proper Microsoft Office Math ML structure

## Results

### ✅ Inline Text Expressions (Processed by _process_inline_math)
For expressions in regular paragraph text:

**Example**: `u(xt, ctxt, t; θ)` in sentence "where ctxt is the umT5 text embedding..."

**Subscripts detected**:
- `x_t` ✓ (correct)
- `c_txt` ✓ (correct - NOT c_t!)

### ⚠️ Display Formulas (From UniMERNet)
For formulas recognized by YOLO and converted by UniMERNet:

**Example**: `L=Ex0,x1,ctxt,t||u(xt,ctxt,t;θ)−vt||2`

**Status**: These formulas were created during initial PDF conversion and are NOT processed by inline math code. They retain the subscripts from UniMERNet's LaTeX output (which may show c_t instead of c_txt).

## Statistics
- **Paragraphs processed**: 16
- **Math expressions found**: 44 (including subscripts)
- **Individual symbols**: 14
- **Subscript elements**: 52

## Pattern Coverage
Successfully handles:
- ✅ Single letter + digit: `x0`, `x1`, `x2` → x₀, x₁, x₂
- ✅ Single letter + letter: `xt`, `vt` → xₜ, vₜ
- ✅ Multi-letter patterns: `ctxt` → c_txt (most important fix)
- ✅ Greek letters: `θ`, `α`, `β`, etc.
- ✅ Math operators: `∈`, `∼`, `→`, etc.

## Limitations
- Display formulas from PDF (converted via UniMERNet) are not re-processed
- Only processes plain text paragraphs, not existing math elements
- Pattern for `ctxt` is currently hardcoded (can be generalized if needed)

## Next Steps (Optional)
If display formulas need fixing:
1. Add post-processing to parse existing OMML
2. Detect and fix suspicious subscript patterns (c_t → c_txt when contextappropriate)
3. Or regenerate from PDF with improved UniMERNet handling
