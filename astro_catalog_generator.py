#=============================================================================
#                          (c) AEROPIC 2026
#           all in one Messier/Caldwell/RASC/O'Meara catalog generator
#  
# https://github.com/aeropic/Messier_Caldwell_RASC_OMeara_catalog_generator
# http://www.messier.seds.org/xtra/similar/rasc-ngc.html
# https://www.catchersofthelight.com/astrophotography-hidden-treasures-list.aspx
# https://app.astrobin.com/u/GaryI?collection=677&i=esls3b#gallery
#
#   V5.2 : fixed visible to night option
#   V5.1 : plot of object altitude curve - added visible to night option
#   V5.0 : database restructuration: first field is direct type
#          internationalization with only one file
#   V4.4 : hollow heart when no note 
#   V4.3 : a free comment can be added when loving an object. 
#          TODO.txt can be edited as well to manually add single line comments
#   V4.2 : tooltip labels in LANG dictionnary
#   V4.1 : season is computed from RA value. RA added in database
#   V4.0.1 : added few comments all in english
#   V4.0 : added selection of todo objects (red heart) and export of TODO.txt
#   V3.1 : huge mod in hidden treasures!
#   V3.0 : added O'Meara lists (secret deep and hidden treasures)
#   V2.1 : season is displayed only when all seasons is selected
#   V2.0 : rolling menus for seasons and direction selection
#   V1.6 : display size for small object in orange (small means < 2'x2')
#   V1.5.1 : bug fix in size display
#   V1.5 : update of RASC objects usual name
#   V1.4 : image box points on telescopius when no image
#   V1.3.1 : tooltip border color light blue
#   V1.3 : logs in cmd window during thumbnails generation
#   V1.2 : .tif/tiff  is supported - dedicate view jpg files are created for display
#   V1.1.1 : .tif is partly supported (thumbnail OK, zoom KO)
#   V1.1 : syntax error in a comment fixed
#   V1.0 : first release
#============================================================================

import os
import re
import subprocess
import sys
import json
import importlib
from datetime import datetime


