#!/bin/bash
# Build wheels for Linux (Docker compatible)
set -euo pipefail

echo "🐧 Building Linux wheels for Docker..."

# Clean previous wheels to avoid confusion between runs
rm -rf dist
mkdir -p dist

# Build using manylinux Docker image for multiple architectures
# Note: with abi3 (cp39-abi3) only one wheel per architecture is produced, regardless of interpreters.
# aarch64 (Apple Silicon / ARM64)
docker run --rm -v "$(pwd)":/io \
  --platform linux/arm64 \
  ghcr.io/pyo3/maturin:latest \
  build --release --out dist \
  --target aarch64-unknown-linux-gnu \
  --manylinux 2_17 \
  -i python3.9 -i python3.10 -i python3.11 -i python3.12 -i python3.13

# x86_64 (Intel/AMD 64-bit)
docker run --rm -v "$(pwd)":/io \
  --platform linux/amd64 \
  ghcr.io/pyo3/maturin:latest \
  build --release --out dist \
  --target x86_64-unknown-linux-gnu \
  --manylinux 2_17 \
  -i python3.9 -i python3.10 -i python3.11 -i python3.12 -i python3.13

# Verify output
if [ -d dist ] && ls dist/*.whl >/dev/null 2>&1; then
  echo "✅ Linux wheels built in ./dist/"
  ls -la dist/
else
  echo "💥 maturin succeeded but no wheels were found in ./dist/" >&2
  exit 1
fi

# Also sync wheels/ folder for Dockerfiles that expect /wheels
rm -rf wheels
mkdir -p wheels
cp -v dist/*.whl wheels/

# Optional: Build for specific architectures
# For aarch64 (ARM64):
# docker run --rm -v $(pwd):/io \
#   --platform linux/arm64 \
#   ghcr.io/pyo3/maturin:latest \
#   build --release --out dist

echo "
📦 Built wheels are manylinux compatible and work in Docker!
Two common ways to use them:
- Copy from dist/ (default):
  COPY dist/rusticsoup-*.whl /wheels/
  RUN pip install /wheels/rusticsoup-*.whl
- Or copy the pre-synced wheels/ directory (matches Dockerfiles expecting /wheels):
  COPY wheels/ /wheels/
  RUN python -m pip install /wheels/rusticsoup-*.whl
"