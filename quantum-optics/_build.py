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
        ("squeezing", "Squeezing"),
        ("density", "Density Ops"),
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
            sampler. (See <code>~/Code/Ideas/cim/notes/feedback_fidelity.md</code>.)
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
              classical SDEs, and the Lyapunov sampler in
              <code>~/Code/Ideas/cim/notes/langevin_to_lyapunov.md</code>
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
            "the OU machine — see "
            "<code>~/Code/Ideas/cim/experiments/exp00_lyapunov_killshot.py</code>."
          ),
         ["Squeezed input → e^(−2r) on photocurrent variance",
          "Detection loss caps usable r",
          "No κ-dependence — Direction B's killshot"]),
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
            <tr><td>Reference</td><td><code>~/Code/Ideas/cim/notes/feedback_fidelity.md</code> — overdamped specialization (the corrected envelope)</td></tr>
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
        ("dopo", "DOPO Bifurcation"),
        ("quantum-classical", "Quantum vs Classical"),
        ("mfb-network", "MFB Network"),
        ("ising-mapping", "Ising Mapping"),
        ("rosetta", "Update Rosetta"),
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
          ),
         ["DOPO mean-field = pitchfork bifurcation",
          "Two stable phases (\\(\\pm\\)) above threshold",
          "Quantum noise selects which phase wins"]),
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
          ),
         ["Above threshold: classical SDE",
          "Below threshold: full Lindblad / squeezing",
          "At threshold: amplification of \\(O(1)\\) quantum events"]),
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
          """,
         ["Time-multiplexed pulses = spins",
          "FPGA implements \\(\\sum_j J_{ij} x_j\\)",
          "EOM injection = spin-spin coupling"]),
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
            <code>cim-optimizer</code> implements all three variants
            (see <code>~/Code/Ideas/cim/vendor/cim-optimizer/</code>).
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
            <tr><td>Project</td><td><code>~/Code/Ideas/cim/notes/cim_to_ou_rosetta.md</code> — the rosetta stone in markdown form</td></tr>
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
        ("langevin-lyapunov", "Langevin→Lyapunov"),
        ("optical-adapt", "Optical Adaptation"),
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
          """,
         ["\\(\\dot x = -A x + \\sqrt{D}\\,\\xi \\Rightarrow A\\Sigma + \\Sigma A^T = D\\)",
          "Symmetric PD \\(A\\) + \\(D = I\\) ⇒ \\(\\Sigma = \\tfrac{1}{2}A^{-1}\\)",
          "\\(\\hat\\Sigma\\) from sample averaging gives \\(A^{-1}\\)"]),
        ("optical-adapt", "Optical Adaptation: One-Line Diff vs CIM", r"""
          <p>
            From Note 06's Rosetta stone, the MFB-CIM Euler step is:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
# CIM (cubic saturation, Ising solver)
x += time_step * (x * ((r[t] - 1) - mu * x_squared))   # gain - x³
x += time_step * eps[t] * (MVM * error_var)            # MVM = J·x feedback
x += eps[t] * noise * (torch.rand(N) - 0.5)            # uniform noise
          </pre>
          <p>
            The OU machine in
            <a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a>
            makes three surgical changes:
          </p>
          <pre style="background: var(--page-panel); padding: 0.7rem; border-radius: 0.3rem; font-size: 0.82rem; overflow-x: auto;">
# OU machine (linear damping, Lyapunov sampler)
x += time_step * (-A_drift @ x.T).T                    # cubic → linear
# (FPGA MVM still applied via A_drift's off-diagonal part)
x += sqrt(time_step) * (D_chol @ randn(N).T).T         # uniform → Gaussian
# + accumulator: M += x.T @ x
          </pre>
          <p>
            The hardware substrate is unchanged: same time-multiplexed
            pulse loop, same homodyne, same FPGA, same EOM. Only the
            firmware changes. <em>Same bench can run CIM on Tuesday and
            OU machine on Wednesday.</em>
          </p>
          <p>
            The verification (cim/<code>experiments/exp02_ou_lyapunov.py</code>):
            for \(d \in \{4, 8, 16\}\) and \(\kappa(A) \in \{1, 10, 100\}\),
            empirical \(\hat\Sigma\) matches
            <code>scipy.linalg.solve_continuous_lyapunov</code> to within
            \(\le 5\%\) relative Frobenius error (the simulator hits
            ≤ 2.7% at the worst-case cell). See
            <code>~/Code/Ideas/cim/notebooks/02_overdamped_ou.ipynb</code>
            for the headline experiment.
          </p>
          """ + callout(
            "The OU machine isn't faster than <code>scipy.linalg.solve</code> "
            "in software — the simulator is a Python loop. The claim is "
            "about the optical hardware, where per-round-trip MVM is "
            "O(d) latency vs CPU's O(d³) for Bartels-Stewart."
          ),
         ["Three-line firmware diff vs CIM",
          "Same hardware, different operating regime",
          "Verified: \\(\\hat\\Sigma \\to \\frac{1}{2}A^{-1}\\) within 3%"]),
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
            sub-linear additive. The
            <code>cim/experiments/exp03_ou_hardware_envelope.py</code>
            measurement caught this — see
            <code>cim/notes/feedback_fidelity.md</code> for the
            corrected story.
          </p>
          """,
         ["η: exact steady-state shift, no envelope",
          "τ: sub-linear additive correction",
          "σ_meas: inflates diffusion, no encoding bias"]),
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
            See
            <code>~/Code/Ideas/cim/notes/hardware_noise_budget.md</code>
            for the full noise-budget breakdown.
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
            are in <code>~/Code/Ideas/TLA/direction_A_underdamped/</code>
            — paper draft submitted to NeurIPS 2026.
          </p>
          """ + callout(
            "The √κ advantage is the killer feature. Overdamped is the "
            "stepping-stone we de-risk on; underdamped is the asymptotic "
            "win. They share hardware. <em>The right way to think about "
            "this proposal is: the bench we build for overdamped <strong>is</strong> "
            "the bench that runs underdamped, with a firmware update.</em>"
          ),
         ["Overdamped: \\(T_\\mathrm{mix} \\propto \\kappa\\)",
          "Underdamped (Direction A): \\(T_\\mathrm{mix} \\propto \\sqrt\\kappa\\)",
          "Same hardware, firmware-distinguished operating regimes"]),
        ("open", "Open Questions", r"""
          <ol>
            <li><strong>Scaling to d ≥ 64.</strong> The simulator
              currently caps at d = 16 on CPU; GPU experiment (see
              <code>~/Code/Ideas/cim/handoff.md</code>) is the next
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
            <tr><td>Project</td><td><a href="https://github.com/nez0b/cim-spu-optical-simulation">cim-spu-optical-simulation</a> — live repo: simulator, notebooks, hardware-noise-budget</td></tr>
            <tr><td>Note</td><td><code>cim/notes/langevin_to_lyapunov.md</code> — Itô derivation</td></tr>
            <tr><td>Note</td><td><code>cim/notes/cim_to_ou_rosetta.md</code> — three-line CIM → OU diff</td></tr>
            <tr><td>Note</td><td><code>cim/notes/feedback_fidelity.md</code> — corrected (η, τ) envelope analysis</td></tr>
            <tr><td>Note</td><td><code>cim/notes/hardware_noise_budget.md</code> — full QCi-actionable breakdown</td></tr>
            <tr><td>Note</td><td><code>cim/handoff.md</code> — prioritized next steps for the GPU machine</td></tr>
            <tr><td>Paper</td><td>Aifer, Duffield, Coles, et al., "Thermodynamic Linear Algebra", arXiv:2306.14740 (2023); npj Unconventional Computing (2024)</td></tr>
            <tr><td>Paper</td><td>Aifer et al., 8-cell RLC SPU hardware demo, <em>Nat. Commun.</em> (2025)</td></tr>
            <tr><td>Reference</td><td>Wiseman &amp; Milburn, <em>Quantum Measurement and Control</em>, Ch. 5</td></tr>
            <tr><td>Project</td><td><code>~/Code/Ideas/TLA/direction_A_underdamped/</code> — underdamped √κ paper</td></tr>
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
