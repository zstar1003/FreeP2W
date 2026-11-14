"""Keep legacy setuptools metadata aligned with the declared Python minimum."""
import ast
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PythonRequirementTests(unittest.TestCase):
    def test_setup_and_pyproject_require_python_310(self):
        tree = ast.parse((ROOT / 'setup.py').read_text(encoding='utf-8'))
        setup = next(node for node in ast.walk(tree)
                     if isinstance(node, ast.Call)
                     and isinstance(node.func, ast.Name)
                     and node.func.id == 'setup')
        keywords = {item.arg: item.value for item in setup.keywords}
        self.assertEqual(ast.literal_eval(keywords['python_requires']), '>=3.10')
        project = (ROOT / 'pyproject.toml').read_text(encoding='utf-8')
        requirement = re.search(r'^requires-python\s*=\s*"([^"]+)"', project, re.M)
        self.assertIsNotNone(requirement)
        self.assertEqual(requirement.group(1), '>=3.10')
        classifiers = ast.literal_eval(keywords['classifiers'])
        for old_version in ('3.8', '3.9'):
            self.assertNotIn('Programming Language :: Python :: ' + old_version,
                             classifiers)


if __name__ == '__main__':
    unittest.main()
