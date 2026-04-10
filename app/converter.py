import os
import logging
from dataclasses import dataclass

import cascadio

logger = logging.getLogger(__name__)


@dataclass
class ConversionResult:
    obj_path: str
    file_size_bytes: int
    vertex_count: int
    face_count: int


def _count_obj_geometry(obj_path: str) -> tuple[int, int]:
    """Parse an OBJ file and return (vertex_count, face_count)."""
    vertices = 0
    faces = 0
    with open(obj_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("v "):
                vertices += 1
            elif stripped.startswith("f "):
                faces += 1
    return vertices, faces


def convert_step_to_obj(
    step_path: str,
    obj_path: str,
    linear_tolerance: float = 0.001,
    angular_tolerance: float = 0.5,
) -> ConversionResult:
    """
    Read a STEP file and write it as OBJ using cascadio (OpenCASCADE).

    Raises ValueError for bad input, RuntimeError for conversion failures.
    """
    if not os.path.isfile(step_path):
        raise FileNotFoundError(f"STEP file not found: {step_path}")

    ext = os.path.splitext(step_path)[1].lower()
    if ext not in (".step", ".stp"):
        raise ValueError(f"Unsupported file extension '{ext}'. Expected .step or .stp")

    step_path_posix = step_path.replace("\\", "/")
    obj_path_posix = obj_path.replace("\\", "/")

    logger.info("Converting STEP -> OBJ: %s", step_path)
    try:
        cascadio.step_to_obj(
            step_path_posix,
            obj_path_posix,
            tol_linear=linear_tolerance,
            tol_angular=angular_tolerance,
        )
    except Exception as exc:
        raise RuntimeError(f"Conversion failed: {exc}") from exc

    if not os.path.isfile(obj_path):
        raise RuntimeError("OBJ file was not created — conversion may have failed silently")

    file_size = os.path.getsize(obj_path)
    vertex_count, face_count = _count_obj_geometry(obj_path)

    logger.info(
        "Conversion complete: %d vertices, %d faces, %.1f KB",
        vertex_count,
        face_count,
        file_size / 1024,
    )

    return ConversionResult(
        obj_path=obj_path,
        file_size_bytes=file_size,
        vertex_count=vertex_count,
        face_count=face_count,
    )
