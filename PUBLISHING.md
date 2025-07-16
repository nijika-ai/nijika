# Publishing Nijika to PyPI

This guide walks you through the process of publishing the Nijika AI Agent Framework to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [PyPI](https://pypi.org/account/register/) (production)
   - [TestPyPI](https://test.pypi.org/account/register/) (testing)

2. **Install Publishing Tools**:
   ```bash
   pip install --upgrade pip
   pip install --upgrade build twine
   ```

3. **API Tokens**: Generate API tokens for both PyPI and TestPyPI:
   - PyPI: Go to Account Settings → API tokens → Add API token
   - TestPyPI: Go to Account Settings → API tokens → Add API token

## Pre-Publishing Checklist

### 1. Update Version Information
- [x] Version updated in `setup.py` (1.0.0)
- [x] Version updated in `nijika/__init__.py` (1.0.0)
- [x] Version updated in `pyproject.toml` (1.0.0)

### 2. Update Repository URLs
**Important**: Update the GitHub URLs in the following files to match your actual repository:

In `setup.py`:
```python
url="https://github.com/nijika-ai/nijika",
project_urls={
    "Bug Reports": "https://github.com/nijika-ai/nijika/issues",
    "Source": "https://github.com/nijika-ai/nijika",
    "Documentation": "https://docs.nijika.ai",
    "Changelog": "https://github.com/nijika-ai/nijika/blob/main/CHANGELOG.md",
},
```

In `pyproject.toml`:
```toml
[project.urls]
Homepage = "https://github.com/nijika-ai/nijika"
Repository = "https://github.com/nijika-ai/nijika"
"Bug Reports" = "https://github.com/nijika-ai/nijika/issues"
Changelog = "https://github.com/nijika-ai/nijika/blob/main/CHANGELOG.md"
```

### 3. Verify Package Structure
```bash
# Check package structure
find nijika -name "*.py" | head -10

# Verify all required files exist
ls -la README.md LICENSE CHANGELOG.md CONTRIBUTING.md requirements.txt
```

### 4. Clean Previous Builds
```bash
# Remove old build artifacts
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
```

## Building the Package

### 1. Build the Distribution
```bash
# Build both source distribution and wheel
python -m build

# This creates:
# - dist/nijika-1.0.0.tar.gz (source distribution)
# - dist/nijika-1.0.0-py3-none-any.whl (wheel)
```

### 2. Verify the Build
```bash
# Check the contents
ls -la dist/

# Verify the wheel contents
python -m zipfile -l dist/nijika-1.0.0-py3-none-any.whl

# Check package metadata
python -m twine check dist/*
```

## Testing on TestPyPI

### 1. Upload to TestPyPI
```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# Username: __token__
# Password: [your TestPyPI API token]
```

### 2. Test Installation from TestPyPI
```bash
# Create a test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ nijika

# Test the installation
python -c "import nijika; print(nijika.__version__)"
```

### 3. Test Basic Functionality
```bash
# Test basic import and functionality
python -c "
import nijika
from nijika import Agent, AgentConfig, ProviderType
print('✅ Basic imports successful')
print(f'📦 Version: {nijika.__version__}')
"
```

## Publishing to PyPI

### 1. Final Verification
- [ ] TestPyPI installation works correctly
- [ ] All imports work as expected
- [ ] Version numbers are consistent
- [ ] Repository URLs are correct
- [ ] Documentation links are valid

### 2. Upload to PyPI
```bash
# Upload to production PyPI
python -m twine upload dist/*

# You'll be prompted for:
# Username: __token__
# Password: [your PyPI API token]
```

### 3. Verify Publication
```bash
# Check the package page
# https://pypi.org/project/nijika/

# Test installation from PyPI
pip install nijika

# Verify installation
python -c "import nijika; print(f'✅ Nijika {nijika.__version__} installed successfully')"
```

## Post-Publication Steps

### 1. Create a GitHub Release
```bash
# Tag the release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create a release on GitHub with:
# - Release notes from CHANGELOG.md
# - Link to PyPI package
# - Installation instructions
```

### 2. Update Documentation
- [ ] Update installation instructions in README.md
- [ ] Update documentation website
- [ ] Announce the release on social media/forums

### 3. Monitor the Release
- [ ] Check PyPI download statistics
- [ ] Monitor GitHub issues for bug reports
- [ ] Respond to community feedback

## Troubleshooting

### Common Issues

1. **Authentication Error**:
   ```bash
   # Make sure you're using the correct token format
   Username: __token__
   Password: pypi-[your-token-here]
   ```

2. **Package Already Exists**:
   ```bash
   # You cannot overwrite existing versions
   # Increment version number and rebuild
   ```

3. **Missing Dependencies**:
   ```bash
   # Install missing build dependencies
   pip install --upgrade setuptools wheel build twine
   ```

4. **File Not Found Errors**:
   ```bash
   # Check MANIFEST.in includes all necessary files
   python setup.py check --restructuredtext --strict
   ```

### Package Validation
```bash
# Validate package before upload
python -m twine check dist/*

# Check for common issues
python setup.py check --restructuredtext --strict

# Verify package metadata
python -c "
import pkg_resources
dist = pkg_resources.get_distribution('nijika')
print(f'Name: {dist.project_name}')
print(f'Version: {dist.version}')
print(f'Location: {dist.location}')
"
```

## Security Considerations

1. **API Token Security**:
   - Never commit API tokens to version control
   - Use environment variables or secure storage
   - Rotate tokens regularly

2. **Package Signing**:
   ```bash
   # Optional: Sign your packages
   python -m twine upload --sign dist/*
   ```

3. **Dependency Security**:
   ```bash
   # Check for known vulnerabilities
   pip audit
   ```

## Automation (Optional)

### GitHub Actions Workflow
Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Support

If you encounter issues during publishing:

1. **Check the PyPI Help**: https://pypi.org/help/
2. **Read the Packaging Guide**: https://packaging.python.org/
3. **Ask for Help**: Create an issue in the Nijika repository

## Next Steps

After successful publication:

1. **Monitor Usage**: Track downloads and user feedback
2. **Plan Updates**: Regular maintenance releases
3. **Community Building**: Engage with users and contributors
4. **Documentation**: Keep docs updated with new features

---

**Happy Publishing!** 🚀

The Nijika AI Agent Framework is now ready to be shared with the world. 