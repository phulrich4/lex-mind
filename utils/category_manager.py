# utils/category_manager.py

CATEGORIES = {
    "Verträge": [
        "vertrag", "klausel", "vereinbarung", "vereinbart", "vereinigen", "konditionen",
        "vertragsdauer", "laufzeit", "kündigungsfrist", "kündigung", "parteien", "schuldner",
        "vertragsgegenstand", "vertragsstrafe", "zahlungspflicht", "gesellschafter", 
        "gesellschaftervertrag", "gesellschafterbindungsvertrag", "bindung", "bindungsklausel", 
        "aktionsplan", "optionsvertrag", "darlehen", "leasing", "lizenz", "miete", "kaufvertrag",
        "lieferung", "liefervertrag", "dienstleistung", "consultingvertrag", "rahmenvertrag", 
        "arbeitsvertrag", "werkvertrag", "auftrag", "vertragspartner", "abrede"
    ],
    "Urkunden": [
        "urkunde", "notar", "notariell", "beglaubigung", "beurkundung", "öffentlich", 
        "gründung", "gründungsurkunde", "gründungsvertrag", "gesellschaftsgründung", 
        "register", "handelsregister", "registereintrag", "eintragung", 
        "statuten", "satzung", "gesellschafterliste", "geschäftsanteil", "übertragung", 
        "abtretung", "anteilsübertragung", "registergericht", "protokoll", "notariat"
    ],
    "Klagen": [
        "klage", "klagen", "gericht", "gerichtsurteil", "prozess", "rechtsstreit", "streitfall",
        "rechtsstreitigkeit", "anwalt", "forderung", "gerichtsbeschluss", "verfahren"
    ],
    "Andere": []  # Fallback
}

def assign_category(text: str) -> str:
    """
    Weist einem Text auf Basis einfacher Keyword-Erkennung eine Kategorie zu.
    Falls kein Treffer, wird 'Andere' zurückgegeben.
    """
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "Andere"

def get_all_categories() -> list:
    """Gibt eine Liste aller verfügbaren Kategorien zurück (z. B. für Filter)."""
    return list(CATEGORIES.keys())
