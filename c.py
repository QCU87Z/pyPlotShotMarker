import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Circle

def save_plot(df, name):
    # Check if the DataFrame is empty aka no left shooter
    if df.empty:
        return
    _, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect("equal")

    x_max_value = 300 if not df["x mm"].max() > 300 else df["x mm"].max()
    x_min_value = -300 if not df["x mm"].min() < -300 else df["x mm"].min()
    y_max_value = 300 if not df["y mm"].max() > 300 else df["y mm"].max()
    y_min_value = -300 if not df["y mm"].min() < -300 else df["y mm"].min()

    ax.set_xlim(x_min_value - 50, x_max_value + 50)
    ax.set_ylim(y_min_value - 50, y_max_value + 50)

    # 900m
    rings = {
        "(X)": 127 / 2,
        "(6)": 255 / 2,
        "(5)": 510 / 2,
        "(4)": 815 / 2,
        "(3)": 1120 / 2,
        "(2)": 1830 / 2,
    }
    for label, radius in rings.items():
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

    major_spacing_xy = 261.8  # Major grid lines every 2 units on the x-axis
    minor_spacing_xy = 130.9  # Minor grid lines every 0.5 units on the x-axis
    ax.xaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.yaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.grid(
        which="major", linestyle="-", linewidth="1.5", alpha=0.5, color="gray"
    )  # Customize major grid
    ax.grid(
        which="minor", linestyle="-", linewidth="1.0", alpha=0.5, color="gray"
    )  # Customize minor grid
    ax.set_title("900m - " + name + "\n\n29-Dec-2025")

    for _, row in df.iterrows():
        x, y = row["x mm"], row["y mm"]
        label = row["id"]
        if "S" in label:
            colour = "red"
        else:
            colour = "blue"
        plt.scatter(x, y, color=colour, marker="x", label="Point A")
        ax.annotate(
            label, (x, y), textcoords="offset points", xytext=(0, 10), ha="center"
        )

    plt.savefig(name, dpi=300)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="The csv file to process")
    parser.add_argument("--prefix", required=True, help="Prefix for the output files")
    args = parser.parse_args()

    df = pd.read_csv(args.filename)

    left_df = df[df["id"].str.startswith("L")]
    middle_df = df[df["id"].str.startswith("M")]
    right_df = df[df["id"].str.startswith("R")]

    save_plot(left_df, "output/" + args.prefix + "_l.png")
    save_plot(middle_df, "output/" + args.prefix + "_m.png")
    save_plot(right_df, "output/" + args.prefix + "_r.png")


if __name__ == "__main__":
    main()
