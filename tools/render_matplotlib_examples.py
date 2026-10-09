"""Load a generated mplstyle and render illustrative charts with Matplotlib/Agg.

Usage: python tools/render_matplotlib_examples.py RUN [ISOLATED_DEPENDENCIES]
Matplotlib is optional; it is not required by the theme generator.
"""
import io
import json
import logging
import sys
from pathlib import Path


def render(run, dependencies=None):
    if dependencies:
        sys.path.insert(0, str(dependencies.resolve()))
    import matplotlib as mpl
    mpl.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap, to_hex
    run = run.resolve()
    directory = run / "data_visualization"
    result = json.loads((directory / "tokens.json").read_text())
    data = json.loads((directory / "example-data.json").read_text())
    scales = json.loads((directory / "scales.json").read_text())
    style = next(directory.glob("*.mplstyle"))
    messages = io.StringIO()
    handler = logging.StreamHandler(messages)
    logging.getLogger("matplotlib").addHandler(handler)
    try:
        with plt.style.context(style):
            assert to_hex(mpl.rcParams["axes.facecolor"]).upper() == result["tokens"]["panel"]["hex"]
            series = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
            assert [to_hex(c).upper() for c in series] == [result["tokens"][f"series_{i}"]["hex"] for i in range(1, 7)]
            outputs = []
            for kind in ("bars", "lines", "heatmap"):
                fig, ax = plt.subplots(figsize=(9.6, 5.4), layout="constrained")
                if kind == "bars":
                    ax.bar(data["categories"], data["bars"], color=series[:4], hatch="//")
                    ax.set_ylim(0, 80)
                    for i, value in enumerate(data["bars"]):
                        ax.text(i, value + 2, str(value), ha="center")
                    ax.set_ylabel("Illustrative units")
                elif kind == "lines":
                    for i, values in enumerate(data["lines"], 1):
                        ax.plot(range(1, 5), values, marker="o" if i == 1 else "s", label=f"Series {i}")
                    ax.set_ylim(0, 80)
                    ax.set_xticks(range(1, 5), [f"Period {i}" for i in range(1, 5)])
                    ax.set_ylabel("Illustrative units")
                    ax.legend()
                else:
                    image = ax.imshow(data["heatmap"], cmap=ListedColormap(scales["sequential"]), vmin=0, vmax=8)
                    ax.grid(False)
                    ax.set_xticks(range(4), data["categories"])
                    ax.set_yticks(range(3), [f"Row {i}" for i in range(1, 4)])
                    fig.colorbar(image, ax=ax, ticks=range(9), label="Illustrative level")
                ax.set_title(f"{kind.title()} / illustrative data")
                for extension in ("png", "svg"):
                    filename = f"matplotlib-{kind}.{extension}"
                    fig.savefig(directory / filename, dpi=100)
                    outputs.append(filename)
                plt.close(fig)
        if messages.getvalue():
            raise ValueError("Matplotlib diagnostics: " + messages.getvalue())
    finally:
        logging.getLogger("matplotlib").removeHandler(handler)
    evidence = {"matplotlib_version": mpl.__version__, "backend": "Agg", "style": style.name,
                "parser_diagnostics": messages.getvalue(), "style_color_assertions": "passed", "outputs": outputs,
                "scope": "Local style loading and static Agg render; no interactive GUI or external application import."}
    (run / "matplotlib-render-evidence.json").write_text(json.dumps(evidence, indent=2)+"\n")
    print(f"Loaded style without diagnostics; rendered {len(outputs)} Matplotlib artifacts.")


if __name__ == "__main__":
    render(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None)
