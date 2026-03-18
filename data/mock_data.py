"""
Données mockées BRUTES pour 3 produits e-commerce.

PHILOSOPHIE:
  Les données sont BRUTES et NON ANALYSÉES. C'est le LLM qui fera l'analyse.
  
  - Le scraper retourne des prix par plateforme (déjà brut → inchangé)
  - Le sentiment analyzer retourne des AVIS CLIENTS EN TEXTE (pas des scores)
  - Le trend analyzer retourne des CHIFFRES BRUTS (pas d'interprétation)

  Le LLM reçoit ces données brutes et doit:
    - Lire les avis et identifier lui-même les thèmes, le sentiment, les patterns
    - Lire les chiffres de tendances et interpréter les directions, la saisonnalité
    - Croiser toutes les données pour produire des recommandations

Produits:
  - Apple AirPods Pro 2 (Tech)
  - Nike Air Max 90 (Mode/Sport)
  - Nespresso Vertuo Next (Maison)
"""


# =============================================================================
# DONNÉES DU WEB SCRAPER
# Prix et infos par plateforme — c'est déjà de la donnée brute, pas de changement
# =============================================================================

SCRAPER_DATA = {

    "airpods pro 2": {
        "product": "Apple AirPods Pro 2 (USB-C)",
        "category": "Écouteurs sans fil premium",
        "brand": "Apple",
        "platforms": [
            {"name": "Amazon", "price": 279.99, "currency": "EUR", "rating": 4.7, "total_reviews": 12453, "in_stock": True, "seller": "Apple (officiel)"},
            {"name": "Fnac", "price": 299.99, "currency": "EUR", "rating": 4.5, "total_reviews": 3211, "in_stock": True, "seller": "Fnac"},
            {"name": "Cdiscount", "price": 259.99, "currency": "EUR", "rating": 4.3, "total_reviews": 876, "in_stock": True, "seller": "TechDeals Pro"},
            {"name": "Darty", "price": 289.99, "currency": "EUR", "rating": 4.6, "total_reviews": 2104, "in_stock": False, "seller": "Darty"},
            {"name": "Boulanger", "price": 279.99, "currency": "EUR", "rating": 4.6, "total_reviews": 1567, "in_stock": True, "seller": "Boulanger"}
        ]
    },

    "nike air max 90": {
        "product": "Nike Air Max 90",
        "category": "Sneakers lifestyle",
        "brand": "Nike",
        "platforms": [
            {"name": "Nike.com", "price": 149.99, "currency": "EUR", "rating": 4.5, "total_reviews": 8934, "in_stock": True, "seller": "Nike (officiel)"},
            {"name": "Zalando", "price": 139.99, "currency": "EUR", "rating": 4.4, "total_reviews": 2567, "in_stock": True, "seller": "Zalando"},
            {"name": "Courir", "price": 149.99, "currency": "EUR", "rating": 4.3, "total_reviews": 1234, "in_stock": True, "seller": "Courir"},
            {"name": "Foot Locker", "price": 144.99, "currency": "EUR", "rating": 4.5, "total_reviews": 3456, "in_stock": True, "seller": "Foot Locker"},
            {"name": "Amazon", "price": 129.99, "currency": "EUR", "rating": 4.1, "total_reviews": 1890, "in_stock": True, "seller": "SneakerShop EU"}
        ]
    },

    "nespresso vertuo": {
        "product": "Nespresso Vertuo Next",
        "category": "Machine à café à capsules",
        "brand": "Nespresso (Nestlé)",
        "platforms": [
            {"name": "Nespresso.com", "price": 149.00, "currency": "EUR", "rating": 4.2, "total_reviews": 5678, "in_stock": True, "seller": "Nespresso (officiel)"},
            {"name": "Amazon", "price": 119.99, "currency": "EUR", "rating": 4.0, "total_reviews": 9876, "in_stock": True, "seller": "Amazon.fr"},
            {"name": "Boulanger", "price": 129.99, "currency": "EUR", "rating": 4.1, "total_reviews": 2345, "in_stock": True, "seller": "Boulanger"},
            {"name": "Darty", "price": 139.99, "currency": "EUR", "rating": 4.3, "total_reviews": 1876, "in_stock": True, "seller": "Darty"},
            {"name": "Cdiscount", "price": 109.99, "currency": "EUR", "rating": 3.9, "total_reviews": 654, "in_stock": False, "seller": "ElectroMenager+"}
        ]
    }
}


