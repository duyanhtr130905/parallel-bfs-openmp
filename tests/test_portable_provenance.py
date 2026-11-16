"""Portable checks use published text only; no private raw or D: backup."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('audit', ROOT / 'scripts/audit_final_evidence.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class PortableProvenance(unittest.TestCase):
    def fixture(self, root, ending):
        paths = list(audit.PUBLICATION_TEXT_V1.values()) + ['results/experiment-20261112/provenance.json']
        for name in paths:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            data = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
            target.write_bytes(data.replace(b'\n', ending))

    def test_published_hashes_lf_crlf_and_tampering(self):
        for ending in (b'\n', b'\r\n'):
            with self.subTest(ending=ending), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                self.fixture(root, ending)
                audit.audit_publication_text(root)
                # Figure provenance must use the same historical plotter hash.
                for provenance in (ROOT / 'report/figures/experiment-20261112').glob('*/provenance.json'):
                    expected = json.loads(provenance.read_text())['plot_script_sha256']
                    self.assertEqual(audit.publication_digest_v1('scripts/plot_results.py', root), expected)
                for name in audit.PUBLICATION_TEXT_V1.values():
                    path = root / name
                    original = path.read_bytes()
                    path.write_bytes(original + b'changed content')
                    with self.assertRaisesRegex(ValueError, 'publication provenance'):
                        audit.audit_publication_text(root)
                    path.write_bytes(original)

    def test_byte_exact_evidence_is_not_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ('raw.jsonl', 'manifest.json', 'dataset.json', 'bfs.exe', 'figure.pdf'):
                path = root / name
                path.write_bytes(b'evidence\r\n')
                before = audit.digest(path)
                self.assertEqual(before, hashlib.sha256(path.read_bytes()).hexdigest())
                path.write_bytes(b'evidence\n')
                self.assertNotEqual(before, audit.digest(path))
                with self.assertRaisesRegex(ValueError, 'unregistered'):
                    audit.publication_digest_v1(name, root)

    def test_reject_mixed_bare_cr_and_preserve_other_bytes(self):
        name = 'scripts/plot_results.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, b'\n')
            path = root / name
            original = path.read_bytes()
            for content in (b'a\r\nb\n', b'a\rb'):
                path.write_bytes(content)
                with self.assertRaises(ValueError):
                    audit.publication_digest_v1(name, root)
            for content in (b'\xef\xbb\xbf' + original, original.rstrip(b'\n'), original + b' '):
                path.write_bytes(content)
                with self.assertRaisesRegex(ValueError, 'publication provenance'):
                    audit.audit_publication_text(root)


if __name__ == '__main__':
    unittest.main()
