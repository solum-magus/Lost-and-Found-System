"""Decides which Lost items and Found items look like each other.

Discrete math used here (all of it is plain Python sets):
  - Set:           each item becomes a SET of words
  - Intersection:  A & B  = words both items have
  - Union:         A | B  = all words from either item
  - Difference:    A - B  = words only in your item, B - A = words only in theirs
  - Jaccard:       |A & B| / |A | B|   (cardinality of one set over another)
  - Subset/filter: only items in the SAME category and the OPPOSITE type are compared
"""
import re

# CONFIG
# Words that say nothing about an item, so they would only create fake matches
STOPWORDS = {"a", "an", "and", "the", "of", "in", "on", "at", "to", "for", "with",
             "my", "is", "it", "was", "near", "i", "me", "has", "have", "from"}

MIN_SCORE = 0.10      # below 10% similarity we don't call it a possible match


def words(text):
    """'Black Nike bag!' -> {'black', 'nike', 'bag'}  (a SET, so repeats disappear).
        No need to filter duplicates, Python sets do that automatically."""
    found = re.findall(r"[a-z0-9]+", (text or "").lower())
    return {w for w in found if w not in STOPWORDS and len(w) > 1}


def item_words(item):
    """The set of words that describe one item: union of its fields' word sets."""
    return (words(item["name"]) | words(item["location"]) | words(item["description"]))


def jaccard(a, b):
    """|A intersect B| / |A union B|.  0 = nothing in common, 1 = identical."""
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def find_matches(new_item, candidates):
    """Returns [(item, score, shared_words)] best first.

    candidates should already be the opposite type (Lost vs Found).
    """
    mine = item_words(new_item)
    results = []
    for other in candidates:
        if other["category"] != new_item["category"]:      # different category = skip
            continue
        theirs = item_words(other)
        score = jaccard(mine, theirs)
        if score >= MIN_SCORE:
            results.append((other, score, sorted(mine & theirs),
                            sorted(mine - theirs), sorted(theirs - mine)))
    results.sort(key=lambda r: r[1], reverse=True)
    return results