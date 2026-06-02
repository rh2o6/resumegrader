from tika import parser
import re
from collections import Counter
from tech_keyword import TECH_KEYWORDS, NEAR_MISS_HINTS

# ===== 1. CONFIGURATION =====

RESUME_PATH = 'robertresumefall.pdf'

# Paste the job description here as a multi-line string
with open("jobdesc.txt", "r", encoding="utf-8") as f:
    JOB_DESCRIPTION = f.read()

# Common English words to ignore (stop words)
STOP_WORDS = set("""
a an the and or but if then else for of in on at to from by with as is are was were
be been being have has had do does did will would shall should can could may might must
this that these those i you he she it we they me him her us them my your his its our their
not no yes also more most some any all each every other another such same so than too very
about into through during before after above below between within without across against
job role work team company candidate applicant position experience required preferred
plus bonus etc ability years year minimum maximum responsibilities qualifications skills
including ensure able strong excellent good great new our we you your
""".split())


# ===== 2. EXTRACT TEXT FROM RESUME =====

def extract_resume_text(path):
    parsed = parser.from_file(path)
    return parsed['content'] or ''


# ===== 3. TOKENIZATION (mimics ATS behavior) =====

def tokenize(text):
    """Lowercase, strip punctuation, split on whitespace — same as basic ATS."""
    text = text.lower()
    # Keep alphanumerics, dots (for .net, node.js), pluses (c++), hashes (c#), hyphens
    text = re.sub(r"[^\w\s\.\+\#\-/]", ' ', text)
    tokens = text.split()
    # Strip trailing punctuation but preserve internal
    tokens = [t.strip('.-/') for t in tokens]
    return [t for t in tokens if t and t not in STOP_WORDS and len(t) > 1]


def extract_phrases(text, max_n=3):
    """Extract 1-, 2-, and 3-word phrases (n-grams) for compound keyword matching."""
    tokens = tokenize(text)
    phrases = set(tokens)
    for n in range(2, max_n + 1):
        for i in range(len(tokens) - n + 1):
            phrases.add(' '.join(tokens[i:i + n]))
    return phrases


# ===== 4. KEYWORD EXTRACTION FROM JD =====

# Curated technical keyword dictionary — extend for your field

def extract_jd_keywords(jd_text):
    """Find which known tech keywords appear in the JD."""
    jd_phrases = extract_phrases(jd_text, max_n=3)
    found = set()
    for kw in TECH_KEYWORDS:
        if kw in jd_phrases:
            found.add(kw)
    return found


def find_must_haves(jd_text, all_keywords):
    """Heuristic: keywords mentioned near 'required', 'must', 'minimum'."""
    must_haves = set()
    sentences = re.split(r'[.\n]', jd_text.lower())
    trigger_words = ['required', 'must have', 'must-have', 'minimum',
                     'requirements', 'essential', 'mandatory']
    for sentence in sentences:
        if any(t in sentence for t in trigger_words):
            for kw in all_keywords:
                if kw in sentence:
                    must_haves.add(kw)
    return must_haves


def find_near_misses(missing_keywords, resume_text):
    """For each missing keyword, check if the resume has a related term."""
    resume_lower = resume_text.lower()
    near_misses = {}

    for kw in missing_keywords:
        hints = NEAR_MISS_HINTS.get(kw, [])
        found_hints = []
        for hint in hints:
            # Use the same strict matching
            if '/' in hint or '.' in hint:
                pattern = rf'(?<!\w){re.escape(hint)}(?!\w)'
            else:
                pattern = rf'\b{re.escape(hint)}\b'
            if re.search(pattern, resume_lower):
                found_hints.append(hint)
        if found_hints:
            near_misses[kw] = found_hints

    return near_misses




# ===== 5. MATCHING =====

def match_resume_to_jd(resume_text, jd_text):
    """Strict ATS-style matching: word-boundary regex, no variants."""
    resume_normalized = re.sub(r'\s+', ' ', resume_text.lower())
    jd_keywords = extract_jd_keywords(jd_text)
    must_haves = find_must_haves(jd_text, jd_keywords)

    def keyword_present(keyword, text):
        # Escape regex special chars; allow / and . to match literally
        escaped = re.escape(keyword)
        # Word boundary on both sides — but \b doesn't work well with /
        # so for keywords containing /, use lookarounds
        if '/' in keyword or '.' in keyword or '+' in keyword or '#' in keyword:
            pattern = rf'(?<!\w){escaped}(?!\w)'
        else:
            pattern = rf'\b{escaped}\b'
        return bool(re.search(pattern, text))

    matched = {kw for kw in jd_keywords if keyword_present(kw, resume_normalized)}
    missing = jd_keywords - matched
    missing_critical = must_haves - matched

    return {
        'jd_keywords': jd_keywords,
        'matched': matched,
        'missing': missing,
        'must_haves': must_haves,
        'missing_critical': missing_critical,
        'match_rate': len(matched) / len(jd_keywords) if jd_keywords else 0,
        'critical_match_rate': (
            len(must_haves & matched) / len(must_haves) if must_haves else 1.0
        ),
    }

