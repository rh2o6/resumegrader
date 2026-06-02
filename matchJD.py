from tika import parser
import re
from collections import Counter
from tech_keyword import TECH_KEYWORDS, NEAR_MISS_HINTS

# ===== 1. CONFIGURATION =====

RESUME_PATH = 'robertresumefall.pdf'

# Paste the job description here as a multi-line string
JOB_DESCRIPTION = """
At KPMG, you’ll join a team of diverse and dedicated problem solvers, connected by a common cause turning insight into opportunity for clients and communities around the world.

As a Security Program Support Intern, you will support day‑to‑day activities within the CISO Office and the Digital Security Group. The role provides hands‑on exposure to security operations, compliance tracking, reporting, project coordination and cybersecurity awareness initiatives. You’ll work alongside experienced security professionals, assist with routine security tasks, and collaborate with other ITS and security teams across the organization.

This internship is designed to help you build foundational skills in information security, gain experience working in an enterprise environment, and learn how cybersecurity programs operate in practice.

The Support Intern will be a member of the Digital Security Group at KPMG and work under the supervision of the Senior Manager in the CISO Office.

What You Will Do

Support the CISO Office with day-to-day security program activities and ad hoc tasks
Collaborate with Digital Security Group (DSG), DevSecOps, and other ITS teams to coordinate, track, and follow up on key security initiatives, priorities, and compliance activities
Assist with project coordination by scheduling and organizing meetings, preparing agendas, capturing meeting notes, action items, owners, and next steps
Follow up with internal teams and external vendors on assigned tasks to support timely progress and delivery
Maintain project trackers, task lists, and status logs to support visibility into ongoing work, dependencies, and risks
Help track remediation activities for security and compliance findings using global compliance dashboards
Contribute to the creation of cybersecurity awareness and education materials.
Performs other security duties, when required
Help support basic automation initiatives for security-related processes
Perform other security-related duties as assigned

What You Bring To The Role

Currently enrolled in a university or college program related to Information Technology, Computer Science, Project Management or a related field 
Strong organizational and time‑management skills, with the ability to track multiple tasks and follow through on commitments
Ability to collaborate effectively with team members across security and ITS functions 
Proactive, organized, and self‑motivated, with a willingness to learn and take initiative 
Strong written and verbal communication skills, with attention to detail 
Foundational understanding of common cybersecurity challenges faced by organizations (e.g., phishing, data protection, cyber awareness, etc.)

KPMG Ontario Region Pay Range Information

The expected base salary range for this position is $43,500 to $60,000 and may be eligible for bonus awards. The determination of an applicant’s base salary within this range is based on the individual’s location, skills & competencies, and unique qualifications. In addition, KPMG offers a comprehensive and competitive Total Rewards program.

Providing you with the support you need to be at your best

Our Values, The KPMG Way

Integrity, we do what is right | Excellence, we never stop learning and improving | Courage, we think and act boldly | Together, we respect each other and draw strength from our differences | For Better, we do what matters

KPMG in Canada is a proud equal opportunities employer and we are committed to creating a respectful, inclusive and barrier-free workplace that allows all of our people to reach their full potential. A diverse workforce is key to our success and we believe in bringing your whole self to work. We welcome all qualified candidates to apply and hope you will choose KPMG in Canada as your employer of choice.

Adjustments and accommodations throughout the recruitment process

At KPMG, we are committed to fostering an inclusive recruitment process where all candidates can be themselves and excel. We aim to provide a positive experience and are prepared to offer adjustments or accommodations to help you perform at your best. Adjustments (informal requests), such as extra preparation time or the option for micro breaks during interviews, and accommodations (formal requests), such as accessible communication supports or technology aids, are tailored to individual needs and role requirements. You will have an opportunity to request an adjustment or accommodation at any point throughout the recruitment process. If you require support, please contact KPMG’s Employee Relations Service team by calling 1-888-466-4778.

AI Usage

We embrace the use of artificial intelligence (AI) to enhance the candidate experience and streamline our recruitment processes. AI tools may help with organizing applications or surfacing relevant qualifications. However, no hiring decisions are made using AI. Every hiring decision is made by our hiring managers and recruitment professionals, who are equipped with training that empowers them to use these tools responsibly. AI technologies used in our recruitment process undergo detailed risk assessments, including security and privacy requirements, that align with KPMG’s Trusted AI framework.

We believe technology should empower human judgment, not replace it. It’s one of the many ways we’re delivering on our vision of being a technology-first, people-driven firm.

"""

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
            warnings.append(f"JD uses '{hyphenated}' — not found in resume")

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
                warnings.append(f"JD uses acronym '{acronym.upper()}' — add it alongside '{full}' in resume")
            if jd_has_full and not resume_has_full:
                warnings.append(f"JD uses full phrase '{full}' — spell it out in resume")

    return warnings


# ===== 7. REPORT =====

def print_report(result, risk_warnings, near_misses):
    print("=" * 70)
    print("ATS MATCH REPORT (strict word-boundary mode)")
    print("=" * 70)

    rate = result['match_rate'] * 100
    crit = result['critical_match_rate'] * 100

    print(f"\n📊 Overall keyword match: {len(result['matched'])}/{len(result['jd_keywords'])} ({rate:.0f}%)")
    print(f"🎯 Must-have match:       {len(result['must_haves'] & result['matched'])}/{len(result['must_haves'])} ({crit:.0f}%)")

    print("\n" + "─" * 70)
    if rate >= 75:
        print("✅ STRONG MATCH — likely to pass keyword screening")
    elif rate >= 50:
        print("🟡 MODERATE MATCH — borderline, optimize gaps below")
    else:
        print("🔴 WEAK MATCH — significant gaps, likely auto-rejected")
    print("─" * 70)

    print(f"\n✅ MATCHED KEYWORDS ({len(result['matched'])}):")
    for kw in sorted(result['matched']):
        print(f"   ✓ {kw}")

    print(f"\n❌ MISSING KEYWORDS ({len(result['missing'])}):")
    for kw in sorted(result['missing']):
        marker = "🔴" if kw in result['missing_critical'] else "  "
        hint_note = ""
        if kw in near_misses:
            hint_note = f"  ← you have: {', '.join(near_misses[kw])}"
        print(f"   {marker} {kw}{hint_note}")

    if result['missing_critical']:
        print(f"\n⚠️  CRITICAL GAPS (mentioned as required in JD):")
        for kw in sorted(result['missing_critical']):
            print(f"   🔴 {kw}")

    if near_misses:
        print(f"\n💡 NEAR-MISSES (easy wins — add the exact phrase):")
        for kw, hints in sorted(near_misses.items()):
            print(f"   • JD wants '{kw}' — you wrote '{hints[0]}'. Add '{kw}' explicitly.")

    if risk_warnings:
        print(f"\n⚠️  TOKENIZATION RISKS:")
        for w in risk_warnings:
            print(f"   • {w}")

    print("\n" + "=" * 70)

# ===== 8. RUN =====

if __name__ == '__main__':
    resume_text = extract_resume_text(RESUME_PATH)
    if not JOB_DESCRIPTION.strip() or 'PASTE THE FULL' in JOB_DESCRIPTION:
        print("❌ Please paste a job description into the JOB_DESCRIPTION variable.")
        exit(1)

    result = match_resume_to_jd(resume_text, JOB_DESCRIPTION)
    risks = check_tokenization_risks(resume_text, JOB_DESCRIPTION)
    near_misses = find_near_misses(result['missing'], resume_text)
    print_report(result, risks, near_misses)