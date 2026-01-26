"""
Ontario & Toronto AI Data Center Research — Visualization
==========================================================
Generates a multi-panel figure summarizing publicly reported data on
data-center capacity, investment, and power-grid demand in Ontario / Toronto.

Data sources (all public, Jan 2026):
  - Toronto 312 MW operational, 236 MW under construction, 360 MW planned
    (goranbrelih.com H1 2025 market snapshot)
  - Ontario 6,500 MW of grid-connection applications (Ontario gov / IESO)
  - Microsoft C$19 B total Canada commitment (blogs.microsoft.com Dec 2025)
  - CPP Investments C$225 M Cambridge ON facility (cppinvestments.com)
  - QScale multi-billion-dollar Toronto hyperscale (datacenterdynamics.com)
  - Yondr 27 MW Toronto groundbreaking Jan 2025 (yondrgroup.com)
  - STACK TOR01 campus 4 MW + 24 MW + 24 MW phases (stantec.com)
  - Federal C$2.4 B AI compute budget (Budget 2024)
  - Federal C$15 B loan/equity program for pension-co-invested DC projects
  - Canada market 1,370 MW (2025) → 2,000+ MW by 2030 (Mordor Intelligence)
  - Ontario colocation: 291 MW capacity, 500+ MW pipeline (various)
"""

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from textwrap import fill

# ── colour palette ──────────────────────────────────────────────────────
C_DARK   = "#1a1a2e"
C_ACCENT = "#e94560"
C_BLUE   = "#0f3460"
C_TEAL   = "#16213e"
C_GOLD   = "#f5a623"
C_GREEN  = "#27ae60"
C_GRAY   = "#95a5a6"
C_LIGHT  = "#ecf0f1"

# ── figure ──────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28), facecolor="white")
fig.suptitle(
    "Ontario & Toronto: AI Data Center Boom",
    fontsize=28, fontweight="bold", y=0.98, color=C_DARK,
)
fig.text(
    0.5, 0.965,
    "Public data compiled Jan 2026 — capacity in MW, investments in C$ billions",
    ha="center", fontsize=13, color=C_GRAY,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 1 — Toronto Data-Center Capacity Pipeline  (horizontal stacked bar)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax1 = fig.add_subplot(4, 2, 1)
categories = ["Operational", "Under\nConstruction", "Planned"]
values = [312, 236, 360]
colors = [C_GREEN, C_GOLD, C_ACCENT]
bars = ax1.barh(categories, values, color=colors, height=0.55, edgecolor="white", linewidth=1.2)
for bar, v in zip(bars, values):
    ax1.text(bar.get_width() + 8, bar.get_y() + bar.get_height()/2,
             f"{v} MW", va="center", fontsize=13, fontweight="bold", color=C_DARK)
ax1.set_xlim(0, 450)
ax1.set_xlabel("Megawatts (MW)", fontsize=11)
ax1.set_title("Toronto Data-Center Capacity Pipeline (H1 2025)", fontsize=14, fontweight="bold", pad=12)
ax1.spines[["top", "right"]].set_visible(False)
ax1.tick_params(axis="y", labelsize=12)

# annotation
ax1.text(0.98, 0.05,
         f"Total pipeline: {sum(values)} MW",
         transform=ax1.transAxes, ha="right", fontsize=11, color=C_GRAY, style="italic")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 2 — Major Announced Investments (C$ billions)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax2 = fig.add_subplot(4, 2, 2)
inv_labels = [
    "Microsoft\n(Canada-wide\n2023-2027)",
    "Fed. Loan/Equity\nProgram\n(pension co-invest)",
    "Microsoft\n(near-term\n2026-2027)",
    "Fed. Budget\nAI Compute\n(2024)",
    "QScale\nToronto\n(planned)",
    "CPP Inv.\nCambridge ON",
]
inv_values = [19.0, 15.0, 7.5, 2.4, 2.0, 0.225]
inv_colors = [C_ACCENT, C_BLUE, C_GOLD, C_TEAL, C_GREEN, C_GRAY]

bars2 = ax2.bar(range(len(inv_labels)), inv_values, color=inv_colors,
                width=0.65, edgecolor="white", linewidth=1.2)
ax2.set_xticks(range(len(inv_labels)))
ax2.set_xticklabels(inv_labels, fontsize=9)
for bar, v in zip(bars2, inv_values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             f"C${v}B" if v >= 1 else f"C${int(v*1000)}M",
             ha="center", fontsize=11, fontweight="bold", color=C_DARK)
ax2.set_ylabel("C$ Billions", fontsize=11)
ax2.set_ylim(0, 23)
ax2.set_title("Major Announced Investments in Canadian AI Data Centers", fontsize=14, fontweight="bold", pad=12)
ax2.spines[["top", "right"]].set_visible(False)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 3 — Ontario Grid: Data-Center Applications vs Existing Capacity
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax3 = fig.add_subplot(4, 2, 3)
grid_labels = ["Ontario\nOperational DC\nCapacity", "Toronto\nOperational\nCapacity",
               "Ontario DC\nPipeline", "Grid Connection\nApplications"]
grid_values = [860, 312, 500, 6500]
grid_colors = [C_GREEN, C_TEAL, C_GOLD, C_ACCENT]

bars3 = ax3.bar(range(len(grid_labels)), grid_values, color=grid_colors,
                width=0.6, edgecolor="white", linewidth=1.2)
for bar, v in zip(bars3, grid_values):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100,
             f"{v:,} MW", ha="center", fontsize=12, fontweight="bold", color=C_DARK)