# ===== 6. TOKENIZATION RISK CHECKS =====

def check_tokenization_risks(resume_text, jd_text):
    """Flag specific failure modes the Reddit post warned about."""
    warnings = []

    # Compound word splits
    resume_lower = resume_text.lower()
    jd_lower = jd_text.lower()
    compound_pairs = [
        ('cross-functional', 'crossfunctional'),
        ('role-based', 'rolebased'),
        ('real-time', 'realtime'),
        ('full-stack', 'fullstack'),
        ('back-end', 'backend'),
        ('front-end', 'frontend'),
    ]
    for hyphenated, joined in compound_pairs:
        in_jd = hyphenated in jd_lower or joined in jd_lower
        in_resume = hyphenated in resume_lower or joined in resume_lower
        if in_jd and not in_resume:
            warnings.append(f"JD uses '{hyphenated}'. Please add it in resume")

    # Acronym vs spelled-out
    acronym_pairs = [
        ('rbac', 'role-based access control'),
        ('ad', 'active directory'),
        ('dba', 'database administrator'),
        ('ci/cd', 'continuous integration'),
        ('sop', 'standard operating procedure'),
    ]
    for acronym, full in acronym_pairs:
        jd_has_acronym = re.search(rf'\b{re.escape(acronym)}\b', jd_lower)
        jd_has_full = full in jd_lower
        resume_has_acronym = re.search(rf'\b{re.escape(acronym)}\b', resume_lower)
        resume_has_full = full in resume_lower
        if (jd_has_acronym or jd_has_full) and not (resume_has_acronym and resume_has_full):
            if jd_has_acronym and not resume_has_acronym:
                warnings.append(f"JD uses acronym '{acronym.upper()}'. Please add it alongside '{full}' in resume")
            if jd_has_full and not resume_has_full:
                warnings.append(f"JD uses full phrase '{full}'. Please spell it out in resume")

    return warnings


# ===== 7. REPORT =====

def print_report(result, risk_warnings, near_misses):
    print("=" * 70)
    print("ATS MATCH REPORT")
    print("=" * 70)

    rate = result["match_rate"] * 100
    crit = result["critical_match_rate"] * 100

    print(
        f"\nOverall Keyword Match: "
        f"{len(result['matched'])}/{len(result['jd_keywords'])} ({rate:.0f}%)"
    )
    print(
        f"Required Keyword Match: "
        f"{len(result['must_haves'] & result['matched'])}/"
        f"{len(result['must_haves'])} ({crit:.0f}%)"
    )

    print("\n" + "-" * 70)

    if rate >= 75:
        print("Assessment: Strong Match")
        print("You are likely to pass initial ATS keyword screening.")
    elif rate >= 50:
        print("Assessment: Moderate Match")
        print("You may pass screening, but keyword gaps should be addressed.")
    else:
        print("Assessment: Weak Match")
        print("Significant keyword gaps may reduce ATS performance.")

    print("-" * 70)

    print(f"\nMatched Keywords ({len(result['matched'])})")
    for kw in sorted(result["matched"]):
        print(f"  ✓ {kw}")

    print(f"\nMissing Keywords ({len(result['missing'])})")
    for kw in sorted(result["missing"]):
        critical_marker = "*" if kw in result["missing_critical"] else " "
        hint_note = ""

        if kw in near_misses:
            hint_note = f"  (Found similar term: {', '.join(near_misses[kw])})"

        print(f"  {critical_marker} {kw}{hint_note}")

    if result["missing_critical"]:
        print("\nCritical Gaps (Required by Job Description)")
        for kw in sorted(result["missing_critical"]):
            print(f"  - {kw}")

    if near_misses:
        print("\nNear-Miss Keywords")
        for kw, hints in sorted(near_misses.items()):
            print(
                f"  - Job description requests '{kw}', "
                f"but resume contains '{hints[0]}'. "
                f"Consider adding the exact phrase."
            )

    if risk_warnings:
        print("\nTokenization Risks")
        for warning in risk_warnings:
            print(f"  - {warning}")

    print("\n" + "=" * 70)

# ===== 8. RUN =====

if __name__ == '__main__':
    resume_text = extract_resume_text(RESUME_PATH)
    if not JOB_DESCRIPTION.strip() or 'PASTE THE FULL' in JOB_DESCRIPTION:
        print("Please paste a job description into the jobdesc.txt file.")
        exit(1)

    result = match_resume_to_jd(resume_text, JOB_DESCRIPTION)
    risks = check_tokenization_risks(resume_text, JOB_DESCRIPTION)
    near_misses = find_near_misses(result['missing'], resume_text)
    print_report(result, risks, near_misses)