#!/usr/bin/env python3
"""Consolide les rapports persona d'un run de recette.

Usage:
    python consolidate.py <run_dir> [--seuil-similarite 0.6]

Lit   : <run_dir>/run.json (optionnel), <run_dir>/reports/*.json
Écrit : consolidated.json, backlog.json, rapport.md, rapport.html, GO_PENDING.md
"""
import argparse
import datetime as dt
import html
import json
import re
import statistics
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

SEVERITES = ["BLOQUANT", "MAJEUR", "MINEUR", "COSMETIQUE"]
POIDS_SEV = {"BLOQUANT": 40, "MAJEUR": 20, "MINEUR": 5, "COSMETIQUE": 1}
TYPES = {"BUG", "MANQUE_FONCTIONNEL", "UX", "ACCESSIBILITE", "PERFORMANCE", "SECURITE",
         "DONNEES", "AMELIORATION", "REGRESSION"}
STATUTS = ["OK", "PARTIEL", "KO", "NON_COUVERT", "BLOQUE", "NON_TESTE"]
VERDICTS = {"PRET", "PRET_AVEC_RESERVES", "NON_PRET"}
SCORES = ["couverture", "fluidite", "facilite", "accessibilite", "fiabilite"]


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def comp_key(c):
    c = c or {}
    name = norm(c.get("nom"))
    if not name or name == "inconnu":
        return None
    return f"{c.get('type', 'Autre')}:{c.get('nom')}"


# ---------------------------------------------------------------- lecture
def load_reports(run_dir: Path):
    reports, erreurs = [], []
    for f in sorted((run_dir / "reports").glob("*.json")):
        try:
            r = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            erreurs.append(f"{f.name}: JSON illisible ({e})")
            continue
        pid = r.get("persona_id") or f.stem
        r["persona_id"] = pid
        if r.get("verdict") not in VERDICTS:
            erreurs.append(f"{pid}: verdict invalide '{r.get('verdict')}'")
        ok_constats = []
        for i, c in enumerate(r.get("constats", []) or []):
            pb = []
            if c.get("type") not in TYPES:
                pb.append(f"type '{c.get('type')}'")
            if c.get("severite") not in SEVERITES:
                pb.append(f"sévérité '{c.get('severite')}'")
            if not c.get("titre"):
                pb.append("titre manquant")
            if pb:
                erreurs.append(f"{pid} constat #{i + 1}: rejeté ({', '.join(pb)})")
                continue
            c.setdefault("id", f"{pid}-{i + 1:03d}")
            ok_constats.append(c)
        r["constats"] = ok_constats
        for p in r.get("parcours", []) or []:
            if p.get("statut") not in STATUTS:
                erreurs.append(f"{pid} parcours {p.get('id')}: statut '{p.get('statut')}' invalide")
        reports.append(r)
    return reports, erreurs


