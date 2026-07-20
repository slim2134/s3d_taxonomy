# Contributing

Every system is one YAML file in `systems/`, validated against `schema/system.schema.json`.

## Adding a system

1. Copy an existing complete entry (e.g. `systems/prio.yaml`) as a template.
2. Name the file in kebab-case after the system (`my-new-system.yaml`).
3. Fill in the fields (see rules below).
4. Run the checks locally:
   ```bash
   pip install pyyaml jsonschema
   python scripts/validate.py
   python scripts/build_readme.py
   python scripts/build_db.py
   ```
5. Commit your new YAML file plus the regenerated `README.md` and `data/` files, then open a PR.

If you don't have time for a full analysis, you can still contribute a stub: set
`analysis_status: needs-analysis`, fill in `name`, `developer`, `source`, and
`description`, and leave `hoepman`/`oecd` as empty lists. Completing existing
stubs is equally welcome.

## Analysis rules

These keep the dataset consistent and are checked in review:

- **Rationales must reference the system's specific mechanics.** Explain *how this
  system* implements the strategy or principle, not what the strategy means in
  general. Bad: "Hide means making data unobservable." Good: "Secret sharing makes
  each individual value unobservable to any single server."
- **Descriptions are one sentence,** objective, and describe how the system
  functions. No marketing language, no framing around any particular research
  agenda.
- **Technologies vs. techniques:** `technologies` are infrastructure and deployed
  components (e.g. `trusted-execution-environment`, `bigquery`);
  `techniques` are algorithmic or methodological mechanisms (e.g.
  `shamir-secret-sharing`, `gradient-clipping`). Both use kebab-case.
- **Controlled vocabulary.** Hoepman strategies and OECD principles must come from
  the enums in the schema. Note that Hoepman's "aggregate" was renamed
  "abstract"; this repo uses `abstract`.
- **Sources** should be the canonical origin: the paper (PoPETs/PETS, PEPR, arXiv)
  or the developer's own engineering blog or documentation. Not press coverage.
- Only tag a strategy or principle if the system *materially* implements it. Two
  or three well-justified tags beat six weak ones.

## Scope

In scope: deployed or published systems whose primary purpose is privacy
preservation, including differential privacy, federated learning, secure
multi-party computation, homomorphic encryption, TEE/confidential computing,
PIR, anonymous credentials, and transparency/enforcement infrastructure.

Out of scope: general security tools with no privacy-specific design, and
products with no public technical documentation.

## CI

Every PR runs `scripts/validate.py` and verifies `README.md` and `data/systems.json`
are up to date with the YAML files. PRs that fail either check will not be merged.
