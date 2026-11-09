# 四种图像解析算法 Docker 镜像

SEM 微观图像分割、曲线提取、柱状图解析、XRD 谱图解析的已有镜像归档。平台为 **Linux x86_64 / amd64**。

| 算法 | 镜像标签 | 容器端口 | API |
|---|---|---|---|
| SEM | `ceramics-algorithms/sem:20261021-7228e529190e` | 8012 | `/segment` |
| 曲线 | `plextract-curve-service:local-20261009` | 8013 | `/curve` |
| 柱状图 | `plextract-bar-service:gpu-20261014` | 6262 | `/analyze/bar` |
| XRD | `plextract-xrd-service:gpu-20260908` | 8013 | `/analyze/xrd` |

## 下载与导入

打开 [Releases](https://github.com/XTanpk/ceramics-image-algorithms/releases/tag/images-20261021)，下载全部 `ceramics-four-images.tar.partNNN`、`images.json`、`SHA256SUMS` 和 `import_images.py` 到同一目录。

```bash
python import_images.py /path/to/downloads
# 仅校验文件，不导入
python import_images.py /path/to/downloads --verify-only
```

需要 Python 3.8+ 和可访问的 Docker Engine。脚本先校验每卷大小与 SHA-256，再按编号流式传给 `docker load`，最后核对四个镜像的配置摘要。无需拼接额外的大文件。分卷总大小为 13.78 GiB，Docker 解压后的占用更大；三个 GPU 镜像共享基础层。

也可在 Linux 下手动导入：

```bash
sha256sum -c SHA256SUMS
cat ceramics-four-images.tar.part[0-9][0-9][0-9] | docker load
```

## 版本与运行条件

镜像来自项目本地已有归档，保留原始配置与层内容；四个镜像合并导出时仅对共享层去重，并移除了旧 SEM 版本。发布标签记录 2026-10-21 的镜像集合，具体算法版本见上表；这次发布没有重新训练或构建算法。

曲线、柱状图和 XRD 的 GPU 运行需要 NVIDIA 驱动与 NVIDIA Container Toolkit。SEM 镜像包含补入的代码及 `unet.h5`。实际启动参数、模型挂载和业务接入需按部署环境配置。本仓库提供镜像分发与导入，未执行本次目标服务器上的推理验收。

`images.json` 记录原镜像标签、平台、配置摘要、文件层摘要、启动命令和端口，以及归档与分卷的校验信息。大镜像放在 Releases 中，Git 仓库保存说明、清单和导入脚本。

镜像包含第三方运行库、算法和模型权重；相关权利与许可证仍归各原作者所有，本仓库不更改其授权条件。
