"""Disposable files only; model setup is mocked, DOCX writing is real."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch
from docx import Document
from freep2w import cli
from freep2w.output_utils import safe_output


class OutputSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'input.pdf'
        self.original = b'%PDF-disposable-original'
        self.pdf.write_bytes(self.original)
        self.output = self.root / 'output.docx'
        spec = importlib.util.spec_from_file_location('source_cli', Path(__file__).resolve().parents[1] / 'freep2w.py')
        self.source = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.source)

    def run_cli(self, module, output, *, overwrite=False, fail=False):
        downloader = Mock(return_value=('model', 'config'))
        def write(**kwargs):
            doc = Document()
            doc.add_paragraph('converted')
            doc.save(kwargs['docx_path'])
            if fail:
                raise RuntimeError('failure after saving')
        converter = Mock()
        converter.return_value.convert.side_effect = write
        modules = {'freep2w.model_downloader': types.SimpleNamespace(check_and_download_models=downloader),
                   'freep2w.hybrid_converter': types.SimpleNamespace(HybridConverter=converter),
                   'hybrid_converter': types.SimpleNamespace(HybridConverter=converter),
                   'pdf2docx': types.SimpleNamespace(Converter=Mock())}
        with patch.dict('sys.modules', modules), contextlib.redirect_stdout(io.StringIO()):
            result = module.convert_pdf_to_docx(str(self.pdf), str(output), overwrite=overwrite)
        return result, downloader, converter

    def test_existing_output_refused_before_model_setup(self):
        for module in (cli, self.source):
            with self.subTest(module=module.__name__):
                self.output.write_bytes(b'valuable existing output')
                ok, downloader, converter = self.run_cli(module, self.output)
                self.assertFalse(ok)
                downloader.assert_not_called()
                converter.assert_not_called()
                self.assertEqual(self.output.read_bytes(), b'valuable existing output')

    def test_input_aliases_refused_even_with_overwrite(self):
        symlink = self.root / 'alias.docx'
        symlink.symlink_to(self.pdf)
        hardlink = self.root / 'hardlink.docx'
        os.link(self.pdf, hardlink)
        for module in (cli, self.source):
            for target in (self.pdf, symlink, hardlink):
                for overwrite in (False, True):
                    with self.subTest(module=module.__name__, target=target, overwrite=overwrite):
                        ok, downloader, converter = self.run_cli(module, target, overwrite=overwrite)
                        self.assertFalse(ok)
                        downloader.assert_not_called()
                        converter.assert_not_called()
                        self.assertEqual(self.pdf.read_bytes(), self.original)

    def test_success_and_failure_publish_only_complete_output(self):
        for module in (cli, self.source):
            for existing in (False, True):
                for fail in (False, True):
                    with self.subTest(module=module.__name__, existing=existing, fail=fail):
                        if self.output.exists(): self.output.unlink()
                        if existing: self.output.write_bytes(b'valuable existing output')
                        ok, _, _ = self.run_cli(module, self.output, overwrite=existing, fail=fail)
                        self.assertEqual(ok, not fail)
                        if fail:
                            if existing: self.assertEqual(self.output.read_bytes(), b'valuable existing output')
                            else: self.assertFalse(self.output.exists())
                        else:
                            self.assertEqual(Document(self.output).paragraphs[0].text, 'converted')
                        self.assertEqual(self.pdf.read_bytes(), self.original)
                        self.assertEqual(list(self.root.glob('.freep2w-*')), [])

    def test_late_output_collision_preserves_other_file(self):
        with self.assertRaises(FileExistsError):
            with safe_output(self.pdf, self.output) as staged:
                Path(staged).write_bytes(b'new output')
                self.output.write_bytes(b'created during conversion')
        self.assertEqual(self.output.read_bytes(), b'created during conversion')
        self.assertEqual(list(self.root.glob('.freep2w-*')), [])

    def test_dangling_symlink_is_not_followed(self):
        target = self.root / 'missing-target'
        self.output.symlink_to(target)
        ok, _, converter = self.run_cli(cli, self.output)
        self.assertFalse(ok)
        converter.assert_not_called()
        self.assertFalse(target.exists())
        self.assertTrue(self.output.is_symlink())


if __name__ == '__main__':
    unittest.main()
