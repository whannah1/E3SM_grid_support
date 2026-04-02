"""
Unit tests for swag/config.py.

Tests cover _is_blank(), _expand(), swag_config loading, key access,
derived paths, validation, export helpers, machine detection, and
alternate constructors.

Run with:
    python -m pytest tests/test_config.py -v
"""

import os
import sys
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from swag.config import (
    _is_blank,
    _expand,
    swag_config,
    swag_config_error,
)


# ---------------------------------------------------------------------------
# Minimal machines YAML used across all tests

MINIMAL_MACHINES = {
    '_required_keys': {
        'paths': ['grid_data_root', 'e3sm_src_root'],
        'slurm': ['account'],
    },
    'TESTMACH': {
        'detection': {'probe_path': '/nonexistent/testmach'},
        'paths': {
            'grid_data_root': '/mach/data',
            'e3sm_src_root':  '/mach/e3sm',
            'DIN_LOC_ROOT':   '/mach/inputdata',
            'unified_bin':    '/mach/bin',
            'unified_src':    '/mach/load.sh',
            'homme_tool_root': '',
            'mbda_path':      '/mach/mbda',
            'topo_file_src':  '/mach/topo.nc',
        },
        'slurm': {
            'mail_user':  '',
            'mail_type':  'END,FAIL',
            'account':    'e3sm',
            'constraint': '',
            'qos':        'regular',
        }
    },
    'OTHERMACH': {
        'detection': {'probe_path': '/exists/othermach'},
        'paths': {
            'grid_data_root': '/other/data',
            'e3sm_src_root':  '/other/e3sm',
            'DIN_LOC_ROOT':   '/other/inputdata',
            'unified_bin':    '/other/bin',
            'unified_src':    '/other/load.sh',
            'homme_tool_root': '',
            'mbda_path':      '/other/mbda',
            'topo_file_src':  '/other/topo.nc',
        },
        'slurm': {
            'mail_user':  '',
            'mail_type':  'END,FAIL',
            'account':    'other_account',
            'constraint': '',
            'qos':        'regular',
        }
    },
}


# ---------------------------------------------------------------------------
# Helpers

def write_machines_yaml(tmp_path) -> Path:
    """Write MINIMAL_MACHINES to tmp_path/machines.yaml and return the Path."""
    machines_path = tmp_path / 'machines.yaml'
    machines_path.write_text(yaml.dump(MINIMAL_MACHINES))
    return machines_path


def make_cfg(tmp_path, machines_yaml_path, project_overrides=None):
    """
    Write a minimal project.yaml with machine=TESTMACH into tmp_path, optionally
    deep-merging project_overrides, then load swag_config with _MACHINES_YAML patched.
    """
    base = {
        'machine': {'name': 'TESTMACH'},
        'project': {'name': 'myproj', 'timestamp': '20240101'},
        'grid':    {'name': 'ne30pg2'},
    }
    if project_overrides:
        for section, values in project_overrides.items():
            if section in base and isinstance(base[section], dict):
                base[section].update(values)
            else:
                base[section] = values

    proj_yaml = tmp_path / 'project.yaml'
    proj_yaml.write_text(yaml.dump(base))

    with patch('swag.config._MACHINES_YAML', machines_yaml_path):
        return swag_config(proj_yaml)


# ===========================================================================
# TestIsBlank

class TestIsBlank:

    def test_none_is_blank(self):
        assert _is_blank(None) is True

    def test_empty_string_is_blank(self):
        assert _is_blank('') is True

    def test_unset_is_blank(self):
        assert _is_blank('UNSET') is True

    def test_yyyymmdd_is_blank(self):
        assert _is_blank('YYYYMMDD') is True

    def test_none_string_is_blank(self):
        assert _is_blank('None') is True

    def test_none_lower_is_blank(self):
        assert _is_blank('none') is True

    def test_null_is_blank(self):
        assert _is_blank('null') is True

    def test_whitespace_padded_unset_is_blank(self):
        assert _is_blank('  UNSET  ') is True

    def test_real_value_not_blank(self):
        assert _is_blank('value') is False

    def test_zero_string_not_blank(self):
        assert _is_blank('0') is False

    def test_false_string_not_blank(self):
        assert _is_blank('false') is False

    def test_hello_not_blank(self):
        assert _is_blank('hello') is False

    def test_integer_not_blank(self):
        assert _is_blank(42) is False