# ---------------------------------------------------------------- dédup
def similar(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def dedupe(reports, seuil):
    groupes = []
    for r in reports:
        for c in r["constats"]:
            ck = comp_key(c.get("composant"))
            cible = None
            for g in groupes:
                if g["type"] != c["type"] and not {g["type"], c["type"]} <= {"BUG", "REGRESSION"}:
                    continue
                if ck and g["composant_key"] == ck and similar(g["titre"], c["titre"]) >= seuil:
                    cible = g
                    break
                if not ck and not g["composant_key"] and similar(g["titre"], c["titre"]) >= max(seuil, 0.8):
                    cible = g
                    break
            if cible is None:
                cible = {
                    "titre": c["titre"], "type": c["type"], "severite": c["severite"],
                    "composant": c.get("composant") or {"type": "Autre", "nom": "inconnu"},
                    "composant_key": ck, "description": c.get("description", ""),
                    "etapes": c.get("etapes", []), "attendu": c.get("attendu", ""),
                    "observe": c.get("observe", ""), "suggestions": [], "preuves": [],
                    "personas": [], "sources": [],
                }
                groupes.append(cible)
            if SEVERITES.index(c["severite"]) < SEVERITES.index(cible["severite"]):
                cible["severite"] = c["severite"]
            if r["persona_id"] not in cible["personas"]:
                cible["personas"].append(r["persona_id"])
            cible["sources"].append(c["id"])
            if c.get("suggestion") and c["suggestion"] not in cible["suggestions"]:
                cible["suggestions"].append(c["suggestion"])
            cible["preuves"] += c.get("preuves", []) or []
    return groupes


def prioriser(groupes):
    for g in groupes:
        if g["type"] == "SECURITE" and g["severite"] in ("MINEUR", "COSMETIQUE"):
            g["severite"] = "MAJEUR"
        n = len(g["personas"])
        g["score"] = round(POIDS_SEV[g["severite"]] * (1 + 0.5 * (n - 1)), 1)
        if g["severite"] == "BLOQUANT" or (g["type"] in ("SECURITE", "REGRESSION") and g["severite"] == "MAJEUR"):
            g["priorite"] = "P0"
        elif g["severite"] == "MAJEUR":
            g["priorite"] = "P1"
        elif g["severite"] == "MINEUR":
            g["priorite"] = "P2"
        else:
            g["priorite"] = "P3"
        g["necessite_decision"] = g["type"] == "MANQUE_FONCTIONNEL"
    groupes.sort(key=lambda g: (-g["score"], g["priorite"], g["titre"]))
    for i, g in enumerate(groupes, 1):
        g["id"] = f"C{i:03d}"
    return groupes


def construire_lots(groupes):
    """Un lot = un composant (pas de conflit entre agents). Les constats P3 sans composant
    ou purement cosmétiques sont regroupés par type de composant pour éviter l'émiettement."""
    paquets = {}
    for g in groupes:
        if g["necessite_decision"]:
            continue  # arbitrage utilisateur d'abord
        if g["composant_key"] and g["priorite"] != "P3":
            cle = g["composant_key"]
        elif g["composant_key"]:
            cle = f"divers-{g['composant'].get('type', 'Autre')}"
        else:
            cle = f"sans-composant-{g['type']}"
        paquets.setdefault(cle, []).append(g)
    lots = []
    for cle, gs in paquets.items():
        prio = min(x["priorite"] for x in gs)
        composants = sorted({x["composant_key"] for x in gs if x["composant_key"]})
        lots.append({
            "cle": cle,
            "titre": (cle.split(":", 1)[1] if ":" in cle else cle),
            "priorite": prio,
            "score": round(sum(x["score"] for x in gs), 1),
            "constats": [x["id"] for x in gs],
            "composants": composants,
            "personas_impactees": sorted({p for x in gs for p in x["personas"]}),
            "effort": "S" if len(gs) <= 2 else ("M" if len(gs) <= 5 else "L"),
            "a_investiguer": not composants,
        })
    lots.sort(key=lambda l: (l["priorite"], -l["score"]))
    for i, l in enumerate(lots, 1):
        l["id"] = f"L{i}"
    return lots


# ---------------------------------------------------------------- stats
def stats(reports, groupes, attendus):
    par_persona = []
    for r in reports:
        sc = r.get("scores", {}) or {}
        cnt = {s: 0 for s in STATUTS}
        for p in r.get("parcours", []) or []:
            if p.get("statut") in cnt:
                cnt[p["statut"]] += 1
        par_persona.append({
            "persona_id": r["persona_id"], "label": r.get("persona_label", r["persona_id"]),
            "verdict": r.get("verdict"), "mode_acces": r.get("mode_acces"),
            "scores": {k: sc.get(k) for k in SCORES}, "parcours": cnt,
            "nb_constats": len(r["constats"]), "limites": r.get("limites", ""),
            "synthese": r.get("synthese", ""),
        })
    moy = {}
    for k in SCORES:
        vals = [p["scores"][k] for p in par_persona if isinstance(p["scores"][k], (int, float))]
        moy[k] = round(statistics.mean(vals), 1) if vals else None
    sev = {s: sum(1 for g in groupes if g["severite"] == s) for s in SEVERITES}
    verdicts = [p["verdict"] for p in par_persona]
    if "NON_PRET" in verdicts or sev["BLOQUANT"]:
        global_v = "NON_PRET"
    elif "PRET_AVEC_RESERVES" in verdicts or sev["MAJEUR"]:
        global_v = "PRET_AVEC_RESERVES"
    else:
        global_v = "PRET" if verdicts else "INCONNU"
    recus = {p["persona_id"] for p in par_persona}
    return {
        "verdict_global": global_v, "moyennes": moy, "constats_par_severite": sev,
        "nb_constats_bruts": sum(len(r["constats"]) for r in reports),
        "nb_constats_dedupliques": len(groupes), "par_persona": par_persona,
        "personas_manquantes": [p for p in attendus if p not in recus],
    }


# ---------------------------------------------------------------- rendu
def md_table(rows, headers):
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in r) + " |")
    return "\n".join(out)


