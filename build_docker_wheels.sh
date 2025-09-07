#!/bin/bash
# Build wheels for Linux (Docker compatible)

echo "🐧 Building Linux wheels for Docker..."

# Build using manylinux Docker image
docker run --rm -v $(pwd):/io \
  ghcr.io/pyo3/maturin:latest \
  build --release --out dist --interpreter python3.8 python3.9 python3.10 python3.11 python3.12

echo "✅ Linux wheels built in ./dist/"
ls -la dist/

# Optional: Build for specific architectures
# For aarch64 (ARM64):
# docker run --rm -v $(pwd):/io \
#   --platform linux/arm64 \
#   ghcr.io/pyo3/maturin:latest \
#   build --release --out dist

echo "
📦 Built wheels are manylinux compatible and work in Docker!
Use in Dockerfile:
  COPY dist/rusticsoup-*.whl /tmp/
  RUN pip install /tmp/rusticsoup-*.whl
"