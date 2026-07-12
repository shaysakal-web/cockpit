"""
Analytics chart helpers — SWD-style publication charts.

Trimmed fork inspired by ai-analyst-lab/ai-analyst (MIT). Use from study scripts or
phase 10 chart-maker-run.

    from lib.chart_helpers import (
        swd_style, highlight_bar, highlight_line, action_title,
        format_date_axis, annotate_point, save_chart, check_label_collisions,
        CHART_FIGSIZE, COLORS,
    )
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

COLORS = {
    "action": "#D97706",
    "accent": "#DC2626",
    "negative": "#DC2626",
    "gray900": "#1F2937",
    "gray600": "#6B7280",
    "gray400": "#9CA3AF",
    "gray200": "#E5E7EB",
    "bg": "#F7F6F2",
}

_STYLE_FILE = Path(__file__).with_name("analytics_chart_style.mplstyle")
CHART_FIGSIZE = (10, 6)


def swd_style() -> dict:
    """Apply SWD matplotlib style and return the color palette."""
    if _STYLE_FILE.exists():
        plt.style.use(str(_STYLE_FILE))
    else:
        plt.rcParams.update(
            {
                "figure.figsize": (8, 5),
                "figure.dpi": 150,
                "figure.facecolor": COLORS["bg"],
                "axes.facecolor": COLORS["bg"],
                "axes.spines.top": False,
                "axes.spines.right": False,
                "axes.grid": False,
                "font.family": "sans-serif",
                "font.size": 10,
                "axes.titlesize": 14,
                "axes.titleweight": "bold",
            }
        )
    return dict(COLORS)


def highlight_bar(
    ax,
    categories,
    values,
    highlight=None,
    highlight_color=None,
    base_color=None,
    horizontal=True,
    sort=True,
    fmt=None,
    label_offset=0.02,
):
    """Bar chart with one category highlighted; others gray."""
    highlight_color = highlight_color or COLORS["action"]
    base_color = base_color or COLORS["gray200"]

    cats = list(categories)
    vals = list(values)

    if sort:
        paired = sorted(zip(vals, cats), reverse=False)
        vals, cats = zip(*paired)
        vals, cats = list(vals), list(cats)

    if isinstance(highlight, str):
        highlight = [highlight]
    highlight_set = set(highlight) if highlight else set()
    bar_colors = [highlight_color if c in highlight_set else base_color for c in cats]

    if horizontal:
        bars = ax.barh(cats, vals, color=bar_colors)
        ax.set_xlim(0, max(vals) * 1.15 if vals else 1)
        ax.xaxis.set_visible(False)
        ax.spines["bottom"].set_visible(False)
        max_val = max(vals) if vals else 1
        for bar, v in zip(bars, vals):
            label = fmt.format(v) if fmt else f"{v:,.0f}"
            ax.text(
                v + max_val * label_offset,
                bar.get_y() + bar.get_height() / 2,
                label,
                va="center",
                fontsize=9,
                color=COLORS["gray900"],
            )
    else:
        bars = ax.bar(cats, vals, color=bar_colors)
        ax.set_ylim(0, max(vals) * 1.15 if vals else 1)
        ax.yaxis.set_visible(False)
        ax.spines["left"].set_visible(False)
        max_val = max(vals) if vals else 1
        for bar, v in zip(bars, vals):
            label = fmt.format(v) if fmt else f"{v:,.0f}"
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + max_val * label_offset,
                label,
                ha="center",
                fontsize=9,
                color=COLORS["gray900"],
            )
    ax.grid(False)


def highlight_line(
    ax,
    x,
    y_dict,
    highlight=None,
    highlight_color=None,
    base_color=None,
    linewidth_highlight=2.5,
    linewidth_base=1.2,
):
    """Multi-series line chart with highlighted series in action color."""
    highlight_color = highlight_color or COLORS["action"]
    base_color = base_color or COLORS["gray200"]

    if isinstance(highlight, str):
        highlight = [highlight]
    highlight_set = set(highlight) if highlight else set()

    for name, y in y_dict.items():
        if name not in highlight_set:
            ax.plot(x, y, color=base_color, linewidth=linewidth_base, zorder=1)
            ax.text(x[-1], y[-1], f" {name}", va="center", fontsize=8, color=COLORS["gray400"])

    for name, y in y_dict.items():
        if name in highlight_set:
            ax.plot(x, y, color=highlight_color, linewidth=linewidth_highlight, zorder=2)
            ax.text(
                x[-1],
                y[-1],
                f" {name}",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=highlight_color,
            )

    ax.yaxis.grid(True, color=COLORS["gray200"], linewidth=0.5)
    ax.set_axisbelow(True)


def action_title(ax, title, subtitle=None):
    """Action headline (takeaway) with optional context subtitle."""
    if subtitle:
        ax.text(
            0,
            1.12,
            title,
            transform=ax.transAxes,
            fontsize=17,
            fontweight="bold",
            color=COLORS["gray900"],
            va="bottom",
            ha="left",
        )
        ax.text(
            0,
            1.06,
            subtitle,
            transform=ax.transAxes,
            fontsize=12,
            color=COLORS["gray600"],
            va="bottom",
            ha="left",
        )
        ax.set_title("")
    else:
        ax.set_title(title, fontsize=17, fontweight="bold", color=COLORS["gray900"], loc="left", pad=16)


def format_date_axis(ax, fmt="%b", axis="x"):
    """Format date axis with readable month labels (Jan, Feb, …)."""
    import pandas as pd

    target = ax.xaxis if axis == "x" else ax.yaxis

    if isinstance(target.get_major_formatter(), mdates.DateFormatter):
        target.set_major_formatter(mdates.DateFormatter(fmt))
        return

    try:
        target.set_major_formatter(mdates.DateFormatter(fmt))
        ax.figure.canvas.draw()
        labels = [t.get_text() for t in target.get_ticklabels() if t.get_text().strip()]
        if labels:
            return
    except Exception:
        pass

    try:
        tick_labels = [t.get_text() for t in target.get_ticklabels()]
        if tick_labels and any(tick_labels):
            parsed = pd.to_datetime(tick_labels, errors="coerce")
            new_labels = [
                d.strftime(fmt) if pd.notna(d) else lbl for d, lbl in zip(parsed, tick_labels)
            ]
            if axis == "x":
                ax.set_xticklabels(new_labels)
            else:
                ax.set_yticklabels(new_labels)
    except Exception:
        pass


def annotate_point(ax, x, y, text, arrow_color=None, offset=(20, 20)):
    """Annotation with arrow to a data point."""
    arrow_color = arrow_color or COLORS["gray600"]
    ax.annotate(
        text,
        xy=(x, y),
        xytext=offset,
        textcoords="offset points",
        fontsize=9,
        color=arrow_color,
        arrowprops=dict(arrowstyle="->", color=arrow_color, lw=1.0),
    )


def save_chart(fig, path, dpi=150, close=True):
    """Save PNG (and optionally SVG sibling) with tight layout."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight", facecolor=COLORS["bg"], edgecolor="none")
    if path.suffix.lower() == ".png":
        svg_path = path.with_suffix(".svg")
        fig.savefig(svg_path, bbox_inches="tight", facecolor=COLORS["bg"], edgecolor="none")
    if close:
        plt.close(fig)


