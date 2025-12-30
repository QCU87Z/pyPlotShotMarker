from datetime import date
import argparse
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from matplotlib.patches import Circle
import targets


def save_plot(df, name, target, moa, distance, x, y):
    # Check if the DataFrame is empty aka no left shooter
    if df.empty:
        return
    _, ax = plt.subplots(figsize=(10, 10))
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

    major_spacing_xy = moa  # Major grid lines every 2 units on the x-axis
    minor_spacing_xy = moa * 0.5  # Minor grid lines every 0.5 units on the x-axis
    ax.xaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.xaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.yaxis.set_major_locator(MultipleLocator(major_spacing_xy))
    ax.yaxis.set_minor_locator(MultipleLocator(minor_spacing_xy))
    ax.grid(which="major", linestyle="--", linewidth="0.75", alpha=0.5, color="gray")
    ax.grid(which="minor", linestyle="-.", linewidth="0.75", alpha=0.5, color="gray")
    today = date.today().strftime("%d-%b-%Y")
    ax.set_title(f"{distance}m - {name}\n\n{today}")

    for _, row in df.iterrows():
        x, y = row["x mm"], row["y mm"]
        s = row["id"].replace("L", "").replace("M", "").replace("R", "")
        label = s + "\n(" + row["score"] + ")"
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
    parser.add_argument(
        "--distance", type=int, required=True, help="Distance in meters"
    )
    parser.add_argument("--x", type=int, help="X offset in mm", default=0)
    parser.add_argument("--y", type=int, help="Y offset in mm", default=0)
    args = parser.parse_args()

    match args.distance:
        case 300:
            target = targets.target_300m
            moa = targets.moa_300m
        case 500:
            target = targets.target_500m
            moa = targets.moa_500m
        case 600:
            target = targets.target_600m
            moa = targets.moa_600m
        case 700:
            target = targets.target_700m
            moa = targets.moa_700m
        case 800:
            target = targets.target_800m
            moa = targets.moa_800m
        case 900:
            target = targets.target_900m
            moa = targets.mmoa_900m
        case _:
            print("Unsupported distance:", args.distance)
            return

    df = pd.read_csv(args.filename)
    left_df = df[df["id"].str.startswith("L")]
    middle_df = df[df["id"].str.startswith("M")]
    right_df = df[df["id"].str.startswith("R")]

    save_plot(
        left_df,
        "output/" + args.prefix + "_l.png",
        target,
        moa,
        args.distance,
        args.x,
        args.y,
    )
    save_plot(
        middle_df,
        "output/" + args.prefix + "_m.png",
        target,
        moa,
        args.distance,
        args.x,
        args.y,
    )
    save_plot(
        right_df,
        "output/" + args.prefix + "_r.png",
        target,
        moa,
        args.distance,
        args.x,
        args.y,
    )


if __name__ == "__main__":
    main()
