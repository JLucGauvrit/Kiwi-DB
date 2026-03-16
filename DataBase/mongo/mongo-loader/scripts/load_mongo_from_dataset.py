#!/usr/bin/env python3
"""
Insert animal documents into MongoDB.

Usage:
  python3 scripts/load_mongo_from_dataset.py --uri mongodb://localhost:27017 --db animaux_db --collection animaux --drop
"""
import argparse
import os
from pymongo import MongoClient

ANIMAUX = [
    {
        "nom": "Lion",
        "espece": "Panthera leo",
        "famille": "Félidés",
        "habitat": "Savane",
        "continent": "Afrique",
        "poids_kg": 190,
        "longevite_ans": 16,
        "regime": "Carnivore",
        "statut_conservation": "Vulnérable",
        "description": "Le lion est le plus grand félin d'Afrique. Il vit en groupe appelé troupe.",
        "traits": ["crinière", "rugissement", "chasse en groupe"]
    },
    {
        "nom": "Éléphant d'Afrique",
        "espece": "Loxodonta africana",
        "famille": "Éléphantidés",
        "habitat": "Savane et forêt",
        "continent": "Afrique",
        "poids_kg": 5000,
        "longevite_ans": 70,
        "regime": "Herbivore",
        "statut_conservation": "En danger",
        "description": "Le plus grand animal terrestre. Ses défenses en ivoire en font une cible du braconnage.",
        "traits": ["trompe", "défenses", "mémoire exceptionnelle", "vie sociale"]
    },
    {
        "nom": "Grand Panda",
        "espece": "Ailuropoda melanoleuca",
        "famille": "Ursidés",
        "habitat": "Forêt de bambous",
        "continent": "Asie",
        "poids_kg": 120,
        "longevite_ans": 20,
        "regime": "Herbivore",
        "statut_conservation": "Vulnérable",
        "description": "Symbole de la conservation, le panda géant se nourrit quasi exclusivement de bambou.",
        "traits": ["pelage noir et blanc", "pouce supplémentaire", "solitaire"]
    },
    {
        "nom": "Tigre du Bengale",
        "espece": "Panthera tigris tigris",
        "famille": "Félidés",
        "habitat": "Forêt tropicale et mangrove",
        "continent": "Asie",
        "poids_kg": 220,
        "longevite_ans": 15,
        "regime": "Carnivore",
        "statut_conservation": "En danger",
        "description": "Le plus grand félin du monde. Excellent nageur, il chasse seul.",
        "traits": ["rayures", "nage", "territoire solitaire"]
    },
    {
        "nom": "Dauphin commun",
        "espece": "Delphinus delphis",
        "famille": "Delphinidés",
        "habitat": "Océan",
        "continent": "Mondial",
        "poids_kg": 80,
        "longevite_ans": 25,
        "regime": "Carnivore",
        "statut_conservation": "Préoccupation mineure",
        "description": "Mammifère marin très intelligent, le dauphin communique par ultrasons.",
        "traits": ["écholocation", "intelligence", "vie en groupe", "saut"]
    },
    {
        "nom": "Girafe",
        "espece": "Giraffa camelopardalis",
        "famille": "Giraffidés",
        "habitat": "Savane",
        "continent": "Afrique",
        "poids_kg": 1200,
        "longevite_ans": 25,
        "regime": "Herbivore",
        "statut_conservation": "Vulnérable",
        "description": "Le plus grand animal terrestre en hauteur. Son long cou lui permet d'atteindre les feuilles des acacias.",
        "traits": ["long cou", "taches", "langue bleue", "cœur puissant"]
    },
    {
        "nom": "Gorille des plaines",
        "espece": "Gorilla gorilla gorilla",
        "famille": "Hominidés",
        "habitat": "Forêt tropicale",
        "continent": "Afrique",
        "poids_kg": 180,
        "longevite_ans": 40,
        "regime": "Herbivore",
        "statut_conservation": "En danger critique",
        "description": "Le plus grand primate. Partage 98% de son ADN avec l'être humain.",
        "traits": ["dos argenté", "intelligence", "outil", "vie sociale"]
    },
    {
        "nom": "Loup gris",
        "espece": "Canis lupus",
        "famille": "Canidés",
        "habitat": "Forêt, toundra, montagne",
        "continent": "Eurasie et Amérique du Nord",
        "poids_kg": 40,
        "longevite_ans": 14,
        "regime": "Carnivore",
        "statut_conservation": "Préoccupation mineure",
        "description": "Prédateur social vivant en meute hiérarchisée. Ancêtre du chien domestique.",
        "traits": ["meute", "hurlements", "territoire", "endurance"]
    },
    {
        "nom": "Aigle royal",
        "espece": "Aquila chrysaetos",
        "famille": "Accipitridés",
        "habitat": "Montagne et forêt",
        "continent": "Eurasie et Amérique du Nord",
        "poids_kg": 4.5,
        "longevite_ans": 30,
        "regime": "Carnivore",
        "statut_conservation": "Préoccupation mineure",
        "description": "L'un des plus grands rapaces diurnes, reconnaissable à sa envergure imposante.",
        "traits": ["vue perçante", "grande envergure", "serres puissantes", "vol plané"]
    },
    {
        "nom": "Pieuvre géante du Pacifique",
        "espece": "Enteroctopus dofleini",
        "famille": "Octopodidés",
        "habitat": "Océan Pacifique",
        "continent": "Mondial",
        "poids_kg": 15,
        "longevite_ans": 5,
        "regime": "Carnivore",
        "statut_conservation": "Préoccupation mineure",
        "description": "La plus grande pieuvre connue. Très intelligente, elle peut ouvrir des bocaux et résoudre des problèmes.",
        "traits": ["8 tentacules", "camouflage", "encre", "intelligence"]
    },
    {
        "nom": "Cheetah",
        "espece": "Acinonyx jubatus",
        "famille": "Félidés",
        "habitat": "Savane",
        "continent": "Afrique",
        "poids_kg": 55,
        "longevite_ans": 12,
        "regime": "Carnivore",
        "statut_conservation": "Vulnérable",
        "description": "L'animal terrestre le plus rapide, pouvant atteindre 120 km/h.",
        "traits": ["vitesse", "taches noires", "griffes non rétractiles", "sprint court"]
    },
    {
        "nom": "Hippopotame",
        "espece": "Hippopotamus amphibius",
        "famille": "Hippopotamidés",
        "habitat": "Rivières et lacs",
        "continent": "Afrique",
        "poids_kg": 3000,
        "longevite_ans": 45,
        "regime": "Herbivore",
        "statut_conservation": "Vulnérable",
        "description": "Troisième plus grand mammifère terrestre. Passe ses journées dans l'eau.",
        "traits": ["semi-aquatique", "gueule énorme", "agressivité", "transpiration rouge"]
    }
]


def main():
    parser = argparse.ArgumentParser(description="Load animal data into MongoDB")
    parser.add_argument('--uri',        default=os.environ.get('MONGO_URI', 'mongodb://localhost:27017'))
    parser.add_argument('--db',         default='animaux_db')
    parser.add_argument('--collection', default='animaux')
    parser.add_argument('--drop',       action='store_true')
    args = parser.parse_args()

    client = MongoClient(args.uri)
    db = client[args.db]
    col = db[args.collection]

    if args.drop:
        print(f"Dropping collection {args.db}.{args.collection}")
        col.drop()

    col.insert_many(ANIMAUX)
    print(f"Done. Inserted {len(ANIMAUX)} animals into {args.db}.{args.collection}")


if __name__ == '__main__':
    main()
