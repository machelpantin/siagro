# siagro

Test charts for Siagro visualizer

## Quarto Website

This repository contains a Quarto website that is automatically published to GitHub Pages.

### Local Development

To render the website locally:

```bash
quarto render
```

To preview the website:

```bash
quarto preview
```

### GitHub Pages Deployment

The website is automatically deployed to GitHub Pages when changes are pushed to the `main` branch. The deployment is handled by GitHub Actions (see `.github/workflows/publish.yml`).

### Structure

- `_quarto.yml` - Main configuration file
- `index.qmd` - Homepage
- `about.qmd` - About page
- `styles.css` - Custom CSS styles
- `docs/` - Output directory (generated, not tracked in git)
