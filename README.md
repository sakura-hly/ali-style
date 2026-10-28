# 阿里味 · ali-style

[![Repository checks](https://github.com/sakura-hly/ali-style/actions/workflows/validate.yml/badge.svg)](https://github.com/sakura-hly/ali-style/actions/workflows/validate.yml)

把中文素材改写成有辨识度的互联网大厂职场表达，支持 **清淡、标准、爆炒** 三档浓度，也能把黑话翻译成人话。

适用于日常协作、周报、述职、项目汇报、复盘、OKR、会议发言和向上沟通。“阿里味”指网络语境中的风格创作，不代表阿里巴巴的内部规范或官方背书。

**[安装到 Codex](#codex) · [安装到 Claude Code](#claude-code) · [安装到 Cursor](#cursor)**

[12 个场景模板](docs/prompt-cookbook.md) · [效果对比](#效果对比) · [验证与回归](docs/evaluation.md) · [贡献指南](CONTRIBUTING.md) · [更新记录](CHANGELOG.md)

## 一行安装

先安装并配置好对应客户端，以及 [Node.js](https://nodejs.org/) **22.20.0 或更新版本**（包含 npm / npx）和 [Git](https://git-scm.com/)。在终端复制运行对应的一行命令，安装器会下载完整技能目录，包括示例与图标。

### Codex

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --skill ali-style --agent codex --global --yes
```

### Claude Code

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --skill ali-style --agent claude-code --global --yes
```

### Cursor

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --skill ali-style --agent cursor --global --yes
```

以上命令使用 [Vercel Skills CLI](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)，跳过交互选择，并通过 `--global` 安装到当前用户范围，供不同项目使用。安装器版本固定为 `1.7.4`，技能内容来自本仓库当前默认分支。重新运行同一命令可获取当前版本；已有同名技能会被更新。

只希望当前项目使用时，在目标项目目录运行对应命令，并去掉 `--global`。支持的其他客户端及其 `--agent` 参数见[客户端列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)。

安装后，在对应客户端的新对话中试一句：

```text
用阿里味，标准档，改写这句话：这周先把需求说清楚，下周再开始开发。
```

> 这些命令将技能安装到本机的 Codex、Claude Code 或 Cursor；ChatGPT 云端 Skills 需要单独安装，不会通过这些命令同步。

## 按场景直接开始

在[场景提示词手册](docs/prompt-cookbook.md)中，复制完整模板、填入素材，即可开始使用。模板会提示你写清时间、数字、当前进度和待确认事项。

| 你想做什么 | 可以直接复制的模板 |
| --- | --- |
| 给同事发消息、协调依赖 | [日常协作](docs/prompt-cookbook.md#1-日常协作)、[跨团队对齐](docs/prompt-cookbook.md#4-跨团队对齐) |
| 汇报进展、展示贡献 | [技术周报](docs/prompt-cookbook.md#2-技术周报)、[向上汇报](docs/prompt-cookbook.md#3-向上汇报)、[述职材料](docs/prompt-cookbook.md#5-述职材料) |
| 讨论方案、规划目标 | [方案评审](docs/prompt-cookbook.md#6-方案评审)、[OKR 草稿](docs/prompt-cookbook.md#7-okr-草稿) |
| 解释延期、故障或数据结果 | [延期沟通](docs/prompt-cookbook.md#8-延期沟通)、[故障复盘](docs/prompt-cookbook.md#9-故障复盘)、[数据复盘](docs/prompt-cookbook.md#10-数据复盘) |
| 看懂黑话、轻松玩梗 | [黑话翻译](docs/prompt-cookbook.md#11-黑话翻译)、[爆炒玩梗](docs/prompt-cookbook.md#12-爆炒玩梗) |

## 三档浓度

| 档位 | 表达方式 | 适合场景 |
| --- | --- | --- |
| 清淡 | 以直接表达为主，适量使用“对齐、推进、复用” | 日常协作、给同事发消息 |
| 标准（默认） | 围绕目标、抓手、结果组织内容 | 周报、项目汇报、述职 |
| 爆炒 | 增强“底层逻辑、心智、颗粒度、势能、闭环”等用语 | 玩梗、调侃、黑话拉满 |

浓度只改变语气，不改变原始事实、实际进度和个人贡献。

## 使用示例

加载 skill 后，可以直接提出以下请求，并附上需要处理的素材：

```text
用阿里味帮我改写这段周报，标准档：……
```

```text
用阿里味，清淡档，改写这句话：麻烦你今天看一下方案，有问题我们下午聊。
```

```text
用阿里味，爆炒档：这个会开了两小时，还没决定谁来做。
```

```text
把这段大厂黑话翻译成人话：围绕用户心智，以内容为抓手，打通转化链路，形成增长闭环。
```

支持四种模式：保留原意的改写、根据素材起草、黑话翻译、玩梗创作。未指定浓度时使用标准档；普通周报请求不会自动套用本风格。

## 效果对比

**原话**

> 这周先把需求说清楚，下周再开始开发。

**清淡**

> 这周先对齐需求，下周再开始开发。

**标准**

> 本周先拉齐需求口径，把要做什么、做到什么程度讲清楚，下周进入开发阶段。

**爆炒**

> 本周先把需求的底层逻辑打透，在目标和交付颗粒度上拉齐认知，明确要做什么、做到什么程度，下周再把共识转成研发动作。

更多示例见 [表达与场景示例](skills/ali-style/references/style-examples.md)。示例中的项目、数字和计划仅用于演示，不代表使用者的经历。

## 安装管理与常见问题

### 先查看可安装的技能

以下命令只列出仓库中的技能，不执行技能安装：

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --list
```

### 更新与卸载

更新时，重新运行上方对应客户端的安装命令。

从 Codex 卸载此技能：

```bash
npx --yes skills@1.7.4 remove ali-style --agent codex --global --yes
```

Claude Code 或 Cursor 用户将 `codex` 换成 `claude-code` 或 `cursor`。如果此前安装在项目内，请在同一项目目录运行，并去掉 `--global`。

### 安装遇到问题

| 现象 | 处理方式 |
| --- | --- |
| 找不到 `npx`，或提示 Node.js 版本不支持 | 安装或更新到 Node.js 22.20.0 或更新版本，再打开终端运行命令 |
| 找不到 `git`，或仓库下载失败 | 安装 Git，并检查终端能否访问 GitHub |
| 创建符号链接失败 | 在原安装命令末尾追加 `--copy`，使用文件复制方式 |
| 客户端未识别技能 | 检查 `--agent` 是否选对；项目内安装还需在对应项目中打开客户端，再创建新对话 |

### 手动获取

```bash
git clone https://github.com/sakura-hly/ali-style.git
```

完整 skill 位于 `skills/ali-style/`。按所用工具支持的方式导入或加载这个目录，保留其中的 `references/`、`agents/` 和 `assets/`，以保证示例与图标的相对路径有效。

技能本体是一套提示词与参考材料，没有运行时依赖；上方的 Node.js 与 Git 用于安装过程。

### 能否点击网页按钮直接安装？

本仓库提供的是可复制的一行安装命令。GitHub 页面的链接可以引导用户到安装说明，实际写入本机技能目录仍由用户在终端运行安装器完成。

如果需要 ChatGPT 应用内的“点击安装”体验，应走平台支持的插件分发流程；OpenAI 的[技能分发说明](https://learn.chatgpt.com/docs/build-skills#distribute-skills-with-plugins)推荐将可复用技能打包为插件。本仓库目前提供技能源码与本地安装入口，尚未发布 ChatGPT 插件。

## 文件说明

| 文件 | 用途 |
| --- | --- |
| [SKILL.md](skills/ali-style/SKILL.md) | 触发条件、模式、浓度、执行流程和事实边界 |
| [style-examples.md](skills/ali-style/references/style-examples.md) | 改写、技术周报、述职、延期、会议、玩梗与翻译示例 |
| [openai.yaml](skills/ali-style/agents/openai.yaml) | 显示名称、默认提示词、图标引用与调用策略 |
| [icon.svg](skills/ali-style/assets/icon.svg) | skill 图标 |
| [场景提示词手册](docs/prompt-cookbook.md) | 12 个可直接复制的场景模板与后续调节指令 |
| [验证与回归指南](docs/evaluation.md) | 检查方法、评估标准及三个实际演练样例 |
| [回归案例](evals/cases.json) | 12 个行为案例，覆盖事实、格式与误触发 |
| [仓库检查器](scripts/validate_repo.py) | 检查文件、基础元数据、本地引用与案例格式 |

## 验证与贡献

维护者可在仓库根目录运行以下命令，需要 Python 3.10 或更新版本，无需额外 Python 依赖：

```bash
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

[自动检查工作流](.github/workflows/validate.yml)在提交和 Pull Request 时执行结构检查及检查器测试。它不调用模型；事实准确性、风格和触发行为需按[回归指南](docs/evaluation.md)核对实际输出。

欢迎贡献场景、案例和规则修正。请先阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，反馈问题时使用[问题反馈模板](.github/ISSUE_TEMPLATE/bug_report.md)，提出新场景时使用[场景建议模板](.github/ISSUE_TEMPLATE/scenario_request.md)。

## 表达边界

- 保留数字、单位、基线、时间范围和明确限定。
- 区分已完成、进行中、计划中、尚未上线和收益待验证。
- 保留“参与、负责、主导”的贡献边界，不新增业绩或承诺。
- 事故、延期和投诉先讲清实际影响，不用黑话掩盖事实。
- 翻译成人话时不臆测动机，不把意向解释成已完成的结果。
- 文案生成不代表获得发送、发布或代替使用者承诺的授权。
