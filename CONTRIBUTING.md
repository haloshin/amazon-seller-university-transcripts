# 贡献与纠错

欢迎提交有证据的错字、漏句、时间定位和校注修正。请附课程原标题、语言、时间戳、当前文字、建议文字，以及可核对的官方来源。可直接使用[纠错 Issue 模板](https://github.com/haloshin/seller-university/issues/new?template=correction.yml)。

原音与原画面优先；另一语言版本和当前政策只作对照。原课程中的口误、算例矛盾和历史建议应在校注中说明，不要静默改写成当前说法。

修改音轨转写正文时，同步更新 Markdown、TXT、VTT；校注单独保存。不要把猜测写成确定原文。不要提交视频、音频片段、官方 PDF、账号信息、订单数据、密钥、Cookie 或内部工作路径。

中文译文存放在 `amazon/translations/<课程ID>/zh_CN/`，与 `amazon/courses/` 中的原音轨稿分开。纠正译文时请对照英文原稿，修改 `translation.json` 对应段落并同步 `translation.txt`，再生成 Markdown 与 HTML；不新增或伪造中文音轨及 VTT。保留来源、英文源文件指纹和段落对应，源文有疑点时保留说明。

Amazon 课程、译文及目录元数据统一放在 `amazon/`；`amazon/catalog.json` 和译文元数据中的文件路径以 `amazon/` 为基准。HTML 阅读入口与公共脚本保留在仓库根目录。

中文导航名与主题归类保存在 `amazon/catalog.json` 的 `navigationTitleZh`、`navigationTopic` 字段中，属于编辑导航。官方标题保存在 `title` 字段中。修改正文 TXT、导航字段或语言入口后，可重新生成中英文学习导航和 Markdown 课程页；该命令不改动 TXT 或 VTT：

```bash
python3 scripts/build_navigation.py
python3 scripts/build_reader.py
```

生成器会在 Markdown 阅读页和学习导航加入整理署名、原仓库与使用说明链接。请保留这些来源标识；不要把非课程的署名或使用条款混入 TXT 正文或 VTT 字幕。

本地校验仅依赖 Python 3 标准库：

```bash
python3 scripts/verify.py
```

在明确更正内容并同步相关文件后，更新内容指纹与清单，再检查：

```bash
python3 scripts/verify.py --refresh
python3 scripts/verify.py
```

刷新指纹不表示语义校准通过；它只使文件清单与当前已审阅文件一致。校验检查主题覆盖、阅读导航、课程数量、语言、正文/字幕一致性、字幕时间、译文覆盖、译文来源指纹、段落对应、链接与文件指纹，不判断课程事实或听辨准确率。
