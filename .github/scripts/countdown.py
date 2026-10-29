#!/usr/bin/env python3
"""Moves the myOS countdown on this profile forward by one block each day.

Usage: python3 .github/scripts/countdown.py [--today YYYY-MM-DD] [--dir assets/profile]

Redraws assets/profile/countdown-{hell,dunkel}.svg for the given day. Standard library only: the
font subset embedded in yesterday's file already holds every glyph the countdown can show (digits and
fixed words), so it is carried over byte for byte. The drawing matches countdown() in the Wellux design
kit (kit/profile_art.py), which renders the same file for the same day.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import re
from pathlib import Path

RELEASE = dt.date(2027, 1, 1)  # 17:00 CET, launch with livestream
COUNT_FROM = dt.date(2026, 10, 28)  # the day the countdown started
THEMES = {
    "hell": {"bg": "#FFFFFF", "ink": "#16191D", "ink2": "#4B535D", "mute": "#8A9099", "line": "#DDE3E8",
             "acc": "#1B8DBE", "acc2": "#21A8E0", "tint": "#EEF8FD"},
    "dunkel": {"bg": "#0D1117", "ink": "#E9EEF3", "ink2": "#A7B0BA", "mute": "#7D8590", "line": "#262D36",
               "acc": "#2EA6DA", "acc2": "#21A8E0", "tint": "#0F2433"},
}
E = lambda s: html.escape(str(s), quote=True)  # noqa: E731


def head(w: int, h: int, title: str, desc: str, fonts: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-labelledby="t d"><title id="t">{E(title)}</title><desc id="d">{E(desc)}</desc>'
            f"<style>{fonts}"
            "@keyframes drop{0%{opacity:0;transform:translateY(-18px)}65%{opacity:1;transform:translateY(2px)}"
            "100%{opacity:1;transform:none}}"
            "@keyframes rise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}"
            "@keyframes draw{to{stroke-dashoffset:0}}"
            "@keyframes flow{to{stroke-dashoffset:-48}}"
            ".dp{animation:drop .55s cubic-bezier(.2,.9,.25,1) both}.ri{animation:rise .7s ease-out both}"
            ".dw{animation:draw 1.4s cubic-bezier(.6,0,.2,1) both}.fl{animation:flow 1.6s linear infinite}"
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}.dw{stroke-dashoffset:0}"
            ".rm-hide{display:none}}"
            "</style>")


def d(s: float) -> str:
    return f"animation-delay:{s:.2f}s"


def countdown(t: dict, today: dt.date, fonts: str) -> str:
    w, h = 620, 320
    days = max((RELEASE - today).days, 0)
    total = (RELEASE - COUNT_FROM).days
    built = total - days
    digits = f"{days:02d}"
    p = [head(w, h, "myOS countdown", f"{days} days until myOS goes open source on 1 January 2027, 5 pm CET.", fonts),
         f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="14" fill="{t["tint"]}" stroke="{t["acc"]}" stroke-width="1.5"/>',
         f'<text class="f-PlexM" x="32" y="44" font-size="13" letter-spacing="3" fill="{t["acc"]}">myOS · OPEN SOURCE IN</text>']
    for i, dg in enumerate(digits):
        x = 32 + i * 92
        target = int(dg)
        p.append(f'<rect x="{x}" y="64" width="80" height="112" rx="10" fill="{t["bg"]}" stroke="{t["line"]}"/>')
        p.append(f'<clipPath id="od{i}"><rect x="{x}" y="64" width="80" height="112" rx="10"/></clipPath>')
        strip = "".join(f'<text class="f-PlexB" x="{x+40}" y="{150 + n*112}" text-anchor="middle" font-size="84" '
                        f'fill="{t["ink"]}">{n % 10}</text>' for n in range(0, 10 + target + 1))
        spins = 10 + target
        p.append(f'<g clip-path="url(#od{i})"><g transform="translate(0 {-spins*112})">'
                 f'<animateTransform attributeName="transform" type="translate" from="0 0" to="0 {-spins*112}" '
                 f'begin="{.3+i*.25:.2f}s" dur="{1.6+i*.3:.1f}s" fill="freeze" calcMode="spline" keyTimes="0;1" '
                 f'keySplines=".15 .6 .2 1"/>{strip}</g></g>')
        p.append(f'<path d="M{x} 120 H{x+80}" stroke="{t["line"]}" stroke-width="1.5"/>')
    p.append(f'<text class="f-PlexS ri" style="{d(1.8)}" x="230" y="112" font-size="30" fill="{t["ink"]}">days</text>')
    p.append(f'<text class="f-PlexR ri" style="{d(1.9)}" x="230" y="146" font-size="17" fill="{t["ink2"]}">'
             f'release 01.01.2027 · 17:00</text>')
    p.append(f'<text class="f-PlexR ri" style="{d(2)}" x="230" y="170" font-size="17" fill="{t["ink2"]}">'
             f'friends test from 29.11.</text>')
    for i in range(total):
        col, row = i % 22, i // 22
        solid = i < built
        last = i == built - 1
        p.append(f'<rect class="dp" style="{d(.5+i*.025)}" x="{32+col*25}" y="{212+row*24}" width="17" height="17" '
                 f'rx="4" ' + (f'fill="{t["acc"]}"' if solid else f'fill="none" stroke="{t["acc"]}" stroke-opacity=".45" stroke-width="1.5"')
                 + "/>")
        if last:
            p.append(f'<rect class="rm-hide" x="{32+col*25}" y="{212+row*24}" width="17" height="17" rx="4" '
                     f'fill="{t["acc2"]}"><animate attributeName="opacity" values="1;.2;1" dur="1.6s" '
                     f'repeatCount="indefinite"/></rect>')
    p.append(f'<text class="f-PlexM ri" style="{d(2.2)}" x="32" y="300" font-size="13" fill="{t["mute"]}">'
             f'{built} of {total} blocks built · one per day</text>')
    p.append("</svg>")
    return "".join(p)


def embedded_fonts(svg: str) -> str:
    """The @font-face rules at the start of the style block of an existing countdown file."""
    m = re.search(r"<style>(.*?)@keyframes drop", svg, re.S)
    if not m or "@font-face" not in m.group(1):
        raise SystemExit("countdown: no embedded fonts found, render the file once with the Wellux design kit")
    return m.group(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Redraws the myOS countdown for one day.")
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--dir", type=Path, default=Path("assets/profile"))
    a = ap.parse_args()
    for name, theme in THEMES.items():
        path = a.dir / f"countdown-{name}.svg"
        old = path.read_text(encoding="utf-8")
        new = countdown(theme, a.today, embedded_fonts(old))
        if new != old:
            path.write_text(new, encoding="utf-8")
            print(f"{path}: {max((RELEASE - a.today).days, 0)} days left")


if __name__ == "__main__":
    main()
