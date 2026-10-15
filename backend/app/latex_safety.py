"""Fail-closed grammar for untrusted mathematical fragments, not TeX programs."""
from __future__ import annotations

import re

ALLOWED_LATEX_COMMANDS = frozenset("""
frac dfrac tfrac sqrt binom dbinom tbinom
text textrm textbf textit textsf texttt emph underline overline
mathrm mathbf mathit mathsf mathtt mathbb mathcal mathfrak boldsymbol
left right middle big Big bigg Bigg bigl bigr Bigl Bigr biggl biggr Biggl Biggr
alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa
lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega
Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega
le leq ge geq neq ne approx sim simeq equiv cong propto
in notin ni subset supset subseteq supseteq nsubseteq nsupseteq
cup cap setminus emptyset varnothing forall exists nexists neg land lor
Rightarrow Leftarrow Leftrightarrow rightarrow leftarrow leftrightarrow
Longrightarrow Longleftarrow Longleftrightarrow longrightarrow longleftarrow
mapsto to implies iff uparrow downarrow updownarrow
times cdot div pm mp ast star circ bullet oplus otimes
sum prod coprod int iint iiint oint lim limsup liminf min max inf sup
sin cos tan cot sec csc arcsin arccos arctan sinh cosh tanh log ln exp
det gcd deg ker dim arg Pr
infty partial nabla ell hbar imath jmath Re Im
angle measuredangle triangle square parallel perp mid nmid
ldots cdots vdots ddots dots
langle rangle lbrace rbrace lvert rvert lVert rVert vert Vert
lfloor rfloor lceil rceil backslash
hat widehat bar vec tilde widetilde dot ddot acute grave breve check
overbrace underbrace overset underset stackrel substack limits nolimits
displaystyle textstyle scriptstyle scriptscriptstyle
quad qquad enspace thinspace medspace thickspace negthinspace
textbackslash textasciitilde textasciicircum
par newline smallskip medskip bigskip centering
item hline cline begin end
""".split())
ALLOWED_LATEX_ENVIRONMENTS = frozenset({
    "math", "displaymath", "equation", "equation*", "align", "align*",
    "aligned", "gather", "gather*", "gathered", "split", "cases",
    "matrix", "pmatrix", "bmatrix", "Bmatrix", "vmatrix", "Vmatrix",
    "smallmatrix", "array", "itemize", "enumerate", "center", "tikzpicture",
})
_CONTROL_SYMBOLS = frozenset("\\{}$%&#_ ,;:!()[]|/")
_WORD = re.compile(r"[A-Za-z]+")
_ENVIRONMENT = re.compile(r"\{([A-Za-z]+\*?)\}")
_NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
_POINT = rf"\(\s*{_NUMBER}\s*,\s*{_NUMBER}\s*\)"
_DRAW = re.compile(rf"{_POINT}(?:\s*(?:--|rectangle)\s*{_POINT})+(?:\s*--\s*cycle)?\s*;")
_NODE = re.compile(rf"at\s*{_POINT}\s*")
_DRAW_STYLES = frozenset({"thin", "thick", "very thick", "dashed", "dotted"})


def _skip_space(value: str, position: int) -> int:
    while position < len(value):
        if value[position].isspace():
            position += 1
        elif value[position] == "%":
            end = re.search(r"[\r\n]", value[position:])
            position = len(value) if end is None else position + end.end()
        else:
            break
    return position


def _tikz_fragment(value: str) -> bool:
    """Numeric lines, rectangles and nodes used by the seed; no general keys/hooks."""
    position = _skip_space(value, 0)
    if value[position:position + 1] == "[":
        end = value.find("]", position)
        option = value[position + 1:end].strip()
        if end < 0 or not re.fullmatch(r"scale\s*=\s*(?:\d+(?:\.\d*)?|\.\d+)", option):
            return False
        if not 0 < float(option.split("=")[1]) <= 20:
            return False
        position = end + 1
    while (position := _skip_space(value, position)) < len(value):
        command = re.match(r"\\(draw|node)\b", value[position:])
        if command is None:
            return False
        position = _skip_space(value, position + command.end())
        if command[1] == "draw":
            if value[position:position + 1] == "[":
                end = value.find("]", position)
                if end < 0 or any(item.strip() not in _DRAW_STYLES for item in value[position + 1:end].split(",")):
                    return False
                position = _skip_space(value, end + 1)
            path = _DRAW.match(value, position)
            if path is None:
                return False
            position = path.end()
        else:
            node = _NODE.match(value, position)
            if node is None:
                return False
            position = node.end()
            if value[position:position + 1] != "{":
                return False
            start = position + 1
            depth = 1
            position += 1
            while position < len(value) and depth:
                char = value[position]
                if char == "%":
                    position = _skip_space(value, position)
                    continue
                if char == "\\":
                    position += 2
                    continue
                depth += (char == "{") - (char == "}")
                position += 1
            label = value[start:position - 1]
            if depth or "\\begin" in label or "\\end" in label or latex_violation(label):
                return False
            position = _skip_space(value, position)
            if value[position:position + 1] != ";":
                return False
            position += 1
    return True


def latex_violation(value: str) -> str | None:
    try:
        value.encode("utf-8", errors="strict")
    except (UnicodeEncodeError, AttributeError):
        return "texte Unicode invalide"
    if "^^" in value or any(ord(char) < 32 and char not in "\t\n\r" for char in value):
        return "syntaxe de fragment non autorisée"
    position = 0
    groups = 0
    environments: list[tuple[str, int]] = []
    while position < len(value):
        char = value[position]
        if char == "%":
            position = _skip_space(value, position)
            continue
        if char in "{}":
            groups += 1 if char == "{" else -1
            if groups < 0:
                return "groupe déséquilibré"
        if char != "\\":
            position += 1
            continue
        position += 1
        command = _WORD.match(value, position)
        if command is None:
            if position >= len(value) or value[position] not in _CONTROL_SYMBOLS:
                return "séquence de contrôle non autorisée"
            position += 1
            continue
        name = command[0]
        position = command.end()
        if name not in ALLOWED_LATEX_COMMANDS:
            return name
        if name not in {"begin", "end"}:
            continue
        position = _skip_space(value, position)
        environment = _ENVIRONMENT.match(value, position)
        if environment is None or environment[1] not in ALLOWED_LATEX_ENVIRONMENTS:
            return "environnement non autorisé"
        position = environment.end()
        env = environment[1]
        if name == "end":
            if not environments or environments.pop() != (env, groups):
                return "environnement déséquilibré"
        elif env == "tikzpicture":
            closing = re.search(r"\\end\s*\{tikzpicture\}", value[position:])
            if closing is None or not _tikz_fragment(value[position:position + closing.start()]):
                return "syntaxe TikZ non autorisée"
            position += closing.end()
        else:
            environments.append((env, groups))
    if groups or environments:
        return "fragment déséquilibré"
    return None


def ensure_safe_latex(value: str) -> str:
    violation = latex_violation(value)
    if violation:
        raise ValueError(f"Commande LaTeX interdite dans le contenu utilisateur : {violation}.")
    return value
