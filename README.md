# 亚马逊卖家大学 · 课程转写稿

**把视频课程变成可以阅读、检索和核对的全文资料。**

[浏览 270 门课程](课程目录.md) · [下载完整资料](https://github.com/haloshin/amazon-seller-university-transcripts/releases/latest) · [English](README.en.md)

这里收录了本次归档的 Amazon Seller University 视频课程转写稿：**270 份英文、185 份中文，共 455 份正文**。每份都附字幕、修订记录和校注。

适合学习亚马逊运营、查找课程原话，或把指定课程交给 AI 辅助阅读。可以直接在 GitHub 看，也可以下载后离线检索，无需安装软件。

> 非官方整理项目。保留原课程的顺序、案例和历史表述；原课有口误或版本差异时，在校注中解释。当前仍有 [2 处辨识疑点](docs/KNOWN_ISSUES.md)。

## 从这里开始

### 直接读课程

打开[全部课程目录](课程目录.md)，按原标题查找，选择英文或中文版本。每篇旁边都有 TXT、VTT、修订记录和校注。

想先看看成品，可以从这两门开始：

| 课程 | 中文 | English |
| --- | --- | --- |
| 亚马逊物流入门 · Intro to Fulfillment by Amazon (FBA) | [阅读全文](courses/472d8e74-3402-4871-88d2-0ebaeb3263eb/zh_CN/transcript.md) | [Read](courses/472d8e74-3402-4871-88d2-0ebaeb3263eb/en_US/transcript.md) |
| 选择广告定向策略 · Choose a targeting strategy for your campaign | [阅读全文](courses/09a25aab-2175-41ad-b349-443e73a9d646/zh_CN/transcript.md) | [Read](courses/09a25aab-2175-41ad-b349-443e73a9d646/en_US/transcript.md) |

### 下载后使用

从 [Releases](https://github.com/haloshin/amazon-seller-university-transcripts/releases/latest) 下载完整 ZIP。也可以克隆仓库：

```bash
git clone https://github.com/haloshin/amazon-seller-university-transcripts.git
```

用编辑器搜索课程关键词、术语或具体表述，就能找到对应全文。`catalog.json` 提供机器可读的课程索引。

### 让 AI 陪读一门课

把选定课程的 `transcript.md` 和 `校注.md` 一起交给 AI，例如：

```text
请只依据这份课程转写稿和校注，解释课程的主要概念。
每个结论标出原文依据，区分课程原话和你的推断。
不要补成现行政策；遇到校注中的疑点，请明确保留。
```

## 资料里有什么

| 文件 | 用途 |
| --- | --- |
| `transcript.md` | 在 GitHub 或 Markdown 编辑器中阅读全文 |
| `transcript.txt` | 搜索、复制或导入个人阅读工具 |
| `captions.vtt` | 与原视频配合使用的句段级字幕 |
| `corrections.md` | 查看这一轮具体改了什么、为什么改 |
| `校注.md` | 查看原课口误、版本差异和未确定片段 |
| `course.json` | 课程 ID、语言、来源指纹及校准状态 |

范围以 **2026-07-27 归档素材**为准，校准版本日期为 **2026-10-07**。270 门视频课程中，有 185 门提供正常中文音轨稿；另外 85 门保留英文原文。中文稿来自中文音轨，不是英文稿的机器翻译。

有 3 份原素材的语言或内容与课程记录不符，已单独登记，未混入正常正文。见[源素材异常](源素材异常.md)。本仓库提供文字与字幕，观看视频请使用 [Amazon 官方学习入口](https://sell.amazon.com/learn/seller-university)。

## 校准到什么程度

针对 458 份归档视频完成了第二轮识别、3,723 组差异判断和 AI 全文通读，累计落实 1,222 项修订；其中 455 份正常稿件进入本仓库。

核对时使用既有知识库、696 条术语记录和中文 ASR 错词规则，并对重点疑点补查音频片段和原画面。原片证据优先，原话与校注分开。

- 29 份稿件附课程专属校注，2 处局部辨识疑点公开列明。
- 字幕文字与 TXT 去空白后逐字一致，时间在原视频时长内。
- 属于 AI 全文校准与重点原片核对，尚未进行人类逐字听审。字幕采用机器句段对齐。

课程反映录制时的说法。实际经营中的费用、政策和操作入口，请核对当前官方页面。

[校准方法](校准说明.md) · [已知疑点](docs/KNOWN_ISSUES.md) · [来源说明](docs/SOURCES.md)

## 发现错字，欢迎指出

请通过 [Issue](https://github.com/haloshin/amazon-seller-university-transcripts/issues/new?template=correction.yml) 提供课程名、语言、时间位置、当前文字、建议更正和依据。有原课程证据的修正优先；原课本身的问题会继续放在校注中。

[贡献说明](CONTRIBUTING.md) · [版本记录](CHANGELOG.md)

## 来源与权利

Amazon Seller University 课程内容及相关标识的权利归 Amazon 或相应权利人所有。本项目由 SHIN 独立整理，非 Amazon 官方发布或背书。

**公开可读不等于重新授予原课程开放许可证。** 本仓库不以 MIT/CC 等许可重新授权课程转写、字幕或原课内容；MIT 仅适用于本项目自行编写的校验脚本。详细范围见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE.md)。

由 [SHIN](https://github.com/haloshin) 整理与维护。
