# 维护与发布流程

[返回 README](../README.md) · [贡献指南](../CONTRIBUTING.md) · [回归指南](evaluation.md) · [安装排错](install-troubleshooting.md)

本文约定如何把经过验证的仓库状态发布成可追溯版本。本轮仅补充流程，未创建版本标签或 GitHub Release；实际已发布版本以仓库的 [Releases 页面](https://github.com/sakura-hly/ali-style/releases)为准。

## 1. 明确本次改变了什么

发布说明先回答用户会看到什么变化。技能规则、示例、安装方式、评估工具分别写清，避免把“新增案例”写成“全部案例已通过”。在 Pull Request 中保留检查结果，以及涉及行为变化时的原始输入和输出。

用户文档放在 `docs/`；安装器实际分发的是 `skills/ali-style/`。修改 README 或评估工具，通常不会改变已安装技能的措辞行为。

## 2. 验证候选提交

在候选提交对应的干净检出目录中运行：

```bash
git rev-parse HEAD
git status --short
python scripts/validate_repo.py
python -m unittest discover -s tests -v
```

记录完整提交 SHA。`git status --short` 应没有未提交改动，结构检查和测试应通过；同时查看 Pull Request 的 GitHub Actions 结果。验证后若有代码或规则修改，重新检查受影响的部分。

按实际变化选择行为案例：

| 变化 | 需要补充的证据 |
| --- | --- |
| 调整进度、数字、贡献或承诺的写法 | 相关案例的原始输出与逐项人工核对 |
| 修改触发条件 | 明确风格请求，以及未强制选择技能的反向触发案例 |
| 改动安装目录或引用 | 空项目安装、文件完整性和客户端发现情况 |
| 只修正用户文档 | 链接和命令核对；不宣称重新评估了全部模型 |

评估工具检查的字数、字面值等硬约束，与人工核对事实、语气和触发行为分开记录。具体方法见[回归指南](evaluation.md)。

## 3. 在空项目试装

先将候选提交保存到 GitHub，再在新的空项目目录中运行固定提交安装。完整可执行示例和已验证的基线 SHA 见[固定到已知提交](install-troubleshooting.md#固定到已知提交)。将示例中的 SHA 替换为本次候选提交，保留其余路径：

```text
https://github.com/sakura-hly/ali-style/tree/完整提交SHA/skills/ali-style
```

试装时先不加 `--global`，避免覆盖日常使用的用户范围安装。安装完成后：

1. 用 `skills@1.7.4 list --agent codex` 的对应 `npx` 命令确认项目中存在 `ali-style`。
2. 将安装后的目录与候选提交中的 `skills/ali-style/` 比较，确认文件集合、内容和相对引用完整。
3. 若需要发布“某客户端已验证”的结论，在那个客户端打开该项目，使用新对话执行相关提示词，并记录客户端与模型版本。

一次 Codex 安装器检查，只能作为对应安装路径的证据，不能外推为 Claude Code、Cursor 或 ChatGPT 云端已完成验证。Claude Code 与 Cursor 使用各自的 `--agent` 参数分别验证。

## 4. 确定版本并准备 Release 草稿

未来采用 `v主版本.次版本.修订号` 标签。首次版本可以使用 `v0.1.0`，这里是命名示例，不表示该版本已经存在。参考 [SemVer](https://semver.org/lang/zh-CN/)：兼容修正增加修订号，兼容功能增加次版本，不兼容变化增加主版本。`0.x` 阶段仍属于初始开发，发布说明必须明确行为变化和迁移方式。

对本仓库，需要明确的兼容性边界包括技能名称与目录、调用方式，以及评估数据和命令接口。风格改进可能影响文案，仍应说明改变了什么；不承诺相同输入在不同模型中逐字输出相同文本。

发布时按 [GitHub 的 Release 流程](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)操作：将版本标签指向已验证的提交，选择这个标签创建草稿，核对提交和说明，再发布。发布后需要修正时使用新版本，不移动已经用于安装和评估的旧标签。

可从下面的结构起草说明，并将所有待填写项换成实际记录：

```markdown
## 本次变化
- 用户可以……

## 安装与更新
- 默认安装跟随 main；复现本次版本请使用完整提交 SHA。
- 提交：待填写完整 SHA
- 安装命令：待填写并实际验证

## 已完成验证
- 仓库结构与脚本测试：待填写结果
- 实际安装：待填写系统、客户端参数、文件核对结果
- 行为案例：待填写案例 ID、模型与结果

## 已知限制或迁移事项
- 待填写；尚未执行的客户端或行为测试应明确列出。
```

更新 [CHANGELOG.md](../CHANGELOG.md) 时使用相同的版本、范围和验证结论。默认 README 安装命令继续跟随 `main`；需要固定版本的用户使用发布说明中的完整提交入口。安装器版本变化时，重新核对 Node.js 要求、参数与试装结果。

## 5. 区分源码归档与技能安装

GitHub Release 自动提供的 `Source code` 归档包含标签时点的仓库源码，不是已经安装到某个客户端的技能。解压后应使用其中的 `skills/ali-style/`，保留它的全部资源目录；下载归档不会把技能写入客户端配置。归档含义见 [GitHub 源码下载说明](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives)。

发布说明只列实际存在的入口。未发布的插件、未创建的独立技能压缩包或尚未测试的客户端，不应写成现成能力。
