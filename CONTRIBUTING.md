# Contributing to Sue the Map

Thank you for your interest in contributing!

## How to Contribute

1. **Fork** the repository
2. **Create a branch**: `git checkout -b feat/your-feature`
3. **Make your change** — keep it focused (one PR = one thing)
4. **Test**: open `sue_the_map.html` in Chrome and verify it works
5. **Push**: `git push origin feat/your-feature`
6. **Open a Pull Request** against `anaswara/sue-the-map`

## Regenerating the HTML

After changing `generate_html.py`:

```bash
python generate_html.py
```

After changing the raw Excel data:

```bash
python process_data.py
python generate_html.py
```

## Coding Style

- Vanilla JS only — no frameworks, no npm
- Keep CSS variables in `:root`
- Use `DM Sans` for body text, `DM Mono` for numbers, `Bebas Neue` for headings
- All colors via CSS variables — don't hardcode hex values in JS

## Bug Reports

Open a GitHub issue with:
- What you expected to happen
- What actually happened
- Browser and OS version
