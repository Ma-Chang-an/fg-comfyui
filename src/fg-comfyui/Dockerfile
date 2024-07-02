# syntax = docker/dockerfile:experimental
FROM python:3.10.9-slim as deps

RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --no-cache-dir \
    torch \
    torchsde \
    torchvision \
    einops \
    transformers>=4.25.1 \
    safetensors>=0.3.0 \
    aiohttp \
    pyyaml \
    Pillow \
    scipy \
    tqdm \
    psutil \
    kornia>=0.7.1 -i https://pypi.tuna.tsinghua.edu.cn/simple

FROM alpine/git:2.36.2 as repos

RUN git clone https://github.com/comfyanonymous/ComfyUI.git /code && \
    cd /code && \
    git checkout 0a03009808a5ad13fa3a44edbabcae68576c3982 && \
    rm -rf .git

FROM alpine/git:2.36.2 as custom_nodes

WORKDIR /custom_nodes

RUN git clone https://github.com/ltdrdata/ComfyUI-Manager.git && \
    cd ComfyUI-Manager && \
    git checkout 02b2bf96d24ed6297dad8f676aa68d7512a166b3 && \
    rm -rf .git

FROM python:3.10.9-slim as models

RUN apt update && apt install -y aria2

RUN aria2c -x 16 --dir "/models" --out "sd-v1-5-inpainting.ckpt" "https://huggingface.co/runwayml/stable-diffusion-inpainting/resolve/main/sd-v1-5-inpainting.ckpt"


FROM python:3.10.9-slim as base

ENV BUILTIN="/built-in"
ENV COMFYUI="/comfyui"
ENV NAS_DIR="/mnt/auto/comfyui"
ENV VIRTUAL_NAS="/virtual_nas"
ENV GROUP_ID=1003
ENV USER_ID=1003
ENV GROUP_NAME=paas
ENV USER_NAME=paas
ENV VIRTUAL_ENV="${NAS_DIR}/venv"

RUN groupadd -g ${GROUP_ID} ${GROUP_NAME} && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} ${USER_NAME}
RUN sed -i 's/http:\/\/deb.debian.org/http:\/\/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    sed -i 's/http:\/\/security.debian.org/http:\/\/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list

RUN --mount=type=cache,target=/var/cache/apt \
    apt update && \
    apt install -y \
    rsync vim git curl wget jq ffmpeg \
    gcc g++ unzip build-essential

# 从依赖镜像获取所需的依赖文件，并映射至 /mnt/auto/comfyui
COPY --from=deps --chown=${USER_NAME}:${GROUP_NAME} /venv /venv

# 获取 ComfyUI 代码
COPY --from=repos --chown=${USER_NAME}:${GROUP_NAME} /code ${COMFYUI} 
# 复制内置文件
COPY --chown=${USER_NAME}:${GROUP_NAME} ./entrypoint.bash /entrypoint.bash

# 使用 venv 环境
ENV VIRTUAL_ENV="/venv"
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"

RUN touch /IMAGE_TAG && chown ${USER_NAME}:${GROUP_NAME} /IMAGE_TAG

WORKDIR /

# 确保依赖最新
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r ${COMFYUI}/requirements.txt --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple && \ 
    find ${COMFYUI} -type f -name requirements.txt | xargs -I {} pip install -r {} -i https://pypi.tuna.tsinghua.edu.cn/simple

# 移动自带文件
RUN mkdir -p ${BUILTIN}/custom_nodes && \
    chown ${USER_NAME}:${GROUP_NAME} ${BUILTIN}/custom_nodes && \
    mv ${COMFYUI}/custom_nodes/* ${BUILTIN}/custom_nodes

RUN mkdir -p ${VIRTUAL_NAS} && chown ${USER_NAME}:${GROUP_NAME} ${VIRTUAL_NAS}
RUN rm -rf /home/paas && chown ${USER_NAME}:${GROUP_NAME} /home


ARG IMAGE_TAG="${IMAGE_TAG}"
ENV IMAGE_TAG=${IMAGE_TAG}

ENTRYPOINT [ "/entrypoint.bash" ]

FROM base as builtin

COPY --chown=${USER_NAME}:${GROUP_NAME}  . /docker

# lite 轻量版镜像
FROM base as lite

ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
USER ${USER_NAME}

EXPOSE 8000

RUN --mount=type=bind,from=builtin,source=/docker,target=/docker \
    bash /docker/init.bash

RUN chmod a+x /entrypoint.bash

# sd1.5 内置 sd1.5 模型及推荐自定义节点的镜像
FROM base as sd1.5

ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
# 内置模型
COPY --from=models --chown=${USER_NAME}:${GROUP_NAME} /models ${BUILTIN}/models/checkpoints

# 内置自定义节点
COPY --from=custom_nodes --chown=${USER_NAME}:${GROUP_NAME} /custom_nodes ${BUILTIN}/custom_nodes

# 更新依赖至最新
RUN --mount=type=cache,target=/root/.cache/pip \
    find ${BUILTIN}/custom_nodes -type f -name requirements.txt | xargs -I {} pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r {}

USER ${USER_NAME}

EXPOSE 8000

RUN --mount=type=bind,from=builtin,source=/docker,target=/docker \
    bash /docker/init.bash

RUN chmod a+x /entrypoint.bash