def render_md(run_id, st, groupes, lots, erreurs, meta):
    L = [f"# Recette multi-agents — rapport consolidé (run {run_id})", "",
         f"Domaine : **{meta.get('domaine') or 'non précisé'}** · Consigne : {meta.get('consigne') or 'aucune (toute l’org)'}", "",
         "<!-- SYNTHESE_EXECUTIVE : à rédiger par l'orchestrateur -->", "",
         f"**Verdict global : {st['verdict_global']}** — {len(st['par_persona'])} personas, "
         f"{st['nb_constats_bruts']} constats bruts → {st['nb_constats_dedupliques']} après dédoublonnage.", "",
         "Constats par sévérité : " + ", ".join(f"{k} {v}" for k, v in st["constats_par_severite"].items()), "",
         "Scores moyens (0-5) : " + ", ".join(f"{k} {v}" for k, v in st["moyennes"].items()), ""]
    if st["personas_manquantes"]:
        L += [f"⚠️ Personas sans rapport : {', '.join(st['personas_manquantes'])}", ""]
    L += ["## Vue par persona", "", md_table(
        [[p["label"], p["verdict"], p["mode_acces"], *[p["scores"][k] for k in SCORES],
          f"{p['parcours']['OK']}/{sum(p['parcours'].values())}", p["nb_constats"]] for p in st["par_persona"]],
        ["Persona", "Verdict", "Accès", *SCORES, "Parcours OK", "Constats"]), ""]
    L += ["## Constats consolidés", "", md_table(
        [[g["id"], g["priorite"], g["severite"], g["type"], g["titre"],
          g["composant"].get("nom"), len(g["personas"]), ", ".join(g["personas"])] for g in groupes],
        ["ID", "Prio", "Sévérité", "Type", "Titre", "Composant", "Nb", "Personas"]), ""]
    dec = [g for g in groupes if g["necessite_decision"]]
    L += ["## Décisions à prendre", ""]
    L += [f"- **{g['id']}** {g['titre']} — demandé par {', '.join(g['personas'])}" for g in dec] or ["- Aucune"]
    L += ["", "## Lots d'amélioration proposés", "", md_table(
        [[l["id"], l["priorite"], l["titre"], l["effort"], ", ".join(l["constats"]),
          ", ".join(l["personas_impactees"]), "oui" if l["a_investiguer"] else ""] for l in lots],
        ["Lot", "Prio", "Périmètre", "Effort", "Constats", "Personas", "Composant à identifier"]), ""]
    L += ["## Limites déclarées par les agents", ""]
    L += [f"- **{p['label']}** : {p['limites']}" for p in st["par_persona"] if p["limites"]] or ["- Aucune"]
    if erreurs:
        L += ["", "## Anomalies de format des rapports", ""] + [f"- {e}" for e in erreurs]
    L += ["", "## Détail des constats", ""]
    for g in groupes:
        L += [f"### {g['id']} — {g['titre']}",
              f"*{g['priorite']} · {g['severite']} · {g['type']} · {g['composant'].get('type')} `{g['composant'].get('nom')}` · "
              f"{', '.join(g['personas'])}*", "", g["description"] or ""]
        if g["etapes"]:
            L += ["", "Étapes : " + " → ".join(g["etapes"])]
        if g["attendu"] or g["observe"]:
            L += ["", f"Attendu : {g['attendu']}  ", f"Observé : {g['observe']}"]
        if g["suggestions"]:
            L += ["", "Suggestions : " + " / ".join(g["suggestions"])]
        L += [f"", f"Sources : {', '.join(g['sources'])}", ""]
    return "\n".join(L)


CSS = """body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1f2937;background:#f8fafc}
main{max-width:1200px;margin:auto;padding:24px}h1{font-size:24px}h2{margin-top:32px;border-bottom:2px solid #e5e7eb;padding-bottom:4px}
.kpis{display:flex;gap:12px;flex-wrap:wrap}.kpi{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px 16px;min-width:140px}
.kpi b{display:block;font-size:22px}table{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin-top:8px}
th,td{border:1px solid #e5e7eb;padding:6px 8px;text-align:left;vertical-align:top}th{background:#f1f5f9;cursor:pointer}
.b{display:inline-block;padding:1px 8px;border-radius:9px;font-size:12px;font-weight:600}
.BLOQUANT,.NON_PRET,.P0{background:#fee2e2;color:#991b1b}.MAJEUR,.P1,.PRET_AVEC_RESERVES{background:#ffedd5;color:#9a3412}
.MINEUR,.P2{background:#fef9c3;color:#854d0e}.COSMETIQUE,.P3,.PRET{background:#dcfce7;color:#166534}
.s0,.s1{background:#fecaca}.s2{background:#fed7aa}.s3{background:#fef08a}.s4{background:#bbf7d0}.s5{background:#86efac}
details{background:#fff;border:1px solid #e5e7eb;border-radius:8px;margin:6px 0;padding:8px 12px}summary{cursor:pointer;font-weight:600}
input{padding:6px 10px;width:320px;border:1px solid #cbd5e1;border-radius:6px}"""

