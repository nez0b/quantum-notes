#!/usr/bin/env python3
"""Build the quantum-optics track HTML files from a shared head template.

The existing course tutorials in `quantum-information-science-Sp26/` are
single-file HTML artifacts — each ~2,700–5,400 lines, with ~1,000 lines of
embedded CSS at the top. Rather than duplicate the CSS by hand across the
seven new notes, this script reads the `<head>` from `grovers.html` once,
substitutes per-note title and description, then writes each note's body
content into a complete standalone file.

The committed artifacts are still single-file HTML — no runtime build is
needed. This script is invoked manually when adding/refreshing notes.

Usage:
    python3 _build.py            # rebuild all 7 notes
    python3 _build.py 06         # rebuild a single note by index

The notes/ content lives in this file; sections are Python data structures
that the renderer turns into HTML. Adding note 08 means: define another
`NOTE_08` dict at the bottom, append to `ALL_NOTES`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parent
GROVERS_HTML = ROOT.parent / "quantum-information-science-Sp26" / "grovers.html"


# ---------------------------------------------------------------------------
# Head extraction & substitution
# ---------------------------------------------------------------------------

def read_head_template() -> str:
    """Return everything from `<!DOCTYPE` up to and including `</head>`."""
    text = GROVERS_HTML.read_text()
    end = text.index("</head>") + len("</head>")
    return text[:end]


def make_head(template: str, *, title: str, description: str) -> str:
    """Substitute the title/description meta into the shared head."""
    out = re.sub(
        r"<title>.*?</title>",
        f"<title>{title}</title>",
        template,
        count=1,
    )
    out = re.sub(
        r'<meta\s+name="description"\s+content=".*?"\s*/>',
        f'<meta name="description" content="{description}" />',
        out,
        count=1,
        flags=re.DOTALL,
    )
    return out


# ---------------------------------------------------------------------------
# Body rendering helpers
# ---------------------------------------------------------------------------

def page_header(*, eyebrow: str, h1: str, subtitle: str, covers: list[str]) -> str:
    cover_lis = "\n".join(f"              <li>{c}</li>" for c in covers)
    return dedent(f"""\
        <header class="page-header">
          <div class="header-shell">
            <div class="eyebrow">{eyebrow}</div>
            <div class="header-grid">
              <div>
                <h1>{h1}</h1>
                <p class="header-subtitle">{subtitle}</p>
              </div>
              <aside class="header-card">
                <h2>What This Note Covers</h2>
                <ul>
        {cover_lis}
                </ul>
              </aside>
            </div>
          </div>
        </header>""")


def top_nav(items: list[tuple[str, str]]) -> str:
    """items: list of (anchor, label)."""
    links = "\n".join(f'        <a href="#{a}">{label}</a>' for a, label in items)
    return dedent(f"""\
        <nav class="top-nav" aria-label="Section navigation">
          <div class="top-nav-shell">
        {links}
          </div>
        </nav>""")


def section_shell(*, anchor: str, title: str, body_html: str, keypoints: list[str]) -> str:
    kp_lis = "\n".join(f"              <li>{kp}</li>" for kp in keypoints)
    return dedent(f"""\
        <section class="section-shell" id="{anchor}">
          <div class="section-main">
            <h2>{title}</h2>
        {body_html}
          </div>
          <div class="section-side">
            <aside class="keypoints">
              <h3>Key takeaways</h3>
              <ul>
        {kp_lis}
              </ul>
            </aside>
          </div>
        </section>""")


def callout(html: str) -> str:
    return f'<div class="callout">{html}</div>'


def math_details(summary: str, body_html: str) -> str:
    return dedent(f"""\
        <details class="math-details">
          <summary>{summary}</summary>
        {body_html}
        </details>""")


def footer_block(*, sub_index_label: str = "↑ All quantum-optics notes",
                 sub_index_href: str = "index.html",
                 portal_label: str = "↑↑ All tracks",
                 portal_href: str = "../index.html") -> str:
    return dedent(f"""\
        <footer class="page-footer">
          <div class="footer-shell">
            <p>
              <a href="{sub_index_href}">{sub_index_label}</a>
              &nbsp;&middot;&nbsp;
              <a href="{portal_href}">{portal_label}</a>
            </p>
            <p class="footer-meta">
              Part of <a href="https://github.com/nez0b/quantum-notes">quantum-notes</a>.
              Source PDFs in <a href="_lectures/"><code>_lectures/</code></a>.
            </p>
          </div>
        </footer>""")


FOOTER_CSS = dedent("""\
    <style>
      .page-footer {
        margin-top: 4rem;
        border-top: 1px solid var(--page-rule);
        padding: 2rem 0;
      }
      .footer-shell {
        width: min(calc(100% - 2rem), var(--content-width));
        margin: 0 auto;
        font-size: 0.92rem;
        color: var(--page-muted);
      }
      .footer-meta {
        margin-top: 0.4rem;
        font-size: 0.85rem;
      }
      .keypoints h3 {
        margin: 0 0 0.5rem;
        font-size: 0.92rem;
        color: var(--page-muted);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 600;
      }
      .keypoints ul {
        margin: 0;
        padding-left: 1.05rem;
        font-size: 0.93rem;
      }
      .keypoints li {
        margin-bottom: 0.35rem;
      }
      .lede {
        font-size: 1.04rem;
        margin-top: 0;
      }
      table.refs {
        margin-top: 0.6rem;
        border-collapse: collapse;
        font-size: 0.92rem;
      }
      table.refs td {
        padding: 0.18rem 0.7rem 0.18rem 0;
        vertical-align: top;
      }
      table.refs td:first-child {
        white-space: nowrap;
        color: var(--page-muted);
      }
      .pre-req {
        margin: 1rem 0;
        font-size: 0.92rem;
        color: var(--page-muted);
      }
      .back {
        display: inline-block;
        font-size: 0.9rem;
        color: var(--page-muted);
        text-decoration: none;
        margin: 0 0 1.6rem;
      }
      .back:hover { color: var(--page-accent); }
      /* Wider main column. Overrides the grovers.html default (which used
         roughly equal columns); gives prose, figures, and widgets more room. */
      .section-shell {
        grid-template-columns: minmax(0, 2.4fr) minmax(220px, 1fr) !important;
        gap: 1.6rem !important;
      }
      .widget-shell, .figure-band, figure, pre {
        grid-column: 1 / -1;
      }
      @media (max-width: 760px) {
        .section-shell {
          grid-template-columns: 1fr !important;
        }
        .section-side {
          order: 2;
        }
      }
      .sources-list {
        display: grid;
        gap: 0.7rem;
        margin-top: 0.8rem;
      }
      .source-item {
        padding: 0.6rem 0.8rem;
        border-left: 2px solid var(--page-rule);
        background: var(--page-panel);
        border-radius: 0 4px 4px 0;
      }
      .source-tag {
        display: inline-block;
        font-size: 0.74rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--page-muted);
        margin-right: 0.5rem;
        font-weight: 600;
      }
      .source-note {
        margin: 0.2rem 0 0;
        font-size: 0.88rem;
        color: var(--page-muted);
      }
      .widget-shell {
        margin: 1.2rem 0;
        padding: 1rem 1.1rem;
        background: var(--page-panel);
        border: 1px solid var(--page-rule);
        border-radius: 8px;
      }
      .widget-shell h4 {
        margin: 0 0 0.5rem;
        font-size: 0.95rem;
        color: var(--page-muted);
        letter-spacing: 0.04em;
        text-transform: uppercase;
        font-weight: 600;
      }
      .widget-controls {
        display: grid;
        gap: 0.5rem;
        margin: 0.6rem 0;
      }
      .widget-controls label {
        display: grid;
        grid-template-columns: 7rem 1fr 4rem;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
      }
      .widget-controls input[type="range"] {
        width: 100%;
      }
      .widget-controls .val {
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 0.85rem;
        color: var(--page-accent);
        text-align: right;
      }
      .widget-readout {
        margin-top: 0.6rem;
        padding: 0.5rem 0.7rem;
        background: var(--page-bg);
        border-radius: 4px;
        font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        font-size: 0.84rem;
        line-height: 1.5;
      }
      .widget-canvas, .widget-svg {
        display: block;
        width: 100%;
        max-width: 100%;
        height: auto;
        background: var(--page-bg);
        border-radius: 4px;
      }
      .widget-row {
        display: grid;
        grid-template-columns: 1fr;
        gap: 0.6rem;
      }
      @media (min-width: 720px) {
        .widget-row.two-col { grid-template-columns: 1fr 1fr; }
      }
      .widget-buttons {
        display: flex;
        gap: 0.4rem;
        flex-wrap: wrap;
        margin-top: 0.4rem;
      }
      .widget-buttons button {
        padding: 0.35rem 0.7rem;
        font-size: 0.85rem;
        border: 1px solid var(--page-rule);
        background: var(--page-bg);
        color: var(--page-fg);
        border-radius: 4px;
        cursor: pointer;
      }
      .widget-buttons button:hover {
        border-color: var(--page-accent);
        color: var(--page-accent);
      }
    </style>""")


KATEX_INIT_SCRIPT = dedent("""\
    <script>
      (function () {
        function updateMath(root) {
          if (!window.renderMathInElement) return false;
          window.renderMathInElement(root, {
            delimiters: [
              { left: "$$", right: "$$", display: true },
              { left: "\\\\[", right: "\\\\]", display: true },
              { left: "\\\\(", right: "\\\\)", display: false }
            ],
            throwOnError: false
          });
          return true;
        }
        function ensureMathRendered(attempts) {
          attempts = attempts == null ? 24 : attempts;
          if (updateMath(document.body)) return;
          if (attempts <= 0) return;
          setTimeout(function () { ensureMathRendered(attempts - 1); }, 150);
        }
        // Re-render math inside <details> when first opened (some browsers
        // skip rendering hidden subtrees). Idempotent.
        document.addEventListener("toggle", function (e) {
          if (e.target && e.target.tagName === "DETAILS" && e.target.open) {
            updateMath(e.target);
          }
        }, true);
        if (document.readyState === "loading") {
          document.addEventListener("DOMContentLoaded", function () { ensureMathRendered(); });
        } else {
          ensureMathRendered();
        }
      })();
    </script>""")


def assemble(*, head: str, header: str, nav: str, main_html: str, footer_html: str) -> str:
    return f"""{head}\n  {FOOTER_CSS}\n  </head>\n  <body>\n    <a class="skip-link" href="#main-content">Skip to content</a>\n    {header}\n    {nav}\n    <main id="main-content">\n{main_html}\n    </main>\n    {footer_html}\n  </body>\n</html>\n"""


def assemble_proper(*, head: str, header: str, nav: str, main_html: str,
                    footer_html: str, extra_scripts: str = "") -> str:
    """The head already ends with </head>; we need to inject FOOTER_CSS *before*
    that close tag so styles are inside <head>. The simpler approach: drop </head>
    from head, append FOOTER_CSS, append fresh </head>, then body.

    A nav-back link sits at the top of <main>, the KaTeX init script sits
    just before </body>, and any per-note widget scripts are appended after
    KATEX_INIT_SCRIPT (so widgets can call window.renderMathInElement).
    """
    head_open = head.rsplit("</head>", 1)[0]
    back_link = ('      <a class="back" href="index.html">'
                 '&larr; back to quantum-optics notes</a>\n')
    return (
        head_open
        + "\n    " + FOOTER_CSS + "\n"
        + "  </head>\n"
        + "  <body>\n"
        + '    <a class="skip-link" href="#main-content">Skip to content</a>\n\n'
        + "    " + header + "\n\n"
        + "    " + nav + "\n\n"
        + '    <main id="main-content">\n'
        + back_link
        + main_html + "\n"
        + "    </main>\n\n"
        + "    " + footer_html + "\n\n"
        + "    " + KATEX_INIT_SCRIPT + "\n"
        + (extra_scripts + "\n" if extra_scripts else "")
        + "  </body>\n"
        + "</html>\n"
    )


# ---------------------------------------------------------------------------
# Widget helpers
# ---------------------------------------------------------------------------
# Each interactive widget is a <div class="widget-shell"> containing:
#   - a brief title and 1-line description
#   - one or more <input type="range"> sliders (built via slider())
#   - a <canvas> or <svg> visualization
#   - a <div class="widget-readout"> for live numeric output
# A matching <script> block (passed via the note's "scripts" field) wires
# slider events to a render function. Vanilla JS only — no libraries.

def slider(*, var: str, label: str, min_: float, max_: float, step: float,
           value: float, fmt: str = "{:.2f}") -> str:
    """Render a labeled <input type=range>.  `var` becomes the id; the
    `.val` span gets id=`{var}-val` so the JS can update its text."""
    return (
        f'        <label>\n'
        f'          <span>{label}</span>\n'
        f'          <input type="range" id="{var}" min="{min_}" max="{max_}" '
        f'step="{step}" value="{value}" />\n'
        f'          <span class="val" id="{var}-val">{fmt.format(value)}</span>\n'
        f'        </label>'
    )


def widget_shell(*, anchor: str, title: str, blurb: str,
                 controls_html: str, canvas_html: str,
                 readout_html: str = "", buttons_html: str = "") -> str:
    """Compose a widget shell.  Returns the inner HTML of one <div class="widget-shell">."""
    parts = [
        f'<div class="widget-shell" id="{anchor}">',
        f'  <h4>{title}</h4>',
        f'  <p style="margin: 0 0 0.6rem; font-size: 0.92rem;">{blurb}</p>',
        f'  <div class="widget-controls">\n{controls_html}\n  </div>',
    ]
    if buttons_html:
        parts.append(f'  <div class="widget-buttons">{buttons_html}</div>')
    parts.append(f'  {canvas_html}')
    if readout_html:
        parts.append(f'  <div class="widget-readout" id="{anchor}-readout">{readout_html}</div>')
    parts.append('</div>')
    return "\n".join(parts)


def canvas_el(anchor: str, *, w: int = 480, h: int = 320) -> str:
    return (f'<canvas class="widget-canvas" id="{anchor}-canvas" '
            f'width="{w}" height="{h}"></canvas>')


def svg_el(anchor: str, *, w: int = 480, h: int = 280) -> str:
    return (f'<svg class="widget-svg" id="{anchor}-svg" '
            f'viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg"></svg>')


def script_block(js: str) -> str:
    """Wrap a JS body in a <script> block.  The body should be self-contained
    (its own IIFE if it needs closure)."""
    return f'<script>\n{js}\n</script>'


# ---------------------------------------------------------------------------
# Per-note content
# ---------------------------------------------------------------------------
# Each note is a dict. The `sections` list holds tuples of
#   (anchor, title, body_html, [keypoints])
# Body HTML is written as a Python triple-quoted string so we can keep
# inline LaTeX (\(…\), \[…\]) without escape gymnastics.

NOTE_01 = {
    "filename": "01_coherent_states.html",
    "title": "Coherent States and the Quadrature Picture",
    "description": "Field quantization, vacuum fluctuations, displacement, squeezing, and the Wigner picture — the language for everything that follows.",
    "eyebrow": "Quantum Optics · Coherent States",
    "h1": "Coherent States and the Quadrature Picture",
    "subtitle": "Foundational note. The language of single-mode states — coherent, squeezed, thermal — that we will reuse for every photonic device in this track.",
    "covers": [
        r"Single-mode quantization: \(a, a^\dagger, [a, a^\dagger]=1\)",
        r"Coherent states \(\lvert\alpha\rangle\) as displaced vacuum, minimum uncertainty",
        r"Quadratures \(X, P\); phase-space picture; Wigner functions",
        r"Squeezed vacuum and the squeeze operator \(S(r)\)",
        "Density operators in the Fock and coherent bases; thermal vs vacuum",
        "Why coherent states behave like classical fields, and where that breaks",
    ],
    "nav": [
        ("quantization", "Quantization"),
        ("coherent", "Coherent States"),
        ("quadratures", "Quadratures"),
        ("wigner", "Wigner"),
        ("wigner-explorer", "Wigner Lab"),
        ("squeezing", "Squeezing"),
        ("density", "Density Ops"),
        ("photon-stats", "Photon Stats"),
        ("classical-limit", "Classical Limit"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("quantization", "Single-Mode Quantization", r"""
          <p class="lede">
            Pick one optical mode — one frequency, one polarization, one
            spatial profile. Promote its complex amplitude to an operator
            \(a\), with hermitian conjugate \(a^\dagger\). The defining
            commutator
            \[
              [a, a^\dagger] = 1
            \]
            is what makes everything quantum.
          </p>
          <p>
            From this single relation everything in the field-theory
            chapter of an optics textbook follows: the number operator
            \(N = a^\dagger a\) with eigenstates \(\lvert n\rangle\) and
            integer eigenvalues, the ladder action
            \(a \lvert n\rangle = \sqrt{n}\,\lvert n-1\rangle\) and
            \(a^\dagger \lvert n\rangle = \sqrt{n+1}\,\lvert n+1\rangle\),
            and the Hamiltonian
            \[
              H = \hbar\omega\bigl(a^\dagger a + \tfrac{1}{2}\bigr).
            \]
            That \(\tfrac{1}{2}\) is the zero-point energy, and it is the
            first hint that the vacuum \(\lvert 0\rangle\) is not "nothing".
          </p>
          """ + callout(
            "The vacuum is not empty — it has nonzero energy and "
            "nonzero quadrature variance. This is the bedrock fact "
            "behind every shot-noise calculation in this track."
          ),
         ["Mode = (frequency, polarization, spatial profile)",
          r"\([a, a^\dagger] = 1\) is the entire quantum input",
          "Vacuum has zero photons but nonzero energy and quadrature variance"]),
        ("coherent", "Coherent States as Displaced Vacuum", r"""
          <p>
            The coherent state \(\lvert\alpha\rangle\) is the eigenstate of
            the (non-Hermitian) annihilation operator:
            \[
              a\,\lvert\alpha\rangle = \alpha\,\lvert\alpha\rangle,
              \qquad \alpha \in \mathbb{C}.
            \]
            Equivalently, it is the displaced vacuum:
            \[
              \lvert\alpha\rangle = D(\alpha)\,\lvert 0\rangle,\quad
              D(\alpha) = \exp\!\bigl(\alpha a^\dagger - \alpha^* a\bigr).
            \]
          </p>
          <p>
            Coherent states have Poissonian photon-number statistics with
            \(\langle N\rangle = \lvert\alpha\rvert^2\) and
            \(\mathrm{Var}(N) = \lvert\alpha\rvert^2\). They are
            <em>minimum-uncertainty</em> states — saturating
            \(\Delta X\,\Delta P = \tfrac{1}{2}\) — with equal X and P
            variance. They are the closest quantum mechanical states to
            classical sinusoidal oscillations of the field.
          </p>
          """ + math_details("Why D(α) gives a coherent state", r"""
            <p>
              Use the Baker-Campbell-Hausdorff identity for displacement
              operators and the fact that
              \(D(\alpha)^\dagger a D(\alpha) = a + \alpha\). Then
              \[
                a\, D(\alpha)\lvert 0\rangle = D(\alpha)\bigl(a + \alpha\bigr)\lvert 0\rangle
                = \alpha\, D(\alpha)\lvert 0\rangle,
              \]
              since \(a\lvert 0\rangle = 0\). Hence
              \(D(\alpha)\lvert 0\rangle\) is an eigenstate of \(a\) with
              eigenvalue \(\alpha\) — by definition,
              \(\lvert\alpha\rangle\).
            </p>
          """),
         ["Coherent state = eigenstate of \\(a\\), not of \\(N\\)",
          "Displaced vacuum: \\(\\lvert\\alpha\\rangle = D(\\alpha)\\lvert 0\\rangle\\)",
          "Photon-number statistics are Poissonian"]),
        ("quadratures", "Quadratures and Phase Space", r"""
          <p>
            Define the dimensionless quadratures
            \[
              X = \tfrac{1}{\sqrt{2}}\bigl(a + a^\dagger\bigr),
              \qquad
              P = \tfrac{1}{i\sqrt{2}}\bigl(a - a^\dagger\bigr),
            \]
            so that \([X, P] = i\). They are the optical analogue of
            position and momentum for a harmonic oscillator, except they
            both refer to amplitude (in-phase and out-of-phase) of a
            single optical mode.
          </p>
          <p>
            The vacuum has
            \(\langle X\rangle = \langle P\rangle = 0\) and
            \(\langle X^2\rangle = \langle P^2\rangle = \tfrac{1}{2}\) —
            the canonical "1/2 unit of vacuum noise". Coherent states
            have the same variances, with means
            \(\langle X\rangle = \sqrt{2}\,\Re\alpha\),
            \(\langle P\rangle = \sqrt{2}\,\Im\alpha\): a Gaussian blob
            of variance 1/2 displaced to \((\Re\alpha,\Im\alpha)\) in
            phase space.
          </p>
          """,
         ["\\(X\\), \\(P\\) are conjugate quadratures with \\([X,P] = i\\)",
          "Vacuum: \\(\\langle X^2\\rangle = \\langle P^2\\rangle = 1/2\\)",
          "Coherent states are vacuum-shaped Gaussians displaced in phase space"]),
        ("wigner", "The Wigner Function", r"""
          <p>
            Phase-space pictures of quantum states use the Wigner
            quasiprobability distribution
            \[
              W(x, p) = \tfrac{1}{\pi}\int dy\, e^{-2ipy}\,
                \langle x+y\,\lvert\,\rho\,\rvert\,x-y\rangle.
            \]
            For Gaussian states (vacuum, coherent, squeezed, thermal), W
            is a Gaussian and is everywhere non-negative — these states
            behave classically in phase space. For Fock states with
            \(n \ge 1\), W has negative regions: an unambiguous quantum
            signature.
          </p>
          <p>
            The vacuum Wigner function is
            \(W_0(x,p) = \tfrac{1}{\pi}e^{-(x^2+p^2)}\): an isotropic
            Gaussian centered at the origin with covariance matrix
            \(\Sigma = \tfrac{1}{2}I\). All Gaussian states share that
            functional form with a different mean \(\bar r\) and
            covariance \(\Sigma\).
          </p>
          """ + callout(
            "Negative Wigner = nonclassicality. Coherent and squeezed "
            "states are <em>not</em> nonclassical in this technical "
            "sense — their Wigner functions are positive Gaussians. "
            "But squeezing is the first Gaussian state that has no "
            "classical electromagnetic-field analogue."
          ),
         ["Wigner W(x,p) = phase-space density for \\(\\rho\\)",
          "Gaussian states ↔ Gaussian Wigner ↔ classical-like",
          "Negative Wigner ⇒ Fock-like \\(n \\ge 1\\) state"]),
        ("wigner-explorer", "Interactive: The Wigner Function for Gaussian States", r"""
          <p class="lede">
            Slide \(\Re\alpha\), \(\Im\alpha\), squeeze amplitude
            \(r\), squeeze angle \(\theta\), and thermal occupation
            \(\bar n\) to see the Wigner function deform. Coherent =
            displaced unit Gaussian; squeezed = stretched ellipse;
            thermal = isotropic but inflated.
          </p>
          """ + widget_shell(
            anchor="wigner-explorer",
            title="Live Wigner explorer",
            blurb=(
              "All Gaussian-state Wigner functions are 2D Gaussians "
              "with covariance matrix <em>V</em>. The displacement "
              "translates the centre; the squeeze parameters rotate "
              "and stretch the ellipse; thermal occupation inflates "
              "both axes uniformly."
            ),
            controls_html=(
              slider(var="wig-re", label="Re α", min_=-3, max_=3,
                     step=0.05, value=1.2, fmt="{:+.2f}") + "\n" +
              slider(var="wig-im", label="Im α", min_=-3, max_=3,
                     step=0.05, value=0.0, fmt="{:+.2f}") + "\n" +
              slider(var="wig-r", label="squeeze r", min_=0, max_=1.5,
                     step=0.05, value=0.0, fmt="{:.2f}") + "\n" +
              slider(var="wig-theta", label="squeeze θ", min_=0,
                     max_=3.14, step=0.05, value=0.0, fmt="{:.2f}") + "\n" +
              slider(var="wig-nbar", label="thermal n̄", min_=0,
                     max_=3, step=0.05, value=0.0, fmt="{:.2f}")
            ),
            canvas_html=canvas_el("wigner-explorer", w=440, h=440),
            readout_html=(
              '<div>⟨X⟩ = <span id="wig-mean-x">—</span> &nbsp; '
              '⟨P⟩ = <span id="wig-mean-p">—</span></div>'
              '<div>Var X = <span id="wig-var-x">—</span> &nbsp; '
              'Var P = <span id="wig-var-p">—</span></div>'
              '<div>State type: <span id="wig-type">coherent</span></div>'
            ),
          ) + r"""
          """,
         ["Coherent: displaced unit Gaussian",
          "Squeezed: rotated/stretched ellipse",
          "Thermal: isotropic, inflated"]),
        ("squeezing", "Squeezed States", r"""
          <p>
            The single-mode squeeze operator
            \[
              S(r) = \exp\!\bigl[\tfrac{r}{2}\bigl(a^2 - (a^\dagger)^2\bigr)\bigr],
              \qquad r \in \mathbb{R},
            \]
            generates a squeezed vacuum
            \(\lvert 0, r\rangle = S(r)\lvert 0\rangle\) with reduced
            X-variance and inflated P-variance:
            \[
              \langle X^2\rangle_r = \tfrac{1}{2}e^{-2r},
              \qquad
              \langle P^2\rangle_r = \tfrac{1}{2}e^{+2r}.
            \]
            For \(r=1\) (about 8.7 dB of X-quadrature squeezing), \(X\)
            has variance \(0.07\) — sub-shot-noise. The product
            \(\Delta X\,\Delta P = 1/2\) still saturates the uncertainty
            relation: squeezing redistributes noise, not eliminates it.
          </p>
          <p>
            Real squeezed-light sources — sub-threshold optical
            parametric oscillators (Note 03), Kerr media, electro-optic
            squeezers — typically deliver \(r \le 1\) reliably. Above
            that, decoherence and detection-loss eat the squeezing
            faster than the χ⁽²⁾ medium can produce it.
          </p>
          """,
         ["Squeezing redistributes vacuum noise between X and P",
          "X-variance: \\(\\tfrac{1}{2}e^{-2r}\\) (below shot noise)",
          "Detection loss \\(1-\\eta\\) caps usable \\(r\\) on a real bench"]),
        ("density", "Density Operators: Pure vs Mixed", r"""
          <p>
            For a pure state \(\lvert\psi\rangle\) the density operator
            is \(\rho = \lvert\psi\rangle\langle\psi\rvert\). For an
            ensemble (or after partial tracing over an environment),
            \(\rho\) is a positive Hermitian operator with
            \(\mathrm{Tr}\rho = 1\) but generically rank > 1.
          </p>
          <p>
            Two diagonal representations matter for us:
          </p>
          <ul>
            <li><strong>Fock:</strong>
              \(\rho = \sum_n p_n \lvert n\rangle\langle n\rvert\) with
              \(p_n \ge 0,\ \sum_n p_n = 1\). Photon-number diagonal.
              Thermal states have \(p_n = (1-\bar n^{-1})\bar n^{n}/(\bar n+1)^{n+1}\)
              — well, almost; see exercises.</li>
            <li><strong>Glauber-Sudarshan P:</strong>
              \(\rho = \int d^2\alpha\, P(\alpha)
              \lvert\alpha\rangle\langle\alpha\rvert\). For thermal and
              classical mixtures \(P\) is a (possibly broad) probability
              density; for Fock states \(P\) is a singular
              distribution.</li>
          </ul>
          <p>
            The thermal state at mean photon number \(\bar n\) has
            covariance \(\Sigma = \bigl(\bar n + \tfrac{1}{2}\bigr) I\)
            — adds vacuum-plus-thermal noise on both quadratures
            equally. The vacuum is \(\bar n = 0\).
          </p>
          """,
         ["Pure: rank-1 \\(\\rho\\); mixed: higher rank",
          "Thermal state inflates both X and P symmetrically",
          'P-representation singular ⇒ a "nonclassical" state']),
        ("photon-stats", "Photon Number Statistics", r"""
          <p class="lede">
            Coherent, squeezed, and thermal states share Gaussian
            phase-space distributions but have <em>radically different
            photon-counting statistics</em>. The photon-number
            distribution \(P(n) = \langle n\rvert\rho\lvert n\rangle\)
            is the experimental observable from a click detector.
          </p>
          <ul>
            <li><strong>Coherent</strong>:
              \(P(n) = e^{-\bar n}\,\bar n^n / n!\) — Poisson, with
              \(\mathrm{Var}(N) = \bar n\) and Fano factor 1.</li>
            <li><strong>Thermal</strong>:
              \(P(n) = \bar n^n / (\bar n + 1)^{n+1}\) — geometric,
              with \(\mathrm{Var}(N) = \bar n^2 + \bar n\); Fano factor
              \(\bar n + 1\). Super-Poissonian.</li>
            <li><strong>Squeezed vacuum</strong>:
              \(P(n) = 0\) for odd \(n\); for even
              \(n = 2k\), \(P(2k) = (\tanh r)^{2k}\,(2k)! / [2^{2k}(k!)^2 \cosh r]\).
              Pair-only — never an odd photon count.</li>
            <li><strong>Number state</strong>:
              \(P(n) = \delta_{n, n_0}\). Sub-Poissonian:
              \(\mathrm{Var}(N) = 0 \le \bar n\). The most non-classical
              photon-number distribution.</li>
          </ul>
          <p>
            The <strong>Mandel Q parameter</strong>
            \(Q = (\mathrm{Var}(N) - \bar N) / \bar N\) is the canonical
            signature: \(Q = 0\) Poisson, \(Q > 0\) super-Poissonian
            (classical mixture), \(Q < 0\) sub-Poissonian (truly quantum).
          </p>
          """ + widget_shell(
            anchor="photon-distribution",
            title="Interactive: photon-number distributions side-by-side",
            blurb=(
              "Plots <em>P</em>(<em>n</em>) for coherent, thermal, and "
              "squeezed-vacuum states with the same mean photon number "
              "<em>n̄</em>. The Mandel-Q readout flags the regime; the "
              "two states have radically different statistics yet share "
              "the same mean."
            ),
            controls_html=slider(var="pn-nbar", label="mean ⟨n⟩", min_=0.5,
                                 max_=15, step=0.1, value=4.0,
                                 fmt="{:.1f}"),
            canvas_html=svg_el("photon-distribution", w=540, h=300),
            readout_html=(
              '<div>Coherent Q = <span id="pn-q-coh">0.000</span> (Poisson)</div>'
              '<div>Thermal Q = <span id="pn-q-th">—</span></div>'
              '<div>Squeezed-vacuum Q = <span id="pn-q-sq">—</span></div>'
            ),
          ) + r"""
          """ + math_details("Why P(n) for squeezed vacuum has only even terms", r"""
            <p>
              The squeeze operator
              \(S(r) = \exp[\tfrac{r}{2}(a^{\dagger 2} - a^2)]\) is a
              quadratic generator: it raises and lowers photon number
              <em>in pairs</em>. Acting on the vacuum
              \(\lvert 0\rangle\), it generates a superposition of
              even-\(n\) Fock states. Direct calculation of the
              expansion coefficient \(\langle 2k\rvert S(r)\lvert 0\rangle\)
              (e.g.\ via the disentangled normal-ordered form
              \(S(r) = e^{\frac{1}{2}\tanh r\,a^{\dagger 2}}
              (\cosh r)^{-1/2 - a^\dagger a} e^{-\frac{1}{2}\tanh r\,a^2}\))
              yields the formula \(P(2k) \propto (\tanh r)^{2k}\)
              quoted above. <em>The forbidden-odd-\(n\) feature is the
              hallmark of a parametric process: photons are created in
              pairs.</em>
            </p>
          """),
         ["Coherent ↔ Poisson, Q = 0",
          "Thermal ↔ super-Poissonian, Q > 0",
          "Squeezed-vacuum ↔ even-only, can be sub-Poissonian",
          "Number state ↔ Q < 0, fully quantum"]),
        ("classical-limit", "Where Coherent States Are Classical", r"""
          <p>
            For \(\lvert\alpha\rvert \gg 1\), the coherent-state field is
            indistinguishable from a classical sinusoid with amplitude
            \(\lvert\alpha\rvert\) up to vacuum-fluctuation noise. The
            relative noise on the photon number is
            \(\Delta N / \langle N\rangle = 1/\lvert\alpha\rvert\), which
            vanishes for bright fields.
          </p>
          <p>
            This explains why a 100 mW laser beam is well-modeled by a
            Maxwell-equation simulator: with \(\sim 10^{18}\) photons
            per second and shot noise of order \(10^9\), the classical
            field is a 9-decimal approximation. The cases where this
            fails — and where we need quantum optics — are precisely
            (i) <em>weak fields</em> (single photons, threshold OPOs,
            sub-threshold squeezing), and (ii) <em>nonlinear
            interactions where weak fields amplify into bright ones
            with quantum-statistical structure</em>. The Coherent Ising
            Machine (Note 06) lives entirely in the second case.
          </p>
          """ + callout(
            "Classical vs quantum on a photonic bench is not a binary — "
            "it is a continuum parameterized by the photon number per "
            "mode. The interesting physics happens at the bifurcation, "
            "where the field is large enough that mean-field theory "
            "starts to apply <em>and</em> small enough that quantum "
            "fluctuations select among classical attractors."
          ),
         ["Bright coherent state \\(\\lvert\\alpha\\rvert \\gg 1\\) ≈ classical EM wave",
          "Quantum optics matters at low photon number per mode",
          "CIM operates at the bifurcation — quantum noise selects classical attractor"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/coherent_states.pdf">coherent_states.pdf</a> — primary source for §1–§4</td></tr>
            <tr><td>Lecture</td><td><a href="_lectures/density_operators.pdf">density_operators.pdf</a> — §6</td></tr>
            <tr><td>Lecture</td><td><a href="_lectures/L1_wavepackets_and_such.pdf">L1_wavepackets_and_such.pdf</a> — single-mode quantization</td></tr>
            <tr><td>Reference</td><td>Walls &amp; Milburn, <em>Quantum Optics</em> (2nd ed., Springer, 2008), Ch. 2–4</td></tr>
            <tr><td>Reference</td><td>Lvovsky &amp; Raymer, "Continuous-variable optical quantum-state tomography", <em>Rev. Mod. Phys.</em> <strong>87</strong>, 803 (2015) — Wigner reconstruction in practice</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §02 — Linear optics: beam splitters
            and networks. We extend single-mode states to multi-mode by
            mixing modes through passive linear devices.
          </p>
          """,
         ["Lecture PDFs in `_lectures/` are the primary source",
          "Walls &amp; Milburn for graduate-level reference",
          "Continue: Note 02 (linear optics)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: Wigner function explorer (canvas heatmap) ------------
      (function () {
        var canvas = document.getElementById('wigner-explorer-canvas');
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        var W = canvas.width, H = canvas.height;
        var ids = ['re', 'im', 'r', 'theta', 'nbar'];
        var els = {};
        ids.forEach(function (k) {
          els[k] = document.getElementById('wig-' + k);
          els[k + 'V'] = document.getElementById('wig-' + k + '-val');
        });
        var meanX = document.getElementById('wig-mean-x');
        var meanP = document.getElementById('wig-mean-p');
        var varX = document.getElementById('wig-var-x');
        var varP = document.getElementById('wig-var-p');
        var typeSpan = document.getElementById('wig-type');
        function draw() {
          var re = parseFloat(els.re.value);
          var im = parseFloat(els.im.value);
          var r = parseFloat(els.r.value);
          var theta = parseFloat(els.theta.value);
          var nbar = parseFloat(els.nbar.value);
          els.reV.textContent = re.toFixed(2);
          els.imV.textContent = im.toFixed(2);
          els.rV.textContent = r.toFixed(2);
          els.thetaV.textContent = theta.toFixed(2);
          els.nbarV.textContent = nbar.toFixed(2);
          // Convention: phase-space coords (x,p) such that vacuum has Var X = Var P = 1/2
          // Coherent at α: ⟨X⟩ = √2 Re α, ⟨P⟩ = √2 Im α
          // Squeeze with (r, θ) rotates and scales. Combined with thermal n̄:
          // Var_squeezed = (n̄ + 1/2) e^{-2r}, anti-Var = (n̄ + 1/2) e^{+2r}
          var mx = Math.SQRT2 * re;
          var mp = Math.SQRT2 * im;
          var Vsq = (nbar + 0.5) * Math.exp(-2*r);
          var Vasq = (nbar + 0.5) * Math.exp(2*r);
          // Cov in (X,P) basis after rotation by θ
          var c = Math.cos(theta), s = Math.sin(theta);
          // rotation matrix R(θ); cov in lab = R diag(Vsq,Vasq) R^T
          var Cxx = c*c*Vsq + s*s*Vasq;
          var Cpp = s*s*Vsq + c*c*Vasq;
          var Cxp = c*s*(Vsq - Vasq);
          // Render heatmap of W(x,p)
          var XMIN = -5, XMAX = 5, PMIN = -5, PMAX = 5;
          var img = ctx.getImageData(0, 0, W, H);
          var data = img.data;
          // det and inverse of cov
          var det = Cxx*Cpp - Cxp*Cxp;
          var iC11 = Cpp/det, iC22 = Cxx/det, iC12 = -Cxp/det;
          var norm = 1/(2*Math.PI*Math.sqrt(det));
          // colormap: viridis-ish
          function color(t) {
            // t in [0,1]
            t = Math.max(0, Math.min(1, t));
            var rr = Math.floor(68 + 200*t);
            var gg = Math.floor(20 + 220*t*t);
            var bb = Math.floor(140 - 140*t + 80*(1-t));
            return [rr, gg, Math.max(0,bb)];
          }
          var maxW = norm; // for unit-trace Gaussian peak is at center
          for (var py = 0; py < H; py++) {
            var p_phys = PMAX - (py / H) * (PMAX - PMIN);
            for (var px = 0; px < W; px++) {
              var x_phys = XMIN + (px / W) * (XMAX - XMIN);
              var dx = x_phys - mx, dp = p_phys - mp;
              var q = iC11*dx*dx + 2*iC12*dx*dp + iC22*dp*dp;
              var Wval = norm * Math.exp(-0.5*q);
              var t = Wval / maxW;
              var col = color(t);
              var idx = (py*W + px)*4;
              data[idx] = col[0]; data[idx+1] = col[1]; data[idx+2] = col[2]; data[idx+3] = 255;
            }
          }
          ctx.putImageData(img, 0, 0);
          // axes overlay
          ctx.strokeStyle = '#fff'; ctx.globalAlpha = 0.3;
          ctx.beginPath();
          ctx.moveTo(0, H/2); ctx.lineTo(W, H/2);
          ctx.moveTo(W/2, 0); ctx.lineTo(W/2, H);
          ctx.stroke();
          ctx.globalAlpha = 1;
          ctx.fillStyle = '#fff';
          ctx.font = '11px monospace';
          ctx.fillText('X →', W-22, H/2-5);
          ctx.fillText('P →', W/2+5, 12);
          // readouts
          meanX.textContent = mx.toFixed(2);
          meanP.textContent = mp.toFixed(2);
          varX.textContent = Cxx.toFixed(3);
          varP.textContent = Cpp.toFixed(3);
          var label;
          if (nbar > 0.05 && r < 0.05) label = 'thermal' + (re !== 0 || im !== 0 ? ' + displaced' : '');
          else if (r > 0.05) label = 'squeezed' + (re !== 0 || im !== 0 ? ' + displaced' : ' vacuum');
          else label = 'coherent' + (re === 0 && im === 0 ? ' (= vacuum)' : '');
          typeSpan.textContent = label;
        }
        ids.forEach(function (k) { els[k].addEventListener('input', draw); });
        draw();
      })();

      // -- Widget: photon-number distribution ---------------------------
      (function () {
        var svg = document.getElementById('photon-distribution-svg');
        if (!svg) return;
        var nbarS = document.getElementById('pn-nbar');
        var nbarV = document.getElementById('pn-nbar-val');
        var qCoh = document.getElementById('pn-q-coh');
        var qTh = document.getElementById('pn-q-th');
        var qSq = document.getElementById('pn-q-sq');
        function poisson(n, lam) {
          var lp = -lam;
          for (var k = 1; k <= n; k++) lp += Math.log(lam) - Math.log(k);
          return Math.exp(lp);
        }
        function thermal(n, nbar) {
          return Math.pow(nbar, n) / Math.pow(nbar+1, n+1);
        }
        function squeezedVac(n, r) {
          if (n % 2 === 1) return 0;
          var k = n / 2;
          // P(2k) = (tanh r)^(2k) (2k)! / (4^k (k!)^2 cosh r)
          var lt = Math.log(Math.tanh(r));
          var lp = (2*k) * lt - Math.log(Math.cosh(r));
          // log of (2k)! / (4^k k!^2) — central binomial coefficient / 4^k
          var lcoeff = 0;
          for (var j = 1; j <= 2*k; j++) lcoeff += Math.log(j);
          for (var j = 1; j <= k; j++) lcoeff -= 2*Math.log(j);
          lcoeff -= 2*k * Math.log(2);
          return Math.exp(lp + lcoeff);
        }
        function draw() {
          var nbar = parseFloat(nbarS.value);
          nbarV.textContent = nbar.toFixed(1);
          // For squeezed-vacuum to have same ⟨n⟩=nbar, need sinh²r = nbar ⇒ r = asinh(√nbar)
          var r_for_nbar = Math.asinh(Math.sqrt(nbar));
          var W = 540, H = 300, pad = 50;
          var inner_w = W - 2*pad, inner_h = H - 2*pad - 24;
          var Nmax = Math.min(40, Math.ceil(nbar*4) + 6);
          var bw = inner_w / Nmax;
          var html = '';
          // axes
          html += '<line x1="' + pad + '" y1="' + (pad+inner_h) + '" x2="' + (W-pad) + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          html += '<line x1="' + pad + '" y1="' + pad + '" x2="' + pad + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          // find max P for scaling
          var maxP = 0;
          var coh_arr = [], th_arr = [], sq_arr = [];
          for (var n = 0; n < Nmax; n++) {
            var pc = poisson(n, nbar), pt = thermal(n, nbar), ps = squeezedVac(n, r_for_nbar);
            coh_arr.push(pc); th_arr.push(pt); sq_arr.push(ps);
            if (pc > maxP) maxP = pc;
            if (pt > maxP) maxP = pt;
            if (ps > maxP) maxP = ps;
          }
          for (var n = 0; n < Nmax; n++) {
            var x0 = pad + n * bw;
            var pc = coh_arr[n], pt = th_arr[n], ps = sq_arr[n];
            var hc = (pc / maxP) * inner_h, ht = (pt / maxP) * inner_h, hs = (ps / maxP) * inner_h;
            var bw_each = bw * 0.27;
            html += '<rect x="' + (x0 + 1) + '" y="' + (pad + inner_h - hc) + '" width="' + bw_each + '" height="' + hc + '" fill="#7a9fd1" opacity="0.85"/>';
            html += '<rect x="' + (x0 + 1 + bw_each + 1) + '" y="' + (pad + inner_h - ht) + '" width="' + bw_each + '" height="' + ht + '" fill="#e8b96a" opacity="0.85"/>';
            html += '<rect x="' + (x0 + 1 + 2*bw_each + 2) + '" y="' + (pad + inner_h - hs) + '" width="' + bw_each + '" height="' + hs + '" fill="#79c79f" opacity="0.85"/>';
            if (n % 5 === 0) html += '<text x="' + (x0 + bw/2) + '" y="' + (pad + inner_h + 14) + '" text-anchor="middle" font-size="10" fill="#888">' + n + '</text>';
          }
          // legend
          html += '<rect x="' + (W-pad-180) + '" y="' + pad + '" width="10" height="10" fill="#7a9fd1"/>';
          html += '<text x="' + (W-pad-165) + '" y="' + (pad+9) + '" font-size="10" fill="#7a9fd1">coherent (Poisson)</text>';
          html += '<rect x="' + (W-pad-180) + '" y="' + (pad+15) + '" width="10" height="10" fill="#e8b96a"/>';
          html += '<text x="' + (W-pad-165) + '" y="' + (pad+24) + '" font-size="10" fill="#e8b96a">thermal (geometric)</text>';
          html += '<rect x="' + (W-pad-180) + '" y="' + (pad+30) + '" width="10" height="10" fill="#79c79f"/>';
          html += '<text x="' + (W-pad-165) + '" y="' + (pad+39) + '" font-size="10" fill="#79c79f">squeezed vac (even only)</text>';
          html += '<text x="' + (W/2) + '" y="' + (H-12) + '" text-anchor="middle" font-size="11" fill="#888">photon number n  (each state has ⟨n⟩ = ' + nbar.toFixed(2) + ')</text>';
          svg.innerHTML = html;
          // Mandel Q values (analytic): coherent 0, thermal n̄, squeezed-vac 2sinh²r·(1+something)
          // For squeezed vacuum with sinh²r=nbar: Var(N) = 2 nbar(nbar+1), so Q = (Var-N)/N = (2nbar(nbar+1)-nbar)/nbar = 2nbar+1
          qCoh.textContent = '0.000';
          qTh.textContent = nbar.toFixed(3);
          qSq.textContent = (2*nbar + 1).toFixed(3) + ' (super-Poiss; pair statistics)';
        }
        nbarS.addEventListener('input', draw);
        draw();
      })();
    """),
}


NOTE_02 = {
    "filename": "02_linear_optics.html",
    "title": "Linear Optics: Beam Splitters and Networks",
    "description": "Two-mode mixing, Mach-Zehnder, Reck/Clements decomposition. The substrate for boson sampling, photonic neural networks, and the FPGA-MVM in the OU machine.",
    "eyebrow": "Quantum Optics · Linear Networks",
    "h1": "Linear Optics: Beam Splitters and Networks",
    "subtitle": "Passive multi-mode mixing. How a 2-port beam splitter generalizes to an arbitrary N-port unitary, and why programmable photonic meshes are the substrate for everything from boson sampling to the Coherent Ising Machine.",
    "covers": [
        "Two-mode beam splitter as a unitary on field operators",
        "Hong-Ou-Mandel: the simplest non-classical two-photon interference",
        "Mach-Zehnder interferometer as a programmable two-mode unitary",
        "Reck and Clements decompositions of arbitrary N×N unitaries",
        "Photonic mesh implementations: integrated waveguide MZI grids",
    ],
    "nav": [
        ("two-mode-bs", "2-Mode BS"),
        ("bs-mixer", "BS Mixer Lab"),
        ("hom", "Hong-Ou-Mandel"),
        ("mzi", "Mach-Zehnder"),
        ("decompositions", "Decompositions"),
        ("photonic-meshes", "Meshes"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("two-mode-bs", "The Two-Mode Beam Splitter", r"""
          <p class="lede">
            A 50/50 beam splitter takes two input modes
            \(a_1, a_2\) and outputs two modes \(b_1, b_2\). The
            input-output relation, for a symmetric lossless beam
            splitter, is the unitary
            \[
              \begin{pmatrix} b_1 \\ b_2 \end{pmatrix} =
              \frac{1}{\sqrt{2}}
              \begin{pmatrix} 1 & i \\ i & 1 \end{pmatrix}
              \begin{pmatrix} a_1 \\ a_2 \end{pmatrix}.
            \]
            More generally a beam splitter with reflectance \(r\) and
            transmittance \(t = \sqrt{1-r^2}\) realizes
            \(U_{\mathrm{BS}}(\theta)\) with
            \(\theta = \arccos r\).
          </p>
          <p>
            The crucial fact: this is a <em>unitary on the operator
            algebra</em>, not on the wavefunction. It is the Heisenberg
            picture of how vacuum and fields mix. A coherent state
            \(\lvert\alpha\rangle\) on input 1 plus vacuum on input 2 emerges
            as a product
            \(\lvert\alpha/\sqrt{2}\rangle \otimes \lvert i\alpha/\sqrt{2}\rangle\)
            — split classically. A single photon
            \(\lvert 1\rangle \otimes \lvert 0\rangle\) emerges as the
            <em>superposition</em>
            \((\lvert 1\rangle\lvert 0\rangle + i\lvert 0\rangle\lvert 1\rangle)/\sqrt{2}\)
            — split quantum-mechanically. The bench is the same; the
            input state decides whether it looks classical.
          </p>
          """ + callout(
            "Photon loss is mathematically a beam splitter with one input "
            "tied to vacuum. This is why the same unitary algebra "
            "describes lossless mode-mixing and lossy attenuation — "
            "the difference is just whether you can access the "
            "second input."
          ),
         ["Beam splitter = 2×2 unitary on field operators",
          "Coherent state splits classically; single photon splits quantumly",
          "Loss = BS with vacuum on the unused input"]),
        ("bs-mixer", "Interactive: Beam-Splitter Mixer", r"""
          """ + widget_shell(
            anchor="bs-mixer",
            title="Two-mode beam splitter: phase + transmittance",
            blurb=(
              "Two coherent inputs <em>α</em>₁, <em>α</em>₂ enter a "
              "BS with transmittance <em>T</em> and relative input phase "
              "<em>φ</em>. The output amplitudes "
              "<em>β</em>₁ = √<em>T</em> <em>α</em>₁ + i√(1−<em>T</em>) e<sup>iφ</sup> <em>α</em>₂, "
              "<em>β</em>₂ = i√(1−<em>T</em>) <em>α</em>₁ + √<em>T</em> e<sup>iφ</sup> <em>α</em>₂. "
              "Watch the output intensities trace out the cosine "
              "interference pattern as you sweep <em>φ</em>."
            ),
            controls_html=(
              slider(var="bs-T", label="transmittance T", min_=0,
                     max_=1, step=0.01, value=0.5, fmt="{:.2f}") + "\n" +
              slider(var="bs-phi", label="phase φ", min_=0,
                     max_=6.283, step=0.05, value=0.0, fmt="{:.2f}") + "\n" +
              slider(var="bs-a1", label="|α₁|", min_=0,
                     max_=2.5, step=0.05, value=1.0, fmt="{:.2f}") + "\n" +
              slider(var="bs-a2", label="|α₂|", min_=0,
                     max_=2.5, step=0.05, value=1.0, fmt="{:.2f}")
            ),
            canvas_html=svg_el("bs-mixer", w=520, h=260),
            readout_html=(
              '<div>|β₁|² = <span id="bs-out1">—</span> &nbsp; '
              '|β₂|² = <span id="bs-out2">—</span></div>'
              '<div>Total |β|² = <span id="bs-tot">—</span> '
              '(should equal |α₁|²+|α₂|² for a unitary)</div>'
            ),
          ) + r"""
          """,
         ["BS = 2×2 unitary, phase-sensitive",
          "Output intensities are sinusoidal in φ",
          "Total photon number is conserved"]),
        ("hom", "Hong-Ou-Mandel Interference", r"""
          <p>
            Send two indistinguishable single photons into the two
            inputs of a 50/50 BS:
            \(\lvert 1, 1\rangle_{a_1 a_2} \to \tfrac{1}{2}
            (\lvert 2, 0\rangle - \lvert 0, 2\rangle)
            i^2 = -\tfrac{1}{2}(\lvert 2,0\rangle - \lvert 0,2\rangle)\).
            The amplitude for the \(\lvert 1,1\rangle\) outcome —
            "one photon in each output" — is exactly zero by
            destructive interference. Both photons bunch together.
          </p>
          <p>
            HOM is the simplest experiment that demonstrates non-classical
            interference. Its visibility is set by photon
            indistinguishability (spectral, temporal, polarization
            overlap), and a HOM dip is now the standard benchmark for
            single-photon-source quality.
          </p>
          """,
         ["HOM dip = bosonic two-photon interference",
          "Visibility ↔ photon indistinguishability",
          "Standard benchmark for SPS quality"]),
        ("mzi", "Mach-Zehnder Interferometer", r"""
          <p>
            Sandwich a controllable phase \(\phi\) between two BSs and
            you get a Mach-Zehnder interferometer:
            \[
              U_\mathrm{MZI}(\phi, \theta)
              = \mathrm{BS}(\theta_2)\,
                \mathrm{Phase}(\phi)\,
                \mathrm{BS}(\theta_1).
            \]
            With two phase-shifter knobs, the MZI realizes any 2×2
            unitary up to a global phase — i.e. it is a
            <em>programmable</em> two-mode unitary. On integrated
            silicon photonics, MZIs are the building block of
            reconfigurable optical processors.
          </p>
          """,
         ["MZI = 2 BS + 2 phase shifters",
          "Realizes any 2×2 unitary up to global phase",
          "Building block for reconfigurable photonic chips"]),
        ("decompositions", "Reck and Clements Decompositions", r"""
          <p>
            <strong>Theorem (Reck et al., 1994; Clements et al., 2016):</strong>
            any N×N unitary \(U \in U(N)\) can be implemented by a
            cascade of \(\binom{N}{2}\) two-mode MZIs plus phase
            shifters arranged in a triangular (Reck) or rectangular
            (Clements) layout. Every entry of \(U\) shows up as an
            interference of paths through the mesh.
          </p>
          <p>
            For \(N=8\) this is 28 MZIs, plus 8 input-phase shifters.
            For \(N=64\) it is 2,016 MZIs — the limit of current
            silicon photonics in a single chip. The Clements layout is
            depth-balanced (depth \(N\)) and is what most modern
            photonic-processor chips use.
          </p>
          """ + math_details("Why the count is \\(\\binom{N}{2}\\)", r"""
            <p>
              The unitary group \(U(N)\) has real dimension \(N^2\). The
              maximal torus of phase shifters absorbs \(N\) of those.
              The remaining \(N^2 - N = N(N-1)\) parameters are
              accounted for by \(\binom{N}{2} = N(N-1)/2\) MZIs, each
              carrying two angles (\(\theta\) and \(\phi\)). Hence the
              count.
            </p>
          """),
         ["Any N×N unitary realized as an MZI mesh",
          "Mesh has \\(\\binom{N}{2}\\) MZIs",
          "Clements layout is depth-N, used by modern photonic chips"]),
        ("photonic-meshes", "Photonic Meshes in the Wild", r"""
          <p>
            Programmable MZI meshes are the substrate behind several
            otherwise-distinct photonic computing efforts:
          </p>
          <ul>
            <li><strong>Boson sampling</strong> (Aaronson &amp; Arkhipov 2011;
              Xanadu Borealis 2022): N-port unitary acting on
              indistinguishable single photons; output statistics
              hard-to-classically-simulate when \(N \gtrsim 50\).</li>
            <li><strong>Photonic neural networks</strong> (Shen et al.
              <em>Nat. Photonics</em> 2017; Hamerly et al. <em>Sci. Adv.</em>
              2019): the mesh implements a linear layer; nonlinearity
              comes from electro-optic modulators or detector responses.</li>
            <li><strong>Photonic quantum simulators</strong>: continuous-time
              quantum walks, vibronic spectra, etc.</li>
            <li><strong>Coherent Ising Machine FPGA-MVM (Note 06)</strong>:
              the matrix-vector multiply
              \(\textstyle\sum_j J_{ij} x_j\) in the homodyne-feedback
              loop is structurally identical to a classical photonic
              MAC, even though it runs on the digitized photocurrent
              rather than the optical field. The architecture would
              naturally generalize to optical-domain MVM via a Reck/
              Clements mesh — an active research direction.</li>
          </ul>
          """ + callout(
            "Any unitary is realizable on a passive linear optical "
            "mesh. <em>Any nonunitary linear map</em> requires either "
            "loss (post-selection) or an extra ancilla mode. This is "
            "the structural reason photonic processors that run a "
            "non-unitary operation (e.g. solving Ax=b) need either "
            "feedback (CIM/OU) or auxiliary modes (HHL-style)."
          ),
         ["MZI meshes underlie boson sampling, PNN, photonic QC",
          "Pure unitaries are easy; nonunitary linear maps need feedback",
          "CIM-MVM is digital today, optical-MVM is the natural extension"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/L3_beamsplitters_and_interference.pdf">L3_beamsplitters_and_interference.pdf</a></td></tr>
            <tr><td>Lecture</td><td><a href="_lectures/optical_components.pdf">optical_components.pdf</a></td></tr>
            <tr><td>Figure</td><td><a href="_lectures/Interferometer.png">Interferometer.png</a>, <a href="_lectures/beamsplitter.png">beamsplitter.png</a></td></tr>
            <tr><td>Paper</td><td>Reck, Zeilinger, Bernstein, Bertani, "Experimental realization of any discrete unitary operator", <em>PRL</em> <strong>73</strong>, 58 (1994)</td></tr>
            <tr><td>Paper</td><td>Clements, Humphreys, Metcalf, Kolthammer, Walmsley, "Optimal design for universal multiport interferometers", <em>Optica</em> <strong>3</strong>, 1460 (2016)</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §03 — Nonlinear optics. Linear
            networks alone don't generate non-classical light; for that
            we need a χ⁽²⁾ or χ⁽³⁾ medium.
          </p>
          """,
         ["Reck 1994: original triangular decomposition",
          "Clements 2016: depth-balanced rectangular form",
          "Continue: Note 03 (nonlinear optics)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: beam-splitter mixer (SVG diagram + intensities) ------
      (function () {
        var svg = document.getElementById('bs-mixer-svg');
        if (!svg) return;
        var els = {};
        ['T', 'phi', 'a1', 'a2'].forEach(function (k) {
          els[k] = document.getElementById('bs-' + k);
          els[k+'V'] = document.getElementById('bs-' + k + '-val');
        });
        var out1 = document.getElementById('bs-out1');
        var out2 = document.getElementById('bs-out2');
        var tot = document.getElementById('bs-tot');
        function draw() {
          var T = parseFloat(els.T.value);
          var phi = parseFloat(els.phi.value);
          var a1 = parseFloat(els.a1.value);
          var a2 = parseFloat(els.a2.value);
          els.TV.textContent = T.toFixed(2);
          els.phiV.textContent = phi.toFixed(2);
          els.a1V.textContent = a1.toFixed(2);
          els.a2V.textContent = a2.toFixed(2);
          // β₁ = √T α₁ + i√(1-T) e^(iφ) α₂  (real α treatment)
          // β₂ = i√(1-T) α₁ + √T e^(iφ) α₂
          var rT = Math.sqrt(T), rR = Math.sqrt(1-T);
          var c = Math.cos(phi), s = Math.sin(phi);
          // re/im of β₁
          var b1r = rT*a1 - rR*a2*s;
          var b1i = rR*a2*c;
          var b2r = -rR*a1*s + rT*a2*c;
          var b2i = rR*a1 + rT*a2*s;
          var I1 = b1r*b1r + b1i*b1i;
          var I2 = b2r*b2r + b2i*b2i;
          var W = 520, H = 260, cx = W/2, cy = H/2;
          var html = '';
          // BS as a 45° box
          html += '<rect x="' + (cx-30) + '" y="' + (cy-30) + '" width="60" height="60" fill="rgba(122,159,209,0.15)" stroke="#7a9fd1" stroke-width="1.5" transform="rotate(45 ' + cx + ' ' + cy + ')"/>';
          html += '<text x="' + cx + '" y="' + (cy+5) + '" text-anchor="middle" font-size="11" fill="#7a9fd1">BS</text>';
          // input 1: from left
          html += '<line x1="40" y1="' + cy + '" x2="' + (cx-50) + '" y2="' + cy + '" stroke="#888" stroke-width="2"/>';
          html += '<text x="40" y="' + (cy-8) + '" font-size="11" fill="#7a9fd1">α₁ = ' + a1.toFixed(2) + '</text>';
          // input 2: from top
          html += '<line x1="' + cx + '" y1="40" x2="' + cx + '" y2="' + (cy-50) + '" stroke="#888" stroke-width="2"/>';
          html += '<text x="' + (cx+8) + '" y="40" font-size="11" fill="#e8b96a">α₂ e^{iφ} = ' + a2.toFixed(2) + ' e^{i' + phi.toFixed(2) + '}</text>';
          // output 1: to right
          var maxI = Math.max(I1, I2, 0.001);
          var w1 = 1 + 6*Math.sqrt(I1 / maxI);
          var w2 = 1 + 6*Math.sqrt(I2 / maxI);
          html += '<line x1="' + (cx+50) + '" y1="' + cy + '" x2="' + (W-40) + '" y2="' + cy + '" stroke="#79c79f" stroke-width="' + w1.toFixed(1) + '"/>';
          html += '<text x="' + (W-40) + '" y="' + (cy-8) + '" text-anchor="end" font-size="11" fill="#79c79f">|β₁|² = ' + I1.toFixed(2) + '</text>';
          // output 2: down
          html += '<line x1="' + cx + '" y1="' + (cy+50) + '" x2="' + cx + '" y2="' + (H-30) + '" stroke="#79c79f" stroke-width="' + w2.toFixed(1) + '"/>';
          html += '<text x="' + (cx+8) + '" y="' + (H-30) + '" font-size="11" fill="#79c79f">|β₂|² = ' + I2.toFixed(2) + '</text>';
          // T label
          html += '<text x="20" y="20" font-size="11" fill="#888">T = ' + T.toFixed(2) + ' (transmittance)</text>';
          svg.innerHTML = html;
          out1.textContent = I1.toFixed(3);
          out2.textContent = I2.toFixed(3);
          tot.textContent = (I1+I2).toFixed(3) + '  vs.  α₁²+α₂² = ' + (a1*a1+a2*a2).toFixed(3);
        }
        ['T', 'phi', 'a1', 'a2'].forEach(function (k) { els[k].addEventListener('input', draw); });
        draw();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Note 03: Nonlinear Optics
# ---------------------------------------------------------------------------

NOTE_03 = {
    "filename": "03_nonlinear_optics.html",
    "title": "Nonlinear Optics and Parametric Processes",
    "description": "χ⁽²⁾ and χ⁽³⁾ susceptibilities, three-wave mixing, parametric down-conversion, and where squeezed light comes from.",
    "eyebrow": "Quantum Optics · Nonlinear",
    "h1": "Nonlinear Optics and Parametric Processes",
    "subtitle": "Where squeezing and entanglement are made. The χ⁽²⁾ and χ⁽³⁾ medium is the only place in the photonic stack where photon-photon interactions are non-trivial — and that is the entire source of quantumness in subsequent notes.",
    "covers": [
        "Polarization expansion: \\(P = \\varepsilon_0(\\chi^{(1)}E + \\chi^{(2)}E^2 + \\chi^{(3)}E^3 + \\dots)\\)",
        "Three-wave mixing in χ⁽²⁾: SHG, sum/difference frequency",
        "Parametric down-conversion as photon pair generation",
        "Optical parametric amplification and oscillation thresholds",
        "Squeezed-vacuum generation: what S(r) actually does in hardware",
        "χ⁽³⁾ effects: Kerr, four-wave mixing, soliton OPOs",
    ],
    "nav": [
        ("polarization", "Polarization Expansion"),
        ("three-wave", "Three-Wave Mixing"),
        ("pdc", "Down-Conversion"),
        ("opa-opo", "OPA / OPO"),
        ("squeezing-gen", "Squeezing"),
        ("squeeze-trajectory", "Squeeze Lab"),
        ("chi3", "χ⁽³⁾ Effects"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("polarization", "The Polarization Expansion", r"""
          <p class="lede">
            Linear optics — beam splitters, mirrors, free-space propagation
            — assumes the medium responds proportionally to the incident
            electric field: \(P = \varepsilon_0 \chi^{(1)} E\). Real
            materials are linear only at low intensity. At high enough
            field, the polarization picks up corrections:
            \[
              P = \varepsilon_0\bigl(\chi^{(1)} E
                  + \chi^{(2)} E^2
                  + \chi^{(3)} E^3 + \cdots\bigr).
            \]
            \(\chi^{(2)}\) is allowed only in non-centrosymmetric crystals
            (LiNbO\(_3\), KTP, BBO, periodically-poled LiNbO\(_3\)). \(\chi^{(3)}\)
            exists in everything but is typically much smaller.
          </p>
          <p>
            The numbers: in a good χ⁽²⁾ crystal, you start to see
            three-wave-mixing effects at intensities of order
            10\(^9\)–10\(^{12}\) W/m². Pulsed lasers focused into a few-mm
            crystal hit that comfortably. CW lasers need cavity
            enhancement (Note 06).
          </p>
          """,
         ["Linear ↔ nonlinear: order in E in the polarization",
          "χ⁽²⁾ requires non-centrosymmetric crystals",
          "Cavity enhancement is the standard way to reach NL regime in CW"]),
        ("three-wave", "Three-Wave Mixing", r"""
          <p>
            In a χ⁽²⁾ medium with two input fields at frequencies
            \(\omega_1, \omega_2\), the polarization picks up a term
            \(\sim \chi^{(2)} E_1 E_2\) that drives radiation at
            \(\omega_1 \pm \omega_2\). The energy- and momentum-conserving
            outputs are:
          </p>
          <ul>
            <li><strong>Second-harmonic generation (SHG):</strong>
              \(\omega + \omega \to 2\omega\). Standard frequency-doubling.</li>
            <li><strong>Sum-frequency generation:</strong>
              \(\omega_1 + \omega_2 \to \omega_1 + \omega_2\).</li>
            <li><strong>Difference-frequency generation:</strong>
              \(\omega_1 - \omega_2 \to \omega_1 - \omega_2\).</li>
            <li><strong>Spontaneous parametric down-conversion (SPDC):</strong>
              \(\omega_p \to \omega_s + \omega_i\). The reverse of
              sum-frequency: a pump photon spontaneously decays into
              signal + idler photons. The cornerstone of two-photon
              entanglement experiments.</li>
          </ul>
          <p>
            All four require <strong>phase matching</strong>: the wavevectors
            must satisfy \(k_p = k_s + k_i\) (and analogously for SHG, etc.)
            to interfere constructively over the crystal length. Phase
            matching is the engineering constraint that decides which
            wavelengths and polarizations a given crystal can mix.
          </p>
          """ + callout(
            "Phase matching is a 1D problem with three knobs: temperature, "
            "angle, and quasi-phase-matching grating period. Periodically "
            "poled LiNbO₃ (PPLN) — flipping the χ⁽²⁾ sign every coherence "
            "length — gave the field the room-temperature, normal-dispersion, "
            "any-wavelength flexibility that makes modern integrated "
            "OPOs possible."
          ),
         ["χ⁽²⁾ media drive sum/difference/SHG/SPDC",
          "Energy + momentum conservation = phase matching",
          "PPLN: quasi-phase-matched χ⁽²⁾, the workhorse"]),
        ("pdc", "Spontaneous Parametric Down-Conversion", r"""
          <p>
            The Hamiltonian for the SPDC interaction in the
            <em>undepleted-pump approximation</em> (treat the pump
            classically as a coherent state \(\beta_p\)) is
            \[
              H_\mathrm{int} = i\hbar\,g\bigl(\beta_p^* a_s a_i
                - \beta_p a_s^\dagger a_i^\dagger\bigr),
            \]
            where \(g \propto \chi^{(2)}\) and \(\beta_p\) is the pump
            amplitude. Time evolution under \(H_\mathrm{int}\) creates
            signal-idler photon pairs from the pump.
          </p>
          <p>
            For degenerate SPDC (\(\omega_s = \omega_i = \omega_p/2\),
            same polarization, same mode), \(a_s = a_i = a\) and the
            Hamiltonian becomes
            \(H = i\hbar(g\beta_p^* a^2 - g\beta_p (a^\dagger)^2)/2\).
            The unitary it generates is exactly the squeeze operator
            \(S(r)\) with \(r = g\lvert\beta_p\rvert t\). <em>The physical
            mechanism that produces squeezing is degenerate SPDC.</em>
          </p>
          """,
         ["SPDC: pump → signal + idler photon pair",
          "Degenerate SPDC = squeezing generation",
          "Pump amplitude × interaction strength × time = squeezing parameter"]),
        ("opa-opo", "Parametric Amplifiers and Oscillators", r"""
          <p>
            Send a weak signal field through a χ⁽²⁾ crystal pumped
            classically. The signal picks up gain (it is being
            "amplified" by photons borrowed from the pump). With no
            feedback and a single pass, the gain is small —
            you have an <strong>optical parametric amplifier (OPA)</strong>.
          </p>
          <p>
            Now place the χ⁽²⁾ crystal inside an optical cavity that
            resonates at the signal frequency. Below the threshold pump
            power, photons leak out faster than gain replenishes them —
            output is just amplified vacuum (squeezed light). Above
            threshold, gain exceeds loss and the cavity field grows
            exponentially until pump depletion saturates it. This is
            an <strong>optical parametric oscillator (OPO)</strong>.
            For degenerate (signal = idler), the output picks one of
            two phases (the <strong>DOPO</strong>, Note 06).
          </p>
          """ + callout(
            "Below threshold: OPO output is squeezed vacuum. Above "
            "threshold: OPO output is a coherent state with a binary "
            "phase. The threshold pump power is the most physically "
            "important parameter of a parametric oscillator."
          ),
         ["OPA: parametric gain, no cavity",
          "OPO: gain + cavity → threshold dynamics",
          "Below threshold: squeezing; above threshold: binary-phase oscillation"]),
        ("squeezing-gen", "Squeezing Generation in Practice", r"""
          <p>
            Hardware records: the world record for inferred squeezing
            is \(\sim 15\) dB (Vahlbruch et al., <em>PRL</em> 2016) using a
            sub-threshold OPO with periodically-poled KTP. For
            usable-at-detector squeezing (after homodyne efficiency),
            10 dB is excellent; 5–6 dB is routine.
          </p>
          <p>
            The chain of efficiency hits is:
          </p>
          <ul>
            <li>Crystal escape efficiency (intracavity loss): −0.5 dB</li>
            <li>Optical path loss to detector: −0.5 to −1 dB</li>
            <li>Detector quantum efficiency (e.g. 95%): −0.2 dB</li>
            <li>LO mode-match: −0.5 dB</li>
            <li>Excess phase noise: degrades anti-squeezing-into-squeezing leakage</li>
          </ul>
          <p>
            For our purposes (Note 06's CIM, Note 07's OU machine
            running below threshold for sampling): squeezing is a
            constant-factor advantage on a homodyne measurement. It
            does not solve the κ-conditioning problem of the linear-algebra
            sampler.
          </p>
          """,
         ["State-of-the-art: ~15 dB squeezing in lab",
          "Detection-loss eats squeezing rapidly",
          "Squeezing alone doesn't break κ-scaling for OU sampler"]),
        ("chi3", "χ⁽³⁾ Effects, Briefly", r"""
          <p>
            The cubic susceptibility χ⁽³⁾ exists in centrosymmetric
            media — silica fiber, silicon waveguides, AlGaAs. It drives:
          </p>
          <ul>
            <li><strong>Self-phase modulation:</strong> intensity-dependent
              refractive index \(n = n_0 + n_2 I\). Fundamental to optical
              soliton physics in fiber.</li>
            <li><strong>Cross-phase modulation:</strong> field-1 modulates
              the index seen by field-2.</li>
            <li><strong>Four-wave mixing:</strong>
              \(\omega_1 + \omega_2 \to \omega_3 + \omega_4\). Source of
              fiber-based squeezed light and soliton-OPOs.</li>
            <li><strong>Optical Kerr effect</strong> in cavities → bistability,
              soliton combs (the basis of integrated frequency combs).</li>
          </ul>
          <p>
            For the CIM and OU-machine programs: χ⁽³⁾ comes up only as
            a parasitic effect — Kerr-induced self-phase shifts that
            distort the round-trip dynamics if the pulse intensity is
            too high. It is generally a thing to engineer
            <em>against</em>, not a resource. The exception is
            soliton-DOPO research (Marandi group, Caltech) where Kerr
            stabilizes ultrashort pulse trains.
          </p>
          """,
         ["χ⁽³⁾ ubiquitous: SPM, XPM, FWM, Kerr",
          "Soliton physics is χ⁽³⁾",
          "For CIM/OU: typically a parasitic to suppress, not exploit"]),
        ("squeeze-trajectory", "Interactive: Squeezing in Phase Space", r"""
          <p class="lede">
            The χ⁽²⁾-driven squeeze operator \(S(r,\theta)\) takes the
            unit-circle vacuum noise and stretches it into an ellipse:
            \(e^{-r}\) along one axis, \(e^{+r}\) along the orthogonal
            axis, rotated by \(\theta\). This is the geometry that
            below-threshold OPOs produce.
          </p>
          """ + widget_shell(
            anchor="squeeze-trajectory",
            title="Phase-space squeezed-vacuum ellipse",
            blurb=(
              "Slide squeeze parameter <em>r</em> and angle <em>θ</em>. "
              "The unit-circle vacuum noise (dashed) is the reference; "
              "the squeezed ellipse (solid) shows the squeezed and "
              "anti-squeezed quadratures. The product Var(<em>X</em>) · "
              "Var(<em>P</em>) = ¼ holds: this is a minimum-uncertainty "
              "state."
            ),
            controls_html=(
              slider(var="sq-r", label="squeeze r", min_=0, max_=1.5,
                     step=0.05, value=0.6, fmt="{:.2f}") + "\n" +
              slider(var="sq-theta", label="angle θ", min_=0, max_=3.14,
                     step=0.05, value=0.0, fmt="{:.2f}")
            ),
            canvas_html=svg_el("squeeze-trajectory", w=440, h=320),
            readout_html=(
              '<div>Squeezed Var = ½e^{−2r} = <span id="sq-var-min">—</span> '
              '(<span id="sq-db-min">—</span> dB below SNL)</div>'
              '<div>Anti-squeezed Var = ½e^{+2r} = <span id="sq-var-max">—</span></div>'
              '<div>Product Var(X)·Var(P) = <span id="sq-prod">—</span> (Heisenberg minimum: 1/4)</div>'
            ),
          ) + r"""
          """,
         ["Squeeze ellipse: shrunk in one quadrature, stretched in other",
          "\\(e^{-2r}\\) variance reduction in dB: \\(-8.7 r\\)",
          "Heisenberg saturation: Var(X)·Var(P) = ¼"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/nonlinear_optics.pdf">nonlinear_optics.pdf</a> — primary source</td></tr>
            <tr><td>Lecture</td><td><a href="_lectures/OPOs_and_coherent_Ising.pdf">OPOs_and_coherent_Ising.pdf</a> — OPO threshold, used heavily in Note 06</td></tr>
            <tr><td>Reference</td><td>Boyd, <em>Nonlinear Optics</em> (4th ed., Academic Press, 2020)</td></tr>
            <tr><td>Paper</td><td>Vahlbruch et al., "Detection of 15 dB squeezed states of light", <em>PRL</em> <strong>117</strong>, 110801 (2016)</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §04 — Cavity QED and open
            systems. We put a χ⁽²⁾ medium inside a leaky cavity and
            derive the master equation that everything in this track
            ultimately uses.
          </p>
          """,
         ["Boyd is the standard nonlinear-optics text",
          "Vahlbruch 2016: 15 dB squeezing record",
          "Continue: Note 04 (cavity QED)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: squeeze-trajectory phase-space ellipse ---------------
      (function () {
        var svg = document.getElementById('squeeze-trajectory-svg');
        if (!svg) return;
        var rS = document.getElementById('sq-r');
        var thS = document.getElementById('sq-theta');
        var rV = document.getElementById('sq-r-val');
        var thV = document.getElementById('sq-theta-val');
        var vmin = document.getElementById('sq-var-min');
        var vmax = document.getElementById('sq-var-max');
        var dbmin = document.getElementById('sq-db-min');
        var prod = document.getElementById('sq-prod');
        function draw() {
          var r = parseFloat(rS.value);
          var th = parseFloat(thS.value);
          rV.textContent = r.toFixed(2);
          thV.textContent = th.toFixed(2);
          var W = 440, H = 320, cx = W/2, cy = H/2;
          var SCALE = 50;
          var Vsq = 0.5 * Math.exp(-2*r);
          var Vasq = 0.5 * Math.exp(2*r);
          var html = '';
          // axes
          html += '<line x1="0" y1="' + cy + '" x2="' + W + '" y2="' + cy + '" stroke="#666"/>';
          html += '<line x1="' + cx + '" y1="0" x2="' + cx + '" y2="' + H + '" stroke="#666"/>';
          html += '<text x="' + (W-12) + '" y="' + (cy-5) + '" font-size="11" fill="#888">X</text>';
          html += '<text x="' + (cx+5) + '" y="12" font-size="11" fill="#888">P</text>';
          // unit-circle vacuum reference  (radius √(1/2) * SCALE)
          var Rvac = Math.sqrt(0.5) * SCALE;
          html += '<circle cx="' + cx + '" cy="' + cy + '" r="' + Rvac + '" fill="none" stroke="#888" stroke-width="1.2" stroke-dasharray="3,3"/>';
          html += '<text x="' + (cx + Rvac + 4) + '" y="' + (cy + Rvac + 4) + '" font-size="10" fill="#888">vacuum</text>';
          // squeezed ellipse: semi-axes √Vsq and √Vasq * SCALE, rotated by θ rad
          var ax_sq = Math.sqrt(Vsq) * SCALE;
          var ax_asq = Math.sqrt(Vasq) * SCALE;
          var deg = th * 180 / Math.PI;
          html += '<ellipse cx="' + cx + '" cy="' + cy + '" rx="' + ax_sq + '" ry="' + ax_asq + '" fill="rgba(121,247,156,0.18)" stroke="#79f29c" stroke-width="2" transform="rotate(' + deg.toFixed(1) + ' ' + cx + ' ' + cy + ')"/>';
          // arrow showing squeeze direction
          var dx = ax_sq * Math.cos(th), dy = -ax_sq * Math.sin(th);
          html += '<line x1="' + cx + '" y1="' + cy + '" x2="' + (cx+dx) + '" y2="' + (cy+dy) + '" stroke="#79f29c" stroke-width="1.5"/>';
          html += '<text x="' + (cx+dx+5) + '" y="' + (cy+dy-5) + '" font-size="10" fill="#79f29c">squeezed</text>';
          var dx2 = ax_asq * Math.cos(th + Math.PI/2), dy2 = -ax_asq * Math.sin(th + Math.PI/2);
          html += '<line x1="' + cx + '" y1="' + cy + '" x2="' + (cx+dx2) + '" y2="' + (cy+dy2) + '" stroke="#f29c79" stroke-width="1.5"/>';
          html += '<text x="' + (cx+dx2+5) + '" y="' + (cy+dy2-5) + '" font-size="10" fill="#f29c79">anti-squeezed</text>';
          svg.innerHTML = html;
          vmin.textContent = Vsq.toFixed(4);
          vmax.textContent = Vasq.toFixed(4);
          dbmin.textContent = (-8.686 * r).toFixed(2);
          prod.textContent = (Vsq * Vasq).toFixed(4) + ' = (1/2)² (saturated)';
        }
        rS.addEventListener('input', draw);
        thS.addEventListener('input', draw);
        draw();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Note 04: Cavity QED & Open Systems
# ---------------------------------------------------------------------------

NOTE_04 = {
    "filename": "04_cavity_qed_open_systems.html",
    "title": "Cavity QED and Open Quantum Systems",
    "description": "Driven leaky cavities, the Lindblad master equation, input-output formalism, and the bridge from operator dynamics to classical Langevin in the bright-field limit.",
    "eyebrow": "Quantum Optics · Open Systems",
    "h1": "Cavity QED and Open Quantum Systems",
    "subtitle": "How a bench-realistic optical cavity is described mathematically. The Lindblad master equation is the workhorse for everything we model in subsequent notes; the bright-field reduction to classical Langevin is what makes the Coherent Ising Machine analytically tractable.",
    "covers": [
        "Driven-cavity Hamiltonian: free field + classical drive + nonlinearity",
        "Photon loss as a beam-splitter with vacuum: the standard derivation",
        "Lindblad master equation \\(d\\rho/dt = -i[H,\\rho] + \\sum_k \\mathcal{D}[L_k]\\rho\\)",
        "Input-output formalism: \\(a_\\mathrm{out} = a_\\mathrm{in} + \\sqrt{2\\kappa}\\, a\\)",
        "Quantum Langevin equation in the Heisenberg picture",
        "The bright-field / mean-field limit: Heisenberg → classical Langevin",
    ],
    "nav": [
        ("driven-cavity", "Driven Cavity"),
        ("loss-as-bs", "Loss as BS"),
        ("lindblad", "Lindblad"),
        ("input-output", "Input-Output"),
        ("langevin", "Langevin"),
        ("classical-limit", "Classical Limit"),
        ("cavity-decay", "Decay Lab"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("driven-cavity", "The Driven Cavity Hamiltonian", r"""
          <p class="lede">
            Take a single-mode optical cavity with annihilation operator
            \(a\), resonance frequency \(\omega_c\). Drive it with a
            classical coherent field at \(\omega_d\), with amplitude
            \(\varepsilon\). In the rotating frame at \(\omega_d\) the
            Hamiltonian is
            \[
              H = \Delta\, a^\dagger a
                + i\bigl(\varepsilon a^\dagger - \varepsilon^* a\bigr)
                + H_\mathrm{NL},
            \]
            where \(\Delta = \omega_c - \omega_d\) is the detuning and
            \(H_\mathrm{NL}\) is whatever nonlinear term the χ⁽²⁾ or χ⁽³⁾
            medium contributes (e.g.\ degenerate SPDC for an OPO).
          </p>
          <p>
            By itself \(H\) generates unitary, lossless, eternal
            dynamics. Real cavities have output mirrors, so photons
            leak. We need to handle that systematically.
          </p>
          """,
         ["\\(H = \\Delta a^\\dagger a + i(\\varepsilon a^\\dagger - \\varepsilon^* a) + H_\\mathrm{NL}\\)",
          "Detuning Δ controls resonance offset",
          "Drive ε is the classical coherent input"]),
        ("loss-as-bs", "Photon Loss as a Beam-Splitter with Vacuum", r"""
          <p>
            The physical mechanism: an output mirror with reflectance
            \(r\) and transmittance \(t = \sqrt{1-r^2}\) couples the
            cavity mode to an external bath of vacuum modes. By the
            beam-splitter relation (Note 02), the field that emerges
            from the mirror is
            \[
              a_\mathrm{out} = t\, a_\mathrm{cav} + r\, a_\mathrm{vac},
            \]
            and the field that remains is
            \(r\, a_\mathrm{cav} + t\, a_\mathrm{vac}\). Each round
            trip mixes a fraction \(r^2\) of vacuum into the cavity
            field. In the continuous-time limit (\(t\) small,
            round-trip time \(\Delta t\)), this becomes
            \(da/dt = -\kappa\, a + \xi(t)\), where the cavity decay
            rate \(\kappa\) is set by the mirror transmittance and the
            bath \(\xi(t)\) is white-noise vacuum fluctuations.
          </p>
          """ + callout(
            'Loss is not &ldquo;non-unitary&rdquo; in any deep sense — it is a '
            'unitary entanglement with a much larger bath, traced '
            'out at the end. The beam-splitter derivation makes this '
            'concrete: the unitary that mixes cavity and vacuum is the '
            'exact opposite of mysterious.'
          ),
         ["Loss = unitary entanglement with vacuum modes",
          "Cavity decay rate κ ↔ output mirror transmittance",
          "Continuous-time limit: \\(da/dt = -\\kappa a + \\xi(t)\\)"]),
        ("lindblad", "The Lindblad Master Equation", r"""
          <p>
            Tracing out the bath gives a closed evolution for the
            reduced density operator \(\rho\) of the cavity mode:
            \[
              \frac{d\rho}{dt}
              = -\tfrac{i}{\hbar}\bigl[H, \rho\bigr]
                + \sum_k \mathcal{D}[L_k]\,\rho,
            \]
            where the Lindblad superoperator
            \[
              \mathcal{D}[L]\,\rho
              = L\rho L^\dagger
                - \tfrac{1}{2}\bigl\{L^\dagger L, \rho\bigr\}.
            \]
            The "jump operators" \(L_k\) describe the irreversible
            channels. For a leaky cavity with one output port:
            \(L_1 = \sqrt{2\kappa}\, a\). For multiple ports, add more
            \(L_k\). For thermal-bath excitations at temperature
            \(T > 0\): a second jump operator \(L_2 = \sqrt{2\kappa\bar n}\, a^\dagger\).
          </p>
          <p>
            Three concrete uses of the Lindblad form in this track:
          </p>
          <ul>
            <li><strong>OPO threshold dynamics</strong> (Note 06): full
              quantum description of the bifurcation, including
              spontaneous-emission-driven phase selection.</li>
            <li><strong>CIM full-quantum simulation</strong>: exact for
              small networks (\(\le 4\) modes); requires Gaussian
              approximations or trajectories above that.</li>
            <li><strong>OU machine cross-check</strong>: in the bright-field
              limit, the Heisenberg-Langevin equations reduce to
              classical SDEs, and the Lyapunov sampler of Note 07
              applies.</li>
          </ul>
          """ + math_details("Why the Lindblad form is the unique GKSL structure", r"""
            <p>
              Gorini–Kossakowski–Sudarshan and Lindblad (independently,
              1976) proved that any time-local, completely positive,
              trace-preserving map on a finite-dimensional Hilbert space
              has a generator of exactly the above form — Hamiltonian
              part plus a sum of "dissipator" terms. The structure is
              not a modeling choice; it is forced by physical consistency
              (positivity of probabilities, no signaling, …).
            </p>
          """),
         ["GKSL form: \\(\\dot\\rho = -i[H,\\rho] + \\sum_k \\mathcal{D}[L_k]\\rho\\)",
          "Each jump operator \\(L_k\\) is one decoherence channel",
          "Cavity loss: \\(L = \\sqrt{2\\kappa} a\\). Thermal: add \\(L = \\sqrt{2\\kappa\\bar n} a^\\dagger\\)"]),
        ("input-output", "Input-Output Formalism", r"""
          <p>
            Gardiner &amp; Collett (1985) made the bath-and-cavity
            picture rigorous. The input field — vacuum or whatever —
            arriving at the cavity mirror is \(a_\mathrm{in}(t)\).
            The output field that propagates away is \(a_\mathrm{out}(t)\).
            The cavity mode \(a(t)\) is the intracavity operator.
            They are related by the <strong>input-output relation</strong>:
            \[
              a_\mathrm{out}(t) = a_\mathrm{in}(t) + \sqrt{2\kappa}\, a(t).
            \]
            What we measure outside the cavity (homodyne, photon
            counting, etc., Note 05) is \(a_\mathrm{out}\); the
            \(\sqrt{2\kappa}\, a\) term is the signal we want, and
            \(a_\mathrm{in}\) is the unavoidable vacuum noise at our
            detector.
          </p>
          <p>
            The picture: the cavity mode \(a(t)\) is a memory; vacuum
            comes in, mixes with it, leaves. What you can read off the
            output current is the cavity dynamics convolved with the
            \(\kappa\)-bandwidth filter.
          </p>
          """,
         ["\\(a_\\mathrm{out} = a_\\mathrm{in} + \\sqrt{2\\kappa}\\, a\\)",
          "Input field \\(a_\\mathrm{in}\\) carries unavoidable vacuum noise",
          "Output is a κ-bandwidth-filtered view of cavity dynamics"]),
        ("langevin", "The Quantum Langevin Equation", r"""
          <p>
            In the Heisenberg picture, the input-output formalism gives
            \[
              \dot a(t) = -\bigl(i\Delta + \kappa\bigr) a
                + \varepsilon
                + \tfrac{i}{\hbar}[H_\mathrm{NL}, a]
                - \sqrt{2\kappa}\, a_\mathrm{in}(t).
            \]
            For vacuum input, \(a_\mathrm{in}(t)\) has
            \(\langle a_\mathrm{in}(t)\rangle = 0\) and
            \(\langle a_\mathrm{in}(t) a_\mathrm{in}^\dagger(t')\rangle = \delta(t-t')\)
            (white noise). This is the quantum analogue of an
            Ornstein-Uhlenbeck Langevin equation.
          </p>
          """,
         ["Heisenberg-picture EoM with vacuum white-noise drive",
          "Operator-valued Langevin equation",
          "Reduces to classical Langevin in bright-field limit (next §)"]),
        ("classical-limit", "Bright-Field Limit and Classical Langevin", r"""
          <p>
            Decompose \(a(t) = \alpha(t) + \delta a(t)\) with \(\alpha = \langle a\rangle\)
            the (large) classical mean and \(\delta a\) the (small)
            quantum fluctuation. To zeroth order in \(\delta a\), the
            mean satisfies a deterministic equation:
            \[
              \dot\alpha = -(i\Delta + \kappa)\alpha + \varepsilon
                + (\text{nonlinear terms in }\alpha).
            \]
            To first order in \(\delta a\), the fluctuations satisfy a
            linear stochastic differential equation driven by the
            input vacuum noise:
            \[
              \delta\dot{\mathbf{x}} = -A_{\mathrm{eff}}(\alpha)\,\delta\mathbf{x}
                + \sqrt{D}\,\xi(t),
            \]
            where \(\delta\mathbf{x} = (\delta X, \delta P)^T\),
            \(A_\mathrm{eff}\) is the linearized drift around the
            classical attractor, and \(D\) is set by the vacuum input
            (\(D = I\) for vacuum, \(D = e^{-2r}I\) along squeezed
            quadrature). <em>This is the Langevin equation that the OU
            machine in Note 07 turns into a Lyapunov sampler.</em>
          </p>
          """ + callout(
            "The bright-field limit is what makes optical computing "
            "feasible. We are working in the regime where the field "
            "amplitude is large enough that mean-field captures the "
            "dynamics, and small enough that quantum fluctuations are "
            "the dominant noise. This is the regime of every analog "
            "optical processor — CIM, OU machine, photonic Ising."
          ),
         ["Mean field: \\(\\dot\\alpha\\) deterministic + nonlinearity",
          "Fluctuations: linear SDE driven by vacuum (or squeezed) noise",
          "Defines the regime of all bench-scale optical computing"]),
        ("cavity-decay", "Interactive: Driven-Cavity Decay", r"""
          <p class="lede">
            With drive turned off, an initial coherent state
            \(\lvert\alpha_0\rangle\) decays as
            \(\alpha(t) = \alpha_0 e^{-\kappa t/2}\) — a simple
            exponential ringdown. With drive, the cavity reaches a
            non-zero steady state \(\alpha_\mathrm{ss} = \varepsilon/\kappa\).
          </p>
          """ + widget_shell(
            anchor="cavity-decay",
            title="Driven cavity ringdown / steady-state",
            blurb=(
              "Slide cavity decay <em>κ</em>, drive amplitude "
              "<em>ε</em>, and toggle the drive. Phase-space trajectory "
              "shows |α(t)|; the full curve is the analytic solution "
              "<em>α</em>(t) = (ε/κ)(1 − e<sup>−κt</sup>) + α₀ e<sup>−κt</sup>."
            ),
            controls_html=(
              slider(var="cd-kappa", label="decay κ", min_=0.1, max_=3.0,
                     step=0.05, value=1.0, fmt="{:.2f}") + "\n" +
              slider(var="cd-eps", label="drive ε", min_=0.0, max_=3.0,
                     step=0.05, value=1.5, fmt="{:.2f}") + "\n" +
              slider(var="cd-alpha0", label="|α₀|", min_=0.0, max_=4.0,
                     step=0.05, value=2.0, fmt="{:.2f}")
            ),
            canvas_html=svg_el("cavity-decay", w=520, h=280),
            readout_html=(
              '<div>Steady-state |α_ss|² = <span id="cd-ss">—</span>  '
              '(half-decay time t<sub>1/2</sub> = <span id="cd-thalf">—</span>)</div>'
            ),
          ) + r"""
          """,
         ["Free decay: \\(\\alpha(t) = \\alpha_0 e^{-\\kappa t/2}\\)",
          "Driven steady state: \\(\\alpha_\\mathrm{ss} = \\varepsilon/\\kappa\\)",
          "Half-life: \\(t_{1/2} = \\ln 2 / \\kappa\\)"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/CIM_description/CIM_description.pdf">CIM_description.pdf</a> — primary source for Lindblad form</td></tr>
            <tr><td>Reference</td><td>Gardiner &amp; Zoller, <em>Quantum Noise</em> (3rd ed., Springer, 2004), Chs. 3, 5</td></tr>
            <tr><td>Reference</td><td>Walls &amp; Milburn, <em>Quantum Optics</em>, Ch. 5–7</td></tr>
            <tr><td>Paper</td><td>Gardiner &amp; Collett, "Input and output in damped quantum systems", <em>PRA</em> <strong>31</strong>, 3761 (1985)</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §05 — Homodyne detection and
            continuous measurement. The output field is what we
            measure; we need to know what shot noise looks like and
            how feedback enters.
          </p>
          """,
         ["Gardiner &amp; Zoller is the standard open-systems text",
          "Original I/O paper: Gardiner-Collett 1985",
          "Continue: Note 05 (homodyne)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: cavity decay (driven, exponential ringdown) ----------
      (function () {
        var svg = document.getElementById('cavity-decay-svg');
        if (!svg) return;
        var kS = document.getElementById('cd-kappa');
        var eS = document.getElementById('cd-eps');
        var aS = document.getElementById('cd-alpha0');
        var kV = document.getElementById('cd-kappa-val');
        var eV = document.getElementById('cd-eps-val');
        var aV = document.getElementById('cd-alpha0-val');
        var ssSp = document.getElementById('cd-ss');
        var thalfSp = document.getElementById('cd-thalf');
        function draw() {
          var k = parseFloat(kS.value);
          var eps = parseFloat(eS.value);
          var a0 = parseFloat(aS.value);
          kV.textContent = k.toFixed(2);
          eV.textContent = eps.toFixed(2);
          aV.textContent = a0.toFixed(2);
          var W = 520, H = 280, pad = 50;
          var inner_w = W - 2*pad, inner_h = H - 2*pad;
          var TMAX = 8.0;
          var alpha_ss = eps / k;
          var maxA = Math.max(a0, alpha_ss) * 1.15 + 0.1;
          function xpos(t) { return pad + (t/TMAX) * inner_w; }
          function ypos(a) { return pad + inner_h - (a/maxA) * inner_h; }
          var html = '';
          html += '<line x1="' + pad + '" y1="' + (pad+inner_h) + '" x2="' + (W-pad) + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          html += '<line x1="' + pad + '" y1="' + pad + '" x2="' + pad + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          // SS line
          html += '<line x1="' + pad + '" y1="' + ypos(alpha_ss) + '" x2="' + (W-pad) + '" y2="' + ypos(alpha_ss) + '" stroke="#e8b96a" stroke-width="1" stroke-dasharray="4,3"/>';
          html += '<text x="' + (W-pad-8) + '" y="' + (ypos(alpha_ss)-4) + '" text-anchor="end" font-size="10" fill="#e8b96a">|α_ss| = ' + alpha_ss.toFixed(2) + '</text>';
          // curve: α(t) = α_ss + (α₀ - α_ss) e^{-κt/2}  (amplitude convention)
          var pts = [];
          for (var t = 0; t <= TMAX; t += 0.05) {
            var a = alpha_ss + (a0 - alpha_ss) * Math.exp(-k*t/2);
            pts.push(xpos(t) + ',' + ypos(Math.abs(a)));
          }
          html += '<polyline points="' + pts.join(' ') + '" fill="none" stroke="#79c79f" stroke-width="2"/>';
          // half-life marker
          var thalf = Math.log(2)/k;
          if (a0 > alpha_ss) {
            var a_half = alpha_ss + (a0 - alpha_ss) * 0.5;
            html += '<circle cx="' + xpos(thalf) + '" cy="' + ypos(a_half) + '" r="4" fill="#fff"/>';
            html += '<text x="' + (xpos(thalf)+6) + '" y="' + (ypos(a_half)-4) + '" font-size="10" fill="#fff">t₁/₂</text>';
          }
          // axes labels
          html += '<text x="' + (W/2) + '" y="' + (H-pad/2 + 12) + '" text-anchor="middle" font-size="11" fill="#888">time t  (in units of 1/κ_ref)</text>';
          html += '<text x="' + (pad/2) + '" y="' + (H/2) + '" text-anchor="middle" font-size="11" fill="#888" transform="rotate(-90 ' + (pad/2) + ' ' + (H/2) + ')">|α(t)|</text>';
          // tick labels
          for (var t of [0, 1, 2, 4, 6, 8]) {
            html += '<text x="' + xpos(t) + '" y="' + (pad+inner_h+15) + '" text-anchor="middle" font-size="10" fill="#888">' + t + '</text>';
          }
          svg.innerHTML = html;
          ssSp.textContent = (alpha_ss*alpha_ss).toFixed(3);
          thalfSp.textContent = thalf.toFixed(3);
        }
        kS.addEventListener('input', draw);
        eS.addEventListener('input', draw);
        aS.addEventListener('input', draw);
        draw();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Note 05: Homodyne & Continuous Measurement
# ---------------------------------------------------------------------------

NOTE_05 = {
    "filename": "05_homodyne_continuous_measurement.html",
    "title": "Homodyne Detection and Continuous Measurement",
    "description": "Balanced homodyne, shot noise, sub-shot-noise sensing with squeezing, and the Wiseman-Milburn measurement-feedback formalism.",
    "eyebrow": "Quantum Optics · Measurement",
    "h1": "Homodyne Detection and Continuous Measurement",
    "subtitle": "How quadratures get read out, where the shot-noise floor comes from, and what changes when you close the measurement-feedback loop. The single most important measurement modality for the Coherent Ising Machine and the OU machine.",
    "covers": [
        "Balanced homodyne setup: signal + LO on a 50/50 beam splitter",
        "Photocurrent ↔ X-quadrature; the shot-noise floor",
        "Phase-resolved homodyne vs heterodyne",
        "Sub-shot-noise sensing with squeezed-light injection",
        "Continuous measurement: the stochastic master equation",
        "Wiseman-Milburn measurement feedback: closing the loop",
    ],
    "nav": [
        ("balanced-homodyne", "Balanced Homodyne"),
        ("shot-noise", "Shot Noise"),
        ("phase-vs-het", "Phase vs Het."),
        ("sub-shot", "Sub-Shot-Noise"),
        ("homodyne-quadrature", "Quadrature Lab"),
        ("sme", "SME"),
        ("wm-feedback", "Wiseman-Milburn"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("balanced-homodyne", "The Balanced Homodyne Setup", r"""
          <p class="lede">
            Take a signal field \(a_\mathrm{sig}\) (the cavity output
            from Note 04) and combine it with a strong "local
            oscillator" coherent field \(a_\mathrm{LO}\) at a 50/50 beam
            splitter. Detect the two output ports with photodetectors;
            subtract the photocurrents.
          </p>
          <p>
            The two output operators are
            \(b_\pm = (a_\mathrm{sig} \pm a_\mathrm{LO})/\sqrt{2}\). The
            corresponding photon-number operators are
            \(b_\pm^\dagger b_\pm = \tfrac{1}{2}(a_\mathrm{sig}^\dagger a_\mathrm{sig}
            + a_\mathrm{LO}^\dagger a_\mathrm{LO}
            \pm a_\mathrm{sig}^\dagger a_\mathrm{LO} \pm a_\mathrm{LO}^\dagger a_\mathrm{sig})\).
            The difference is
            \[
              i(t) \;\propto\; b_+^\dagger b_+ - b_-^\dagger b_-
              = a_\mathrm{sig}^\dagger a_\mathrm{LO} + a_\mathrm{LO}^\dagger a_\mathrm{sig}.
            \]
            Treating the LO classically (\(a_\mathrm{LO} = \alpha_\mathrm{LO}\),
            \(\lvert\alpha_\mathrm{LO}\rvert\) large), the photocurrent is
            \[
              i(t) = \lvert\alpha_\mathrm{LO}\rvert\,
              \bigl(a_\mathrm{sig}\,e^{-i\phi_\mathrm{LO}}
                + a_\mathrm{sig}^\dagger\,e^{+i\phi_\mathrm{LO}}\bigr).
            \]
            For \(\phi_\mathrm{LO} = 0\) this is
            \(\sqrt{2}\,\lvert\alpha_\mathrm{LO}\rvert\,X_\mathrm{sig}\) — the
            X-quadrature of the signal, amplified by the LO.
          </p>
          """ + callout(
            "The LO acts as a phase reference and a noiseless gain. "
            "Because we subtract the two arms, the LO's classical "
            "amplitude noise cancels and we are left with the "
            "interference cross-term — which carries the signal "
            "quadrature times \\(|\\alpha_\\mathrm{LO}|\\)."
          ),
         ["Balanced homodyne = signal + LO mixed on 50/50 BS",
          "Subtraction cancels LO classical noise",
          "Photocurrent measures X-quadrature × LO amplitude"]),
        ("shot-noise", "The Shot-Noise Floor", r"""
          <p>
            Even with vacuum on the signal port (\(a_\mathrm{sig} = 0\) +
            vacuum fluctuation), the photocurrent has nonzero variance:
            \[
              \mathrm{Var}\,i \;\propto\; \lvert\alpha_\mathrm{LO}\rvert^2
              \cdot \langle X_\mathrm{vac}^2\rangle
              = \lvert\alpha_\mathrm{LO}\rvert^2 \cdot \tfrac{1}{2}.
            \]
            This is the <strong>shot-noise floor</strong> — the
            fundamental noise level that any homodyne setup hits when
            the signal is vacuum. It is set by the LO photon-number
            statistics; per integration time \(T\),
            \(\sigma_i \sim \sqrt{\eta\,\bar\Phi_\mathrm{LO}\,T}\) for
            detector quantum efficiency \(\eta\) and LO photon flux
            \(\bar\Phi_\mathrm{LO}\).
          </p>
          <p>
            For our purposes (CIM/OU machine on a typical bench): with
            a pulse train at GHz repetition rate, a per-pulse photon
            flux \(\sim 10^9\) and integration time \(\sim 1\) ns gives
            \(\sigma_\mathrm{meas} \sim 1\) (per shot, in units of
            \(x_\mathrm{RMS}\)). This is the
            <code>σ_meas</code> parameter in
            <a href="07_thermodynamic_la_ou_machine.html">Note 07</a>.
          </p>
          """,
         ["Shot noise = vacuum fluctuation on the signal port",
          "Floor: σ ∼ √(η Φ_LO T)",
          "Sub-shot-noise sensing requires squeezed signal"]),
        ("phase-vs-het", "Phase-Resolved Homodyne vs Heterodyne", r"""
          <p>
            Tune the LO phase \(\phi_\mathrm{LO}\) and the photocurrent
            measures
            \(X_{\phi_\mathrm{LO}} = \cos\phi\,X + \sin\phi\,P\) — any
            quadrature you want. Phase-resolved homodyne (with stable
            \(\phi_\mathrm{LO}\)) projects onto a chosen quadrature.
          </p>
          <p>
            Heterodyne detection lets the LO be at a frequency
            \(\omega_\mathrm{LO} \neq \omega_\mathrm{sig}\). The
            photocurrent oscillates at the difference frequency, and
            sweeping \(\phi_\mathrm{LO}\) over a 2π range gives
            simultaneously partial information about both quadratures
            — at the cost of an extra factor of 2 in the noise
            (Arthurs-Kelly bound). Phase-resolved homodyne is the
            quantum-limited choice when you know which quadrature you
            care about.
          </p>
          """,
         ["Tune \\(\\phi_\\mathrm{LO}\\) → choose which quadrature",
          "Heterodyne: simultaneous \\(X, P\\) at 2× the noise penalty",
          "MFB-CIM uses phase-resolved homodyne on X"]),
        ("sub-shot", "Sub-Shot-Noise Sensing", r"""
          <p>
            Inject squeezed vacuum on the homodyne signal port. The
            X-quadrature noise is now
            \(\langle X^2\rangle = \tfrac{1}{2}e^{-2r}\) — below the
            vacuum level. Photocurrent variance drops by \(e^{-2r}\)
            on the squeezed quadrature.
          </p>
          <p>
            On a real bench, the achievable squeezing-after-detection
            is bounded by detection efficiency \(\eta\):
            \(e^{-2r_\mathrm{eff}} = \eta e^{-2r} + (1-\eta)\). At
            \(\eta = 0.95\), even infinite-r squeezing produces only
            \(e^{-2r_\mathrm{eff}} = 0.05\) → 13 dB. Detection loss
            is the binding constraint, not the squeezer.
          </p>
          """ + callout(
            "Squeezing alone is a constant-factor (in r) variance "
            "reduction on a homodyne measurement. For ill-conditioned "
            "linear-algebra problems where the variance has additional "
            "κ-dependence, the squeezing factor doesn't address the "
            "κ scaling. This was Direction B's killshot result for "
            "the OU machine."
          ),
         ["Squeezed input → e^(−2r) on photocurrent variance",
          "Detection loss caps usable r",
          "No κ-dependence — Direction B's killshot"]),
        ("homodyne-quadrature", "Interactive: Homodyne Quadrature Selection", r"""
          <p class="lede">
            Slide LO phase \(\varphi\). The homodyne photocurrent
            measures the rotated quadrature
            \(X_\varphi = X\cos\varphi + P\sin\varphi\). For a coherent
            state, the histogram of measured \(X_\varphi\) is a
            Gaussian; for squeezed input, the variance dips below the
            shot-noise floor when \(\varphi\) hits the squeezed
            quadrature's angle.
          </p>
          """ + widget_shell(
            anchor="homodyne-quadrature",
            title="LO phase scan with optional squeezed input",
            blurb=(
              "Histogram of 600 random samples of <em>X<sub>φ</sub></em>. "
              "Toggle squeezing on the input to see variance dip below "
              "the shot-noise floor (dashed) at <em>φ</em> = 0. "
              "Anti-squeezing (variance above floor) at <em>φ</em> = π/2."
            ),
            controls_html=(
              slider(var="hd-phi", label="LO phase φ", min_=0,
                     max_=3.14, step=0.05, value=0.0, fmt="{:.2f}") + "\n" +
              slider(var="hd-r", label="signal squeeze r", min_=0,
                     max_=1.2, step=0.05, value=0.0, fmt="{:.2f}")
            ),
            buttons_html='<button id="hd-resample">Resample</button>',
            canvas_html=svg_el("homodyne-quadrature", w=520, h=300),
            readout_html=(
              '<div>Sample variance: <span id="hd-var">—</span> &nbsp; '
              'Shot-noise floor: <span id="hd-snf">0.500</span></div>'
              '<div>dB vs SNL: <span id="hd-db">—</span></div>'
            ),
          ) + r"""
          """,
         ["LO phase φ selects measured quadrature \\(X_\\varphi\\)",
          "Squeezed input dips below SNL at the right φ",
          "π/2 phase shift swaps squeezed ↔ anti-squeezed"]),
        ("sme", "Continuous Measurement: The Stochastic Master Equation", r"""
          <p>
            A homodyne detector running continuously gives a
            time-resolved photocurrent \(i(t)\). The conditional state
            of the cavity, given the trajectory of the photocurrent,
            obeys the <strong>stochastic master equation</strong>:
            \[
              d\rho_c
              = -i[H,\rho_c]\,dt
                + \mathcal{D}[L]\rho_c\,dt
                + \mathcal{H}[L]\rho_c\,dW(t),
            \]
            where \(L = \sqrt{2\kappa}\,a\), \(dW\) is a Wiener
            increment, and \(\mathcal{H}[L]\rho = L\rho + \rho L^\dagger
            - \mathrm{Tr}(L\rho + \rho L^\dagger)\rho\) is the
            measurement-conditioning superoperator. Averaging over the
            measurement record recovers the unconditional Lindblad
            equation.
          </p>
          <p>
            Practically: the SME is the level of detail at which we
            simulate measurement-feedback CIM dynamics in Strawberry
            Fields or QuTiP. For Gaussian states it reduces to a
            stochastic ODE on the mean and covariance — that's the
            classical-limit form we use in Note 06.
          </p>
          """,
         ["SME: density operator conditioned on photocurrent",
          "Wiener-driven; averaging recovers Lindblad",
          "For Gaussian states: SDE on mean + covariance"]),
        ("wm-feedback", "Wiseman-Milburn Measurement Feedback", r"""
          <p>
            Now close the loop: feed the photocurrent \(i(t)\) back into
            the system through a control Hamiltonian
            \(H_\mathrm{ctrl}(t) = \lambda(t) F\), where \(\lambda(t)\)
            is a function of the measurement record (e.g.\ a linear
            filter on \(i(t)\)) and \(F\) is some operator (typically a
            quadrature, implemented optically by an EOM). Wiseman &amp;
            Milburn (1993, 1994) showed that the unconditional
            evolution of the system (averaged over the measurement
            outcomes) is described by a modified Lindblad equation
            with effective Hamiltonian and dissipator that depend on
            the feedback strength.
          </p>
          <p>
            For our purposes (CIM, OU machine), the relevant fact is:
            in the bright-field limit, MFB reduces to a classical
            stochastic-feedback control problem on the mean, with the
            FPGA implementing the linear feedback law and the
            shot-noise floor entering as additional input noise. The
            "MFB envelope" derived in Direction A —
            \(f_\mathrm{eff} = \eta\,e^{-\gamma\tau}\) —
            comes from this analysis applied to underdamped symplectic
            dynamics. (Note 07 explains why the overdamped variant has
            a different envelope structure.)
          </p>
          """,
         ["MFB: photocurrent → control field via FPGA",
          "Wiseman-Milburn 1993, 1994: rigorous formalism",
          "Bright-field limit: classical stochastic feedback control"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/homodyne.pdf">homodyne.pdf</a> — figures of the standard balanced setup</td></tr>
            <tr><td>Reference</td><td>Wiseman &amp; Milburn, <em>Quantum Measurement and Control</em> (Cambridge, 2010), Chs. 4–7</td></tr>
            <tr><td>Paper</td><td>Wiseman &amp; Milburn, "Quantum theory of optical feedback via homodyne detection", <em>PRL</em> <strong>70</strong>, 548 (1993)</td></tr>
            <tr><td>Reference</td><td>Note 07, §<em>Hardware Envelope</em> — overdamped specialization (the corrected envelope)</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §06 — OPO, DOPO, and the
            Coherent Ising Machine. With Notes 01–05 in hand, the
            full MFB-CIM is just an assembly of components.
          </p>
          """,
         ["WM 1993 is the original homodyne-feedback paper",
          "WM textbook (2010) is the modern reference",
          "Continue: Note 06 (CIM, the headline)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: homodyne quadrature with optional squeezing ----------
      (function () {
        var svg = document.getElementById('homodyne-quadrature-svg');
        if (!svg) return;
        var phS = document.getElementById('hd-phi');
        var rS = document.getElementById('hd-r');
        var phV = document.getElementById('hd-phi-val');
        var rV = document.getElementById('hd-r-val');
        var varSp = document.getElementById('hd-var');
        var dbSp = document.getElementById('hd-db');
        var resampleBtn = document.getElementById('hd-resample');
        var seed = 12345;
        function gauss() {
          var u = 0, v = 0;
          while(u===0) u = Math.random();
          while(v===0) v = Math.random();
          return Math.sqrt(-2*Math.log(u)) * Math.cos(2*Math.PI*v);
        }
        function draw() {
          var phi = parseFloat(phS.value);
          var r = parseFloat(rS.value);
          phV.textContent = phi.toFixed(2);
          rV.textContent = r.toFixed(2);
          // squeezed quadratures: Var(X)=½ e^{-2r}, Var(P)=½ e^{2r}
          // measured X_phi = X cos φ + P sin φ has variance:
          // Var(X_phi) = ½ (e^{-2r} cos²φ + e^{2r} sin²φ)  [for squeezed vacuum]
          // For coherent state: Var = 1/2
          var Vphi;
          if (r < 0.005) {
            Vphi = 0.5;
          } else {
            Vphi = 0.5 * (Math.exp(-2*r)*Math.cos(phi)*Math.cos(phi) + Math.exp(2*r)*Math.sin(phi)*Math.sin(phi));
          }
          // sample 600 measurements
          var samples = [];
          var sample_var = 0, sample_mean = 0;
          for (var i = 0; i < 600; i++) {
            var x = Math.sqrt(Vphi) * gauss();
            samples.push(x);
            sample_mean += x;
          }
          sample_mean /= 600;
          for (var i = 0; i < samples.length; i++) {
            var d = samples[i] - sample_mean;
            sample_var += d*d;
          }
          sample_var /= 600;
          // build histogram
          var W = 520, H = 300, pad = 50;
          var inner_w = W - 2*pad, inner_h = H - 2*pad - 24;
          var nb = 30;
          var XMIN = -3, XMAX = 3;
          var bins = new Array(nb).fill(0);
          for (var i = 0; i < samples.length; i++) {
            var idx = Math.floor((samples[i] - XMIN) / (XMAX - XMIN) * nb);
            if (idx >= 0 && idx < nb) bins[idx]++;
          }
          var maxCount = Math.max.apply(null, bins);
          var bw = inner_w / nb;
          var html = '';
          for (var k = 0; k < nb; k++) {
            var x0 = pad + k*bw;
            var bh = (bins[k]/maxCount) * inner_h;
            html += '<rect x="' + (x0+0.5) + '" y="' + (pad + inner_h - bh) + '" width="' + (bw-1) + '" height="' + bh + '" fill="#79c79f" opacity="0.65"/>';
          }
          // shot-noise floor reference Gaussian (Var = 1/2)
          var coherent_pts = [];
          for (var k = 0; k < nb; k++) {
            var x = XMIN + (k+0.5) * (XMAX - XMIN) / nb;
            // expected count for coherent: 600 * (XMAX-XMIN)/nb * gaussian_pdf(x; var=1/2)
            var pdf = Math.exp(-x*x/(2*0.5)) / Math.sqrt(2*Math.PI*0.5);
            var count = 600 * pdf * (XMAX-XMIN)/nb;
            var x0 = pad + k*bw + bw/2;
            var py = pad + inner_h - (count/maxCount)*inner_h;
            coherent_pts.push(x0 + ',' + py);
          }
          html += '<polyline points="' + coherent_pts.join(' ') + '" fill="none" stroke="#888" stroke-width="1.5" stroke-dasharray="4,3"/>';
          // axes
          html += '<line x1="' + pad + '" y1="' + (pad+inner_h) + '" x2="' + (W-pad) + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          html += '<text x="' + (W/2) + '" y="' + (H-12) + '" text-anchor="middle" font-size="11" fill="#888">measured X_φ</text>';
          html += '<text x="' + pad + '" y="' + (pad+inner_h+15) + '" font-size="10" fill="#888">' + XMIN + '</text>';
          html += '<text x="' + (W-pad) + '" y="' + (pad+inner_h+15) + '" text-anchor="end" font-size="10" fill="#888">' + XMAX + '</text>';
          html += '<text x="' + (W-pad-160) + '" y="' + (pad+12) + '" font-size="10" fill="#888">solid: actual histogram (Var=' + sample_var.toFixed(3) + ')</text>';
          html += '<text x="' + (W-pad-160) + '" y="' + (pad+25) + '" font-size="10" fill="#888">dashed: shot-noise floor (Var=0.500)</text>';
          svg.innerHTML = html;
          varSp.textContent = sample_var.toFixed(4);
          var db = (Vphi < 0.5) ? -10*Math.log10(0.5/Vphi) : 10*Math.log10(Vphi/0.5);
          dbSp.textContent = (db > 0 ? '+' : '') + db.toFixed(2) + ' dB ' + (db < 0 ? '(below SNL — squeezed!)' : (db > 0.1 ? '(above SNL — anti-squeezed)' : '(at SNL)'));
        }
        phS.addEventListener('input', draw);
        rS.addEventListener('input', draw);
        if (resampleBtn) resampleBtn.addEventListener('click', draw);
        draw();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Note 06: OPO/DOPO/CIM (HEADLINE — User requirement 1)
# ---------------------------------------------------------------------------

NOTE_06 = {
    "filename": "06_opo_dopo_cim.html",
    "title": "OPO, DOPO, and the Coherent Ising Machine",
    "description": "Optical parametric oscillator dynamics, the DOPO bifurcation, and how a network of measurement-feedback DOPOs solves Ising minimization. When is the machine quantum, when classical, and what does the bifurcation actually do?",
    "eyebrow": "Quantum Optics · Coherent Ising Machine",
    "h1": "OPO, DOPO, and the Coherent Ising Machine",
    "subtitle": "The headline applied note. We assemble the OPO physics from Note 03, the open-system formalism from Note 04, and the homodyne feedback from Note 05 into the canonical Inagaki/Yamamoto measurement-feedback CIM. We also confront — explicitly — when the machine is operating in a quantum regime versus a purely classical one.",
    "covers": [
        "OPO: χ⁽²⁾ medium in a cavity, threshold dynamics",
        "DOPO bifurcation: pump depletion as cubic saturation",
        "Quantum vs classical regime: where the line lives",
        "Network of DOPOs with measurement feedback (Inagaki / Marandi)",
        "Mapping onto Ising minimization: the heuristic argument",
        "The discrete-time round-trip update equation, annotated",
        "State of the art: 2k → 100k spins; what these machines actually solve",
    ],
    "nav": [
        ("opo-basics", "OPO Basics"),
        ("below-threshold", "Below Threshold"),
        ("dopo", "DOPO Bifurcation"),
        ("quantum-classical", "Quantum vs Classical"),
        ("mfb-network", "MFB Network"),
        ("time-multiplexing", "Time-Multiplex"),
        ("ising-mapping", "Ising Mapping"),
        ("qubo-mappings", "QUBO &amp; Beyond"),
        ("rosetta", "Update Rosetta"),
        ("comparison", "vs Annealers / SA"),
        ("scaling", "Scaling"),
        ("open-questions", "Open Questions"),
        ("sota", "State of the Art"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("opo-basics", "OPO: A χ⁽²⁾ Medium in a Cavity", r"""
          <p class="lede">
            Place a periodically-poled LiNbO₃ crystal (Note 03) inside
            a fiber-ring or free-space cavity (Note 04). Pump it at
            \(2\omega\) with a classical coherent field of amplitude
            \(\beta_p\). The intracavity signal mode \(a\) at \(\omega\)
            obeys, in the rotating frame and undepleted-pump
            approximation,
            \[
              \dot a = -\kappa\, a + g\,\beta_p\, a^\dagger
                - \sqrt{2\kappa}\,a_\mathrm{in}.
            \]
            The first term is cavity decay; the second is parametric
            amplification (the squeezing-generation term from Note 03);
            the third is vacuum input from the output mirror.
          </p>
          <p>
            Linear stability of the steady state \(a = 0\): the
            characteristic exponents are \(\pm(g\lvert\beta_p\rvert - \kappa)\).
            For \(g\lvert\beta_p\rvert < \kappa\) (below threshold),
            both modes decay — the cavity is a squeezed-vacuum source.
            For \(g\lvert\beta_p\rvert > \kappa\) (above threshold),
            one mode grows exponentially until pump depletion
            saturates it. <strong>The OPO threshold is exactly when
            parametric gain equals cavity loss.</strong>
          </p>
          """,
         ["OPO = χ⁽²⁾ + cavity, pumped at \\(2\\omega\\)",
          "Threshold: \\(g\\lvert\\beta_p\\rvert = \\kappa\\)",
          "Below: squeezing source. Above: oscillation."]),
        ("below-threshold", "Below Threshold: The Squeezed-Vacuum Source", r"""
          <p class="lede">
            Below threshold, an OPO is the canonical workhorse for
            generating <em>squeezed vacuum</em> — a state with one
            quadrature variance below the shot-noise floor and the
            other above (Note 03 introduced the squeeze operator
            \(S(r)\); here we generate it physically).
          </p>
          <p>
            Linearizing the intracavity equations around \(a = 0\)
            and solving for the steady-state output via input-output
            (Note 04, Gardiner-Collett),
            \[
              \langle X_\mathrm{out}^2 \rangle
                = \frac{1}{4}\,\frac{1 - \eta\,\Lambda}{1 + \Lambda},
              \qquad
              \langle P_\mathrm{out}^2 \rangle
                = \frac{1}{4}\,\frac{1 + \eta\,\Lambda}{1 - \Lambda},
            \]
            where \(\Lambda = (g\lvert\beta_p\rvert/\kappa)^2 = p^2\) and
            \(\eta\) is the detection efficiency (1 for perfect
            detection). At threshold \(p \to 1\), the squeezed
            quadrature variance \(\to 0\) and the anti-squeezed
            quadrature \(\to \infty\) — perfect EPR correlations are a
            critical phenomenon of the OPO.
          </p>
          <p>
            <em>State of the art</em>: 15 dB squeezing demonstrated by
            Vahlbruch et al.\ 2016 with periodically-poled KTP at
            \(\eta \approx 0.99\), corresponding to
            \(\langle X_\mathrm{out}^2\rangle / (1/4) \approx 0.032\) —
            a 30× variance reduction. This is the working substrate
            for gravitational-wave squeezed-light injection in LIGO.
          </p>
          """ + callout(
            "Below-threshold OPO and above-threshold DOPO are <em>the same "
            "device</em> with the pump knob turned. The bifurcation at "
            "threshold is therefore not just a computational primitive — "
            "it is the connection between two operational regimes that "
            "have utterly different applications (squeezed light for "
            "metrology vs.\\ Ising spins for optimization)."
          ),
         ["Below threshold: linearized Langevin = squeezed vacuum",
          "Squeezed variance \\(\\to 0\\) as \\(p \\to 1\\) — critical",
          "Vahlbruch 2016: 15 dB demonstrated"]),
        ("dopo", "The DOPO Bifurcation", r"""
          <p>
            For a <em>degenerate</em> OPO (signal frequency = idler
            frequency, same mode), the gain term in the Hamiltonian is
            \(\sim a^{\dagger 2}\) — same as the squeeze operator
            generator. Above threshold, pump depletion enters and the
            mean-field equation becomes (e.g. Drummond, McNeil, Walls
            1980):
            \[
              \dot\alpha = (p - 1)\alpha - \mu\lvert\alpha\rvert^2 \alpha
                + \xi(t),
            \]
            where \(p = g\lvert\beta_p\rvert/\kappa\) is the normalized
            pump (1 at threshold), \(\mu \propto g^2/\kappa\) is the
            saturation coefficient, and \(\xi(t)\) is the linearized
            quantum noise (vacuum input). The dynamics is exactly the
            normal form of a <strong>pitchfork bifurcation</strong>.
          </p>
          <p>
            Below threshold (\(p < 1\)): the only stable fixed point is
            \(\alpha = 0\) — squeezed vacuum. Above threshold (\(p > 1\)):
            two stable fixed points at \(\alpha = \pm\sqrt{(p-1)/\mu}\),
            and the unstable origin. The cubic saturation
            \(-\mu\lvert\alpha\rvert^2\alpha\) is what bounds the
            oscillation amplitude. Because the gain term respects
            \(\alpha \to -\alpha\), the steady-state phase is
            spontaneously selected — by quantum noise during the
            crossing of threshold.
          </p>
          """ + callout(
            "The DOPO is a noise-driven coin flip. The phase the "
            "device commits to is selected by the quantum-noise "
            "fluctuation that happens to be largest at the moment "
            "the system crosses threshold. This noise-driven phase "
            "selection is the entire computational primitive of the "
            "CIM."
          ) + math_details("Detailed math: pitchfork normal form from pump depletion", r"""
            <p>
              Start with the two-mode Hamiltonian for a degenerate
              parametric amplifier with a depleted pump:
              \[
                H = \omega\, a^\dagger a + 2\omega\, b^\dagger b
                  + \tfrac{i}{2} g\,(a^{\dagger 2} b - a^{2} b^\dagger).
              \]
              The Heisenberg equations, going to the rotating frame
              and adding cavity decay \(\kappa\) to the signal mode and
              \(\kappa_p\) to the pump:
              \[
                \dot a = -\kappa\, a + g\,a^\dagger b, \qquad
                \dot b = -\kappa_p\,b - \tfrac{1}{2} g\,a^2 + \kappa_p\beta_\mathrm{in}.
              \]
              Adiabatically eliminate the pump (\(\kappa_p \gg \kappa\),
              fast pump): \(b \approx \beta_\mathrm{in} - g a^2 / (2\kappa_p)\).
              Substitute back into \(\dot a\):
              \[
                \dot a = -\kappa\, a + g\, a^\dagger \beta_\mathrm{in}
                       - \frac{g^2}{2\kappa_p}\,a^\dagger a^2.
              \]
              For a real pump amplitude this is a real-coefficient
              equation in \(a\); on a single quadrature
              \(\alpha = \langle (a + a^\dagger)/\sqrt{2}\rangle\) we get
              \[
                \dot\alpha = -\kappa\,\alpha + g\beta_\mathrm{in}\,\alpha
                           - \frac{g^2}{2\kappa_p}\,\alpha^3.
              \]
              Rescale time by \(\kappa^{-1}\) and define
              \(p \equiv g\beta_\mathrm{in}/\kappa\) and
              \(\mu \equiv g^2/(2\kappa\kappa_p)\) to land on the
              dimensionless form
              \(\dot\alpha = (p-1)\alpha - \mu\alpha^3\), the canonical
              normal form of the supercritical pitchfork. The
              fixed-point equation \((p-1)\alpha = \mu\alpha^3\) gives
              \(\alpha = 0\) (always) plus
              \(\alpha = \pm\sqrt{(p-1)/\mu}\) for \(p > 1\).
            </p>
          """) + r"""
          """ + widget_shell(
            anchor="dopo-bifurcation",
            title="Interactive: DOPO bifurcation",
            blurb=(
              "Slide the normalized pump <em>p</em>. Below threshold "
              "(<em>p</em> &lt; 1) only the origin is stable — the cavity "
              "is a squeezed-vacuum source. Above threshold the origin "
              "becomes unstable and two new fixed points "
              "<em>α</em> = ±√((<em>p</em>−1)/<em>μ</em>) emerge. The "
              "noise cloud at <em>p</em> = 1 is what selects which one wins."
            ),
            controls_html=(
              slider(var="dopo-p", label="pump p / p_th", min_=0, max_=3,
                     step=0.01, value=0.6, fmt="{:.2f}") + "\n" +
              slider(var="dopo-mu", label="saturation μ", min_=0.05, max_=1.5,
                     step=0.01, value=0.3, fmt="{:.2f}") + "\n" +
              slider(var="dopo-noise", label="noise level √D", min_=0.01,
                     max_=0.4, step=0.005, value=0.08, fmt="{:.3f}")
            ),
            canvas_html=canvas_el("dopo-bifurcation", w=520, h=320),
            readout_html=(
              '<span id="dopo-bifurcation-text">'
              'Below threshold — origin stable, vacuum is squeezed.'
              '</span>'
            ),
          ) + r"""
          """,
         ["DOPO mean-field = pitchfork bifurcation",
          "Two stable phases (\\(\\pm\\)) above threshold",
          "Quantum noise selects which phase wins",
          "Adiabatic pump elimination ⇒ \\(\\dot\\alpha = (p-1)\\alpha - \\mu\\alpha^3\\)"]),
        ("quantum-classical", "When Is the CIM Quantum, When Is It Classical?", r"""
          <p>
            This is the question the CIM literature has spent two
            decades arguing about. The honest answer has three
            ingredients:
          </p>
          <ol>
            <li><strong>Far above threshold</strong>
              (\(p \gg 1, \lvert\alpha\rvert \gg 1\)): the field is
              bright, fluctuations are a small perturbation around the
              mean, mean-field theory is exact to leading order in
              \(1/\lvert\alpha\rvert\). The dynamics is operationally
              <em>classical</em>: it can be simulated by an SDE with
              the same equations of motion, no Hilbert space needed.</li>
            <li><strong>Far below threshold</strong>
              (\(p \ll 1, \lvert\alpha\rvert \to 0\)): the field is
              vacuum-fluctuation-scale; the full Lindblad master
              equation is needed; entanglement and squeezing are
              intrinsically non-classical features. The cavity is in a
              squeezed-vacuum state.</li>
            <li><strong>At threshold</strong> (\(p \approx 1\)): both
              limits fail. The system is sensitive to a finite (\(O(1)\))
              number of quantum-fluctuation noise events, which then
              get amplified by the pitchfork instability into
              macroscopic phase commitments. This is where the
              "quantum advantage" arguments live.</li>
          </ol>
          <p>
            The empirical evidence so far (Hamerly et al.\ 2018, Honjo
            et al.\ 2021, Marandi et al.\ ongoing): for the Ising
            problems CIMs have been benchmarked on,
            <em>classical-noise-driven simulators of the same equations
            of motion solve them just as well as the actual machines.</em>
            Whether there exist problem classes where the genuine
            quantum noise at threshold outperforms classical noise
            (e.g.\ via tunneling through saddle points) remains
            open. That's the live research question, not a settled
            claim.
          </p>
          """ + callout(
            'Don\'t conflate &ldquo;the dynamics involves quantum optics&rdquo; '
            'with &ldquo;the device offers a quantum computational '
            'advantage&rdquo;. The first is uncontroversial. The second is '
            'an open empirical question — and the answer is currently '
            '<em>&ldquo;no, on the problems tested so far&rdquo;</em>.'
          ) + r"""
          <p>
            <em>Where does the line live numerically?</em> A useful rule
            of thumb: the regime is operationally classical when
            \(\langle n\rangle \gtrsim 10\)–\(30\) per pulse —
            i.e.\ when the signal-to-noise ratio
            \(\sqrt{\langle n\rangle}/1 \gtrsim 3\)–\(5\). Below that,
            quantum-optical features (squeezing, single-photon
            statistics, entanglement across pulses) dominate. The
            interactive below lets you slide \(\langle n\rangle\) across
            this crossover.
          </p>
          """ + widget_shell(
            anchor="qc-regime",
            title="Interactive: where is the quantum/classical crossover?",
            blurb=(
              "Slide the photon number per pulse <em>n̄</em> on a log "
              "scale. The signal-to-vacuum ratio is √<em>n̄</em> : 1. The "
              "regime label flips when SNR crosses 3."
            ),
            controls_html=slider(var="qc-n", label="log₁₀ ⟨n⟩", min_=-2,
                                 max_=6, step=0.05, value=2.0,
                                 fmt="{:+.2f}"),
            canvas_html=svg_el("qc-regime", w=520, h=180),
            readout_html='<span id="qc-regime-text">SNR ≈ 10 — bright-field, classical SDE applies.</span>',
          ) + r"""
          """ + math_details("Detailed math: when does linearization around the mean become exact?", r"""
            <p>
              Write the field as \(a = \alpha + \delta a\), where
              \(\alpha = \langle a\rangle\) is the (large) classical
              mean and \(\delta a\) carries quantum fluctuations. The
              Heisenberg-Langevin equation for \(\delta a\) becomes
              <em>linear</em> with coefficients evaluated at \(\alpha\):
              \[
                \dot{\delta a} = M(\alpha)\,\delta a + \xi(t),
              \]
              where \(M(\alpha)\) is a \(2\times 2\) drift matrix
              capturing parametric gain plus cubic-saturation
              feedback. Nonlinear terms in \(\delta a\) are suppressed
              by \(1/\lvert\alpha\rvert\). For
              \(\lvert\alpha\rvert^2 \gg 1\) (i.e.\ many photons per
              pulse) those nonlinearities are a small perturbation, the
              linearized Gaussian description is exact, and
              <em>by a theorem of Mandel-Wolf</em> the dynamics is
              exactly reproducible by a classical SDE with Gaussian
              white noise of variance set by the vacuum.
            </p>
            <p>
              Below threshold, \(\lvert\alpha\rvert \to 0\), the
              linearization is around the unstable fixed point and
              \(M(\alpha)\) has positive eigenvalues for one quadrature
              and negative for the other — so the Gaussian
              approximation predicts squeezing (variance below the
              vacuum floor). At threshold, \(M(\alpha)\) has a zero
              eigenvalue and the linearization breaks down: cubic
              terms in \(\delta a\) become essential, and the dynamics
              is genuinely nonlinear.
            </p>
          """),
         ["Above threshold: classical SDE (Mandel-Wolf)",
          "Below threshold: full Lindblad / squeezing",
          "At threshold: nonlinear amplification of \\(O(1)\\) events",
          "Crossover empirically near \\(\\langle n\\rangle \\sim 10\\)"]),
        ("mfb-network", "Network of DOPOs with Measurement Feedback", r"""
          <p>
            One DOPO commits to one bit of phase. To compute, we need
            interactions between bits. The Inagaki/Yamamoto/Marandi
            <strong>measurement-feedback CIM</strong> (MFB-CIM)
            architecture, in pictures:
          </p>
          <pre style="background: var(--page-panel); padding: 0.8rem; border-radius: 0.3rem; font-size: 0.86rem; white-space: pre; overflow-x: auto;">
       ┌─────────────────────────────────────────────────────┐
       │  pulse loop (fiber ring + DOPO gain medium)         │
       │  N pulses circulating, one slot per spin            │
       └──────────────┬──────────────────────────────────────┘
                      │ tap output ~1%
                      ▼
          balanced homodyne   ──► measures X-quadrature x_i
                      │
                      ▼
          FPGA: compute MVM = J · x   (the Ising coupling)
                      │
                      ▼
          electro-optic modulator
          inject ε·MVM into next round-trip slot
                      │
                      ▼
          [also inject calibrated stochastic noise √D·ξ]
                      │
                      └─► back into the loop
          </pre>
          <p>
            Pulses are time-multiplexed in a fiber ring: each
            round-trip the FPGA reads the X-quadratures via balanced
            homodyne (Note 05), computes the Ising matrix-vector
            product \(\sum_j J_{ij} x_j\), and injects the result back
            into the next pulse via an electro-optic modulator. This
            <em>is</em> the spin-spin coupling — it lives in the
            digital feedback loop, not in the optics.
          </p>
          <p>
            Why time-multiplexed? You can fit \(N\) pulses
            (one per spin) into one fiber loop and the whole thing
            runs at the round-trip rate. The Honjo et al.\ 2021
            machine has \(N = 100{,}144\) — over 100k spins on a
            single fiber loop, all processed by one FPGA. The
            architecture is dimension-efficient in a way no
            spatially-multiplexed scheme is.
          </p>
          """ + widget_shell(
            anchor="cim-roundtrip",
            title="Interactive: 4-spin CIM round-trip",
            blurb=(
              "A miniature 4-spin chain with Heisenberg-style coupling. "
              "Press <em>Run</em> to step through 80 round-trips of the "
              "McMahon Euler update (AHC.py:131–133). The bars show "
              "pulse amplitudes; the trace below shows Ising energy "
              "<em>H</em> = −½ <em>s</em>ᵀ<em>J</em><em>s</em> "
              "decreasing as the system commits to a low-energy spin "
              "configuration."
            ),
            controls_html=(
              slider(var="cim-pump", label="pump rate", min_=0.005,
                     max_=0.05, step=0.001, value=0.02, fmt="{:.3f}") + "\n" +
              slider(var="cim-coupling", label="coupling ε", min_=0.005,
                     max_=0.08, step=0.001, value=0.03, fmt="{:.3f}") + "\n" +
              slider(var="cim-noise", label="noise √D", min_=0.0,
                     max_=0.1, step=0.002, value=0.04, fmt="{:.3f}")
            ),
            buttons_html=(
              '<button id="cim-roundtrip-run">Run</button>'
              '<button id="cim-roundtrip-step">Step</button>'
              '<button id="cim-roundtrip-reset">Reset</button>'
            ),
            canvas_html=svg_el("cim-roundtrip", w=520, h=320),
            readout_html=(
              '<div>Spin config: <span id="cim-roundtrip-spins">+ + + +</span></div>'
              '<div>Ising energy: <span id="cim-roundtrip-energy">0.000</span></div>'
              '<div>Round-trip: <span id="cim-roundtrip-step-num">0</span> / 80</div>'
            ),
          ) + r"""
          """,
         ["Time-multiplexed pulses = spins",
          "FPGA implements \\(\\sum_j J_{ij} x_j\\)",
          "EOM injection = spin-spin coupling",
          "Round-trip rate sets clock speed"]),
        ("time-multiplexing", "Time-Multiplexed Pulses: The Architecture", r"""
          <p class="lede">
            The fiber-loop CIM is not <em>N</em> separate cavities — it
            is one cavity holding <em>N</em> pulses. Understanding the
            timing budget is what makes the architecture intelligible.
          </p>
          <p>
            The Honjo-NTT 100k-spin machine uses a 5 km fiber ring
            (round-trip \(\tau_\mathrm{rt} \approx 25\,\mu\text{s}\))
            with pulses spaced at 200 ps — that fits \(\sim\)125,000
            time slots, of which 100,144 are used. The PPLN gain
            crystal is traversed once per round-trip; each pulse picks
            up gain proportional to the current pump amplitude. The
            FPGA budget per slot is a few ns (200 ps slot ⇒ FPGA must
            finish its part of the MVM faster than the pulse leaves
            the EOM zone).
          </p>
          """ + math_details("Detailed math: round-trip latency budget", r"""
            <p>
              Per round-trip the FPGA does \(O(N^2)\) multiply-accumulates
              for the dense Ising MVM, plus \(O(N)\) reads and writes
              from homodyne and to EOM driver. With pulses spaced
              \(\Delta\tau_\mathrm{slot}\) and total round-trip time
              \(\tau_\mathrm{rt} = N \Delta\tau_\mathrm{slot}\), the FPGA
              has \(\Delta\tau_\mathrm{slot}\) per spin to pipeline its
              MVM contribution. For \(N = 10^5, \Delta\tau_\mathrm{slot}
              = 200\) ps, that's \(2 \times 10^4\)
              multiply-accumulates per spin in \(2 \times 10^{-10}\) s
              — a sustained \(10^{14}\) MACS, hard but tractable on a
              top-tier FPGA. <strong>The latency budget is the
              load-bearing constraint of the entire architecture.</strong>
            </p>
            <p>
              The Honjo et al.\ paper reports their FPGA runs at 250
              MHz clock with parallelism \(\approx\) 250 lanes,
              giving \(6 \times 10^{10}\) MACS — they only achieve
              this because the \(J\) matrix is a sparse graph,
              not dense. Dense problems would saturate well below 100k.
            </p>
          """) + callout(
            "Time-multiplexing trades spatial expense (one waveguide per "
            "spin) for temporal expense (one round-trip per update). "
            "It's a win as long as the FPGA can keep up with the "
            "round-trip rate — and that constraint is precisely what "
            "Note 07's OU machine inherits."
          ),
         ["100k spins fit in one 5 km fiber ring",
          "Pulse slot \\(\\Delta\\tau \\approx 200\\,\\mathrm{ps}\\); RT \\(\\sim 25\\,\\mu\\)s",
          "FPGA latency = the load-bearing assumption"]),
        ("ising-mapping", "From Pulses to Ising Solutions", r"""
          <p>
            When each DOPO settles to ±1 (above threshold, after
            relaxation), the spin configuration
            \(s = (\mathrm{sgn}\,x_1, \dots, \mathrm{sgn}\,x_N)\) is
            the output. The quantity the dynamics minimizes — argued
            heuristically by Yamamoto and others — is the Ising
            energy
            \[
              H_\mathrm{Ising}(s) = -\tfrac{1}{2} s^T J s.
            \]
            The argument: each pulse's phase wants to align with the
            phase of \(\sum_j J_{ij} x_j\), which is the phase that
            maximizes coherent build-up; that is the phase that
            minimizes the local field \(-\sum_j J_{ij} s_j\) seen by
            spin \(i\), which collectively minimizes \(H_\mathrm{Ising}\).
          </p>
          <p>
            <em>Caveat:</em> the heuristic is not a proof. The
            machine is doing something like simulated bifurcation,
            where the pump is ramped from below to above threshold;
            the system commits to a low-energy attractor of an
            effective dynamical system that is closely related to —
            but not identical to — the Ising landscape.
            Amplitude-Heterogeneity-Correction (AHC, Leleu et al.\ 2019)
            and Chaotic-Amplitude-Control (CAC, Leleu et al.\ 2021)
            are post-hoc corrections that improve performance on
            hard instances. The McMahon Lab
            <a href="https://github.com/mcmahon-lab/cim-optimizer">cim-optimizer</a>
            implements all three variants.
          </p>
          """ + callout(
            "MAX-CUT on a graph with adjacency \\(A\\) maps to Ising "
            "with \\(J = -A\\). This is the encoding used in the "
            "<code>cim-optimizer</code> regression test "
            "(<code>experiments/exp01_cim_baseline.py</code>) which hits "
            "the ground state on a 16-spin Erdős-Rényi instance "
            "100% of the time."
          ),
         ["Output: \\(s = \\mathrm{sgn}\\,x\\) — bipolar spin string",
          "Heuristic: minimizes \\(-\\tfrac{1}{2}s^T J s\\)",
          "AHC/CAC = post-hoc fixes for amplitude heterogeneity"]),
        ("qubo-mappings", "QUBO, MAX-CUT, and the Encoding Overhead", r"""
          <p class="lede">
            Most combinatorial problems are not natively Ising; they
            reduce to Ising. The reduction comes with overhead — the
            number of physical spins per logical variable matters for
            whether the CIM beats a CPU.
          </p>
          <p>
            <strong>QUBO &harr; Ising</strong>. A 0/1 QUBO over
            \(z \in \{0,1\}^n\) with cost
            \(C(z) = z^T Q z\) maps to bipolar spins
            \(s = 2z - 1 \in \{\pm 1\}^n\) via
            \[
              C(z) = \tfrac{1}{4}\,s^T Q s + \tfrac{1}{4}\,(\mathbf{1}^T Q + Q\mathbf{1})\,s
                   + \tfrac{1}{4}\,\mathbf{1}^T Q \mathbf{1}.
            \]
            The diagonal of \(Q\) becomes a linear field
            \(h_i = \tfrac{1}{2}(\mathbf{1}^T Q)_i\); the off-diagonal
            becomes \(J_{ij} = \tfrac{1}{4}(Q_{ij} + Q_{ji})\). One
            logical bit ↔ one physical spin: zero overhead.
          </p>
          <p>
            <strong>MAX-CUT &harr; Ising</strong>. For a graph
            \(G = (V, E)\), maximizing \(\lvert\mathrm{cut}(s)\rvert\)
            corresponds to minimizing \(s^T A s / 2\) where \(A\) is
            the adjacency matrix, i.e.\ \(J = -A\). The
            <code>cim-optimizer</code> regression tests use exactly
            this convention. Again zero overhead.
          </p>
          <p>
            <strong>Beyond Ising: 3-SAT, TSP, …</strong> Lucas (2014)
            catalogs reductions for ~30 NP problems. Most introduce
            \(O(n)\)–\(O(n \log n)\) auxiliary spins per logical
            variable to encode constraints (e.g.\ TSP needs
            \(n^2\) spins for an \(n\)-city tour: a one-hot
            position-time matrix). For 3-SAT the overhead is roughly
            quadratic. <em>The CIM's 100k-spin scale becomes only a
            316-city TSP or a 100-variable 3-SAT instance after
            encoding.</em> This is the fine print on "100,000 spins".
          </p>
          """ + callout(
            "When CIM advocates and skeptics talk past each other, the "
            "encoding-overhead distinction is often the missing common "
            "ground. <em>MAX-CUT on dense graphs at N=100k</em> is "
            "genuinely impressive — but only a tiny minority of "
            "real-world problems reduce to MAX-CUT without inflating "
            "spin count by 100×."
          ),
         ["QUBO ↔ Ising: zero overhead",
          "MAX-CUT ↔ Ising: \\(J = -A\\), zero overhead",
          "TSP, 3-SAT, …: quadratic-or-worse overhead",
          "Lucas 2014 = the Ising-reduction catalog"]),
        ("rosetta", "The Rosetta Stone: Update Equation", r"""
          <p>
            The McMahon Lab <code>cim-optimizer</code>
            (<code>vendor/cim-optimizer/cim_optimizer/AHC.py</code>,
            lines 130–133) implements the discrete-time MFB-CIM as
            an explicit Euler step:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
MVM = x @ J                                          # FPGA matrix-vector multiply
x += time_step * (x * ((r[t] - 1) - mu * x_squared)) # gain - cubic saturation
x += time_step * eps[t] * (MVM * error_var)          # measurement-feedback injection
x += eps[t] * noise * (torch.rand(N) - 0.5)          # injected stochastic noise
          </pre>
          <p>
            And the Yamamoto-Inagaki continuous-time SDE this
            discretizes:
            \[
              \dot x_i = (p - 1)\,x_i - \mu\,x_i^3
                + \zeta \sum_j J_{ij}\,x_j
                + \sqrt{d_n}\,\xi_i(\tau).
            \]
          </p>
          <table class="refs">
            <tr><td>simulator</td><td>physical role</td></tr>
            <tr><td><code>x @ J</code></td><td>FPGA MVM \(\Sigma_j J_{ij} x_j\) — homodyne photocurrent processed</td></tr>
            <tr><td><code>x*(r-1)</code></td><td>linear gain (above threshold) or loss (below)</td></tr>
            <tr><td><code>-mu*x³</code></td><td>pump-depletion saturation in the χ⁽²⁾ medium — what makes CIM bistable</td></tr>
            <tr><td><code>eps*MVM*error_var</code></td><td>EOM injection via the FPGA loop; \(error\_var\) is Leleu's correction</td></tr>
            <tr><td><code>eps*noise*uniform</code></td><td>stochastic injection; vacuum diffusion in the literature</td></tr>
            <tr><td><code>time_step</code></td><td>round-trip time in dimensionless cavity-decay units</td></tr>
          </table>
          <p>
            <em>Substituting</em> \(-\mu x^3 \to -A\,x\) (linear damping
            instead of cubic saturation) <em>turns this exact code into
            an Ornstein-Uhlenbeck linear-system solver</em> — the OU
            machine of Note 07. Same hardware, different dynamical
            regime.
          </p>
          """,
         ["AHC.py:131-133 = explicit Euler of MFB-CIM SDE",
          "Each line ↔ one physical mechanism",
          "OU machine: replace \\(-\\mu x^3\\) with \\(-A x\\)"]),
        ("comparison", "Comparison: CIM vs Quantum Annealers vs SA", r"""
          <p class="lede">
            How does the MFB-CIM stack up against D-Wave (quantum
            annealing) and well-tuned simulated annealing (SA) on
            CPUs? Honest answer: <em>it depends on the problem class
            and the metric</em>.
          </p>
          <p>
            <strong>D-Wave (transverse-field Ising annealer)</strong>:
            superconducting-flux qubits, ~5,000 qubits but with
            chimera/pegasus connectivity (degree 6–15). The CIM has
            <em>all-to-all</em> connectivity (FPGA can route any
            \(J_{ij}\)) — a major win on dense problem instances.
            For sparse problems matching D-Wave's native graph,
            D-Wave is faster. For dense MAX-CUT at \(N \gtrsim 1000\),
            CIM has demonstrated clearer wins.
          </p>
          <p>
            <strong>Simulated annealing on a top-tier CPU</strong>:
            implementing the CIM SDE on a GPU and running the same
            update Yamamoto-style is what Hamerly et al.\ 2018
            actually do — and they call it "noisy mean-field
            annealing", and it solves the same instances at the same
            wall-clock as the optical machine. <em>The classical
            simulator is the dual</em>: when the CIM beats SA, it's
            because the CIM hardware runs a particular SDE faster
            than CPU SA runs Metropolis, not because of quantum
            advantage.
          </p>
          <p>
            <strong>Where the CIM <em>does</em> win</strong>:
            \(O(\mu\)s\()\) round-trip latency per update on hardware
            that scales O(N²) only at the FPGA level — the constant
            factors in front of the asymptotic complexity are 2–3
            orders of magnitude better than CPU SA. For dense large-N
            problems where you care about wall-clock time-to-solution
            (not asymptotic complexity), CIM is a serious contender.
          </p>
          """ + callout(
            "If you read one paper to calibrate your priors here, "
            "make it Hamerly et al.\\ <em>Sci. Adv.</em> 2018 — "
            "<em>Experimental investigation of performance differences "
            "between coherent Ising machines and a quantum annealer</em>. "
            "It is the most honest head-to-head comparison in the "
            "literature."
          ),
         ["All-to-all connectivity: CIM beats D-Wave on dense",
          "vs SA: same physics, different hardware constants",
          "Wall-clock wins, asymptotic ties"]),
        ("scaling", "Scaling Demonstrated", r"""
          <p>
            What problem sizes have actually been solved by physical
            CIMs (not their simulators)? The numbers, year by year:
          </p>
          <table class="refs">
            <tr><td>Year</td><td>Group</td><td>N spins</td><td>Substrate</td><td>Demonstrated</td></tr>
            <tr><td>2014</td><td>Yamamoto / Stanford</td><td>4</td><td>free-space PPLN</td><td>1D Ising chain demo</td></tr>
            <tr><td>2016</td><td>Inagaki et al.\ (NTT)</td><td>2,048</td><td>1 km fiber</td><td>complete-graph K₂₀₀₀</td></tr>
            <tr><td>2016</td><td>McMahon et al.\ (Stanford)</td><td>100</td><td>fiber + measurement-feedback</td><td>programmable J on hardware</td></tr>
            <tr><td>2018</td><td>Hamerly et al.\ (Stanford+NTT)</td><td>2,000</td><td>1 km fiber</td><td>head-to-head vs D-Wave</td></tr>
            <tr><td>2021</td><td>Honjo et al.\ (NTT)</td><td>100,144</td><td>5 km fiber</td><td>sparse-graph MAX-CUT</td></tr>
            <tr><td>2024+</td><td>Marandi (Caltech)</td><td>~100</td><td>integrated thin-film LiNbO₃</td><td>chip-scale DOPO networks</td></tr>
          </table>
          <p>
            The 2014 → 2021 progression is a 25,000× scaling in 7
            years — limited by FPGA throughput and fiber length, not
            by photonics. The Marandi nanophotonic effort is the
            inflection: integrated DOPOs at ~5 mm scale would let one
            chip do what a 5 km fiber loop currently does, with
            \(10^4\)× lower latency. <em>That</em> would change the
            economics — and is the substrate the OU machine in Note
            07 inherits.
          </p>
          """,
         ["2014 → 2021: 4 → 100k spin scaling",
          "Limited by FPGA + fiber, not photonics",
          "Marandi integrated path = the inflection"]),
        ("open-questions", "Open Theoretical Questions", r"""
          <p class="lede">
            Five questions whose answers would change the field's
            self-image. None are settled in 2026.
          </p>
          <ol>
            <li><strong>Is there a quantum-noise-driven advantage at
              threshold?</strong> Bouland et al.\ have argued that
              tunneling between spin configurations during the
              bifurcation should give a polynomial speedup — but the
              empirical evidence is mixed and depends sensitively on
              how SA is tuned. <em>Settling this requires a problem
              class where SA provably fails and CIM provably succeeds
              with the same wall-clock budget.</em></li>
            <li><strong>What does AHC/CAC actually correct?</strong>
              The corrections work empirically but have no first-principles
              derivation. They look suspiciously like they're
              solving a different optimization problem (something
              like \(\min \sum_i (h_i^2 - 1)^2\)) than Ising — and that
              might be why they help.</li>
            <li><strong>What is the right embedding for non-binary
              variables?</strong> Continuous QUBOs, mixed-integer
              programs, constraint-satisfaction with non-trivial
              constraint topologies — none have a clean CIM mapping.
              The literature is currently piling auxiliary spins as
              one-hot ancillas, which kills the constant-factor
              advantage.</li>
            <li><strong>Is the dynamical regime "quantum"?</strong>
              The pedagogical answer is "below threshold, yes; above
              threshold, no" — but the actual computation happens
              <em>at</em> threshold, and the linearization breaks down
              there. We don't have a rigorous characterization of the
              threshold regime.</li>
            <li><strong>Can the same hardware do <em>not-Ising</em>
              tasks?</strong> Note 07 is one answer: linear algebra
              via Lyapunov sampling. Bayesian inference via Langevin
              MCMC is another. Each requires a different firmware in
              the FPGA's update step.</li>
          </ol>
          """,
         ["Quantum advantage: open empirically",
          "AHC/CAC: works but not understood",
          "Embedding non-Ising: kills constant factors",
          "Threshold regime: theoretically under-characterized",
          "Same hardware, new tasks: Note 07 is one direction"]),
        ("sota", "State of the Art (1996 → 2026)", r"""
          <table class="refs">
            <tr><td>1996</td><td>Yamamoto group: first DOPO Ising-machine concept</td></tr>
            <tr><td>2014</td><td>Wang et al.\ (Yamamoto): 4-spin demo, free-space</td></tr>
            <tr><td>2016</td><td>Inagaki et al., <em>Science</em>: 2,048-spin MFB-CIM at NTT</td></tr>
            <tr><td>2016</td><td>McMahon et al., <em>Science</em>: 100-spin programmable CIM at Stanford (the codebase we use)</td></tr>
            <tr><td>2018</td><td>Hamerly et al., <em>Sci. Adv.</em>: dual-polarization CIM scaling demo</td></tr>
            <tr><td>2019</td><td>Leleu et al., <em>PRL</em>: amplitude-heterogeneity-correction</td></tr>
            <tr><td>2021</td><td>Honjo et al., <em>Sci. Adv.</em>: 100,144-spin CIM, single fiber loop</td></tr>
            <tr><td>2025</td><td>Marandi group ongoing: integrated nanophotonic DOPO networks at Caltech</td></tr>
          </table>
          <p>
            What these machines actually solve: spin-glass instances,
            MAX-CUT, MIS, BIQ. They are heuristic solvers — competitive
            with simulated annealing on many problem classes, sometimes
            faster wall-clock — but no rigorous quantum advantage has
            been demonstrated against well-tuned classical solvers.
            The interesting research front is now (a) physically
            integrated implementations (Marandi nanophotonic) and (b)
            re-purposing the same hardware for non-Ising tasks
            (linear algebra: Note 07; sampling: Bayesian inference;
            etc.).
          </p>
          """,
         ["1996–2025: 1 → 100k spins",
          "Heuristic Ising solvers, competitive with SA",
          "No rigorous quantum-advantage demonstration"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Lecture</td><td><a href="_lectures/OPOs_and_coherent_Ising.pdf">OPOs_and_coherent_Ising.pdf</a> — primary source</td></tr>
            <tr><td>Lecture</td><td><a href="_lectures/CIM_description/CIM_description.pdf">CIM_description.pdf</a> — Lindblad form</td></tr>
            <tr><td>Paper</td><td><a href="_lectures/papers/Coherent_Ising_mahcines.pdf">Yamamoto et al., <em>npj Quantum Inf.</em> <strong>3</strong>, 49 (2017)</a> — the canonical review</td></tr>
            <tr><td>Paper</td><td>Inagaki et al., "A coherent Ising machine for 2000-node optimization problems", <em>Science</em> <strong>354</strong>, 603 (2016)</td></tr>
            <tr><td>Paper</td><td>Honjo et al., "100,000-spin coherent Ising machine", <em>Sci. Adv.</em> <strong>7</strong>, eabh0952 (2021)</td></tr>
            <tr><td>Code</td><td><a href="https://github.com/mcmahon-lab/cim-optimizer">mcmahon-lab/cim-optimizer</a> — McMahon Lab simulator</td></tr>
            <tr><td>Project</td><td><a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a> — live simulator and the CIM → OU rosetta in code</td></tr>
          </table>
          <p class="pre-req">
            <strong>Next note:</strong> §07 — Thermodynamic LA and the
            OU machine proposal. We re-purpose the MFB-CIM
            substrate as a Lyapunov sampler for linear-algebra
            primitives.
          </p>
          """,
         ["Yamamoto 2017 = the canonical CIM review",
          "Inagaki 2016, Honjo 2021 = state-of-the-art hardware",
          "Continue: Note 07 (OU machine — the headline)"]),
    ],
    "scripts": script_block(r"""
      // -- Widget 1: DOPO bifurcation phase portrait ----------------------
      (function () {
        var canvas = document.getElementById('dopo-bifurcation-canvas');
        if (!canvas) return;
        var ctx = canvas.getContext('2d');
        var W = canvas.width, H = canvas.height;
        var pSlider = document.getElementById('dopo-p');
        var muSlider = document.getElementById('dopo-mu');
        var nSlider = document.getElementById('dopo-noise');
        var pVal = document.getElementById('dopo-p-val');
        var muVal = document.getElementById('dopo-mu-val');
        var nVal = document.getElementById('dopo-noise-val');
        var text = document.getElementById('dopo-bifurcation-text');
        var SCALE = 80;       // pixels per unit α
        var ORIGIN_X = W/2, ORIGIN_Y = H/2;
        function draw() {
          var p = parseFloat(pSlider.value);
          var mu = parseFloat(muSlider.value);
          var noise = parseFloat(nSlider.value);
          pVal.textContent = p.toFixed(2);
          muVal.textContent = mu.toFixed(2);
          nVal.textContent = noise.toFixed(3);
          ctx.fillStyle = getComputedStyle(canvas).getPropertyValue('background-color') || '#0e0e16';
          ctx.fillRect(0, 0, W, H);
          // axes
          ctx.strokeStyle = '#666'; ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(0, ORIGIN_Y); ctx.lineTo(W, ORIGIN_Y);
          ctx.moveTo(ORIGIN_X, 0); ctx.lineTo(ORIGIN_X, H);
          ctx.stroke();
          // axis labels
          ctx.fillStyle = '#888'; ctx.font = '11px monospace';
          ctx.fillText('X', W - 12, ORIGIN_Y - 5);
          ctx.fillText('P', ORIGIN_X + 5, 12);
          // potential V(x) = -(p-1)/2 x² + μ/4 x⁴ — visualize via a faint
          // contour map of |gradient|
          var step = 6;
          for (var px = 0; px < W; px += step) {
            for (var py = 0; py < H; py += step) {
              var x = (px - ORIGIN_X) / SCALE;
              var y = (py - ORIGIN_Y) / SCALE;
              // drift magnitude in 2D where pump only acts on X axis:
              var dx = (p - 1) * x - mu * x * x * x;
              var dy = -1.0 * y; // damping on P only (no parametric gain)
              var mag = Math.sqrt(dx*dx + dy*dy);
              var v = Math.max(0, 1 - mag*1.4);
              ctx.fillStyle = 'rgba(122, 159, 209, ' + (v*0.20).toFixed(3) + ')';
              ctx.fillRect(px, py, step, step);
            }
          }
          // sample trajectories: random initial conditions, integrate Euler
          ctx.strokeStyle = 'rgba(180, 200, 240, 0.45)';
          ctx.lineWidth = 1;
          var N_TRAJ = 40;
          for (var k = 0; k < N_TRAJ; k++) {
            var x = (Math.random() - 0.5) * 4;
            var y = (Math.random() - 0.5) * 4;
            ctx.beginPath();
            ctx.moveTo(ORIGIN_X + x*SCALE, ORIGIN_Y - y*SCALE);
            for (var s = 0; s < 220; s++) {
              var dx = (p-1)*x - mu*x*x*x;
              var dy = -1.0*y;
              var dt = 0.06;
              x += dt*dx + Math.sqrt(dt)*noise*(Math.random()-0.5)*2;
              y += dt*dy + Math.sqrt(dt)*noise*(Math.random()-0.5)*2;
              if (Math.abs(x) > 4 || Math.abs(y) > 4) break;
              ctx.lineTo(ORIGIN_X + x*SCALE, ORIGIN_Y - y*SCALE);
            }
            ctx.stroke();
          }
          // fixed points
          var fps = [{x: 0, color: (p < 1 ? '#79f29c' : '#f27979')}];
          if (p > 1) {
            var ax = Math.sqrt((p-1)/mu);
            fps.push({x: ax, color: '#79f29c'});
            fps.push({x: -ax, color: '#79f29c'});
          }
          for (var i = 0; i < fps.length; i++) {
            ctx.fillStyle = fps[i].color;
            ctx.beginPath();
            ctx.arc(ORIGIN_X + fps[i].x*SCALE, ORIGIN_Y, 5, 0, 2*Math.PI);
            ctx.fill();
          }
          var label;
          if (p < 0.95) label = 'Below threshold (p = ' + p.toFixed(2) + ') — origin stable. Cavity is squeezed-vacuum.';
          else if (p > 1.05) label = 'Above threshold (p = ' + p.toFixed(2) + ') — two stable phases at α = ±' + Math.sqrt((p-1)/mu).toFixed(2) + '. Phase commitment.';
          else label = 'At threshold (p = ' + p.toFixed(2) + ') — origin marginal. Quantum noise selects which phase wins.';
          text.textContent = label;
        }
        [pSlider, muSlider, nSlider].forEach(function (el) {
          el.addEventListener('input', draw);
        });
        draw();
      })();

      // -- Widget 2: quantum/classical regime gauge -----------------------
      (function () {
        var svg = document.getElementById('qc-regime-svg');
        if (!svg) return;
        var nSlider = document.getElementById('qc-n');
        var nVal = document.getElementById('qc-n-val');
        var text = document.getElementById('qc-regime-text');
        var W = 520, H = 180;
        function regimeLabel(snr) {
          if (snr < 1) return {name: 'vacuum-fluctuation regime', color: '#7a9fd1', detail: 'Full Lindblad / squeezed-vacuum description.'};
          if (snr < 3) return {name: 'crossover (threshold)', color: '#e8b96a', detail: 'Linearization breaks down; nonlinear quantum noise.'};
          if (snr < 30) return {name: 'bright but quantum-influenced', color: '#79c79f', detail: 'Linearized Gaussian (mean-field + Langevin noise).'};
          return {name: 'classical bright-field', color: '#79c79f', detail: 'Operationally classical; Mandel-Wolf says SDE suffices.'};
        }
        function draw() {
          var logn = parseFloat(nSlider.value);
          var n = Math.pow(10, logn);
          var snr = Math.sqrt(n);
          nVal.textContent = logn.toFixed(2);
          var reg = regimeLabel(snr);
          // build SVG content
          var pad = 40;
          var bar_y = H/2 - 8;
          var bar_h = 16;
          var bar_x = pad, bar_w = W - 2*pad;
          // log scale bar from 10^-2 to 10^6
          var nx = bar_x + (logn + 2)/8 * bar_w;
          var threshold_x = bar_x + (Math.log10(9) + 2)/8 * bar_w;  // SNR=3 ⇒ n=9
          var bright_x = bar_x + (Math.log10(900) + 2)/8 * bar_w;   // SNR=30 ⇒ n=900
          svg.innerHTML = (
            '<defs>' +
            '  <linearGradient id="qcgrad" x1="0" x2="1">' +
            '    <stop offset="0" stop-color="#7a9fd1"/>' +
            '    <stop offset="' + ((Math.log10(9)+2)/8) + '" stop-color="#e8b96a"/>' +
            '    <stop offset="' + ((Math.log10(900)+2)/8) + '" stop-color="#79c79f"/>' +
            '    <stop offset="1" stop-color="#79c79f"/>' +
            '  </linearGradient>' +
            '</defs>' +
            '<rect x="' + bar_x + '" y="' + bar_y + '" width="' + bar_w + '" height="' + bar_h + '" rx="8" fill="url(#qcgrad)" opacity="0.7"/>' +
            '<line x1="' + threshold_x + '" x2="' + threshold_x + '" y1="' + (bar_y-8) + '" y2="' + (bar_y+bar_h+8) + '" stroke="#e8b96a" stroke-width="1.5" stroke-dasharray="3,3"/>' +
            '<line x1="' + bright_x + '" x2="' + bright_x + '" y1="' + (bar_y-8) + '" y2="' + (bar_y+bar_h+8) + '" stroke="#79c79f" stroke-width="1.5" stroke-dasharray="3,3"/>' +
            '<text x="' + threshold_x + '" y="' + (bar_y-12) + '" text-anchor="middle" font-size="10" fill="#888">SNR=3</text>' +
            '<text x="' + bright_x + '" y="' + (bar_y-12) + '" text-anchor="middle" font-size="10" fill="#888">SNR=30</text>' +
            '<circle cx="' + nx + '" cy="' + (bar_y + bar_h/2) + '" r="9" fill="' + reg.color + '" stroke="#fff" stroke-width="1.5"/>' +
            '<text x="' + bar_x + '" y="' + (H-20) + '" font-size="10" fill="#888">⟨n⟩=10⁻²</text>' +
            '<text x="' + (bar_x+bar_w) + '" y="' + (H-20) + '" font-size="10" fill="#888" text-anchor="end">⟨n⟩=10⁶</text>' +
            '<text x="' + (W/2) + '" y="' + (bar_y + bar_h + 30) + '" font-size="13" fill="' + reg.color + '" text-anchor="middle" font-weight="600">⟨n⟩ ≈ 10^' + logn.toFixed(2) + ' &#8594; SNR ≈ ' + snr.toFixed(2) + '</text>'
          );
          text.innerHTML = '<strong>' + reg.name + '</strong>: ' + reg.detail;
        }
        nSlider.addEventListener('input', draw);
        draw();
      })();

      // -- Widget 3: 4-spin CIM round-trip simulation ---------------------
      (function () {
        var svg = document.getElementById('cim-roundtrip-svg');
        if (!svg) return;
        var pumpSlider = document.getElementById('cim-pump');
        var couplingSlider = document.getElementById('cim-coupling');
        var noiseSlider = document.getElementById('cim-noise');
        var pumpVal = document.getElementById('cim-pump-val');
        var couplingVal = document.getElementById('cim-coupling-val');
        var noiseVal = document.getElementById('cim-noise-val');
        var spinsText = document.getElementById('cim-roundtrip-spins');
        var energyText = document.getElementById('cim-roundtrip-energy');
        var stepText = document.getElementById('cim-roundtrip-step-num');
        var runBtn = document.getElementById('cim-roundtrip-run');
        var stepBtn = document.getElementById('cim-roundtrip-step');
        var resetBtn = document.getElementById('cim-roundtrip-reset');

        // 4-spin frustrated chain: J = -A where A is graph adjacency
        // (MAX-CUT convention from earlier work). Triangle 0-1-2 + pendant 3:
        // edges (0,1), (1,2), (0,2), (1,3) ⇒ ground state is unique up to flip
        var J = [
          [0, -1, -1,  0],
          [-1, 0, -1, -1],
          [-1, -1, 0,  0],
          [0, -1,  0,  0]
        ];
        var W = 520, H = 320;
        var x = [0, 0, 0, 0];
        var energyHistory = [];
        var step = 0;
        var maxSteps = 80;
        var running = false;
        var raf = null;

        function isingEnergy() {
          var E = 0;
          var s = x.map(function (v) { return v >= 0 ? 1 : -1; });
          for (var i = 0; i < 4; i++)
            for (var j = i+1; j < 4; j++)
              E -= J[i][j] * s[i] * s[j];
          return E;
        }
        function reset() {
          x = [0.01*(Math.random()-0.5), 0.01*(Math.random()-0.5),
               0.01*(Math.random()-0.5), 0.01*(Math.random()-0.5)];
          energyHistory = [];
          step = 0;
          running = false;
          if (raf) { cancelAnimationFrame(raf); raf = null; }
          render();
        }
        function doStep() {
          if (step >= maxSteps) return;
          var pump = parseFloat(pumpSlider.value);
          var eps = parseFloat(couplingSlider.value);
          var noise = parseFloat(noiseSlider.value);
          var dt = 1.0;
          // r ramps from -0.5 (below threshold) to +1.5 (above) over the run
          var r = -0.5 + 2.0 * (step / maxSteps);
          var mu = 0.05;
          // MVM = J · x
          var mvm = [0,0,0,0];
          for (var i = 0; i < 4; i++)
            for (var j = 0; j < 4; j++)
              mvm[i] += J[i][j] * x[j];
          for (var i = 0; i < 4; i++) {
            // gain - cubic saturation
            x[i] += pump*dt * (x[i] * (r - mu*x[i]*x[i]));
            // EOM injection
            x[i] += eps*dt * mvm[i];
            // injected noise
            x[i] += noise * (Math.random() - 0.5);
            // bound for visualization stability
            if (x[i] > 3) x[i] = 3;
            if (x[i] < -3) x[i] = -3;
          }
          energyHistory.push(isingEnergy());
          step++;
          render();
        }
        function loop() {
          doStep();
          if (running && step < maxSteps) {
            raf = requestAnimationFrame(loop);
          } else {
            running = false;
          }
        }
        function render() {
          var pump = parseFloat(pumpSlider.value);
          var eps = parseFloat(couplingSlider.value);
          var noise = parseFloat(noiseSlider.value);
          pumpVal.textContent = pump.toFixed(3);
          couplingVal.textContent = eps.toFixed(3);
          noiseVal.textContent = noise.toFixed(3);
          // bars on top half
          var barTop = 30, barH = 90, pad = 30;
          var bw = (W - 2*pad) / 4;
          var s_strs = [];
          var bars = '';
          var labels = '';
          var colors = ['#7a9fd1', '#e8b96a', '#79c79f', '#c879d1'];
          for (var i = 0; i < 4; i++) {
            var v = x[i];
            var s = v >= 0 ? '+' : '−';
            s_strs.push(s);
            var bx = pad + i*bw + bw*0.15;
            var by_zero = barTop + barH/2;
            var bh = -v * (barH/2) / 2.5;
            bars += '<rect x="' + bx + '" y="' + (bh < 0 ? by_zero : by_zero - bh) + '" width="' + (bw*0.7) + '" height="' + Math.abs(bh) + '" fill="' + colors[i] + '" opacity="0.75"/>';
            bars += '<line x1="' + bx + '" x2="' + (bx+bw*0.7) + '" y1="' + by_zero + '" y2="' + by_zero + '" stroke="#888"/>';
            labels += '<text x="' + (bx + bw*0.35) + '" y="' + (barTop + barH + 15) + '" text-anchor="middle" font-size="11" fill="#888">x_' + (i+1) + '=' + v.toFixed(2) + '</text>';
          }
          // energy trace below
          var traceTop = barTop + barH + 38, traceH = H - traceTop - 30;
          var trace = '<text x="' + pad + '" y="' + (traceTop - 6) + '" font-size="10" fill="#888">Ising energy −½sᵀJs</text>';
          if (energyHistory.length > 1) {
            var minE = Math.min.apply(null, energyHistory);
            var maxE = Math.max.apply(null, energyHistory);
            if (maxE === minE) maxE += 1;
            var pts = energyHistory.map(function (E, k) {
              var px = pad + (k / maxSteps) * (W - 2*pad);
              var py = traceTop + traceH * (1 - (E - minE) / (maxE - minE));
              return px + ',' + py;
            }).join(' ');
            trace += '<polyline points="' + pts + '" fill="none" stroke="#79c79f" stroke-width="1.8"/>';
            trace += '<text x="' + (W-pad) + '" y="' + (traceTop + 12) + '" font-size="10" fill="#888" text-anchor="end">E_max=' + maxE.toFixed(2) + '</text>';
            trace += '<text x="' + (W-pad) + '" y="' + (traceTop + traceH - 2) + '" font-size="10" fill="#888" text-anchor="end">E_min=' + minE.toFixed(2) + '</text>';
          }
          svg.innerHTML = bars + labels + trace;
          spinsText.textContent = s_strs.join(' ');
          energyText.textContent = (energyHistory.length ? energyHistory[energyHistory.length-1] : 0).toFixed(3);
          stepText.textContent = step + ' / ' + maxSteps;
        }
        runBtn.addEventListener('click', function () {
          if (step >= maxSteps) reset();
          if (!running) { running = true; loop(); }
        });
        stepBtn.addEventListener('click', function () { if (!running) doStep(); });
        resetBtn.addEventListener('click', reset);
        [pumpSlider, couplingSlider, noiseSlider].forEach(function (el) {
          el.addEventListener('input', render);
        });
        reset();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Note 07: OU Machine Proposal (HEADLINE — User requirement 3)
# ---------------------------------------------------------------------------

NOTE_07 = {
    "filename": "07_thermodynamic_la_ou_machine.html",
    "title": "Thermodynamic Linear Algebra and the OU Machine",
    "description": "Re-purposing the MFB-CIM substrate as a Lyapunov sampler. The optical SPU proposal: Langevin → Lyapunov, hardware envelope, and the bridge to the underdamped √κ research direction.",
    "eyebrow": "Quantum Optics · Optical SPU",
    "h1": "Thermodynamic LA &amp; the OU Machine Proposal",
    "subtitle": "The synthesis. With every component from Notes 01–06 in place, we re-purpose the MFB-CIM hardware to compute matrix inverses by sampling. The math is exact; the engineering envelope is in flight.",
    "covers": [
        "Thermodynamic linear algebra: Aifer-Coles-Duffield framing",
        "Langevin → Lyapunov: \\(d x = -A x dt + \\sqrt{D} dW \\Rightarrow A\\Sigma + \\Sigma A^T = D\\)",
        "Optical adaptation: replace cubic saturation with linear damping",
        "Hardware imperfection envelope (η, τ, σ_meas)",
        "QCi target table: Stretch / Practical / Loose",
        "Roadmap: overdamped → underdamped √κ speedup",
        "Open questions: scaling to d ≥ 64, non-symmetric A, non-CIM applications",
    ],
    "nav": [
        ("tla", "TLA Framing"),
        ("tla-primitives", "Three Primitives"),
        ("langevin-lyapunov", "Langevin→Lyapunov"),
        ("optical-adapt", "Optical Adaptation"),
        ("matrix-encoding", "Encoding A"),
        ("readout-protocols", "Readout Modes"),
        ("simulator-diff", "Simulator Diff"),
        ("rlc-comparison", "vs RLC SPU"),
        ("envelope", "Hardware Envelope"),
        ("targets", "QCi Targets"),
        ("roadmap", "Roadmap"),
        ("open", "Open Questions"),
        ("sources", "Sources"),
    ],
    "sections": [
        ("tla", "Thermodynamic Linear Algebra: The Framing", r"""
          <p class="lede">
            The observation behind <em>thermodynamic linear algebra</em>
            (Aifer, Coles, Duffield, et al., arXiv:2306.14740, 2023) is
            simple: a stochastic-differential-equation system at
            stationarity has a covariance matrix \(\Sigma\) that solves
            an algebraic equation determined by its drift and diffusion.
            For the right SDE, that algebraic equation is the one we
            wanted to solve in the first place.
          </p>
          <p>
            The first realization is electronic — Normal Computing's RLC
            Stochastic Processing Unit (Aifer et al., <em>Nat. Commun.</em>
            2025): a network of resistors-inductors-capacitors thermally
            driven, where the steady-state covariance of the node
            voltages encodes \(A^{-1}\) for a user-programmable matrix
            \(A\). They demonstrated 8×8 problems on bench hardware.
          </p>
          <p>
            The hypothesis of this proposal: <em>the same primitive
            runs on the MFB-CIM photonic substrate</em>, with two key
            advantages: (i) per-round-trip MVM is O(1) latency in the
            photonic loop, vs CPU's O(d²); (ii) the room-temperature
            photonic noise floor is much lower than thermal Johnson
            noise on RLC, so the precision per joule should be
            substantially better.
          </p>
          """ + callout(
            'We are re-using the entire CIM hardware — pulse loop, '
            'homodyne, FPGA, EOM, calibrated noise — and changing only '
            'the FPGA firmware (linear damping instead of cubic). The '
            'engineering risk is shifted from &ldquo;build new hardware&rdquo; to '
            '&ldquo;characterize a different operating regime of an existing '
            'hardware class.&rdquo;'
          ),
         ["TLA: SDE stationary covariance ↔ algebraic primitive",
          "Aifer-Coles-Duffield 2023 (arXiv:2306.14740) — RLC version",
          "Photonic re-implementation: same primitive, faster MVM, lower noise floor"]),
        ("tla-primitives", "Three TLA Primitives", r"""
          <p class="lede">
            Thermodynamic linear algebra is a family of algorithms — not
            a single primitive. The OU machine implements the simplest
            (and most-tested) one. The catalog matters because it tells
            us what else this hardware could do.
          </p>
          <ol>
            <li><strong>Linear systems / matrix inverse</strong>: solve
              \(A v = b\) by reading \(2\hat\Sigma b\) from a sample
              average. <em>This is the OU machine</em>. Symmetric PD
              \(A\) and isotropic noise. Direct application: linear
              regression, Gaussian-process inference, Newton steps.</li>
            <li><strong>Sampling from a Gaussian</strong>: draw samples
              from \(\mathcal{N}(0, A^{-1})\). Same SDE; instead of
              averaging covariance you record trajectory points. Direct
              application: Bayesian posterior sampling, MCMC
              initialization, simulation.</li>
            <li><strong>Determinant estimation</strong>: \(\log\det A\)
              from the equilibrium free energy of the OU process. The
              elegant Aifer-Coles-Duffield trick. Direct application:
              evidence in Bayesian model comparison, normalising
              constants for partition functions.</li>
          </ol>
          <p>
            For the optical implementation, all three primitives share
            the same hardware: <em>only the postprocessing changes</em>.
            Linear systems read \(2\hat\Sigma b\); sampling reads
            \(x(t)\) directly; determinant reads the cumulative work
            done by the EOM. The economic argument is therefore: build
            one optical SPU, get three primitives.
          </p>
          """ + callout(
            "The hardware that does any one of these does all three. "
            "The pitch to a hardware sponsor is therefore a portfolio "
            "bet: the OU machine de-risks the substrate; sampling and "
            "determinant estimation come for free in firmware once the "
            "substrate exists."
          ),
         ["Three primitives, one substrate",
          "Linear systems / sampling / determinant",
          "Postprocessing differs, hardware does not"]),
        ("langevin-lyapunov", "Langevin → Lyapunov", r"""
          <p>
            For the linear SDE
            \[
              dx = -A\,x\,dt + B\,dW,
              \qquad D := B B^T,
            \]
            with Hurwitz \(A\) (eigenvalues with positive real part),
            the stationary covariance \(\Sigma = \mathbb{E}[x x^T]\)
            solves the <strong>continuous Lyapunov equation</strong>:
            \[
              A\,\Sigma + \Sigma\,A^T = D.
            \]
          </p>
          """ + math_details("Derivation via Itô's lemma", r"""
            <p>
              Apply Itô to \(x x^T\): \(d(x x^T) = (dx) x^T + x (dx^T) + (dx)(dx^T)\).
              Substitute \(dx = -A x\,dt + B\,dW\), use
              \(\mathbb{E}[dW\,dW^T] = I\,dt\), and take expectation:
              \[
                d\,\mathbb{E}[xx^T]
                = \bigl(-A\,\mathbb{E}[xx^T] - \mathbb{E}[xx^T]\,A^T + D\bigr) dt.
              \]
              At stationarity, set the LHS to zero:
              \(A\Sigma + \Sigma A^T = D\). For a symmetric PD \(A\)
              and \(D = I\), this gives \(2 A \Sigma = I\), so
              \(\Sigma = \tfrac{1}{2} A^{-1}\).
            </p>
          """) + r"""
          <p>
            <strong>The matrix-inverse application:</strong> with symmetric
            PD \(A\) and white-noise drive \(D = I\), the steady-state
            covariance is exactly half the inverse:
            \[
              \Sigma = \tfrac{1}{2}\,A^{-1}.
            \]
            So the OU machine doubles as a linear-system solver: given
            a right-hand side \(b\), compute
            \(v = A^{-1} b = 2 \Sigma b \approx 2 \hat\Sigma b\) where
            \(\hat\Sigma\) is the empirical sample covariance from the
            simulator's trajectory.
          </p>
          <p>
            For non-symmetric Hurwitz \(A\) the relation between
            \(\Sigma\) and \(A^{-1}\) is more involved, but the
            primitive still works — we just choose a different
            estimator. See the Aifer-Coles-Duffield recipe table.
          </p>
          """ + widget_shell(
            anchor="lyapunov-sampler",
            title="Interactive: 4-D OU machine convergence",
            blurb=(
              "Press <em>Run</em> to step a small (d=4) OU machine. The "
              "trace plots Frobenius error "
              "‖<em>Σ̂</em>(t) − ½<em>A</em>⁻¹‖_F as the empirical "
              "covariance from running averages converges to the "
              "Lyapunov solution. Convergence rate is "
              "<em>T<sub>mix</sub></em> ∝ <em>κ</em> for the overdamped "
              "OU machine (Note 07's central scaling result)."
            ),
            controls_html=(
              slider(var="lya-kappa", label="κ = λ_max/λ_min", min_=1.5,
                     max_=20, step=0.5, value=5, fmt="{:.1f}") + "\n" +
              slider(var="lya-dt", label="step Δt", min_=0.005,
                     max_=0.1, step=0.005, value=0.04, fmt="{:.3f}")
            ),
            buttons_html=(
              '<button id="lya-run">Run</button>'
              '<button id="lya-reset">Reset</button>'
            ),
            canvas_html=svg_el("lyapunov-sampler", w=520, h=260),
            readout_html=(
              '<div>Sample covariance error: <span id="lya-err">—</span></div>'
              '<div>Step: <span id="lya-step">0</span> / 1500</div>'
            ),
          ) + r"""
          """ + callout(
            "The Lyapunov equation <em>is</em> the algebraic content of "
            "what an OU process knows at stationarity. The hardware "
            "advantage of the OU machine is not that it computes a "
            "different equation — it's that the matrix-vector "
            "multiplication that lives at the heart of "
            "<em>A</em>Σ + Σ<em>A</em>ᵀ = <em>D</em> can be evaluated "
            "in O(1) photonic round-trip time, vs CPU's O(d²)."
          ),
         ["\\(\\dot x = -A x + \\sqrt{D}\\,\\xi \\Rightarrow A\\Sigma + \\Sigma A^T = D\\)",
          "Symmetric PD \\(A\\) + \\(D = I\\) ⇒ \\(\\Sigma = \\tfrac{1}{2}A^{-1}\\)",
          "\\(\\hat\\Sigma\\) from sample averaging gives \\(A^{-1}\\)",
          "Mixing time \\(\\propto \\kappa\\) (overdamped)"]),
        ("optical-adapt", "Optical Adaptation: From MFB-CIM to OU Sampler", r"""
          <p class="lede">
            We do not build new hardware for the OU machine. We
            <em>re-purpose</em> the MFB-CIM substrate (Note 06,
            Yamamoto/Inagaki/Marandi) by changing the FPGA firmware so
            the loop runs a different SDE. The substrate is the same
            time-multiplexed pulse loop with balanced homodyne,
            FPGA-implemented matrix-vector multiply, and EOM injection.
            Below is the architectural comparison, then a precise
            inventory of which physical element holds which mathematical
            object.
          </p>
          <figure style="margin: 1rem 0;">
            <svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px;display:block;background:var(--page-bg);border:1px solid var(--page-rule);border-radius:6px;">
              <defs>
                <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                  <path d="M0,0 L10,5 L0,10 z" fill="#7a9fd1"/>
                </marker>
                <marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                  <path d="M0,0 L10,5 L0,10 z" fill="#79c79f"/>
                </marker>
              </defs>
              <!-- Title strip -->
              <text x="180" y="20" text-anchor="middle" font-size="13" font-weight="600" fill="#7a9fd1">MFB-CIM (Note 06)</text>
              <text x="540" y="20" text-anchor="middle" font-size="13" font-weight="600" fill="#79c79f">Optical OU machine (Note 07)</text>
              <line x1="360" y1="32" x2="360" y2="345" stroke="#444" stroke-width="0.5" stroke-dasharray="3,3"/>
              <!-- LEFT (CIM) -->
              <!-- Fiber loop drawn as ellipse -->
              <ellipse cx="180" cy="170" rx="130" ry="60" fill="none" stroke="#888" stroke-width="1.4"/>
              <text x="180" y="172" text-anchor="middle" font-size="10" fill="#888">fiber-loop pulses (1 per spin)</text>
              <!-- pulses on the loop -->
              <circle cx="100" cy="178" r="3" fill="#7a9fd1"/><circle cx="135" cy="124" r="3" fill="#7a9fd1"/>
              <circle cx="200" cy="111" r="3" fill="#7a9fd1"/><circle cx="252" cy="146" r="3" fill="#7a9fd1"/>
              <!-- PPLN gain crystal -->
              <rect x="160" y="105" width="40" height="14" fill="#c879d1" stroke="#a55fa9" rx="2"/>
              <text x="180" y="115" text-anchor="middle" font-size="9" fill="#fff">PPLN χ⁽²⁾</text>
              <text x="180" y="100" text-anchor="middle" font-size="9" fill="#c879d1">gain (above threshold)</text>
              <!-- tap → homodyne -->
              <line x1="297" y1="190" x2="335" y2="245" stroke="#7a9fd1" stroke-width="1.6" marker-end="url(#arr)"/>
              <rect x="55" y="245" width="280" height="38" fill="rgba(122,159,209,0.12)" stroke="#7a9fd1" rx="3"/>
              <text x="80" y="263" font-size="10" fill="#7a9fd1">homodyne</text>
              <text x="80" y="276" font-size="9" fill="#888">measures X_i</text>
              <text x="160" y="263" font-size="10" fill="#7a9fd1">FPGA</text>
              <text x="160" y="276" font-size="9" fill="#888">computes <tspan font-weight="600">J · x</tspan></text>
              <text x="240" y="263" font-size="10" fill="#7a9fd1">EOM</text>
              <text x="240" y="276" font-size="9" fill="#888">injects ε(t)·MVM</text>
              <!-- back-to-loop arrow -->
              <line x1="60" y1="245" x2="60" y2="200" stroke="#7a9fd1" stroke-width="1.6" marker-end="url(#arr)"/>
              <!-- annotations -->
              <text x="20" y="305" font-size="10" fill="#888" font-weight="600">Update:</text>
              <text x="20" y="320" font-size="10" fill="#888">x ← x + dt[(r−1)x − μx³] + ε(t)·J·x + noise(t)</text>
              <text x="20" y="338" font-size="10" fill="#888" font-style="italic">(cubic saturation; ε ramps; noise schedule)</text>
              <!-- RIGHT (OU) -->
              <ellipse cx="540" cy="170" rx="130" ry="60" fill="none" stroke="#888" stroke-width="1.4"/>
              <text x="540" y="172" text-anchor="middle" font-size="10" fill="#888">fiber-loop pulses (1 per dimension)</text>
              <circle cx="460" cy="178" r="3" fill="#79c79f"/><circle cx="495" cy="124" r="3" fill="#79c79f"/>
              <circle cx="560" cy="111" r="3" fill="#79c79f"/><circle cx="612" cy="146" r="3" fill="#79c79f"/>
              <!-- PPLN at threshold or removed -->
              <rect x="520" y="105" width="40" height="14" fill="#c879d1" stroke="#a55fa9" rx="2" opacity="0.4"/>
              <text x="540" y="115" text-anchor="middle" font-size="9" fill="#fff" opacity="0.6">PPLN at thr.</text>
              <text x="540" y="100" text-anchor="middle" font-size="9" fill="#c879d1" opacity="0.6">no bifurcation</text>
              <line x1="657" y1="190" x2="695" y2="245" stroke="#79c79f" stroke-width="1.6" marker-end="url(#arr2)"/>
              <rect x="415" y="245" width="280" height="38" fill="rgba(121,199,159,0.12)" stroke="#79c79f" rx="3"/>
              <text x="440" y="263" font-size="10" fill="#79c79f">homodyne</text>
              <text x="440" y="276" font-size="9" fill="#888">measures X_i</text>
              <text x="520" y="263" font-size="10" fill="#79c79f">FPGA</text>
              <text x="520" y="276" font-size="9" fill="#888">computes <tspan font-weight="600">−A_off · x</tspan></text>
              <text x="600" y="263" font-size="10" fill="#79c79f">EOM</text>
              <text x="600" y="276" font-size="9" fill="#888">injects ε·MVM + b</text>
              <line x1="420" y1="245" x2="420" y2="200" stroke="#79c79f" stroke-width="1.6" marker-end="url(#arr2)"/>
              <text x="380" y="305" font-size="10" fill="#888" font-weight="600">Update:</text>
              <text x="380" y="320" font-size="10" fill="#888">x ← x − dt·A·x + dt·b + √(dt)·D^{½}·ξ</text>
              <text x="380" y="338" font-size="10" fill="#888" font-style="italic">(linear damping; constant ε; Gaussian noise)</text>
            </svg>
            <figcaption style="font-size: 0.85rem; color: var(--page-muted); margin-top: 0.4rem; text-align: center;">
              <strong>Fig.&nbsp;1.</strong> Architectural comparison. Same fiber-loop substrate; different FPGA firmware. The MFB-CIM lives above the DOPO threshold and uses cubic saturation to commit to ±1 spin states; the OU machine operates at or below threshold with linear damping, never committing to a discrete state. The Yamamoto-NTT measurement-feedback CIM schematic (<a href="_lectures/classical_CIM_from_Yamamoto.png">classical_CIM_from_Yamamoto.png</a>) is the reference for the left side.
            </figcaption>
          </figure>
          <p>
            The OU machine in
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            makes three surgical firmware changes vs MFB-CIM (the
            "AHC.py three-line diff" referred to throughout):
          </p>
          <ol>
            <li><strong>Cubic → linear damping.</strong>
              \((r-1)x - \mu x^3\) is replaced by \(-A_\mathrm{diag}\,x\),
              evaluated per pulse. No bifurcation, no spin commitment;
              dynamics stays in the linear (Gaussian-state) regime.</li>
            <li><strong>Ising J → Lyapunov \(-A_\mathrm{off}\).</strong>
              The FPGA MVM RAM is loaded with the negative off-diagonal
              of the user's drift matrix instead of an Ising coupling.</li>
            <li><strong>Uniform noise → Gaussian noise.</strong>
              \((\mathrm{rand}-0.5)\) is replaced by
              \(\sqrt{2\,dt}\,D^{1/2}\xi\) with \(\xi \sim \mathcal{N}(0,I)\).
              This is the formally-correct Langevin diffusion;
              \(D^{1/2}\) is the Cholesky of the user's diffusion matrix.</li>
          </ol>
          <p>
            Critically, every passive optical element (fiber loop,
            beam splitters, output coupler, EOM, photodetectors,
            ADCs/DACs, FPGA hardware) is unchanged. The same bench can
            run CIM on Tuesday and OU machine on Wednesday — the
            firmware that loads the FPGA's MVM table and the per-pulse
            update logic is the only difference.
          </p>
          <p>
            <strong>Verification</strong> (cim/<code>experiments/exp02_ou_lyapunov.py</code>):
            for \(d \in \{4, 8, 16\}\) and \(\kappa(A) \in \{1, 10, 100\}\),
            empirical \(\hat\Sigma\) matches
            <code>scipy.linalg.solve_continuous_lyapunov</code> to within
            \(\le 5\%\) relative Frobenius error (the simulator hits
            ≤ 2.7% at the worst-case cell). The success grid is the
            headline figure of the cim repo's notebook 02.
          </p>
          """ + callout(
            "The OU machine is not faster than <code>scipy.linalg.solve</code> "
            "in software — our simulator is a Python loop. The claim is "
            "about the optical hardware, where per-round-trip MVM is "
            "O(d) latency in the optical loop vs CPU's O(d²) per "
            "iteration plus O(d³) Cholesky. The simulator's role is to "
            "<em>verify</em> the dynamics, not race against LAPACK."
          ),
         ["Same fiber loop, homodyne, FPGA, EOM as MFB-CIM",
          "Three-line firmware diff: cubic→linear, J→−A_off, uniform→Gaussian",
          "Verified: \\(\\hat\\Sigma \\to \\frac{1}{2}A^{-1}\\) within 3% (sim)"]),
        ("matrix-encoding", "Encoding A: Where Each Mathematical Object Lives", r"""
          <p class="lede">
            The OU machine has four user-controllable mathematical
            objects: the drift matrix \(A\), the bias vector \(b\), the
            diffusion matrix \(D\), and the step size \(dt\). Each maps
            onto a specific physical element of the bench. Understanding
            this mapping is the difference between thinking of the
            machine as a black box and being able to debug it.
          </p>
          <figure style="margin: 1rem 0;">
            <svg viewBox="0 0 720 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:720px;display:block;background:var(--page-bg);border:1px solid var(--page-rule);border-radius:6px;">
              <defs>
                <marker id="arr3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
                  <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
                </marker>
              </defs>
              <text x="120" y="20" text-anchor="middle" font-size="12" font-weight="600" fill="#888">Mathematical objects</text>
              <text x="540" y="20" text-anchor="middle" font-size="12" font-weight="600" fill="#888">Physical realization</text>
              <line x1="270" y1="32" x2="270" y2="345" stroke="#444" stroke-width="0.5" stroke-dasharray="3,3"/>
              <!-- Matrix A as a 4x4 grid -->
              <g transform="translate(40, 40)">
                <text x="80" y="-4" text-anchor="middle" font-size="11" fill="#7a9fd1" font-weight="600">A = A_diag + A_off</text>
                <!-- diag part -->
                <text x="20" y="14" font-size="9" fill="#888">A_diag</text>
                <g>
                  <rect x="0" y="20" width="20" height="20" fill="#79c79f" opacity="0.7"/>
                  <rect x="20" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="40" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="60" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="0" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="20" y="40" width="20" height="20" fill="#79c79f" opacity="0.7"/>
                  <rect x="40" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="60" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="0" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="20" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="40" y="60" width="20" height="20" fill="#79c79f" opacity="0.7"/>
                  <rect x="60" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="0" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="20" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="40" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="60" y="80" width="20" height="20" fill="#79c79f" opacity="0.7"/>
                </g>
                <text x="100" y="55" font-size="14" fill="#888">+</text>
                <text x="135" y="14" font-size="9" fill="#888">A_off</text>
                <g transform="translate(118, 0)">
                  <rect x="0" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="20" y="20" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="40" y="20" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="60" y="20" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="0" y="40" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="20" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="40" y="40" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="60" y="40" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="0" y="60" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="20" y="60" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="40" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                  <rect x="60" y="60" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="0" y="80" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="20" y="80" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="40" y="80" width="20" height="20" fill="#e8b96a" opacity="0.7"/>
                  <rect x="60" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                </g>
              </g>
              <!-- b vector -->
              <g transform="translate(40, 165)">
                <text x="20" y="14" font-size="9" fill="#888">bias b</text>
                <rect x="0" y="20" width="20" height="20" fill="#7a9fd1" opacity="0.7"/>
                <rect x="0" y="40" width="20" height="20" fill="#7a9fd1" opacity="0.7"/>
                <rect x="0" y="60" width="20" height="20" fill="#7a9fd1" opacity="0.7"/>
                <rect x="0" y="80" width="20" height="20" fill="#7a9fd1" opacity="0.7"/>
              </g>
              <!-- D matrix -->
              <g transform="translate(120, 165)">
                <text x="40" y="14" font-size="9" fill="#888">noise covar D</text>
                <rect x="0" y="20" width="20" height="20" fill="#c879d1" opacity="0.7"/>
                <rect x="20" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="40" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="60" y="20" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="0" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="20" y="40" width="20" height="20" fill="#c879d1" opacity="0.7"/>
                <rect x="40" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="60" y="40" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="0" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="20" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="40" y="60" width="20" height="20" fill="#c879d1" opacity="0.7"/>
                <rect x="60" y="60" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="0" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="20" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="40" y="80" width="20" height="20" fill="#222" opacity="0.5"/>
                <rect x="60" y="80" width="20" height="20" fill="#c879d1" opacity="0.7"/>
              </g>
              <!-- arrows to right side -->
              <line x1="225" y1="60" x2="430" y2="60" stroke="#79c79f" stroke-width="1.4" marker-end="url(#arr3)"/>
              <line x1="225" y1="100" x2="430" y2="140" stroke="#e8b96a" stroke-width="1.4" marker-end="url(#arr3)"/>
              <line x1="225" y1="195" x2="430" y2="220" stroke="#7a9fd1" stroke-width="1.4" marker-end="url(#arr3)"/>
              <line x1="225" y1="225" x2="430" y2="295" stroke="#c879d1" stroke-width="1.4" marker-end="url(#arr3)"/>
              <!-- right side hardware boxes -->
              <g>
                <rect x="430" y="45" width="270" height="34" fill="rgba(121,199,159,0.18)" stroke="#79c79f" rx="3"/>
                <text x="445" y="62" font-size="11" fill="#79c79f" font-weight="600">In-loop intensity modulator (per pulse)</text>
                <text x="445" y="74" font-size="10" fill="#888">cavity loss κᵢ = A_(ii); diagonal damping</text>
                <rect x="430" y="125" width="270" height="34" fill="rgba(232,185,106,0.18)" stroke="#e8b96a" rx="3"/>
                <text x="445" y="142" font-size="11" fill="#e8b96a" font-weight="600">FPGA RAM: M[i,j] = −A_{ij} (off-diag)</text>
                <text x="445" y="154" font-size="10" fill="#888">computes Σⱼ M_(ij) · x_j per pulse i</text>
                <rect x="430" y="205" width="270" height="34" fill="rgba(122,159,209,0.18)" stroke="#7a9fd1" rx="3"/>
                <text x="445" y="222" font-size="11" fill="#7a9fd1" font-weight="600">EOM constant DC bias per pulse</text>
                <text x="445" y="234" font-size="10" fill="#888">imposes drive b_i on pulse i each round-trip</text>
                <rect x="430" y="285" width="270" height="34" fill="rgba(200,121,209,0.18)" stroke="#c879d1" rx="3"/>
                <text x="445" y="302" font-size="11" fill="#c879d1" font-weight="600">Calibrated white-noise generator</text>
                <text x="445" y="314" font-size="10" fill="#888">√(2 dt) · D^½ · ξᵢ injected via EOM</text>
              </g>
            </svg>
            <figcaption style="font-size: 0.85rem; color: var(--page-muted); margin-top: 0.4rem; text-align: center;">
              <strong>Fig.&nbsp;2.</strong> Encoding map. The drift matrix \(A\) splits into a diagonal part (per-pulse loss, realised by a programmable intensity modulator inside the loop, immune to η/τ imperfections) and an off-diagonal part (loaded into FPGA RAM as a coefficient table for the MVM, suffers η/τ). The bias \(b\) and noise covariance \(D\) attach via the same EOM as additional channels.
            </figcaption>
          </figure>
          <p>
            <strong>Why the diagonal/off-diagonal split matters.</strong>
            In the simulator
            <code>HardwareImperfectOUMachine</code> (cim/ou_machine.py:160),
            the hardware decomposition is explicit:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
self._A_diag = torch.diag(torch.diagonal(self._A))   # per-pulse loss (no η, no τ)
self._A_off  = self._A - self._A_diag                # FPGA path (has η, τ)
...
drift = -x @ self._A_diag.T  -  self.eta * (x_delayed @ self._A_off.T)
          </pre>
          <p>
            The diagonal term acts <em>locally</em> on each pulse — no
            cross-pulse coupling, no homodyne, no FPGA round-trip. We
            put it on a dedicated per-pulse intensity modulator inside
            the loop. The off-diagonal term is the only piece that needs
            to leave the loop and traverse the homodyne–FPGA–EOM chain;
            it is therefore the only piece exposed to detection
            efficiency \(\eta\) and feedback delay \(\tau\). Section
            <a href="#envelope">§Envelope</a> quantifies the resulting
            error.
          </p>
          <p>
            <strong>The bias \(b\).</strong> If the user only wants
            samples from \(\mathcal{N}(0,\frac{1}{2}A^{-1})\), set
            \(b = 0\). For the linear-system mode (next section), add a
            constant DC bias to each pulse's EOM injection. Steady-state
            mean is then \(\langle x\rangle_\mathrm{ss} = A^{-1} b\) by
            direct integration of \(\dot x = -A x + b + \mathrm{noise}\).
          </p>
          <p>
            <strong>The noise covariance \(D\).</strong> For the
            simplest case \(D = I\) (uncorrelated unit-variance noise
            on each pulse), the calibrated noise injection is per-pulse
            uncorrelated white Gaussian. Non-isotropic \(D\) requires
            cross-pulse-correlated noise — implementable via a digital
            stochastic injection routed through the FPGA, but more
            elaborate. The published proposal targets \(D = I\) only;
            the result \(\Sigma = \frac{1}{2} A^{-1}\) requires this.
          </p>
          """ + callout(
            "The diagonal-vs-off-diagonal split is the single most "
            "important simplification of the hardware analysis. By "
            "putting <em>A_diag</em> on per-pulse local optics and only "
            "<em>A_off</em> through the FPGA loop, we make η and τ "
            "imperfections affect only off-diagonal coupling — never "
            "the dominant self-damping. This is why the η-axis "
            "correction is exact and not multiplicative."
          ),
         ["A_diag → per-pulse loss (η, τ-immune)",
          "A_off → FPGA RAM (η, τ-affected)",
          "b → EOM DC bias (linear-system mode)",
          "D → calibrated white-noise gain"]),
        ("readout-protocols", "Readout: Three Measurements, Three Primitives", r"""
          <p class="lede">
            The same hardware substrate produces three different
            primitives depending on what we record. The dynamics is
            always the same SDE; the difference is in
            post-processing.
          </p>
          <figure style="margin: 1rem 0;">
            <div style="display: grid; grid-template-columns: minmax(180px, 240px) 1fr; gap: 1rem; align-items: stretch; background: var(--page-bg); border: 1px solid var(--page-rule); border-radius: 6px; padding: 1rem;">
              <!-- LEFT: small SVG showing the OU loop (no math inside SVG) -->
              <div style="display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <svg viewBox="0 0 240 280" xmlns="http://www.w3.org/2000/svg" style="width: 100%; height: auto;">
                  <text x="120" y="20" text-anchor="middle" font-size="13" font-weight="600" fill="#888">OU loop running</text>
                  <ellipse cx="120" cy="140" rx="95" ry="48" fill="none" stroke="#888" stroke-width="1.4"/>
                  <text x="120" y="143" text-anchor="middle" font-size="10" fill="#888">x_i(t) circulating</text>
                  <circle cx="48" cy="148" r="3" fill="#79c79f"/><circle cx="82" cy="100" r="3" fill="#79c79f"/>
                  <circle cx="160" cy="100" r="3" fill="#79c79f"/><circle cx="195" cy="148" r="3" fill="#79c79f"/>
                  <line x1="120" y1="190" x2="120" y2="225" stroke="#888" stroke-width="0.8" stroke-dasharray="3,3"/>
                  <text x="120" y="245" text-anchor="middle" font-size="11" fill="#888">→ photocurrent x_i(t)</text>
                  <text x="120" y="265" text-anchor="middle" font-size="9" fill="#888" font-style="italic">same SDE; differing</text>
                  <text x="120" y="276" text-anchor="middle" font-size="9" fill="#888" font-style="italic">post-processing</text>
                </svg>
              </div>
              <!-- RIGHT: HTML stack of four mode boxes; KaTeX renders math here -->
              <div style="display: grid; gap: 0.5rem; font-size: 0.92rem;">
                <div style="background: rgba(122,159,209,0.10); border: 1px solid #7a9fd1; border-radius: 4px; padding: 0.6rem 0.8rem;">
                  <div style="color: #7a9fd1; font-weight: 600; margin-bottom: 0.25rem;">Mode 1 — Linear solve \(A v = b\)</div>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">Drive each pulse with constant DC bias \(b_i\). Record time-averaged photocurrent.</p>
                  <p style="margin: 0.15rem 0; font-style: italic;">\(v_i = \langle x_i \rangle\) averaged over \(T_\mathrm{record} \gg T_\mathrm{mix}\)&nbsp;&nbsp;\(\Rightarrow\)&nbsp;&nbsp;\(v = A^{-1} b\)</p>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">Sample efficiency: \(\mathcal{O}(1/\varepsilon^2)\) round-trips for \(\varepsilon\) relative error.</p>
                </div>
                <div style="background: rgba(232,185,106,0.10); border: 1px solid #e8b96a; border-radius: 4px; padding: 0.6rem 0.8rem;">
                  <div style="color: #e8b96a; font-weight: 600; margin-bottom: 0.25rem;">Mode 2 — Diagonal \(\tfrac{1}{2}A^{-1}\), trace \(\mathrm{Tr}(A^{-1})\)</div>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">No drive (\(b = 0\)). Record per-pulse variance \(\langle x_i^2 \rangle\).</p>
                  <p style="margin: 0.15rem 0; font-style: italic;">\(\Sigma_{ii} = \langle x_i^2 \rangle = \tfrac{1}{2}(A^{-1})_{ii}\)&nbsp;&nbsp;\(\Rightarrow\)&nbsp;&nbsp;\(\mathrm{Tr}(A^{-1}) = 2\sum_i \langle x_i^2 \rangle\)</p>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">Use case: log-evidence in Bayesian model comparison.</p>
                </div>
                <div style="background: rgba(121,199,159,0.10); border: 1px solid #79c79f; border-radius: 4px; padding: 0.6rem 0.8rem;">
                  <div style="color: #79c79f; font-weight: 600; margin-bottom: 0.25rem;">Mode 3 — Full \(\tfrac{1}{2}A^{-1}\) / Gaussian sampling</div>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">No drive. Record cross-correlations \(\langle x_i x_j \rangle\) across all pulse pairs.</p>
                  <p style="margin: 0.15rem 0; font-style: italic;">\(\hat\Sigma = M / N_\mathrm{samples}\), with \(M \mathrel{+}= x x^\mathrm{T}\) each round-trip; \(A^{-1} \approx 2\hat\Sigma\).</p>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">Use case: posterior sampling, full GP inference.</p>
                </div>
                <div style="background: rgba(200,121,209,0.10); border: 1px solid #c879d1; border-radius: 4px; padding: 0.6rem 0.8rem;">
                  <div style="color: #c879d1; font-weight: 600; margin-bottom: 0.25rem;">Mode 4 (bonus) — \(\log \det A\) from cumulative EOM work</div>
                  <p style="margin: 0.15rem 0; font-size: 0.88rem; color: var(--page-muted);">Aifer-Coles-Duffield 2023; same loop, integrate the work done by the feedback drive over a quasi-static schedule. Output: \(\tfrac{1}{2}\log\det A\) up to a constant.</p>
                </div>
              </div>
            </div>
            <figcaption style="font-size: 0.85rem; color: var(--page-muted); margin-top: 0.4rem; text-align: center;">
              <strong>Fig.&nbsp;3.</strong> Three readout protocols on one substrate. The dynamics is identical in all four cases — only the post-processing of the photocurrent stream differs.
            </figcaption>
          </figure>
          <p>
            <strong>Mode 1 — Linear solve.</strong> The EOM imposes a
            constant DC bias \(b_i\) on each pulse per round-trip. The
            full SDE is \(dx = (-Ax + b)\,dt + \sqrt{2D}\,dW\), whose
            stationary mean is \(\langle x\rangle_\mathrm{ss} = A^{-1}b\)
            (set \(\dot{\langle x\rangle} = 0\)). Read off the
            time-averaged photocurrent on each pulse — that is the
            answer. <em>This is how the RLC SPU operates</em>: drive,
            then read the steady-state node voltages. It is the natural
            optical mode for "I have a one-shot \(b\), give me
            \(A^{-1}b\) at hardware speed."
          </p>
          <p>
            <strong>Mode 2 — Diagonal of the inverse.</strong> The
            per-pulse variance \(\langle x_i^2\rangle\) is exactly
            \(\frac{1}{2}(A^{-1})_{ii}\). Summing across pulses gives
            \(\mathrm{Tr}(A^{-1}) = 2\sum_i \langle x_i^2\rangle\) at
            essentially zero post-processing cost — the photodetector
            current squared, integrated. This trace appears in
            log-evidence calculations for Bayesian model comparison
            and in regularization-parameter selection.
          </p>
          <p>
            <strong>Mode 3 — Full covariance.</strong> Streaming
            accumulator \(M \mathrel{+}= x x^\mathrm{T}\) per round-trip
            (FPGA-side, O(d²) MAC ops); divide by sample count to get
            \(\hat\Sigma\); multiply by 2 to get \(A^{-1}\). The mode
            this entire note is built around. The simulator's
            <code>OUMachine.run</code> implements exactly this
            (cim/ou_machine.py:140).
          </p>
          <p>
            <strong>Mode 4 — log-det.</strong> The Aifer-Coles-Duffield
            trick (arXiv:2306.14740, §III.B): drive a quasi-static ramp
            of an auxiliary parameter, integrate the work done by the
            feedback drive, and the cumulative work equals
            \(\frac{1}{2} \log\det A\) up to thermal-bath constants.
            Same hardware, no extra components, just a careful
            calibration of the integrator.
          </p>
          """ + callout(
            "On the bench, you choose the readout mode by what you wire "
            "<em>after</em> the homodyne ADC, not by what the optics is "
            "doing. All four modes can run in parallel on the same "
            "trajectory if you have enough digital readout channels — "
            "this is the deepest reason the OU machine is "
            "<em>portfolio</em> hardware, not single-purpose."
          ),
         ["Linear solve: drive with b, read mean → \\(A^{-1}b\\)",
          "Trace mode: per-pulse variance → \\(\\mathrm{Tr}(A^{-1})\\)",
          "Full covariance: cross-correlation → \\(\\frac{1}{2}A^{-1}\\)",
          "log det A: cumulative work, ACD trick"]),
        ("simulator-diff", "Simulator: cim-optimizer Fork in 50 Lines", r"""
          <p class="lede">
            The
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            package implements both the ideal OU machine
            (<code>OUMachine</code>) and a hardware-imperfect variant
            (<code>HardwareImperfectOUMachine</code>) that exposes the
            three knobs from §<a href="#envelope">Envelope</a>: detection
            efficiency \(\eta\), feedback delay \(\tau\), and
            measurement shot noise \(\sigma_\mathrm{meas}\). Both fork
            cleanly from the McMahon Lab cim-optimizer's AHC.py update
            step.
          </p>
          <p>
            <strong>The original (cim-optimizer/AHC.py:130–133).</strong>
            One Euler step of the MFB-CIM:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
MVM = x @ J                                                    # FPGA matrix-vector multiply
x += time_step * (x * ((r[t] - 1) - mu * x_squared))           # gain (above thr.) - cubic saturation
x += time_step * eps[t] * (MVM * error_var)                    # measurement-feedback injection
x += eps[t] * noise * (torch.rand(N) - 0.5)                    # uniform stochastic noise
          </pre>
          <p>
            <strong>The OU fork (cim/ou_machine.py:99–109).</strong>
            One Euler step of the OU machine:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
def step(self, x: Tensor) -&gt; Tensor:
    # One Euler-Maruyama step:
    #   x_{n+1} = (I - A·dt) x_n  +  sqrt(dt) · D^(1/2) · xi_n
    drift = -x @ self._A.T                                     # FPGA + per-pulse loss combined
    xi = torch.randn(x.shape, generator=self._rng, ...)        # standard Gaussian draw
    diffusion = (xi @ self._D_chol.T) * (self.dt**0.5)         # Cholesky-shaped white noise
    return x + drift * self.dt + diffusion
          </pre>
          <p>
            The <em>hardware-imperfect</em> version (cim/ou_machine.py:160)
            adds the (η, τ, σ_meas) knobs and decomposes the drift to
            mirror the diagonal-vs-off-diagonal split:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
# In __init__:
self._A_diag = torch.diag(torch.diagonal(self._A))         # per-pulse loss (immune)
self._A_off  = self._A - self._A_diag                      # FPGA path (η, τ-affected)

# In the run loop:
delay_buffer.append(x_seen)                                # FIFO of past measurements
x_delayed = delay_buffer[0]                                # x_seen[n − tau_steps]
drift = -x @ self._A_diag.T  -  self.eta * (x_delayed @ self._A_off.T)
xi = torch.randn(x.shape, ...)
diffusion = (xi @ self._D_chol.T) * (self.dt**0.5)
x = x + drift * self.dt + diffusion
          </pre>
          <p>
            <strong>The accumulator</strong> (cim/ou_machine.py:147–150)
            is what makes this a Lyapunov sampler rather than just an
            Euler integrator:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
M = torch.zeros((d, d))                                    # streaming covariance
for n in range(n_rounds):
    x = self.step(x)
    if n &gt;= n_burn_in:
        M += x.T @ x                                       # accumulator
sigma_hat = M / (batch * (n_rounds - n_burn_in))           # ½ A⁻¹ for D=I
          </pre>
          """ + math_details("Why this is the right discretization", r"""
            <p>
              Discretizing \(dx = -A x\,dt + \sqrt{2D}\,dW\) by
              explicit Euler-Maruyama gives
              \(x_{n+1} = x_n - A x_n \Delta t + \sqrt{\Delta t}\,B \xi_n\)
              with \(B B^\mathrm{T} = 2D\) (we use \(B = \sqrt{2D}\)
              symmetric). The continuous-time stationary covariance
              \(\Sigma_\infty\) solves \(A\Sigma + \Sigma A^\mathrm{T} = 2D\);
              the discrete-time stationary covariance solves an analogous
              equation with extra terms in \((A\Delta t)^2\). For
              \(\Delta t \cdot \lambda_\mathrm{max}(A) \ll 1\), the
              two coincide to leading order.
            </p>
            <p>
              <strong>Stability constraint</strong>:
              \(\Delta t < 2/\lambda_\mathrm{max}(A)\) (else the explicit
              Euler diverges). For normalized \(A\) with
              \(\lambda_\mathrm{max} = 1\), this is \(\Delta t < 2\). The
              simulator's default \(\Delta t = 0.02\) is well inside.
            </p>
            <p>
              <strong>Variance bias from finite \(\Delta t\)</strong>:
              the discrete steady-state has
              \(\Sigma_\Delta = \Sigma_\infty + O(\Delta t)\). For
              \(\Delta t = 0.02\) and well-conditioned \(A\), this is
              ~1% bias on \(\Sigma\) — folded into the verification
              tolerance.
            </p>
          """) + r"""
          <p>
            <strong>The verification grid</strong>
            (cim/<code>experiments/exp02_ou_lyapunov.py</code>): for
            each cell of \(d \in \{4, 8, 16\}\) and
            \(\kappa \in \{1, 10, 100\}\), draw a random PD matrix
            \(A\), run the simulator to stationarity, compare
            \(\hat\Sigma\) against
            <code>scipy.linalg.solve_continuous_lyapunov</code>. Worst-case
            cell hits 2.7% relative Frobenius error; all cells pass
            the 5% acceptance threshold. The error grid is the
            headline figure of the
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            repo's notebook 02.
          </p>
          <p>
            <strong>What you would actually run on bench</strong>
            (vs the simulator). Most of the simulator code maps to
            firmware on a programmable FPGA: load the matrix
            \(-A_\mathrm{off}\) into MVM RAM (one-time), set the
            per-pulse loss controls to encode \(A_\mathrm{diag}\),
            apply constant DC bias \(b\) (if any) on the EOM,
            calibrate the noise generator to match \(D\). The
            accumulator \(M \mathrel{+}= x x^\mathrm{T}\) runs on the
            same FPGA in parallel with the dynamics; one read-out
            register per cell of the empirical covariance. <em>Total
            firmware effort: ~1000 lines of HDL, derived directly from
            the Python simulator</em>.
          </p>
          """ + callout(
            "The simulator is <em>not</em> a separate scientific "
            "artifact — it is a <em>specification</em> of the firmware "
            "that runs on bench. Every line of <code>cim/ou_machine.py</code> "
            "has a one-to-one mapping to either an FPGA module or a "
            "passive optical element. This is by design: the proposal "
            "is for a 1-to-1 hardware port of a working simulator, not "
            "a research project to figure out what the SDE ought to be."
          ),
         ["Three-line firmware diff from cim-optimizer/AHC.py",
          "OUMachine.step ↔ one optical round-trip",
          "Accumulator \\(M += x x^T\\) on FPGA in parallel",
          "Verification: \\(\\hat\\Sigma \\to \\frac{1}{2}A^{-1}\\) within 3%"]),
        ("rlc-comparison", "Comparison: RLC SPU vs Optical OU Machine", r"""
          <p class="lede">
            Normal Computing's RLC stochastic processing unit (Aifer
            et al., <em>Nat. Commun.</em> 2025) is the existing,
            demonstrated, electronic instance of the same primitive.
            Why optical, given that RLC works?
          </p>
          <table class="refs">
            <tr><td><strong>Axis</strong></td><td><strong>RLC SPU</strong></td><td><strong>Optical OU</strong></td></tr>
            <tr><td>Substrate</td><td>resistors-inductors-capacitors</td><td>fiber-loop pulses + FPGA</td></tr>
            <tr><td>Encoding</td><td>passive analog (RC time constants set drift)</td><td>digital firmware on FPGA + optical loop</td></tr>
            <tr><td>Reconfigurability</td><td>Patch-board topology change for different \(A\)</td><td>FPGA firmware update</td></tr>
            <tr><td>Demonstrated d</td><td>8</td><td>32 (sim) / TBD on bench</td></tr>
            <tr><td>Noise floor</td><td>thermal Johnson noise \(\sim k_B T R\)</td><td>vacuum shot noise \(\sim \hbar\omega\)</td></tr>
            <tr><td>Power per MVM</td><td>~ pJ (passive, plus readout)</td><td>~ nJ (FPGA + optical loop)</td></tr>
            <tr><td>Latency per MVM</td><td>~ μs (RC settling)</td><td>~ ns (round-trip)</td></tr>
            <tr><td>Mature year</td><td>2024–2025</td><td>2026 + (in proposal)</td></tr>
          </table>
          <p>
            The economic argument: <em>RLC is better in steady-state
            energy efficiency; optical is better in latency per update,
            and by 2–3 orders of magnitude</em>. For applications where
            wall-clock matters (real-time Bayesian inference, online
            learning), optical wins. For batch jobs where you can
            wait microseconds per MVM, RLC is more efficient.
          </p>
          <p>
            <strong>Engineering risk inherited from CIM</strong>: the
            optical OU machine reuses the entire MFB-CIM substrate
            (Note 06). Every component has flight heritage at scale.
            The risk is not "build new hardware"; it is "characterize
            a different operating regime of an existing hardware
            class". This <em>de-risking</em> argument is the
            single-most-important reason to run the optical proposal in
            parallel with continued RLC investment.
          </p>
          """ + callout(
            "An honest comparison concludes RLC and optical OU are not "
            "competitors but complements. RLC: low-power, low-rate, "
            "edge inference. Optical: high-throughput, high-dimension, "
            "datacenter inference. <em>Both</em> belong in a complete "
            "thermodynamic-linear-algebra portfolio."
          ),
         ["RLC: better steady-state energy",
          "Optical: better latency, 2-3 OOM",
          "CIM heritage: low risk on hardware, high risk on regime"]),
        ("envelope", "Hardware Imperfection Envelope (η, τ, σ_meas)", r"""
          <p>
            Three knobs determine bench performance:
          </p>
          <ol>
            <li><strong>Homodyne efficiency</strong> \(\eta\): the
              detected fraction of the signal photocurrent. Reduces the
              FPGA-implemented coupling. The drift matrix actually
              realized is
              \(A_\mathrm{eff} = A_\mathrm{diag} + \eta\,A_\mathrm{off}\)
              (where \(A_\mathrm{off}\) is the off-diagonal part) —
              <em>exactly</em>, no envelope-approximation. The
              steady-state \(\hat\Sigma\) solves the Lyapunov equation
              with this <em>wrong</em> matrix.</li>
            <li><strong>Feedback delay</strong> \(\tau\): the time
              between the homodyne measurement and the EOM injection.
              Turns the dynamics into a delay-differential equation.
              Subleading in the overdamped regime; we measure the
              slope empirically.</li>
            <li><strong>Measurement shot noise</strong> \(\sigma_\mathrm{meas}\):
              additive Gaussian noise on the photocurrent. Inflates
              the effective diffusion: \(D_\mathrm{eff} = D + (\eta\zeta\sigma_\mathrm{meas})^2\,A_\mathrm{off}A_\mathrm{off}^T\).
              Costs sample-efficiency, not encoding correctness.</li>
          </ol>
          <p>
            <strong>Important correction.</strong> An earlier draft of
            this proposal claimed the envelope was multiplicative:
            \(f_\mathrm{eff} = \eta\,e^{-\gamma\tau}\). That formula
            is the <em>underdamped</em> Wiseman-Milburn result and
            does not transfer to the overdamped case. For overdamped
            OU, the η-axis is exact (not an envelope), the τ-axis is
            sub-linear additive. The hardware-envelope experiment in
            the
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            repo caught this; the corrected story replaces the earlier
            multiplicative envelope.
          </p>
          """ + widget_shell(
            anchor="eta-tau-envelope",
            title="Interactive: (η, γτ) feasibility envelope",
            blurb=(
              "2D envelope plot in the (homodyne-efficiency η, "
              "feedback-delay γτ) plane. Dot color shows expected "
              "Frobenius error in <em>Σ̂</em> vs the ideal Lyapunov "
              "solution. Click anywhere to read off the value. The "
              "Practical/Stretch/Loose target boxes are overlaid; the "
              "FPGA-latency wall at γτ ≈ 10 is the dashed line."
            ),
            controls_html=(
              slider(var="env-d", label="dimension d", min_=4, max_=64,
                     step=4, value=16, fmt="{:d}".replace(":d}", ":.0f}"))
            ),
            canvas_html=svg_el("eta-tau-envelope", w=520, h=320),
            readout_html='<span id="eta-tau-readout">Click anywhere on the plot.</span>',
          ) + r"""
          """ + math_details("Where these scaling expressions come from", r"""
            <p>
              For the η-axis: the FPGA realises
              \(J_\mathrm{eff} = \eta J\) on the off-diagonal coupling
              (since the homodyne returns \(\eta x\) instead of \(x\)).
              Substituting back into the Euler step shows the dynamics
              has effective drift
              \(A_\mathrm{eff}(\eta) = \mathrm{diag}(A) + \eta\,(A - \mathrm{diag}(A))\).
              The steady-state \(\hat\Sigma(\eta)\) solves
              \(A_\mathrm{eff}\hat\Sigma + \hat\Sigma A_\mathrm{eff}^T = D\)
              <em>exactly</em>: there is no perturbative envelope, just
              a different operator.
            </p>
            <p>
              For the τ-axis: an explicit-Euler integration of a
              delay-differential equation
              \(\dot x = -A_\mathrm{eff}\,x(t-\tau) + \xi\) with a
              one-step delay \(\tau\) of order the round-trip time has
              leading-order error
              \(\delta\Sigma = O(\gamma\tau \cdot \Sigma)\) for
              \(\gamma\tau \ll 1\), where \(\gamma\) is the slowest
              eigenvalue of \(A_\mathrm{eff}\). This is sub-linear
              additive — not the multiplicative \(e^{-\gamma\tau}\)
              that would obtain in the underdamped Wiseman-Milburn
              regime.
            </p>
          """),
         ["η: exact steady-state shift, no envelope",
          "τ: sub-linear additive correction",
          "σ_meas: inflates diffusion, no encoding bias",
          "FPGA latency = the load-bearing wall"]),
        ("targets", "QCi-Actionable Target Table", r"""
          <table class="refs">
            <tr><td><strong>Target</strong></td><td><strong>Encoding error</strong></td><td><strong>η</strong></td><td><strong>γτ</strong></td><td><strong>Realization</strong></td></tr>
            <tr><td>Stretch</td><td>≤ 5%</td><td>≥ 0.99</td><td>≤ 0.05</td><td>analog-RF hybrid; γ ≤ 50 MHz</td></tr>
            <tr><td>Practical</td><td>≤ 10%</td><td>≥ 0.95</td><td>≤ 0.20</td><td>SNSPD + sub-ns FPGA; γ = 200 MHz</td></tr>
            <tr><td>Loose</td><td>≤ 20%</td><td>≥ 0.85</td><td>≤ 0.50</td><td>commodity PIN diode + standard FPGA</td></tr>
          </table>
          <p>
            The <strong>load-bearing assumption</strong> is FPGA-MVM
            latency at target dimension \(d\). Optical insertion loss
            and detector quantum efficiency can be improved with
            engineering money. FPGA latency is structural — a CMOS
            FPGA running a serialized MVM at \(d=64\) is typically
            \(\sim 50\) ns, which is γτ ≈ 10 at γ = 200 MHz, far
            outside the Practical envelope. Reaching γτ ≤ 0.1 at
            d=64 likely requires either an analog-electronic feedback
            (resistor-based MAC, no digitization) or a purpose-built
            RF pipeline.
          </p>
          <p>
            <strong>The single most important conversation to have
            with a hardware partner is FPGA-MVM-latency-at-target-d.</strong>
            The full noise-budget breakdown lives in the
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            repository.
          </p>
          """,
         ["Practical target: η ≥ 0.95, γτ ≤ 0.20, error ≤ 10%",
          "FPGA MVM latency is the structural bottleneck",
          "Analog-electronic feedback is the natural fallback"]),
        ("roadmap", "Roadmap: Overdamped → Underdamped √κ", r"""
          <p>
            The current proposal (this note) is the <strong>overdamped
            stepping-stone</strong>: linear damping, mixing time
            \(T_\mathrm{mix} \propto 1/\lambda_\mathrm{min}(A) = \kappa\).
            For ill-conditioned problems (κ ≫ 1) this is slow.
          </p>
          <p>
            The <strong>underdamped variant</strong> (parallel theory
            project, Direction A) replaces overdamped Langevin with a
            symplectic Hamiltonian-plus-friction system: separated X
            and P quadratures with momentum, friction tuned to match
            the slowest mode. The mixing time is
            \(T_\mathrm{mix} \propto 1/\sqrt{\lambda_\mathrm{min}} = \sqrt{\kappa}\).
            For κ = 100, this is a 10× speedup. For κ = 10⁴, it's
            100×.
          </p>
          <p>
            The hardware substrate is unchanged: still time-multiplexed
            pulses, still homodyne + FPGA + EOM. The change is that
            the FPGA tracks <em>two</em> quadratures per pulse (X and
            P) and implements the symplectic update equation. This
            requires below-threshold OPO operation (so that quantum
            noise on P is well-defined) and Wiseman-Milburn feedback
            on the homodyne measurement.
          </p>
          <p>
            The full derivation, simulation, and hardware spec table
            are part of the underdamped <em>Direction&nbsp;A</em>
            research effort — paper in preparation.
          </p>
          """ + callout(
            "The √κ advantage is the killer feature. Overdamped is the "
            "stepping-stone we de-risk on; underdamped is the asymptotic "
            "win. They share hardware. <em>The right way to think about "
            "this proposal is: the bench we build for overdamped <strong>is</strong> "
            "the bench that runs underdamped, with a firmware update.</em>"
          ) + widget_shell(
            anchor="mixing-time-scaling",
            title="Interactive: T_mix vs κ scaling",
            blurb=(
              "The empirical mixing-time-vs-condition-number scaling "
              "from <a href=\"https://github.com/nez0b/cim-spu-optical-simulation\">"
              "cim-spu-optical-simulation</a> notebook 02. Slide κ to "
              "see how each algorithm scales: overdamped "
              "<em>T<sub>mix</sub></em> ∝ κ (empirical α ≈ 0.93), "
              "underdamped <em>T<sub>mix</sub></em> ∝ √κ (theory; "
              "Direction A measurement pending). Log–log axes."
            ),
            controls_html=slider(var="mix-kappa", label="condition κ", min_=1,
                                 max_=200, step=1, value=20, fmt="{:.0f}"),
            canvas_html=svg_el("mixing-time-scaling", w=520, h=320),
            readout_html=(
              '<div>Overdamped T_mix at κ: <span id="mix-over">—</span></div>'
              '<div>Underdamped T_mix at κ: <span id="mix-under">—</span></div>'
              '<div>Speedup ratio: <span id="mix-ratio">—</span></div>'
            ),
          ) + r"""
          """,
         ["Overdamped: \\(T_\\mathrm{mix} \\propto \\kappa\\)",
          "Underdamped (Direction A): \\(T_\\mathrm{mix} \\propto \\sqrt\\kappa\\)",
          "Same hardware, firmware-distinguished operating regimes",
          "Empirical α=0.93 (overdamped) vs theory α=1"]),
        ("open", "Open Questions", r"""
          <ol>
            <li><strong>Scaling to d ≥ 64.</strong> The simulator
              currently caps at d = 16 on CPU; a GPU port is the next
              deliverable, including a wallclock benchmark vs scipy
              and torch.</li>
            <li><strong>Joint η-τ envelope</strong>: the additive
              decomposition is empirical at d=4. Testing across a
              range of <em>A</em> structures (random PD,
              graph-Laplacian, Hessian-of-MLE) would establish the
              general envelope shape.</li>
            <li><strong>Non-symmetric Hurwitz <em>A</em></strong>: real
              workloads (Markov-chain rates, asymmetric Jacobians)
              are non-symmetric. Recipe table for choosing \(D\) such
              that \(\Sigma\) encodes the desired functional of \(A\)
              — needs derivation.</li>
            <li><strong>Application demo</strong>: Bayesian linear
              regression posterior covariance is the cleanest
              end-to-end use of the OU sampler. Notebook 04 in
              <code>cim-spu-optical-simulation</code> (planned, see
              handoff.md Step 4).</li>
            <li><strong>Direct head-to-head with Normal Computing's
              RLC SPU</strong> on their published 8×8 instances
              (handoff.md Step 2). Direct competitive claim or
              reframing.</li>
            <li><strong>Quantum advantage at threshold?</strong> The
              CIM literature (Note 06) has been arguing this for
              two decades. For the OU machine specifically, the
              squeezing-advantage path is closed (Direction B
              killshot); but the MFB-controlled below-threshold
              regime (where the dynamics is genuinely quantum) is
              not yet ruled out as a source of advantage on
              specific problem classes.</li>
          </ol>
          """,
         ["GPU scaling to d ≥ 64 is next on the queue",
          "Non-symmetric A is the natural generalization",
          "Bayesian regression is the end-to-end demo"]),
        ("sources", "Sources &amp; Further Reading", r"""
          <table class="refs">
            <tr><td>Project</td><td><a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a> — live repo: simulator, notebooks, experiments, hardware-envelope analysis</td></tr>
            <tr><td>Paper</td><td>Aifer, Duffield, Coles, et al., "Thermodynamic Linear Algebra", arXiv:2306.14740 (2023); <em>npj Unconventional Computing</em> (2024)</td></tr>
            <tr><td>Paper</td><td>Aifer et al., 8-cell RLC SPU hardware demo, <em>Nat. Commun.</em> (2025)</td></tr>
            <tr><td>Code</td><td><a href="https://github.com/mcmahon-lab/cim-optimizer">mcmahon-lab/cim-optimizer</a> — the AHC.py update step that the OU machine forks from</td></tr>
            <tr><td>Reference</td><td>Wiseman &amp; Milburn, <em>Quantum Measurement and Control</em>, Ch. 5 (continuous measurement; underdamped envelope)</td></tr>
            <tr><td>Project</td><td>Underdamped <em>Direction&nbsp;A</em> research — paper in preparation</td></tr>
          </table>
          <p class="pre-req">
            <strong>End of track.</strong> The seven notes above are
            the foundational + applied path from quantum-optics
            primitives (coherent states, beam splitters, OPOs) through
            the Coherent Ising Machine to the in-progress optical-SPU
            research direction. Subsequent material will live in the
            live repo at
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>.
          </p>
          """,
         ["Live repo: cim-spu-optical-simulation",
          "Aifer-Coles-Duffield 2023: TLA framing",
          "End of track — research continues in the cim repo"]),
    ],
    "scripts": script_block(r"""
      // -- Widget: 4-D OU machine convergence ---------------------------
      (function () {
        var svg = document.getElementById('lyapunov-sampler-svg');
        if (!svg) return;
        var kappaS = document.getElementById('lya-kappa');
        var dtS = document.getElementById('lya-dt');
        var kappaV = document.getElementById('lya-kappa-val');
        var dtV = document.getElementById('lya-dt-val');
        var errSpan = document.getElementById('lya-err');
        var stepSpan = document.getElementById('lya-step');
        var runBtn = document.getElementById('lya-run');
        var resetBtn = document.getElementById('lya-reset');
        var d = 4;
        var x = new Float64Array(d);
        var sumX = new Float64Array(d);
        var sumXX = new Float64Array(d*d);
        var step = 0, MAX = 1500, raf = null;
        var errHistory = [];
        var A = null, Ainv = null;

        function buildA(kappa) {
          // diagonal A with eigenvalues 1/kappa, ..., 1, normalized so λ_max=1
          A = new Float64Array(d*d);
          Ainv = new Float64Array(d*d);
          for (var i = 0; i < d; i++) {
            // eigenvalue: linspace from 1/kappa to 1
            var lambda_i = (1.0/kappa) + (1 - 1/kappa) * (i / (d-1));
            A[i*d + i] = lambda_i;
            Ainv[i*d + i] = 1 / lambda_i;
          }
        }
        function reset() {
          step = 0;
          for (var i = 0; i < d; i++) { x[i] = 0; sumX[i] = 0; }
          for (var i = 0; i < d*d; i++) sumXX[i] = 0;
          errHistory = [];
          if (raf) { cancelAnimationFrame(raf); raf = null; }
          buildA(parseFloat(kappaS.value));
          render();
        }
        function gauss() {
          var u = 0, v = 0;
          while(u===0) u = Math.random();
          while(v===0) v = Math.random();
          return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);
        }
        function doStep() {
          if (step >= MAX) return;
          var dt = parseFloat(dtS.value);
          // dx = -A x dt + sqrt(2 dt) ξ  (so D = 2I, Σ = A^{-1})
          for (var i = 0; i < d; i++) {
            var drift = 0;
            for (var j = 0; j < d; j++) drift += A[i*d+j] * x[j];
            x[i] += -drift * dt + Math.sqrt(2*dt) * gauss();
          }
          // accumulate covariance estimate
          for (var i = 0; i < d; i++) {
            sumX[i] += x[i];
            for (var j = 0; j < d; j++) sumXX[i*d+j] += x[i] * x[j];
          }
          step++;
          // Frobenius error of (Σ̂ − A^{-1}) every 5 steps; convention here
          // D=2I so target is Σ = A^{-1} (not ½A^{-1}).
          if (step % 5 === 0 || step === 1) {
            var err = 0;
            for (var i = 0; i < d; i++) {
              for (var j = 0; j < d; j++) {
                var sigma_hat = sumXX[i*d+j] / step - (sumX[i]/step)*(sumX[j]/step);
                var target = Ainv[i*d+j];
                err += (sigma_hat - target)*(sigma_hat - target);
              }
            }
            err = Math.sqrt(err);
            errHistory.push({s: step, e: err});
          }
          render();
        }
        function loop() {
          for (var k = 0; k < 5; k++) doStep();
          if (step < MAX && raf !== null) {
            raf = requestAnimationFrame(loop);
          } else {
            raf = null;
          }
        }
        function render() {
          kappaV.textContent = parseFloat(kappaS.value).toFixed(1);
          dtV.textContent = parseFloat(dtS.value).toFixed(3);
          var W = 520, H = 260, pad = 50;
          var inner_w = W - 2*pad, inner_h = H - 2*pad;
          var html = '';
          html += '<text x="' + (W/2) + '" y="' + (pad/2) + '" text-anchor="middle" font-size="11" fill="#888">Frobenius error vs steps (log scale)</text>';
          html += '<line x1="' + pad + '" y1="' + (pad+inner_h) + '" x2="' + (W-pad) + '" y2="' + (pad+inner_h) + '" stroke="#666"/>';
          html += '<line x1="' + pad + '" y1="' + pad + '" x2="' + pad + '" y2="' + (pad+inner_h) + '" stroke="#666"/>';
          if (errHistory.length > 1) {
            var maxE = -Infinity, minE = Infinity;
            for (var k = 0; k < errHistory.length; k++) {
              var le = Math.log10(Math.max(errHistory[k].e, 1e-3));
              if (le > maxE) maxE = le;
              if (le < minE) minE = le;
            }
            if (maxE - minE < 0.5) maxE = minE + 0.5;
            var pts = errHistory.map(function (pt) {
              var px = pad + (pt.s / MAX) * inner_w;
              var le = Math.log10(Math.max(pt.e, 1e-3));
              var py = pad + inner_h * (1 - (le - minE)/(maxE - minE));
              return px + ',' + py;
            }).join(' ');
            html += '<polyline points="' + pts + '" fill="none" stroke="#79c79f" stroke-width="1.8"/>';
            html += '<text x="' + (pad-4) + '" y="' + (pad+8) + '" text-anchor="end" font-size="10" fill="#888">10^' + maxE.toFixed(1) + '</text>';
            html += '<text x="' + (pad-4) + '" y="' + (pad+inner_h) + '" text-anchor="end" font-size="10" fill="#888">10^' + minE.toFixed(1) + '</text>';
            html += '<text x="' + (pad+inner_w) + '" y="' + (H-pad/2) + '" text-anchor="end" font-size="10" fill="#888">step ' + MAX + '</text>';
          } else {
            html += '<text x="' + (W/2) + '" y="' + (H/2) + '" text-anchor="middle" font-size="11" fill="#888">press <em>Run</em> to begin</text>';
          }
          svg.innerHTML = html;
          var lastErr = errHistory.length ? errHistory[errHistory.length-1].e : 0;
          errSpan.textContent = lastErr.toFixed(4);
          stepSpan.textContent = step;
        }
        runBtn.addEventListener('click', function () {
          if (step >= MAX) reset();
          if (raf === null) { raf = requestAnimationFrame(loop); }
        });
        resetBtn.addEventListener('click', reset);
        kappaS.addEventListener('input', reset);
        dtS.addEventListener('input', function () {
          dtV.textContent = parseFloat(dtS.value).toFixed(3);
        });
        reset();
      })();

      // -- Widget: (η, γτ) feasibility envelope -------------------------
      (function () {
        var svg = document.getElementById('eta-tau-envelope-svg');
        if (!svg) return;
        var dS = document.getElementById('env-d');
        var dV = document.getElementById('env-d-val');
        var readout = document.getElementById('eta-tau-readout');
        function buildPlot(d_dim, click_eta, click_gtau) {
          var W = 520, H = 320, pad = 56;
          var inner_w = W - 2*pad, inner_h = H - 2*pad;
          // η ∈ [0.5, 1], γτ ∈ [0, 12] log-ish; we'll use linear γτ for clarity
          var ETA_MIN = 0.5, ETA_MAX = 1.0;
          var GT_MIN = 0, GT_MAX = 12;
          var html = '';
          // background heatmap: error model
          // err(η, γτ, d) ≈ 0.5*(1-η) + 0.04*γτ * sqrt(d/16)
          var step = 12;
          for (var px = pad; px < W-pad; px += step) {
            for (var py = pad; py < H-pad; py += step) {
              var eta = ETA_MIN + (px-pad)/inner_w * (ETA_MAX - ETA_MIN);
              var gt = GT_MAX - (py-pad)/inner_h * (GT_MAX - GT_MIN);
              var err = 0.5*(1-eta) + 0.04*gt * Math.sqrt(d_dim/16);
              var v = Math.max(0, Math.min(1, err));
              // green low → orange mid → red high
              var r = Math.round(120 + 130*v);
              var g = Math.round(200*(1-v) + 60*v);
              var b = Math.round(160*(1-v) + 60*v);
              html += '<rect x="' + px + '" y="' + py + '" width="' + step + '" height="' + step + '" fill="rgb(' + r + ',' + g + ',' + b + ')" opacity="0.55"/>';
            }
          }
          // axes
          html += '<line x1="' + pad + '" y1="' + (H-pad) + '" x2="' + (W-pad) + '" y2="' + (H-pad) + '" stroke="#888"/>';
          html += '<line x1="' + pad + '" y1="' + pad + '" x2="' + pad + '" y2="' + (H-pad) + '" stroke="#888"/>';
          // tick labels
          var etas = [0.5, 0.7, 0.85, 0.95, 1.0];
          for (var k = 0; k < etas.length; k++) {
            var ex = pad + (etas[k]-ETA_MIN)/(ETA_MAX-ETA_MIN) * inner_w;
            html += '<line x1="' + ex + '" y1="' + (H-pad) + '" x2="' + ex + '" y2="' + (H-pad+5) + '" stroke="#888"/>';
            html += '<text x="' + ex + '" y="' + (H-pad+18) + '" text-anchor="middle" font-size="10" fill="#888">' + etas[k].toFixed(2) + '</text>';
          }
          var gts = [0, 1, 3, 6, 10, 12];
          for (var k = 0; k < gts.length; k++) {
            var gy = H - pad - (gts[k] - GT_MIN)/(GT_MAX - GT_MIN) * inner_h;
            html += '<line x1="' + (pad-5) + '" y1="' + gy + '" x2="' + pad + '" y2="' + gy + '" stroke="#888"/>';
            html += '<text x="' + (pad-8) + '" y="' + (gy+3) + '" text-anchor="end" font-size="10" fill="#888">' + gts[k] + '</text>';
          }
          html += '<text x="' + (W/2) + '" y="' + (H-pad/2 + 12) + '" text-anchor="middle" font-size="11" fill="#888">homodyne efficiency η</text>';
          html += '<text x="' + (pad/3) + '" y="' + (H/2) + '" text-anchor="middle" font-size="11" fill="#888" transform="rotate(-90 ' + (pad/3) + ' ' + (H/2) + ')">feedback delay γτ</text>';
          // target boxes
          function boxTarget(eta_min, gt_max, color, label) {
            var x0 = pad + (eta_min-ETA_MIN)/(ETA_MAX-ETA_MIN) * inner_w;
            var x1 = pad + inner_w;
            var y0 = pad;
            var y1 = H - pad - (0 - GT_MIN)/(GT_MAX - GT_MIN) * inner_h;
            var y_top = H - pad - (gt_max - GT_MIN)/(GT_MAX - GT_MIN) * inner_h;
            html += '<rect x="' + x0 + '" y="' + y_top + '" width="' + (x1-x0) + '" height="' + (y1 - y_top) + '" fill="none" stroke="' + color + '" stroke-width="1.5" stroke-dasharray="4,3"/>';
            html += '<text x="' + (x0 + 6) + '" y="' + (y_top + 12) + '" font-size="10" fill="' + color + '" font-weight="600">' + label + '</text>';
          }
          boxTarget(0.99, 0.05, '#79c79f', 'Stretch');
          boxTarget(0.95, 0.20, '#79f29c', 'Practical');
          boxTarget(0.85, 0.50, '#e8b96a', 'Loose');
          // FPGA wall
          var wall_y = H - pad - (10 - GT_MIN)/(GT_MAX - GT_MIN) * inner_h;
          html += '<line x1="' + pad + '" y1="' + wall_y + '" x2="' + (W-pad) + '" y2="' + wall_y + '" stroke="#f27979" stroke-width="1.5" stroke-dasharray="6,3"/>';
          html += '<text x="' + (W-pad-6) + '" y="' + (wall_y-4) + '" text-anchor="end" font-size="10" fill="#f27979">FPGA wall (γτ ≈ 10)</text>';
          // click marker
          if (click_eta != null) {
            var cx = pad + (click_eta - ETA_MIN)/(ETA_MAX-ETA_MIN) * inner_w;
            var cy = H - pad - (click_gtau - GT_MIN)/(GT_MAX - GT_MIN) * inner_h;
            html += '<circle cx="' + cx + '" cy="' + cy + '" r="6" fill="none" stroke="#fff" stroke-width="2"/>';
            var err = 0.5*(1-click_eta) + 0.04*click_gtau * Math.sqrt(d_dim/16);
            html += '<text x="' + (cx + 10) + '" y="' + (cy + 4) + '" font-size="11" fill="#fff" font-weight="600">err ≈ ' + err.toFixed(3) + '</text>';
            readout.innerHTML = '<strong>η = ' + click_eta.toFixed(3) + ', γτ = ' + click_gtau.toFixed(2) + '</strong> at d = ' + d_dim + ' &rarr; estimated Σ-error ≈ ' + err.toFixed(3) + ' (Frobenius)';
          }
          svg.innerHTML = html;
          dV.textContent = d_dim;
        }
        function fromClick(evt) {
          var rect = svg.getBoundingClientRect();
          var W_actual = rect.width, H_actual = rect.height;
          // map back to viewBox 520x320
          var vx = (evt.clientX - rect.left) * (520 / W_actual);
          var vy = (evt.clientY - rect.top) * (320 / H_actual);
          var pad = 56;
          var inner_w = 520 - 2*pad, inner_h = 320 - 2*pad;
          var eta = 0.5 + Math.max(0, Math.min(1, (vx - pad)/inner_w)) * 0.5;
          var gt = 0 + Math.max(0, Math.min(1, 1 - (vy - pad)/inner_h)) * 12;
          buildPlot(parseFloat(dS.value), eta, gt);
        }
        svg.addEventListener('click', fromClick);
        dS.addEventListener('input', function () { buildPlot(parseFloat(dS.value)); });
        buildPlot(parseFloat(dS.value));
      })();

      // -- Widget: T_mix vs κ scaling -----------------------------------
      (function () {
        var svg = document.getElementById('mixing-time-scaling-svg');
        if (!svg) return;
        var kS = document.getElementById('mix-kappa');
        var kV = document.getElementById('mix-kappa-val');
        var overSp = document.getElementById('mix-over');
        var underSp = document.getElementById('mix-under');
        var ratioSp = document.getElementById('mix-ratio');
        function tOver(k) { return 8 * Math.pow(k, 0.93); }   // empirical
        function tUnder(k) { return 16 * Math.sqrt(k); }      // theory
        function draw() {
          var k_now = parseFloat(kS.value);
          kV.textContent = k_now.toFixed(0);
          var W = 520, H = 320, pad = 56;
          var inner_w = W - 2*pad, inner_h = H - 2*pad;
          var KMIN = 1, KMAX = 200;
          var TMIN = 4, TMAX = 4000;
          function xpos(k) { return pad + (Math.log10(k)-Math.log10(KMIN))/(Math.log10(KMAX)-Math.log10(KMIN)) * inner_w; }
          function ypos(t) { return pad + inner_h - (Math.log10(t)-Math.log10(TMIN))/(Math.log10(TMAX)-Math.log10(TMIN)) * inner_h; }
          var html = '';
          // axes
          html += '<line x1="' + pad + '" y1="' + (pad+inner_h) + '" x2="' + (W-pad) + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          html += '<line x1="' + pad + '" y1="' + pad + '" x2="' + pad + '" y2="' + (pad+inner_h) + '" stroke="#888"/>';
          var ks = [1, 3, 10, 30, 100, 200];
          for (var k = 0; k < ks.length; k++) {
            var xx = xpos(ks[k]);
            html += '<line x1="' + xx + '" y1="' + (pad+inner_h) + '" x2="' + xx + '" y2="' + (pad+inner_h+5) + '" stroke="#888"/>';
            html += '<text x="' + xx + '" y="' + (pad+inner_h+18) + '" text-anchor="middle" font-size="10" fill="#888">κ=' + ks[k] + '</text>';
          }
          var ts = [4, 16, 64, 256, 1024, 4000];
          for (var k = 0; k < ts.length; k++) {
            var yy = ypos(ts[k]);
            html += '<line x1="' + (pad-5) + '" y1="' + yy + '" x2="' + pad + '" y2="' + yy + '" stroke="#888"/>';
            html += '<text x="' + (pad-8) + '" y="' + (yy+3) + '" text-anchor="end" font-size="10" fill="#888">' + ts[k] + '</text>';
          }
          html += '<text x="' + (W/2) + '" y="' + (H-pad/3 + 4) + '" text-anchor="middle" font-size="11" fill="#888">condition number κ = λ_max / λ_min</text>';
          html += '<text x="' + (pad/3) + '" y="' + (H/2) + '" text-anchor="middle" font-size="11" fill="#888" transform="rotate(-90 ' + (pad/3) + ' ' + (H/2) + ')">mixing time T_mix</text>';
          // overdamped curve
          var ov = []; for (var k = KMIN; k <= KMAX; k *= 1.08) ov.push(k);
          var ovStr = ov.map(function(k){return xpos(k)+','+ypos(tOver(k));}).join(' ');
          html += '<polyline points="' + ovStr + '" fill="none" stroke="#7a9fd1" stroke-width="2"/>';
          // underdamped curve
          var unStr = ov.map(function(k){return xpos(k)+','+ypos(tUnder(k));}).join(' ');
          html += '<polyline points="' + unStr + '" fill="none" stroke="#79f29c" stroke-width="2" stroke-dasharray="5,3"/>';
          // current κ marker
          var cx = xpos(k_now);
          html += '<circle cx="' + cx + '" cy="' + ypos(tOver(k_now)) + '" r="5" fill="#7a9fd1"/>';
          html += '<circle cx="' + cx + '" cy="' + ypos(tUnder(k_now)) + '" r="5" fill="#79f29c"/>';
          html += '<line x1="' + cx + '" y1="' + pad + '" x2="' + cx + '" y2="' + (pad+inner_h) + '" stroke="#fff" stroke-width="0.7" stroke-dasharray="2,3" opacity="0.5"/>';
          // legend
          html += '<text x="' + (W-pad-180) + '" y="' + (pad+12) + '" font-size="11" fill="#7a9fd1" font-weight="600">overdamped: T ∝ κ^0.93 (empirical)</text>';
          html += '<text x="' + (W-pad-180) + '" y="' + (pad+30) + '" font-size="11" fill="#79f29c" font-weight="600">underdamped: T ∝ √κ (theory)</text>';
          svg.innerHTML = html;
          overSp.textContent = tOver(k_now).toFixed(1);
          underSp.textContent = tUnder(k_now).toFixed(1);
          ratioSp.textContent = (tOver(k_now) / tUnder(k_now)).toFixed(2) + '×';
        }
        kS.addEventListener('input', draw);
        draw();
      })();
    """),
}


# ---------------------------------------------------------------------------
# Main render loop
# ---------------------------------------------------------------------------

ALL_NOTES = [NOTE_01, NOTE_02, NOTE_03, NOTE_04, NOTE_05, NOTE_06, NOTE_07]


def render_note(note: dict, head_template: str) -> str:
    head = make_head(
        head_template,
        title=note["title"],
        description=note["description"],
    )
    header = page_header(
        eyebrow=note["eyebrow"],
        h1=note["h1"],
        subtitle=note["subtitle"],
        covers=note["covers"],
    )
    nav = top_nav(note["nav"])
    main_html = ""
    for anchor, title, body_html, keypoints in note["sections"]:
        main_html += "      " + section_shell(
            anchor=anchor, title=title, body_html=body_html, keypoints=keypoints
        ) + "\n"
    footer_html = footer_block()
    extra_scripts = note.get("scripts", "")
    return assemble_proper(
        head=head, header=header, nav=nav, main_html=main_html,
        footer_html=footer_html, extra_scripts=extra_scripts,
    )


def main():
    args = sys.argv[1:]
    head_template = read_head_template()
    for note in ALL_NOTES:
        if args and not any(a in note["filename"] for a in args):
            continue
        out = ROOT / note["filename"]
        out.write_text(render_note(note, head_template))
        print(f"  wrote {out.relative_to(ROOT.parent.parent)}  ({len(out.read_text().splitlines())} lines)")
    print("done.")


if __name__ == "__main__":
    main()
