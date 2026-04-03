"""
Unit tests for swag/grid.py.

These tests cover pure-Python logic (command-string construction, path checks)
without requiring any HPC tools, SLURM, or real files on disk.
run_cmd() and os.path.exists() are mocked throughout.

Run with:
    python -m pytest tests/test_grid.py
"""
import sys
import unittest
from pathlib import Path
from unittest.mock import call, MagicMock, patch


from swag.grid import (
    _e3sm_env_prefix,
    _grid_paths,
    create_grid,
)

# ---------------------------------------------------------------------------
# helpers

class MockConfig:
    """Minimal stand-in for swag_config with fixed test values."""

    _data = {
        'grid.name':              'ne30',
        'derived.grid_root':      '/data/grids',
        'paths.homme_tool_root':  '/homme',
        'paths.unified_bin':      '/unified/bin',
        'paths.e3sm_src_root':    '/e3sm',
    }

    def __getitem__(self, key):
        return self._data[key]

    def get(self, key, default=None):
        return self._data.get(key, default)


# ---------------------------------------------------------------------------
# _e3sm_env_prefix

class TestE3smEnvPrefix(unittest.TestCase):

    def test_returns_eval_command(self):
        cfg = MockConfig()
        result = _e3sm_env_prefix(cfg)
        self.assertEqual(result, 'eval $(/e3sm/cime/CIME/Tools/get_case_env)')


# ---------------------------------------------------------------------------
# _grid_paths

class TestGridPaths(unittest.TestCase):

    def setUp(self):
        self.p = _grid_paths(MockConfig())

    def test_grid_file_exodus(self):
        self.assertEqual(self.p['grid_file_exodus'], '/data/grids/ne30.g')

    def test_grid_file_np4_scrip(self):
        self.assertEqual(self.p['grid_file_np4_scrip'], '/data/grids/ne30np4_scrip.nc')

    def test_grid_file_np4_mbda(self):
        self.assertEqual(self.p['grid_file_np4_mbda'], '/data/grids/ne30np4_mbda.nc')

    def test_grid_file_pg2_scrip(self):
        self.assertEqual(self.p['grid_file_pg2_scrip'], '/data/grids/ne30pg2_scrip.nc')

    def test_grid_file_pg2_mbda(self):
        self.assertEqual(self.p['grid_file_pg2_mbda'], '/data/grids/ne30pg2_mbda.nc')

    def test_grid_file_3km_exodus(self):
        self.assertEqual(self.p['grid_file_3km_exodus'], '/data/grids/ne3000.g')

    def test_grid_file_3km_scrip(self):
        self.assertEqual(self.p['grid_file_3km_scrip'], '/data/grids/ne3000pg1_scrip.nc')

    def test_grid_file_3km_mbda(self):
        self.assertEqual(self.p['grid_file_3km_mbda'], '/data/grids/ne3000pg1_mbda.nc')

    def test_grid_template_file(self):
        self.assertEqual(self.p['grid_template_file'], '/homme/ne30_ne0np4_tmp1.nc')

    def test_nl_file(self):
        self.assertEqual(self.p['nl_file'], '/homme/input.grd.ne30.nl')


# ---------------------------------------------------------------------------
# create_grid — main command tests
#
# Default scenario: no stale template (exists[0]=False), all outputs succeed,
# 3km_mbda already present (skip creation).
#   exists call order:
#     [0] grid_template_file  — stale check        → False (no rm)
#     [1] grid_template_file  — success check       → True
#     [2] grid_file_np4_mbda  — success check       → True
#     [3] grid_file_pg2_mbda  — success check       → True
#     [4] grid_file_3km_mbda  — already-exists check → True (skip)

