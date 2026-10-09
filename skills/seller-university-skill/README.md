# 卖家大学 Skill

**带着实际问题找课程，再把课程用于自己的工作。**

Amazon 全量覆盖 Beta：**356 个知识模块 · 13 个能力包**。其中 270 个模块可打开本项目的中文课程阅读页；另 86 个模块提供整理要点与官方课程定位，暂无公开转写页。模块来自视频、PDF 等课程资料，因此数量与阅读库的 270 门视频课程不同。

[下载安装 ZIP](https://github.com/haloshin/seller-university/releases/tag/skill-v1.0.0-beta.1) · [课程目录](references/INDEX.md) · [使用示例](examples/README.md) · [English](README.en.md)

## 可以怎么用

> 使用卖家大学 Skill，帮我排查商品上架报错。先问清必要信息，再给步骤和对应课程。

> 使用卖家大学 Skill，解释 Sessions 和 Page views 的区别，并告诉我原课在哪里。

> 使用卖家大学 Skill，结合我提供的站点、库龄和成本数据，整理库存处理方案；缺少数据先问我。

本版支持课程检索、概念解释、问题排查和按需整理 SOP、决策分析或学习计划。默认简短回答，再给步骤与来源。不会替你连接店铺、修改广告、调整价格或提交申诉。

<br>

## 安装

下载 **`seller-university-skill-1.0.0-beta.1.zip`**，解压得到 `seller-university-skill` 文件夹。需要支持 Skills 的 Agent；运行本地检索脚本需要 Python 3.10 或以上，无第三方 Python 依赖，无作者服务器、账号或 API Key 依赖。联网核对政策使用你自己的 Agent 已有能力。

在解压得到的文件夹内打开终端：

```bash
# 先预览目标位置，不写入文件
python3 scripts/install.py --agent codex
# 确认后安装到当前用户的 Codex Skills 目录
python3 scripts/install.py --agent codex --apply
```

Claude Code 将 `codex` 换成 `claude`。自定义宿主目录使用 `--target <Skills父目录>`；同样默认预览，添加 `--apply` 才复制。也可手动将整个文件夹放进宿主支持的 Skills 目录。

安装后开启新会话，发送：

```text
请使用 seller-university-skill。先说明覆盖范围，然后帮我找到“商品推广预算”的课程，只引用实际读到的资料。
```

**安装器只复制这个 Skill，不改模型、账号、环境变量或其他配置。** 遇到同名目录会拒绝覆盖；目标路径有符号链接也会拒绝。升级前先手动备份旧文件夹；回滚时移走新版、恢复旧文件夹并重启会话。

Codex / Claude 目录安装、重复安装保护和临时目录检索均有自动验证；Agent 对话模拟见 [验证说明](VALIDATION.md)。WorkBuddy、Windows 与各宿主 UI 的完整实机流程尚未验证，不标为已兼容验收。

<br>

## 包里有什么

| 内容 | 用途 |
| --- | --- |
| `SKILL.md` | Agent 的使用流程与回答边界 |
| `references/modules/` | 356 个模块的整理要点、来源锚点与阅读链接 |
| `references/packs/` | 13 个主题能力包与所需背景信息 |
| `references/catalog.json` | 中英文检索索引 |
| `scripts/find_modules.py` | 本地只读检索 |
| `scripts/install.py` | 预览或复制安装 |
| `examples/`、`evals/` | 用法示例与 Skill 行为测试用例，非课程题库 |
| `LICENSE`、`NOTICE.md` | 署名、来源与使用范围 |

**不含视频、PDF 文件、知识卡图集和课程题库。** 当前仓库首页中的知识卡、题库图片仍只是预告。v0.9.2 阅读 ZIP 不包含本 Skill，请下载上方独立安装包。

## 来源与时效

课程快照为 **2026-07-27**，不是 Amazon 最新完整目录。课程要点保留录制时语境；费用、资格、预算、政策阈值和后台页面步骤使用前必须核对当前官方信息。脚本不会自动更新课程或联网替你验证政策。

每条要点提供原视频时间戳或 PDF 页码；270 个模块有公开中文阅读页。其余模块不伪造阅读页。官方链接的记录状态分别标明，可能需要登录；未逐课完成播放验收。

## 署名与使用

SHIN 整理维护，非 Amazon 官方项目。代码按 MIT 提供；SHIN 享有权利的原创编辑内容沿用本项目有限使用许可，第三方课程内容不被重新授权。详见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE.md)。这里的“公开”不代表整包内容均采用 MIT 或获得 Amazon 授权。
