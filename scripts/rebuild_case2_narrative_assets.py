"""
Rebuild Case 2 review data and narrative satisfaction driver tables.

This script collects English Steam reviews for:
- God of War
- Red Dead Redemption 2
- The Witcher 3: Wild Hunt

Filtering rule:
- 10+ hours playtime
- review text with 20+ English words
- up to 5,000 filtered reviews per game

Raw review-level text is written to private_data/ and should not be committed.
Aggregated Power BI tables are written to data/.
"""

from __future__ import annotations

import csv
import html
import argparse
import json
import re
import time
from pathlib import Path
from typing import Dict, Iterable, List
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_DIR = ROOT / "private_data"
DATA_DIR = ROOT / "data"

TARGET_REVIEWS_PER_GAME = 5000
MIN_PLAYTIME_HOURS = 10
MIN_WORDS = 20
MAX_PAGES_PER_GAME = 220
REQUEST_SLEEP_SECONDS = 0.35

GAMES = [
    {"game": "God of War", "appid": 1593500, "slug": "god_of_war"},
    {"game": "RDR2", "appid": 1174180, "slug": "rdr2"},
    {"game": "The Witcher 3", "appid": 292030, "slug": "witcher3"},
]

BASE_NARRATIVE_CATEGORIES: Dict[str, List[str]] = {
    "Story & Quest Engagement": [
        "story",
        "stories",
        "storyline",
        "plot",
        "narrative",
        "quest",
        "quests",
        "mission",
        "missions",
        "campaign",
        "dialogue",
        "writing",
        "side quest",
        "main quest",
    ],
    "Character & Relationship Attachment": [
        "character",
        "characters",
        "protagonist",
        "companion",
        "companions",
        "cast",
        "relationship",
        "relationships",
    ],
    "World & Genre Immersion": [
        "world",
        "open world",
        "immersion",
        "immersive",
        "atmosphere",
        "setting",
        "environment",
        "exploration",
    ],
    "Emotional Payoff": [
        "emotional",
        "emotion",
        "emotions",
        "cried",
        "cry",
        "tears",
        "heartbreaking",
        "heart broken",
        "touching",
        "moving",
        "memorable",
        "attached",
        "attachment",
        "made me feel",
        "hit me",
    ],
    "Theme & Meaning": [
        "theme",
        "themes",
        "meaning",
        "meaningful",
        "choice",
        "choices",
        "morality",
        "moral",
        "consequence",
        "consequences",
        "ending",
        "endings",
        "redemption",
        "grief",
        "revenge",
        "family",
        "fate",
        "freedom",
        "sacrifice",
    ],
}

GAME_SPECIFIC_NARRATIVE_CATEGORIES: Dict[str, Dict[str, List[str]]] = {
    "God of War": {
        "Character & Relationship Attachment": [
            "father",
            "son",
            "kratos",
            "atreus",
            "mimir",
            "freya",
        ],
        "World & Genre Immersion": [
            "norse",
            "myth",
            "mythology",
            "gods",
            "realm",
            "realms",
        ],
    },
    "RDR2": {
        "Character & Relationship Attachment": [
            "arthur",
            "dutch",
            "john",
            "sadie",
            "gang",
        ],
        "World & Genre Immersion": [
            "western",
            "cowboy",
            "outlaw",
            "frontier",
            "horse",
            "camp",
        ],
    },
    "The Witcher 3": {
        "Character & Relationship Attachment": [
            "geralt",
            "ciri",
            "yennefer",
            "triss",
            "dandelion",
        ],
        "World & Genre Immersion": [
            "fantasy",
            "monster",
            "monsters",
            "witcher",
        ],
    },
}

NARRATIVE_CATEGORIES = list(BASE_NARRATIVE_CATEGORIES.keys())