class TestCreateGridCommands(unittest.TestCase):

    _DEFAULT_EXISTS = [False, True, True, True, True]

    def _run(self, exists_side_effect=None):
        """Execute create_grid with mocked run_cmd and os.path.exists."""
        if exists_side_effect is None:
            exists_side_effect = list(self._DEFAULT_EXISTS)
        with patch('swag.grid.run_cmd') as mock_run, \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            create_grid(MockConfig())
        return mock_run

    def _all_cmds(self, mock_run):
        return [c.args[0] for c in mock_run.call_args_list]

    # ------------------------------------------------------------------
    # homme_tool invocation

    def test_homme_tool_command(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        matching = [c for c in cmds if 'srun' in c and 'homme_tool' in c]
        self.assertEqual(len(matching), 1)
        nl_file = _grid_paths(MockConfig())['nl_file']
        self.assertIn(nl_file, matching[0])

    # ------------------------------------------------------------------
    # HOMME2SCRIP conversion

    def test_homme2scrip_command(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        matching = [c for c in cmds if 'HOMME2SCRIP.py' in c]
        self.assertEqual(len(matching), 1)
        self.assertIn('--src_file', matching[0])
        self.assertIn('--dst_file', matching[0])

    # ------------------------------------------------------------------
    # np4 MBDA file creation

    def test_np4_mbda_commands(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        p = _grid_paths(MockConfig())
        ncap2_cmds = [c for c in cmds
                      if 'ncap2' in c and p['grid_file_np4_scrip'] in c]
        self.assertEqual(len(ncap2_cmds), 1)
        ncrename_cmds = [c for c in cmds
                         if 'ncrename' in c and p['grid_file_np4_mbda'] in c]
        self.assertEqual(len(ncrename_cmds), 1)

    # ------------------------------------------------------------------
    # PG2 exodus and SCRIP

    def test_pg2_commands(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        vol_cmds = [c for c in cmds if 'GenerateVolumetricMesh' in c]
        self.assertEqual(len(vol_cmds), 1)
        scrip_cmds = [c for c in cmds if 'ConvertMeshToSCRIP' in c]
        self.assertEqual(len(scrip_cmds), 1)

    # ------------------------------------------------------------------
    # PG2 MBDA file creation

    def test_pg2_mbda_commands(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        p = _grid_paths(MockConfig())
        ncap2_cmds = [c for c in cmds
                      if 'ncap2' in c and p['grid_file_pg2_scrip'] in c]
        self.assertEqual(len(ncap2_cmds), 1)
        ncrename_cmds = [c for c in cmds
                         if 'ncrename' in c and p['grid_file_pg2_mbda'] in c]
        self.assertEqual(len(ncrename_cmds), 1)

    # ------------------------------------------------------------------
    # 3km grid skipped when already present

    def test_3km_skipped_when_exists(self):
        mock_run = self._run()
        cmds = self._all_cmds(mock_run)
        self.assertFalse(any('GenerateCSMesh' in c for c in cmds))

    # ------------------------------------------------------------------
    # stale template removal

    def test_stale_template_removed(self):
        # First call for grid_template_file → True (stale file present)
        exists_side_effect = [True, True, True, True, True]
        with patch('swag.grid.run_cmd') as mock_run, \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            create_grid(MockConfig())
        cmds = [c.args[0] for c in mock_run.call_args_list]
        rm_cmds = [c for c in cmds if c.startswith('rm ')]
        self.assertEqual(len(rm_cmds), 1)
        self.assertIn(_grid_paths(MockConfig())['grid_template_file'], rm_cmds[0])

    # ------------------------------------------------------------------
    # RuntimeError when homme_tool output missing

    def test_raises_when_homme_tool_fails(self):
        # exists[1] (grid_template_file success check) → False
        exists_side_effect = [False, False, True, True, True]
        with patch('swag.grid.run_cmd'), \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            with self.assertRaises(RuntimeError) as ctx:
                create_grid(MockConfig())
        self.assertIn('homme_tool', str(ctx.exception))

    # ------------------------------------------------------------------
    # RuntimeError when np4 MBDA file missing

    def test_raises_when_np4_mbda_missing(self):
        # exists[2] (np4_mbda success check) → False
        exists_side_effect = [False, True, False, True, True]
        with patch('swag.grid.run_cmd'), \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            with self.assertRaises(RuntimeError) as ctx:
                create_grid(MockConfig())
        self.assertIn('np4', str(ctx.exception))

    # ------------------------------------------------------------------
    # RuntimeError when pg2 MBDA file missing

    def test_raises_when_pg2_mbda_missing(self):
        # exists[3] (pg2_mbda success check) → False
        exists_side_effect = [False, True, True, False, True]
        with patch('swag.grid.run_cmd'), \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            with self.assertRaises(RuntimeError) as ctx:
                create_grid(MockConfig())
        self.assertIn('pg2', str(ctx.exception))

    # ------------------------------------------------------------------
    # 3km grid created when missing
    #   exists call order with 3km creation path:
    #     [0] grid_template_file  — stale check        → False
    #     [1] grid_template_file  — success check       → True
    #     [2] grid_file_np4_mbda  — success check       → True
    #     [3] grid_file_pg2_mbda  — success check       → True
    #     [4] grid_file_3km_mbda  — already-exists check → False (create)
    #     [5] grid_file_3km_exodus — success check      → True
    #     [6] grid_file_3km_scrip  — success check      → True

    def test_3km_created_when_missing(self):
        exists_side_effect = [False, True, True, True, False, True, True]
        with patch('swag.grid.run_cmd') as mock_run, \
             patch('swag.grid.os.path.exists', side_effect=exists_side_effect), \
             patch('pathlib.Path.write_text'):
            create_grid(MockConfig())
        cmds = [c.args[0] for c in mock_run.call_args_list]
        self.assertTrue(any('GenerateCSMesh' in c for c in cmds))

    # ------------------------------------------------------------------
    # namelist written correctly

    def test_namelist_written(self):
        captured = {}

        def fake_write_text(self_path, content):
            captured['content'] = content

        with patch('swag.grid.run_cmd'), \
             patch('swag.grid.os.path.exists', side_effect=list(self._DEFAULT_EXISTS)), \
             patch('pathlib.Path.write_text', fake_write_text):
            create_grid(MockConfig())

        self.assertIn('content', captured)
        nl = captured['content']
        self.assertIn('mesh_file', nl)
        self.assertIn('grid_template_tool', nl)
        self.assertIn('ne30_', nl)


# ---------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
