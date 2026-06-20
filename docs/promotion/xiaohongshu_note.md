# 小红书笔记：cortex-visualization skill

## 标题

R和Python皮层图终于对齐了

## 正文

皮层图不难画，难的是画得一致。

尤其是一个项目里同时有 R 和 Python 两条路线时，ggseg、python 绘图、Workbench 风格经常会出现形状、边界、颜色、质感都不太一样的问题。

所以我做了一个 cortex-visualization skill。

01｜核心想法

不要让 R 和 Python 各自凭感觉画。

先从 R ggseg / ggsegverse 导出 canonical polygon CSV，然后 Python 和 R 都读同一份几何。

如果需要颜色也严格一致，就共享 fill_hex。

02｜为什么边界更顺了？

原始 polygon 有些边界会偏锯齿。

现在默认用 one-pass Chaikin-smoothed asset：更平滑，更接近我之前 subcortex skill 的哑光平面风格。

03｜现在支持多 atlas

不只是 DK。

目前有 DK、DKT、Destrieux、Yeo7/17、Schaefer100、Glasser、Brainnetome、Gordon、Power。

04｜适合谁？

适合想把 cortex ROI 图做成可复现 workflow 的人：

Python 算值，R 画图，或者两边都要保留，但最后图要长得一样。

项目：
https://github.com/mqqq333/cortex-visualization-skill

A Man's Brainhole｜脑科学  计算神经科学  NeuroAI
一起读论文、拆方法、做工具，一起学习进步。

## Hashtags

#脑科学 #计算神经科学 #NeuroAI #ggseg #Python科研 #R语言 #数据可视化 #科研工具 #可复现研究

## 轮播卡片文案

1. R 和 Python 皮层图，终于能对齐了
2. 痛点：同一个 atlas，不同 backend 画出来不一样
3. 方法：R ggseg 导出共享 polygon CSV
4. Python/R：读同一份几何，同一套 fill_hex
5. 风格：白底、哑光、深色边界、Chaikin 平滑
6. Atlas：DK、Yeo、Schaefer、Glasser 等
7. GitHub：cortex-visualization-skill

