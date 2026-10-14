"""Rebuild Case 1 from frozen private review snapshots, without network calls.

Example: python scripts/rebuild_case1_assets.py --input-dir private_data/case1
The snapshot uses cumulative playtime at collection, not time at review.
See docs/case1-method.md for the revised, explicit theme dictionary.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ["0-10h", "10-50h", "50-100h", "100-300h", "300-1000h", "1000h+"]
BOUNDS = [10, 50, 100, 300, 1000, math.inf]
GAMES = {"apex": "Apex Legends", "icarus": "Icarus", "poe": "Path of Exile"}

# Version 2 makes the full matching rules inspectable. Earlier aggregate exports
# did not include their complete dictionaries and used inconsistent snapshots.
THEMES = {
    "apex": {
        "Onboarding": ["tutorial", "beginner", "new player", "new players", "learning curve"],
        "Technical": ["server", "servers", "lag", "crash", "crashes", "bug", "bugs", "fps", "stutter", "audio"],
        "Systems": ["ranked", "rank", "matchmaking", "balance", "balanced", "unbalanced", "sbmm"],
        "Economy_Content": ["skin", "skins", "battle pass", "content", "monetisation", "monetization", "microtransaction", "microtransactions", "expensive"],
        "Trust_Fairness": ["cheater", "cheaters", "cheating", "hacker", "hackers", "anti cheat", "anticheat", "respawn", "developer", "developers", "trust"],
    },
    "icarus": {
        "Onboarding": ["tutorial", "beginner", "new player", "new players", "learning curve", "confusing"],
        "Technical": ["bug", "bugs", "crash", "crashes", "fps", "performance", "stutter", "lag", "optimization", "optimisation"],
        "Survival_Systems": ["survival", "craft", "crafting", "building", "base", "oxygen", "weather", "storm", "storms", "grind"],
        "Economy_Content": ["content", "mission", "missions", "progression", "update", "updates", "price", "worth"],
        "Value_DLC": ["dlc", "price", "expensive", "money", "worth", "pay", "paid", "buy"],
    },
    "poe": {
        "Onboarding_Complexity": ["tutorial", "beginner", "new player", "new players", "learning curve", "complex", "complexity", "confusing", "guide", "guides"],
        "Server_League_Technical": ["server", "servers", "crash", "crashes", "lag", "disconnect", "disconnection", "queue", "performance", "bug", "bugs"],
        "Trade_Loot_UI": ["trade", "trading", "loot", "ui", "interface", "inventory"],
        "Build_Endgame_Depth": ["build", "builds", "endgame", "end game", "skill tree", "passive tree", "mapping", "atlas"],
        "Monetisation_Content": ["stash", "stash tab", "stash tabs", "microtransaction", "microtransactions", "content", "expansion", "expansions", "monetisation", "monetization"],
    },
}
ATTACHMENT = {
    "apex": {
        "Battle Royale Loop": ["battle royale", "br", "battle royal"],
        "Matchmaking / Ranked Pressure": ["matchmaking", "ranked", "rank", "sbmm"],
        "Movement / Gunplay": ["movement", "gunplay", "shooting", "combat"],
        "Friends / Squad Play": ["friend", "friends", "squad", "squads", "teamwork"],
        "Developer Trust": ["respawn", "developer", "developers", "trust"],
        "Cheaters / Fairness": ["cheater", "cheaters", "cheating", "hacker", "hackers", "anticheat", "anti cheat"],
        "Servers / Stability": ["server", "servers", "lag", "crash", "crashes", "disconnect"],
        "Monetisation": ["skin", "skins", "battle pass", "microtransaction", "microtransactions", "monetisation", "monetization"],
        "Skill / Mastery": ["skill", "skills", "mastery", "improve", "improvement", "learning"],
    },
    "icarus": {
        "Survival Fantasy": ["survival", "survive", "surviving"],
        "Base Building": ["base", "building", "buildings"],
        "DLC / Value": ["dlc", "price", "expensive", "money", "worth"],
        "Mission / Content Structure": ["mission", "missions", "content"],
        "Open World / Exploration": ["open world", "explore", "exploration", "exploring"],
        "Crafting / Progression": ["craft", "crafting", "progression", "progress"],
        "Friends / Co-op": ["friend", "friends", "co op", "coop", "multiplayer"],
        "Technical Stability": ["bug", "bugs", "crash", "crashes", "fps", "performance", "lag"],
        "Grind / Pacing": ["grind", "grinding", "grindy", "pacing", "repetitive"],
    },
    "poe": {
        "Build Depth": ["build", "builds", "skill tree", "passive tree"],
        "Learning / Mastery": ["learn", "learning", "mastery", "master", "complex", "complexity"],
        "League Cycle": ["league", "leagues", "season", "seasons"],
        "Endgame": ["endgame", "end game", "atlas", "mapping"],
        "Trade / Loot / UI": ["trade", "trading", "loot", "ui", "interface"],
        "Server / League Stability": ["server", "servers", "crash", "crashes", "lag", "disconnect", "queue"],
        "Skill Gems / Systems": ["gem", "gems", "skill", "skills"],
        "Monetisation / Stash Tabs": ["stash", "microtransaction", "microtransactions", "monetisation", "monetization"],
        "Balance / Frustration": ["balance", "balanced", "unbalanced", "nerf", "nerfs", "frustrating", "frustration"],
    },
}


def parse_bool(value: object) -> bool:
    token = str(value).strip().lower()
    if token not in {"true", "false", "1", "0"}:
        raise ValueError(f"Invalid recommendation label: {value!r}")
    return token in {"true", "1"}


def stage(hours: float) -> str:
    if not math.isfinite(hours) or hours < 0:
        raise ValueError("Playtime must be finite and non-negative")
    return GROUPS[next(i for i, bound in enumerate(BOUNDS) if hours < bound)]


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[-\u2010-\u2015]", " ", str(text).lower())).strip()


def mentions(text: str, keywords: list[str]) -> bool:
    return any(re.search(r"(?<!\w)" + re.escape(normalized(k)) + r"(?!\w)", text) for k in keywords)


def load_reviews(path: Path, game: str) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"Empty snapshot: {path.name}")
    ids = [row["review_id"] for row in rows]
    if len(set(ids)) != len(ids) or any(not x for x in ids):
        raise ValueError(f"Missing or duplicate review IDs: {path.name}")
    for row in rows:
        if row["game"] != game:
            raise ValueError(f"Unexpected game in {path.name}")
        row["voted_up"] = parse_bool(row["voted_up"])
        row["playtime_hours"] = float(row["playtime_hours"])
        if abs(row["playtime_hours"] - float(row["playtime_forever"]) / 60) > 0.011:
            raise ValueError("playtime_hours differs from playtime_forever / 60")
        row["playtime_group"] = stage(row["playtime_hours"])
        if not str(row["review_text"]).strip():
            raise ValueError(f"Empty review text in {path.name}")
        row["match_text"] = normalized(row["review_text"])
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def rate(n: int, d: int, scale: float = 1) -> float | None:
    return n / d * scale if d else None


def rebuild(input_dir: Path, output_dir: Path) -> dict:
    paths = {slug: input_dir / f"{slug}_reviews.csv" for slug in GAMES}
    # Validate all inputs before writing any output.
    cohorts = {slug: load_reviews(paths[slug], game) for slug, game in GAMES.items()}
    lifecycle = []
    manifest = {"version": "case1-frozen-v2", "audit_date": "2026-10-14", "playtime_basis": "playtime_forever / 60 at collection", "intervals": "[0,10), [10,50), [50,100), [100,300), [300,1000), [1000,infinity)", "source": "Review tables recovered from the original Power BI snapshot; raw text stays private.", "theme_dictionary": "scripts/rebuild_case1_assets.py (version 2)", "games": {}}
    for slug, game in GAMES.items():
        rows = cohorts[slug]
        negatives = [r for r in rows if not r["voted_up"]]
        positive_50h = [r for r in rows if r["voted_up"] and r["playtime_hours"] >= 50]
        manifest["games"][game] = {"input_file": paths[slug].name, "sha256": hashlib.sha256(paths[slug].read_bytes()).hexdigest(), "review_count": len(rows), "negative_count": len(negatives), "positive_50h_count": len(positive_50h)}
        themes = []
        for i, group in enumerate(GROUPS, 1):
            subset = [r for r in rows if r["playtime_group"] == group]
            neg = [r for r in subset if not r["voted_up"]]
            lifecycle.append({"game": game, "playtime_group": group, "sort_order": i, "review_count": len(subset), "negative_rate": rate(len(neg),len(subset)), "negative_count": len(neg), "positive_count": len(subset)-len(neg)})
            for theme, keywords in THEMES[slug].items():
                n = sum(mentions(r["match_text"], keywords) for r in neg)
                themes.append({"game": game, "playtime_group": group, "sort_order": i, "playtime_sort": i, "theme": theme, "theme_display": theme.replace("_", " / "), "negative_reviews": len(neg), "theme_mentions": n, "mention_rate": rate(n,len(neg)), "mention_rate_pct": rate(n,len(neg),100), "negative_review_count": len(neg), "theme_negative_count": n})
        write_csv(output_dir/f"{slug}_theme_by_playtime.csv", themes)
        summaries = []
        for theme in THEMES[slug]:
            group_rows = [r for r in themes if r["theme"] == theme]
            peak = max(group_rows, key=lambda r: -1 if r["mention_rate"] is None else r["mention_rate"])
            rates = [r["mention_rate_pct"] for r in group_rows if r["mention_rate_pct"] is not None]
            count = sum(r["theme_mentions"] for r in group_rows)
            summaries.append({"game":game,"theme":theme,"theme_display":theme.replace("_"," / "),"peak_stage":peak["playtime_group"],"peak_rate_pct":peak["mention_rate_pct"],"average_rate_pct":sum(rates)/len(rates),"overall_rate_pct":rate(count,len(negatives),100),"negative_reviews":len(negatives),"theme_mentions":count,"active_stage_count":sum(r is not None and r>=10 for r in [x["mention_rate_pct"] for x in group_rows]),"pattern":"Descriptive mention pattern; inspect denominators"})
        write_csv(output_dir/f"{slug}_theme_pattern_summary.csv", summaries)
        comparison = []
        for theme, keywords in ATTACHMENT[slug].items():
            pos_n = sum(mentions(r["match_text"],keywords) for r in positive_50h)
            neg_n = sum(mentions(r["match_text"],keywords) for r in negatives)
            pos_rate, neg_rate = rate(pos_n,len(positive_50h),100), rate(neg_n,len(negatives),100)
            signal = "Higher in 50h+ positive reviews" if pos_rate > neg_rate else "Higher in negative reviews" if pos_rate < neg_rate else "Equal mention rates"
            comparison.append({"game":game,"theme":theme,"stayed_positive_reviews":len(positive_50h),"stayed_positive_mentions":pos_n,"stayed_positive_mention_rate_pct":pos_rate,"negative_reviews":len(negatives),"negative_mentions":neg_n,"negative_mention_rate_pct":neg_rate,"total_mentions":pos_n+neg_n,"positive_share":rate(pos_n,pos_n+neg_n),"signal_type":signal})
        write_csv(output_dir/f"{slug}_attachment_vs_friction_signals.csv", comparison)
    write_csv(output_dir/'lifecycle_risk_map_pct.csv', lifecycle)
    output_dir.mkdir(parents=True,exist_ok=True)
    (output_dir/'case1_provenance.json').write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,default=ROOT/'private_data/case1')
    parser.add_argument("--output-dir",type=Path,default=ROOT/'data')
    args=parser.parse_args()
    result=rebuild(args.input_dir,args.output_dir)
    print(json.dumps({g: d["review_count"] for g,d in result["games"].items()},indent=2))