# ===========================================================================
# TestExpand

class TestExpand:

    def test_expands_env_var_in_string(self):
        os.environ['_SWAG_TEST_VAR'] = '/some/test/path'
        result = _expand('$_SWAG_TEST_VAR/sub')
        assert result == '/some/test/path/sub'

    def test_nested_dict_values_expanded(self):
        os.environ['_SWAG_TEST_VAR'] = '/root'
        result = _expand({'key1': '$_SWAG_TEST_VAR/a', 'nested': {'key2': '$_SWAG_TEST_VAR/b'}})
        assert result['key1'] == '/root/a'
        assert result['nested']['key2'] == '/root/b'

    def test_list_values_expanded(self):
        os.environ['_SWAG_TEST_VAR'] = '/base'
        result = _expand(['$_SWAG_TEST_VAR/x', '$_SWAG_TEST_VAR/y'])
        assert result == ['/base/x', '/base/y']

    def test_non_string_int_passed_through(self):
        result = _expand(99)
        assert result == 99

    def test_non_string_none_passed_through(self):
        result = _expand(None)
        assert result is None


# ===========================================================================
# TestSwagConfigLoading

class TestSwagConfigLoading:

    def test_file_not_found_raises(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        nonexistent = tmp_path / 'project.yaml'
        with patch('swag.config._MACHINES_YAML', machines_path):
            with pytest.raises(FileNotFoundError):
                swag_config(nonexistent)

    def test_loads_successfully(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        assert cfg is not None

    def test_machine_attribute(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        assert cfg.machine == 'TESTMACH'

    def test_paths_from_machine_defaults(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        assert cfg.paths['grid_data_root'] == '/mach/data'

    def test_project_value_overrides_machine_default(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path, project_overrides={
            'paths': {'grid_data_root': '/proj/override/data'}
        })
        assert cfg.paths['grid_data_root'] == '/proj/override/data'

    def test_blank_project_value_defers_to_machine_default(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path, project_overrides={
            'paths': {'grid_data_root': ''}
        })
        assert cfg.paths['grid_data_root'] == '/mach/data'

    def test_homme_tool_root_derived_when_blank(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        # machine yaml has homme_tool_root='', so it should be derived from e3sm_src_root
        assert cfg.paths['homme_tool_root'] == '/mach/e3sm/cmake_homme'

    def test_homme_tool_root_not_overridden_when_set(self, tmp_path):
        # Build a machines yaml where homme_tool_root is explicitly set
        machines_with_homme = dict(MINIMAL_MACHINES)
        machines_with_homme['TESTMACH'] = dict(MINIMAL_MACHINES['TESTMACH'])
        machines_with_homme['TESTMACH']['paths'] = dict(MINIMAL_MACHINES['TESTMACH']['paths'])
        machines_with_homme['TESTMACH']['paths']['homme_tool_root'] = '/explicit/homme'

        machines_path = tmp_path / 'machines_homme.yaml'
        machines_path.write_text(yaml.dump(machines_with_homme))

        cfg = make_cfg(tmp_path, machines_path)
        assert cfg.paths['homme_tool_root'] == '/explicit/homme'


# ===========================================================================
# TestSwagConfigKeyAccess

class TestSwagConfigKeyAccess:

    @pytest.fixture
    def cfg(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        return make_cfg(tmp_path, machines_path)

    def test_getitem_returns_value(self, cfg):
        assert cfg['paths.grid_data_root'] == '/mach/data'

    def test_getitem_nonexistent_raises_key_error(self, cfg):
        with pytest.raises(KeyError):
            _ = cfg['paths.nonexistent']

    def test_getitem_blank_value_raises_key_error(self, cfg):
        # mail_user is '' in TESTMACH slurm defaults → blank → KeyError
        with pytest.raises(KeyError):
            _ = cfg['slurm.mail_user']

    def test_get_returns_value(self, cfg):
        assert cfg.get('paths.grid_data_root') == '/mach/data'

    def test_get_nonexistent_returns_default(self, cfg):
        assert cfg.get('paths.nonexistent', 'default') == 'default'

    def test_get_missing_returns_none_by_default(self, cfg):
        assert cfg.get('paths.nonexistent') is None


# ===========================================================================
# TestSwagConfigDerived

class TestSwagConfigDerived:

    @pytest.fixture
    def cfg(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        return make_cfg(tmp_path, machines_path)

    def test_data_root(self, cfg):
        assert cfg.derived['data_root'] == '/mach/data/myproj'

    def test_grid_root(self, cfg):
        assert cfg.derived['grid_root'] == '/mach/data/myproj/files_grid'

    def test_maps_root(self, cfg):
        assert cfg.derived['maps_root'] == '/mach/data/myproj/files_map'

    def test_topo_root(self, cfg):
        assert cfg.derived['topo_root'] == '/mach/data/myproj/files_topo'

    def test_init_root(self, cfg):
        assert cfg.derived['init_root'] == '/mach/data/myproj/files_init'

    def test_domn_root(self, cfg):
        assert cfg.derived['domn_root'] == '/mach/data/myproj/files_domain'

    def test_slurm_log_root(self, cfg, tmp_path):
        assert cfg.derived['slurm_log_root'] == str(tmp_path / 'logs_batch')

    def test_hiccup_log_root(self, cfg, tmp_path):
        assert cfg.derived['hiccup_log_root'] == str(tmp_path / 'logs_hiccup')

    def test_derived_empty_when_project_name_blank(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path, project_overrides={
            'project': {'name': 'UNSET'}
        })
        assert cfg.derived['data_root'] == ''
        assert cfg.derived['grid_root'] == ''
        assert cfg.derived['maps_root'] == ''
        assert cfg.derived['topo_root'] == ''
        assert cfg.derived['init_root'] == ''
        assert cfg.derived['domn_root'] == ''


# ===========================================================================
# TestSwagConfigValidate

class TestSwagConfigValidate:

    def test_validate_passes_when_all_required_set(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        # Should not raise — all required keys have values
        cfg.validate(required_keys=['paths.grid_data_root', 'paths.e3sm_src_root',
                                    'slurm.account', 'project.name', 'grid.name'])

    def test_validate_raises_listing_missing_keys(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        # Remove project.name and timestamp so they are missing
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'TESTMACH'},
            'project': {'name': 'UNSET', 'timestamp': 'UNSET'},
            'grid':    {'name': 'UNSET'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            cfg = swag_config(proj_yaml)
        with pytest.raises(swag_config_error) as exc_info:
            cfg.validate(required_keys=['project.name', 'project.timestamp', 'grid.name'])
        msg = str(exc_info.value)
        assert 'project.name' in msg
        assert 'project.timestamp' in msg
        assert 'grid.name' in msg

    def test_validate_error_message_mentions_count(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'TESTMACH'},
            'project': {'name': 'UNSET', 'timestamp': 'UNSET'},
            'grid':    {'name': 'UNSET'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            cfg = swag_config(proj_yaml)
        with pytest.raises(swag_config_error) as exc_info:
            cfg.validate(required_keys=['project.name', 'project.timestamp', 'grid.name'])
        msg = str(exc_info.value)
        assert '3' in msg

    def test_validate_custom_required_keys(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        # Only check project.name — should pass since it's set
        cfg.validate(required_keys=['project.name'])

    def test_validate_custom_required_keys_missing_raises(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'TESTMACH'},
            'project': {'name': 'UNSET'},
            'grid':    {'name': 'ne30pg2'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            cfg = swag_config(proj_yaml)
        with pytest.raises(swag_config_error):
            cfg.validate(required_keys=['project.name'])


# ===========================================================================
# TestSwagConfigExport

class TestSwagConfigExport:

    @pytest.fixture
    def cfg(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        return make_cfg(tmp_path, machines_path)

    def test_to_env_dict_contains_grid_data_root(self, cfg):
        env = cfg.to_env_dict()
        assert 'grid_data_root' in env
        assert env['grid_data_root'] == '/mach/data'

    def test_to_env_dict_contains_e3sm_src_root(self, cfg):
        env = cfg.to_env_dict()
        assert 'e3sm_src_root' in env

    def test_to_env_dict_contains_proj(self, cfg):
        env = cfg.to_env_dict()
        assert 'proj' in env
        assert env['proj'] == 'myproj'

    def test_to_env_dict_contains_grid_name(self, cfg):
        env = cfg.to_env_dict()
        assert 'grid_name' in env
        assert env['grid_name'] == 'ne30pg2'

    def test_to_env_dict_contains_swag_host(self, cfg):
        env = cfg.to_env_dict()
        assert 'swag_host' in env
        assert env['swag_host'] == 'TESTMACH'

    def test_to_env_dict_contains_swag_slurm_account(self, cfg):
        env = cfg.to_env_dict()
        assert 'swag_slurm_account' in env
        assert env['swag_slurm_account'] == 'e3sm'

    def test_as_dict_contains_dot_notation_path_key(self, cfg):
        d = cfg.as_dict()
        assert 'paths.grid_data_root' in d
        assert d['paths.grid_data_root'] == '/mach/data'

    def test_as_dict_contains_project_name(self, cfg):
        d = cfg.as_dict()
        assert 'project.name' in d
        assert d['project.name'] == 'myproj'

    def test_as_dict_all_values_are_strings(self, cfg):
        d = cfg.as_dict()
        for k, v in d.items():
            assert isinstance(v, str), f"Key {k!r} has non-string value {v!r}"


# ===========================================================================
# TestMachineDetection

class TestMachineDetection:

    def test_explicit_machine_name_used(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        cfg = make_cfg(tmp_path, machines_path)
        assert cfg.machine == 'TESTMACH'

    def test_unknown_machine_name_raises(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'UNKNOWNMACH'},
            'project': {'name': 'myproj'},
            'grid':    {'name': 'ne30pg2'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            with pytest.raises(swag_config_error) as exc_info:
                swag_config(proj_yaml)
        assert 'UNKNOWNMACH' in str(exc_info.value)

    def test_auto_detect_othermach(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        # No machine override — rely on auto-detection
        proj_yaml.write_text(yaml.dump({
            'project': {'name': 'myproj'},
            'grid':    {'name': 'ne30pg2'},
        }))

        def fake_exists(path):
            return path == '/exists/othermach'

        with patch('swag.config._MACHINES_YAML', machines_path):
            with patch('swag.config.os.path.exists', side_effect=fake_exists):
                cfg = swag_config(proj_yaml)

        assert cfg.machine == 'OTHERMACH'

    def test_auto_detect_no_match_raises(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'project': {'name': 'myproj'},
            'grid':    {'name': 'ne30pg2'},
        }))

        with patch('swag.config._MACHINES_YAML', machines_path):
            with patch('swag.config.os.path.exists', return_value=False):
                with pytest.raises(swag_config_error) as exc_info:
                    swag_config(proj_yaml)
        assert 'auto-detect' in str(exc_info.value).lower() or 'machine' in str(exc_info.value).lower()


# ===========================================================================
# TestAlternateConstructors

class TestAlternateConstructors:

    def test_from_project_yaml(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'TESTMACH'},
            'project': {'name': 'myproj', 'timestamp': '20240101'},
            'grid':    {'name': 'ne30pg2'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            cfg = swag_config.from_project_yaml(proj_yaml)
        assert cfg.machine == 'TESTMACH'

    def test_from_project_dir(self, tmp_path):
        machines_path = write_machines_yaml(tmp_path)
        proj_yaml = tmp_path / 'project.yaml'
        proj_yaml.write_text(yaml.dump({
            'machine': {'name': 'TESTMACH'},
            'project': {'name': 'myproj', 'timestamp': '20240101'},
            'grid':    {'name': 'ne30pg2'},
        }))
        with patch('swag.config._MACHINES_YAML', machines_path):
            cfg = swag_config.from_project_dir(tmp_path)
        assert cfg.machine == 'TESTMACH'
        assert cfg.project['name'] == 'myproj'
