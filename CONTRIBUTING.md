# 参与贡献

[返回 README](README.md) · [场景提示词](docs/prompt-cookbook.md) · [验证与回归指南](docs/evaluation.md)

欢迎补充好用的场景、修正失真的表达、改进安装体验。优先提交能复现的问题和可核对的改进，让每条规则都有实际用途。

## 适合贡献什么

- 场景模板：给出用户要解决的问题、输入字段和输出要求。
- 效果案例：提供合成或脱敏的原文、生成结果及具体差异。
- 规则修正：说明什么情况下现有规则会改动事实、进度、贡献或承诺。
- 安装与检查工具：提供客户端、系统版本、完整命令和必要的错误信息。

## 把内容放在哪里

| 内容 | 位置 |
| --- | --- |
| 给用户复制的场景提示词 | [docs/prompt-cookbook.md](docs/prompt-cookbook.md) |
| 原文、成稿与事实核对点 | [docs/before-after.md](docs/before-after.md) |
| 给模型使用的核心流程和边界 | [skills/ali-style/SKILL.md](skills/ali-style/SKILL.md) |
| 模型按需读取的语感示例 | [skills/ali-style/references/style-examples.md](skills/ali-style/references/style-examples.md) |
| 行为回归输入及核对标准 | [evals/cases.json](evals/cases.json) |
| 文件与引用检查 | [scripts/validate_repo.py](scripts/validate_repo.py) |
| 输出记录、机械检查与评估报告 | [scripts/evaluate_responses.py](scripts/evaluate_responses.py) |

用户文档放在技能目录之外。技能目录应保持独立可安装，引用资源都应随目录一起分发。不要仅为增加文件数量而加入重复说明，也不要把用户文档里的占位符当成真实事实写进技能示例。

## 提交改动

1. Fork 仓库并从 `main` 创建分支，先阅读现有规则和示例。
2. 修改内容。每次聚焦一个问题；保持安装命令与目录结构一致。
3. 在仓库根目录运行：

   ```bash
   python scripts/validate_repo.py
   python -m unittest discover -s tests -v
   ```

4. 修改技能行为时，按[验证与回归指南](docs/evaluation.md)执行相关案例，保存实际输出。可使用记录工具选择相关案例并生成报告；修改触发条件时，包含不会触发的对照案例。
5. 提交 Pull Request，说明原问题、修改后的行为与验证结果；适合记录的用户可见变化补入 [CHANGELOG.md](CHANGELOG.md)。

Python 检查器使用标准库，Python 3.10 或更新版本即可。它检查仓库结构；不要把脚本通过当成模型行为一定正确的证据。

准备发布版本时，按[版本发布指南](docs/releasing.md)记录具体提交、验证范围与已知限制。不要仅根据机械检查通过就宣称所有客户端兼容或所有行为案例通过。

## 内容标准

- 数字、单位、状态、时间、因果和个人贡献必须可还原到输入。
- 黑话应对应具体对象或动作；有风格不等于抽象词越多越好。
- 事故、延期、投诉先交代实际影响，不用风格掩盖事实。
- 示例使用合成或脱敏素材；避免上传内部文档、真实账单、客户数据、密钥或个人联系方式。
- 尊重原文的贡献边界，不新增真实公司的官方背书。

## 提问题

安装失败或输出失真时，请使用仓库的“问题反馈”模板；希望增加场景时，使用“场景建议”模板。贴出最小可复现的输入、实际结果和期望保留的事实，会比单独说“不够阿里味”更容易改进。
