"""Curated, estimated demo recipes. These are not extracted YouTube recipes."""

SEED_STOCK = [
    ("rice", 1000, "g"), ("tomato", 600, "g"), ("onion", 500, "g"),
    ("toor dal", 400, "g"), ("semolina", 300, "g"), ("oil", 250, "ml"),
    ("salt", 100, "g"), ("mustard seeds", 50, "g"), ("chilli", 6, "pcs"),
]

RECIPES = {
    "tomato-rice": {
        "name": "Tomato rice", "time_minutes": 25, "servings": 2,
        "ingredients": [("rice", 200, "g"), ("tomato", 250, "g"), ("onion", 100, "g"),
                        ("oil", 20, "ml"), ("salt", 4, "g"), ("mustard seeds", 3, "g"), ("chilli", 2, "pcs")],
        "steps": ["Rinse the rice and cook until tender using your usual rice-to-water ratio.",
                  "Chop the onion and tomatoes. Slit the chillies.",
                  "Warm the oil in a pan. Add mustard seeds; let them splutter. Add onion and chilli.",
                  "When onion softens, add tomato and salt. Cook until the tomatoes become soft.",
                  "Gently fold in the cooked rice. Heat through for 2 minutes and taste before serving."],
    },
    "dal": {
        "name": "Simple dal", "time_minutes": 35, "servings": 2,
        "ingredients": [("toor dal", 150, "g"), ("tomato", 100, "g"), ("onion", 75, "g"),
                        ("oil", 15, "ml"), ("salt", 4, "g"), ("mustard seeds", 3, "g"), ("chilli", 1, "pcs")],
        "steps": ["Rinse the dal. Cook with enough water until completely soft, following your cooker's instructions.",
                  "Chop onion, tomato and chilli. Warm oil in a separate pan.",
                  "Add mustard seeds, then onion and chilli. Cook until the onion softens.",
                  "Add tomato and cook until soft. Stir the tempering into the cooked dal.",
                  "Add salt and water to your preferred consistency. Simmer for 5 minutes."],
    },
    "upma": {
        "name": "Vegetable upma", "time_minutes": 20, "servings": 2,
        "ingredients": [("semolina", 160, "g"), ("onion", 100, "g"), ("carrot", 100, "g"),
                        ("oil", 15, "ml"), ("salt", 4, "g"), ("mustard seeds", 3, "g"), ("chilli", 1, "pcs")],
        "steps": ["Dry-roast semolina over low heat until fragrant. Set aside.",
                  "Chop onion, carrot and chilli into small pieces.",
                  "Warm oil, add mustard seeds, then onion, carrot and chilli. Cook until vegetables soften.",
                  "Add about 400 ml water for 160 g semolina and salt. Bring to a boil.",
                  "Lower the heat. Stir in semolina gradually to avoid lumps. Cover and cook until tender."],
    },
}

TRAINS = {
    "12627": {"name": "Karnataka Express", "origin": "KSR Bengaluru", "destination": "New Delhi",
              "sample_station": "Guntakal", "sample_delay_minutes": 12},
    "12623": {"name": "Trivandrum Mail", "origin": "Chennai Central", "destination": "Thiruvananthapuram",
              "sample_station": "Katpadi", "sample_delay_minutes": 0},
    "12658": {"name": "Chennai Mail", "origin": "KSR Bengaluru", "destination": "Chennai Central",
              "sample_station": "Jolarpettai", "sample_delay_minutes": 8},
}

ALIASES = {"tomatoes": "tomato", "onions": "onion", "carrots": "carrot", "chillies": "chilli",
           "dal": "toor dal", "rava": "semolina", "suji": "semolina"}