def check_label_collisions(fig, ax, fix=False, pad_px=5, include_title=True):
    """
    Detect overlapping text. When fix=True, apply offset → font-reduce → drop cascade.
    Returns list of collision dicts (empty if none).
    """
    from matplotlib.transforms import Bbox

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    axes_list = ax if isinstance(ax, (list, np.ndarray)) else [ax]
    collisions = []
    _IMPORTANCE = {"title": 4, "suptitle": 5, "annotation": 3, "data_label": 2, "tick_label": 1}

    def _text_kind(t, cur_ax):
        if t is cur_ax.title:
            return "title"
        if getattr(fig, "_suptitle", None) is t:
            return "suptitle"
        if t in cur_ax.get_xticklabels() + cur_ax.get_yticklabels():
            return "tick_label"
        return "annotation"

    def _get_bbox(t):
        try:
            bb = t.get_window_extent(renderer)
            return Bbox.from_extents(bb.x0 - pad_px, bb.y0 - pad_px, bb.x1 + pad_px, bb.y1 + pad_px)
        except Exception:
            return None

    for cur_ax in axes_list:
        texts = []
        kinds = []

        if include_title:
            if cur_ax.title and cur_ax.title.get_visible() and cur_ax.title.get_text().strip():
                texts.append(cur_ax.title)
                kinds.append("title")
            st = getattr(fig, "_suptitle", None)
            if st is not None and st.get_visible() and st.get_text().strip():
                texts.append(st)
                kinds.append("suptitle")

        for t in cur_ax.texts:
            if t.get_visible() and t.get_text().strip() and t not in texts:
                texts.append(t)
                kinds.append(_text_kind(t, cur_ax))

        for t in cur_ax.get_xticklabels() + cur_ax.get_yticklabels():
            if t.get_visible() and t.get_text().strip():
                texts.append(t)
                kinds.append("tick_label")

        bboxes = [_get_bbox(t) for t in texts]

        for i in range(len(texts)):
            if bboxes[i] is None:
                continue
            for j in range(i + 1, len(texts)):
                if bboxes[j] is None:
                    continue
                if not bboxes[i].overlaps(bboxes[j]):
                    continue

                entry = {
                    "text_a": texts[i].get_text()[:40].replace("\n", " "),
                    "text_b": texts[j].get_text()[:40].replace("\n", " "),
                    "resolved": False,
                    "strategy": None,
                }

                if not fix:
                    collisions.append(entry)
                    continue

                overlap_h = min(bboxes[i].y1, bboxes[j].y1) - max(bboxes[i].y0, bboxes[j].y0)
                if overlap_h > 0:
                    inv = cur_ax.transData.inverted()
                    _, dy = inv.transform((0, overlap_h + pad_px * 2)) - inv.transform((0, 0))
                    pos = texts[j].get_position()
                    texts[j].set_position((pos[0], pos[1] + dy))
                    fig.canvas.draw()
                    bboxes[j] = _get_bbox(texts[j])
                    if bboxes[j] is not None and not bboxes[i].overlaps(bboxes[j]):
                        entry["resolved"] = True
                        entry["strategy"] = "offset"
                        collisions.append(entry)
                        continue

                imp_i = _IMPORTANCE.get(kinds[i], 2)
                imp_j = _IMPORTANCE.get(kinds[j], 2)
                target = j if imp_j <= imp_i else i
                orig_size = texts[target].get_fontsize()
                if orig_size > 7:
                    texts[target].set_fontsize(max(orig_size - 2, 7))
                    fig.canvas.draw()
                    bboxes[target] = _get_bbox(texts[target])
                    if (
                        bboxes[i] is not None
                        and bboxes[j] is not None
                        and not bboxes[i].overlaps(bboxes[j])
                    ):
                        entry["resolved"] = True
                        entry["strategy"] = "font_reduce"
                        collisions.append(entry)
                        continue
                    texts[target].set_fontsize(orig_size)
                    fig.canvas.draw()
                    bboxes[target] = _get_bbox(texts[target])

                drop_target = j if imp_j <= imp_i else i
                texts[drop_target].set_visible(False)
                fig.canvas.draw()
                bboxes[drop_target] = None
                entry["resolved"] = True
                entry["strategy"] = "drop"
                collisions.append(entry)

    return collisions
