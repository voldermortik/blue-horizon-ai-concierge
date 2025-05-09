"""Compare two batches of generated data to check for regressions."""

from pathlib import Path
from typing import Set
import pandas as pd
import numpy as np


def load_dataset(path: Path) -> pd.DataFrame:
    """Load a CSV dataset and return as DataFrame.

    Args:
        path: Path to the CSV file to load

    Returns:
        DataFrame containing the loaded data, or empty DataFrame if loading fails
    """
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error loading {path}: {str(e)}")
        return pd.DataFrame()


def compare_numeric_stats(
    df1: pd.DataFrame, df2: pd.DataFrame, common_cols: Set[str]
) -> None:
    """Compare numeric column statistics between two DataFrames.

    Args:
        df1: First DataFrame to compare
        df2: Second DataFrame to compare
        common_cols: Set of column names common to both DataFrames
    """
    numeric_cols = [
        col for col in common_cols if np.issubdtype(df1[col].dtype, np.number)
    ]

    if not numeric_cols:
        return

    print("  📈 Numeric column changes:")
    for col in numeric_cols:
        stats1 = df1[col].describe()
        stats2 = df2[col].describe()

        mean_diff = stats2["mean"] - stats1["mean"]
        mean_pct = (
            (mean_diff / stats1["mean"]) * 100 if stats1["mean"] != 0 else float("inf")
        )

        std_diff = stats2["std"] - stats1["std"]
        std_pct = (
            (std_diff / stats1["std"]) * 100 if stats1["std"] != 0 else float("inf")
        )

        print(f"    {col}:")
        print(
            f"      Mean: {stats1['mean']:.2f} → {stats2['mean']:.2f} "
            f"({'↑' if mean_diff > 0 else '↓'}{abs(mean_pct):.1f}%)"
        )
        print(
            f"      Std:  {stats1['std']:.2f} → {stats2['std']:.2f} "
            f"({'↑' if std_diff > 0 else '↓'}{abs(std_pct):.1f}%)"
        )


def compare_datasets(batch1_dir: str, batch2_dir: str) -> None:
    """Compare two batches of datasets for regressions and changes.

    Args:
        batch1_dir: Path to the first batch directory
        batch2_dir: Path to the second batch directory
    """
    batch1_path = Path(batch1_dir)
    batch2_path = Path(batch2_dir)

    # Get list of files in both directories
    batch1_files = {f.name for f in batch1_path.glob("*.csv")}
    batch2_files = {f.name for f in batch2_path.glob("*.csv")}

    # Check for missing files
    missing_in_batch2 = batch1_files - batch2_files
    new_in_batch2 = batch2_files - batch1_files

    if missing_in_batch2:
        print("\n🚨 Files missing in batch2:")
        for file in sorted(missing_in_batch2):
            print(f"  - {file}")

    if new_in_batch2:
        print("\n📝 New files in batch2:")
        for file in sorted(new_in_batch2):
            print(f"  - {file}")

    # Compare common files
    common_files = batch1_files & batch2_files
    print(f"\n🔍 Comparing {len(common_files)} common files...")

    for file in sorted(common_files):
        print(f"\n📊 {file}")
        df1 = load_dataset(batch1_path / file)
        df2 = load_dataset(batch2_path / file)

        if df1.empty or df2.empty:
            continue

        # Compare record counts
        count1, count2 = len(df1), len(df2)
        count_diff = count2 - count1
        count_pct = (count_diff / count1) * 100 if count1 > 0 else float("inf")

        print(
            f"  Records: {count1:,} → {count2:,} "
            f"({'↑' if count_diff > 0 else '↓'}{abs(count_diff):,}, "
            f"{abs(count_pct):.1f}%)"
        )

        # Compare columns
        cols1, cols2 = set(df1.columns), set(df2.columns)
        missing_cols = cols1 - cols2
        new_cols = cols2 - cols1

        if missing_cols:
            print("  ❌ Missing columns in batch2:", ", ".join(sorted(missing_cols)))
        if new_cols:
            print("  ✨ New columns in batch2:", ", ".join(sorted(new_cols)))

        # Compare numeric columns statistics
        compare_numeric_stats(df1, df2, cols1 & cols2)


if __name__ == "__main__":
    compare_datasets("datasets/batch1", "datasets/batch2")
