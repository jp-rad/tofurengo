"""
Dynamic dataset resource loader for the tofurengo library.

ASCII-only comments only.
"""

import importlib
from importlib.metadata import packages_distributions
import re
from typing import Any, Dict


DEFAULT_BASE_NAMESPACE: str = "tofurengo_data"


class ResourceError(Exception):
    """Raised when a dataset module or required symbol cannot be loaded."""
    pass


def normalize_version(version: str) -> str:
    """
    Normalize external version string into internal module identifier.

    Rules:
        - Strip whitespace
        - Replace '.', '-', '_' with '_'
        - Prefix with 'v'

    Example:
        "6.02.201-onka" -> "v6_02_201_onka"
    """
    ver = version.strip()
    ver = re.sub(r"[.\-_]", "_", ver)
    return f"v{ver}"

def normalize_name(name: str) -> str:
    """Normalize a module or package name according to PEP 503 rules.

    Converts characters to lowercase and replaces runs of separator characters
    (`-`, `_`, `.`) with a single hyphen `-`.

    Args:
        name: The module or package name string to normalize.

    Returns:
        The PEP 503 normalized name string.
    """
    return re.sub(r"[-_.]+", "-", name).lower()


def resolve_wheel_name(module_name: str) -> str:
    """Resolve the installed distribution package name for a given module.

    This function normalizes the input module name and compares it against
    the normalized distribution names listed in the metadata environment.
    If no matching installed distribution is found, it falls back to the
    normalized module name.

    Args:
        module_name: The module or namespace path (e.g.,
            `tofurengo_data.mj_plusx.v1_20`).

    Returns:
        The exact distribution package name as registered in metadata if found;
        otherwise, the normalized `module_name`.

    Examples:
        >>> resolve_wheel_name("tofurengo_data.mj_plusx.v1_20")
        'tofurengo-data-mj-plusx-v1-20'

        >>> resolve_wheel_name("yaml")
        'PyYAML'
    """
    # 1. Normalize module_name
    norm_module_name = normalize_name(module_name)

    try:
        # 2. Retrieve metadata distribution mapping
        dist_map = packages_distributions()

        # 3. Normalize each distribution name in dists and compare
        for dists in dist_map.values():
            for dist in dists:
                if normalize_name(dist) == norm_module_name:
                    return dist
    except Exception:
        pass

    # 4. Fallback to normalized module_name
    return norm_module_name


def load_dataset_module(base: str, glyph_set: str, version: str):
    """
    Build module path and import it.

    Example:
        base="tofurengo_data"
        glyph_set="mj"
        version="6.02.201"
        → "tofurengo_data.mj.v6_02_201"
    """
    gs = glyph_set.strip()
    ver_norm = normalize_version(version)
    base_ns = base.strip()

    module_name = f"{base_ns}.{gs}.{ver_norm}"

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as err:
        raise ResourceError(f"Dataset module not found: {module_name}") from err


def extract_required_symbols(mod) -> Dict[str, Any]:
    """
    Extract required dataset symbols.

    Required:
        GLYPH_TABLE : dict
        VERSION     : str
    """
    required = ["GLYPH_TABLE", "VERSION"]
    missing = [sym for sym in required if not hasattr(mod, sym)]

    if missing:
        raise ResourceError(
            f"Dataset module '{mod.__name__}' missing symbols: {missing}"
        )

    return {
        "GLYPH_TABLE": getattr(mod, "GLYPH_TABLE"),
        "VERSION": getattr(mod, "VERSION"),
    }


def get_resource(
    glyph_set: str,
    version: str,
    base: str = DEFAULT_BASE_NAMESPACE,
) -> Dict[str, Any]:
    """
    Load dataset module and return required symbols + wheel name.
    """
    mod = load_dataset_module(base, glyph_set, version)
    symbols = extract_required_symbols(mod)
    wheel_name = resolve_wheel_name(mod.__name__)

    return {
        **symbols,
        "LIBRARY_NAME": wheel_name,
    }

