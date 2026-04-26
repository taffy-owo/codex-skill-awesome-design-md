<div align="center">

# 🎨 Codex Skill: Awesome Design MD

**为 AI 编码助手注入品牌级设计直觉**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Templates](https://img.shields.io/badge/品牌模板-69-blueviolet)](awesome-design-md/references/templates/)
[![Upstream](https://img.shields.io/badge/上游-VoltAgent%2Fawesome--design--md-orange)](https://github.com/VoltAgent/awesome-design-md)

[English](README_EN.md) | **中文**

</div>

---

## 📖 简介

一个可独立发布的 [Codex](https://github.com/openai/codex) 技能包，让你的 AI 编码助手在生成前端 UI 时，自动套用 **69 个知名品牌** 的完整设计规范（`DESIGN.md`），而非千篇一律的默认样式。

每个 `DESIGN.md` 遵循 [Google Stitch](https://github.com/nicepkg/nice-getdesign) 格式，包含 9 大标准章节：

| # | 章节 | 内容 |
|---|------|------|
| 1 | Visual Theme & Atmosphere | 整体视觉风格和美学基调 |
| 2 | Color Palette & Roles | 精确 HEX / RGBA 色值与使用规则 |
| 3 | Typography Rules | 字体族、字号、字重 |
| 4 | Component Stylings | 按钮、卡片、输入框等组件规范 |
| 5 | Layout Principles | 间距、栅格、留白系统 |
| 6 | Depth & Elevation | 阴影与层级体系 |
| 7 | Do's and Don'ts | 品牌设计底线 |
| 8 | Responsive Behavior | 断点与响应式策略 |
| 9 | Agent Prompt Guide | AI 专用快速参考 |

## ✨ 亮点

- 🏢 **69 个品牌** — 覆盖 AI、开发工具、SaaS、金融、汽车、消费科技等领域
- 📦 **完全本地化** — 无需 API、无需网络，Markdown 即取即用
- 🔧 **CLI 工具** — `list` / `install` 一键操作
- 🔄 **上游同步** — 脚本自动拉取 VoltAgent 仓库和 `getdesign` npm 包的最新模板
- 🤖 **多 Agent 支持** — 内含 OpenAI Agent YAML 配置

## 🏷️ 覆盖品牌

<details>
<summary>查看全部 69 个品牌</summary>

### AI & LLM 平台
`claude` · `cohere` · `elevenlabs` · `minimax` · `mistral.ai` · `ollama` · `opencode.ai` · `replicate` · `runwayml` · `together.ai` · `voltagent` · `x.ai`

### 开发工具 & IDE
`cursor` · `expo` · `lovable` · `raycast` · `superhuman` · `vercel` · `warp`

### 后端、数据库 & DevOps
`clickhouse` · `composio` · `hashicorp` · `mongodb` · `posthog` · `sanity` · `sentry` · `supabase`

### 生产力 & SaaS
`cal` · `intercom` · `linear.app` · `mintlify` · `notion` · `resend` · `zapier`

### 设计 & 创意工具
`airtable` · `clay` · `figma` · `framer` · `miro` · `webflow`

### 金融科技 & 加密
`binance` · `coinbase` · `kraken` · `mastercard` · `revolut` · `stripe` · `wise`

### 电商 & 零售
`airbnb` · `meta` · `nike` · `shopify` · `starbucks`

### 媒体 & 消费科技
`apple` · `ibm` · `nvidia` · `pinterest` · `playstation` · `spacex` · `spotify` · `theverge` · `uber` · `vodafone` · `wired`

### 汽车
`bmw` · `bugatti` · `ferrari` · `lamborghini` · `renault` · `tesla`

</details>

## 🚀 安装

### 方式一：通过 Codex 内置 skill-installer

```bash
python <CODEX_HOME>/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo taffy-owo/codex-skill-awesome-design-md \
  --path awesome-design-md
```

### 方式二：指定 GitHub URL

```bash
python <CODEX_HOME>/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --url https://github.com/taffy-owo/codex-skill-awesome-design-md/tree/main/awesome-design-md
```

安装后重启 Codex 即可生效。

## 📋 使用

### 查看所有可用模板

```bash
python scripts/apply_template.py list
python scripts/apply_template.py list --match stripe   # 模糊搜索
python scripts/apply_template.py list --json            # JSON 输出
```

### 安装模板到项目

```bash
# 安装 Vercel 风格到当前项目
python scripts/apply_template.py install vercel --project /path/to/app

# 安装 Linear 风格到指定输出路径
python scripts/apply_template.py install linear --out /path/to/app/docs/DESIGN.md

# 强制覆盖已存在的 DESIGN.md
python scripts/apply_template.py install stripe --project . --force
```

支持别名：`linear` → `linear.app`，`mistral` → `mistral.ai`，`xai` → `x.ai` 等。

### 同步上游更新

```bash
python scripts/sync_upstream.py
```

自动拉取 VoltAgent GitHub 仓库和 `getdesign` npm 包的最新模板。

## 🗂️ 仓库结构

```
.
├── awesome-design-md/          # Codex 技能目录（安装时拷贝这个）
│   ├── SKILL.md                # 技能定义文件
│   ├── agents/
│   │   └── openai.yaml         # OpenAI Agent 集成配置
│   ├── scripts/
│   │   ├── apply_template.py   # 模板列表 / 安装 CLI
│   │   └── sync_upstream.py    # 上游同步脚本
│   └── references/
│       ├── templates/          # 69 个 DESIGN.md 模板 + manifest.json
│       └── upstream/           # 上游快照和同步元数据
├── LICENSE
├── README.md                   # ← 你在这里（中文）
└── README_EN.md                # 英文版
```

## 🎯 快速选型指南

| 风格方向 | 推荐品牌 |
|----------|----------|
| 开发者基础设施 / 精确单色 | `vercel` · `hashicorp` · `replicate` · `warp` · `ibm` |
| 极简 SaaS / 生产力工具 | `linear.app` · `notion` · `mintlify` · `cal` |
| 暗色 AI / 构建者产品 | `claude` · `cursor` · `supabase` · `raycast` · `resend` |
| 动效丰富 / 营销导向 | `framer` · `stripe` · `clay` · `spotify` · `renault` |
| 编辑感 / 奢侈品质感 | `apple` · `tesla` · `ferrari` · `bugatti` · `airbnb` |

## 📄 许可证

本项目采用 [MIT 许可证](LICENSE) 发布。

模板内容来源于 [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) 和官方 [`getdesign`](https://www.npmjs.com/package/getdesign) npm 包。

## 🙏 致谢

- [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) — 原始品牌设计模板集合
- [getdesign](https://www.npmjs.com/package/getdesign) — 官方 npm 包，模板内容的权威来源
- [OpenAI Codex](https://github.com/openai/codex) — AI 编码助手平台
