"""
Utility functions for Flight Delay Analysis Project
Phase 1: Data Ingestion & Preparation

This module contains reusable functions for data loading, cleaning,
profiling, and validation.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import warnings


class DataProfiler:
    """
    Comprehensive data profiling utilities for flight delay analysis.
    """

    @staticmethod
    def get_schema_info(df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate comprehensive schema information for a DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with column info including name, dtype, non-null count, null count, null %
        """
        schema_info = pd.DataFrame({
            'Column': df.columns,
            'Data Type': df.dtypes.values,
            'Non-Null Count': df.count().values,
            'Null Count': df.isnull().sum().values,
            'Null %': (df.isnull().sum() / len(df) * 100).round(2).values,
            'Unique Values': [df[col].nunique() for col in df.columns],
            'Sample Value': [df[col].iloc[0] if len(df) > 0 else None for col in df.columns]
        })
        return schema_info

    @staticmethod
    def get_missing_data_summary(df: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
        """
        Generate missing data summary for columns with missing values above threshold.

        Args:
            df: Input DataFrame
            threshold: Minimum missing percentage to include (default 0.0 = all columns with missing data)

        Returns:
            DataFrame sorted by missing percentage (descending)
        """
        missing_data = pd.DataFrame({
            'Column': df.columns,
            'Missing Count': df.isnull().sum().values,
            'Missing %': (df.isnull().sum() / len(df) * 100).round(2).values,
            'Data Type': df.dtypes.values
        })

        missing_data = missing_data[missing_data['Missing %'] > threshold]
        missing_data = missing_data.sort_values('Missing %', ascending=False)
        return missing_data.reset_index(drop=True)

    @staticmethod
    def get_memory_usage(df: pd.DataFrame) -> Dict[str, str]:
        """
        Calculate and format memory usage statistics.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary with formatted memory usage information
        """
        total_memory_bytes = df.memory_usage(deep=True).sum()

        def format_bytes(bytes_value):
            """Convert bytes to human-readable format."""
            for unit in ['B', 'KB', 'MB', 'GB']:
                if bytes_value < 1024.0:
                    return f"{bytes_value:.2f} {unit}"
                bytes_value /= 1024.0
            return f"{bytes_value:.2f} TB"

        return {
            'total_memory': format_bytes(total_memory_bytes),
            'total_memory_mb': round(total_memory_bytes / (1024 ** 2), 2),
            'per_column_memory': df.memory_usage(deep=True).apply(format_bytes).to_dict()
        }

    @staticmethod
    def detect_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Dict:
        """
        Detect and summarize duplicate rows.

        Args:
            df: Input DataFrame
            subset: Columns to consider for identifying duplicates (None = all columns)

        Returns:
            Dictionary with duplicate statistics
        """
        duplicate_mask = df.duplicated(subset=subset, keep='first')
        duplicate_count = duplicate_mask.sum()

        return {
            'total_duplicates': int(duplicate_count),
            'duplicate_percentage': round(duplicate_count / len(df) * 100, 2),
            'unique_rows': len(df) - duplicate_count,
            'total_rows': len(df)
        }


class DataLoader:
    """
    Memory-efficient data loading utilities.
    """

    @staticmethod
    def load_csv_chunked(file_path: str, chunksize: int = 1000000, **kwargs) -> pd.DataFrame:
        """
        Load large CSV file in chunks and concatenate.

        Args:
            file_path: Path to CSV file
            chunksize: Number of rows per chunk
            **kwargs: Additional arguments to pass to pd.read_csv

        Returns:
            Complete DataFrame
        """
        print(f"Loading CSV file in chunks of {chunksize:,} rows...")
        chunks = []
        total_rows = 0

        for i, chunk in enumerate(pd.read_csv(file_path, chunksize=chunksize, **kwargs)):
            chunks.append(chunk)
            total_rows += len(chunk)
            print(f"  Chunk {i+1}: {len(chunk):,} rows (Total: {total_rows:,})")

        print(f"\nConcatenating {len(chunks)} chunks...")
        df = pd.concat(chunks, ignore_index=True)
        print(f"✓ Loaded {len(df):,} total rows")

        return df

    @staticmethod
    def load_sample(file_path: str, n_rows: int = 10000, **kwargs) -> pd.DataFrame:
        """
        Load a sample of rows from CSV for initial inspection.

        Args:
            file_path: Path to CSV file
            n_rows: Number of rows to load
            **kwargs: Additional arguments to pass to pd.read_csv

        Returns:
            Sample DataFrame
        """
        print(f"Loading sample of {n_rows:,} rows...")
        df_sample = pd.read_csv(file_path, nrows=n_rows, **kwargs)
        print(f"✓ Loaded {len(df_sample):,} rows with {len(df_sample.columns)} columns")
        return df_sample

    @staticmethod
    def discover_csv_files(directory: str) -> List[Path]:
        """
        Discover all CSV files in a directory.

        Args:
            directory: Directory path to search

        Returns:
            List of Path objects for CSV files found
        """
        dir_path = Path(directory)
        csv_files = list(dir_path.glob('*.csv'))

        print(f"Found {len(csv_files)} CSV file(s) in {directory}:")
        for file in csv_files:
            file_size_mb = file.stat().st_size / (1024 ** 2)
            print(f"  - {file.name} ({file_size_mb:.2f} MB)")

        return csv_files


class DataCleaner:
    """
    Data cleaning and transformation utilities specific to flight data.
    """

    @staticmethod
    def identify_cancelled_flights(df: pd.DataFrame,
                                   cancelled_col: str = 'CANCELLED') -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Separate cancelled flights from active flights.

        Args:
            df: Input DataFrame
            cancelled_col: Name of cancellation indicator column

        Returns:
            Tuple of (active_flights_df, cancelled_flights_df)
        """
        if cancelled_col not in df.columns:
            warnings.warn(f"Column '{cancelled_col}' not found. Assuming no cancelled flights.")
            return df.copy(), pd.DataFrame()

        # Handle various representations of cancelled status
        df_copy = df.copy()
        cancelled_mask = df_copy[cancelled_col].notna() & (df_copy[cancelled_col] != 0)

        df_cancelled = df_copy[cancelled_mask].copy()
        df_active = df_copy[~cancelled_mask].copy()

        print(f"✓ Separated flights:")
        print(f"  - Active flights: {len(df_active):,} ({len(df_active)/len(df)*100:.1f}%)")
        print(f"  - Cancelled flights: {len(df_cancelled):,} ({len(df_cancelled)/len(df)*100:.1f}%)")

        return df_active, df_cancelled

    @staticmethod
    def create_delay_binary(df: pd.DataFrame,
                           delay_col: str,
                           threshold: int = 15) -> pd.DataFrame:
        """
        Create binary delay indicator based on threshold.

        Args:
            df: Input DataFrame
            delay_col: Name of delay column (in minutes)
            threshold: Delay threshold in minutes (default 15)

        Returns:
            DataFrame with added binary delay column
        """
        df_copy = df.copy()
        binary_col_name = f'is_delayed_{threshold}min'

        df_copy[binary_col_name] = (df_copy[delay_col] >= threshold).astype(int)

        delayed_count = df_copy[binary_col_name].sum()
        delayed_pct = delayed_count / len(df_copy) * 100

        print(f"✓ Created binary delay indicator '{binary_col_name}':")
        print(f"  - Threshold: {threshold} minutes")
        print(f"  - Delayed flights: {delayed_count:,} ({delayed_pct:.1f}%)")
        print(f"  - On-time flights: {len(df_copy) - delayed_count:,} ({100-delayed_pct:.1f}%)")

        return df_copy

    @staticmethod
    def identify_early_arrivals(df: pd.DataFrame,
                               delay_col: str = 'ARR_DELAY') -> pd.DataFrame:
        """
        Identify flights that arrived early (negative delay).

        Args:
            df: Input DataFrame
            delay_col: Name of arrival delay column

        Returns:
            DataFrame with added early_arrival indicator
        """
        df_copy = df.copy()
        df_copy['early_arrival'] = (df_copy[delay_col] < 0).astype(int)

        early_count = df_copy['early_arrival'].sum()
        early_pct = early_count / len(df_copy) * 100

        print(f"✓ Identified early arrivals:")
        print(f"  - Early arrivals: {early_count:,} ({early_pct:.1f}%)")
        print(f"  - Mean early arrival time: {df_copy[df_copy['early_arrival']==1][delay_col].mean():.1f} minutes")

        return df_copy

    @staticmethod
    def validate_time_consistency(df: pd.DataFrame,
                                 dep_time_col: str = 'DEP_TIME',
                                 arr_time_col: str = 'ARR_TIME',
                                 elapsed_col: str = 'ELAPSED_TIME') -> pd.DataFrame:
        """
        Validate time consistency and flag anomalies.

        Args:
            df: Input DataFrame
            dep_time_col: Departure time column
            arr_time_col: Arrival time column
            elapsed_col: Elapsed time column

        Returns:
            DataFrame with added time_valid indicator
        """
        df_copy = df.copy()

        # Check for required columns
        required_cols = [dep_time_col, arr_time_col, elapsed_col]
        missing_cols = [col for col in required_cols if col not in df_copy.columns]

        if missing_cols:
            warnings.warn(f"Missing columns for time validation: {missing_cols}")
            df_copy['time_valid'] = 1  # Assume valid if can't validate
            return df_copy

        # Flag invalid times (you can add more sophisticated checks)
        df_copy['time_valid'] = 1
        df_copy.loc[df_copy[elapsed_col] < 0, 'time_valid'] = 0

        invalid_count = (df_copy['time_valid'] == 0).sum()
        invalid_pct = invalid_count / len(df_copy) * 100

        print(f"✓ Time validation complete:")
        print(f"  - Valid records: {len(df_copy) - invalid_count:,} ({100-invalid_pct:.1f}%)")
        print(f"  - Invalid records: {invalid_count:,} ({invalid_pct:.1f}%)")

        return df_copy


class ParquetConverter:
    """
    Utilities for converting DataFrames to optimized Parquet format.
    """

    @staticmethod
    def save_to_parquet(df: pd.DataFrame,
                       output_path: str,
                       compression: str = 'snappy') -> Dict[str, any]:
        """
        Save DataFrame to Parquet format with compression.

        Args:
            df: Input DataFrame
            output_path: Output file path
            compression: Compression algorithm (default 'snappy')

        Returns:
            Dictionary with save statistics
        """
        print(f"Saving to Parquet: {output_path}")
        print(f"  - Rows: {len(df):,}")
        print(f"  - Columns: {len(df.columns)}")
        print(f"  - Compression: {compression}")

        df.to_parquet(output_path, compression=compression, index=False)

        # Get file size
        file_path = Path(output_path)
        file_size_mb = file_path.stat().st_size / (1024 ** 2)

        print(f"✓ Saved successfully ({file_size_mb:.2f} MB)")

        return {
            'file_path': output_path,
            'rows': len(df),
            'columns': len(df.columns),
            'file_size_mb': round(file_size_mb, 2),
            'compression': compression
        }

    @staticmethod
    def load_from_parquet(file_path: str) -> pd.DataFrame:
        """
        Load DataFrame from Parquet file.

        Args:
            file_path: Path to Parquet file

        Returns:
            Loaded DataFrame
        """
        print(f"Loading from Parquet: {file_path}")
        df = pd.read_parquet(file_path)
        print(f"✓ Loaded {len(df):,} rows with {len(df.columns)} columns")
        return df


def setup_pandas_display():
    """
    Configure pandas display options for better readability in notebooks.
    """
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_rows', 100)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    pd.set_option('display.float_format', lambda x: f'{x:.2f}')
    print("✓ Pandas display options configured")


def verify_directory_structure(base_path: str = '/home/user/Flight-delay') -> bool:
    """
    Verify that required directory structure exists.

    Args:
        base_path: Base project directory

    Returns:
        True if all directories exist, False otherwise
    """
    required_dirs = [
        'data/raw',
        'data/processed',
        'notebooks',
        'src',
        'reports'
    ]

    base = Path(base_path)
    all_exist = True

    print("Verifying directory structure:")
    for dir_path in required_dirs:
        full_path = base / dir_path
        exists = full_path.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {dir_path}")
        if not exists:
            all_exist = False

    return all_exist


if __name__ == "__main__":
    print("Flight Delay Analysis - Utility Module")
    print("This module provides reusable functions for data processing.")
    print("\nAvailable classes:")
    print("  - DataProfiler: Schema info, missing data, memory usage, duplicates")
    print("  - DataLoader: Chunked loading, sampling, file discovery")
    print("  - DataCleaner: Cancellation handling, delay classification, validation")
    print("  - ParquetConverter: Save/load Parquet files")
    print("\nAvailable functions:")
    print("  - setup_pandas_display(): Configure pandas display options")
    print("  - verify_directory_structure(): Check project directories")
