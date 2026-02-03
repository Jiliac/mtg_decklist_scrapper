#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check why specific tournaments aren't being downloaded
"""
import sys
from datetime import datetime, timezone
import Client.MtgMeleeClientV2 as MTGmelee

# Tournament IDs to check
tournament_ids = [384940, 384985]

print("Fetching tournament data for debugging...\n")

# Get tournaments from the past week
client = MTGmelee.MtgMeleeClient()
start_date = datetime(2025, 11, 29, tzinfo=timezone.utc)
end_date = datetime(2025, 12, 2, tzinfo=timezone.utc)

tournaments = client.get_tournaments(start_date, end_date)

if not tournaments:
    print("No tournaments found in date range")
    sys.exit(1)

# Find our specific tournaments
for tid in tournament_ids:
    print(f"\n{'='*80}")
    print(f"Looking for tournament {tid}...")
    print(f"{'='*80}")

    matching = [t for t in tournaments if t.id == tid]

    if not matching:
        print(f"❌ Tournament {tid} NOT FOUND in the downloaded list")
        print(f"   This means it's being filtered out during the initial tournament fetch")
        continue

    tournament = matching[0]
    print(f"✓ Found tournament: {tournament.name}")
    print(f"  Date: {tournament.date}")
    print(f"  Status: {tournament.statut}")
    print(f"  Formats: {tournament.formats}")
    print(f"  Organizer: {tournament.organizer}")

    # Count decklists
    total_decks = sum(len(player_decks) for player_decks in tournament.decklists.values())
    valid_decks = sum(
        1
        for player_decks in tournament.decklists.values()
        for decklist in player_decks.values()
        if decklist.Valid
    )
    ratio = valid_decks / total_decks if total_decks > 0 else 0

    print(f"\n  Decklist stats:")
    print(f"    Total decklists: {total_decks}")
    print(f"    Valid decklists: {valid_decks}")
    print(f"    Ratio: {ratio:.2%}")
    print(f"    Min required: {MTGmelee.MtgMeleeConstants.Min_number_of_valid_decklists}")
    print(f"    Threshold: {MTGmelee.MtgMeleeConstants.VALID_DECKLIST_THRESHOLD:.0%}")

    # Check filters
    print(f"\n  Filter checks:")

    # Status check
    from datetime import timedelta
    days_ago = (datetime.now(timezone.utc) - tournament.date.replace(tzinfo=timezone.utc)).days
    status_ok = tournament.statut == 'Ended' or days_ago >= 5
    print(f"    Status check: {'✓ PASS' if status_ok else '❌ FAIL'} (status={tournament.statut}, days_ago={days_ago})")

    # Valid decklist count
    min_count_ok = valid_decks >= MTGmelee.MtgMeleeConstants.Min_number_of_valid_decklists
    print(f"    Min valid count: {'✓ PASS' if min_count_ok else '❌ FAIL'} ({valid_decks} >= {MTGmelee.MtgMeleeConstants.Min_number_of_valid_decklists})")

    # Valid decklist ratio
    ratio_ok = ratio >= MTGmelee.MtgMeleeConstants.VALID_DECKLIST_THRESHOLD
    print(f"    Valid ratio: {'✓ PASS' if ratio_ok else '❌ FAIL'} ({ratio:.2%} >= {MTGmelee.MtgMeleeConstants.VALID_DECKLIST_THRESHOLD:.0%})")

    # Format check
    valid_formats = MTGmelee.MtgMeleeAnalyzerSettings.ValidFormats
    format_ok = all(f in valid_formats for f in tournament.formats)
    print(f"    Format check: {'✓ PASS' if format_ok else '❌ FAIL'} (formats={tournament.formats})")

    # Blacklist check
    blacklisted = any(term.lower() in tournament.name.lower() for term in MTGmelee.MtgMeleeAnalyzerSettings.BlacklistedTerms)
    print(f"    Blacklist check: {'✓ PASS' if not blacklisted else '❌ FAIL'}")

    # Try to analyze it
    print(f"\n  Running analyzer...")
    analyzer = MTGmelee.MtgMeleeAnalyzer()
    try:
        result = analyzer.get_scraper_tournaments(tournament)
        if result:
            print(f"    ✓ Analyzer returned {len(result)} tournament(s)")
            for i, t in enumerate(result):
                print(f"      {i+1}. {t.json_file}")
        else:
            print(f"    ❌ Analyzer returned None (tournament filtered out)")
    except Exception as e:
        print(f"    ❌ Analyzer raised exception: {e}")

print(f"\n{'='*80}")
print("Debug complete")
print(f"{'='*80}")
