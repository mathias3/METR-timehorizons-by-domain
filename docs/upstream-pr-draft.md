# Draft PR for METR/eval-analysis-public

## Title
Add LICENSE file and clarify data licensing terms

## Description

This PR adds a missing `LICENSE` file to the repository and updates the README to clarify licensing terms for the Time Horizon benchmark data.

### Background

The `eval-analysis-public` README currently states "See LICENSE file for details" in the License section, but no LICENSE file exists in the repository root. This creates uncertainty for downstream users who want to build on this excellent work.

### Changes

1. **Add LICENSE file** (MIT License)
   - Consistent with METR's other public repositories (vivaria, public-tasks, hcast-public)
   - Permits derivative works with attribution
   - Aligns with the open research spirit evident in METR's public releases

2. **Update README License section**
   - Replace "See LICENSE file for details" with clear licensing statement
   - Add note about citation requirements (already present, but reinforced)
   - Clarify that data is available for research/analysis use

### Motivation

We are building a derivative visualization tool ([METR-timehorizons-by-domain](https://github.com/[YOUR_USERNAME]/METR-timehorizons-by-domain)) that:
- Transforms Time Horizon data into interactive charts
- Provides weekly-updated domain/model comparisons
- Cites METR's methodology and links to original sources

To publish this work responsibly, we need explicit licensing clarity. Based on METR's consistent MIT licensing pattern across all other public repos, we propose MIT for this repository as well.

### Proposed LICENSE file content

```
MIT License

Copyright (c) 2025 METR

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### Alternative: If MIT is not appropriate

If METR prefers a different license (e.g., CC-BY 4.0 for data, Apache 2.0 for code), please let us know and we'll update our downstream work accordingly. The key need is **explicit clarity** so derivative works can properly attribute and comply.

### Checklist

- [ ] LICENSE file added to repository root
- [ ] README.md License section updated to reference LICENSE file
- [ ] (Optional) Add note about citation requirements in LICENSE or README

---

**Note to METR team**: Thank you for making this data publicly available! The Time Horizon methodology is incredibly valuable for the AI safety community. We're happy to adjust this PR based on your preferred licensing approach—we just need clarity to proceed responsibly.

If you'd prefer to handle licensing internally, please let us know your timeline and we'll wait for the official statement before publishing our derivative work.

**Contact**: [Your email or GitHub handle]
