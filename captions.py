"""Légendes Instagram / TikTok. Uniquement des informations présentes sur sparkauto.fr."""
import random
import re
import unicodedata

HOOKS = {
    "jauge": ["Quel est le niveau de modernité de votre tableau de bord ?", "Autoradio CD ou CarPlay sans fil : où en est votre voiture ?"],
    "feu_rouge": ["Votre autoradio d’origine vous bloque au feu rouge.", "Passez au vert : CarPlay sans changer de voiture."],
    "vrai_match": ["Support de téléphone vs vrai écran CarPlay : le match.", "Le support de téléphone, c’est fini."],
    "fausse_vs_vraie": ["La fausse bonne idée vs la vraie solution.", "Arrêtez de coincer votre téléphone dans la grille d’aération."],
    "mise_a_jour": ["Mise à jour importante pour votre voiture.", "Votre voiture peut avoir CarPlay sans fil."],
    "c_est_officiel": ["C’est officiel : le téléphone sur le tableau de bord, c’est fini.", "C’est officiel : votre voiture passe à CarPlay."],
    "communique": ["Communiqué officiel à tous ceux qui roulent avec le téléphone dans la grille d’aération.", "On aurait dû vous le dire plus tôt."],
    "3_raisons": ["3 raisons pour lesquelles votre voiture n’a toujours pas CarPlay.", "Pas besoin de changer de voiture pour avoir CarPlay."],
    "venn": ["La voiture que vous aimez + la techno d’une voiture neuve.", "Gardez votre voiture, changez d’écran."],
    "checklist": ["Avant d’acheter un écran CarPlay, vérifiez ces 6 points.", "La checklist avant d’acheter un écran CarPlay."],
    "3_etapes": ["Installer CarPlay, réglé en 3 étapes.", "Plug & play : on retire l’autoradio, on branche, c’est prêt."],
    "voici_julien": ["Voici Julien. Ne soyez pas comme Julien.", "Julien pensait qu’il fallait changer de voiture pour avoir CarPlay."],
    "voitures_de": ["Un jour un autoradio CD, le lendemain CarPlay sans fil.", "Votre voiture a pris un coup de jeune."],
    "liste_barree": ["Ce que vous pouvez oublier avec CarPlay sans fil.", "Le support qui tombe, le câble qui traîne : terminé."],
    "n_achetez_pas": ["N’achetez pas cet écran si vous ne voulez pas ces effets secondaires.", "Attention, effets secondaires."],
    "baissez_un_doigt": ["Baissez un doigt si votre voiture a plus de 10 ans.", "3 doigts baissés ? C’est l’autoradio qu’il faut changer."],
    "affiche": ["Ce n’est pas votre voiture qui a vieilli. C’est son autoradio.", "Vous reconnaissez ces signes ?"],
    "6_signes": ["6 signes que votre autoradio a fait son temps.", "Votre autoradio a fait son temps ?"],
    "ce_que_vous_ratez": ["Encore le téléphone dans la grille d’aération ? Voici ce que vous ratez.", "Ce que vous ratez sans CarPlay."],
    "probleme_solution": ["Besoin d’un tableau de bord moderne ?", "Un problème, une solution."],
    "colis": ["Livraison pour votre voiture : CarPlay + Android Auto sans fil.", "Un colis pour votre voiture."],
    "ticket": ["Ce qui manque sur le ticket de votre voiture.", "CarPlay, Android Auto, GPS, écran HD : il manquait tout ça."],
    "promo": ["Offre en cours sur sparkauto.fr.", "C’est le moment de passer à CarPlay."],
    "commandez_obtenez": ["Ce que vous commandez vs ce que vous obtenez.", "Un écran, et tout ce qui va avec."],
}

BASE_TAGS_IG = ["carplay", "androidauto", "carplaysansfil", "autoradio", "ecrancarplay", "autoradiocarplay",
                "voiture", "accessoiresauto", "sparkauto"]
BASE_TAGS_TT = ["carplay", "androidauto", "voiture"]


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


def vehicle_tags(v):
    brand = slug(v["brand"])
    model = slug(v["short"])
    tags = [brand]
    if model and model != brand:
        tags.append(model if model.startswith(brand) else brand + model)
    return tags


def build(template_id, v, platform, promo=None, evergreen=None, seed=0):
    rnd = random.Random(seed)
    hook = rnd.choice(HOOKS.get(template_id, ["CarPlay sans fil pour votre voiture."]))
    yrs = f" ({v['years']})" if v.get("years") else ""
    offer = promo["caption"] if promo else (evergreen or "")
    if platform == "instagram":
        lines = [
            hook, "",
            f"{v['name']}{yrs} : écran CarPlay & Android Auto sans fil, installé à la place de l’autoradio d’origine.",
            "• Plug & play, 20 minutes environ",
            "• Commandes au volant conservées (versions équipées)",
            "• Garantie 2 ans · aide 7j/7 sur WhatsApp", "",
            "+300 modèles / 40 marques compatibles. Vérifiez le vôtre sur sparkauto.fr (lien en bio).",
        ]
        if offer:
            lines += ["", offer]
        tags = vehicle_tags(v) + BASE_TAGS_IG
        lines += ["", " ".join("#" + t for t in tags)]
        return "\n".join(lines)
    # TikTok : un seul paragraphe (les retours à la ligne ne passent pas toujours)
    parts = [hook, f"{v['name']}{yrs} : CarPlay & Android Auto sans fil, à la place de l’autoradio d’origine.",
             "+300 modèles / 40 marques → sparkauto.fr"]
    if offer:
        parts.append(offer)
    tags = BASE_TAGS_TT + vehicle_tags(v)
    return " ".join(parts) + " " + " ".join("#" + t for t in tags)
