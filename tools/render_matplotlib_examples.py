"""Load a generated mplstyle and render illustrative charts with Matplotlib/Agg.

Usage: python tools/render_matplotlib_examples.py RUN [ISOLATED_DEPENDENCIES]
Matplotlib is optional; it is not required by the theme generator.
"""
import io
import json
import logging
import sys
import hashlib
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
    # Older preserved runs have the same value keys without label metadata.
    point_count = max(len(values) for values in data["lines"])
    data.setdefault("hatches", ["/", "\\", "|", "-", "+", "x"])
    data.setdefault("markers", ["o", "s", "^", "D", "v", "+"])
    data.setdefault("dash_patterns", ["none", "12 6", "3 5", "12 5 3 5", "18 5", "6 4"])
    data.setdefault("periods", [f"Period {i}" for i in range(1, point_count + 1)])
    data.setdefault("series_labels", [f"Series {i}" for i in range(1, len(data["lines"]) + 1)])
    data.setdefault("heatmap_columns", data["categories"][:len(data["heatmap"][0])])
    data.setdefault("heatmap_rows", [f"Row {i}" for i in range(1, len(data["heatmap"]) + 1)])
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
            counts = {}
            for kind in ("bars", "lines", "heatmap"):
                fig, ax = plt.subplots(figsize=(12, 6.75), layout="constrained")
                if kind == "bars":
                    bars = ax.bar(data["categories"], data["bars"],
                                  color=[series[i % 6] for i in range(len(data["bars"]))],
                                  edgecolor=result["tokens"]["panel"]["hex"])
                    for i, bar in enumerate(bars):
                        bar.set_hatch(data["hatches"][i % 6])
                    assert [bar.get_height() for bar in bars] == data["bars"]
                    counts["bars"] = len(bars)
                    ax.tick_params(axis="x", labelsize=9)
                    ax.set_axisbelow(True)
                    ax.set_ylim(0, 80)
                    for i, value in enumerate(data["bars"]):
                        ax.text(i, value + 2, str(value), ha="center")
                    ax.set_ylabel("Illustrative units")
                elif kind == "lines":
                    for i, values in enumerate(data["lines"]):
                        dash = data["dash_patterns"][i]
                        linestyle = "-" if dash == "none" else (0, tuple(float(v) for v in dash.split()))
                        line, = ax.plot(range(1, len(values)+1), values, marker=data["markers"][i],
                                        linestyle=linestyle, label=data["series_labels"][i])
                        assert list(line.get_ydata()) == values
                    counts["lines"] = [len(line.get_ydata()) for line in ax.lines]
                    ax.set_ylim(0, 80)
                    ticks = sorted({int(i * (point_count - 1) / 6) for i in range(7)})
                    ax.set_xticks([i+1 for i in ticks], [data["periods"][i] for i in ticks])
                    ax.set_ylabel("Illustrative units")
                    ax.legend(ncols=3, loc="upper center", bbox_to_anchor=(.5, -.1), fontsize=9)
                else:
                    image = ax.imshow(data["heatmap"], cmap=ListedColormap(scales["sequential"]), vmin=0, vmax=8)
                    assert image.get_array().tolist() == data["heatmap"]
                    counts["heatmap"] = list(image.get_array().shape)
                    ax.grid(False)
                    ax.set_xticks(range(len(data["heatmap_columns"])), data["heatmap_columns"])
                    ax.set_yticks(range(len(data["heatmap_rows"])), data["heatmap_rows"])
                    fig.colorbar(image, ax=ax, ticks=range(9), label="Illustrative level")
                ax.set_title(f"{kind.title()} / illustrative data")
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
                artists = []
                for axes in fig.axes:
                    artists += [axes.title, axes.xaxis.label, axes.yaxis.label,
                                *axes.get_xticklabels(), *axes.get_yticklabels(), *axes.texts]
                artists = [artist for artist in artists if artist.get_text()]
                if ax.get_legend() is not None:
                    artists.append(ax.get_legend())
                for artist in artists:
                    bounds = artist.get_window_extent(renderer)
                    assert bounds.x0 >= 0 and bounds.y0 >= 0 and bounds.x1 <= fig.bbox.width and bounds.y1 <= fig.bbox.height, str(artist)
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
                "data_sha256": hashlib.sha256((directory / "example-data.json").read_bytes()).hexdigest(),
                "data_assertions": counts, "text_bounds": "passed",
                "scope": "Local style loading and static Agg render; no interactive GUI or external application import."}
    (run / "matplotlib-render-evidence.json").write_text(json.dumps(evidence, indent=2)+"\n")
    print(f"Loaded style without diagnostics; rendered {len(outputs)} Matplotlib artifacts.")


if __name__ == "__main__":
    render(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else None)
