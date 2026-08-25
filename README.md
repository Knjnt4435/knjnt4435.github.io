# OptoVLab Website

This repository hosts the public website for **OptoVLab**, a self-improving
agentic virtual laboratory for organic optoelectronic research.

- Website: <https://optovlab.github.io/>
- Research platform source: <https://github.com/YajingSun-Group/OptoVLab>

The site presents the manuscript overview and a deterministic nine-stage
animation covering literature mining, device-level OLED graph modeling,
scientific critique, experimental planning, and feedback-driven optimization.

## Repository Layout

```text
index.html                  Project and manuscript overview
demo/index.html             Interactive OptoVLab workflow
demo/imgs/                  Optimized media and manuscript figures
agents_logs/index.html      Redirect to the data-mining stage
pathway_explorer/index.html Redirect to the feedback-loop stage
scripts/check_site.py       Public-file and local-link audit
```

## Local Preview

```bash
python3 -m http.server 14001 --bind 127.0.0.1
```

Then open <http://127.0.0.1:14001/>.

Run the release audit with:

```bash
python3 scripts/check_site.py
```

## Deployment

Pushes to `main` are validated and deployed through GitHub Actions. The Pages
artifact contains only the site documents and media listed above.

Headline dataset, model, and experimental values shown on the site are reported
manuscript results. The Stage 8 capability radar is explicitly illustrative and
is not presented as benchmark data.

## Research Team

OptoVLab is developed by researchers at Tianjin University and Shenzhen
University. Please use the corresponding-author contacts shown on the website
for research inquiries.
