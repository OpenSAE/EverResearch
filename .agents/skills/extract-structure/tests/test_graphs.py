"""Purpose and main functions: Exercise mixed folder discovery, saved article details and independent HTML export.

Scope: Explicit developer checks using local samples and skill-owned temporary results; originals stay unchanged.
"""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL / 'scripts'))
import article_graph
import folder_graph
import graph_store
from export_page import export


class MixedFolder(unittest.TestCase):
    def test_save_discover_export_and_source_changes(self):
        results = SKILL / 'results'
        results.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='check-graphs-', dir=results) as temporary:
            home = Path(temporary)
            project = home / 'source'
            project.mkdir()
            (project / 'module.py').write_text('def read():\n    return 1\n')
            (project / 'README.MD').write_text('# Usage\nExplain this module.\n')
            (project / 'notes.md').write_text('# Notes\nAdditional source.\n')
            with patch.object(graph_store, 'SKILL', home / 'generated'):
                store = graph_store.Store(project)
                folder_graph.configure(store)
                _, files = folder_graph.inventory(project, recursive=True)
                self.assertEqual(set(files), {'module.py', 'README.MD', 'notes.md'})
                prefix = project.name + '/'
                evidence = [{'path': prefix + 'README.MD', 'lines': [1, 2]}]
                article = article_graph.build({'source': prefix + 'README.MD', 'purpose': 'Explain usage', 'coverage': 'All source lines',
                    'groups': [{'id': 'usage', 'name': 'Usage', 'nodes': [
                        {'id': 'text', 'name': 'Read usage', 'meaning': 'Read the original explanation.', 'source': evidence}]}]}, project.parent)
                graph_store.write_graph(store, graph_store.graph_id_for(article['source']), article, 'Save local article detail')
                recipe = {'purpose': 'Browse implementation and documentation',
                    'files': {name: {'name': name, 'purpose': 'Describe ' + name, 'scope': 'This selected folder',
                                     'meaning': 'Explain this actual source file.'} for name in files},
                    'groups': [{'id': 'sources', 'name': 'Sources', 'meaning': 'Read the selected inputs.', 'files': list(files)}], 'edges': []}
                identity, _ = folder_graph.store(project, recipe, recursive=True)
                data, _ = graph_store.read_graph(store, identity)
                self.assertEqual(len(data['graphs']['L2']['nodes']), 3)
                from server import graph_payload
                payload = graph_payload(store, identity)
                self.assertTrue(any(h.get('detail_graph', {}).get('source') == prefix + 'README.MD'
                                    for h in payload['graph']['display']['L2']['nodes'].values()))
                delivered = export(store, data['source'], 'mixed-folder', theme='dark')
                html = Path(delivered['path']).read_text()
                self.assertIn('extractStructureBundle', html)
                self.assertNotIn('<script src=', html)
                self.assertEqual(delivered['graph_count'], 2)
                current = folder_graph.discover(project, recursive=True)['files']['README.MD']
                self.assertTrue(current['current'])
                (project / 'README.MD').write_text('# Revised\nA newer source explanation.\n')
                changed = folder_graph.discover(project, recursive=True)['files']['README.MD']
                self.assertTrue(changed['usable'])
                self.assertFalse(changed['current'])
                folder_graph.configure(store, exclude=['notes.md'])
                self.assertEqual(set(folder_graph.inventory(project, recursive=True)[1]), {'module.py', 'README.MD'})


if __name__ == '__main__':
    unittest.main()
