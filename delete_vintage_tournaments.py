#!/usr/bin/env python3
"""
Script to delete vintage tournament files from MTGmelee and MTGO directories
for September and October 2025.
"""

import json
import os
from pathlib import Path

def is_vintage_tournament(file_path):
    """Check if a JSON file is a vintage tournament by reading the Formats field."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            formats = data.get('Tournament', {}).get('Formats', '')
            if formats is None:
                return False
            return formats.lower() == 'vintage'
    except (json.JSONDecodeError, KeyError, IOError) as e:
        print(f"Error reading {file_path}: {e}")
        return False

def delete_vintage_tournaments(base_path, year=2025, months=[9, 10], dry_run=True):
    """
    Delete vintage tournament JSON files from specified months.

    Args:
        base_path: Path to the tournament directory (MTGmelee or MTGO)
        year: Year to process (default: 2025)
        months: List of months to process (default: [9, 10] for Sept and Oct)
        dry_run: If True, only print what would be deleted without actually deleting
    """
    base_path = Path(base_path)
    deleted_count = 0
    total_checked = 0

    for month in months:
        month_str = f"{month:02d}"
        month_path = base_path / str(year) / month_str

        if not month_path.exists():
            print(f"Path does not exist: {month_path}")
            continue

        # Find all JSON files in this month
        json_files = list(month_path.rglob("*.json"))
        print(f"\nChecking {len(json_files)} files in {month_path}")

        for json_file in json_files:
            total_checked += 1
            if is_vintage_tournament(json_file):
                if dry_run:
                    print(f"[DRY RUN] Would delete: {json_file}")
                else:
                    print(f"Deleting: {json_file}")
                    json_file.unlink()
                deleted_count += 1

    return deleted_count, total_checked

def main():
    # Base directory
    base_dir = Path("MTG_decklistcache/Tournaments")

    # Directories to process
    directories = [
        base_dir / "MTGmelee",
        base_dir / "MTGO"
    ]

    print("="*80)
    print("VINTAGE TOURNAMENT DELETION SCRIPT")
    print("Target: September and October 2025")
    print("="*80)

    # First run in dry-run mode
    print("\n*** DRY RUN MODE - No files will be deleted ***\n")

    total_deleted = 0
    total_checked = 0

    for directory in directories:
        print(f"\n{'='*80}")
        print(f"Processing: {directory}")
        print(f"{'='*80}")

        deleted, checked = delete_vintage_tournaments(directory, dry_run=True)
        total_deleted += deleted
        total_checked += checked

        print(f"\nSummary for {directory.name}:")
        print(f"  Files checked: {checked}")
        print(f"  Vintage tournaments found: {deleted}")

    print(f"\n{'='*80}")
    print(f"TOTAL SUMMARY")
    print(f"{'='*80}")
    print(f"Total files checked: {total_checked}")
    print(f"Total vintage tournaments found: {total_deleted}")

    if total_deleted > 0:
        print(f"\n{'='*80}")
        response = input(f"\nDo you want to DELETE these {total_deleted} vintage tournament files? (yes/no): ")

        if response.lower() == 'yes':
            print("\n*** DELETING FILES ***\n")

            total_deleted_actual = 0
            for directory in directories:
                print(f"\n{'='*80}")
                print(f"Processing: {directory}")
                print(f"{'='*80}")

                deleted, _ = delete_vintage_tournaments(directory, dry_run=False)
                total_deleted_actual += deleted

            print(f"\n{'='*80}")
            print(f"DELETION COMPLETE")
            print(f"{'='*80}")
            print(f"Total files deleted: {total_deleted_actual}")
        else:
            print("\nDeletion cancelled.")
    else:
        print("\nNo vintage tournaments found.")

if __name__ == "__main__":
    main()