JS = """document.querySelectorAll('th').forEach(th=>th.onclick=()=>{const t=th.closest('table'),i=[...th.parentNode.children].indexOf(th),
r=[...t.querySelectorAll('tbody tr')],a=th.dataset.a=th.dataset.a!=='1'?'1':'0';r.sort((x,y)=>{const p=x.children[i].innerText,q=y.children[i].innerText;
return (isNaN(p)||isNaN(q)?p.localeCompare(q):p-q)*(a==='1'?1:-1)});r.forEach(e=>t.tBodies[0].appendChild(e))});
const f=document.getElementById('f');if(f)f.oninput=()=>{const v=f.value.toLowerCase();document.querySelectorAll('#tc tbody tr').forEach(r=>r.style.display=r.innerText.toLowerCase().includes(v)?'':'none')}"""


def render_html(run_id, st, groupes, lots, erreurs, meta):
    e = lambda x: html.escape(str(x if x is not None else "–"))  # noqa: E731
    badge = lambda x: f'<span class="b {e(x)}">{e(x)}</span>'  # noqa: E731

    def score(v):
        return f'<td class="s{int(v)}">{v}</td>' if isinstance(v, (int, float)) else "<td>–</td>"

    def table(hid, headers, rows):
        h = "".join(f"<th>{e(x)}</th>" for x in headers)
        return f'<table id="{hid}"><thead><tr>{h}</tr></thead><tbody>{"".join(rows)}</tbody></table>'

    sev = st["constats_par_severite"]
    kpis = "".join(f'<div class="kpi">{e(k)}<b>{e(v)}</b></div>' for k, v in [
        ("Verdict", st["verdict_global"]), ("Personas", len(st["par_persona"])),
        ("Constats", st["nb_constats_dedupliques"]), ("Bloquants", sev["BLOQUANT"]),
        ("Majeurs", sev["MAJEUR"]), ("Lots", len(lots))])
    pers = [f"<tr><td>{e(p['label'])}</td><td>{badge(p['verdict'])}</td><td>{e(p['mode_acces'])}</td>"
            + "".join(score(p["scores"][k]) for k in SCORES)
            + f"<td>{p['parcours']['OK']}/{sum(p['parcours'].values())}</td><td>{p['nb_constats']}</td>"
              f"<td>{e(p['synthese'])}</td></tr>" for p in st["par_persona"]]
    cons = [f"<tr><td>{g['id']}</td><td>{badge(g['priorite'])}</td><td>{badge(g['severite'])}</td><td>{e(g['type'])}</td>"
            f"<td>{e(g['titre'])}</td><td>{e(g['composant'].get('nom'))}</td><td>{len(g['personas'])}</td>"
            f"<td>{e(', '.join(g['personas']))}</td></tr>" for g in groupes]
    lt = [f"<tr><td>{l['id']}</td><td>{badge(l['priorite'])}</td><td>{e(l['titre'])}</td><td>{l['effort']}</td>"
          f"<td>{e(', '.join(l['constats']))}</td><td>{e(', '.join(l['personas_impactees']))}</td></tr>" for l in lots]
    det = "".join(
        f"<details><summary>{g['id']} · {e(g['titre'])} {badge(g['severite'])}</summary>"
        f"<p><i>{e(g['type'])} · {e(g['composant'].get('type'))} <code>{e(g['composant'].get('nom'))}</code> · "
        f"{e(', '.join(g['personas']))}</i></p><p>{e(g['description'])}</p>"
        + (f"<p><b>Étapes :</b> {e(' → '.join(g['etapes']))}</p>" if g["etapes"] else "")
        + f"<p><b>Attendu :</b> {e(g['attendu'])}<br><b>Observé :</b> {e(g['observe'])}</p>"
        + (f"<p><b>Suggestions :</b> {e(' / '.join(g['suggestions']))}</p>" if g["suggestions"] else "")
        + "</details>" for g in groupes)
    dec = "".join(f"<li><b>{g['id']}</b> {e(g['titre'])} — {e(', '.join(g['personas']))}</li>"
                  for g in groupes if g["necessite_decision"]) or "<li>Aucune</li>"
    lim = "".join(f"<li><b>{e(p['label'])}</b> : {e(p['limites'])}</li>" for p in st["par_persona"] if p["limites"])
    manq = (f"<p>⚠️ Personas sans rapport : {e(', '.join(st['personas_manquantes']))}</p>"
            if st["personas_manquantes"] else "")
    err = ("<h2>Anomalies de format</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in erreurs) + "</ul>") if erreurs else ""
    return f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Recette multi-agents — run {e(run_id)}</title><style>{CSS}</style></head><body><main>
<h1>Recette multi-agents — rapport consolidé</h1><p>Run {e(run_id)} · domaine <b>{e(meta.get("domaine") or "non précisé")}</b> · consigne : {e(meta.get("consigne") or "aucune (toute l'org)")} · généré le {dt.datetime.now():%d/%m/%Y %H:%M}</p>
<div class="kpis">{kpis}</div>{manq}
<h2>Vue par persona</h2>{table('tp', ['Persona', 'Verdict', 'Accès', *SCORES, 'Parcours OK', 'Constats', 'Synthèse'], pers)}
<h2>Décisions à prendre</h2><ul>{dec}</ul>
<h2>Lots d'amélioration proposés</h2>{table('tl', ['Lot', 'Prio', 'Périmètre', 'Effort', 'Constats', 'Personas'], lt)}
<h2>Constats consolidés</h2><input id="f" placeholder="Filtrer…">{table('tc', ['ID', 'Prio', 'Sévérité', 'Type', 'Titre', 'Composant', 'Nb', 'Personas'], cons)}
<h2>Détail</h2>{det}<h2>Limites déclarées</h2><ul>{lim or '<li>Aucune</li>'}</ul>{err}
</main><script>{JS}</script></body></html>"""


def render_go(run_id, st, lots, groupes):
    by_id = {g["id"]: g for g in groupes}
    L = [f"# GO en attente — run {run_id}", "",
         f"Verdict global : **{st['verdict_global']}**", "", "## Lots proposés", ""]
    for l in lots:
        L.append(f"- **{l['id']}** [{l['priorite']}] {l['titre']} — effort {l['effort']} — "
                 f"{len(l['constats'])} constat(s) : " + "; ".join(by_id[c]["titre"] for c in l["constats"]))
    dec = [g for g in groupes if g["necessite_decision"]]
    if dec:
        L += ["", "## Décisions à prendre avant développement", ""] + [f"- {g['id']} {g['titre']}" for g in dec]
    L += ["", "## Réponse attendue", "", "`GO` · `GO L1,L3` · `GO P0` · `NO GO`", ""]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--seuil-similarite", type=float, default=0.6)
    a = ap.parse_args()
    run_dir = Path(a.run_dir).resolve()
    meta = {}
    if (run_dir / "run.json").exists():
        meta = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    run_id = meta.get("run_id", run_dir.name)
    attendus = [p["id"] for p in meta.get("personas", [])]

    reports, erreurs = load_reports(run_dir)
    groupes = prioriser(dedupe(reports, a.seuil_similarite))
    lots = construire_lots(groupes)
    st = stats(reports, groupes, attendus)

    cons = {"run_id": run_id, "genere_le": dt.datetime.now().isoformat(timespec="seconds"),
            "stats": st, "constats": groupes, "lots": lots, "erreurs_format": erreurs}
    (run_dir / "consolidated.json").write_text(json.dumps(cons, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "backlog.json").write_text(json.dumps({"run_id": run_id, "lots": lots, "constats": groupes},
                                                     ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "rapport.md").write_text(render_md(run_id, st, groupes, lots, erreurs, meta), encoding="utf-8")
    (run_dir / "rapport.html").write_text(render_html(run_id, st, groupes, lots, erreurs, meta), encoding="utf-8")
    (run_dir / "GO_PENDING.md").write_text(render_go(run_id, st, lots, groupes), encoding="utf-8")
    print(json.dumps({"verdict_global": st["verdict_global"], "personas": len(reports),
                      "constats_bruts": st["nb_constats_bruts"], "constats": len(groupes),
                      "lots": len(lots), "personas_manquantes": st["personas_manquantes"],
                      "erreurs_format": len(erreurs)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