ax3.set_xticks(range(len(grid_labels)))
ax3.set_xticklabels(grid_labels, fontsize=10)
ax3.set_ylabel("Megawatts (MW)", fontsize=11)
ax3.set_ylim(0, 8000)
ax3.set_title("Ontario Grid: DC Demand vs Existing Capacity", fontsize=14, fontweight="bold", pad=12)
ax3.spines[["top", "right"]].set_visible(False)

# Add reference line for Ontario peak demand
ax3.axhline(y=22000, color=C_GRAY, linestyle="--", alpha=0.0)  # invisible — just context
ax3.text(0.98, 0.92,
         "6,500 MW applications ≈ 30% of\nOntario's 2024 peak demand",
         transform=ax3.transAxes, ha="right", fontsize=10,
         color=C_ACCENT, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="#ffeef0", edgecolor=C_ACCENT, alpha=0.9))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 4 — Canada-Wide DC Market Growth Projection
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax4 = fig.add_subplot(4, 2, 4)
years = [2025, 2026, 2027, 2028, 2029, 2030]
# Mordor Intelligence: 3,130 MW (2025) → 3,970 MW (2030), CAGR 4.89%
canada_mw = [3130, 3283, 3443, 3611, 3788, 3970]
ax4.fill_between(years, canada_mw, alpha=0.25, color=C_BLUE)
ax4.plot(years, canada_mw, marker="o", color=C_BLUE, linewidth=2.5, markersize=8)
for yr, mw in zip(years, canada_mw):
    ax4.annotate(f"{mw:,}", (yr, mw), textcoords="offset points",
                 xytext=(0, 12), ha="center", fontsize=10, fontweight="bold", color=C_DARK)
ax4.set_xlabel("Year", fontsize=11)
ax4.set_ylabel("IT Load Capacity (MW)", fontsize=11)
ax4.set_title("Canada Data-Center IT Load Capacity Forecast", fontsize=14, fontweight="bold", pad=12)
ax4.set_ylim(2800, 4400)
ax4.spines[["top", "right"]].set_visible(False)
ax4.text(0.02, 0.92, "CAGR 4.89%", transform=ax4.transAxes,
         fontsize=11, color=C_BLUE, fontweight="bold",
         bbox=dict(boxstyle="round,pad=0.3", facecolor="#e8f4fd", edgecolor=C_BLUE))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 5 — Key Ontario/Toronto Projects Table
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax5 = fig.add_subplot(4, 1, 3)
ax5.axis("off")
ax5.set_title("Key Ontario / Toronto Data-Center Projects", fontsize=16, fontweight="bold", pad=18)

