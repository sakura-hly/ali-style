# 安装排错与版本选择

[返回 README](../README.md) · [场景模板](prompt-cookbook.md) · [发布流程](releasing.md)

先从 [README 的一行安装](../README.md#一行安装)开始。下面按失败发生的位置排查；命令以 Codex 为例，Claude Code 和 Cursor 分别使用 `claude-code`、`cursor`。

## 1. 确认工具能运行

```bash
node --version
npm --version
npx --version
git --version
```

四条命令都应输出版本号。本文固定使用 `skills@1.7.4`，它声明的 Node.js 要求为 `>=22.20.0`；低于该版本时，先升级 Node.js，再打开终端重试。安装器的要求可通过 npm 查询：

```bash
npm view skills@1.7.4 engines --json
```

如果第一组命令已经失败，先处理工具安装或终端路径问题。`npm view` 还需要访问 npm 注册表；它的网络错误不能证明本机 Node.js 版本不满足要求。版本依据见 [skills 1.7.4](https://www.npmjs.com/package/skills/v/1.7.4)。

## 2. 区分 npm 下载和 GitHub 下载

| 检查 | 命令 | 成功说明 |
| --- | --- | --- |
| npm 注册表连通性 | `npm ping` | 当前配置的注册表可访问；不代表 GitHub 可访问 |
| GitHub 仓库连通性 | `git ls-remote https://github.com/sakura-hly/ali-style.git HEAD` | 输出提交哈希与 `HEAD`；不代表客户端已安装技能 |
| 安装器发现技能 | 下方的 `--list` 命令 | 能找到 `ali-style`；此步骤不安装技能 |

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --list
```

如果 `npm ping` 失败，检查正在使用的网络和 npm 注册表配置；如果 GitHub 命令失败，检查终端访问 GitHub 的网络路径。本仓库公开可读，正常下载不需要提供个人访问令牌。保留具体报错，比反复重装技能更容易定位问题。

命令含义见 [npm ping 文档](https://docs.npmjs.com/cli/v11/commands/npm-ping/)和 [Skills CLI 的 add / list 参数](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

## 3. 安装成功，但客户端找不到

先核对安装时有没有 `--global`，以及 `--agent` 是否选对。

```bash
# 查看当前用户范围的 Codex 技能
npx --yes skills@1.7.4 list --agent codex --global

# 查看当前项目范围的 Codex 技能：在安装时的项目目录运行
npx --yes skills@1.7.4 list --agent codex
```

检查列表中是否有 `ali-style`，并确认显示的路径属于预期范围。只在项目里安装时，需要在该项目中使用客户端。随后打开新对话，明确请求：

```text
用阿里味，清淡档，改写这句话：这周先确认需求，下周再开始开发。
```

列表能看到文件，只能说明安装器发现了它；是否加载、如何触发，还需在实际客户端确认。不要仅因输出中出现“对齐”就认定自动触发已经通过测试。不同客户端的安装位置见 [Skills CLI 客户端列表](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)。

这些命令安装的是本机客户端技能。ChatGPT 云端 Skills 是另一条安装路径，本机安装成功不会自动同步到云端；参见 [README 中的分发说明](../README.md#能否点击网页按钮直接安装)。

## 4. 符号链接或目录权限错误

如果错误明确指向创建符号链接失败，在原安装命令末尾追加 `--copy`。例如：

```bash
npx --yes skills@1.7.4 add sakura-hly/ali-style --skill ali-style --agent codex --global --yes --copy
```

`--copy` 改用文件复制；它不能解决目标目录本身不可写的问题。若报错是写入权限不足，先核对目录和安装范围，也可以在自己有写入权限的项目中去掉 `--global` 安装。参数说明见 [Skills CLI 安装方式](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#installation-methods)。

## 5. 更新、固定版本与卸载

### 跟随当前版本

重新运行 README 对应客户端的安装命令，会重新获取仓库默认分支的技能。`skills@1.7.4` 固定的是**安装器**，不是 `ali-style` 的内容版本。更新前，如对已安装文件有个人修改，先保留自己的副本。

### 固定到已知提交

需要复现某次评估时，用完整提交 SHA 指向技能目录。下面固定到仓库第一轮扩充完成时的基线提交，**不是“最新版本”别名**：

```bash
npx --yes skills@1.7.4 add https://github.com/sakura-hly/ali-style/tree/44516fa9ce4154a8161ea28b56e1c6285ff8539c/skills/ali-style --skill ali-style --agent codex --yes
```

这条命令安装到当前项目；需要用户范围时追加 `--global`。复现其他版本时，将 URL 中的完整 SHA 换成已确认存在的提交。后续若重新运行不带提交的 README 命令，就会回到默认分支版本。

2026-10-28，维护环境使用已缓存的官方 `skills@1.7.4` CLI，在空项目按上述来源与参数完成了固定提交安装。安装后的 4 个技能文件与该提交内容逐字节一致，项目范围的 `list --agent codex` 可识别技能。该记录验证下载与文件完整性，未重复测试 npm 下载，也不代表所有客户端的加载行为都已验证。

CLI 支持指向仓库子目录的 GitHub URL，见[来源格式](https://github.com/vercel-labs/skills/blob/main/docs/commands.md#source-formats)。`owner/repo@名称` 中的名称用于选择技能，不应把它当作本仓库的版本标签语法。

### 只卸载这个技能

```bash
npx --yes skills@1.7.4 remove ali-style --agent codex --global --yes
```

卸载范围需与安装时一致：项目内安装就在同一项目目录运行，并去掉 `--global`；其他客户端替换 `codex`。完成后运行对应范围的 `list` 确认结果。此处的更新与移除参数依据 [Skills CLI 命令参考](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

## 6. 仍有问题时如何反馈

使用仓库的[问题反馈模板](../.github/ISSUE_TEMPLATE/bug_report.md)，提供：系统与客户端版本、Node.js 版本、完整安装命令、项目或用户范围、出错阶段及具体报错。如果安装成功但输出不符合预期，再附最小输入和实际输出。

反馈前去掉令牌、个人目录中的敏感名称和内部业务材料。无需提供账号密码或完整环境变量清单。
