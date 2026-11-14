"""Run with python -m unittest discover -s tests -v.

Uses real synthetic PDFs and pdf2docx, but deterministic detections (no ML weights).
"""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import fitz
from docx import Document
from pdf2docx.image.ImagesExtractor import ImagesExtractor
from pdf2docx.page.RawPageFitz import RawPageFitz
from pdf2docx.shape.Paths import Paths

ROOT = Path(__file__).resolve().parents[1]
HOOKS = [(ImagesExtractor, 'extract_images'), (RawPageFitz, '_preprocess_text'),
         (Paths, 'restore'), (Paths, 'to_shapes_and_images')]


class Detector:
    def __init__(self):
        self.detected_regions = {}
        self.calls = 0

    def detect_page_regions(self, page, number):
        if number not in self.detected_regions:
            self.calls += 1
            figures = [{'bbox': [40, 40, 200, 100]}] if page.rect.width == 300 else []
            self.detected_regions[number] = {'figures': figures, 'formulas': []}
        return self.detected_regions[number]


class ConversionIsolationTests(unittest.TestCase):
    def setUp(self):
        self.originals = [(cls, name, getattr(cls, name)) for cls, name in HOOKS]
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.restore_hooks)
        self.folder = Path(self.temp.name)
        for name, width, count in [('first', 300, 2), ('second', 400, 1)]:
            with fitz.open() as doc:
                for _ in range(count):
                    page = doc.new_page(width=width, height=300)
                    page.insert_text((50, 70), 'KEEP ME')
                doc.save(self.folder / (name + '.pdf'))

    def restore_hooks(self):
        for cls, name, method in self.originals:
            setattr(cls, name, method)

    def modules(self):
        for path in [ROOT / 'hybrid_converter.py', ROOT / 'freep2w/hybrid_converter.py']:
            spec = importlib.util.spec_from_file_location('converter_under_test', path)
            module = importlib.util.module_from_spec(spec)
            with patch.dict(sys.modules, {'torch': types.ModuleType('torch'),
                                        'doclayout_yolo': types.SimpleNamespace(YOLOv10=None)}):
                spec.loader.exec_module(module)
            yield module

    def converter(self, module):
        converter = module.HybridConverter.__new__(module.HybridConverter)
        converter.yolo_detector = Detector()
        return converter

    def run_conversion(self, converter, name, output, **kwargs):
        converter.convert(str(self.folder / (name + '.pdf')),
                          str(self.folder / (output + '.docx')), **kwargs)
        doc = Document(self.folder / (output + '.docx'))
        return ([p.text for p in doc.paragraphs], len(doc.inline_shapes))

    def test_reused_converter_matches_fresh_instance(self):
        for module in self.modules():
            with self.subTest(module=module.__file__):
                self.restore_hooks()
                reused = self.converter(module)
                self.run_conversion(reused, 'first', 'first')
                actual = self.run_conversion(reused, 'second', 'reused', yolo_conf=0.5)
                self.restore_hooks()  # independent baseline, including on buggy code
                expected = self.run_conversion(self.converter(module), 'second', 'fresh', yolo_conf=0.5)
                self.assertEqual(actual, expected)
                self.assertIn('KEEP ME', ''.join(actual[0]))
                self.assertEqual(reused.yolo_detector.calls, 3)
                self.assertEqual(set(reused.yolo_detector.detected_regions), {0})

    def test_hooks_restored_after_success_and_failure(self):
        for module in self.modules():
            for fail in [False, True]:
                with self.subTest(module=module.__file__, fail=fail):
                    self.restore_hooks()
                    converter = self.converter(module)
                    if fail:
                        original_close = module.Converter.close
                        closed = []
                        def close(instance):
                            closed.append(instance)
                            return original_close(instance)
                        with patch.object(module.Converter, 'convert', side_effect=RuntimeError('test failure')), patch.object(module.Converter, 'close', close):
                            with self.assertRaisesRegex(RuntimeError, 'test failure'):
                                self.run_conversion(converter, 'first', 'failure')
                        self.assertEqual(len(closed), 1)
                    else:
                        self.run_conversion(converter, 'first', 'success')
                    for cls, name, method in self.originals:
                        self.assertIs(getattr(cls, name), method)
                    result = self.run_conversion(converter, 'second', 'plain', use_yolo_images=False)
                    self.assertIn('KEEP ME', ''.join(result[0]))
                    self.assertEqual(result[1], 0)


if __name__ == '__main__':
    unittest.main()