# =============================================================================
# DONNÉES DU SENTIMENT ANALYZER
# AVIS CLIENTS BRUTS — le LLM doit les lire et analyser lui-même
# =============================================================================

SENTIMENT_DATA = {

    "airpods pro 2": {
        "product": "Apple AirPods Pro 2 (USB-C)",
        "source": "Avis collectés sur Amazon, Fnac et Darty",
        "reviews": [
            {"author": "MusicLover75", "rating": 5, "date": "2025-02-15", "verified_purchase": True,
             "text": "Son exceptionnel, les basses sont profondes et les aigus cristallins. La réduction de bruit est bluffante, dans le métro je n'entends plus rien. Meilleur achat tech de l'année."},
            
            {"author": "TechGeek_Paris", "rating": 5, "date": "2025-02-10", "verified_purchase": True,
             "text": "L'ANC adaptative est incroyable. Elle s'ajuste en temps réel selon l'environnement. Le mode transparence est aussi très naturel. L'intégration avec mon iPhone est parfaite."},
            
            {"author": "CommuterDaily", "rating": 4, "date": "2025-01-28", "verified_purchase": True,
             "text": "Très bons écouteurs pour le trajet quotidien. Confortables même après 2h. Par contre, 280€ c'est quand même cher. J'hésite à les recommander à des amis à cause du prix."},
            
            {"author": "RunnerMarseille", "rating": 4, "date": "2025-01-20", "verified_purchase": True,
             "text": "Je les utilise pour courir. Bonne tenue dans les oreilles, le son est top. Mais attention à la pluie, j'ai eu un bug après une sortie sous l'averse. Depuis ça remarche."},
            
            {"author": "AudioPhile92", "rating": 5, "date": "2025-01-15", "verified_purchase": True,
             "text": "Ayant testé les Sony XM5 et les Bose QCUE, je peux dire que les AirPods Pro 2 sont au top. Le son est équilibré, l'ANC est la meilleure, et le boîtier USB-C enfin!"},
            
            {"author": "MamanDeTwo", "rating": 5, "date": "2025-01-10", "verified_purchase": True,
             "text": "Parfaits pour s'isoler quand les enfants font du bruit! La réduction de bruit est magique. Le confort est excellent, je les oublie dans les oreilles."},
            
            {"author": "BudgetConscious", "rating": 3, "date": "2025-01-05", "verified_purchase": True,
             "text": "Le son est bon mais honnêtement pour 280€ j'attendais mieux. Les Samsung Galaxy Buds font quasiment pareil pour 100€ de moins. Le premium Apple est dur à justifier."},
            
            {"author": "AndroidUser2025", "rating": 2, "date": "2024-12-28", "verified_purchase": True,
             "text": "J'ai un Samsung S24 et c'est la déception. Pas de spatial audio, l'ANC adaptative ne marche pas, la connexion est parfois instable. Ces écouteurs sont faits UNIQUEMENT pour iPhone."},
            
            {"author": "PodcastAddict", "rating": 5, "date": "2024-12-20", "verified_purchase": True,
             "text": "Pour les podcasts et appels, c'est le top. Le micro est excellent, mes collègues m'entendent parfaitement en visio. La réduction de bruit coupe le bruit du bureau open space."},
            
            {"author": "StudentLyon", "rating": 4, "date": "2024-12-15", "verified_purchase": True,
             "text": "Super pour étudier à la bibliothèque. L'ANC aide vraiment à se concentrer. Batterie correcte, environ 5h. Par contre le boîtier se raye facilement."},
            
            {"author": "GymRat_Bordeaux", "rating": 4, "date": "2024-12-10", "verified_purchase": True,
             "text": "Bons pour le sport, tiennent bien. Le son motive pendant les séances. La résistance à la sueur est OK. Seul bémol : après 10 mois la batterie tient 3h30 au lieu de 6h."},
            
            {"author": "DeçuApple", "rating": 2, "date": "2024-12-05", "verified_purchase": True,
             "text": "Mes AirPods Pro 2 ont commencé à grésiller dans l'oreille gauche après 8 mois. Apple me demande 89€ pour la réparation hors garantie. Pour des écouteurs à 280€, c'est inacceptable."},
            
            {"author": "MeloManiac", "rating": 5, "date": "2024-11-28", "verified_purchase": True,
             "text": "Le Lossless Audio avec le boîtier USB-C, c'est un game changer. La qualité sonore est un cran au-dessus de la première version. Apple a fait du très bon travail."},
            
            {"author": "VoyageurFrequent", "rating": 5, "date": "2024-11-20", "verified_purchase": True,
             "text": "Indispensables en avion. L'ANC coupe le bruit des moteurs à 90%. Le mode transparence pour les annonces est pratique. Le boîtier se recharge vite."},
            
            {"author": "CritiqueSévère", "rating": 3, "date": "2024-11-15", "verified_purchase": True,
             "text": "Bons écouteurs mais pas révolutionnaires par rapport aux Pro 1. L'amélioration ne justifie pas le rachat si on a déjà la version précédente. Apple survit sur sa marque."},
            
            {"author": "NouvelUtilisateur", "rating": 5, "date": "2024-11-10", "verified_purchase": True,
             "text": "Premier achat d'écouteurs premium et je comprends enfin pourquoi les gens paient ce prix. Le son, le confort, l'ANC — tout est parfait. Je ne peux plus m'en passer."}
        ]
    },

    "nike air max 90": {
        "product": "Nike Air Max 90",
        "source": "Avis collectés sur Nike.com, Zalando et Amazon",
        "reviews": [
            {"author": "SneakerHead_Lyon", "rating": 5, "date": "2025-02-18", "verified_purchase": True,
             "text": "La Air Max 90, c'est un classique indémodable. Le design est parfait, les couleurs sont fidèles aux photos. Elles vont avec absolument tout dans ma garde-robe."},
            
            {"author": "WalkerParis", "rating": 4, "date": "2025-02-12", "verified_purchase": True,
             "text": "Très confortables pour marcher en ville toute la journée. La bulle d'air absorbe bien les chocs. Par contre, elles taillent petit — prenez une demi-taille au-dessus."},
            
            {"author": "ModeFemme33", "rating": 5, "date": "2025-02-05", "verified_purchase": True,
             "text": "J'adore le coloris blanc/rose. Elles sont stylées et confortables. Je les porte avec des jeans, des jupes, même au bureau avec un look smart casual. Polyvalentes!"},
            
            {"author": "RunnerAmateur", "rating": 3, "date": "2025-01-30", "verified_purchase": True,
             "text": "Je les ai achetées pour courir, mauvaise idée. C'est une chaussure lifestyle, pas de running. Pour le style c'est top, pour le sport c'est insuffisant. Le support de la cheville est faible."},
            
            {"author": "VintageCollector", "rating": 5, "date": "2025-01-25", "verified_purchase": True,
             "text": "30 ans de design et toujours au top. J'en suis à ma 6ème paire depuis 2010. La qualité des matériaux a un peu baissé par rapport aux anciennes, mais le style reste imbattable."},
            
            {"author": "PapaDeAdo", "rating": 4, "date": "2025-01-18", "verified_purchase": True,
             "text": "Achetées pour mon fils de 16 ans qui ne jurait que par ça. Il est ravi. Par contre à 150€ la paire pour un ado qui va les détruire en 6 mois, ça pique."},
            
            {"author": "AchatAmazon_Fail", "rating": 1, "date": "2025-01-12", "verified_purchase": True,
             "text": "ATTENTION contrefaçon!! Commandé sur Amazon via un vendeur tiers. Les coutures sont mal faites, le logo est flou, la semelle sent le plastique. Retour immédiat. Achetez sur Nike.com."},
            
            {"author": "ConfortAvantTout", "rating": 4, "date": "2025-01-05", "verified_purchase": True,
             "text": "Confortables dès le premier jour, pas besoin de période de rodage. La bulle d'air visible est un plus esthétique. Bonne aération du pied. Idéales pour le quotidien."},
            
            {"author": "EtudiantFauché", "rating": 3, "date": "2024-12-28", "verified_purchase": True,
             "text": "Je les ai eues en solde à 110€, à ce prix c'est bien. Mais à 150€ prix plein, c'est cher pour des sneakers. Les New Balance 574 sont aussi bien pour 30€ de moins."},
            
            {"author": "UsureLyon", "rating": 2, "date": "2024-12-20", "verified_purchase": True,
             "text": "Après 4 mois d'utilisation quotidienne, la semelle est déjà bien usée et la bulle d'air semble moins réactive. Pour 150€, j'attendais une meilleure durabilité."},
            
            {"author": "FashionBlogger_Nantes", "rating": 5, "date": "2024-12-15", "verified_purchase": True,
             "text": "THE sneaker à avoir dans sa collection. Le coloris Infrared est mythique. Je les porte non-stop pour mes shootings. Le style rétro-sportif est très tendance cette saison."},
            
            {"author": "Taille_Problème", "rating": 2, "date": "2024-12-10", "verified_purchase": True,
             "text": "Commandé en 42 comme d'habitude, beaucoup trop serré. Échangé pour du 43, un peu grand. Il n'y a pas de demi-tailles sur ce modèle, c'est un vrai problème."},
            
            {"author": "MarathoNice", "rating": 4, "date": "2024-12-05", "verified_purchase": True,
             "text": "Je les utilise pour mes balades quotidiennes (5-10km). Confort correct, amorti satisfaisant. Le look est génial. Pas pour la course, mais parfaites pour la marche active."},
            
            {"author": "RetroFan_Lille", "rating": 5, "date": "2024-11-28", "verified_purchase": True,
             "text": "J'ai la OG de 1990 et cette réédition est très fidèle. Nike a gardé l'essence du modèle. La qualité est bonne, les matériaux sont solides. Un classique."},
            
            {"author": "MinimalistToulouse", "rating": 4, "date": "2024-11-20", "verified_purchase": True,
             "text": "Le coloris triple noir est sobre et élégant. Va avec tout. Confortable au quotidien. Petit bémol: les lacets sont un peu courts et la languette bouge parfois."}
        ]
    },

    "nespresso vertuo": {
        "product": "Nespresso Vertuo Next",
        "source": "Avis collectés sur Amazon, Boulanger et Nespresso.com",
        "reviews": [
            {"author": "CaféDuMatin", "rating": 5, "date": "2025-02-20", "verified_purchase": True,
             "text": "Le café est excellent! La crema est épaisse et onctueuse. Le système Vertuo est nettement supérieur à l'ancien Original pour les grandes tasses. J'adore le format Alto le matin."},
            
            {"author": "SimplicitéFan", "rating": 5, "date": "2025-02-14", "verified_purchase": True,
             "text": "Un seul bouton, c'est tout. La machine lit le code-barre de la capsule et fait tout automatiquement. Mon père de 78 ans l'utilise sans problème. Mise en route en 30 secondes."},
            
            {"author": "PanneAprès6Mois", "rating": 1, "date": "2025-02-08", "verified_purchase": True,
             "text": "Machine en panne après 6 mois. Le voyant orange clignote et impossible de faire un café. Le SAV m'a fait faire 10 manipulations de reset, rien ne marche. Ils m'envoient un colis de retour. 3 semaines sans café."},
            
            {"author": "BaristaAmateur", "rating": 4, "date": "2025-02-01", "verified_purchase": True,
             "text": "Bon café, belle crema. Mais quand on a goûté un vrai espresso fait avec une machine à grain, on sent la différence. C'est un bon compromis qualité/praticité, sans plus."},
            
            {"author": "BudgetRéaliste", "rating": 2, "date": "2025-01-25", "verified_purchase": True,
             "text": "La machine est bien mais le piège c'est les capsules. 0.50€ la capsule minimum, 2-3 cafés par jour = 45€ par mois. Et AUCUNE alternative compatible Vertuo. On est prisonnier de Nespresso à vie."},
            
            {"author": "DesignLover", "rating": 4, "date": "2025-01-20", "verified_purchase": True,
             "text": "La machine est belle, compacte, s'intègre bien dans ma cuisine. Le design est réussi. Le café est bon. Seul reproche : le bac à capsules usagées est trop petit, faut le vider tous les 3 jours."},
            
            {"author": "BruitMatinal", "rating": 3, "date": "2025-01-15", "verified_purchase": True,
             "text": "Le café est très bon MAIS la machine fait un bruit d'enfer au démarrage. Le système de centrifugation est bruyant. Impossible de faire un café à 6h du matin sans réveiller tout l'appartement."},
            
            {"author": "ConvertieVertuo", "rating": 5, "date": "2025-01-10", "verified_purchase": True,
             "text": "Je viens de Dolce Gusto et c'est le jour et la nuit. Le café est incomparablement meilleur. La mousse est naturelle, pas artificielle. Le choix de capsules est vaste. Je ne reviendrai jamais en arrière."},
            
            {"author": "Écolo_Sceptique", "rating": 3, "date": "2025-01-05", "verified_purchase": True,
             "text": "Le café est bon mais le système de capsules en aluminium me dérange. Oui Nespresso a un programme de recyclage mais combien de gens rapportent vraiment leurs capsules? Impact écologique discutable."},
            
            {"author": "DeuxièmePanne", "rating": 1, "date": "2024-12-28", "verified_purchase": True,
             "text": "Deuxième machine Vertuo Next en 2 ans. La première est tombée en panne après 11 mois, remplacée sous garantie. La deuxième commence à fuir par le bas. Qualité de fabrication déplorable."},
            
            {"author": "FanNespresso", "rating": 5, "date": "2024-12-20", "verified_purchase": True,
             "text": "J'ai le programme d'abonnement capsules, ça revient moins cher. Le café est top, les éditions limitées sont un plaisir. Le Barista Creations avec du lait, un délice. Machine fiable depuis 18 mois."},
            
            {"author": "ComparateurPrix", "rating": 2, "date": "2024-12-15", "verified_purchase": True,
             "text": "Calcul rapide: 3 cafés/jour × 0.50€ × 365 jours = 547€/an en capsules. Plus la machine à 130€. Alors qu'une machine à grain à 300€ avec du café en grain revient à 150€/an. Faites le calcul."},
            
            {"author": "MamanPressée", "rating": 5, "date": "2024-12-10", "verified_purchase": True,
             "text": "Avec 3 enfants, je n'ai pas le temps de moudre du café le matin. Capsule, bouton, café prêt en 25 secondes. La qualité est au rendez-vous et la variété des capsules est un plus. Indispensable."},
            
            {"author": "TechBruitMètre", "rating": 3, "date": "2024-12-05", "verified_purchase": True,
             "text": "J'ai mesuré: 72 dB pendant l'extraction. C'est aussi fort qu'un aspirateur. Le café est bon mais ce bruit est le défaut majeur de cette machine. Les anciennes Original étaient bien plus silencieuses."},
            
            {"author": "CadeauNoel", "rating": 4, "date": "2024-11-30", "verified_purchase": True,
             "text": "Reçu en cadeau de Noël, agréablement surpris. Je n'aimais pas le concept des capsules mais le café est vraiment bon. La crema est impressionnante. Par contre oui, les capsules coûtent cher sur le long terme."},
            
            {"author": "FuiteDeau", "rating": 1, "date": "2024-11-25", "verified_purchase": True,
             "text": "Après 9 mois, la machine fuit par le dessous. J'ai retrouvé une flaque d'eau sur mon plan de travail. Les forums sont pleins de gens avec le même problème. Défaut de conception connu mais Nespresso ne fait rien."}
        ]
    }
}


