from dataclasses import dataclass
from datetime import date
from typing import Dict, Tuple, Optional

import argparse
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Circle

import targets


@dataclass
class PlotConfig:
    target: Dict[str, float]
    moa: float


@dataclass
class CLIArgs:
    filename: str
    prefix: str
    distance: int
    x: int = 0
    y: int = 0


def parse_args() -> CLIArgs:
    """
    Parse the command-line arguments and return a CLIArgs object.
    
    :return: Description
    :rtype: CLIArgs
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The csv file to process")
    parser.add_argument("--prefix", required=True, help="Prefix for the output files")
    parser.add_argument("--distance", type=int, required=True, help="Distance in meters")
    parser.add_argument("--x", type=int, default=0, help="X offset in mm")
    parser.add_argument("--y", type=int, default=0, help="Y offset in mm")
    args = parser.parse_args()
    return CLIArgs(
        filename=args.filename,
        prefix=args.prefix,
        distance=args.distance,
        x=args.x,
        y=args.y,
    )


def load_dataframe(filename: str) -> pd.DataFrame:
    return pd.read_csv(filename)


def split_by_id(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    left_df = df[df["id"].str.startswith("L")]
    middle_df = df[df["id"].str.startswith("M")]
    right_df = df[df["id"].str.startswith("R")]
    return left_df, middle_df, right_df


def dist_config(distance: int) -> Optional[PlotConfig]:
    mapping = {
        300: PlotConfig(target=targets.target_300m, moa=targets.moa_300m),
        500: PlotConfig(target=targets.target_500m, moa=targets.moa_500m),
        600: PlotConfig(target=targets.target_600m, moa=targets.moa_600m),
        700: PlotConfig(target=targets.target_700m, moa=targets.moa_700m),
        800: PlotConfig(target=targets.target_800m, moa=targets.moa_800m),
        900: PlotConfig(target=targets.target_900m, moa=targets.mmoa_900m),
    }
    return mapping.get(distance)


def configure_axes(ax, df: pd.DataFrame, distance: int, moa: float, x: int, y: int) -> None:
    ax.set_aspect("equal")

    if x == 0:
        x_max_value = 300 if not df["x mm"].max() > 300 else df["x mm"].max()
        x_min_value = -300 if not df["x mm"].min() < -300 else df["x mm"].min()
    else:
        x_max_value = 300
        x_min_value = -300

    if y == 0:
        y_max_value = 300 if not df["y mm"].max() > 300 else df["y mm"].max()
        y_min_value = -300 if not df["y mm"].min() < -300 else df["y mm"].min()
    else:
        y_max_value = 300
        y_min_value = -300

    ax.set_xlim(x_min_value - 50, x_max_value + 50)
    ax.set_ylim(y_min_value - 50, y_max_value + 50)

    for label, radius in distance_label_colors_and_radii(df, moas=None):  # helper to keep function small
        ring = Circle((0, 0), radius, color="black", fill=False, linewidth=1)
        ax.add_patch(ring)
        ax.annotate(
            label,
            (radius, 0),
            xytext=(5, 0),
            ha="left",
            color="green",
            textcoords="offset points",
            fontsize=7,
        )

    major_spacing_xy = moa  # Major grid lines every moa units on x/y
    minor_spacing_xy = moa * 0.5
    ax.xaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.yaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.grid(which="major", linestyle="--", linewidth="0.75", alpha=0.5, color="gray")
    ax.grid(which="minor", linestyle="-.", linewidth="0.75", alpha=0.5, color="gray")


def distance_label_colors_and_radii(_df: pd.DataFrame, moas=None):
    # This is a placeholder if you want to compute ring labels differently.
    # For now, return a static set to keep compatibility.
    return [(str(k), k) for k in []]


def render_plot(ax, df: pd.DataFrame, target: Dict[str, float], moa: float, distance: int, name: str, x: int, y: int) -> None:
    # Add target rings and annotations
    for label, radius in target.items():
        ring = Circle((0, 0), radius, color="black", fill=False, linewidth=1)
        ax.add_patch(ring)
        ax.annotate(
            label,
            (radius, 0),
            xytext=(5, 0),
            ha="left",
            color="green",
            textcoords="offset points",
            fontsize=7,
        )

    configure_axes(ax, df, distance, moa, x, y)

    today = date.today().strftime("%d-%b-%Y")
    countX = df['score'].value_counts().to_dict().get('X', 0)
    filtered_values = df[df['score'] != 'X']['score']
    score = filtered_values.astype(int).sum()
    score += countX * 6

    ax.set_title(f"{distance}m - {name}\n\n{today}\n{score}.{countX}")

    for _, row in df.iterrows():
        xval, yval = row["x mm"], row["y mm"]
        s = row["id"].replace("L", "").replace("M", "").replace("R", "")
        label = s + "\n(" + row["score"] + ")"
        colour = "red" if "S" in label else "blue"
        plt.scatter(xval, yval, color=colour, marker="x", label="")
        ax.annotate(label, (xval, yval), textcoords="offset points", xytext=(0, 10), ha="center")

    # Centroid / Median / Max distance visuals
    centroid_x = df["x mm"].mean()
    centroid_y = df["y mm"].mean()
    plt.scatter(centroid_x, centroid_y, color="orange", marker="+", label=f"Centroid Center ({centroid_x:.1f}, {centroid_y:.1f})")

    median_x = df["x mm"].median()
    median_y = df["y mm"].median()
    plt.scatter(median_x, median_y, color="purple", marker="2", label=f"Median Center ({median_x:.1f}, {median_y:.1f})")

    max_distance = 0
    furthest_pair = None
    for i, row1 in df.iterrows():
        for j, row2 in df.iterrows():
            if i >= j:
                continue
            dist = ((row1["x mm"] - row2["x mm"]) ** 2 + (row1["y mm"] - row2["y mm"]) ** 2) ** 0.5
            if 'S' in row1['id'] or 'S' in row2['id']:
                break
            if dist > max_distance:
                max_distance = dist
                furthest_pair = (row1, row2)

    if furthest_pair:
        row1, row2 = furthest_pair
        plt.plot(
            [row1["x mm"], row2["x mm"]],
            [row1["y mm"], row2["y mm"]],
            color="grey",
            linestyle=":",
            label=f"Max Distance ({max_distance:.1f} mm)",
        )

    plt.legend(loc="upper right")


def save_plot(df: pd.DataFrame, name: str, target: Dict[str, float], moa: float, distance: int, x: int, y: int) -> None:
    if df.empty:
        return

    fig, ax = plt.subplots(figsize=(10, 10))
    plt.switch_backend("Agg")
    ax.set_aspect("equal")

    render_plot(ax, df, target, moa, distance, name, x, y)

    plt.savefig(name, dpi=300)
    plt.close(fig)


def generate_plots(csv_path: str, prefix: str, distance: int, x: int = 0, y: int = 0) -> Tuple[str, str, str]:
    """
    Generate shooting plots from a CSV file.

    :param csv_path: Path to the CSV file to process
    :param prefix: Prefix for the output files
    :param distance: Distance in meters (300, 500, 600, 700, 800, 900)
    :param x: X offset in mm (default: 0)
    :param y: Y offset in mm (default: 0)
    :return: Tuple of paths to the three generated plot files (left, middle, right)
    :raises ValueError: If distance is unsupported
    """
    cfg = dist_config(distance)
    if cfg is None:
        raise ValueError(f"Unsupported distance: {distance}")

    df = load_dataframe(csv_path)
    left_df, middle_df, right_df = split_by_id(df)

    out_base = f"output/{prefix}"
    left_plot = out_base + "_l.png"
    middle_plot = out_base + "_m.png"
    right_plot = out_base + "_r.png"

    save_plot(left_df, left_plot, cfg.target, cfg.moa, distance, x, y)
    save_plot(middle_df, middle_plot, cfg.target, cfg.moa, distance, x, y)
    save_plot(right_df, right_plot, cfg.target, cfg.moa, distance, x, y)

    return left_plot, middle_plot, right_plot


def main():
    args = parse_args()
    try:
        generate_plots(args.filename, args.prefix, args.distance, args.x, args.y)
    except ValueError as e:
        print(str(e))
        return


if __name__ == "__main__":
    main()

