"""Generate clean hero banner and gold logo from assets/sample.png."""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "sample.png"
BANNER_OUT = ASSETS / "hero-banner.png"
LOGO_OUT = ASSETS / "logo-gold-silhouette.png"

# Gold palette (RGB) — matches site CSS
GOLD_DARK = np.array([139, 105, 20], dtype=np.float32)
GOLD_MID = np.array([201, 168, 76], dtype=np.float32)
GOLD_LIGHT = np.array([245, 208, 122], dtype=np.float32)


def load_source() -> np.ndarray:
    image = cv2.imread(str(SOURCE))
    if image is None:
        raise FileNotFoundError(f"Could not read {SOURCE}")
    return image


def person_crop(image: np.ndarray) -> np.ndarray:
    """Crop to subject area — excludes left text and bottom address."""
    h, w = image.shape[:2]
    x1 = int(w * 0.44)
    y1 = int(h * 0.02)
    x2 = w
    y2 = int(h * 0.86)
    return image[y1:y2, x1:x2].copy()


def build_banner(image: np.ndarray) -> None:
    """Banner = crop only (no inpaint blur)."""
    banner = person_crop(image)
    banner = cv2.convertScaleAbs(banner, alpha=1.04, beta=4)
    cv2.imwrite(str(BANNER_OUT), banner, [cv2.IMWRITE_PNG_COMPRESSION, 3])


def fill_holes(mask: np.ndarray) -> np.ndarray:
    """Fill interior holes in the subject mask."""
    h, w = mask.shape
    flood = mask.copy()
    fill_mask = np.zeros((h + 2, w + 2), np.uint8)
    cv2.floodFill(flood, fill_mask, (0, 0), 255)
    holes = cv2.bitwise_not(flood)
    return cv2.bitwise_or(mask, holes)


def refine_alpha(alpha: np.ndarray) -> np.ndarray:
    _, alpha = cv2.threshold(alpha, 32, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel, iterations=3)
    alpha = fill_holes(alpha)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel, iterations=1)
    alpha = cv2.GaussianBlur(alpha, (5, 5), 0)
    _, alpha = cv2.threshold(alpha, 127, 255, cv2.THRESH_BINARY)
    return alpha


def tight_crop_rgba(rgba: np.ndarray, padding: int = 12) -> np.ndarray:
    alpha = rgba[:, :, 3]
    coords = cv2.findNonZero(alpha)
    if coords is None:
        return rgba
    x, y, w, h = cv2.boundingRect(coords)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(rgba.shape[1], x + w + padding)
    y2 = min(rgba.shape[0], y + h + padding)
    return rgba[y1:y2, x1:x2]


def gold_gradient(h: int, w: int) -> np.ndarray:
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    grad = np.where(
        y < 0.5,
        GOLD_DARK + (GOLD_MID - GOLD_DARK) * (y / 0.5),
        GOLD_MID + (GOLD_LIGHT - GOLD_MID) * ((y - 0.5) / 0.5),
    )
    return np.repeat(grad[:, None, :], w, axis=1).astype(np.uint8)


def build_logo(image: np.ndarray) -> None:
    """Logo = person cutout via rembg, filled with gold gradient."""
    crop = person_crop(image)
    pil = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    cutout = remove(pil)  # RGBA
    rgba = np.array(cutout)
    alpha = refine_alpha(rgba[:, :, 3])

    h, w = alpha.shape
    rgb = gold_gradient(h, w)

    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[:, :, :3] = rgb
    out[:, :, 3] = alpha
    out = tight_crop_rgba(out, padding=16)

    Image.fromarray(out, mode="RGBA").save(LOGO_OUT, optimize=True)


if __name__ == "__main__":
    src = load_source()
    build_banner(src)
    build_logo(src)
    print(f"Generated: {BANNER_OUT.name}, {LOGO_OUT.name}")
