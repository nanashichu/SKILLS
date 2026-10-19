# -*- coding: utf-8 -*-
"""构建 实证结果汇总 docx —— 通用模板（引擎照搬自 知识产权法庭项目 2026-09-04 定稿版，勿改引擎区）。

历史模板已停用：下列用法和硬编码路径/版式仅保留作源码追溯，不能复制或执行。
当前使用 scripts/导出完整结果Word_模板.py，按本轮参考稿导出到测试/分析类别/YYYYMMDD_主题。

旧用法（已废止）：
  1. 复制本模板到 <项目>\初稿\构建脚本\，改名 构建_<初稿文件名>.py（如 构建_实证结果汇总_20260907.py）
  2. 只改下方【配置区】：TITLE/SUBTITLE/MAIN/DOCX/STRUCT
  3. 跑 python 构建_xxx.py → 生成 docx（Word COM 全量重建，几分钟属正常）

排版规范（empirical-research skill · references/report-generation.md）：
  - 三线表：顶线/表头线/底线三条线均为1.5pt，无竖线无隔行线
  - 中文全部仿宋，数字英文全部 Times New Roman；标题靠加粗+字号区分层级
  - 表内一律不加粗（含表头/星号/数字），表内字号10pt（五号）；表外中文正文小四（12pt）
  - 所有表格根据窗口自适应宽度；表格首列左对齐，其余列居中；每张表/图/章单独一页
方式：Word COM（InsertFile插rtf + AddPicture插图），插入后统一后处理。
"""
raise SystemExit("历史COM模板已停用：禁止默认写入初稿。请使用导出完整结果Word_模板.py，结果文档放测试任务目录，先归档已有输出。")

import os
import re
import win32com.client

# =======================【配置区】只改这里 =======================
MAIN = r"F:\项目\【填：项目根目录】"
OUT_DIR = os.path.join(MAIN, "初稿")            # docx 输出目录
DF = os.path.join(MAIN, "output")               # rtf/png 所在目录
DOCX = os.path.join(OUT_DIR, "【填：文档名】.docx")

TITLE = "【填：主标题，如 XX与XX：实证结果汇总】"
SUBTITLE = "【填：副标题，如 （口径说明 · 日期）】"

# (级别, 标题, 文件or None)
# 级别: 0=一级标题(章), 1=二级标题(节), 2=表题/图题(挂文件), "p"=说明段落
# 表题必须以「表N」「图N」开头（正则 ^[表图]\d）才会被居中加粗+分页
# 表题括注来源 do 文件，可追溯复现
STRUCT = [
    ("p", "口径说明：【填：主口径、样本窗、回归设定一句话】"),
    ("p", "生成日期：【填：YYYY-MM-DD】。表内数字均由 output\\ 对应rtf原样插入，未做手工改动。"),

    (0, "一、描述性统计", None),
    (2, "表1-1 描述性统计（02_表_描述性统计.do）", "描述性统计_xxx.rtf"),
    (0, "二、基准回归", None),
    (2, "表2-1 基准回归三列（03_表_基准回归.do）", "基准回归_xxx.rtf"),
    # (2, "图2-1 平行趋势（03_表_平行趋势.do）", "平行趋势_xxx.png"),
]
# =======================【引擎区】勿改 =======================

# Word 常量（数字，避免依赖 MakePy）
WD_ALIGN_LEFT, WD_ALIGN_CENTER = 0, 1
WD_PAGE_BREAK = 7
WD_AUTOFIT_WINDOW = 2
B_TOP, B_LEFT, B_BOTTOM, B_RIGHT, B_H, B_V = -1, -2, -3, -4, -5, -6
LS_NONE, LS_SINGLE = 0, 1
LW_150 = 12  # wdLineWidth150pt：1.5pt，三条线统一用这个

RE_CHAPTER = re.compile(r"^[一二三四五六七八九十]+、|^附：")
RE_SECTION = re.compile(r"^\d+\.\d+")
RE_CAPTION = re.compile(r"^[表图]\d")  # 兼容"图1"（无横线）与"表5-11"


def preflight():
    """STRUCT 引用的文件必须全部存在，缺一个中止（防 docx 里混入[缺失文件]占位）"""
    missing = [it[2] for it in STRUCT if len(it) > 2 and it[2] and not os.path.exists(os.path.join(DF, it[2]))]
    if missing:
        print("缺失文件，已中止（先跑 do 生成或核对文件名）：")
        for m in missing:
            print("  -", m)
        raise SystemExit(1)


