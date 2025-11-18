# GitHub Pages Setup Instructions

This repository is configured to automatically publish a Quarto website to GitHub Pages. Follow these steps to complete the setup:

## Enable GitHub Pages

1. Go to your repository on GitHub: https://github.com/machelpantin/siagro
2. Click on **Settings** (top menu)
3. In the left sidebar, click on **Pages** (under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
   - (The workflow file `.github/workflows/publish.yml` will handle the build and deployment)
5. Click **Save** if needed

## Trigger the First Deployment

Once GitHub Pages is enabled, you can trigger the deployment in two ways:

### Option 1: Push to main branch
After merging this PR to the `main` branch, the workflow will automatically run and deploy the site.

### Option 2: Manual trigger
1. Go to the **Actions** tab in your repository
2. Click on "Publish Quarto Website" workflow
3. Click "Run workflow" button
4. Select the `main` branch and click "Run workflow"

## Accessing Your Website

After the deployment completes successfully (usually 2-5 minutes):
- Your website will be available at: `https://machelpantin.github.io/siagro/`
- The URL will also be shown in the Actions workflow output

## Repository Settings Required

The workflow requires the following permissions (already configured in the workflow file):
- `contents: read` - To read repository files
- `pages: write` - To deploy to GitHub Pages
- `id-token: write` - For deployment authentication

## Troubleshooting

If the deployment fails:
1. Check the Actions tab for error messages
2. Ensure GitHub Pages is enabled in repository settings
3. Verify that the workflow has the necessary permissions
4. Make sure the `main` branch protection rules (if any) allow the workflow to run

## Local Development

To work on the website locally:

```bash
# Install Quarto (if not already installed)
# Visit: https://quarto.org/docs/get-started/

# Render the website
quarto render

# Preview the website (with live reload)
quarto preview
```

The rendered site will be in the `docs/` directory.
