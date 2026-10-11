# Usage: source /root/ContextFlow/env.sh
# Environment settings for this cloud host; does not modify Conda base.
export CONTEXTFLOW_ROOT="/root/ContextFlow"
export CONTEXTFLOW_STORAGE_ROOT="/context-flow-storage/contextflow"
if ! mountpoint -q "$CONTEXTFLOW_STORAGE_ROOT"; then
    echo "ContextFlow 文件存储未挂载：$CONTEXTFLOW_STORAGE_ROOT" >&2
    return 1 2>/dev/null || exit 1
fi
export UV_CACHE_DIR="/app/contextflow/uv-cache"
export UV_PYTHON_INSTALL_DIR="$CONTEXTFLOW_STORAGE_ROOT/runtimes/python"
export UV_LINK_MODE="copy"
export HF_HOME="/app/contextflow/huggingface"
export LEROBOT_HOME="$CONTEXTFLOW_STORAGE_ROOT/datasets"
export OPENPI_DATA_HOME="$CONTEXTFLOW_STORAGE_ROOT/assets/openpi"
export LIBERO_CONFIG_PATH="$CONTEXTFLOW_STORAGE_ROOT/configs/libero"
export MUJOCO_GL="egl"
export PYOPENGL_PLATFORM="egl"
export JAX_DEFAULT_MATMUL_PRECISION="float32"
export XLA_PYTHON_CLIENT_PREALLOCATE="false"
export GIT_LFS_SKIP_SMUDGE="1"
export PYTHONPATH="$CONTEXTFLOW_ROOT/src:$CONTEXTFLOW_ROOT/third_party/libero:$CONTEXTFLOW_ROOT/packages/openpi-client/src${PYTHONPATH:+:$PYTHONPATH}"
# The inherited localhost:7897 proxy fails TLS connections to GitHub on this host.
# Use direct networking only in shells that source this file.
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
