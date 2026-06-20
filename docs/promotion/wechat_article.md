---
title: "让 R ggseg 和 Python 画出同一种皮层图"
summary: "一个用于皮层 ROI 可视化的 Codex Skill：把 R ggseg/ggsegverse atlas 导出为共享 polygon CSV，让 Python 和 R 使用同一套几何、颜色和哑光风格。"
description: "面向 cortex atlas 图的 Python/R 双路线 skill，支持 DK、DKT、Destrieux、Yeo、Schaefer、Glasser、Brainnetome、Gordon、Power 等 atlas。"
author: "A Man's Brainhole"
sourceUrl: "https://github.com/mqqq333/cortex-visualization-skill"
coverImage: "assets/gallery/multi_atlas_showcase.png"
---

# 让 R ggseg 和 Python 画出同一种皮层图

皮层图本来不难画。

真正麻烦的是：当一个项目里同时有 Python 和 R 两条分析分支，或者你想让 cortex 图和 subcortex 图保持同一种质感时，不同工具画出来的形状、边界、颜色和材质经常会微妙地不一致。

我最近把这个问题整理成了一个 Codex Skill：**cortex-visualization skill**。

它的核心目标很简单：让皮层 ROI 图变成一个可复现、可检查、Python/R 都能走的 workflow，而不是每次都在不同绘图库之间重新调风格。

## 核心思路：共享几何，而不是各画各的

如果想让 R 和 Python 严格对齐，最可靠的路线不是让两个 backend 分别“差不多画一个 ggseg 风格图”。

更稳定的做法是：

```text
R ggseg atlas -> export polygon CSV
              -> Python renderer reads the same CSV
              -> R renderer reads the same CSV
              -> optional shared fill_hex for exact colours
```

也就是说，R `ggseg` / ggsegverse 负责提供 canonical atlas geometry。导出之后，Python 和 R 都只读同一份 polygon asset。这样坐标、parcel boundary、颜色映射才有机会真正一致。

## 为什么要做 Chaikin-smoothed 版本？

我之前最不满意的一点是：原始 cortex polygon 的边界有时会显得比较锯齿，而 subcortex 那边的视觉更平滑。

所以现在每个 atlas 都保留两份：

- raw polygon CSV：用于 provenance 和 debugging；
- one-pass Chaikin polygon CSV：用于默认展示。

Chaikin 不是为了改变 atlas，而是为了得到更接近 subcortex skill 的 flat vector 质感：白底、哑光填色、深色边界、没有 Workbench 那种 mesh / lighting / curvature。

## 现在不只是 DK

最开始 cortex skill 只有 DK。现在已经扩展成多 atlas 版本，包括：

- DK / DKT / Destrieux
- Yeo7 / Yeo17
- Schaefer 7-network / 17-network 100 parcels
- Glasser
- Brainnetome
- Gordon
- Power

README 顶部现在放的是 multi-atlas showcase，目的就是说明：这不是一个只服务 DK demo 的小脚本，而是一套可以继续扩展的 ggseg-derived cortex atlas workflow。

## 它适合什么场景？

如果你遇到过这些问题，它可能会有用：

- Python 里算完 ROI value，但想画 ggseg 风格的皮层图；
- R 可以画，但希望 Python 分支也保持同样形状和颜色；
- 想让 cortex 和 subcortex figure 放在一起时风格一致；
- 想保留 SVG/PDF 输出，而不是只拿 PNG；
- 想把 atlas geometry、join key、unmatched labels 都写清楚。

## 还有一个上游贡献方向

这个项目里沉淀出来的想法，也整理成了给 `python-ggseg` 的 upstream PR：共享 polygon atlas API，让 R ggseg 和 Python ggseg-style rendering 更容易严格对齐。

本地 skill 先服务自己的研究 workflow；如果上游接受，之后也可以把这套 interop 思路贡献回社区。

项目地址：

https://github.com/mqqq333/cortex-visualization-skill

相关 PR：

https://github.com/ggsegverse/python-ggseg/pull/10

## 关于这个频道

这里是 **A Man's Brainhole｜脑科学  计算神经科学  NeuroAI**。

我会在这里持续记录我读到的论文、做过的工具和踩过的坑：从脑区、神经数据、表征空间，到 AI 模型和可复现 workflow。希望每一篇都不只是“看个热闹”，而是能帮我们多理解一点大脑，也多理解一点连接大脑与 AI 的方法。

如果这篇文章对你有启发，欢迎点赞、评论、转发，也欢迎关注这个频道。我们一起读论文、拆方法、做工具，一起学习进步。

