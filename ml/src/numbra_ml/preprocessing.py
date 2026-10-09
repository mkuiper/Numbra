"""PLACEHOLDER letterbox contract shared by training and later M4 export.

Explicit half-pixel bilinear coordinates, clamped edges, no antialias filter.
Decode/orientation remains the loader's responsibility; this accepts RGB only.
"""

import numpy as np

SPEC = {
    "version": "1.0.0", "notice": "PLACEHOLDER — not clinically validated",
    "input": "oriented uint8 HWC RGB, nonempty dimensions <=4096, <=16777216 pixels",
    "size": 224, "padding_rgb": [128, 128, 128],
    "resize": "bilinear half-pixel centres, edge clamp, no antialias",
    "dimensions": "scale=min(224/w,224/h); half-up rounding; clamp 1..224",
    "padding": "centred; odd extra right/bottom",
    "rounding": "interpolated RGB half-up to uint8 before normalisation",
    "mean": [0.485, 0.456, 0.406], "std": [0.229, 0.224, 0.225],
    "output": "contiguous float32 CHW; batch externally to NCHW",
    "geometry_warning": "letterbox differs from publisher bicubic centre-crop",
}


def preprocess(rgb: np.ndarray) -> np.ndarray:
    if (not isinstance(rgb, np.ndarray) or rgb.dtype != np.uint8 or rgb.ndim != 3
            or rgb.shape[2] != 3 or min(rgb.shape[:2]) < 1
            or max(rgb.shape[:2]) > 4096):
        raise ValueError("preprocessing requires bounded nonempty uint8 HWC RGB")
    height, width = rgb.shape[:2]
    size = SPEC["size"]
    scale = min(size / width, size / height)
    out_w = min(size, max(1, int(np.floor(width * scale + 0.5))))
    out_h = min(size, max(1, int(np.floor(height * scale + 0.5))))
    x = np.clip((np.arange(out_w, dtype=np.float64) + 0.5) * width / out_w - 0.5, 0, width - 1)
    y = np.clip((np.arange(out_h, dtype=np.float64) + 0.5) * height / out_h - 0.5, 0, height - 1)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    x1, y1 = np.minimum(x0 + 1, width - 1), np.minimum(y0 + 1, height - 1)
    wx, wy = (x - x0)[None, :, None], (y - y0)[:, None, None]
    top = rgb[y0[:, None], x0[None, :]].astype(np.float64) * (1 - wx) + rgb[y0[:, None], x1[None, :]] * wx
    bottom = rgb[y1[:, None], x0[None, :]].astype(np.float64) * (1 - wx) + rgb[y1[:, None], x1[None, :]] * wx
    resized = np.floor(top * (1 - wy) + bottom * wy + 0.5).clip(0, 255).astype(np.uint8)
    boxed = np.full((size, size, 3), 128, dtype=np.uint8)
    left, upper = (size - out_w) // 2, (size - out_h) // 2
    boxed[upper:upper + out_h, left:left + out_w] = resized
    normalised = (boxed.astype(np.float32) / np.float32(255) - np.array(SPEC["mean"], dtype=np.float32)) / np.array(SPEC["std"], dtype=np.float32)
    return np.ascontiguousarray(normalised.transpose(2, 0, 1))
