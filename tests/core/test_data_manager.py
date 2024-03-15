import json
from pathlib import Path

from core import data_manager
import pytest


@pytest.fixture(autouse=True)
def cleanup_datamanager():
    data_manager.basic_config = None
    data_manager.jsonio = None


@pytest.fixture()
def data_mgr_config(tmpdir):
    default = data_manager.basic_config_default.copy()
    default['BASE_DIR'] = str(tmpdir)
    return default


@pytest.fixture()
def cog_instance():
    thing = type('CogTest', (object, ), {})
    return thing()


def test_no_basic(cog_instance):
    with pytest.raises(RuntimeError):
        data_manager.core_data_path()

    with pytest.raises(RuntimeError):
        data_manager.cog_data_path(cog_instance)


def test_core_path(data_mgr_config, tmpdir):
    conf_path = tmpdir.join('config.json')
    conf_path.write(json.dumps(data_mgr_config))

    data_manager.load_basic_configuration(Path(str(conf_path)))

    assert data_manager.core_data_path().parent == Path(data_mgr_config['BASE_DIR'])
