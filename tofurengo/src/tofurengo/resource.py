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


def resolve_wheel_name(module_name: str) -> str:
    """
    Resolve installed wheel distribution name for a module.

    If metadata lookup fails, fallback to hyphenated module path.
    """
    try:
        dist_map = packages_distributions()
        parts = module_name.split(".")

        # Try full path → parent namespaces
        for i in range(len(parts), 0, -1):
            ns = ".".join(parts[:i])
            dists = dist_map.get(ns)
            if dists:
                return dists[0]
    except Exception:
        pass

    # Fallback heuristic
    return module_name.replace(".", "-").replace("_", "-")


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