def assemble(word, doc, sel):
    """封面 + 逐项插入。全部仿宋+Times New Roman，标题靠加粗和字号区分。"""
    sel.ParagraphFormat.Alignment = WD_ALIGN_CENTER
    sel.Font.Name = "Times New Roman"
    sel.Font.NameFarEast = "仿宋"
    sel.Font.Size = 18
    sel.Font.Bold = True
    sel.TypeText(TITLE)
    sel.TypeParagraph()
    sel.Font.Size = 12
    sel.Font.Bold = False
    sel.TypeText(SUBTITLE)
    sel.TypeParagraph()
    sel.ParagraphFormat.Alignment = WD_ALIGN_LEFT
    sel.TypeParagraph()

    n_table = n_fig = 0
    for item in STRUCT:
        kind, text = item[0], item[1]
        fname = item[2] if len(item) > 2 else None
        if kind in (0, 1):
            sel.Font.Name = "Times New Roman"
            sel.Font.NameFarEast = "仿宋"
            sel.Font.Size = 15 if kind == 0 else 13
            sel.Font.Bold = True
            sel.TypeText(text)
            sel.Font.Bold = False
            sel.TypeParagraph()
        elif kind == "p":
            sel.Font.Name = "Times New Roman"
            sel.Font.NameFarEast = "仿宋"
            sel.Font.Size = 12  # 表外中文小四
            sel.Font.Bold = True
            sel.TypeText(text)
            sel.Font.Bold = False
            sel.TypeParagraph()
        elif kind == 2:
            sel.Font.Name = "Times New Roman"
            sel.Font.NameFarEast = "仿宋"
            sel.Font.Size = 12  # 表题中文小四
            sel.Font.Bold = True
            sel.ParagraphFormat.Alignment = WD_ALIGN_CENTER
            sel.TypeText(text)
            sel.TypeParagraph()
            sel.Font.Bold = False
            sel.ParagraphFormat.Alignment = WD_ALIGN_LEFT
            path = os.path.join(DF, fname)
            if not os.path.exists(path):
                sel.TypeText(f"[缺失文件: {fname}]")
                sel.TypeParagraph()
                continue
            if fname.lower().endswith(".png"):
                sel.ParagraphFormat.Alignment = WD_ALIGN_CENTER
                sel.InlineShapes.AddPicture(path)
                sel.TypeParagraph()
                sel.ParagraphFormat.Alignment = WD_ALIGN_LEFT
                n_fig += 1
            else:
                sel.InsertFile(path, "", False)
                sel.TypeParagraph()
                n_table += 1
    return n_table, n_fig


def postprocess(doc):
    """统一字体 → 三线表(全1.5pt) → 窗口自适应 → 对齐 → 分页"""
    # 1. 全文统一：西文 Times New Roman + 中文仿宋（覆盖esttab rtf自带格式）
    doc.Content.Font.Name = "Times New Roman"
    doc.Content.Font.NameFarEast = "仿宋"
    doc.Content.Font.Bold = False  # rtf插入内容可能带粗体，统一清掉

    # 2. 表格：窗口自适应 + 三线化（三条线均1.5pt） + 首列左对齐其余居中
    for tb in doc.Tables:
        try:
            tb.AutoFitBehavior(WD_AUTOFIT_WINDOW)  # 根据窗口调整表格
        except Exception:
            pass
        try:
            tb.Borders(B_LEFT).LineStyle = LS_NONE
            tb.Borders(B_RIGHT).LineStyle = LS_NONE
            tb.Borders(B_H).LineStyle = LS_NONE
            tb.Borders(B_V).LineStyle = LS_NONE
            tb.Borders(B_TOP).LineStyle = LS_SINGLE
            tb.Borders(B_TOP).LineWidth = LW_150
            tb.Borders(B_BOTTOM).LineStyle = LS_SINGLE
            tb.Borders(B_BOTTOM).LineWidth = LW_150
            # 表头行（esttab结构Row1=title/Row2=表头）下线，同为1.5pt
            for r in (2, 1):
                try:
                    tb.Rows(r).Borders(B_BOTTOM).LineStyle = LS_SINGLE
                    tb.Rows(r).Borders(B_BOTTOM).LineWidth = LW_150
                    break
                except Exception:
                    continue
        except Exception:
            pass
        try:
            tb.Range.Font.Size = 10       # 表内字号10pt（五号）
            tb.Range.Font.Bold = False    # 表内一律不加粗（含表头/星号/数字）
        except Exception:
            pass
        try:
            tb.Range.ParagraphFormat.Alignment = WD_ALIGN_CENTER
            nrows = tb.Rows.Count
            for ri in range(2, nrows + 1):  # Row1多为title行保持居中
                try:
                    tb.Cell(ri, 1).Range.ParagraphFormat.Alignment = WD_ALIGN_LEFT
                except Exception:
                    pass
        except Exception:
            pass

    # 3. 章/节/表题加粗放大（字体已在步骤1统一为仿宋+TNR，不再用黑体）
    #    必须跳过表内段落：doc.Paragraphs 含表格单元格段落，且表内系数"0.0072"
    #    会匹配 RE_SECTION(^\d+\.\d+) 被误设为小节标题格式（Information(12)=wdWithInTable）
    paras = list(doc.Paragraphs)
    for p in paras:
        try:
            if p.Range.Information(12):  # wdWithInTable
                continue
        except Exception:
            pass
        t = p.Range.Text.strip()
        if not t:
            continue
        try:
            if RE_CHAPTER.match(t):
                f = p.Range.Font
                f.Size = 15; f.Bold = True
            elif RE_SECTION.match(t):
                f = p.Range.Font
                f.Size = 13; f.Bold = True
            elif RE_CAPTION.match(t):
                f = p.Range.Font
                f.Size = 12; f.Bold = True
        except Exception:
            pass

    # 4. 每张表/图/章另起一页（倒序插入分页符避免扰乱索引）
    marks = []
    for p in doc.Paragraphs:
        t = p.Range.Text.strip()
        if t and (RE_CAPTION.match(t) or RE_CHAPTER.match(t)):
            marks.append(p)
    for p in reversed(marks):
        try:
            rg = p.Range.Duplicate
            rg.Collapse(1)  # 折叠到段首
            rg.InsertBreak(WD_PAGE_BREAK)
        except Exception:
            pass


def main():
    preflight()
    os.makedirs(OUT_DIR, exist_ok=True)
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    doc = word.Documents.Add()
    sel = word.Selection
    try:
        n_table, n_fig = assemble(word, doc, sel)
        postprocess(doc)
        doc.SaveAs2(DOCX, FileFormat=16)
    finally:
        doc.Close(False)
        word.Quit()
    print(f"完成: {DOCX}")
    print(f"插入表格 {n_table} 张, 图 {n_fig} 张")


if __name__ == "__main__":
    main()
