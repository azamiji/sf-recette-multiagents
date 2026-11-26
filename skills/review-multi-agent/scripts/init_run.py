#!/usr/bin/env python3
"""Crée l'arborescence d'un run de recette, puis les squelettes de briefs persona.

Usage:
    # 1. Lancement : crée le run (domaine + consigne)
    python init_run.py --root <projet> --domaine "Banque" [--consigne "uniquement l'app Sales"]
    # 2. Après génération de personas.md : crée les briefs
    python init_run.py --root <projet> --run-id <run_id> --personas recette-runs/<run_id>/personas.md [--only id1,id2]

Sortie (stdout, JSON): run_id, run_dir, data_prefix, personas[].
"""
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^##\s+([a-z0-9_]+)\s+[—-]\s+(.+?)\s*$")


def parse_personas(md_path: Path):
    personas, current = [], None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = HEADING.match(line)
        if m:
            current = {"id": m.group(1), "label": m.group(2), "body": []}
            personas.append(current)
        elif current is not None:
            current["body"].append(line)
    for p in personas:
        body = "\n".join(p.pop("body")).strip()
        p["body"] = body
        typ = re.search(r"(?:Type|Accès)\s*:\s*([^\n—-]+)", body)
        t = (typ.group(1).strip().lower() if typ else "i")
        p["acces"] = "E" if t.startswith(("e", "externe")) else ("A" if t.startswith(("a", "admin")) else "I")
    return personas


def ensure_gitignore(root: Path):
    gi = root / ".gitignore"
    lines = gi.read_text(encoding="utf-8").splitlines() if gi.exists() else []
    wanted = ["recette-runs/*/evidence/"]
    missing = [w for w in wanted if w not in lines]
    if missing:
        with gi.open("a", encoding="utf-8") as f:
            if lines and lines[-1].strip():
                f.write("\n")
            f.write("# sf-recette-multiagents\n" + "\n".join(missing) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--personas")
    ap.add_argument("--domaine")
    ap.add_argument("--consigne")
    ap.add_argument("--nb", type=int, help="nombre d'agents (3 à 20)")
    ap.add_argument("--run-id")
    ap.add_argument("--only", help="ids séparés par des virgules")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    run_id = a.run_id or dt.datetime.now().strftime("%Y%m%d-%H%M")
    run_dir = root / "recette-runs" / run_id
    for sub in ("briefs", "reports", "evidence", "lots", "retest"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    meta_path = run_dir / "run.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "run_id": run_id, "run_dir": str(run_dir), "data_prefix": f"RCT{run_id}",
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "domaine": "", "consigne": "", "personas": []}
    if a.domaine is not None:
        meta["domaine"] = a.domaine
    if a.consigne is not None:
        meta["consigne"] = a.consigne
    if a.nb is not None:
        nb = max(3, min(20, a.nb))
        if nb != a.nb:
            print(f"Nombre d'agents ramené à {nb} (bornes 3-20).", file=sys.stderr)
        meta["nb_agents"] = nb
    data_prefix = meta["data_prefix"]

    if a.personas:
        personas = parse_personas(Path(a.personas))
        if not personas:
            sys.exit("Aucun persona trouvé (titres attendus : '## <id> — <Libellé>')")
        if a.only:
            keep = {x.strip() for x in a.only.split(",")}
            personas = [p for p in personas if p["id"] in keep]
        if "ceo" not in {p["id"] for p in personas} and not a.only:
            print("ATTENTION : aucun persona 'ceo' — le CEO doit toujours être présent.", file=sys.stderr)
        if meta.get("nb_agents") and len(personas) > meta["nb_agents"] and not a.only:
            print(f"ATTENTION : {len(personas)} personas pour {meta['nb_agents']} agents demandés.", file=sys.stderr)
        for p in personas:
            brief = run_dir / "briefs" / f"{p['id']}.md"
            (run_dir / "evidence" / p["id"]).mkdir(exist_ok=True)
            if brief.exists():
                continue  # reprise : ne pas écraser un brief déjà complété
            brief.write_text(
                f"<!-- Squelette : compléter avec references/agent-brief.md -->\n"
                f"# Mission de recette — {p['label']}\n\n"
                f"persona_id: {p['id']}\n"
                f"domaine: {meta['domaine']}\n"
                f"consigne: {meta['consigne'] or '(aucune)'}\n"
                f"acces: MCP partagé (même utilisateur pour tous les agents)\n"
                f"data_prefix: {data_prefix}_{p['id'].upper()}_\n"
                f"rapport_json: {run_dir / 'reports' / (p['id'] + '.json')}\n"
                f"rapport_md: {run_dir / 'reports' / (p['id'] + '.md')}\n\n"
                f"## Fiche persona\n{p['body']}\n",
                encoding="utf-8",
            )
        meta["personas"] = [{"id": p["id"], "label": p["label"], "acces": p["acces"]} for p in personas]

    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, title in (("context.md", "Contexte org"), ("plan.md", "Plan de recette")):
        f = run_dir / name
        if not f.exists():
            f.write_text(f"# {title} — run {run_id}\n\nDomaine : {meta['domaine']}\nConsigne : {meta['consigne'] or '(aucune)'}\n\n", encoding="utf-8")
    ensure_gitignore(root)
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
