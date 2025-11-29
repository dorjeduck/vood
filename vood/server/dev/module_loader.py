"""
Module reloading for development server.

Safely reloads Python animation modules with proper cleanup.
"""

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Optional, Tuple, Callable

from vood.vscene import VScene

# Registry for @animation decorated functions
_animation_registry = {}


def animation(func: Callable) -> Callable:
    """
    Decorator to mark a function as the main animation for the dev server.

    Usage:
        @animation
        def my_scene():
            return VScene(...)

    This is optional - only needed when you have multiple VScenes in a module.
    """
    _animation_registry[func.__module__] = func
    return func


def extract_scene(module) -> Tuple[Optional[VScene], Optional[str]]:
    """
    Extract VScene from a module using priority order.

    Priority order:
    1. @animation decorator (if present, always wins)
    2. Variable named 'scene' (optional convention)
    3. Function named 'create_scene()' (optional convention)
    4. Any VScene instance (fallback, must be only one)
    5. Any function returning VScene (fallback, must be only one)

    Args:
        module: The loaded Python module

    Returns:
        Tuple of (VScene instance or None, error message or None)
    """
    module_name = module.__name__

    # Priority 1: @animation decorator
    if module_name in _animation_registry:
        decorated_func = _animation_registry[module_name]
        try:
            scene = decorated_func()
            if isinstance(scene, VScene):
                return scene, None
            return None, f"@animation decorated function '{decorated_func.__name__}' did not return a VScene"
        except Exception as e:
            return None, f"Error calling @animation decorated function: {str(e)}"

    # Priority 2: 'scene' variable (convention)
    if hasattr(module, "scene"):
        scene = getattr(module, "scene")
        if isinstance(scene, VScene):
            return scene, None

    # Priority 3: 'create_scene()' function (convention)
    if hasattr(module, "create_scene"):
        create_scene_fn = getattr(module, "create_scene")
        if callable(create_scene_fn):
            try:
                scene = create_scene_fn()
                if isinstance(scene, VScene):
                    return scene, None
            except Exception as e:
                return None, f"Error calling create_scene(): {str(e)}"

    # Priority 4 & 5: Auto-detect any VScene or function returning VScene
    vscenes = []
    vscene_funcs = []

    for name in dir(module):
        if name.startswith("_"):  # Skip private attributes
            continue

        attr = getattr(module, name)

        # Check for VScene instances
        if isinstance(attr, VScene):
            vscenes.append((name, attr))

        # Check for functions that might return VScene
        elif callable(attr) and not isinstance(attr, type):  # Exclude classes
            # We can't call arbitrary functions to check return type
            # So we just collect them
            vscene_funcs.append((name, attr))

    # If exactly one VScene instance found, use it
    if len(vscenes) == 1:
        return vscenes[0][1], None

    # If multiple VScenes found, error with helpful message
    if len(vscenes) > 1:
        scene_list = "\n".join(f"  - {name}" for name, _ in vscenes)
        return None, (
            f"Found multiple VScene instances:\n{scene_list}\n\n"
            "Please use one of these solutions:\n"
            "  1. Remove unused scenes\n"
            "  2. Use @animation decorator to mark your main scene\n"
            "  3. Rename your main scene to 'scene'"
        )

    # No VScene found
    return None, None


def file_path_to_module_name(file_path: Path) -> str:
    """
    Convert file path to a unique module name.

    Args:
        file_path: Path to the Python file

    Returns:
        Module name string
    """
    # Use absolute path to ensure uniqueness
    abs_path = file_path.resolve()
    # Replace path separators with dots, remove .py extension
    module_name = f"vood_devserver_{abs_path.stem}_{abs(hash(str(abs_path)))}"
    return module_name


def safe_reload_module(file_path: Path) -> Tuple[Optional[VScene], Optional[str]]:
    """
    Safely reload a Python animation module.

    This function:
    1. Removes the module from sys.modules to force clean reload
    2. Imports the module fresh using importlib
    3. Extracts the VScene using priority order (see extract_scene)

    Args:
        file_path: Path to the Python animation file

    Returns:
        Tuple of (VScene instance or None, error string or None)
        - On success: (scene, None)
        - On failure: (None, error_message)
    """
    try:
        # Ensure file exists
        if not file_path.exists():
            return None, f"File not found: {file_path}"

        # Generate unique module name
        module_name = file_path_to_module_name(file_path)

        # Remove from sys.modules to force clean reload
        if module_name in sys.modules:
            del sys.modules[module_name]

        # Clear from animation registry if present
        if module_name in _animation_registry:
            del _animation_registry[module_name]

        # Import fresh
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None, f"Could not load module spec from: {file_path}"

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Extract scene using priority order
        scene, error = extract_scene(module)

        if error:
            # extract_scene returned an error message
            return None, error

        if scene is None:
            # No scene found and no specific error
            return None, (
                "No VScene found in module.\n\n"
                "Your animation file should contain a VScene. Examples:\n\n"
                "  # Simple (any variable name works):\n"
                "  my_animation = VScene(...)\n\n"
                "  # Convention (optional):\n"
                "  scene = VScene(...)\n\n"
                "  # Function (optional):\n"
                "  def create_scene():\n"
                "      return VScene(...)\n\n"
                "  # Decorator (for multiple scenes):\n"
                "  from vood.server.dev import animation\n"
                "  @animation\n"
                "  def my_scene():\n"
                "      return VScene(...)"
            )

        return scene, None

    except SyntaxError as e:
        error_msg = f"Syntax Error in {file_path.name}:\n{str(e)}"
        return None, error_msg

    except Exception as e:
        error_msg = f"Error loading {file_path.name}:\n{traceback.format_exc()}"
        return None, error_msg