# =============================================================================
# DONNÉES DU TREND ANALYZER
# CHIFFRES BRUTS — pas d'interprétation, le LLM analysera lui-même
# =============================================================================

TRENDS_DATA = {

    "airpods pro 2": {
        "product": "Apple AirPods Pro 2 (USB-C)",
        "market": "france",
        "data_period": "Octobre 2024 - Mars 2025",
        "search_volume_monthly": [
            {"month": "Oct 2024", "search_index": 62},
            {"month": "Nov 2024", "search_index": 85},
            {"month": "Dec 2024", "search_index": 100},
            {"month": "Jan 2025", "search_index": 55},
            {"month": "Feb 2025", "search_index": 65},
            {"month": "Mar 2025", "search_index": 78}
        ],
        "avg_price_monthly": [
            {"month": "Oct 2024", "avg_price": 299.99},
            {"month": "Nov 2024", "avg_price": 279.99},
            {"month": "Dec 2024", "avg_price": 249.99},
            {"month": "Jan 2025", "avg_price": 289.99},
            {"month": "Feb 2025", "avg_price": 284.99},
            {"month": "Mar 2025", "avg_price": 281.99}
        ],
        "competitors": [
            {"name": "Sony WF-1000XM5", "current_avg_price": 269.99, "search_index_current": 45},
            {"name": "Samsung Galaxy Buds 3 Pro", "current_avg_price": 249.99, "search_index_current": 38},
            {"name": "Bose QuietComfort Ultra Earbuds", "current_avg_price": 299.99, "search_index_current": 30}
        ]
    },

    "nike air max 90": {
        "product": "Nike Air Max 90",
        "market": "france",
        "data_period": "Octobre 2024 - Mars 2025",
        "search_volume_monthly": [
            {"month": "Oct 2024", "search_index": 55},
            {"month": "Nov 2024", "search_index": 65},
            {"month": "Dec 2024", "search_index": 80},
            {"month": "Jan 2025", "search_index": 50},
            {"month": "Feb 2025", "search_index": 60},
            {"month": "Mar 2025", "search_index": 100}
        ],
        "avg_price_monthly": [
            {"month": "Oct 2024", "avg_price": 149.99},
            {"month": "Nov 2024", "avg_price": 144.99},
            {"month": "Dec 2024", "avg_price": 139.99},
            {"month": "Jan 2025", "avg_price": 119.99},
            {"month": "Feb 2025", "avg_price": 134.99},
            {"month": "Mar 2025", "avg_price": 142.99}
        ],
        "competitors": [
            {"name": "Adidas Stan Smith", "current_avg_price": 109.99, "search_index_current": 42},
            {"name": "New Balance 990v6", "current_avg_price": 199.99, "search_index_current": 35},
            {"name": "Nike Air Force 1", "current_avg_price": 119.99, "search_index_current": 90}
        ]
    },

    "nespresso vertuo": {
        "product": "Nespresso Vertuo Next",
        "market": "france",
        "data_period": "Octobre 2024 - Mars 2025",
        "search_volume_monthly": [
            {"month": "Oct 2024", "search_index": 65},
            {"month": "Nov 2024", "search_index": 95},
            {"month": "Dec 2024", "search_index": 100},
            {"month": "Jan 2025", "search_index": 45},
            {"month": "Feb 2025", "search_index": 50},
            {"month": "Mar 2025", "search_index": 58}
        ],
        "avg_price_monthly": [
            {"month": "Oct 2024", "avg_price": 149.00},
            {"month": "Nov 2024", "avg_price": 119.99},
            {"month": "Dec 2024", "avg_price": 109.99},
            {"month": "Jan 2025", "avg_price": 139.99},
            {"month": "Feb 2025", "avg_price": 134.99},
            {"month": "Mar 2025", "avg_price": 129.79}
        ],
        "competitors": [
            {"name": "Dolce Gusto Genio S", "current_avg_price": 79.99, "search_index_current": 55},
            {"name": "Tassimo My Way 2", "current_avg_price": 69.99, "search_index_current": 30},
            {"name": "Senseo Select", "current_avg_price": 59.99, "search_index_current": 25}
        ]
    }
}
