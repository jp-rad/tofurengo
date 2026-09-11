import pytest
from tofurengo.resource import (
    normalize_version,
    resolve_wheel_name,
    load_dataset_module,
    extract_required_symbols,
    get_resource,
    ResourceError,
)

# ------------------------------------------------------------
# normalize_version
# ------------------------------------------------------------

def test_normalize_version_basic():
    assert normalize_version("6.02.201") == "v6_02_201"

def test_normalize_version_with_suffix():
    assert normalize_version("6.02.201-onka") == "v6_02_201_onka"

def test_normalize_version_strip_spaces():
    assert normalize_version("  4.10.0  ") == "v4_10_0"

def test_normalize_version_mixed_separators():
    assert normalize_version("1-20_a") == "v1_20_a"


# ------------------------------------------------------------
# resolve_wheel_name (fallback only)
# ------------------------------------------------------------

def test_resolve_wheel_name_fallback():
    name = resolve_wheel_name("tofurengo_data.mj.v6_02_201")
    assert name == "tofurengo-data-mj-v6-02-201"


# ------------------------------------------------------------
# load_dataset_module
# ------------------------------------------------------------

def test_load_dataset_module_not_found():
    with pytest.raises(ResourceError):
        load_dataset_module("tofurengo_data", "unknown_set", "1.0")


# ------------------------------------------------------------
# extract_required_symbols
# ------------------------------------------------------------

class DummyModuleOK:
    GLYPH_TABLE = {"A": 1}
    VERSION = "v1"

class DummyModuleMissing:
    GLYPH_TABLE = {"A": 1}

def test_extract_required_symbols_ok():
    out = extract_required_symbols(DummyModuleOK)
    assert out["GLYPH_TABLE"] == {"A": 1}
    assert out["VERSION"] == "v1"

def test_extract_required_symbols_missing():
    with pytest.raises(ResourceError):
        extract_required_symbols(DummyModuleMissing)


# ------------------------------------------------------------
# get_resource (integration)
# ------------------------------------------------------------

def test_get_resource_missing_module():
    with pytest.raises(ResourceError):
        get_resource("unknown", "1.0")

