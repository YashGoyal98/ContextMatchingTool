import re
from typing import Set
from .models import RevitInput

class ContextAlgorithm:
    def __init__(self):
        # Maps Revit terminology to common detail keywords
        self.synonyms = {
            "exterior": "external", "outside": "external",
            "interior": "internal", "inside": "internal",
            "conc": "concrete", "rc": "concrete",
            "block": "masonry",
            "footing": "foundation",
            "ground": "foundation",
            "earth": "retaining"
        }

        # Words to ignore (Noise)
        self.ignored_words = {
            "detail", "junction", "connection", "abutment",
            "joint", "to", "with", "and", "-", "at", "the", "between"
        }

        # CRITICAL WORDS: If these don't match, it changes the nature of the detail entirely.
        self.functional_keywords = {
            "waterproofing", "firestop", "insulation", "acoustic",
            "sound", "expansion", "control", "movement", "flashing"
        }

    def normalize(self, text: str) -> Set[str]:
        if not text:
            return set()
        text = text.lower().replace("-", " ")
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        tokens = text.split()
        final_tokens = set()
        for t in tokens:
            if t not in self.ignored_words:
                final_tokens.add(self.synonyms.get(t, t))
        return final_tokens

    def calculate_match(self, query: RevitInput, target_detail: str) -> (float, str):
        # 1. Normalize Everything
        host_tokens = self.normalize(query.host_element)
        adj_tokens = self.normalize(query.adjacent_element)
        exp_tokens = self.normalize(query.exposure)

        # Combine all input requirements
        all_input_tokens = host_tokens | adj_tokens | exp_tokens

        # Normalize Target
        target_tokens = self.normalize(target_detail)

        # 2. Base Matching (Recall) - How much of Input is found in Target?
        host_hits = host_tokens.intersection(target_tokens)
        adj_hits = adj_tokens.intersection(target_tokens)
        exp_hits = exp_tokens.intersection(target_tokens)

        score = 0.0
        reasons = []

        # Weights: Host (35%), Adjacent (35%), Exposure (10%), Functionality (20%)

        # Host Match
        if host_hits:
            coverage = len(host_hits) / max(len(host_tokens), 1)
            score += 0.35 * coverage
            reasons.append(f"Host matches {list(host_hits)}")

        # Adjacent Match
        if adj_hits:
            coverage = len(adj_hits) / max(len(adj_tokens), 1)
            score += 0.35 * coverage
            reasons.append(f"Adjacent matches {list(adj_hits)}")

        # Exposure Match
        if exp_hits:
            score += 0.10
            reasons.append("Exposure matches")

        # 3. FUNCTIONAL CHECK (The "Waterproofing" Logic)

        # Extract functional words from Input and Target
        input_funcs = all_input_tokens.intersection(self.functional_keywords)
        target_funcs = target_tokens.intersection(self.functional_keywords)

        # Case A: Input asked for functionality (e.g. "Waterproofing")
        if input_funcs:
            # Check if Target has them
            missing_funcs = input_funcs - target_funcs
            if not missing_funcs:
                score += 0.20 # Bonus for finding the specific function
                reasons.append(f"Functionality matched: {list(input_funcs)}")
            else:
                # PENALTY: User asked for Waterproofing, Detail doesn't have it.
                score -= 0.25
                reasons.append(f"MISSING required function: {list(missing_funcs)}")

        # Case B: Target has functionality, but Input didn't ask for it
        # (e.g. Input: "Wall-Slab", Target: "Wall-Slab Waterproofing")
        elif target_funcs:
            # Slight Penalty for specificity mismatch (Uncertainty)
            # We don't penalize too hard because it might still be the right detail
            score += 0.1
            reasons.append(f"Note: Detail is specific to {list(target_funcs)}")

        else:
            # Neutral case (neither side has functional keywords)
            score += 0.20

        # Cap score 0.0 to 1.0
        final_score = max(0.0, min(score, 1.0))

        return round(final_score, 2), "; ".join(reasons)

matcher = ContextAlgorithm()