table_data = [
    ["Microsoft Azure", "Toronto (Canada Central)", "Multi-GW (planned)", "C$7.5B (2026-27)", "H2 2026+", "Hyperscale AI & cloud"],
    ["QScale", "Greater Toronto Area", "Multi-hundred MW", "~C$2B+", "Planning", "AI hyperscale compute"],
    ["Yondr Group", "Toronto", "27 MW", "Undisclosed", "Mid-2026 RFS", "Carrier-neutral colo"],
    ["STACK Infra.", "Downtown Toronto", "4 + 24 + 24 MW", "Undisclosed", "Phase 1 operational", "Colo campus (TOR01)"],
    ["CPP / Deutsche Bank", "Cambridge, ON", "54 MW", "C$225M", "Under construction", "GPU AI cloud (pre-leased)"],
    ["Cologix", "151 Front St W + Markham", "TOR4: 15 MW", "Undisclosed", "TOR4 complete", "Carrier hotel expansion"],
    ["Related Cos.", "Ontario (site TBD)", "TBD", "Undisclosed", "Early planning", "First NA data center"],
    ["Cohere (Bell AI Fabric)", "Ontario", "500 MW (full build)", "C$240M (fed.)", "Planning", "Sovereign AI compute"],
]
col_labels = ["Operator / Project", "Location", "Capacity", "Investment", "Timeline", "Notes"]

table = ax5.table(
    cellText=table_data,
    colLabels=col_labels,
    loc="center",
    cellLoc="center",
    colWidths=[0.15, 0.17, 0.13, 0.12, 0.15, 0.20],
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.0, 1.8)

# style header row
for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor(C_DARK)
    cell.set_text_props(color="white", fontweight="bold")

# alternating row colours
for i in range(1, len(table_data) + 1):
    for j in range(len(col_labels)):
        cell = table[i, j]
        cell.set_facecolor("#f8f9fa" if i % 2 == 0 else "white")
        cell.set_edgecolor("#dee2e6")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 6 — Ontario's Nuclear Advantage + Power Mix context (pie)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax6 = fig.add_subplot(4, 2, 7)
# Ontario 2024 generation mix (IESO data, approximate)
mix_labels = ["Nuclear\n(58%)", "Hydro\n(24%)", "Gas\n(6%)", "Wind\n(8%)", "Solar\n(3%)", "Bioenergy\n(1%)"]
mix_sizes = [58, 24, 6, 8, 3, 1]
mix_colors = ["#6c5ce7", "#0984e3", "#636e72", "#00b894", "#fdcb6e", "#e17055"]
explode = (0.05, 0, 0, 0, 0, 0)

wedges, texts, autotexts = ax6.pie(
    mix_sizes, labels=mix_labels, colors=mix_colors,
    autopct="%1.0f%%", startangle=140, explode=explode,
    textprops={"fontsize": 10},
)
for at in autotexts:
    at.set_fontweight("bold")
    at.set_fontsize(9)
ax6.set_title("Ontario Electricity Generation Mix\n(Low-Carbon Grid — Key DC Advantage)", fontsize=13, fontweight="bold", pad=10)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Panel 7 — Toronto vs Other Canadian DC Markets
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ax7 = fig.add_subplot(4, 2, 8)
cities = ["Toronto", "Montreal", "Calgary", "Vancouver"]
facility_counts = [86, 57, 20, 18]  # approximate from datacentermap / various
bar_colors = [C_ACCENT, C_BLUE, C_GOLD, C_GREEN]

bars7 = ax7.bar(cities, facility_counts, color=bar_colors, width=0.55, edgecolor="white", linewidth=1.2)
for bar, v in zip(bars7, facility_counts):
    ax7.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
             str(v), ha="center", fontsize=13, fontweight="bold", color=C_DARK)
ax7.set_ylabel("Number of Facilities", fontsize=11)
ax7.set_title("Canadian Data-Center Facilities by City", fontsize=14, fontweight="bold", pad=12)
ax7.spines[["top", "right"]].set_visible(False)
ax7.set_ylim(0, 105)
ax7.tick_params(axis="x", labelsize=12)

# ── footer ──────────────────────────────────────────────────────────────
fig.text(
    0.5, 0.01,
    "Sources: Microsoft (Dec 2025), IESO, Ontario Gov, CPP Investments, Mordor Intelligence, "
    "goranbrelih.com, DataCenterDynamics, BetaKit, Globe & Mail, Torys LLP, various. "
    "All figures are publicly reported estimates; pipeline figures may include speculative projects.",
    ha="center", fontsize=9, color=C_GRAY, style="italic",
    wrap=True,
)

plt.tight_layout(rect=[0, 0.025, 1, 0.955])
plt.savefig("/home/user/datacenters/ontario_ai_datacenter_overview.png", dpi=180, bbox_inches="tight")
print("Saved: ontario_ai_datacenter_overview.png")
