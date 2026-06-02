# Local Installation & Running Instructions.

# Step 1 - Clone the repo

In your terminal, enter the command 'git clone https://github.com/rh2o6/resumegrader'

# Step 2 - Provide Resume & Job Description

In the same directory upload the your resume as a .pdf file. Also paste the job description into the 'jobdesc.txt' file.

# Step 3 - Run matchJD.py

This file provides a report on ur resume vs the job description. Showing an overall job match based on keywords, missing keywords and near misses such as using acronyms instead of full technology names.

Below is an example report:

======================================================================
ATS MATCH REPORT
======================================================================

Overall Keyword Match: 3/13 (23%)
Required Keyword Match: 0/3 (0%)

----------------------------------------------------------------------
Assessment: Weak Match
Significant keyword gaps may reduce ATS performance.
----------------------------------------------------------------------

Matched Keywords (3)
  ✓ compliance
  ✓ cybersecurity
  ✓ training

Missing Keywords (10)
  * ad  (Found similar term: active directory)
  * ai
    artificial intelligence
  * communication
    devsecops
    information security  (Found similar term: cybersecurity)
    organization
    project management
    teams
    time management

Critical Gaps (Required by Job Description)
  - ad
  - ai
  - communication

Near-Miss Keywords
  - Job description requests 'ad', but resume contains 'active directory'. Consider adding the exact phrase.
  - Job description requests 'information security', but resume contains 'cybersecurity'. Consider adding the exact phrase.

Tokenization Risks
  - JD uses acronym 'AD'. Please add it alongside 'active directory' in resume

======================================================================
