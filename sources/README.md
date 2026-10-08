# 来源记录

[返回首页](../README.md) · [文献收录](../docs/methodology.md)

本目录保存引用的原始地址、元数据、版本关系与访问记录，供来源追溯和链接维护使用。

## 记录分组

- `main_research.json`、`main_external_links.json`：基础文献、项目页面与外部资源。
- `basics_*.json`、`agent_*.json`：基础、记忆、多模态和训练等专题来源。
- `evaluation_classics.json`、`safety_classics.json`：评测与安全的经典文献。
- `hot_words.json`：概念发布页、接口说明及相关论文。
- `flagship_models.json`：旗舰模型的技术报告、模型卡、发布博客与系统卡。
- `survey_*.json`、`chapter_expansion_*.json`：综述及专题检索结果。
- `after_snapshot.json`、`arxiv_agent_query_*.xml`：跨专题补充文献与查询响应。
- `public_project_review.json`、`readme_references_*.json`：综述项目页、研究路线图与资源页面。
- `title_aliases.json`、`title_versions.json`、`versioned_papers.json`：题名渲染差异与版本对应；参见[版本说明](../docs/version_notes.md)。

## 常用字段

| 字段 | 用途 |
| --- | --- |
| `url` | 原始来源地址 |
| `retrieval_url` | 实际获取内容的地址，适用于原文转换或转发服务 |
| `checked_at` | 访问时间 |
| `title`、`online_title` | 文献题名或页面题名 |
| `status` | 本次访问及检查结果 |
| `scope`、`notes` | 检查范围与必要说明 |
| `sha256` | 所获取内容的校验值 |

不同来源保留各自适用的字段。元数据获取、节选阅读与访问失败分别记录；经第三方阅读服务取得的页面注明实际获取方式。

## 更新来源

在项目根目录运行：

```bash
python3 scripts/check_sources.py --output sources/example_refresh.json \
  https://arxiv.org/abs/2210.03629
```

网络配置使用进程环境变量。更新时保留已有版本关系，并将新增记录与相关正文一同提交；代理地址和认证信息不写入记录。
