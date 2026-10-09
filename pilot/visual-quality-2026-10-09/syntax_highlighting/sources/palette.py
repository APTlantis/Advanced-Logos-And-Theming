"""Illustrative palette review with immutable entries."""
from dataclasses import dataclass
import re

HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")


@dataclass(frozen=True)
class Color:
    identifier: str
    hex: str
    weight: float = 0.0

    def label(self) -> str:
        return f"{self.identifier}: {self.hex.upper()}"


def summarize(colors: list[Color]) -> dict[str, object]:
    if any(not HEX_COLOR.fullmatch(color.hex) for color in colors):
        raise ValueError("Expected six-digit RGB colors")
    selected = [color.label() for color in colors if color.weight > 0]
    return {"count": len(selected), "labels": selected, "illustrative": True}


if __name__ == "__main__":
    palette = [
        Color("color_01", "#302820", 0.6),
        Color("color_02", "#C8A868", 0.4),
    ]
    try:
        print(summarize(palette))
    except ValueError as error:
        print(f"Review failed: {error}")