GAMEPLAY_FLAW_KEYWORDS = [
    "combat",
    "control",
    "controls",
    "pacing",
    "slow",
    "boring",
    "repetitive",
    "repetition",
    "difficulty",
    "hard",
    "clunky",
    "camera",
    "technical",
    "bug",
    "bugs",
    "crash",
    "crashes",
    "performance",
    "fps",
    "stutter",
    "optimization",
    "grind",
]

WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


def normalize_text(text: str) -> str:
    text = html.unescape(text or "")
    text = text.replace("\r", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def contains_keyword(text: str, keyword: str) -> bool:
    escaped = re.escape(keyword.lower()).replace(r"\ ", r"\s+")
    return re.search(rf"\b{escaped}\b", text.lower()) is not None


def has_any_keyword(text: str, keywords: Iterable[str]) -> bool:
    return any(contains_keyword(text, keyword) for keyword in keywords)


def category_keywords_for_game(game: str, category: str) -> List[str]:
    keywords = list(BASE_NARRATIVE_CATEGORIES[category])
    keywords.extend(GAME_SPECIFIC_NARRATIVE_CATEGORIES.get(game, {}).get(category, []))
    return keywords


def tag_review(row: dict) -> dict:
    lower_text = str(row.get("review_text", "")).lower()
    category_flags = {
        category: has_any_keyword(lower_text, category_keywords_for_game(row["game"], category))
        for category in NARRATIVE_CATEGORIES
    }
    row.update(category_flags)
    row["has_narrative_signal"] = any(category_flags.values())
    row["has_gameplay_flaw"] = has_any_keyword(lower_text, GAMEPLAY_FLAW_KEYWORDS)
    return row


def steam_review_page(appid: int, cursor: str) -> dict:
    url = (
        f"https://store.steampowered.com/appreviews/{appid}"
        f"?json=1&filter=recent&language=english&review_type=all"
        f"&purchase_type=all&num_per_page=100&cursor={quote(cursor)}"
    )
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def collect_game_reviews(game: str, appid: int, slug: str) -> List[dict]:
    rows: List[dict] = []
    seen_ids = set()
    cursor = "*"

    for page_num in range(1, MAX_PAGES_PER_GAME + 1):
        payload = steam_review_page(appid, cursor)
        reviews = payload.get("reviews", [])
        cursor = payload.get("cursor", cursor)

        if not reviews:
            break

        for review in reviews:
            recommendation_id = str(review.get("recommendationid", ""))
            if recommendation_id in seen_ids:
                continue
            seen_ids.add(recommendation_id)

            author = review.get("author", {}) or {}
            playtime_hours = float(author.get("playtime_forever", 0)) / 60
            review_text = normalize_text(review.get("review", ""))
            review_word_count = word_count(review_text)

            if playtime_hours < MIN_PLAYTIME_HOURS or review_word_count < MIN_WORDS:
                continue

            category_flags = {
                category: has_any_keyword(review_text.lower(), category_keywords_for_game(game, category))
                for category in NARRATIVE_CATEGORIES
            }
            has_narrative_signal = any(category_flags.values())
            has_gameplay_flaw = has_any_keyword(review_text.lower(), GAMEPLAY_FLAW_KEYWORDS)

            row = {
                "game": game,
                "appid": appid,
                "recommendation_id": recommendation_id,
                "voted_up": bool(review.get("voted_up")),
                "sentiment": "Positive" if review.get("voted_up") else "Negative",
                "playtime_hours": round(playtime_hours, 2),
                "word_count": review_word_count,
                "has_narrative_signal": has_narrative_signal,
                "has_gameplay_flaw": has_gameplay_flaw,
                "review_text": review_text,
            }
            row.update(category_flags)
            rows.append(row)

            if len(rows) >= TARGET_REVIEWS_PER_GAME:
                break

        print(f"{game}: {len(rows)} filtered reviews after page {page_num}")
        if len(rows) >= TARGET_REVIEWS_PER_GAME:
            break
        time.sleep(REQUEST_SLEEP_SECONDS)

    out_path = PRIVATE_DIR / f"{slug}_reviews_english_5000_10h_20words.csv"
    write_csv(out_path, rows)
    return rows


def pct(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round(numerator / denominator * 100, 2)


def playtime_group(hours: float) -> str:
    if hours < 50:
        return "10-50h"
    if hours < 100:
        return "50-100h"
    if hours < 300:
        return "100-300h"
    if hours < 1000:
        return "300-1000h"
    return "1000h+"


def playtime_sort(group: str) -> int:
    return {
        "10-50h": 1,
        "50-100h": 2,
        "100-300h": 3,
        "300-1000h": 4,
        "1000h+": 5,
    }[group]


def write_csv(path: Path, rows: List[dict], fieldnames: List[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_outputs(all_rows: List[dict]) -> None:
    by_category = []
    overall = []
    narrative_vs_non = []
    compensation_long = []
    compensation_wide = []
    narrative_lift_by_playtime = []

    games = sorted({row["game"] for row in all_rows})

    for game in games:
        game_rows = [row for row in all_rows if row["game"] == game]
        positive_rows = [row for row in game_rows if row["voted_up"]]
        narrative_rows = [row for row in game_rows if row["has_narrative_signal"]]
        non_narrative_rows = [row for row in game_rows if not row["has_narrative_signal"]]

        overall.append(
            {
                "game": game,
                "overall_positive_rate": pct(len(positive_rows), len(game_rows)),
                "narrative_positive_rate": pct(
                    sum(1 for row in narrative_rows if row["voted_up"]),
                    len(narrative_rows),
                ),
                "non_narrative_positive_rate": pct(
                    sum(1 for row in non_narrative_rows if row["voted_up"]),
                    len(non_narrative_rows),
                ),
                "narrative_mention_rate": pct(len(narrative_rows), len(game_rows)),
            }
        )

        for label, rows in [
            ("Narrative Reviews", narrative_rows),
            ("Non-Narrative Reviews", non_narrative_rows),
        ]:
            narrative_vs_non.append(
                {
                    "game": game,
                    "type": label,
                    "positive_rate": pct(sum(1 for row in rows if row["voted_up"]), len(rows)),
                }
            )

        for group in ["10-50h", "50-100h", "100-300h", "300-1000h", "1000h+"]:
            group_rows = [
                row
                for row in game_rows
                if playtime_group(float(row["playtime_hours"])) == group
            ]
            group_narrative_rows = [row for row in group_rows if row["has_narrative_signal"]]
            group_non_narrative_rows = [row for row in group_rows if not row["has_narrative_signal"]]
            narrative_positive_rate = pct(
                sum(1 for row in group_narrative_rows if row["voted_up"]),
                len(group_narrative_rows),
            )
            non_narrative_positive_rate = pct(
                sum(1 for row in group_non_narrative_rows if row["voted_up"]),
                len(group_non_narrative_rows),
            )
            narrative_lift_by_playtime.append(
                {
                    "game": game,
                    "playtime_group": group,
                    "playtime_sort": playtime_sort(group),
                    "total_reviews": len(group_rows),
                    "narrative_reviews": len(group_narrative_rows),
                    "non_narrative_reviews": len(group_non_narrative_rows),
                    "narrative_positive_rate": narrative_positive_rate,
                    "non_narrative_positive_rate": non_narrative_positive_rate,
                    "narrative_lift_pp": round(
                        narrative_positive_rate - non_narrative_positive_rate, 2
                    ),
                }
            )

        flaw_rows = [row for row in game_rows if row["has_gameplay_flaw"]]
        positive_flaw_rows = [row for row in flaw_rows if row["voted_up"]]
        negative_flaw_rows = [row for row in flaw_rows if not row["voted_up"]]

        for category in NARRATIVE_CATEGORIES:
            category_rows = [row for row in game_rows if row[category]]
            positive_count = sum(1 for row in category_rows if row["voted_up"])
            negative_count = len(category_rows) - positive_count

            by_category.append(
                {
                    "category": category,
                    "positive_count": positive_count,
                    "negative_count": negative_count,
                    "game": game,
                    "total": len(category_rows),
                    "positive_rate": pct(positive_count, len(category_rows)),
                    "mention_rate": pct(len(category_rows), len(game_rows)),
                }
            )

            pos_pct = pct(sum(1 for row in positive_flaw_rows if row[category]), len(positive_flaw_rows))
            neg_pct = pct(sum(1 for row in negative_flaw_rows if row[category]), len(negative_flaw_rows))

            compensation_long.extend(
                [
                    {
                        "game": game,
                        "category": category,
                        "sentiment": "Positive Reviews",
                        "flaw_pct": pos_pct,
                    },
                    {
                        "game": game,
                        "category": category,
                        "sentiment": "Negative Reviews",
                        "flaw_pct": neg_pct,
                    },
                ]
            )
            compensation_wide.append(
                {
                    "game": game,
                    "category": category,
                    "positive_flaw_pct": pos_pct,
                    "negative_flaw_pct": neg_pct,
                    "compensation_gap": round(pos_pct - neg_pct, 2),
                }
            )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(DATA_DIR / "narrative_by_category_combined.csv", by_category)
    write_csv(DATA_DIR / "narrative_overall_combined_1.csv", overall)
    write_csv(DATA_DIR / "narrative_vs_nonnarrative.csv", narrative_vs_non)
    write_csv(DATA_DIR / "narrative_lift_by_playtime.csv", narrative_lift_by_playtime)
    write_csv(DATA_DIR / "compensation_flaw_combined.csv", compensation_long)
    write_csv(DATA_DIR / "compensation_flaw_wide.csv", compensation_wide)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rebuild Case 2 Steam review aggregates.")
    parser.add_argument(
        "--only",
        choices=[game["slug"] for game in GAMES],
        help="Collect only one game. Existing private_data files for the other games will be reused.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=MAX_PAGES_PER_GAME,
        help="Maximum Steam review pages to request per selected game.",
    )
    parser.add_argument(
        "--reuse-private",
        action="store_true",
        help="Rebuild aggregate tables from existing private_data review files without calling Steam.",
    )
    return parser.parse_args()


def read_csv(path: Path) -> List[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        row["appid"] = int(row["appid"])
        row["voted_up"] = str(row["voted_up"]).lower() == "true"
        row["playtime_hours"] = float(row["playtime_hours"])
        row["word_count"] = int(row["word_count"])
        row["has_narrative_signal"] = str(row["has_narrative_signal"]).lower() == "true"
        row["has_gameplay_flaw"] = str(row["has_gameplay_flaw"]).lower() == "true"
        for category in NARRATIVE_CATEGORIES:
            row[category] = str(row[category]).lower() == "true"
        tag_review(row)
    return rows


def main() -> None:
    args = parse_args()
    global MAX_PAGES_PER_GAME
    MAX_PAGES_PER_GAME = args.max_pages

    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    all_rows: List[dict] = []
    for game_info in GAMES:
        private_path = PRIVATE_DIR / f"{game_info['slug']}_reviews_english_5000_10h_20words.csv"
        if args.reuse_private and private_path.exists():
            rows = read_csv(private_path)
        elif args.only and args.only != game_info["slug"] and private_path.exists():
            rows = read_csv(private_path)
        elif args.only and args.only != game_info["slug"]:
            rows = []
        else:
            rows = collect_game_reviews(**game_info)
        all_rows.extend(rows)

    write_csv(PRIVATE_DIR / "case2_all_reviews_english_5000_10h_20words.csv", all_rows)
    build_outputs(all_rows)
    print(f"Done. Filtered review rows collected: {len(all_rows)}")
    print(f"Private review-level files: {PRIVATE_DIR}")
    print(f"Power BI aggregate tables: {DATA_DIR}")


if __name__ == "__main__":
    main()