# --- DEPENDENCIES AUTO-INSTALL ---
def install_dependencies():
    """
    Checks if required dependencies (specifically Pillow) are installed.
    If missing, automatically upgrades pip and installs Pillow via subprocess.
    """
    try:
        importlib.import_module("PIL")
    except ImportError:
        print("Installation des dépendances manquantes...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "Pillow"])
        importlib.invalidate_caches()

install_dependencies()
from PIL import Image, ImageOps
    
# --- CONFIGURATION  ---
CONFIG = {
    "SOURCE_DIR": os.getcwd(),
    "SELECTED_CATALOG": "Messier",                 # selected catalog at startup: possible values : "Messier", "Caldwell", "RASC"
    "THUMB_DIR": "thumbnails",                     # name of the thumbnails directory
    "OUTPUT_HTML": "astro_catalog.html",          # name of the HTML page
    "THUMB_SIZE": 105,                            # size of the square thumbnail on the HTML page (max 200x200)
    "LATITUDE": 43.6,                              # your latitude
    "LONGITUDE": 1.5,                              # your longitude
    "ELEVATION": 150,                              # your elevation in meters
    "LIMIT_IMPOSSIBLE": 0,                        # degrees : change here if your horizon is masked
    "LIMIT_DIFFICILE": 20,
    "LIMIT_SMALL_OBJECT": 120,                    # arcseconds ; paint small objects size in orange
    "CHART_HEIGHT": 80,                            # Height of the graphic area inside the tooltip (in px)
    "TN_ALTITUDE_THRESHOLD": 30.0,                # altitude threshold (degrees) for visibility computation of high onjects
    "TN_LOW_ALTITUDE_FACTOR": 0.80                 # for low objects, they are "visible tonight" when their altitude becomes > (80% * maxalt) during astro period
}

# -----------------------------------------------
#  défault database and lang = FR
# place LANG_database.py in the script directory
# for english and other langages
# -----------------------------------------------

LANG = {
    "CATALOG": "mon catalogue",                              # "my catalog"
    "PAGE_TITLE": "Mon Catalogue Astro",                     # "my astro catalog"
    "UNIT_LABEL": "objets",                                  # "objects"
    "ALL": "Toutes saisons",                                 # "All seasons"
    "ALL_DIR": "Nord et Sud",                                # "North and South"
    "NO_DATE": "Date inconnue",                              # "unknown date"
    "NORTH": "Nord",                                         # "North"
    "SOUTH": "Sud",                                          # "South"
    "PROMPT_LABEL": "Entrez une description optionnelle :",  # "Enter an optional description:"
    "VALIDATE": "Valider",                                   # "Validate"
    "TYPES": {
        "N": "Nébuleuse",                                    # "nebula"
        "NP": "Néb. Planétaire",                             # "planetary nebula"
        "GC": "Amas Globulaire",                             # "globular cluster"
        "OC": "Amas Ouvert",                                 # "open cluster"
        "G": "Galaxie",                                      # "galaxy
        "SC": "Nuage Stellaire",                             # "stellar cloud"
        "D": "Étoile Double",                                # "double star"
        "A": "Astérisme",                                    # "asterim"
        "SNR": "Rémanent Supernova",                         # "super nova remnant"
        "EN": "Néb. Émission",                               # "Emission Nebula"
        "RN": "Néb. Réflexion",                              # "reflection nebula 
        "E/RN": "Néb. Ém./Réf.",                             # " emission and reflexion nebula"
        "N+C": "Amas + Néb.",                                # " Nebula and cluster"
        "QSR": "Qasar"
    },
    "FAMILIES_LABELS": {
        "ALL": "Tous objets",                               # "all objects"
        "NEB": "Nébuleuses",                                 # "nebula"
        "GAL": "Galaxies",
        "CLU": "Amas et divers"                              # "clusters and others"
    },
    "SEASONS": {"P": "Printemps", "E": "Été", "A": "Automne", "H": "Hiver","TN": "Ce soir"},      # {"P": "Spring", "E": "Summer", "A": "Automn", "H": "Winter", "TN": "Tonight"},
    "TOOLTIP_LABELS": {
        "TYPE": "Type ",                                      # "Type"
        "SEASON": "Saison ",                                  # "Season"
        "CONSTELLATION": "Constellation ",                    # "Constellation"
        "MAGNITUDE": "Magnitude ",                            # "Magnitude"
        "SIZE": "Taille ",                                     # "Size"
        "ELEVATION": "Elévation max "                         # "max elevation"
    }
}


# --- DATABASES (MESSIER, CALDWELL, RASC) ---
# --- you can translate the constellation name and the usual name but keep the NGC reference as is ---
# --- replace the lists here after with the "English_databases.txt" content for the english translation


# --- Format: [Type, Tech_Ref, Constellation, Mag, Size, Common Name, RA, Dec]


MESSIER_DATA = {
    1: ["SNR", "NGC 1952", "Taureau", "8.4", "6'x4'", "Nébuleuse du Crabe", 5.57, 22.0],
    2: ["GC", "NGC 7089", "Verseau", "6.3", "16'", "Amas du Verseau", 21.56, -0.8],
    3: ["GC", "NGC 5272", "Ch. de Chasse", "6.2", "18'", "Amas des Chiens de Chasse", 13.7, 28.4],
    4: ["GC", "NGC 6121", "Scorpion", "5.9", "36'", "Amas du Scorpion", 16.4, -26.5],
    5: ["GC", "NGC 5904", "Serpent", "5.7", "23'", "Amas du Serpent", 15.31, 2.1],
    6: ["OC", "NGC 6405", "Scorpion", "4.2", "25'", "Amas du Papillon", 17.67, -32.2],
    7: ["OC", "NGC 6475", "Scorpion", "3.3", "80'", "Amas de Ptolémée", 17.89, -34.8],
    8: ["N", "NGC 6523", "Sagittaire", "6.0", "90'x40'", "Nébuleuse de la Lagune", 18.06, -24.4],
    9: ["GC", "NGC 6333", "Ophiuchus", "7.7", "11'", "Amas d'Ophiuchus", 17.32, -18.5],
    10: ["GC", "NGC 6254", "Ophiuchus", "6.6", "20'", "Amas d'Ophiuchus", 16.95, -4.1],
    11: ["OC", "NGC 6705", "Écu", "5.8", "14'", "Amas du Canard Sauvage", 18.85, -6.3],
    12: ["GC", "NGC 6218", "Ophiuchus", "6.7", "16'", "Amas d'Ophiuchus", 16.79, -1.9],
    13: ["GC", "NGC 6205", "Hercule", "5.8", "20'", "Grand Amas d'Hercule", 16.69, 36.5],
    14: ["GC", "NGC 6402", "Ophiuchus", "7.6", "11'", "Amas d'Ophiuchus", 17.62, -3.3],
    15: ["GC", "NGC 7078", "Pégase", "6.2", "18'", "Amas de Pégase", 21.5, 12.2],
    16: ["N", "NGC 6611", "Serpent", "6.0", "7'", "Nébuleuse de l'Aigle", 18.31, -13.8],
    17: ["N", "NGC 6618", "Sagittaire", "6.0", "11'", "Nébuleuse Omega", 18.35, -16.2],
    18: ["OC", "NGC 6613", "Sagittaire", "7.5", "9'", "Cygne Noir", 18.33, -17.1],
    19: ["GC", "NGC 6273", "Ophiuchus", "6.8", "17'", "Amas d'Ophiuchus", 17.04, -26.3],
    20: ["N", "NGC 6514", "Sagittaire", "6.3", "28'", "Nébuleuse Trifide", 18.04, -23.0],
    21: ["OC", "NGC 6531", "Sagittaire", "6.5", "13'", "Amas du Sagittaire", 18.08, -22.5],
    22: ["GC", "NGC 6656", "Sagittaire", "5.1", "32'", "Grand Amas du Sagittaire", 18.6, -23.9],
    23: ["OC", "NGC 6494", "Sagittaire", "6.9", "27'", "Amas du Sagittaire", 17.95, -19.0],
    24: ["SC", "NGC 6603", "Sagittaire", "4.6", "90'", "Petit Nuage Stellaire du Sagittaire", 18.28, -18.4],
    25: ["OC", "IC 4725", "Sagittaire", "4.6", "32'", "Amas du Sagittaire", 18.53, -19.2],
    26: ["OC", "NGC 6694", "Écu", "8.0", "15'", "Amas de l'Écu", 18.75, -9.4],
    27: ["NP", "NGC 6853", "Petit Renard", "7.4", "8'x6'", "Nébuleuse Dumbbell", 19.99, 22.7],
    28: ["GC", "NGC 6626", "Sagittaire", "6.8", "11'", "Amas du Sagittaire", 18.41, -24.9],
    29: ["OC", "NGC 6913", "Cygne", "7.1", "7'", "Amas du Cygne", 20.4, 38.5],
    30: ["GC", "NGC 7099", "Capricorne", "7.2", "12'", "Amas du Capricorne", 21.67, -23.2],
    31: ["G", "NGC 224", "Andromède", "3.4", "190'x60'", "Galaxie d'Andromède", 0.71, 41.3],
    32: ["G", "NGC 221", "Andromède", "8.1", "8'x6'", "Le Gentil (M32)", 0.71, 40.9],
    33: ["G", "NGC 598", "Triangle", "5.7", "70'x40'", "Galaxie du Triangle", 1.56, 30.7],
    34: ["OC", "NGC 1039", "Persée", "5.2", "35'", "Amas de Persée", 2.7, 42.8],
    35: ["OC", "NGC 2168", "Gémeaux", "5.1", "28'", "Amas des Gémeaux", 6.15, 24.3],
    36: ["OC", "NGC 1960", "Cocher", "6.0", "12'", "Amas du Cocher", 5.6, 34.1],
    37: ["OC", "NGC 2099", "Cocher", "5.6", "24'", "Amas du Cocher", 5.87, 32.5],
    38: ["OC", "NGC 1912", "Cocher", "6.4", "21'", "Amas de l'Étoile de Mer", 5.47, 35.8],
    39: ["OC", "NGC 7092", "Cygne", "4.6", "32'", "Amas du Cygne", 21.54, 48.4],
    40: ["D", "WNC 4", "Grande Ourse", "8.4", "0.8'", "Winnecke 4", 12.37, 58.1],
    41: ["OC", "NGC 2287", "Grand Chien", "4.5", "38'", "Amas du Petit Rucher", 6.78, -20.7],
    42: ["N", "NGC 1976", "Orion", "4.0", "85'x60'", "Nébuleuse d'Orion", 5.59, -5.4],
    43: ["N", "NGC 1982", "Orion", "9.0", "20'x15'", "Nébuleuse de De Mairan", 5.59, -5.2],
    44: ["OC", "NGC 2632", "Cancer", "3.1", "95'", "Amas de la Crèche", 8.67, 19.7],
    45: ["OC", "NGC 1432", "Taureau", "1.6", "110'", "Les Pléiades", 3.78, 24.1],
    46: ["OC", "NGC 2437", "Poupe", "6.1", "27'", "Amas de la Poupe", 7.7, -14.8],
    47: ["OC", "NGC 2422", "Poupe", "4.4", "30'", "Amas de la Poupe", 7.61, -14.4],
    48: ["OC", "NGC 2548", "Hydre", "5.8", "54'", "Amas de l'Hydre", 8.23, -5.8],
    49: ["G", "NGC 4472", "Vierge", "8.4", "10'x9'", "Galaxie de la Vierge", 12.5, 8.0],
    50: ["OC", "NGC 2323", "Licorne", "5.9", "16'", "Amas de la Licorne", 7.05, -8.3],
    51: ["G", "NGC 5194", "Ch. de Chasse", "8.4", "11'x7'", "Galaxie du Tourbillon", 13.5, 47.2],
    52: ["OC", "NGC 7654", "Cassiopée", "6.9", "13'", "Amas de Cassiopée", 23.4, 61.6],
    53: ["GC", "NGC 5024", "Chevelure", "7.6", "13'", "Amas de la Chevelure", 13.21, 18.2],
    54: ["GC", "NGC 6715", "Sagittaire", "7.6", "12'", "Amas du Sagittaire", 18.92, -30.5],
    55: ["GC", "NGC 6809", "Sagittaire", "6.3", "19'", "Amas du Sagittaire", 19.67, -30.9],
    56: ["GC", "NGC 6779", "Lyre", "8.3", "9'", "Amas de la Lyre", 19.28, 33.0],
    57: ["NP", "NGC 6720", "Lyre", "8.8", "1.5'x1'", "Nébuleuse de l'Anneau", 18.89, 33.0],
    58: ["G", "NGC 4579", "Vierge", "9.7", "6'x5'", "Galaxie de la Vierge", 12.63, 11.8],
    59: ["G", "NGC 4621", "Vierge", "10.6", "5'x4'", "Galaxie de la Vierge", 12.7, 11.6],
    60: ["G", "NGC 4649", "Vierge", "8.8", "7'x6'", "Galaxie de la Vierge", 12.73, 11.6],
    61: ["G", "NGC 4303", "Vierge", "9.7", "6'x6'", "Galaxie de la Vierge", 12.37, 4.5],
    62: ["GC", "NGC 6266", "Ophiuchus", "6.5", "15'", "Amas d'Ophiuchus", 17.02, -30.1],
    63: ["G", "NGC 5055", "Ch. de Chasse", "8.6", "12'x8'", "Galaxie du Tournesol", 13.26, 42.0],
    64: ["G", "NGC 4826", "Chevelure", "8.5", "10'x5'", "Galaxie de l'Œil Noir", 12.94, 21.7],
    65: ["G", "NGC 3623", "Lion", "9.3", "10'x3'", "Galaxie du Lion", 11.32, 13.1],
    66: ["G", "NGC 3627", "Lion", "8.9", "9'x4'", "Galaxie du Lion", 11.34, 13.0],
    67: ["OC", "NGC 2682", "Cancer", "6.1", "30'", "Amas du Cobra Royal", 8.85, 11.8],
    68: ["GC", "NGC 4590", "Hydre", "7.8", "11'", "Amas de l'Hydre", 12.66, -26.7],
    69: ["GC", "NGC 6637", "Sagittaire", "7.6", "10'", "Amas du Sagittaire", 18.52, -32.3],
    70: ["GC", "NGC 6681", "Sagittaire", "7.9", "9'", "Amas du Sagittaire", 18.72, -32.3],
    71: ["GC", "NGC 6838", "Flèche", "8.2", "7'", "Amas de la Flèche", 19.89, 18.8],
    72: ["GC", "NGC 6981", "Verseau", "9.3", "7'", "Amas du Verseau", 20.89, -12.5],
    73: ["A", "NGC 6994", "Verseau", "9.0", "2.8'", "Astérisme du Verseau", 20.98, -12.6],
    74: ["G", "NGC 628", "Poissons", "9.4", "10'x10'", "Galaxie du Fantôme", 1.61, 15.8],
    75: ["GC", "NGC 6864", "Sagittaire", "8.5", "7'", "Amas du Sagittaire", 20.1, -21.9],
    76: ["NP", "NGC 650", "Persée", "10.1", "2.7'x1.8'", "Nébuleuse de la Petite Haltère", 1.7, 51.6],
    77: ["G", "NGC 1068", "Baleine", "8.9", "7'x6'", "Galaxie de la Baleine", 2.71, -0.0],
    78: ["N", "NGC 2068", "Orion", "8.3", "8'x6'", "M78 (Nébuleuse)", 5.78, 0.1],
    79: ["GC", "NGC 1904", "Lièvre", "7.7", "10'", "Amas du Lièvre", 5.41, -24.5],
    80: ["GC", "NGC 6093", "Scorpion", "7.3", "10'", "Amas du Scorpion", 16.28, -22.9],
    81: ["G", "NGC 3031", "Grande Ourse", "6.9", "26'x14'", "Galaxie de Bode", 9.92, 69.1],
    82: ["G", "NGC 3034", "Grande Ourse", "8.4", "11'x4'", "Galaxie du Cigare", 9.93, 69.7],
    83: ["G", "NGC 5236", "Hydre", "7.5", "13'x11'", "Galaxie du Moulinet Austral", 13.62, -29.9],
    84: ["G", "NGC 4374", "Vierge", "9.1", "6'x6'", "Galaxie de la Vierge", 12.42, 12.9],
    85: ["G", "NGC 4382", "Chevelure", "9.1", "7'x5'", "Galaxie de la Chevelure", 12.42, 18.2],
    86: ["G", "NGC 4406", "Vierge", "8.9", "9'x6'", "Galaxie de la Vierge", 12.44, 12.9],
    87: ["G", "NGC 4486", "Vierge", "8.6", "8'x8'", "Virgo A", 12.51, 12.4],
    88: ["G", "NGC 4501", "Chevelure", "9.6", "7'x4'", "Galaxie de la Chevelure", 12.53, 14.4],
    89: ["G", "NGC 4552", "Vierge", "9.8", "5'x5'", "Galaxie de la Vierge", 12.59, 12.6],
    90: ["G", "NGC 4569", "Vierge", "9.5", "10'x4'", "Galaxie de la Vierge", 12.61, 13.2],
    91: ["G", "NGC 4548", "Chevelure", "10.2", "5'x4'", "Galaxie de la Chevelure", 12.59, 14.5],
    92: ["GC", "NGC 6341", "Hercule", "6.3", "14'", "Amas d'Hercule", 17.28, 43.1],
    93: ["OC", "NGC 2447", "Poupe", "6.0", "22'", "Amas de la Poupe", 7.74, -23.9],
    94: ["G", "NGC 4736", "Ch. de Chasse", "8.2", "11'x9'", "Galaxie de l'Œil de Crocodile", 12.85, 41.1],
    95: ["G", "NGC 3351", "Lion", "9.7", "7'x5'", "Galaxie du Lion", 10.73, 11.7],
    96: ["G", "NGC 3368", "Lion", "9.2", "8'x5'", "Galaxie du Lion", 10.78, 11.8],
    97: ["NP", "NGC 3587", "Grande Ourse", "9.9", "3.4'", "Nébuleuse du Hibou", 11.25, 55.0],
    98: ["G", "NGC 4192", "Chevelure", "10.1", "10'x3'", "Galaxie de la Chevelure", 12.23, 14.9],
    99: ["G", "NGC 4254", "Chevelure", "9.9", "5'x5'", "Galaxie du Coma Pinwheel", 12.31, 14.4],
    100: ["G", "NGC 4321", "Chevelure", "9.3", "7'x6'", "Galaxie de la Chevelure", 12.38, 15.8],
    101: ["G", "NGC 5457", "Grande Ourse", "7.9", "28'x27'", "Galaxie du Moulinet", 14.05, 54.4],
    102: ["G", "NGC 5866", "Dragon", "9.9", "6'x3'", "Galaxie du Fuseau", 15.11, 55.8],
    103: ["OC", "NGC 581", "Cassiopée", "7.4", "6'", "Amas de Cassiopée", 1.55, 60.7],
    104: ["G", "NGC 4594", "Vierge", "8.0", "9'x4'", "Galaxie du Sombrero", 12.67, -11.6],
    105: ["G", "NGC 3379", "Lion", "9.3", "5'x5'", "Galaxie du Lion", 10.79, 12.6],
    106: ["G", "NGC 4258", "Ch. de Chasse", "8.4", "18'x7'", "Galaxie des Chiens de Chasse", 12.32, 47.3],
    107: ["GC", "NGC 6171", "Ophiuchus", "7.9", "13'", "Amas d'Ophiuchus", 16.54, -13.1],
    108: ["G", "NGC 3556", "Grande Ourse", "10.0", "9'x2'", "Galaxie de la Planche à Surf", 11.19, 53.4],
    109: ["G", "NGC 3992", "Grande Ourse", "9.8", "8'x5'", "Galaxie de la Grande Ourse", 11.96, 53.4],
    110: ["G", "NGC 205", "Andromède", "8.1", "17'x10'", "Galaxie d'Andromède (sat.)", 0.67, 41.7]
}



CALDWELL_DATA = {
    1: ["OC", "NGC 188", "Céphée", "8.1", "13'", "NGC 188", 0.74, 85.3],
    2: ["NP", "NGC 40", "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 0.05, 72.5],
    3: ["G", "NGC 4236", "Dragon", "9.7", "18.6'x6.9'", "Galaxie du Dragon", 12.28, 69.5],
    4: ["RN", "NGC 7023", "Céphée", "-", "18'x18'", "Nébuleuse de l'Iris", 21.03, 68.2],
    5: ["G", "IC 342", "Girafe", "8.4", "21.1'x20.9'", "Galaxie de la Girafe", 3.78, 68.1],
    6: ["NP", "NGC 6543", "Dragon", "8.1", "18''", "Nébuleuse de l'Œil de Chat", 17.98, 66.6],
    7: ["G", "NGC 2403", "Girafe", "8.4", "24.9'x12'", "NGC 2403", 7.62, 65.6],
    8: ["OC", "NGC 559", "Cassiopée", "7.1", "5.8'", "NGC 559", 1.49, 63.3],
    9: ["EN", "Sh2-155", "Céphée", "-", "50'x40'", "Nébuleuse de la Grotte", 22.95, 62.3],
    10: ["OC", "NGC 663", "Cassiopée", "7.1", "16'", "NGC 663", 1.77, 61.2],
    11: ["EN", "NGC 7635", "Cassiopée", "-", "15'x8'", "Nébuleuse de la Bulle", 23.35, 61.2],
    12: ["G", "NGC 6946", "Céphée", "8.9", "11.5'x11.5'", "Galaxie du Feu d'Artifice", 20.58, 60.1],
    13: ["OC", "NGC 457", "Cassiopée", "6.7", "13'", "Amas de la Chouette", 1.32, 58.3],
    14: ["OC", "NGC 869", "Persée", "4.4", "30'", "Double Amas de Persée", 2.32, 57.1],
    15: ["NP", "NGC 6826", "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 19.75, 50.5],
    16: ["OC", "NGC 7243", "Lézard", "6.4", "20'", "NGC 7243", 22.25, 49.9],
    17: ["G", "NGC 147", "Cassiopée", "9.1", "13'x8'", "NGC 147", 0.55, 48.5],
    18: ["G", "NGC 185", "Cassiopée", "9.2", "12'x10'", "NGC 185", 0.65, 48.3],
    19: ["EN", "IC 5146", "Céphée", "-", "12'", "Nébuleuse du Cocon", 21.89, 47.3],
    20: ["EN", "NGC 7000", "Cygne", "-", "120'x100'", "Nébuleuse de l'Amérique du Nord", 20.99, 44.3],
    21: ["G", "NGC 4449", "Chiens de Chasse", "9.4", "5'x4'", "NGC 4449", 12.47, 44.1],
    22: ["NP", "NGC 7662", "Andromède", "8.3", "20''", "Nébuleuse de la Boule de Neige Bleue", 23.43, 42.5],
    23: ["G", "NGC 891", "Andromède", "10.0", "13'x3'", "Galaxie de l'Aiguille d'Argent", 2.38, 42.3],
    24: ["G", "NGC 1275", "Persée", "11.7", "2'x2'", "Perseus A", 3.33, 41.5],
    25: ["GC", "NGC 2419", "Lynx", "10.4", "4'", "Amas de l'Errant Intergalactique", 7.63, 38.9],
    26: ["G", "NGC 4244", "Chiens de Chasse", "10.2", "16'x2'", "NGC 4244", 12.3, 37.8],
    27: ["EN", "NGC 6888", "Cygne", "-", "20'x10'", "Nébuleuse du Croissant", 20.2, 38.4],
    28: ["OC", "NGC 752", "Andromède", "5.2", "45'", "NGC 752", 1.96, 37.8],
    29: ["G", "NGC 5005", "Chiens de Chasse", "9.8", "5'x3'", "NGC 5005", 13.18, 37.1],
    30: ["G", "NGC 7331", "Pégase", "9.5", "11'x4'", "Galaxie de Deer Lick", 22.62, 34.4],
    31: ["EN", "IC 405", "Cocher", "-", "30'x20'", "Nébuleuse de l'Étoile Flamboyante", 5.27, 34.3],
    32: ["G", "NGC 4631", "Chiens de Chasse", "9.3", "15'x3'", "Galaxie de la Baleine", 12.7, 32.5],
    33: ["SNR", "NGC 6992", "Cygne", "-", "78'x8'", "Grande Dentelle du Cygne", 20.94, 31.7],
    34: ["SNR", "NGC 6960", "Cygne", "-", "70'x6'", "Petite Dentelle du Cygne", 20.76, 30.7],
    35: ["G", "NGC 4889", "Chevelure de Bérénice", "11.4", "1'x1'", "Amas de la Chevelure", 13.0, 28.0],
    36: ["G", "NGC 4559", "Chevelure de Bérénice", "9.6", "11'x5'", "NGC 4559", 12.6, 28.0],
    37: ["OC", "NGC 6885", "Petit Renard", "6.0", "14'", "NGC 6885", 20.2, 26.5],
    38: ["G", "NGC 4565", "Chevelure de Bérénice", "9.6", "16'x3'", "Galaxie de l'Aiguille", 12.6, 26.0],
    39: ["NP", "NGC 2392", "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 7.48, 20.9],
    40: ["G", "NGC 3626", "Lion", "10.7", "3'x2'", "NGC 3626", 11.33, 18.4],
    41: ["OC", "Mel 25", "Taureau", "0.5", "330'", "Les Hyades", 4.45, 15.9],
    42: ["GC", "NGC 7006", "Dauphin", "10.6", "3'", "NGC 7006", 21.02, 16.2],
    43: ["G", "NGC 7814", "Pégase", "10.0", "7'x2'", "NGC 7814", 0.05, 16.1],
    44: ["G", "NGC 7479", "Pégase", "10.3", "5'x4'", "NGC 7479", 23.08, 12.3],
    45: ["G", "NGC 5248", "Bouvier", "10.0", "5'x5'", "NGC 5248", 13.63, 8.9],
    46: ["EN", "NGC 2261", "Licorne", "-", "2'x1'", "Nébuleuse Variable de Hubble", 6.65, 8.7],
    47: ["GC", "NGC 6934", "Dauphin", "8.3", "7'", "NGC 6934", 20.57, 7.4],
    48: ["G", "NGC 2775", "Hydre", "9.2", "5'x4'", "NGC 2775", 9.17, 7.0],
    49: ["EN", "NGC 2237", "Licorne", "-", "80'x60'", "Nébuleuse de la Rosette", 6.54, 5.0],
    50: ["OC", "NGC 2244", "Licorne", "4.8", "24'", "Amas de la Rosette", 6.54, 4.9],
    51: ["G", "IC 1613", "Baleine", "9.0", "16'x15'", "IC 1613", 1.08, 2.1],
    52: ["G", "NGC 4697", "Vierge", "9.4", "4'x3'", "NGC 4697", 12.81, -5.8],
    53: ["G", "NGC 3115", "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", 10.09, -7.7],
    54: ["OC", "NGC 2506", "Licorne", "7.6", "14'", "NGC 2506", 8.0, -10.8],
    55: ["NP", "NGC 7009", "Verseau", "8.0", "25''", "Nébuleuse Saturne", 21.07, -11.4],
    56: ["NP", "NGC 246", "Baleine", "8.0", "4'", "Nébuleuse du Crâne", 0.78, -11.9],
    57: ["G", "NGC 6822", "Sagittaire", "7.5", "15'x13'", "Galaxie de Barnard", 19.75, -14.8],
    58: ["OC", "NGC 2360", "Grand Chien", "7.2", "20'", "Amas de Caroline", 7.3, -15.6],
    59: ["NP", "NGC 3242", "Hydre", "8.3", "16''", "Le Fantôme de Jupiter", 10.41, -18.6],
    60: ["G", "NGC 4038", "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes A", 12.03, -18.9],
    61: ["G", "NGC 4039", "Corbeau", "10.3", "3'x2'", "Galaxies des Antennes B", 12.03, -19.0],
    62: ["G", "NGC 247", "Baleine", "8.9", "12'x3'", "NGC 247", 0.78, -20.8],
    63: ["NP", "NGC 7293", "Verseau", "7.3", "13'", "Nébuleuse de l'Hélice", 22.49, -20.8],
    64: ["OC", "NGC 2362", "Grand Chien", "4.1", "20'", "NGC 2362", 7.31, -24.9],
    65: ["G", "NGC 253", "Sculpteur", "7.1", "25'x7'", "Galaxie du Sculpteur", 0.79, -25.3],
    66: ["GC", "NGC 5694", "Hydre", "8.5", "2'", "NGC 5694", 14.66, -26.5],
    67: ["G", "NGC 1097", "Fourneau", "9.3", "9'x6'", "NGC 1097", 2.77, -30.3],
    68: ["EN", "NGC 6729", "Couronne Australe", "-", "1'", "NGC 6729", 19.03, -36.9],
    69: ["NP", "NGC 6302", "Scorpion", "9.6", "2'", "Nébuleuse du Papillon", 17.23, -37.1],
    70: ["G", "NGC 300", "Sculpteur", "8.1", "12'x9'", "NGC 300", 0.91, -37.7],
    71: ["OC", "NGC 2477", "Poupe", "4.2", "27'", "NGC 2477", 7.87, -38.5],
    72: ["G", "NGC 55", "Sculpteur", "7.8", "31'x6'", "NGC 55", 0.25, -39.2],
    73: ["GC", "NGC 1851", "Colombe", "7.3", "11'", "NGC 1851", 5.24, -40.1],
    74: ["NP", "NGC 3132", "Voiles", "8.2", "1'", "Nébuleuse du Huit Éclatant", 10.12, -40.4],
    75: ["OC", "NGC 6124", "Loup", "5.8", "40'", "NGC 6124", 16.42, -40.7],
    76: ["OC", "NGC 6231", "Scorpion", "2.6", "15'", "NGC 6231", 16.9, -41.8],
    77: ["G", "NGC 5128", "Centaure", "6.8", "18'x14'", "Centaurus A", 13.42, -43.0],
    78: ["GC", "NGC 5139", "Centaure", "3.7", "36'", "Omega Centauri", 13.45, -47.5],
    79: ["OC", "NGC 4755", "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", 12.89, -60.3],
    80: ["GC", "NGC 5139", "Centaure", "3.7", "36'", "Omega Centauri bis", 13.45, -47.5],
    81: ["GC", "NGC 6352", "Autel", "8.1", "6'", "NGC 6352", 17.42, -48.4],
    82: ["GC", "NGC 6362", "Autel", "8.1", "12'", "NGC 6362", 17.53, -67.0],
    83: ["G", "NGC 4945", "Centaure", "8.6", "13'x4'", "NGC 4945", 13.09, -49.5],
    84: ["GC", "NGC 5286", "Centaure", "7.4", "10'", "NGC 5286", 13.77, -51.4],
    85: ["OC", "IC 2391", "Voiles", "2.5", "50'", "IC 2391", 8.67, -53.0],
    86: ["GC", "NGC 6397", "Autel", "5.3", "30'", "NGC 6397", 17.68, -53.7],
    87: ["GC", "NGC 1261", "Horloge", "8.4", "7'", "NGC 1261", 3.2, -55.2],
    88: ["OC", "NGC 5823", "Compas", "9.1", "11'", "NGC 5823", 15.09, -55.6],
    89: ["OC", "NGC 6067", "Règle", "5.1", "14'", "NGC 6067", 16.22, -54.2],
    90: ["NP", "NGC 2867", "Carène", "10.9", "18''", "NGC 2867", 9.36, -58.3],
    91: ["OC", "NGC 3532", "Carène", "3.9", "41'", "NGC 3532", 11.11, -58.7],
    92: ["EN", "NGC 3372", "Carène", "-", "120'", "Nébuleuse d'Eta Carinae", 10.75, -59.7],
    93: ["GC", "NGC 6752", "Paon", "5.4", "27'", "NGC 6752", 19.18, -59.9],
    94: ["OC", "NGC 4755", "Croix du Sud", "4.2", "10'", "La Boîte à Bijoux", 12.89, -60.3],
    95: ["OC", "NGC 6025", "Triangle Austral", "5.1", "12'", "NGC 6025", 16.03, -60.5],
    96: ["OC", "NGC 2516", "Carène", "3.8", "30'", "NGC 2516", 7.97, -60.8],
    97: ["OC", "NGC 3766", "Centaure", "3.9", "12'", "NGC 3766", 11.6, -61.5],
    98: ["OC", "NGC 4609", "Croix du Sud", "4.1", "5'", "NGC 4609", 12.71, -61.0],
    99: ["EN", "C99", "Croix du Sud", "-", "420'x300'", "Nébuleuse du Sac à Charbon", 12.83, -62.5],
    100: ["EN", "IC 2944", "Centaure", "-", "60'", "Nébuleuse du Poulet qui Court", 11.6, -63.0],
    101: ["G", "NGC 6744", "Paon", "8.3", "16'x11'", "NGC 6744", 19.16, -63.9],
    102: ["OC", "IC 2602", "Carène", "1.9", "100'", "Pléiades du Sud", 10.72, -64.4],
    103: ["EN", "NGC 2070", "Dorade", "-", "40'", "Nébuleuse de la Tarentule", 5.65, -69.1],
    104: ["GC", "NGC 47", "Toucan", "4.0", "31'", "NGC 47", 0.4, -72.1],
    105: ["GC", "NGC 4833", "Mouche", "7.8", "14'", "NGC 4833", 12.99, -70.9],
    106: ["GC", "NGC 104", "Toucan", "4.0", "31'", "47 Tucanae", 0.4, -72.1],
    107: ["GC", "NGC 6101", "Oiseau de Paradis", "9.2", "10'", "NGC 6101", 16.43, -72.2],
    108: ["GC", "NGC 4372", "Mouche", "7.2", "20'", "NGC 4372", 12.43, -73.0],
    109: ["NP", "NGC 3195", "Caméléon", "10.6", "15''", "NGC 3195", 10.16, -81.2]
}



RASC_DATA = {
    1: ["NP", "NGC 7009", "Verseau", "8.3", "25''", "Nébuleuse Saturne", 21.07, -11.4],
    2: ["NP", "NGC 7293", "Verseau", "6.5", "12'50''", "Nébuleuse de l'Hélice", 22.49, -20.8],
    3: ["G", "NGC 7331", "Pégase", "9.5", "10.7x4.0'", "Galaxie de Deer Lick", 22.62, 34.4],
    4: ["EN", "NGC 7635", "Cassiopée", "-", "15x8'", "Nébuleuse de la Bulle", 23.35, 61.2],
    5: ["OC", "NGC 7789", "Cassiopée", "6.7", "16'", "Amas de la Rose Blanche", 23.95, 56.7],
    6: ["G", "NGC 185", "Cassiopée", "11.7", "2x2'", "Galaxie naine de Cassiopée", 0.65, 48.3],
    7: ["EN", "NGC 281", "Cassiopée", "-", "35x30'", "Nébuleuse Pacman", 0.87, 56.6],
    8: ["OC", "NGC 457", "Cassiopée", "6.4", "13'", "Amas de la Chouette", 1.32, 58.3],
    9: ["OC", "NGC 663", "Cassiopée", "7.1", "16'", "Amas de l'Écharpe (Scarf Cluster)", 1.77, 61.2],
    10: ["NP", "NGC 1289", "Cassiopée", "12.3", "34''", "Phantom Streak Nebula", 0.51, 61.3],
    11: ["NP", "NGC 7662", "Andromède", "9.2", "20''", "Nébuleuse de la Boule de Neige Bleue", 23.43, 42.5],
    12: ["G", "NGC 891", "Andromède", "10", "13.5x2.8'", "Galaxie de l'Aiguille d'Argent", 2.38, 42.3],
    13: ["G", "NGC 253", "Sculpteur", "7.1", "25.1x7.4'", "Galaxie du Sculpteur", 0.79, -25.3],
    14: ["G", "NGC 772", "Bélier", "10.3", "7.1x4.5'", "Galaxie Spirale", 1.98, 19.0],
    15: ["NP", "NGC 246", "Baleine", "8.0", "3'45''", "Nébuleuse du Crâne", 0.78, -11.9],
    16: ["G", "NGC 936", "Baleine", "10.1", "5.2x4.4'", "Galaxie lenticulaire", 2.47, -1.1],
    17: ["OC", "NGC 869", "Persée", "4.4", "30'/30'", "Double Amas de Persée", 2.32, 57.1],
    18: ["G", "NGC 1023", "Persée", "9.5", "8.7x4.3'", "Galaxie lenticulaire", 2.67, 39.0],
    19: ["EN", "NGC 1491", "Persée", "-", "3.0x3.0'", "Fossil Footprint Nebula", 4.05, 51.3],
    20: ["NP", "NGC 1501", "Girafe", "12.0", "52''", "Nébuleuse de l'Huître", 4.11, 60.9],
    21: ["G", "NGC 1232", "Eridan", "9.9", "7.8x6.9'", "Galaxie NGC 1232", 3.16, -20.6],
    22: ["NP", "NGC 1535", "Eridan", "10.4", "18''", "Nébuleuse de l'Œil de Cléopâtre", 4.24, -12.7],
    23: ["NP", "NGC 1514", "Taureau", "10.8", "1'54''", "Crystal Ball Nebula", 4.15, 30.8],
    24: ["E/RN", "NGC 1931", "Cocher", "-", "3.0x3.0'", "Fly Nebula", 5.52, 34.2],
    25: ["RN", "NGC 1788", "Orion", "-", "8.0x5.0'", "Nébuleuse de la Tête de Renard", 5.13, -3.3],
    26: ["E/RN", "NGC 1973", "Orion", "-", "40x25'", "Nébuleuse Courante", 5.58, -4.7],
    27: ["NP", "NGC 2022", "Orion", "12.4", "18''", "Nébuleuse planétaire", 5.7, 9.1],
    28: ["EN", "NGC 2024", "Orion", "-", "30x30'", "Nébuleuse de la Flamme", 5.69, -1.9],
    29: ["OC", "NGC 2194", "Orion", "8.5", "10'", "Amas ouvert", 6.23, 12.8],
    30: ["NP", "NGC 2371", "Gémeaux", "13.0", "55''", "Nébuleuse de la Cacahuète", 7.43, 29.5],
    31: ["NP", "NGC 2392", "Gémeaux", "8.3", "13''", "Nébuleuse de l'Esquimau", 7.48, 20.9],
    32: ["EN", "NGC 2237", "Licorne", "-", "80x60'", "Nébuleuse de la Rosette", 6.54, 5.0],
    33: ["E/RN", "NGC 2261", "Licorne", "var", "2x1'", "Nébuleuse Variable de Hubble", 6.65, 8.7],
    34: ["EN", "NGC 2359", "Grand Chien", "-", "8.0x6.0'", "Nébuleuse du Casque de Thor", 7.31, -13.2],
    35: ["NP", "NGC 2440", "Poupe", "10.3", "14''", "Nébuleuse de l'Insecte", 7.69, -18.2],
    36: ["OC", "NGC 2539", "Poupe", "6.5", "22'", "Amas ouvert", 8.18, -12.8],
    37: ["G", "NGC 2403", "Girafe", "8.4", "17.8x11.0'", "Galaxie spirale", 7.62, 65.6],
    38: ["G", "NGC 2655", "Girafe", "10.1", "5.1x4.4'", "Galaxie lenticulaire", 8.9, 78.2],
    39: ["G", "NGC 2683", "Lynx", "9.7", "9.3x2.5'", "Galaxie de la Soucoupe volante", 8.88, 33.4],
    40: ["G", "NGC 2841", "Grande Ourse", "9.3", "8.1x3.8'", "Galaxie spirale", 9.37, 51.0],
    41: ["G", "NGC 3079", "Grande Ourse", "10.6", "7.6x1.7'", "Galaxie spirale", 10.03, 55.7],
    42: ["G", "NGC 3184", "Grande Ourse", "9.7", "6.9x6.8'", "Galaxie spirale", 10.3, 41.4],
    43: ["G", "NGC 3877", "Grande Ourse", "10.9", "5.4x1.5'", "Galaxie spirale", 11.77, 47.5],
    44: ["G", "NGC 3941", "Grande Ourse", "9.8", "3.8x2.5'", "Galaxie lenticulaire", 11.88, 45.0],
    45: ["G", "NGC 4026", "Grande Ourse", "10.7", "5.1x1.4'", "Galaxie lenticulaire", 11.99, 50.9],
    46: ["G", "NGC 4088", "Grande Ourse", "10.5", "5.8x2.5'", "Galaxie spirale", 12.1, 50.5],
    47: ["G", "NGC 4157", "Grande Ourse", "11.9", "6.9x1.7'", "Galaxie spirale", 12.2, 50.5],
    48: ["G", "NGC 4605", "Grande Ourse", "9.6", "5.5x2.3'", "Galaxie spirale", 12.67, 61.6],
    49: ["G", "NGC 3115", "Sextant", "9.2", "8.3x3.2'", "Galaxie du Fuseau", 10.09, -7.7],
    50: ["NP", "NGC 3242", "Hydre", "8.6", "16''", "Le Fantôme de Jupiter", 10.41, -18.6],
    51: ["G", "NGC 3003", "Petit Lion", "11.7", "5.9x1.7'", "Galaxie spirale", 9.81, 33.4],
    52: ["G", "NGC 3344", "Petit Lion", "9.9", "6.9x6.5'", "Galaxie du Petit Moulinet", 10.73, 25.0],
    53: ["G", "NGC 3432", "Petit Lion", "11.3", "6.2x1.5'", "Galaxie spirale", 10.91, 36.6],
    54: ["G", "NGC 2903", "Lion", "8.9", "12.6x6.6'", "Galaxie spirale", 9.54, 21.5],
    55: ["G", "NGC 3384", "Lion", "9.9", "5.9x2.6'", "Galaxie lenticulaire", 10.8, 12.6],
    56: ["G", "NGC 3521", "Lion", "8.7", "9.5x5.0'", "Galaxie spirale", 11.08, -0.0],
    57: ["G", "NGC 3607", "Lion", "10.0", "3.7x3.2'", "Galaxie elliptique", 11.28, 18.0],
    58: ["G", "NGC 3628", "Lion", "9.5", "14.8x3.6'", "Galaxie de l'Arête", 11.34, 13.6],
    59: ["G", "NGC 4111", "Chiens de Chasse", "10.8", "4.8x1.1'", "Galaxie lenticulaire", 12.12, 43.1],
    60: ["G", "NGC 4214", "Chiens de Chasse", "9.7", "7.9x6.3'", "Galaxie irrégulière", 12.26, 36.3],
    61: ["G", "NGC 4244", "Chiens de Chasse", "10.2", "16.2x2.5'", "Galaxie de la Lame d'Argent", 12.3, 37.8],
    62: ["G", "NGC 4449", "Chiens de Chasse", "9.4", "5.1x3.7'", "Galaxie irrégulière", 12.47, 44.1],
    63: ["G", "NGC 4490", "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxies des Cocons", 12.51, 41.6],
    64: ["G", "NGC 4631", "Chiens de Chasse", "9.3", "15.1x3.3'", "Galaxie de la Baleine", 12.7, 32.5],
    65: ["G", "NGC 4656", "Chiens de Chasse", "10.4", "13.8x3.3'", "La Crosse de Hockey", 12.71, 32.2],
    66: ["G", "NGC 5005", "Chiens de Chasse", "9.8", "5.9x3.1'", "Galaxie spirale", 13.18, 37.1],
    67: ["G", "NGC 5033", "Chiens de Chasse", "10.1", "10.5x5.6'", "Galaxie spirale", 13.22, 36.6],
    68: ["G", "NGC 4274", "Chevelure de Bérénice", "10.4", "6.9x2.8'", "Galaxie spirale", 12.33, 29.6],
    69: ["G", "NGC 4414", "Chevelure de Bérénice", "10.2", "3.6x2.2'", "Galaxie spirale", 12.44, 31.2],
    70: ["G", "NGC 4494", "Chevelure de Bérénice", "9.8", "4.8x3.8'", "Galaxie elliptique", 12.52, 25.8],
    71: ["G", "NGC 4559", "Chevelure de Bérénice", "9.8", "10.5x4.9'", "Galaxie spirale", 12.6, 28.0],
    72: ["G", "NGC 4565", "Chevelure de Bérénice", "9.6", "16.2x2.8'", "Galaxie de l'Aiguille", 12.6, 26.0],
    73: ["G", "NGC 4725", "Chevelure de Bérénice", "9.2", "11.0x7.9'", "Galaxie spirale", 12.84, 25.5],
    74: ["G", "NGC 4038", "Corbeau", "10.7", "~3x2'", "Galaxies des Antennes", 12.03, -18.9],
    75: ["NP", "NGC 4361", "Corbeau", "10.3", "45''", "Galaxie de l'Atome pour la Paix", 12.41, -18.8],
    76: ["G", "NGC 4216", "Vierge", "9.9", "8.3x2.2'", "Galaxie spirale", 12.26, 13.1],
    77: ["G", "NGC 4388", "Vierge", "11.0", "5.1x1.4'", "Galaxie spirale", 12.43, 12.7],
    78: ["G", "NGC 4438", "Vierge", "10.1", "9.3x3.9'", "Les Yeux", 12.46, 13.0],
    79: ["G", "NGC 4517", "Vierge", "10.5", "10.2x1.9'", "Galaxie spirale", 12.54, 0.1],
    80: ["G", "NGC 4526", "Vierge", "9.6", "7.6x2.3'", "Galaxie spirale", 12.57, 7.7],
    81: ["G", "NGC 4535", "Vierge", "9.8", "6.8x5.0'", "Galaxie spirale", 12.57, 8.2],
    82: ["G", "NGC 4567", "Vierge", "~11", "4.6x2.1'", "Les Jumeaux Siamois", 12.61, 11.3],
    83: ["G", "NGC 4699", "Vierge", "9.6", "3.5x2.7'", "Galaxie spirale", 12.81, -8.7],
    84: ["G", "NGC 4762", "Vierge", "10.2", "8.7x1.6'", "Galaxie de l'Équerre", 12.88, 11.2],
    85: ["G", "NGC 5746", "Vierge", "10.6", "7.9x1.7'", "Galaxie spirale", 14.75, 1.9],
    86: ["GC", "NGC 5466", "Bouvier", "9.1", "11.0'", "Amas globulaire", 14.09, 28.5],
    87: ["G", "NGC 5907", "Dragon", "10.4", "12.3x1.8'", "Galaxie de l'Éclat", 15.26, 56.3],
    88: ["G", "NGC 6503", "Dragon", "10.2", "6.2x2.3'", "Galaxie spirale", 17.81, 70.1],
    89: ["NP", "NGC 6543", "Dragon", "8.8", "18''", "Nébuleuse de l'Œil de Chat", 17.98, 66.6],
    90: ["NP", "NGC 6210", "Hercule", "9.3", "14''", "Nébuleuse de la Tortue", 16.74, 23.8],
    91: ["NP", "NGC 6369", "Ophiuchus", "10.4", "30''", "Nébuleuse du Petit Fantôme", 17.49, -17.8],
    92: ["NP", "NGC 6572", "Ophiuchus", "9.0", "8''", "Emerald Nebula", 18.2, 6.8],
    93: ["OC", "NGC 6633", "Ophiuchus", "4.6", "27'", "Amas de Tweedledum", 18.46, 6.5],
    94: ["GC", "NGC 6712", "Ecu de Sobieski", "8.2", "7.2'", "Amas globulaire", 18.89, -8.7],
    95: ["NP", "NGC 6781", "Aigle", "11.8", "1'49''", "Phantom Feather Nebula", 19.31, 6.5],
    96: ["OC", "NGC 6819", "Cygne", "7.3", "5'", "Amas de la Tête de Renard (Foxhead)", 19.69, 40.2],
    97: ["NP", "NGC 6826", "Cygne", "9.8", "30''", "Nébuleuse de l'Œil Clignotant", 19.75, 50.5],
    98: ["SNR", "NGC 6888", "Cygne", "-", "20x10'", "Nébuleuse du Croissant", 20.2, 38.4],
    "99a": ["SNR", "NGC 6960", "Cygne", "-", "70x6'", "Petite Dentelle du Cygne", 20.76, 30.7],
    "99b": ["SNR", "NGC 6992", "Cygne", "-", "78x8'", "Grande Dentelle du Cygne", 20.94, 31.7],
    100: ["EN", "NGC 7000", "Cygne", "-", "120x100'", "Nébuleuse de l'Amérique du Nord", 20.99, 44.3],
    101: ["NP", "NGC 7027", "Cygne", "10.4", "15''", "Nébuleuse planétaire", 21.12, 42.2],
    102: ["NP", "NGC 6445", "Sagittaire", "11.8", "34''", "Little Gem Nebula", 17.82, -16.2],
    103: ["OC", "NGC 6520", "Sagittaire", "8.1", "6'", "Amas ouvert", 18.06, -27.9],
    104: ["NP", "NGC 6818", "Sagittaire", "9.9", "17''", "Little Gem Nebula", 19.73, -16.2],
    105: ["OC", "NGC 6802", "Petit Renard", "8.8", "3.2'", "Amas ouvert", 19.51, 20.3],
    106: ["OC", "NGC 6940", "Petit Renard", "6.3", "31'", "Amas ouvert", 20.58, 28.3],
    107: ["OC", "NGC 6939", "Céphée", "7.8", "8'", "Amas ouvert", 20.57, 60.6],
    108: ["G", "NGC 6946", "Céphée", "8.9", "11.0x9.8'", "Galaxie du Feu d'Artifice", 20.58, 60.1],
    109: ["RN", "NGC 7129", "Céphée", "-", "8x7'", "Nébuleuse par réflexion", 21.72, 66.1],
    110: ["NP", "NGC 40", "Céphée", "10.2", "37''", "Nébuleuse du Nœud Coulant", 0.05, 72.5]
}

O_MEARA_DATA = {
    # hidden treasures
    1: ["OC", "NGC 189", "Cassiopée", "8.8", "5'", "NGC 189", 0.38, 61.1],
    2: ["OC", "Amas du Voilier", "Cassiopée", "7.0", "15'", "Amas du Voilier", 0.73, 61.8],
    3: ["N", "NGC 281", "Cassiopée", "7.8", "30'x35'", "Nébuleuse Pacman", 0.87, 56.6],
    4: ["GC", "NGC 288", "Sculpteur", "8.1", "13'", "NGC 288", 0.88, -26.6],
    5: ["G", "NGC 404", "Andromède", "10.0", "3.5'", "Galaxie de la Perle Perdue", 1.16, 35.7],
    6: ["G", "NGC 584", "Céto", "10.5", "4'x2'", "Galaxie du Petit Fuseau", 1.52, -6.9],
    7: ["OC", "NGC 659", "Cassiopée", "7.9", "6'", "Amas Ying Yang", 1.77, 60.7],
    8: ["G", "NGC 772", "Bélier", "10.3", "7'x4'", "Galaxie Fiddlehead", 1.99, 19.0],
    9: ["G", "NGC 908", "Céto", "10.2", "6'x3'", "NGC 908", 2.38, -21.2],
    10: ["G", "NGC 1023", "Persée", "9.5", "7'x3'", "Galaxie Lenticulaire de Persée", 2.67, 39.1],
    11: ["G", "NGC 1232", "Éridan", "9.8", "7'x7'", "Galaxie de l'Œil de Dieu", 3.16, -20.6],
    12: ["G", "NGC 1291", "Éridan", "8.5", "11'x10'", "Galaxie au Col de Neige", 3.29, -41.1],
    13: ["G", "NGC 1316", "Fourneau", "9.4", "12'x9'", "Fornax A", 3.38, -37.2],
    14: ["OC", "Alpha Per", "Persée", "1.2", "185'", "Amas d'Alpha Persei", 3.40, 49.0],
    15: ["N", "NGC 1333", "Persée", "5.7", "3'", "nuage de Persée (NGC 1333)", 3.48, 31.4],
    16: ["NP", "NGC 1360", "Fourneau", "9.4", "6'", "Nébuleuse de l'Embryon", 3.55, -25.9],
    17: ["G", "NGC 1365", "Fourneau", "9.5", "11'x6'", "NGC 1365", 3.56, -36.1],
    18: ["G", "NGC 1399", "Fourneau", "9.4", "7'x7'", "NGC 1399", 3.64, -35.4],
    19: ["G", "NGC 1398", "Fourneau", "9.5", "8'x5'", "NGC 1398", 3.65, -26.3],
    20: ["G", "NGC 1404", "Fourneau", "10.0", "3'x3'", "NGC 1404", 3.65, -35.6],
    21: ["A", "Kemble 1", "Girafe", "5.0", "150'", "Cascade de Kemble", 3.96, 63.0],
    22: ["NP", "NGC 1501", "Girafe", "11.5", "0.9'", "Nébuleuse de l'Huître", 4.11, 61.0],
    23: ["OC", "NGC 1502", "Girafe", "6.0", "20'", "Amas du Jolly Roger", 4.13, 62.3],
    24: ["NP", "NGC 1535", "Éridan", "9.6", "0.9'", "Œil de Cléopâtre", 4.24, -12.7],
    25: ["OC", "NGC 1528", "Persée", "6.4", "18'", "Amas m & m", 4.25, 51.2],
    26: ["OC", "NGC 1545", "Persée", "6.2", "12'", "Amas m & m", 4.30, 50.3],
    27: ["OC", "NGC 1647", "Taureau", "6.4", "40'", "Amas de la Lune Pirate", 4.77, 19.1],
    28: ["NP", "IC 418", "Lièvre", "9.6", "0.5'", "Nébuleuse de la Framboise", 5.10, -12.7],
    29: ["OC", "Cr 69", "Orion", "5.0", "50'", "Amas de Lambda Orionis", 5.58, 9.9],
    30: ["OC", "NGC 1981", "Orion", "4.2", "28'", "Amas du Wagon de Charbon", 5.59, -4.4],
    31: ["OC", "NGC 1980", "Orion", "5.0", "30'", "Le Joyau Perdu d'Orion", 5.59, -4.9],
    32: ["N", "NGC 1977", "Orion", "6.3", "20'", "Nébuleuse de l'Homme qui Court", 5.59, -4.8],
    33: ["N", "NGC 1999", "Orion", "9.5", "2'", "Nébuleuse du Tampon en Caoutchouc", 5.61, -6.7],
    34: ["N", "NGC 2024", "Orion", "7.2", "30'", "Nébuleuse de la Flamme", 5.69, 1.9],
    35: ["N", "NGC 2163", "Orion", "10.0", "3'", "NGC 2163", 6.25, 18.7],
    36: ["OC", "NGC 2169", "Orion", "5.9", "6'", "Amas des Petites Pléiades", 6.36, 14.0],
    37: ["N", "NGC 2175", "Orion", "6.9", "18'", "NGC 2175", 6.38, 20.5],
    38: ["OC", "NGC 2264", "Licorne", "4.1", "40'", "Amas de l'Arbre de Noël", 6.68, 9.9],
    39: ["OC", "NGC 2301", "Licorne", "6.0", "15'", "Le Dragon d'Hagrid", 6.86, 0.5],
    40: ["OC", "NGC 2353", "Licorne", "7.1", "18'", "Avery's Island", 7.24, -10.3],
    41: ["NP", "NGC 2440", "Poupe", "9.4", "1.3'", "Nébuleuse du Papillon Albinos", 7.70, -18.2],
    42: ["OC", "NGC 2451", "Poupe", "2.8", "50'", "Amas du Scorpion Piquant", 7.75, -38.0],
    43: ["N", "NGC 2467", "Poupe", "7.1", "15'", "NGC 2467", 7.87, -26.4],
    44: ["OC", "NGC 2547", "Voiles", "4.7", "25'", "Amas de la Boucle d'Oreille d'Or", 8.17, -49.2],
    45: ["OC", "NGC 2539", "Poupe", "6.5", "15'", "Amas de l'Assiette", 8.18, -12.8],
    46: ["OC", "NGC 2546", "Poupe", "6.3", "70'", "Amas du Cœur et de la Dague", 8.20, -37.6],
    47: ["G", "NGC 2683", "Lynx", "9.7", "9'x2'", "Galaxie de l'OVNI", 8.88, 33.4],
    48: ["G", "NGC 2655", "Girafe", "10.1", "5'x4'", "NGC 2655", 8.93, 78.2],
    49: ["G", "NGC 2841", "Grande Ourse", "9.3", "8'x4'", "Galaxie de l'Œil de Tigre", 9.55, 51.0],
    50: ["OC", "IC 2488", "Voiles", "7.0", "15'", "Amas du Collier de Perles", 9.77, -57.0],
    51: ["G", "NGC 2903", "Lion", "8.8", "13'x6'", "NGC 2903", 9.53, 21.5],
    52: ["G", "NGC 3184", "Grande Ourse", "9.6", "7'x7'", "Petite Galaxie du Moulinet", 10.30, 41.4],
    53: ["OC", "NGC 3228", "Voiles", "6.0", "5'", "Amas du Trésor de la Reine", 10.36, -51.7],
    54: ["OC", "NGC 3293", "Carène", "4.7", "5'", "Petite Boîte à Bijoux", 10.58, -58.2],
    55: ["G", "NGC 3344", "Petit Lion", "9.7", "7'x7'", "NGC 3344", 10.73, 24.9],
    56: ["G", "NGC 3521", "Lion", "9.2", "11'x5'", "NGC 3521", 11.09, 0.0],
    57: ["G", "NGC 3621", "Hydre", "9.4", "12'x7'", "Galaxie Cadre", 11.31, -32.8],
    58: ["G", "NGC 3628", "Lion", "9.6", "13'x3'", "Galaxie du Fantôme du Roi Hamlet", 11.34, 13.6],
    59: ["G", "NGC 4214", "Chiens de Chasse", "9.6", "8'x7'", "NGC 4214", 12.26, 36.3],
    60: ["G", "NGC 4216", "Vierge", "10.3", "8'x2'", "Galaxie Silver Streak", 12.26, 13.1],
    61: ["NP", "NGC 4361", "Corbeau", "10.9", "2.1'", "NGC 4361", 12.41, -18.8],
    62: ["OC", "Mel 111", "Chevelure de Bérénice", "1.8", "300'", "Amas de Coma", 12.42, 25.9],
    63: ["G", "NGC 4490", "Chiens de Chasse", "9.5", "6'x3'", "Galaxie du Cocon", 12.51, 41.6],
    64: ["NP", "IC 3568", "Girafe", "10.6", "0.3'", "Nébuleuse du Citron Vert", 12.55, 82.6],
    65: ["G", "NGC 4526", "Vierge", "9.6", "7'x3'", "Galaxie du Sourcil Poilu", 12.57, 7.7],
    66: ["G", "NGC 4605", "Grande Ourse", "10.1", "6'x2'", "Galaxie de l'Œuf de Fabergé", 12.69, 61.6],
    67: ["G", "NGC 4656", "Chiens de Chasse", "10.1", "15'x2'", "Galaxie du Crochet", 12.71, 32.2],
    68: ["G", "NGC 4699", "Vierge", "9.6", "4'x3'", "NGC 4699", 12.82, -8.7],
    69: ["G", "NGC 4725", "Chevelure de Bérénice", "9.3", "11'x8'", "NGC 4725", 12.84, 25.5],
    70: ["G", "NGC 5102", "Centaure", "9.5", "9'x3'", "Le Fantôme d'Iota", 13.36, -36.6],
    71: ["OC", "NGC 5281", "Centaure", "5.9", "8'", "Amas du Petit Scorpion", 13.80, -62.9],
    72: ["G", "NGC 5363", "Vierge", "10.5", "4'x3'", "NGC 5363", 13.94, 5.3],
    73: ["OC", "NGC 5662", "Centaure", "5.5", "30'", "NGC 5662", 14.59, -56.7],
    74: ["G", "NGC 5746", "Vierge", "10.5", "7'x1'", "Galaxie de la Lame et la Perle", 14.75, 2.0],
    75: ["G", "NGC 5866", "Dragon", "9.9", "7'x3'", "Galaxie de l'Or des Fous", 15.11, 55.8],
    76: ["GC", "NGC 5897", "Balance", "8.4", "11'", "Amas Globulaire Fantôme", 15.30, -21.0],
    77: ["GC", "NGC 5986", "Loup", "7.6", "10'", "NGC 5986", 15.77, -37.8],
    78: ["NP", "NGC 6210", "Hercule", "8.8", "0.4'", "Nébuleuse de la Tortue", 16.74, 23.8],
    79: ["OC", "NGC 6242", "Scorpion", "6.4", "9'", "NGC 6242", 16.92, -39.5],
    80: ["OC", "NGC 6281", "Scorpion", "5.4", "8'", "Amas de l'Aile de Papillon de Nuit", 17.01, -37.9],
    81: ["NP", "NGC 6369", "Ophiuchus", "11.4", "0.6'", "Nébuleuse du Petit Fantôme", 17.49, -23.8],
    82: ["OC", "NGC 6400", "Scorpion", "8.8", "12'", "Amas Fantôme", 17.67, -37.0],
    83: ["OC", "NGC 4665", "Ophiuchus", "8.3", "45'", "La Ruche d'Été", 17.66, 5.7],
    84: ["NP", "NGC 6445", "Sagittaire", "11.2", "0.7'", "Nébuleuse de la Boîte", 17.82, -20.0],
    85: ["G", "NGC 6503", "Dragon", "10.2", "7'x3'", "Galaxie Perdue dans l'Space", 17.82, 70.1],
    86: ["GC", "NGC 6441", "Scorpion", "7.2", "10'", "Amas de la Pépite d'Argent", 17.83, -37.1],
    87: ["D", "Barnard", "Ophiuchus", "9.5", "n/a", "Étoile de Barnard", 17.96, 4.7],
    88: ["OC", "NGC 6520", "Sagittaire", "7.6", "5'", "Le Coffre du Mort", 18.06, -27.9],
    89: ["GC", "NGC 6544", "Sagittaire", "7.5", "9'", "Amas de l'Étoile de Mer", 18.12, -25.0],
    90: ["NP", "NGC 6572", "Ophiuchus", "8.1", "0.3'", "Nébuleuse de l'Œil d'Émeraude", 18.20, 6.9],
    91: ["GC", "NGC 6624", "Sagittaire", "7.6", "9'", "NGC 6624", 18.39, -30.4],
    92: ["OC", "NGC 6633", "Ophiuchus", "4.6", "20'", "Amas de Tweedledum", 18.46, 6.5],
    93: ["OC", "IC 4756", "Serpent", "5.0", "52'", "Amas de Graff", 18.65, 5.4],
    94: ["OC", "NGC 6709", "Aigle", "6.7", "15'", "Amas de la Licorne Volante", 18.86, 10.3],
    95: ["GC", "NGC 6712", "Écu", "8.1", "10'", "NGC 6712", 18.88, -8.7],
    96: ["GC", "NGC 6723", "Sagittaire", "6.8", "13'", "NGC 6723", 18.99, -36.6],
    97: ["A", "Cr 399", "Petit Renard", "3.6", "60'", "Le Cintre", 19.42, 20.2],
    98: ["OC", "NGC 6819", "Cygne", "7.3", "5'", "Amas de la Tête de Renard", 19.69, 40.2],
    99: ["NP", "NGC 6818", "Sagittaire", "9.3", "0.8'", "Nébuleuse du Petit Joyau", 19.73, -14.2],
    100: ["OC", "NGC 6866", "Cygne", "7.6", "7'", "Amas de la Frégate Pirate", 20.06, 44.2],
    101: ["OC", "NGC 6940", "Petit Renard", "6.3", "25'", "Amas de Mothra", 20.58, 28.3],
    102: ["N", "LDN 906", "Cygne", "n/a", "480'", "Sac à Charbon du Nord", 20.62, 41.0],
    103: ["NP", "NGC 7008", "Cygne", "10.7", "1.4'", "Nébuleuse du Bouton de Manteau", 21.01, 54.5],
    104: ["NP", "NGC 7027", "Cygne", "8.5", "0.3'", "NGC 7027", 21.12, 42.2],
    105: ["N+C", "IC 1396", "Céphée", "3.5", "154'", "Amas de l'Éléphant / Trèfle", 21.65, 57.8],
    106: ["OC", "NGC 7380", "Céphée", "7.2", "20'", "Vif d'Or de Harry Potter", 22.78, 58.1],
    107: ["A", "Asterism", "Poissons", "8.0", "12'", "Petite Louche", 23.82, 8.0],
    108: ["OC", "NGC 7789", "Cassiopée", "6.7", "25'", "Amas de la Rose Rose (O'Meara)", 23.95, 56.7],
    109: ["G", "NGC 7793", "Sculpteur", "9.0", "9'", "Galaxie de Bond", 23.98, -32.6],
    # secret deep
    1001: ["RN", "vdB 1", "Cassiopée", "10.1", "8.6'", "vdB 1", 0.18, 58.7],
    1002: ["G", "NGC 134", "Sculpteur", "10.4", "8.1'", "Galaxie du Calmar Géant", 0.50, -33.2],
    1003: ["G", "NGC 488", "Poissons", "10.4", "5.2'", "Galaxie du Tourbillon", 1.39, 5.2],
    1004: ["OC", "NGC 654", "Cassiopée", "7.9", "40'", "Amas ouvert avec nébulosité", 1.74, 61.8],
    1005: ["OC", "Collinder 463", "Cassiopée", "9.1", "57'", "Lund 57 / Loch Ness monster", 1.89, 71.9],
    1006: ["OC", "Stock 2", "Cassiopée", "4.4", "130'", "Strong Man Cluster", 2.25, 59.4],
    1007: ["G", "NGC 936", "Céto", "10.1", "5.2'", "Galaxie de la Soucoupe", 2.46, -1.1],
    1008: ["G", "NGC 1084", "Éridan", "10.6", "2.9'", "Galaxie de la Truffe", 2.77, -7.5],
    1009: ["OC", "NGC 1245", "Persée", "7.6", "10'", "Amas de l'Étoile de Mer", 3.24, 47.2],
    1010: ["G", "NGC 1300", "Éridan", "10.4", "6.5'", "Galaxie spirale barrée", 3.33, -19.4],
    1011: ["OC", "NGC 1342", "Persée", "8.1", "30'", "Amas de la Raie / Petit Scorpion", 3.53, 37.3],
    1012: ["N", "Barnard 33", "Orion", "10.0", "90'", "La Tête de Cheval (dans Barnard's Loop)", 5.68, 0.7],
    1013: ["G", "NGC 1400", "Éridan", "10.8", "1.9'", "Galaxie avec NGC 1407", 3.66, -18.6],
    1014: ["G", "NGC 1407", "Éridan", "9.7", "2.5'", "Galaxie avec NGC 1400", 3.67, -18.5],
    1015: ["EN", "NGC 1491", "Persée", "10.0", "12'", "Nébuleuse de l'Empreinte Fossile", 4.05, 51.3],
    1016: ["NP", "NGC 1514", "Taureau", "10.0", "2'", "Nébuleuse de la Boule de Cristal", 4.15, 30.7],
    1017: ["EN", "NGC 1579", "Persée", "10.0", "12'", "Trifide du Nord", 4.51, 35.2],
    1018: ["OC", "NGC 1750", "Taureau", "7.0", "60'", "Amas ouvert", 5.06, 23.6],
    1019: ["OC", "NGC 1758", "Taureau", "7.0", "90'", "Amas ouvert", 5.07, 23.7],
    1020: ["EN", "NGC 1788", "Orion", "10.0", "8'", "Chauve-Souris Cosmique / Foxface", 5.13, -3.3],
    1021: ["OC", "NGC 1807", "Taureau", "7.0", "17'", "Amas ouvert", 5.20, 16.5],
    1022: ["OC", "NGC 1817", "Taureau", "7.7", "16'", "Amas ouvert", 5.21, 16.6],
    1023: ["EN", "IC 417", "Cocher", "10.0", "13'", "Nébuleuse de l'Araignée", 5.47, 34.4],
    1024: ["OC", "NGC 1931", "Cocher", "8.3", "3'", "La Mouche (avec IC 417)", 5.52, 34.2],
    1025: ["OC", "Collinder 70", "Orion", "0.4", "150'", "Ceinture d'Orion", 5.60, -1.0],
    1026: ["NP", "NGC 2022", "Orion", "11.6", "0.5'", "Nébuleuse des Baisers", 5.70, 9.1],
    1027: ["NP", "IC 2149", "Cocher", "11.5", "0.25'", "Nébuleuse planétaire", 5.91, 46.1],
    1028: ["EN", "NGC 2149", "Licorne", "10.0", "3'", "Nébuleuse par émission", 6.13, -9.7],
    1029: ["RN", "NGC 2170", "Licorne", "10.0", "110'", "Nébuleuse de l'Ange", 6.13, -6.3],
    1030: ["OC", "NGC 2281", "Cocher", "7.2", "15'", "Amas du Cœur Brisé", 6.81, 41.1],
    1031: ["GC", "NGC 2298", "Poupe", "7.3", "6.8'", "Amas Globulaire de la Poupe", 6.81, -36.0],
    1032: ["EN", "NGC 2316", "Licorne", "10.0", "4'", "Nébuleuse par émission", 7.02, -7.7],
    1033: ["OC", "NGC 2343", "Licorne", "5.5", "7'", "Amas ouvert", 7.14, -10.6],
    1034: ["NP", "NGC 2346", "Licorne", "10.3", "2'", "Nébuleuse du Papillon", 7.15, -0.8],
    1035: ["EN", "NGC 2359", "Grand Chien", "10.0", "10'", "Casque de Thor / Canard", 7.31, -13.2],
    1036: ["NP", "NGC 2371", "Gémeaux", "9.1", "2.1'", "Nébuleuse de la Double Bulle", 7.43, 29.4],
    1037: ["OC", "NGC 2420", "Gémeaux", "9.1", "10'", "Amas de la Comète Scintillante", 7.64, 21.5],
    1038: ["G", "NGC 3079", "Grande Ourse", "10.1", "7.6'", "Galaxie du Frisbee Fantôme", 10.03, 55.6],
    1039: ["G", "NGC 3077", "Grande Ourse", "10.0", "4.6'", "Galaxie irrégulière", 10.06, 68.7],
    1040: ["G", "NGC 3166", "Sextant", "10.5", "30'", "Galaxie Impétueuse", 10.27, 3.4],
    1041: ["G", "NGC 3169", "Sextant", "10.3", "4.8'", "Galaxie spirale", 10.27, 3.4],
    1042: ["G", "NGC 3198", "Grande Ourse", "10.7", "8.3'", "Galaxie spirale", 10.33, 45.5],
    1043: ["G", "NGC 3226", "Lion", "10.3", "2.8'", "Arp 94 (avec NGC 3227)", 10.40, 19.8],
    1044: ["G", "NGC 3227", "Lion", "10.3", "5.6'", "Arp 94 (avec NGC 3226)", 10.40, 19.8],
    1045: ["G", "NGC 3432", "Petit Lion", "10.5", "6.2'", "Arp 206 / Aiguille à tricoter", 10.87, 36.6],
    1046: ["G", "NGC 3675", "Grande Ourse", "10.1", "5.9'", "Galaxie spirale", 11.44, 43.5],
    1047: ["G", "NGC 3893", "Grande Ourse", "10.6", "4.4'", "Galaxie spirale", 11.81, 48.7],
    1048: ["G", "NGC 3953", "Grande Ourse", "10.3", "6.6'", "Galaxie spirale", 11.91, 52.3],
    1049: ["G", "NGC 4036", "Grande Ourse", "10.5", "4.5'", "Galaxie avec NGC 4041", 12.04, 61.9],
    1050: ["G", "NGC 4051", "Grande Ourse", "10.1", "5'", "Galaxie spirale", 12.05, 44.5],
    1051: ["G", "NGC 4111", "Chiens de Chasse", "10.7", "4.8'", "Galaxie spirale", 12.12, 43.0],
    1052: ["GC", "NGC 4147", "Chevelure de Bérénice", "10.3", "4'", "Amas Kick the Can", 12.17, 18.5],
    1053: ["G", "NGC 4293", "Chevelure de Bérénice", "10.1", "6'", "Galaxie de l'Oeil Noir", 12.36, 18.3],
    1054: ["G", "NGC 4414", "Chevelure de Bérénice", "10.3", "3.6'", "Galaxie en troupeau", 12.44, 31.2],
    1055: ["G", "NGC 4435", "Vierge", "11.0", "3'", "Arp 120 (les yeux avec NGC 4438)", 12.46, 13.0],
    1056: ["G", "NGC 4438", "Vierge", "10.1", "9.3'", "Les Yeux (Arp 120)", 12.46, 13.0],
    1057: ["G", "NGC 4450", "Chevelure de Bérénice", "10.1", "4.8'", "Galaxie spirale", 12.48, 17.0],
    1058: ["G", "NGC 4461", "Vierge", "10.3", "3.7'", "Galaxie proche des Yeux", 12.49, 13.1],
    1059: ["QSR", "3C 273", "Vierge", "11.7-13.2", "-", "Quasar", 12.49, 2.05],
    1060: ["G", "NGC 4473", "Chevelure de Bérénice", "10.2", "3.7' x 2.4'", "Galaxie elliptique / Part of Pair", 12.50, 13.4],
    1061: ["G", "NGC 4477", "Chevelure de Bérénice", "10.4", "3.9' x 3.6'", "Galaxie spirale / Part of Pair", 12.50, 13.6],
    1062: ["G", "NGC 4636", "Vierge", "9.5", "7.1' x 5.2'", "Galaxie elliptique", 12.71, 2.6],
    1063: ["G", "NGC 4665", "Vierge", "10.5", "4.1' x 4.1'", "Galaxie spirale", 12.75, 3.0],
    1064: ["G", "NGC 4753", "Vierge", "9.9", "4.1' x 2.3'", "Galaxie lenticulaire / Dust Devil", 12.87, -1.2],
    1065: ["G", "NGC 4762", "Vierge", "10.1", "9.1' x 2.2'", "Galaxie avec NGC 4754 / Paper-Kite", 12.88, 11.2],
    1066: ["G", "NGC 5033", "Chiens de Chasse", "10.2", "10.5' x 5.1'", "Galaxie spirale / Waterbug", 13.22, 36.5],
    1067: ["G", "NGC 5195", "Chiens de Chasse", "9.6", "6.4' x 4.6'", "Compagne de M51 (Arp 85)", 13.50, 47.25],
    1068: ["GC", "NGC 5466", "Bouvier", "9.0", "9'", "Amas Globulaire Fantôme / Snowglobe", 14.09, 28.5],
    1069: ["G", "NGC 5846", "Vierge", "10.0", "3.0' x 3.0'", "Galaxie spirale", 15.10, 1.6],
    1070: ["G", "NGC 5907", "Dragon", "10.3", "11.5' x 1.7'", "Galaxie de l'Éclat / Splinter", 15.27, 56.3],
    1071: ["NP", "IC 4593", "Hercule", "10.7", ">12\"", "Nébuleuse du Petit Pois / White-Eyed Pea", 16.20, 12.07],
    1072: ["GC", "NGC 6144", "Scorpion", "9.0", "9'", "Amas Globulaire", 16.45, -26.02],
    1073: ["G", "NGC 6207", "Hercule", "11.6", "3.0' x 1.1'", "Galaxie proche de M13", 16.72, 36.83],
    1074: ["GC", "NGC 6229", "Hercule", "9.4", "4.5'", "Amas Globulaire d'Hercule / \"Prize Comet\"", 16.78, 47.53],
    1075: ["GC", "NGC 6293", "Ophiuchus", "8.2", "7.9'", "Amas Globulaire", 17.17, -26.58],
    1076: ["NP", "NGC 6309", "Ophiuchus", "11.5", ">16\"", "Nébuleuse de la Boîte / Box", 17.24, -12.92],
    1077: ["GC", "NGC 6356", "Ophiuchus", "8.2", "10'", "Amas Globulaire", 17.39, -17.82],
    1078: ["GC", "NGC 6522", "Sagittaire", "8.3", "9.4'", "Fenêtre de Baade", 18.06, -30.03],
    1079: ["GC", "NGC 6528", "Sagittaire", "9.6", "3.7'", "Amas Globulaire", 18.08, -30.05],
    1080: ["NP", "NGC 6563", "Sagittaire", "11.0", "50\" x 38\"", "Anneau Austral / Southern Ring", 18.20, -33.87],
    1081: ["RN", "NGC 6589", "Sagittaire", "10.0", "5' x 3'", "Nébuleuse par réflexion", 18.28, -19.78],
    1082: ["RN", "NGC 6595", "Sagittaire", "10.0", "4' x 3'", "Nébuleuse par réflexion / = NGC 6590", 18.29, -19.87],
    1083: ["GC", "NGC 6638", "Sagittaire", "9.2", "7.3'", "Amas Globulaire", 18.52, -25.50],
    1084: ["OC", "NGC 6664", "Écu de Sobieski", "7.8", "12'", "Amas du Traîneau / Santa's Sleigh", 18.61, -8.18],
    1085: ["GC", "NGC 6717", "Sagittaire", "8.4", "5.4'", "Amas Globulaire (Palomar 9)", 18.92, -22.70],
    1086: ["NP", "NGC 6751", "Aigle", "11.9", "24\"", "Nébuleuse de la Fleur de Pissenlit / Glowing Eye", 19.10, -5.99],
    1087: ["OC", "NGC 6755", "Aigle", "7.5", "15'", "Amas avec NGC 6756 / Part of Binary Cluster?", 19.12, 4.27],
    1088: ["OC", "NGC 6756", "Aigle", "10.6", "4'", "Amas avec NGC 6755 / Part of Binary Cluster?", 19.15, 4.70],
    1089: ["NP", "NGC 6778", "Aigle", "11.9", "20\" x 40\"", "Mini Dumbbell / Son of M76", 19.31, -1.60],
    1090: ["NP", "NGC 6781", "Aigle", "11.4", "2'", "Nébuleuse de la Boule de Neige / Ghost of the Moon", 19.31, 6.53],
    1091: ["NP", "NGC 6804", "Aigle", "12.2", "~50\"", "Nébuleuse du Rétrécissement / Incredible Shrinking", 19.53, 9.22],
    1092: ["OC", "NGC 6811", "Cygne", "6.8", "15'", "Smoke Ring / Hole in a Cluster", 19.62, 46.38],
    1093: ["A", "Cygnus Kite Asterism", "Cygne", "8.8 (star)", "-", "Astérisme du Cerf-Volant / HDE 226868", 19.97, 35.20],
    1094: ["A", "OME 3", "Cygne", "-", "12'", "Alessi J20053+4732", 20.09, 47.53],
    1095: ["NP", "NGC 6891", "Dauphin", "10.5", ">18\"", "Nébuleuse planétaire", 20.25, 12.70],
    1096: ["NP", "NGC 6894", "Cygne", "12.3", ">42\"", "Petite Nébuleuse de l'Anneau / Diamond Ring", 20.27, 30.57],
    1097: ["EN", "IC 1318(a)", "Cygne", "-", "45' x 20'", "Nébuleuse Gamma Cygni / Near Gamma Cygni", 20.28, 41.82],
    1098: ["NP", "NGC 6905", "Dauphin", "11.1", "42\" x 35\"", "Nébuleuse de l'Éclair Bleu / Blue Flash", 20.37, 20.10],
    1099: ["OC", "NGC 6910", "Cygne", "6.6", "10'", "Amas de l'Arpenteur (Inchworm)", 20.39, 40.78],
    1100: ["OC", "NGC 6939", "Céphée", "7.8", "10'", "Astérisme de l'Oie en vol / Flying Geese", 20.53, 60.67],
    1101: ["NP", "NGC 7026", "Cygne", "10.9", "21\"", "Nébuleuse du Cheeseburger / Cheeseburger", 21.11, 47.85],
    1102: ["NP", "NGC 7048", "Cygne", "12.1", "61\"", "Nébuleuse du Disque Fantôme / Peek-a-Boo", 21.24, 46.28],
    1103: ["RN", "NGC 7129", "Céphée", "-", "7' x 7'", "Rose Cosmique / Cosmic Rosebud", 21.71, 66.10],
    1104: ["OC", "NGC 7160", "Céphée", "6.1", "5'", "Alligator Nageur / Bruce Lee", 21.90, 62.60],
    1105: ["OC", "NGC 7209", "Lézard", "7.7", "15'", "Amas ouvert / Star Lizard", 22.10, 46.48],
    1106: ["NP", "NGC 7354", "Céphée", "12.2", "22\" x 18\"", "Nébuleuse planétaire", 22.67, 61.28],
    1107: ["OC", "NGC 7510", "Céphée", "7.9", "7'", "Amas du Loir (Dormouse)", 23.19, 60.57],
    1108: ["EN", "NGC 7538", "Céphée", "-", "9' x 6'", "Nébuleuse de la Lagune Nord / Northern Lagoon", 23.23, 61.52],
    1109: ["OC", "NGC 7790", "Cassiopée", "8.5", "5'", "Widow's Web", 23.97, 61.21],
}

try:
    # Si le fichier 'LANG_database.py' existe à côté, on charge ses données
    from LANG_database import LANG, MESSIER_DATA, CALDWELL_DATA, RASC_DATA, O_MEARA_DATA
except ImportError:
    # Si le fichier n'existe pas, Python ignore l'erreur et garde les données FR ci-dessus
    pass

CATALOGS = {
    "Messier": {"prefix": "M", "data": MESSIER_DATA},          # the prefix is used in the HTML page
    "Caldwell": {"prefix": "C", "data": CALDWELL_DATA},
    "RASC": {"prefix": "R", "data": RASC_DATA},
    "O'Meara": {"prefix": "X", "data": O_MEARA_DATA}
}

TODO_FILE = "TODO.txt" # format is {"Catalog name": {"IdObjet": "free Comment"}}


# --- SCRIPT ---


def compute_best_season(ra):
    """Calculates the best observation season based on Right Ascension (RA)"""
    if 3 <= ra < 9:
        return LANG["SEASONS"]["H"] # Hiver
    elif 9 <= ra < 15:
        return LANG["SEASONS"]["P"] # Printemps
    elif 15 <= ra < 21:
        return LANG["SEASONS"]["E"] # Été
    else:
        return LANG["SEASONS"]["A"] # Automne

def find_image(prefix, obj_id, tech_ref):
    """Search for a matching image in the source directory based on technical references or IDs"""
    valid_exts = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.lnk')
    if not os.path.exists(CONFIG["SOURCE_DIR"]): return None
    
    # Pre-filter files with valid extensions and exclude thumbnails
    files = [f for f in os.listdir(CONFIG["SOURCE_DIR"]) 
             if f.lower().endswith(valid_exts) and "_thumb" not in f]

    if tech_ref:
        # Search by technical designation (e.g., NGC 7000, IC 434)
        match = re.search(r"(NGC|IC|SH2|Mel|WNC|M|Barnard|vdB)\s?(\d+)", tech_ref, re.IGNORECASE)
        if match:
            a_type, a_num = match.group(1), match.group(2)
            pattern = rf"{a_type}[_ \-\s]?{a_num}(?!\d)"
            for filename in files:
                if re.search(pattern, filename, re.IGNORECASE):
                    return filename

    # Fallback search: match using catalog prefix + object ID
    pattern_id = rf"(^|[_ \-\.]){prefix}[_ \-\s]?{obj_id}(?!\d)"
    for filename in files:
        if re.search(pattern_id, filename, re.IGNORECASE):
            return filename
                
    return None
    
def get_exif_date(path):
    """Extract capture date from EXIF or fallback to file modification date"""
    try:
        with Image.open(path) as img:
            exif = img._getexif()
            if exif and 306 in exif:
                return datetime.strptime(exif[306], "%Y:%m:%d %H:%M:%S").strftime("%d/%m/%Y %H:%M")
    except: pass
    return datetime.fromtimestamp(os.path.getmtime(path)).strftime("%d/%m/%Y %H:%M")

def make_thumbnail(src):
    """
    CRITICAL ZONE: Dynamic processing of source assets & automated TIF conversions.
    Browsers cannot natively render astronomical high-fidelity TIF/TIFF master files.
    When a .tif/tiff file is detected, this block compresses and downscales it into 
    a 'view_*.jpg' proxy image targeted for standard HTML display. 
    It also yields the square grid thumbnail for the interface layout.
    """
    if not os.path.exists(CONFIG["THUMB_DIR"]): os.makedirs(CONFIG["THUMB_DIR"])
    dest = os.path.join(CONFIG["THUMB_DIR"], f"thumb_{src}")
    
    # Check for TIF/TIFF formats to generate a web-friendly compressed preview proxy
    if src.lower().endswith(('.tif', '.tiff')):
        view_dest = os.path.join(CONFIG["THUMB_DIR"], f"view_{os.path.splitext(src)[0]}.jpg")
        if not os.path.exists(view_dest):
            try:
                with Image.open(src) as img_view:
                    img_view = ImageOps.exif_transpose(img_view).convert("RGB")
                    view_size = CONFIG.get("VIEW_SIZE", 1200)
                    img_view.thumbnail((view_size, view_size), Image.Resampling.LANCZOS)
                    img_view.save(view_dest, "JPEG", quality=85)
            except Exception:
                pass

    if os.path.exists(dest): return dest
    
    # Create the square micro-thumbnail used within the catalog layout grid
    try:
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img).convert("RGB")
            w, h = img.size
            min_dim = min(w, h)
            left, top = (w - min_dim) / 2, (h - min_dim) / 2
            right, bottom = (w + min_dim) / 2, (h + min_dim) / 2
            img = img.crop((left, top, right, bottom))
            size = CONFIG["THUMB_SIZE"]
            img = img.resize((size, size), Image.Resampling.LANCZOS)
            img.save(dest, "JPEG", quality=85)
            print(src)
            return dest
    except: return src
    
def load_todo_list():
    """Load the list of marked objects from TODO.txt (JSON format)"""
    if not os.path.exists(TODO_FILE): return {}
    try:
        with open(TODO_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content: return {}
            return json.loads(content)
    except Exception as e:
        print(f"Error reading TODO.txt : {e}")
        return {}
        
def generate():
    """Main function: processes data and generates the HTML gallery"""
    final_json = {}
    stats = {}
    todo_list = load_todo_list() 
    prefixes_js = {k: v["prefix"] for k, v in CATALOGS.items()}
    
    for name, data_dict in CATALOGS.items():
        marked_dict = todo_list.get(name, {})
        objs = []
        found_count = 0
        prefix = data_dict["prefix"]
        keys = sorted(data_dict["data"].keys(), key=lambda x: (int(re.sub(r'\D', '', str(x))), str(x)))
        
        print(" ")
        print("==============")
        print("   " + name)
        print("==============")
        
        for k in keys:
            # working on list copy to modifiy the type without impact on the database
            info_raw = data_dict["data"][k]
            info = list(info_raw) 
            
            # --- translation logic ---
            type_code = info[0] # Ex: "SNR"
            info[0] = LANG["TYPES"].get(type_code, type_code) # becomes "Rémanent Supernova"
            
            tech_ref = info[1]
            img_file = find_image(prefix, k, tech_ref)
            thumb, date = "", ""
            if img_file:
                found_count += 1
                thumb, date = make_thumbnail(img_file), get_exif_date(img_file)
            
            ra, dec = info[6], info[7]
            h_max = 90 - abs(CONFIG["LATITUDE"] - dec)
            season_computed = compute_best_season(ra)

            color = "#c9d1d9" 
            if h_max <= CONFIG["LIMIT_IMPOSSIBLE"]: color = "#da3633" 
            elif h_max <= CONFIG["LIMIT_DIFFICILE"]: color = "#ff9f43" 

            objs.append({
                "id": k, 
                "prefix": prefix, 
                "info": info, 
                "type_code": type_code, # needed for JS filters
                "tech_ref": tech_ref,
                "img": img_file or "", 
                "thumb": thumb, 
                "date": date,
                "h_max": round(h_max, 1),
                "season_computed": season_computed,
                "label_color": color,
                "todo": str(k) in marked_dict,
                "todo_comment": marked_dict.get(str(k), "")
            })
            
        final_json[name] = objs
        stats[name] = f"{found_count}/{len(data_dict['data'])}"

    select_options = "".join([f'<option value="{c}" {"selected" if c == CONFIG["SELECTED_CATALOG"] else ""}>{c}</option>' for c in CATALOGS.keys()])
    season_options = "".join([f'<option value="{val}">{val}</option>' for val in LANG["SEASONS"].values()])
    dir_options = f'<option value="Tous">{LANG["ALL_DIR"]}</option><option value="{LANG["NORTH"]}">{LANG["NORTH"]}</option><option value="{LANG["SOUTH"]}">{LANG["SOUTH"]}</option>'
    family_options = f"""
        <option value="Tous">{LANG['FAMILIES_LABELS']['ALL']}</option>
        <option value="Nébuleuse">{LANG['FAMILIES_LABELS']['NEB']}</option>
        <option value="Galaxie">{LANG['FAMILIES_LABELS']['GAL']}</option>
        <option value="Amas">{LANG['FAMILIES_LABELS']['CLU']}</option>
    """

    limit_small = CONFIG.get("LIMIT_SMALL_OBJECT", 60)
    
    html_template = fr"""<!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/astronomy-engine@2.1.19/astronomy.browser.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            :root {{ --case-size: {CONFIG["THUMB_SIZE"]}px; }}
            body {{ background: #0d1117; color: #c9d1d9; font-family: 'Segoe UI', sans-serif; text-align: center; padding: 20px; overflow-x: hidden; }}
            h1 {{ font-size: 2.2em; margin-bottom: 5px; color: #fff; }}
            .stats-header {{ color: #8b949e; font-size: 1.1em; margin-bottom: 20px; }}
            .filter-bar {{ margin-bottom: 30px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
            .filter-select {{ 
                background: #21262d; color: #fff; border: 1px solid #388bfd; 
                padding: 8px 35px 8px 15px; border-radius: 20px; cursor: pointer; 
                font-family: inherit; font-size: 14px; outline: none; transition: 0.2s;
                appearance: none; -webkit-appearance: none; -moz-appearance: none;
                background-image: url('data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23ffffff%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E');
                background-repeat: no-repeat; background-position: right 12px top 50%; background-size: 10px auto;
            }}
            .btn-export {{ 
                position: fixed; top: 10px; right: 10px; z-index: 1000;
                background: #161b22; border: 1px solid #30363d; color: #8b949e;
                padding: 6px 12px; border-radius: 6px; font-size: 11px;
                cursor: pointer; transition: 0.2s;
            }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(var(--case-size), 1fr)); gap: 15px; width: 100%; margin: 0 auto; }}
            .case {{ background: #161b22; border-radius: 8px; border: 1px solid #30363d; overflow: hidden; position: relative; display: flex; flex-direction: column; }}
            
            /* Hearts handling - same size empty or full */
            .todo-heart {{ 
                position: absolute !important; 
                top: 5px; 
                right: 8px; 
                font-size: 20px; 
                z-index: 10; 
                user-select: none; 
                pointer-events: none;
                color: #ff4d4d;
                line-height: 1;
            }}
            .todo-heart.no-comment {{ 
                color: transparent;
                -webkit-text-stroke: 1.5px #ff4d4d;  // this makes the heart hollow
            }}
            .todo-heart.has-comment {{
                color: #ff4d4d !important;
                -webkit-text-stroke: 0px transparent;
            }}
            .img-box {{ width: 100%; aspect-ratio: 1 / 1; display: flex; align-items: center; justify-content: center; background: #000; cursor: pointer; overflow: hidden; position: relative; }}
            .img-box img {{ width: 100%; height: 100%; object-fit: cover; }}
            .empty-info {{ color: #484f58; font-size: 11px; font-weight: bold; text-align: center; padding: 5px; line-height: 1.2; }}
            .label {{ background: #21262d; padding: 8px 5px; font-weight: bold; font-size: 12px; border-top: 1px solid #30363d; cursor: pointer; transition: 0.2s; user-select: none; }}
            
            #tooltip {{ position: fixed; display: none; background: #0d1117; border: 1px solid #3498db; border-radius: 8px; padding: 12px; z-index: 2000; text-align: left; min-width: 320px; box-shadow: 0 8px 24px #000; pointer-events: none; }}
            #tooltip.frozen {{ border-color: #ff4d4d !important; pointer-events: auto !important; cursor: default; }}
            
            #overlay {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; overflow: hidden; }}
            #fullImg {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); cursor: grab; user-select: none; max-width: 95%; max-height: 95%; transition: transform 0.05s linear; }}
            #customPrompt {{ background: #161b22; color: #fff; border: 1px solid #388bfd; border-radius: 8px; padding: 15px; box-shadow: 0 8px 24px #000; max-width: 300px; text-align: center; }}
            #customPrompt::backdrop {{ background: rgba(0,0,0,0.6); }}
            #customPrompt label {{ display: block; font-size: 13px; margin-bottom: 10px; color: #c9d1d9; }}
            #customPrompt input {{ background: #0d1117; color: #fff; border: 1px solid #30363d; border-radius: 4px; padding: 6px; width: 90%; margin-bottom: 12px; outline: none; }}
            #customPrompt button {{ background: #21262d; border: 1px solid #388bfd; color: #fff; padding: 6px 15px; border-radius: 4px; cursor: pointer; font-size: 13px; }}
            
            .chart-container {{ background: #000000; padding: 5px; position: relative; margin-top: 10px; width: 300px; height: {CONFIG["CHART_HEIGHT"]}px; }}
            canvas {{ display: block; width: 100% !important; height: 100% !important; }}
        </style>
    </head>
    <body>
        <h1 id="catTitle">{LANG['CATALOG']}</h1>
        <div class="stats-header" id="statsText"></div>
        <div class="filter-bar">
            <select id="catSelect" class="filter-select" onchange="update()">
                {select_options}
            </select>
            <select id="familySelect" class="filter-select" onchange="filterF(this.value)">
                {family_options}
            </select>
            <select id="seasonSelect" class="filter-select" onchange="filterS(this.value)">
                <option value="Tous">{LANG['ALL']}</option>
                {season_options}
            </select>
            <select id="dirSelect" class="filter-select" onchange="filterD(this.value)">
                {dir_options}
            </select>
            <button onclick="exportTodo()" class="filter-select btn-export">💾 TODO.txt ❤</button>
        </div>
        <div class="grid" id="grid"></div>
        <div id="tooltip"></div>
        <div id="overlay" onclick="if(event.target===this) closeM()"><img id="fullImg"></div>

        <dialog id="customPrompt">
            <form method="dialog" id="promptForm">
                <label>{LANG['PROMPT_LABEL']}</label>
                <input type="text" id="promptInput" autocomplete="off">
                <br>
                <button type="submit">{LANG['VALIDATE']}</button>
            </form>
        </dialog>

        <script>
            const data = {json.dumps(final_json)};
            const stats = {json.dumps(stats)};
            const prefixes = {json.dumps(prefixes_js)};
            const thumbDir = "{CONFIG['THUMB_DIR']}";
            const userLat = {CONFIG['LATITUDE']}; 
            const userLon = {CONFIG['LONGITUDE']};
            const userElv = {CONFIG['ELEVATION']};
            let globalChartInstance = null;
            let isTooltipFrozen = false;
            
            // Sync local storage with JSON data on load
            let localTodo = JSON.parse(localStorage.getItem('astro_todo')) || {{}};
            for (let cat in data) {{
                if (!localTodo[cat]) localTodo[cat] = {{}};
                data[cat].forEach(obj => {{
                    if (obj.todo) {{ localTodo[cat][obj.id] = obj.todo_comment || ""; }}
                }});
            }}
            localStorage.setItem('astro_todo', JSON.stringify(localTodo));

            const FAMILIES = {{
                "Nébuleuse": ["N", "NP", "SC", "SNR", "EN", "RN", "E/RN", "N+C"],
                "Galaxie": ["G"],
                "Amas": ["GC", "OC", "D", "A", "N+C", "QSR"]
            }};
            
            let currentSeason = 'Tous', currentDir = 'Tous', currentFamily = 'Tous';
            let scale = 1, posX = 0, posY = 0, isDragging = false, startX, startY;
            const m = document.getElementById("overlay"), mi = document.getElementById("fullImg"), t = document.getElementById('tooltip');

            // Unfreeze tooltip when user right-clicks on a frozen tooltip box
            t.addEventListener('contextmenu', (e) => {{
                if (isTooltipFrozen) {{
                    e.preventDefault();
                    unfreezeTooltip();
                }}
            }});

            // Filters handling functions triggered by select elements change
            function filterS(s) {{ currentSeason = s; update(); }}
            function filterD(d) {{ currentDir = d; update(); }}
            function filterF(f) {{ currentFamily = f; update(); }}

            /**
             * Exports the favorite/todo objects list from localStorage as a JSON file named TODO.txt
             */
            function exportTodo() {{
                const blob = new Blob([JSON.stringify(localTodo, null, 4)], {{type: 'text/plain'}});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url; a.download = 'TODO.txt'; a.click();
                window.URL.revokeObjectURL(url);
            }}

            /**
             * Handles adding or removing an object from the favorite/todo list (Right-click on thumbnail image box)
             */
            function toggleHeart(e, catName, objId) {{
                e.preventDefault(); 
                if (isTooltipFrozen) return false;
                if (!localTodo[catName]) localTodo[catName] = {{}};
                
                if (localTodo[catName][objId] !== undefined) {{
                    delete localTodo[catName][objId];
                    localStorage.setItem('astro_todo', JSON.stringify(localTodo));
                    update();
                }} else {{
                    const dialog = document.getElementById('customPrompt');
                    const form = document.getElementById('promptForm');
                    const input = document.getElementById('promptInput');
                    input.value = ""; 
                    dialog.showModal();
                    form.onsubmit = () => {{
                        localTodo[catName][objId] = input.value.trim();
                        localStorage.setItem('astro_todo', JSON.stringify(localTodo));
                        update();
                    }};
                }}
                return false;
            }}

            /**
             * Locks or unlocks the tooltip visibility on right-click over a card label
             */
            function freezeTooltip(e, element, obj, currentComment) {{
                e.preventDefault();
                if (isTooltipFrozen) {{
                    unfreezeTooltip();
                    return false;
                }}
                showT(element, obj, currentComment);
                isTooltipFrozen = true;
                t.classList.add('frozen');
                
                if (globalChartInstance) {{
                    globalChartInstance.options.plugins.tooltip.enabled = true;
                    globalChartInstance.update();
                }}
                return false;
            }}

            /**
             * Completely hides and unlocks the locked tooltip, resetting the active chart instance
             */
            function unfreezeTooltip() {{
                isTooltipFrozen = false;
                t.classList.remove('frozen');
                t.style.display = 'none';
                if (globalChartInstance) {{
                    globalChartInstance.destroy();
                    globalChartInstance = null;
                }}
            }}

             /**
             * Computes if an object is currently visible tonight during astronomical night hours.
             * Strictly replicates the graph's rendering logic.
             */
            function computeIsVisibleToday(raTarget, decTarget) {{
                try {{
                    const userLat = parseFloat("{CONFIG["LATITUDE"]}");
                    const userLon = parseFloat("{CONFIG["LONGITUDE"]}");
                    
                    const latRad = userLat * Math.PI / 180;
                    const decRad = decTarget * Math.PI / 180;

                    // Recreate the graph's time base (around local midnight)
                    const now = new Date();
                    const midnightLocal = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);

                    let indexCoucherAstro = null;
                    let indexLeverAstro = null;

                    let altitudesSoleil = [];
                    let altitudesObjet = [];

                    // --- 1. COMPUTE BOTH CURVES (SUN AND OBJECT) ON THE SAME INDICES ---
                    for (let i = -72; i < 72; i++) {{
                        const hr = i / 6;
                        const datePoint = new Date(midnightLocal.getTime() + hr * 60 * 60 * 1000);
                        
                        // Local Sidereal Time (LST) calculation identical to the graph
                        const j2000 = (datePoint.getTime() / 86400000) - 10957.5;
                        const lstHours = (18.697374558 + 24.06570982441908 * j2000 + userLon / 15) % 24;

                        // A. Target altitude
                        const hourAngleRad = (lstHours - raTarget) * 15 * Math.PI / 180;
                        const sinAltTarget = Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad) * Math.cos(hourAngleRad);
                        const altTargetDeg = Math.asin(sinAltTarget) * 180 / Math.PI;
                        altitudesObjet.push(altTargetDeg);

                        // B. Sun altitude (reproducing the graph's formula)
                        const sunRA = (typeof raSunHours !== 'undefined') ? raSunHours : 3.6; 
                        const sunDec = (typeof DEC_SUN_RAD !== 'undefined') ? DEC_SUN_RAD : (19.3 * Math.PI / 180);
                        
                        const sunHourAngleRad = (lstHours - sunRA) * 15 * Math.PI / 180;
                        const sinAltSun = Math.sin(latRad) * Math.sin(sunDec) + Math.cos(latRad) * Math.cos(sunDec) * Math.cos(sunHourAngleRad);
                        const altSunDeg = Math.asin(sinAltSun) * 180 / Math.PI;
                        altitudesSoleil.push(altSunDeg);
                    }}

                    // --- 2. FIND NIGHT BOUNDARIES (ASTRO TWILIGHT / NIGHT BELOW -12°) ---
                    // Scan chronologically to find when the sun sets and rises below the threshold
                    for (let idx = 0; idx < altitudesSoleil.length; idx++) {{
                        // Threshold set to -12° (start of astronomical twilight / night)
                        if (altitudesSoleil[idx] <= -12) {{
                            if (indexCoucherAstro === null) {{
                                indexCoucherAstro = idx; // First point under the threshold
                            }}
                            indexLeverAstro = idx; // Last point under the threshold (updated at each step)
                        }}
                    }}

                    // If the sun never drops below -12° tonight (no astronomical window)
                    if (indexCoucherAstro === null || indexLeverAstro === null) {{
                        return false;
                    }}

                    // --- 3. COMPUTE DYNAMIC VISIBILITY THRESHOLD ---
                    // Calculate absolute maximum altitude regardless of the season: 90 - abs(lat - dec)
                    const maxAbsoluteAltitude = 90 - Math.abs(userLat - decTarget);
                    
                    const configThreshold = parseFloat("{CONFIG["TN_ALTITUDE_THRESHOLD"]}");
                    const configLowFactor = parseFloat("{CONFIG["TN_LOW_ALTITUDE_FACTOR"]}");
                    
                    let targetThreshold = 0;
                    if (maxAbsoluteAltitude > configThreshold) {{
                        targetThreshold = configThreshold;
                    }} else {{
                        targetThreshold = maxAbsoluteAltitude * configLowFactor;
                    }}

                    // --- 4. CHECK TARGET ALTITUDE BETWEEN THESE TWO BOUNDARIES ---
                    for (let idx = indexCoucherAstro; idx <= indexLeverAstro; idx++) {{
                        if (altitudesObjet[idx] > targetThreshold) {{
                            return true; // Match found! The object exceeds the dynamic threshold during the astro window
                        }}
                    }}

                    return false;

                }} catch (err) {{
                    return true; 
                }}
            }}
            
            /**
             * Rebuilds and filters the grid view based on the current selection of catalog, family, season, and direction
             */
            function update() {{
                const cat = document.getElementById('catSelect').value;
                const g = document.getElementById('grid'); 
                g.innerHTML = '';
                document.getElementById('catTitle').innerText = "{LANG['CATALOG']} " + cat;
                document.getElementById('statsText').innerText = "(" + stats[cat] + ")";
                
                data[cat].forEach(obj => {{
                    if (!obj.info || obj.info.length < 7) return;
                    const objType = obj.info[0].trim();
                    const rawTypeCode = obj.type_code.trim();
                    const objSeason = obj.season_computed; 
                    const raVal = parseFloat(obj.info[6]);
                    const declin = parseFloat(obj.info[7]);
                    const objDir = declin > userLat ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                    
                    if (currentFamily !== 'Tous' && !(FAMILIES[currentFamily] && FAMILIES[currentFamily].includes(rawTypeCode))) return;
                    
                    if (currentSeason !== 'Tous') {{
                        if (currentSeason === "{LANG['SEASONS']['TN']}") {{
                            if (!computeIsVisibleToday(raVal, declin)) return;
                        }} else if (objSeason !== currentSeason) {{
                            return;
                        }}
                    }}
                    if (currentDir !== 'Tous' && objDir !== currentDir) return;
                    
                    const d = document.createElement('div'); d.className = 'case';
                    const isTodo = localTodo[cat] && localTodo[cat][obj.id] !== undefined;
                    const currentComment = isTodo ? localTodo[cat][obj.id] : "";
                    
                    d.onmouseenter = (e) => {{ if (!isTooltipFrozen) showT(d, obj, currentComment); }};
                    d.onmouseleave = () => {{ if (!isTooltipFrozen) {{ t.style.display='none'; if(globalChartInstance) {{ globalChartInstance.destroy(); globalChartInstance = null; }} }} }}
                    
                    const heartClass = currentComment ? 'has-comment' : 'no-comment';
                    const heart = isTodo ? `<div class="todo-heart ${{heartClass}}">❤</div>` : '';

                    let displaySeason = currentSeason === 'Tous' ? `<br>(${{objSeason}})` : '';
                    let content = obj.thumb ? `<img src="${{obj.thumb}}">` : `<div class="empty-info">${{objType}}${{displaySeason}}</div>`;
                    
                    /* CRITICAL ZONE: Dynamic full-resolution preview assignment.
                       If the source image was a high-fidelity TIFF format, we intercept the link 
                       and map the card interaction event to open the generated 'view_*.jpg' proxy 
                       instead of trying to open the unsupported raw .tif binary directly.
                    */
                    let clickImg = obj.img;
                    if (obj.img && (obj.img.toLowerCase().endsWith('.tif') || obj.img.toLowerCase().endsWith('.tiff'))) {{
                        let baseName = obj.img.substring(0, obj.img.lastIndexOf('.'));
                        if (baseName.startsWith('thumb_')) baseName = baseName.substring(6);
                        clickImg = thumbDir + "/view_" + baseName + ".jpg";
                    }}
                    
                    /* CRITICAL ZONE: Heterogeneous Dynamic URL Generation For Telescopius routing.
                       Each deep-sky index handles naming profiles uniquely based on its survey ecosystem:
                       1. Messier & Caldwell: Directly match uniform sequential tracking codes ('m-X', 'c-X').
                       2. RASC & O'Meara: Mixed cross-referenced deep-sky tables. The script parses the target's 
                          technical designation field using regular expressions to extract standard catalog 
                          sub-identifiers (NGC, IC, Sh2, Barnard, vdB) and formats them into accurate URLs.
                    */
                    let tUrl = "https://telescopius.com/deep-sky-objects/";
                    if (obj.prefix === prefixes.Messier) tUrl += "m-" + obj.id;
                    else if (obj.prefix === prefixes.Caldwell) tUrl += "c-" + obj.id;
                    else if (obj.prefix === prefixes.RASC || obj.prefix === prefixes["O'Meara"]) {{
                        const match = obj.tech_ref.match(/(?:NGC|IC|SH2|BARNARD|VDB)[_ \-]?(\d+)/i);
                        const idNum = match ? match[1] : ""; 
                        
                        if (obj.tech_ref.toUpperCase().includes("IC")) tUrl += "ic-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("SH2")) tUrl += "sh2-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("BARNARD")) tUrl += "barnard-" + idNum;
                        else if (obj.tech_ref.toUpperCase().includes("VDB")) tUrl += "vdb-" + idNum;
                        else tUrl += "ngc-" + idNum;
                    }}
                
                    const labelText = obj.tech_ref ? `${{obj.prefix}}${{obj.id}} - ${{obj.tech_ref}}` : `${{obj.prefix}}${{obj.id}}`;
                    const imgAction = obj.img ? `openM('${{clickImg}}')` : `window.open('${{tUrl}}', '_blank')`;

                    const imgBoxEl = document.createElement('div');
                    imgBoxEl.className = "img-box";
                    imgBoxEl.onclick = () => eval(imgAction);
                    imgBoxEl.oncontextmenu = (e) => toggleHeart(e, cat, obj.id);
                    imgBoxEl.innerHTML = heart + content;

                    const labelEl = document.createElement('div');
                    labelEl.className = "label";
                    labelEl.style.color = obj.label_color;
                    labelEl.onclick = () => window.open(tUrl, '_blank');
                    labelEl.oncontextmenu = (e) => freezeTooltip(e, d, obj, currentComment);
                    labelEl.innerText = labelText;

                    d.appendChild(imgBoxEl);
                    d.appendChild(labelEl);
                    g.appendChild(d);
                }});
            }}


            // Full screen overlay image viewer control functions
            function openM(s) {{ if(!s) return; scale = 1; posX = 0; posY = 0; mi.src = s; m.style.display = "flex"; updateTransform(); }}
            function closeM() {{ m.style.display = "none"; }}
            function updateTransform() {{ mi.style.transform = `translate(calc(-50% + ${{posX}}px), calc(-50% + ${{posY}}px)) scale(${{scale}})`; }}
            
            // Image viewer pan & zoom mouse event listeners
            m.addEventListener('wheel', e => {{ e.preventDefault(); scale = Math.min(Math.max(0.5, scale * (e.deltaY > 0 ? 0.9 : 1.1)), 10); updateTransform(); }}, {{passive: false}});
            mi.addEventListener('mousedown', e => {{ isDragging = true; startX = e.clientX - posX; startY = e.clientY - posY; e.preventDefault(); }});
            window.addEventListener('mousemove', e => {{ if (isDragging) {{ posX = e.clientX - startX; posY = e.clientY - startY; updateTransform(); }} }});
            window.addEventListener('mouseup', () => isDragging = false);

            /**
             * Renders the details info box (tooltip) with object metadata and altitude profile chart via Chart.js
             */
            function showT(element, obj, comment) {{
                if (globalChartInstance) {{
                    globalChartInstance.destroy();
                    globalChartInstance = null;
                }}

                let html = "";
                if (obj.img) {{
                    html += `<div style="color:#4a9eff; font-weight:bold; font-size:12px; margin-bottom:2px;">${{obj.img}}</div>`;
                    html += `<div style="color:#888; font-size:11px; margin-bottom:8px;">Date: ${{obj.date}}</div>`;
                    html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                }}
                
                // Small object detection logic
                let s = obj.info[4] || "", c = "", threshold = {limit_small}; 
                let dims = s.split(/[x×]/), isSmall = dims.length > 0;
                for (let i = 0; i < dims.length; i++) {{
                    let d = dims[i].trim(), tm = 0, ts = 0;
                    let mMatch = d.match(/([0-9.]+)'($|[^'])/), sMatch = d.match(/([0-9.]+)(?:''|["])/);
                    if (mMatch) tm = parseFloat(mMatch[1]);
                    if (sMatch) ts = parseFloat(sMatch[1]);
                    if (!mMatch && !sMatch) {{ let v = parseFloat(d); if (!isNaN(v)) tm = v; }}
                    if ((tm * 60) + ts >= threshold || (tm * 60) + ts === 0) {{ isSmall = false; break; }}
                }}
                if (isSmall) c = ' style="color:orange;"';

                // Direction and badge calculation
                const declin = parseFloat(obj.info[7]), isNorth = declin > userLat;
                const direction = isNorth ? "{LANG['NORTH']}" : "{LANG['SOUTH']}";
                const badgeColor = isNorth ? "#3498db" : "#f1c40f";

                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["TYPE"]}:</strong> ${{obj.info[0]}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["SEASON"]}:</strong> ${{obj.season_computed}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["CONSTELLATION"]}:</strong> ${{obj.info[2]}}</div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["MAGNITUDE"]}:</strong> ${{obj.info[3]}}</div>`;
                html += `<div ${{c}}><strong>{LANG["TOOLTIP_LABELS"]["SIZE"]}:</strong> ${{s}}</div>`;
                
                // RA conversion to HMS
                let raDecimal = parseFloat(obj.info[6]);
                let hours = Math.floor(raDecimal), minDec = (raDecimal - hours) * 60, minutes = Math.floor(minDec), seconds = Math.round((minDec - minutes) * 60);
                if (seconds === 60) {{ seconds = 0; minutes += 1; }}
                if (minutes === 60) {{ minutes = 0; hours += 1; }}

                html += `<div><strong>RA :</strong> ${{hours}}h ${{String(minutes).padStart(2, '0')}}m ${{String(seconds).padStart(2, '0')}}s</div>`;
                html += `<div><strong>Dec :</strong> ${{obj.info[7]}}° <span style="font-size:9px; background:#21262d; color:${{badgeColor}}; padding:1px 4px; border-radius:3px; border:1px solid ${{badgeColor}}; margin-left:5px; vertical-align:middle; font-weight:bold;">${{direction}}</span></div>`;
                html += `<div><strong>{LANG["TOOLTIP_LABELS"]["ELEVATION"]}:</strong> ${{obj.h_max}}</div>`;
                
                if (comment) {{
                    html += `<hr style="border:0; border-top:1px solid #ff4d4d; margin:8px 0;">`;
                    html += `<div style="color:#ff6b6b; font-size:12px;"><strong>Note :</strong> ${{comment}}</div>`;
                }}

                html += `<hr style="border:0; border-top:1px solid #444; margin:8px 0;">`;
                html += `<div style="font-style:italic; color:#3498db; margin-top:5px;"><strong>${{obj.info[5]}}</strong></div>`;
                
                html += `<div class="chart-container"><canvas id="astroChart"></canvas></div>`;

                t.innerHTML = html; t.style.display = 'block';

                /* CRITICAL ZONE: Viewport-Relative Tooltip Anchoring & Collision Strategy.
                   The styling layout applies 'position: fixed' to avoid viewport breakout bugs 
                   when rendering massive databases containing large scroll containers.
                   The layout reads bounding viewport box geometries using 'getBoundingClientRect()'.
                   By checking the card midpoint against the global center of the viewport window, 
                   it automatically shifts the anchor offsets to avoid boundary clippings.
                */
                const rect = element.getBoundingClientRect();
                const windowWidth = window.innerWidth;
                const windowHeight = window.innerHeight;
                const midX = windowWidth / 2;
                const midY = windowHeight / 2;
                const cardCenterX = rect.left + rect.width / 2;
                const cardCenterY = rect.top + rect.height / 2;

                let leftPos = 0, topPos = 0;

                if (cardCenterY < midY) {{
                    topPos = rect.bottom;
                    if (cardCenterX < midX) {{
                        leftPos = rect.right;
                    }} else {{
                        leftPos = rect.left - t.offsetWidth;
                    }}
                }} else {{
                    topPos = rect.top - t.offsetHeight;
                    if (cardCenterX < midX) {{
                        leftPos = rect.right;
                    }} else {{
                        leftPos = rect.left - t.offsetWidth;
                    }}
                }}

                t.style.left = leftPos + 'px'; t.style.top = topPos + 'px';

                try {{
                    const RA_TARGET = raDecimal;
                    const DEC_TARGET = declin;
                    const ASTRE_NOM = (obj.prefix + obj.id);
                    const DECALAGE_HEURES = 1.5;

                    const maintenant = new Date();
                    const minuitLocal = new Date(maintenant.getFullYear(), maintenant.getMonth(), maintenant.getDate(), 0, 0, 0);

                    const heuresRelatives = [];
                    const altitudes = [];
                    const labelsX = [];
                    const altitudesSoleil = [];

                    let maxAlt = -90;
                    let idxMax = 0;
                    let nowIndex = -1;

                    const latRad = userLat * Math.PI / 180;
                    const decRad = DEC_TARGET * Math.PI / 180;
                    const DEC_SUN_RAD = 19.3 * Math.PI / 180;

                    let idxCoucher = -1;
                    let idxLever = -1;

                    // Compute sun altitudes for the whole 24h window
                    for (let i = -72; i < 72; i++) {{
                        const hr = i / 6;
                        const datePoint = new Date(minuitLocal.getTime() + hr * 60 * 60 * 1000);
                        try {{
                            const astroTimePoint = Astronomy.MakeTime(datePoint);
                            const lstHours = Astronomy.SiderealTime(astroTimePoint) + userLon / 15;
                            const raSunHours = 3.6;
                            const hourAngleRad = (lstHours - raSunHours) * 15 * Math.PI / 180;
                            const sinAlt = Math.sin(latRad) * Math.sin(DEC_SUN_RAD) + Math.cos(latRad) * Math.cos(DEC_SUN_RAD) * Math.cos(hourAngleRad);
                            altitudesSoleil.push(Math.asin(sinAlt) * 180 / Math.PI);
                        }} catch (err) {{
                            altitudesSoleil.push(-20);
                        }}
                    }}

                    // Detect sunset and sunrise index points
                    for (let k = 1; k < altitudesSoleil.length; k++) {{
                        if (k < 72 && altitudesSoleil[k-1] >= 0 && altitudesSoleil[k] < 0) idxCoucher = k;
                        if (k >= 72 && altitudesSoleil[k-1] <= 0 && altitudesSoleil[k] > 0) idxLever = k;
                    }}

                    let xMinIndex = 0;
                    let xMaxIndex = altitudesSoleil.length - 1;
                    const PAS_PAR_HEURE = 6;
                    const pasDecalage = DECALAGE_HEURES * PAS_PAR_HEURE;

                    if (idxCoucher !== -1 && idxLever !== -1) {{
                        xMinIndex = Math.max(0, idxCoucher - pasDecalage);
                        xMaxIndex = Math.min(altitudesSoleil.length - 1, idxLever + pasDecalage);
                    }} else {{
                        xMinIndex = 72 - (12 * PAS_PAR_HEURE);
                        xMaxIndex = 72 + (12 * PAS_PAR_HEURE) - 1;
                    }}

                    // Calculate targeted object altitude coordinates inside the active chart limits
                    for (let i = -72; i < 72; i++) {{
                        const hr = i / 6;
                        heuresRelatives.push(hr);
                        const datePoint = new Date(minuitLocal.getTime() + hr * 60 * 60 * 1000);
                        labelsX.push(`${{datePoint.getHours()}}h${{datePoint.getMinutes() === 0 ? '' : datePoint.getMinutes()}}`);
                        
                        if (nowIndex === -1 && datePoint >= maintenant) nowIndex = heuresRelatives.length - 1;

                        try {{
                            const astroTimePoint = Astronomy.MakeTime(datePoint);
                            const lstHours = Astronomy.SiderealTime(astroTimePoint) + userLon / 15;
                            const hourAngleRad = (lstHours - RA_TARGET) * 15 * Math.PI / 180;
                            const sinAlt = Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad) * Math.cos(hourAngleRad);
                            let alt = Math.asin(sinAlt) * 180 / Math.PI;
                            altitudes.push(alt);
                            if (alt > maxAlt) {{ maxAlt = alt; idxMax = heuresRelatives.length - 1; }}
                        }} catch (err) {{ altitudes.push(0); }}
                    }}

                    // Custom Chart.js layout drawing plugin (Sky background color shifts and vertical marker lines)
                    const backgroundPlugin = {{
                        id: 'customBackgroundAndLines',
                        beforeDraw: (chart) => {{
                            const {{ctx, chartArea: {{top, bottom, left, right}}, scales: {{x, y}}}} = chart;
                            const gradient = ctx.createLinearGradient(left, 0, right, 0);
                            const xMinVisible = chart.scales.x.min;
                            const xMaxVisible = chart.scales.x.max;
                            const totalVisible = xMaxVisible - xMinVisible;

                            for (let index = xMinVisible; index <= xMaxVisible; index++) {{
                                let ratio = (index - xMinVisible) / totalVisible;
                                let altSoleil = altitudesSoleil[index];
                                let color = "#000000";
                                if (altSoleil > 0) color = "#2a528a";
                                else if (altSoleil > -6) color = "#1a3360";
                                else if (altSoleil > -12) color = "#0e1c3a";
                                else if (altSoleil > -18) color = "#060a1e";
                                gradient.addColorStop(Math.max(0, Math.min(1, ratio)), color);
                            }}

                            ctx.save();
                            ctx.fillStyle = gradient;
                            ctx.fillRect(left, top, right - left, bottom - top);

                            ctx.lineWidth = 1;
                            ctx.setLineDash([5, 5]);
                            ctx.strokeStyle = 'rgba(255, 255, 255, 0.2)';
                            ctx.beginPath(); ctx.moveTo(left, y.getPixelForValue(0)); ctx.lineTo(right, y.getPixelForValue(0)); ctx.stroke();
                            ctx.strokeStyle = 'rgba(0, 255, 0, 0.3)';
                            ctx.beginPath(); ctx.moveTo(left, y.getPixelForValue(30)); ctx.lineTo(right, y.getPixelForValue(30)); ctx.stroke();

                            const xMaxPix = x.getPixelForValue(idxMax);
                            if (idxMax >= xMinVisible && idxMax <= xMaxVisible) {{
                                ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
                                ctx.lineWidth = 1; ctx.setLineDash([2, 4]);
                                ctx.beginPath(); ctx.moveTo(xMaxPix, top); ctx.lineTo(xMaxPix, bottom); ctx.stroke();
                            }}

                            if (nowIndex !== -1 && nowIndex >= xMinVisible && nowIndex <= xMaxVisible) {{
                                const xNowPix = x.getPixelForValue(nowIndex);
                                ctx.strokeStyle = 'rgba(0, 255, 0, 0.6)';
                                ctx.lineWidth = 1.5; ctx.setLineDash([4, 4]);
                                ctx.beginPath(); ctx.moveTo(xNowPix, top); ctx.lineTo(xNowPix, bottom); ctx.stroke();
                                ctx.fillStyle = 'rgba(0, 255, 0, 0.8)'; ctx.font = 'bold 10px sans-serif';
                                ctx.save(); ctx.translate(xNowPix - 4, top + 10); ctx.rotate(-Math.PI / 2); ctx.fillText('now', 0, 0); ctx.restore();
                            }}
                            ctx.restore();
                        }}
                    }};

                    const canvasCtx = document.getElementById('astroChart').getContext('2d');
                    globalChartInstance = new Chart(canvasCtx, {{
                        type: 'line',
                        data: {{
                            labels: labelsX,
                            datasets: [{{
                                label: 'Altitude',
                                data: altitudes,
                                borderColor: isNorth ? '#3498db' : '#f1c40f',
                                borderWidth: 3,
                                pointRadius: (context) => context.dataIndex === idxMax ? 6 : 0,
                                pointBackgroundColor: (context) => context.dataIndex === idxMax ? 'white' : 'transparent',
                                tension: 0.25
                            }}]
                        }},
                        plugins: [backgroundPlugin],
                        options: {{
                            responsive: true,
                            maintainAspectRatio: false,
                            interaction: {{ mode: 'nearest', axis: 'x', intersect: false }},
                            plugins: {{
                                legend: {{ display: false }},
                                title: {{ display: false }}, 
                                tooltip: {{ 
                                    enabled: isTooltipFrozen,
                                    displayColors: false,
                                    callbacks: {{
                                        title: function() {{ return null; }},
                                        beforeLabel: function() {{ return null; }},
                                        label: function(context) {{
                                            return `${{context.label}} ${{context.parsed.y.toFixed(0)}}°`;
                                        }}
                                    }}
                                }}
                            }},
                            scales: {{
                                x: {{
                                    type: 'category',
                                    min: xMinIndex,
                                    max: xMaxIndex,
                                    grid: {{ display: false }},
                                    ticks: {{ display: false }}, 
                                    border: {{ color: '#444444' }}
                                }},
                                y: {{
                                    min: 0,
                                    max: maxAlt > 0 ? Math.ceil(maxAlt + 15) : 90,
                                    ticks: {{ color: '#888888', font: {{ size: 9 }}, callback: (v) => Math.round(v) + '°' }}
                                }}
                            }}
                        }}
                    }});
                }} catch (err) {{ console.error(err); }}
            }}
            
            // Initialization update trigger on page startup
            update();
        </script>
    </body>
    </html>"""
    
    with open(CONFIG["OUTPUT_HTML"], "w", encoding="utf-8") as f: f.write(html_template)

if __name__ == "__main__":
    generate()
