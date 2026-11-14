"""Invalid input must not trigger model setup or leave files in the user's home."""
import contextlib
import io
import os
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from freep2w import cli


class CliValidationTests(unittest.TestCase):
    def test_invalid_input_never_downloads_models(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp) / 'home'
            home.mkdir()
            def download():
                (Path.home() / 'download-was-started').touch()
                return 'model.pt', 'demo.yaml'
            downloader = Mock(side_effect=download)
            module = types.SimpleNamespace(check_and_download_models=downloader)
            with patch.dict(os.environ, {'HOME': str(home), 'USERPROFILE': str(home)}), patch.dict('sys.modules', {'freep2w.model_downloader': module}), contextlib.redirect_stdout(io.StringIO()):
                for path in (Path(temp) / 'missing.pdf', home):
                    with self.subTest(path=path):
                        self.assertFalse(cli.convert_pdf_to_docx(str(path)))
                        downloader.assert_not_called()
                        self.assertEqual(list(home.iterdir()), [])
                with patch('sys.argv', ['freep2w', str(Path(temp) / 'missing.pdf')]):
                    with self.assertRaises(SystemExit) as exit_result:
                        cli.main()
                    self.assertEqual(exit_result.exception.code, 1)
                    downloader.assert_not_called()

    def test_existing_file_still_downloads_then_converts(self):
        with tempfile.TemporaryDirectory() as temp:
            pdf = Path(temp) / 'input.pdf'
            pdf.write_bytes(b'%PDF-1.7\n')
            downloader = Mock(return_value=('model.pt', 'demo.yaml'))
            converter = Mock()
            modules = {
                'freep2w.model_downloader': types.SimpleNamespace(check_and_download_models=downloader),
                'freep2w.hybrid_converter': types.SimpleNamespace(HybridConverter=converter),
                'pdf2docx': types.SimpleNamespace(Converter=Mock()),
            }
            output = str(Path(temp) / 'output.docx')
            with patch.dict('sys.modules', modules), contextlib.redirect_stdout(io.StringIO()):
                self.assertTrue(cli.convert_pdf_to_docx(str(pdf), output))
            downloader.assert_called_once_with()
            converter.assert_called_once_with(yolo_model_path='model.pt', unimernet_cfg_path='demo.yaml')
            converter.return_value.convert.assert_called_once_with(pdf_path=str(pdf), docx_path=output)


if __name__ == '__main__':
    unittest.main()
