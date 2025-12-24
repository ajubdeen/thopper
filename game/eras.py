"""
Era definitions for Anachron
Full version: 13 eras spanning 3,000+ years of human history

Each era includes:
- Base content (used in all modes)
- Adult content additions (used in Mature/Historian modes)
"""

ERAS = [
    # ═══════════════════════════════════════════════════════════════════
    # ERA 1: ANCIENT EGYPT - REIGN OF RAMESSES II
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "ancient_egypt",
        "name": "Ancient Egypt - Reign of Ramesses II",
        "year": -1250,
        "location": "Egypt",
        
        "image_description": """The banks of the Nile River at midday. Mud-brick houses 
cluster near the water. Workers in white linen kilts haul stones on wooden sledges. 
Palm trees line the riverbank. In the distance, massive temple columns rise against 
a blazing blue sky. A noble is carried past in a litter. Hieroglyphics are carved 
into a nearby wall. Fishing boats with triangular sails dot the river. No iron tools, 
no horses with saddles, no glass.""",
        
        "guess_keywords": ["egypt", "pharaoh", "nile", "pyramid", "ancient", "1000 bc",
                          "ramesses", "moses", "hieroglyphics", "bronze age"],
        
        "key_events": [
            "Ramesses II rules as living god - the most powerful pharaoh in history",
            "Massive temple construction at Abu Simbel and Karnak employs thousands",
            "Egypt has just fought the Hittites to a draw at the Battle of Kadesh",
            "The Nile flood determines whether people eat or starve this year",
            "Slavery is common - war captives and debtors work on royal projects"
        ],
        
        "figures": [
            "Ramesses II - The Great Pharaoh, builder of monuments, living god",
            "Nefertari - Great Royal Wife, one of the most powerful women in Egypt",
            "High Priest of Amun - Controls vast temple wealth, rivals Pharaoh's power",
            "Overseer of Works - Manages thousands of laborers on construction projects",
            "Nubian Soldiers - Elite archers serving in Pharaoh's army"
        ],
        
        "hard_rules": {
            "Lower": [
                "Corvée labor required - must work on Pharaoh's projects during flood season",
                "Cannot leave your village without permission",
                "Must give portion of harvest as taxes to temple and state",
                "Literacy is rare and powerful - scribes are a privileged class",
                "If the Nile flood fails, you starve first"
            ],
            "Middle": [
                "Artisans and scribes have more freedom but serve the temples",
                "Merchants can accumulate wealth but hold low social status",
                "Skills in demand can earn royal patronage"
            ],
            "Upper": [
                "Nobles serve at Pharaoh's pleasure - favor can be withdrawn",
                "Expected to provide troops and resources for royal projects",
                "Tomb building is essential - afterlife depends on it"
            ],
            "Female": [
                "More rights than in many ancient societies - can own property",
                "Can initiate divorce and conduct business",
                "But political power requires exceptional circumstances",
                "Royal women can wield enormous influence through Pharaoh"
            ]
        },
        
        # ADULT CONTENT ADDITIONS
        "adult_hard_rules": {
            "Lower": [
                "Beatings for slow work are common - overseers carry whips",
                "Sexual availability to masters expected of enslaved women",
                "Malnutrition stunts growth, weakens immune systems",
                "Work injuries often mean death - no medical care for laborers"
            ],
            "Female": [
                "Childbirth kills roughly 1 in 10 women",
                "Concubinage is normalized for lower-class women",
                "Rape of enslaved women carries no legal penalty"
            ]
        },
        
        "adult_events": [
            "Ramesses has over 100 children - his harem numbers in the hundreds",
            "Failed Nile floods cause famine - villages resort to cannibalism in the worst years",
            "Tomb workers who learn royal secrets are sometimes killed to preserve them"
        ],
        
        "agency_windows": [
            "Literacy (becoming a scribe) transforms life possibilities",
            "Skilled craftsmen are valued and can rise in status",
            "Military service offers path to land grants and honor",
            "Royal favor can elevate anyone - but also destroy them",
            "Understanding the Nile's patterns is survival knowledge"
        ],
        
        "debrief_facts": [
            "Ramesses II ruled for 66 years and had over 100 children",
            "Egyptian workers were not slaves - they were paid in bread, beer, and grain",
            "Women in ancient Egypt had more legal rights than women in Europe until the 1800s",
            "The pyramids were built 1,300 years BEFORE this era - they were already ancient",
            "Hieroglyphics were only used by about 1% of the population - most people were illiterate",
            "Average life expectancy was about 35 years due to disease and childbirth mortality"
        ],
        
        "real_people": [
            {
                "name": "Ramesses II (1303-1213 BCE)",
                "description": "The most powerful pharaoh in Egyptian history, he ruled for 66 years, built more monuments than any other ruler, and signed history's first known peace treaty with the Hittites."
            },
            {
                "name": "Nefertari (c. 1290-1255 BCE)",
                "description": "Great Royal Wife of Ramesses II and one of the best-known Egyptian queens. Her tomb in the Valley of the Queens is considered one of the most beautiful ever discovered."
            },
            {
                "name": "Paneb (fl. 1200 BCE)",
                "description": "A tomb worker at Deir el-Medina whose crimes were recorded on papyrus - theft, assault, and corruption. His case shows that even 'ordinary' ancient Egyptians left records behind."
            }
        ],
        
        "resources": [
            "📖 'The Egyptian' by Mika Waltari (historical fiction)",
            "📖 'Red Land, Black Land' by Barbara Mertz (accessible history)",
            "🎬 'Egypt's Golden Empire' - PBS documentary",
            "🌐 britishmuseum.org/collection (search 'ancient egypt')"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 2: CLASSICAL ATHENS - THE GOLDEN AGE
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "classical_athens",
        "name": "Classical Athens - The Golden Age",
        "year": -450,
        "location": "Greece",
        
        "image_description": """The Athenian agora (marketplace) on a busy morning. 
White marble temples and stoas with painted columns line the square. Men in draped 
chitons debate in small groups. A philosopher teaches students in the shade. Slaves 
carry amphorae of wine and oil. The Acropolis rises in the background, the Parthenon 
under construction with wooden scaffolding. No paper, no saddles on horses, pottery 
everywhere.""",
        
        "guess_keywords": ["athens", "greece", "greek", "ancient", "democracy", "parthenon",
                          "500 bc", "400 bc", "classical", "pericles", "socrates"],
        
        "key_events": [
            "Athens has just defeated the Persian Empire - the city is triumphant",
            "Pericles leads Athens and is building the Parthenon with allied tribute money",
            "Democracy exists, but only for adult male citizens - women, slaves, and foreigners cannot vote",
            "Philosophy, theater, and art flourish - Socrates teaches in the agora",
            "Tensions with Sparta are rising - war seems inevitable"
        ],
        
        "figures": [
            "Pericles - Elected leader (strategos), master orator, drives Athenian expansion",
            "Socrates - Philosopher who questions everything, annoys the powerful",
            "Aspasia - Pericles' foreign-born partner, intellectual and influential (but not a citizen)",
            "Phidias - Master sculptor creating the great statues of the gods",
            "Enslaved workers - Perhaps 30% of Athens' population, doing most physical labor"
        ],
        
        "hard_rules": {
            "Lower": [
                "If enslaved, you are property with no legal rights",
                "Free poor can vote but have little real influence",
                "Manual labor is looked down upon by the elite",
                "Military service (as rower or hoplite) is expected of citizens"
            ],
            "Middle": [
                "Merchants and craftsmen can accumulate wealth",
                "Metics (resident foreigners) pay taxes but cannot vote or own land",
                "Liturgies - rich citizens must fund warships or festivals"
            ],
            "Upper": [
                "Expected to participate in politics and fund public works",
                "Ostracism - citizens can vote to exile anyone for 10 years",
                "Elite status requires both wealth AND noble birth"
            ],
            "Female": [
                "Citizen women cannot vote, own property, or go out alone",
                "Confined to the women's quarters (gynaeceum)",
                "Marriage arranged by father or male guardian",
                "Foreign women (like Aspasia) have more freedom but less protection"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Enslaved people can be tortured to extract testimony in court",
                "Sexual use of slaves - male or female - is owner's right",
                "Mining slaves at Laurion have life expectancy under 30"
            ],
            "Female": [
                "Respectable women are essentially confined to home",
                "Hetairai (courtesans) have freedom but no legal protection",
                "Exposure of infant girls is common and legal"
            ]
        },
        
        "adult_events": [
            "Pederasty (older men mentoring/sexualizing adolescent boys) is normalized among the elite",
            "The silver mines at Laurion work slaves to death in brutal conditions",
            "Unwanted infants, especially girls, are exposed on hillsides to die"
        ],
        
        "agency_windows": [
            "Philosophy and rhetoric can win fame regardless of birth",
            "Military heroism in battle can elevate status",
            "Artistic skill (sculpture, pottery, drama) brings recognition",
            "For metics, wealth can buy influence if not citizenship",
            "Education is the key to advancement for free males"
        ],
        
        "debrief_facts": [
            "Athenian democracy excluded women, slaves, and foreigners - only about 10-20% could vote",
            "Slaves made up perhaps 30-40% of Athens' population and did most physical work",
            "The Parthenon was built using tribute money from Athens' 'allies' - essentially an empire",
            "Socrates was eventually executed by Athens for 'corrupting the youth'",
            "The Peloponnesian War (431-404 BCE) would destroy Athens' golden age",
            "Women in Athens had fewer rights than in Sparta, where they could own property"
        ],
        
        "real_people": [
            {
                "name": "Socrates (470-399 BCE)",
                "description": "The philosopher who invented the 'Socratic method' of questioning. He wrote nothing - we know him through his students. Athens eventually executed him for impiety and corrupting youth."
            },
            {
                "name": "Aspasia of Miletus (c. 470-400 BCE)",
                "description": "A foreign-born woman who became Pericles' partner and ran an intellectual salon. She was mocked by comedians but respected by philosophers. Her son with Pericles was eventually granted citizenship."
            },
            {
                "name": "Neaira (fl. 400 BCE)",
                "description": "An enslaved woman whose life is known from a court case. She was bought, sold, freed, and eventually prosecuted for pretending her children were citizens - showing how precarious life was for non-citizens."
            }
        ],
        
        "resources": [
            "📖 'The Histories' by Herodotus (ancient source, surprisingly readable)",
            "📖 'The Last Days of Socrates' by Plato",
            "🎬 'The Greeks' - PBS documentary series",
            "🌐 perseus.tufts.edu (ancient texts and images)"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 3: HAN DYNASTY CHINA - THE SILK ROAD
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "han_dynasty",
        "name": "Han Dynasty China - The Silk Road",
        "year": 100,
        "location": "China",
        
        "image_description": """A bustling market town along the Silk Road. Merchants 
in silk robes haggle over goods. Camels laden with bundles rest in a courtyard. 
A government official in elaborate robes passes with attendants. Chinese characters 
are painted on wooden signs. Pagoda-style roofs with upturned corners line the street.
Soldiers in lacquered armor patrol. Paper scrolls visible in a scholar's hands. 
No gunpowder weapons, no printing press (yet), distinctive Han dynasty aesthetics.""",
        
        "guess_keywords": ["china", "han", "silk road", "100 ad", "ancient china",
                          "dynasty", "emperor", "asia", "1st century", "confucius"],
        
        "key_events": [
            "The Han Dynasty rules the largest empire on Earth - 60 million people",
            "The Silk Road connects China to Rome, spreading goods, ideas, and disease",
            "Confucianism is state ideology - civil service exams determine who governs",
            "Paper has been invented but is still new and rare",
            "Tensions between court factions (eunuchs vs scholars) threaten stability"
        ],
        
        "figures": [
            "The Emperor - Son of Heaven, absolute ruler (in theory)",
            "Court Eunuchs - Powerful palace officials, control access to Emperor",
            "Confucian Scholars - Educated elite who staff the bureaucracy",
            "Silk Road Merchants - Wealthy traders connecting East and West",
            "Generals on the Frontier - Defending against Xiongnu nomad raids"
        ],
        
        "hard_rules": {
            "Lower": [
                "Peasants are tied to the land and owe taxes and labor",
                "Corvée labor required for state projects (walls, canals)",
                "Cannot change social class without education or military service",
                "Famines are common - government granaries sometimes help"
            ],
            "Middle": [
                "Merchants are legally low status but can be very wealthy",
                "Artisans serve the state or wealthy patrons",
                "Education can raise a family's status over generations"
            ],
            "Upper": [
                "Nobles and officials live well but are subject to court politics",
                "Fall from favor can mean execution of entire family",
                "Expected to be cultured - poetry, calligraphy, classical learning"
            ],
            "Female": [
                "Confucian hierarchy places women below men",
                "Foot-binding not yet practiced (comes later)",
                "Elite women can be educated but rarely hold official power",
                "Empresses and concubines can wield enormous behind-scenes influence"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Starvation during famines kills millions",
                "Bandits prey on travelers - robbery often includes murder",
                "Conscript soldiers face brutal conditions on the frontier"
            ],
            "Upper": [
                "Clan punishment means entire families executed for one member's crime",
                "Palace intrigues regularly end in poisoning, assassination"
            ],
            "Female": [
                "Concubines compete for Emperor's favor - losers may be killed",
                "Widow suicide to follow husband is praised"
            ]
        },
        
        "adult_events": [
            "Court eunuchs are castrated as children - many die from the procedure",
            "The Yellow Turban Rebellion will soon kill millions in civil war",
            "Prisoners of war are enslaved or executed en masse"
        ],
        
        "agency_windows": [
            "Civil service exams can elevate even poor scholars to power",
            "Military achievement on the frontier brings rewards",
            "Trade along the Silk Road can make fortunes",
            "Literacy and classical education are pathways to status",
            "Court connections matter more than wealth alone"
        ],
        
        "debrief_facts": [
            "Han China and Rome never directly contacted each other but traded via intermediaries",
            "Paper was invented in China around 100 CE but took 1,000 years to reach Europe",
            "The civil service exam system lasted over 2,000 years until 1905",
            "The Han Dynasty collapsed partly due to a pandemic (165-180 CE) that killed millions",
            "Chinese silk was so valuable in Rome that the Senate tried to ban it as too expensive",
            "The Great Wall was extensively rebuilt during the Han to defend against nomads"
        ],
        
        "real_people": [
            {
                "name": "Ban Zhao (45-116 CE)",
                "description": "Female historian and scholar who completed her brother's history of the Han Dynasty. She also wrote 'Lessons for Women,' advising women on proper behavior - controversial both then and now."
            },
            {
                "name": "Zhang Qian (d. 113 BCE)",
                "description": "The explorer who opened the Silk Road. Sent west by the Emperor, he was captured by nomads for 10 years before escaping and returning with knowledge of Central Asia."
            },
            {
                "name": "Cai Lun (c. 50-121 CE)",
                "description": "The court official credited with improving papermaking. His innovation transformed how information was recorded and transmitted - one of the most important inventions in history."
            }
        ],
        
        "resources": [
            "📖 'The Silk Roads' by Peter Frankopan (accessible history)",
            "📖 'Chronicle of the Chinese Emperors' by Ann Paludan",
            "🎬 'China: A Century of Revolution' - PBS documentary",
            "🌐 depts.washington.edu/silkroad"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 4: VIKING AGE SCANDINAVIA
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "viking_age",
        "name": "Viking Age Scandinavia",
        "year": 900,
        "location": "Scandinavia",
        
        "image_description": """A Norse coastal settlement at dawn. Longhouses with 
turf roofs line a fjord. A dragon-prowed longship is beached on the shore. Warriors 
in chainmail check their axes and round shields. Women in long dresses with brooches 
tend cooking fires. Runes are carved into a standing stone. Snow-capped mountains 
rise in the distance. Sheep graze on green slopes. No castles, no Christianity symbols 
dominant yet, iron age technology.""",
        
        "guess_keywords": ["viking", "norse", "scandinavia", "900", "medieval",
                          "longship", "raid", "norway", "sweden", "denmark", "9th century"],
        
        "key_events": [
            "Viking raids and settlements have spread from Ireland to Russia",
            "Harald Fairhair has recently unified Norway - many flee his rule",
            "Iceland is being settled by Norse seeking freedom and land",
            "Christianity is spreading but most still worship Odin, Thor, and Freyja",
            "The Thing (assembly) governs legal disputes - law is recited from memory"
        ],
        
        "figures": [
            "The Jarl - Local lord, leads raids, dispenses justice",
            "The Völva - Seeress and spiritual leader, speaks with the gods",
            "Shield-Maidens - Women warriors (rare but attested in sagas)",
            "Thralls - Enslaved people, often captured in raids",
            "Skalds - Poets who preserve history and praise heroes"
        ],
        
        "hard_rules": {
            "Lower": [
                "Thralls (slaves) have no rights and can be killed by owners",
                "Free farmers (karls) must support their lord in war",
                "Outlawry means anyone can kill you without penalty",
                "Survival depends on community - exile is often death"
            ],
            "Middle": [
                "Free farmers can own land and speak at the Thing",
                "Craftsmen (smiths especially) are highly valued",
                "Trade can bring wealth and status"
            ],
            "Upper": [
                "Jarls and wealthy landowners wield local power",
                "Expected to be generous - reputation matters enormously",
                "Blood feuds between families can last generations"
            ],
            "Female": [
                "More rights than in many medieval societies",
                "Can own property, divorce, and run households",
                "Cannot speak at the Thing or hold formal office",
                "Some women fight as shield-maidens (exceptional but real)"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Thralls can be sacrificed at their owner's funeral",
                "Female thralls routinely sexually used by owners",
                "Thrall children can be killed if unwanted"
            ],
            "Upper": [
                "Raids involve killing, rape, and enslaving captives",
                "Blood feuds require killing to restore honor"
            ],
            "Female": [
                "Captured women in raids are raped and enslaved",
                "Concubinage with thralls is common for married men"
            ]
        },
        
        "adult_events": [
            "Blood eagle - ritual execution where ribs are spread and lungs pulled out (disputed but recorded)",
            "Raids on monasteries include murder of monks, rape of local women",
            "Infanticide of weak or unwanted children is practiced"
        ],
        
        "agency_windows": [
            "Raiding can bring wealth and fame (but also death)",
            "Settling new lands (Iceland, etc.) offers freedom and opportunity",
            "Skilled craftsmen and traders are valued in any community",
            "Earning a reputation for honor and generosity builds power",
            "Learning the law makes you valuable at the Thing"
        ],
        
        "debrief_facts": [
            "Vikings were farmers and traders first - raiding was seasonal",
            "Women had more legal rights in Norse society than in most of medieval Europe",
            "The word 'viking' means 'pirate raid' - not all Norse people were vikings",
            "Iceland's Althing (930 CE) is one of the world's oldest parliaments",
            "Vikings reached North America (Vinland) around 1000 CE - 500 years before Columbus",
            "Slavery was central to Viking economy - thralls made up perhaps 10-30% of population"
        ],
        
        "real_people": [
            {
                "name": "Aud the Deep-Minded (c. 834-900 CE)",
                "description": "A Norse queen who led her family to settle Iceland after her son was killed. She freed her slaves and gave them land - an unusual act of generosity recorded in the sagas."
            },
            {
                "name": "Ragnar Lothbrok (legendary, fl. 9th century)",
                "description": "A legendary Viking hero whose historical existence is debated. His sons definitely existed and led the Great Heathen Army that invaded England in 865 CE."
            },
            {
                "name": "The Oseberg Women (buried c. 834 CE)",
                "description": "Two women buried in the richest Viking ship burial ever found. One may have been a völva (seeress). Their identities remain mysterious but show women could hold great status."
            }
        ],
        
        "resources": [
            "📖 'The Viking World' edited by Stefan Brink (comprehensive)",
            "📖 'Norse Mythology' by Neil Gaiman (accessible myths)",
            "🎬 'Vikings' TV series (dramatized but atmospheric)",
            "🌐 hurstwic.org (Viking combat and daily life)"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 5: MEDIEVAL EUROPE - THE BLACK DEATH
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "medieval_plague",
        "name": "Medieval Europe - The Black Death",
        "year": 1348,
        "location": "France",
        
        "image_description": """A medieval French village at dusk. Thatched-roof cottages 
line a muddy street. A Gothic church steeple rises in the background. Peasants in 
rough wool clothing hurry past, some covering their faces with cloth. A wooden cart 
sits abandoned. Smoke rises from a distant bonfire. The sky is overcast and ominous. 
No modern elements visible - no glass windows, no printed signs, no metal fixtures.""",
        
        "guess_keywords": ["medieval", "plague", "black death", "1300s", "14th century", 
                          "middle ages", "europe", "france", "feudal"],
        
        "key_events": [
            "The Black Death has arrived from the East, killing 30-60% of Europe's population",
            "The feudal system binds peasants to their lord's land - leaving is illegal",
            "The Church teaches that the plague is God's punishment for sin",
            "The Hundred Years War between England and France has paused due to the plague",
            "Jewish communities are being blamed and attacked across Europe"
        ],
        
        "figures": [
            "Pope Clement VI - Lives in Avignon, trying to make sense of God's wrath",
            "Flagellants - Religious groups who whip themselves publicly to appease God",
            "Local Lord - Controls justice, land, and the lives of peasants",
            "Village Priest - Only literate person most peasants ever meet"
        ],
        
        "hard_rules": {
            "Lower": [
                "Cannot leave lord's land without permission (serfdom)",
                "Cannot own weapons",
                "Must give portion of harvest to lord",
                "First to starve when food is scarce",
                "Poor nutrition = higher plague mortality"
            ],
            "Middle": [
                "Slightly better nutrition improves survival odds",
                "Trade skills are valuable but travel is dangerous",
                "Guild membership provides some protection"
            ],
            "Upper": [
                "Better food and living conditions = better survival odds",
                "Expected to maintain order and lead during crisis",
                "Can flee to country estates"
            ],
            "Female": [
                "Cannot inherit land in most cases",
                "Marriage arranged by family",
                "Convent is only path to education",
                "Widows have more rights than married women"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Plague victims die in agony - buboes swell, fever rages, skin blackens",
                "Bodies pile up - not enough living to bury the dead",
                "Starvation follows plague as farmers die"
            ],
            "Female": [
                "Childbirth mortality around 10% - higher during plague",
                "Rape by soldiers common during war and chaos",
                "Accused witches can be tortured and burned"
            ]
        },
        
        "adult_events": [
            "Flagellants whip themselves bloody in public processions",
            "Jewish communities are massacred - burned alive in their synagogues",
            "Plague doctors lance buboes - pus and blood spray out",
            "Mass graves hold hundreds of rotting corpses"
        ],
        
        "agency_windows": [
            "Recognizing plague symptoms early and fleeing",
            "Entering a convent or monastery for education and relative safety",
            "Learning a trade - post-plague labor shortage creates opportunity",
            "Treating Jewish neighbors well - moral choice with potential alliance",
            "Understanding basic sanitation (avoid sick, clean water)"
        ],
        
        "debrief_facts": [
            "The Black Death killed 30-60% of Europe's population between 1347-1351",
            "The plague was caused by Yersinia pestis bacteria, spread by fleas on rats",
            "Medieval people thought it was caused by 'bad air' (miasma) or God's punishment",
            "After the plague, surviving workers could demand higher wages - serfdom weakened",
            "The plague returned every 10-20 years for centuries",
            "Jewish pogroms killed thousands - people needed someone to blame"
        ],
        
        "real_people": [
            {
                "name": "Giovanni Boccaccio (1313-1375)",
                "description": "Italian writer who survived the plague in Florence and wrote 'The Decameron,' stories told by people fleeing the city. His vivid descriptions are our best account of how people lived through the horror."
            },
            {
                "name": "Pope Clement VI (1291-1352)",
                "description": "Condemned the persecution of Jews, saying 'the plague is not their fault.' He hired doctors to study the disease and protected Jewish communities in Avignon. One of the few powerful people who tried to stop the scapegoating."
            },
            {
                "name": "Margery Kempe (c. 1373-1438)",
                "description": "A middle-class woman who became a famous religious figure despite being illiterate. She dictated her autobiography - the first in English - showing how women could find voice and influence through religion."
            }
        ],
        
        "resources": [
            "📖 'The Decameron' by Giovanni Boccaccio (excerpts online)",
            "📖 'A Distant Mirror' by Barbara Tuchman (ages 12+)",
            "🎬 'The Black Death' - BBC Documentary (YouTube)",
            "🌐 medievalchronicles.com/black-death"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 6: AZTEC EMPIRE - EVE OF CONQUEST
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "aztec_empire",
        "name": "Aztec Empire - Eve of Conquest",
        "year": 1510,
        "location": "Tenochtitlan (Mexico)",
        
        "image_description": """The island city of Tenochtitlan at midday. Great stone 
pyramids rise above whitewashed buildings. Canals filled with canoes cut through 
the city. A market square overflows with goods - jade, feathers, cacao, textiles. 
Priests in black robes with matted hair climb temple steps. Warriors in jaguar and 
eagle costumes stand guard. Chinampas (floating gardens) ring the lake. Mountains 
frame the valley. No horses, no iron, no wheat - distinctly Mesoamerican.""",
        
        "guess_keywords": ["aztec", "mexico", "tenochtitlan", "1500s", "mesoamerica",
                          "pyramid", "conquistador", "montezuma", "pre-columbian"],
        
        "key_events": [
            "The Aztec Empire rules central Mexico through tribute and terror",
            "Tenochtitlan is one of the world's largest cities - 200,000+ people",
            "Human sacrifice is central to religion - feeding the sun to prevent apocalypse",
            "Omens and prophecies trouble the Emperor - strange signs in the sky",
            "Unknown to all, Spanish conquistadors will arrive within a decade"
        ],
        
        "figures": [
            "Motecuhzoma II (Montezuma) - The Emperor, troubled by prophecies",
            "High Priests - Control the temples and sacrificial calendar",
            "Jaguar and Eagle Warriors - Elite soldiers who capture enemies for sacrifice",
            "Pochteca - Long-distance merchants who also serve as spies",
            "Subject Peoples - Conquered nations who pay tribute and resent Aztec rule"
        ],
        
        "hard_rules": {
            "Lower": [
                "Commoners (macehualtin) work the land and pay tribute",
                "Cannot wear certain clothes or jewelry reserved for nobles",
                "Debt can lead to slavery (though children are born free)",
                "Subject peoples bear heaviest tribute and sacrifice demands"
            ],
            "Middle": [
                "Artisans and merchants can accumulate wealth",
                "Pochteca merchants have their own laws and privileges",
                "Skilled craftsmen serve the nobility and temples"
            ],
            "Upper": [
                "Nobles (pipiltin) rule by birth and military achievement",
                "Warriors who capture enemies rise in status",
                "Priests hold enormous power through control of religion"
            ],
            "Female": [
                "Women can own property and conduct business",
                "Midwives and healers hold respected positions",
                "But political and military power belongs to men",
                "Noblewomen can wield influence through family connections"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Subject peoples provide sacrificial victims - terror keeps them obedient",
                "Flower Wars exist to capture victims alive for sacrifice"
            ],
            "Upper": [
                "High-ranking captives sacrificed with elaborate ceremony",
                "Hearts cut from living victims, bodies thrown down temple steps"
            ],
            "Female": [
                "Women who die in childbirth become warrior spirits",
                "Female slaves may be sacrificed"
            ]
        },
        
        "adult_events": [
            "Mass sacrifices at temple dedications kill thousands over days",
            "Priests wear flayed human skin during certain rituals",
            "Cannibalism of sacrificial victims occurs in ritual contexts",
            "Children sacrificed to rain god Tlaloc - their tears please him"
        ],
        
        "agency_windows": [
            "Military achievement can elevate commoners to noble status",
            "Merchant success brings wealth and influence",
            "Artisan skills in featherwork, goldsmithing are highly valued",
            "Understanding political tensions (subject peoples' resentment) is valuable",
            "Prophecies and omens can be interpreted to one's advantage"
        ],
        
        "debrief_facts": [
            "Tenochtitlan was built on an island in Lake Texcoco and was larger than most European cities",
            "The Aztecs did not call themselves 'Aztec' - they were the Mexica",
            "When the Spanish arrived, many subject peoples joined them against the Aztecs",
            "90% of the indigenous population died from European diseases, not conquest",
            "Aztec education was compulsory for all children - rare for any society at the time",
            "Chocolate (xocolatl) was a sacred drink reserved for nobles and warriors"
        ],
        
        "real_people": [
            {
                "name": "Motecuhzoma II (c. 1466-1520)",
                "description": "The last fully independent Aztec emperor. Educated as a priest, he was troubled by prophecies about the return of Quetzalcoatl. He died during the Spanish conquest - possibly killed by his own people."
            },
            {
                "name": "Malintzin/La Malinche (c. 1500-1529)",
                "description": "An indigenous woman who became Cortés' interpreter and advisor. Born noble, sold into slavery, she used her linguistic skills to survive. Mexicans still debate whether she was a traitor or a survivor."
            },
            {
                "name": "Nezahualcoyotl (1402-1472)",
                "description": "Poet-king of Texcoco, an allied city. His philosophical poems questioning human sacrifice and mortality survive today. He represents the intellectual sophistication of pre-conquest Mexico."
            }
        ],
        
        "resources": [
            "📖 'The Fifth Sun' by Camilla Townsend (modern history)",
            "📖 'Aztec' by Gary Jennings (epic historical fiction, mature)",
            "🎬 'Engineering an Empire: The Aztecs' - History Channel",
            "🌐 mexicolore.co.uk (educational resource)"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 7: MUGHAL INDIA - AKBAR'S REIGN
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "mughal_india",
        "name": "Mughal India - Akbar's Court",
        "year": 1600,
        "location": "India (Delhi/Agra)",
        
        "image_description": """The Red Fort at Agra at sunset. Red sandstone walls 
rise above gardens with geometric pools. Nobles in elaborate robes and turbans 
gather in a courtyard with inlaid marble floors. Elephants with decorated howdahs 
wait outside. Hindu and Muslim men converse together. Women in colorful saris 
watch from screened balconies. A master miniature painter works in a workshop. 
Minarets and Hindu temple spires both visible. Distinctive Mughal architecture.""",
        
        "guess_keywords": ["india", "mughal", "1600", "akbar", "taj mahal", "delhi",
                          "agra", "17th century", "emperor", "hindu", "muslim"],
        
        "key_events": [
            "Emperor Akbar has united much of India under Mughal rule through conquest and diplomacy",
            "Akbar's policy of religious tolerance brings Hindus into government",
            "The empire is fabulously wealthy - controlling India's textile and spice trade",
            "Art, architecture, and learning flourish at court",
            "European traders (Portuguese, soon English and Dutch) seek trading posts"
        ],
        
        "figures": [
            "Akbar the Great - Emperor who cannot read but patronizes learning",
            "Birbal - Hindu advisor and wit, one of Akbar's 'Nine Jewels'",
            "Abul Fazl - Court historian recording Akbar's reign",
            "Rajput Princes - Hindu rulers who ally with or fight the Mughals",
            "European Merchants - Seeking spices, textiles, and trading rights"
        ],
        
        "hard_rules": {
            "Lower": [
                "Peasants pay heavy taxes to landlords and the state",
                "Caste still shapes Hindu society even under Muslim rule",
                "Famines occur when monsoons fail",
                "Artisans can be conscripted for imperial projects"
            ],
            "Middle": [
                "Merchants can become wealthy through trade",
                "Skilled craftsmen (weavers, metalworkers) are in demand",
                "Religious scholars and administrators have secure positions"
            ],
            "Upper": [
                "Nobles (mansabdars) hold land in exchange for military service",
                "Court positions depend on imperial favor - insecure",
                "Expected to maintain troops and elephants for the emperor"
            ],
            "Female": [
                "Purdah (seclusion) common among elite Muslim and some Hindu women",
                "Royal women wield power behind the screens",
                "Lower-class women work openly in markets and fields",
                "Sati (widow burning) practiced in some Hindu communities"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Famine deaths number in millions when monsoon fails",
                "Bonded labor traps families for generations"
            ],
            "Upper": [
                "Harem politics lead to poisonings, blinding of rivals",
                "Defeated enemies impaled or trampled by elephants"
            ],
            "Female": [
                "Sati - widows burn alive on husband's funeral pyre",
                "Harem concubines compete for survival",
                "Child marriage common among all classes"
            ]
        },
        
        "adult_events": [
            "Execution by elephant - victims crushed slowly in public",
            "Mass blinding of defeated armies",
            "Sati ceremonies - women drugged or forced onto pyres",
            "Famine cannibalism recorded in worst years"
        ],
        
        "agency_windows": [
            "Religious tolerance means talent matters more than faith at court",
            "Artistic skill brings imperial patronage",
            "Military service can elevate anyone in the mansabdar system",
            "Trade with Europeans offers new opportunities",
            "Linguistic skills (Persian, Sanskrit, local languages) are valuable"
        ],
        
        "debrief_facts": [
            "Akbar was illiterate but had books read to him and debated scholars nightly",
            "The Mughal Empire controlled perhaps 25% of world GDP at its height",
            "Akbar created a new religion (Din-i Ilahi) combining elements of many faiths - it didn't survive him",
            "The Taj Mahal was built later by Akbar's grandson Shah Jahan",
            "Indian textiles were so superior that Britain later banned their import to protect English weavers",
            "Akbar married Hindu Rajput princesses and abolished the tax on non-Muslims"
        ],
        
        "real_people": [
            {
                "name": "Akbar the Great (1542-1605)",
                "description": "One of history's most successful rulers. Though illiterate and a conqueror, he created an empire based on religious tolerance and efficient administration. He held debates between Muslims, Hindus, Christians, and Zoroastrians at his court."
            },
            {
                "name": "Nur Jahan (1577-1645)",
                "description": "Empress consort who effectively ruled the Mughal Empire for years. She issued coins in her own name, hunted tigers, and designed gardens. One of the most powerful women in world history."
            },
            {
                "name": "Tansen (c. 1500-1586)",
                "description": "A Hindu musician at Akbar's court, considered the greatest musician in Indian history. Legend says his singing could light lamps and bring rain. His musical innovations still influence Indian classical music."
            }
        ],
        
        "resources": [
            "📖 'The Mughal World' by Abraham Eraly",
            "📖 'Akbar and the Rise of the Mughal Empire' by G.B. Malleson",
            "🎬 'Jodhaa Akbar' (2008 film - dramatized but beautiful)",
            "🌐 metmuseum.org (search 'Mughal miniatures')"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 8: COLONIAL AMERICA - THE REVOLUTION
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "american_revolution",
        "name": "Colonial America - The Revolution",
        "year": 1775,
        "location": "Massachusetts",
        
        "image_description": """A New England colonial town in spring. Two-story wooden 
houses with white clapboard siding line a cobblestone street. Men in tricorn hats 
and knee breeches argue outside a tavern. A woman in a long dress and bonnet carries 
a basket. British redcoats are visible in the distance. A church with a tall white 
steeple dominates the skyline. Horse-drawn carts, hand-painted shop signs, no 
electricity or modern elements.""",
        
        "guess_keywords": ["colonial", "revolution", "1776", "1775", "america", "boston",
                          "18th century", "british", "independence", "1700s"],
        
        "key_events": [
            "Shots fired at Lexington and Concord - the Revolution has begun",
            "Boston is under British occupation after the Tea Party protests",
            "Colonists are divided: Patriots want independence, Loyalists support the King",
            "The Continental Congress is debating whether to declare independence",
            "Slavery exists throughout the colonies - about 20% of the population is enslaved"
        ],
        
        "figures": [
            "George Washington - Just appointed commander of the Continental Army",
            "Samuel Adams - Radical patriot organizing resistance in Boston",
            "Abigail Adams - Influential voice urging her husband John to 'remember the ladies'",
            "Crispus Attucks - Black man killed in the Boston Massacre, martyr of the cause",
            "Local British Commander - Enforcing order in occupied territory"
        ],
        
        "hard_rules": {
            "Lower": [
                "May be drafted into militia service",
                "Little say in political decisions",
                "Indentured servants have few rights until contract ends",
                "War disrupts trade and work"
            ],
            "Middle": [
                "Merchants must choose sides - affects business",
                "Property can be seized by either army",
                "Skilled workers are valuable to both sides"
            ],
            "Upper": [
                "Expected to take political positions publicly",
                "Wealth makes you a target for taxation or seizure",
                "Social connections determine safety"
            ],
            "Female": [
                "Cannot vote or hold office",
                "Property rights limited (coverture law)",
                "BUT: War creates opportunities as men leave",
                "Can influence through 'Republican Motherhood' ideal"
            ],
            "Enslaved": [
                "No legal rights whatsoever",
                "Can be sold at any time",
                "British offer freedom to those who escape and join them",
                "Some Patriots promise freedom for military service"
            ]
        },
        
        "adult_hard_rules": {
            "Enslaved": [
                "Whipping, branding, mutilation legal punishments",
                "Families separated at auction",
                "Sexual abuse of enslaved women pervasive",
                "Runaways face torture or death if caught"
            ],
            "Female": [
                "Rape by occupying soldiers on both sides",
                "Domestic violence legal within marriage"
            ]
        },
        
        "adult_events": [
            "Tarring and feathering of Loyalists - hot tar burns skin off",
            "Enslaved people branded on the face for running away",
            "Soldiers on both sides rape women in occupied areas",
            "Battlefield wounds lead to agonizing deaths or amputations without anesthesia"
        ],
        
        "agency_windows": [
            "Choosing the winning side early = advantage later",
            "Skills in demand (blacksmith, nurse, spy) create leverage",
            "Women can run businesses while husbands fight",
            "Enslaved people: British lines may offer freedom (risky but possible)",
            "Information is power - those who hear news first can act"
        ],
        
        "debrief_facts": [
            "About 1/3 of colonists were Patriots, 1/3 Loyalists, 1/3 neutral",
            "More Americans died from disease than from battle during the war",
            "Women like Deborah Sampson disguised themselves as men to fight",
            "About 5,000 Black soldiers fought for the Continental Army",
            "The British promised freedom to enslaved people who joined them - about 20,000 did",
            "Many Loyalists fled to Canada after the war - losing everything"
        ],
        
        "real_people": [
            {
                "name": "Deborah Sampson (1760-1827)",
                "description": "Disguised herself as a man named 'Robert Shurtliff' and served in the Continental Army for over a year. She was wounded twice and treated her own wounds to avoid discovery. Later became one of the first women to go on a lecture tour in America."
            },
            {
                "name": "James Armistead Lafayette (1748-1830)",
                "description": "An enslaved man who became one of the most important spies of the Revolution. He worked as a double agent, pretending to spy for the British while actually feeding information to the Americans. He was granted freedom for his service."
            },
            {
                "name": "Phillis Wheatley (1753-1784)",
                "description": "Brought to America as an enslaved child, she became the first African American to publish a book of poetry. Her work was used by abolitionists as proof that Black people were fully capable of intellectual achievement."
            }
        ],
        
        "resources": [
            "📖 'Chains' by Laurie Halse Anderson (historical fiction, ages 10+)",
            "📖 'George vs. George' by Rosalyn Schanzer (accessible comparison)",
            "🎬 'Liberty's Kids' animated series (PBS, free online)",
            "🌐 americanrevolution.org"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 9: INDUSTRIAL BRITAIN - FACTORY AGE
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "industrial_britain",
        "name": "Industrial Britain - The Factory Age",
        "year": 1842,
        "location": "Manchester, England",
        
        "image_description": """A Manchester street at midday, shrouded in coal smoke. 
Tall brick factory chimneys belch black smoke against a gray sky. Workers in caps 
and shawls stream through iron gates. Children as young as eight carry bundles. 
A well-dressed factory owner in a top hat passes a beggar. Horse-drawn carts share 
streets with early railways. Gaslight lamps line the street. Row houses with tiny 
windows crowd together. No cars, no electricity lines, Victorian industrial aesthetic.""",
        
        "guess_keywords": ["industrial", "victorian", "britain", "1800s", "factory",
                          "manchester", "dickens", "19th century", "england", "child labor"],
        
        "key_events": [
            "The Industrial Revolution has transformed Britain into the 'workshop of the world'",
            "Factory work has replaced farming for millions - cities grow explosively",
            "Child labor is common - children as young as 5 work in factories and mines",
            "Chartists demand voting rights for working men - protests are growing",
            "Ireland is about to suffer the Great Famine - refugees will flood English cities"
        ],
        
        "figures": [
            "Factory Owners - The new wealthy class, building fortunes on cotton and coal",
            "Factory Workers - Men, women, and children working 14-hour days",
            "Chartist Leaders - Demanding political rights for working people",
            "Parish Officials - Administering poor relief (badly)",
            "Reformers - Like Lord Shaftesbury, fighting to limit child labor"
        ],
        
        "hard_rules": {
            "Lower": [
                "Work or starve - no unemployment insurance exists",
                "Factory hours: 12-16 hours a day, 6 days a week",
                "Children can legally work from age 9 (younger in practice)",
                "Workplace injuries common, no compensation",
                "Fired workers may end up in the workhouse"
            ],
            "Middle": [
                "Clerks and shopkeepers live better but work long hours",
                "Respectability is everything - scandal ruins careers",
                "Some path to advancement through education"
            ],
            "Upper": [
                "Factory owners and merchants are the new elite",
                "Old aristocracy looks down on 'new money'",
                "Expected to practice charity (but on their own terms)"
            ],
            "Female": [
                "Working-class women work in factories and domestic service",
                "Middle-class women are confined to the home",
                "Cannot vote or hold property if married",
                "Prostitution is common among desperate women"
            ]
        },
        
        "adult_hard_rules": {
            "Lower": [
                "Children's limbs torn off by machines - common occurrence",
                "Workhouse conditions designed to be worse than starvation",
                "Mine collapses bury workers alive",
                "Phossy jaw rots faces off match factory workers"
            ],
            "Female": [
                "Prostitution often the only option for unemployed women",
                "Factory owners sexually exploit female workers",
                "Childbirth without medical care kills many"
            ]
        },
        
        "adult_events": [
            "Chimney sweep boys as young as 4 get stuck and suffocate in flues",
            "Cholera epidemics kill thousands in slum conditions",
            "The Irish Famine drives starving refugees to English cities",
            "Bodies of paupers sold to medical schools for dissection"
        ],
        
        "agency_windows": [
            "Education (Sunday schools, Mechanics' Institutes) offers advancement",
            "Skilled trades pay better than factory work",
            "Emigration to America or Australia offers new starts",
            "Trade unions are forming (illegally, but growing)",
            "Reform movements offer purpose and community"
        ],
        
        "debrief_facts": [
            "In 1842, the average life expectancy in Manchester was 17 years (vs 38 in rural areas)",
            "Children as young as 5 worked as chimney sweeps and in mines",
            "The Factory Act of 1833 limited child labor to 8 hours a day for ages 9-13",
            "Friedrich Engels wrote about Manchester's slums while managing his father's factory there",
            "The 'Irish Famine' (1845-1852) killed 1 million and drove millions more to emigrate",
            "Charles Dickens' novels (Oliver Twist, Hard Times) drew attention to these conditions"
        ],
        
        "real_people": [
            {
                "name": "Robert Blincoe (1792-1860)",
                "description": "A workhouse orphan sent to work in cotton mills at age 7. His memoir described the brutal conditions child workers faced - beatings, maiming, starvation. It helped inspire factory reform laws."
            },
            {
                "name": "Lord Shaftesbury (1801-1885)",
                "description": "An aristocrat who devoted his life to reforming labor laws. He fought for laws limiting child labor in factories and mines. Critics called him a meddler in business affairs."
            },
            {
                "name": "Friedrich Engels (1820-1895)",
                "description": "A German businessman's son who documented Manchester's working-class conditions in 'The Condition of the Working Class in England.' He later co-wrote 'The Communist Manifesto' with Karl Marx."
            }
        ],
        
        "resources": [
            "📖 'Oliver Twist' by Charles Dickens",
            "📖 'Street Child' by Berlie Doherty (ages 9+)",
            "🎬 'The Mill' (Channel 4 series)",
            "🌐 spartacus-educational.com/industrial-revolution"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 10: AMERICAN CIVIL WAR
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "civil_war",
        "name": "American Civil War",
        "year": 1863,
        "location": "United States (Various)",
        
        "image_description": """A Union army camp at dusk. White canvas tents stretch 
across muddy fields. Soldiers in blue uniforms gather around campfires. A Black 
regiment drills in formation nearby. Wagons and ambulances crowd a dirt road. 
The American flag flies above a command tent. Artillery pieces are lined up. 
In the distance, smoke rises from a burned farmhouse. Photography equipment 
visible - this is the first photographed war. No modern military equipment.""",
        
        "guess_keywords": ["civil war", "1860s", "america", "lincoln", "slavery",
                          "union", "confederate", "1863", "gettysburg", "abolition"],
        
        "key_events": [
            "The Civil War has been raging for two years - neither side can win quickly",
            "Lincoln's Emancipation Proclamation freed enslaved people in rebel states",
            "Black soldiers are now fighting for the Union in segregated regiments",
            "The Battle of Gettysburg has just been fought - a turning point",
            "The Underground Railroad continues to help people escape to freedom"
        ],
        
        "figures": [
            "Abraham Lincoln - President, holding the Union together",
            "Frederick Douglass - Formerly enslaved orator, pushing for Black rights",
            "Harriet Tubman - Conductor of the Underground Railroad, now a Union spy",
            "Robert E. Lee - Confederate general, fighting for the South",
            "Clara Barton - Nurse on the battlefield, future founder of Red Cross"
        ],
        
        "hard_rules": {
            "Lower": [
                "Conscription: poor men fight while rich can pay substitutes",
                "Soldiers face disease more than enemy fire",
                "Desertion is punished by death",
                "Refugees and displaced people face starvation"
            ],
            "Middle": [
                "War profiteering offers opportunity for some",
                "Inflation makes money worth less every month",
                "Both sides seize property when needed"
            ],
            "Upper": [
                "Can pay $300 to avoid draft (Union) - 'rich man's war, poor man's fight'",
                "Expected to support war effort financially",
                "Confederate planters losing enslaved workers to Union lines"
            ],
            "Female": [
                "Cannot serve as soldiers (some disguise themselves)",
                "Nursing becomes acceptable 'women's work'",
                "Running farms and businesses while men are away",
                "Spying is one area where women excel"
            ],
            "Enslaved/Freedpeople": [
                "Crossing to Union lines can mean freedom - but it's dangerous",
                "Black soldiers face execution if captured by Confederates",
                "Even in Union, face discrimination and lower pay",
                "Freedom comes with no land, money, or protection"
            ]
        },
        
        "adult_hard_rules": {
            "Enslaved/Freedpeople": [
                "Captured Black soldiers executed or re-enslaved",
                "Sexual violence against enslaved women continues",
                "Confederate massacre at Fort Pillow kills surrendering Black soldiers"
            ],
            "Lower": [
                "Battlefield amputations without anesthesia",
                "Gangrene, infection kill more than bullets",
                "Prison camps like Andersonville starve prisoners to death"
            ]
        },
        
        "adult_events": [
            "Battlefield surgery - limbs sawn off while soldiers scream",
            "Andersonville prison - skeletons eating rats to survive",
            "Fort Pillow massacre - Confederate troops murder surrendering Black soldiers",
            "Sherman's March - farms burned, livestock killed, civilians displaced"
        ],
        
        "agency_windows": [
            "For enslaved people, Union lines offer path to freedom",
            "Military service offers Black men citizenship and respect",
            "Women can serve as nurses, spies, and run households",
            "Skills in medicine, logistics are desperately needed",
            "Literacy and education prepare freedpeople for new life"
        ],
        
        "debrief_facts": [
            "620,000-750,000 soldiers died - more than all other American wars combined until Vietnam",
            "Black soldiers made up about 10% of the Union Army by war's end",
            "Disease killed twice as many soldiers as combat",
            "About 400 women are documented to have disguised themselves as men to fight",
            "The 54th Massachusetts (Black regiment) became famous for its assault on Fort Wagner",
            "The 13th Amendment abolished slavery in 1865, but 'Black Codes' and sharecropping followed"
        ],
        
        "real_people": [
            {
                "name": "Harriet Tubman (c. 1822-1913)",
                "description": "After escaping slavery, she returned South 13 times to lead others to freedom. During the war, she served as a spy and scout for the Union Army and led a raid that freed over 700 enslaved people."
            },
            {
                "name": "Robert Smalls (1839-1915)",
                "description": "An enslaved ship pilot who commandeered a Confederate vessel and delivered it to the Union Navy - with his family aboard. He later became a U.S. Congressman during Reconstruction."
            },
            {
                "name": "Clara Barton (1821-1912)",
                "description": "A clerk who became a battlefield nurse, bringing supplies directly to wounded soldiers. She was called 'the angel of the battlefield' and later founded the American Red Cross."
            }
        ],
        
        "resources": [
            "📖 'Lincoln: A Photobiography' by Russell Freedman (Newbery winner)",
            "📖 'Soldier's Heart' by Gary Paulsen",
            "🎬 'Glory' (1989 film about the 54th Massachusetts)",
            "🌐 civilwar.org"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 11: WORLD WAR II - OCCUPIED EUROPE
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "ww2_europe",
        "name": "World War II - Occupied Europe",
        "year": 1943,
        "location": "Netherlands",
        
        "image_description": """A European city street in the 1940s. Old brick buildings, 
some showing minor damage. People in 1940s clothing hurry past - women in modest 
dresses and headscarves, men in worn suits. A bicycle leans against a building. 
Posters on walls (text not visible). Windows have tape in X patterns (air raid 
protection). No cars, but a horse-drawn cart in background. Gray, overcast sky. 
A German soldier visible in the distance.""",
        
        "guess_keywords": ["ww2", "wwii", "1940s", "world war", "nazi", "1943", "1944",
                          "occupation", "europe", "netherlands", "holland", "resistance"],
        
        "key_events": [
            "Nazi Germany occupies the Netherlands - life is controlled, Jews are being deported",
            "The tide is turning: Germany lost at Stalingrad, Allies planning invasion",
            "Resistance networks are hiding people and gathering intelligence",
            "Food is rationed - everyone is hungry, black market thrives",
            "The Holocaust is underway - Jews, Roma, disabled people are being murdered"
        ],
        
        "figures": [
            "Anne Frank - A Jewish girl your age, hiding in Amsterdam right now",
            "Dutch Resistance members - Ordinary people risking everything",
            "German occupation forces - Soldiers, police, administrators",
            "NSB collaborators - Dutch people who support the Nazis",
            "Queen Wilhelmina - In exile in London, broadcasting hope via radio"
        ],
        
        "hard_rules": {
            "Lower": [
                "Food rations are barely enough to survive",
                "May be conscripted for forced labor in Germany",
                "Less likely to be suspected - 'invisible' to authorities"
            ],
            "Middle": [
                "Must be careful about political statements at work",
                "Radio ownership is registered - listening to BBC is illegal",
                "Some resources to help others or help yourself"
            ],
            "Upper": [
                "More visible to authorities - must choose side carefully",
                "Wealth can buy safety or make you a target",
                "Expected to collaborate or visibly resist"
            ],
            "Female": [
                "Less likely to be searched at checkpoints",
                "Often used as resistance couriers for this reason",
                "Traditional expectations but war creates new roles"
            ],
            "Jewish": [
                "Must wear yellow star",
                "Banned from most jobs, schools, public places",
                "Subject to deportation to concentration camps",
                "Only survival option: hiding or escape"
            ]
        },
        
        "adult_hard_rules": {
            "Jewish": [
                "Deportation means death - gas chambers at Auschwitz, Sobibor",
                "Families separated at selection - children sent directly to death",
                "Medical experiments on living prisoners"
            ],
            "Female": [
                "German soldiers assault women during raids",
                "Jewish women in camps face sexual violence",
                "Resistance women tortured if captured"
            ],
            "Lower": [
                "Forced laborers work to death in German factories",
                "Hunger Winter kills through starvation and cold"
            ]
        },
        
        "adult_events": [
            "Gas chambers at Auschwitz process thousands per day",
            "Gestapo torture includes beatings, drowning, electric shocks",
            "The Hunger Winter - Dutch eat tulip bulbs, cats, rats to survive",
            "Reprisal executions - civilians shot for resistance actions"
        ],
        
        "agency_windows": [
            "Young women and teenagers make effective couriers - less suspected",
            "Knowledge of safe houses and escape routes is power",
            "Radio access = information = better decisions",
            "Timing matters: acting before roundups = survival",
            "Skills in demand (nursing, forgery, languages) create options"
        ],
        
        "debrief_facts": [
            "About 75% of Dutch Jews (102,000 people) were killed - highest rate in Western Europe",
            "About 25,000-30,000 Jews were hidden by Dutch families; roughly 16,000 survived",
            "The Hunger Winter of 1944-45 killed 20,000+ Dutch civilians through starvation",
            "Anne Frank hid for 2 years before being betrayed; she died weeks before liberation",
            "Canadian forces liberated the Netherlands in May 1945",
            "The Dutch still send Canada tulips every year in gratitude"
        ],
        
        "real_people": [
            {
                "name": "Anne Frank (1929-1945)",
                "description": "A Jewish girl who hid with her family in a secret annex in Amsterdam for over 2 years. Her diary, found after the war, became one of the most important documents of the Holocaust. She died in Bergen-Belsen concentration camp at age 15, just weeks before liberation."
            },
            {
                "name": "Hannie Schaft (1920-1945)",
                "description": "A Dutch resistance fighter who helped hide Jews and participated in armed resistance. Known as 'the girl with the red hair,' she was captured and executed just three weeks before liberation. She was 24 years old."
            },
            {
                "name": "Miep Gies (1909-2010)",
                "description": "One of the helpers who hid Anne Frank's family. After the raid, she preserved Anne's diary. When asked why she risked her life, she said: 'I am not a hero. I just did what any decent person would do.' She lived to be 100."
            }
        ],
        
        "resources": [
            "📖 'The Diary of Anne Frank' - Anne Frank (essential reading)",
            "📖 'Number the Stars' by Lois Lowry (fiction, ages 9+)",
            "🎬 'Anne Frank: Parallel Stories' documentary (2019)",
            "🌐 annefrank.org - Virtual tour of the hiding place"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 12: WORLD WAR II - AMERICAN HOME FRONT
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "ww2_pacific",
        "name": "World War II - American Home Front",
        "year": 1943,
        "location": "California",
        
        "image_description": """An American factory scene in the 1940s. Women in 
overalls and headscarves work at an assembly line. 'We Can Do It!' style posters 
on walls. Victory garden visible through a window. Men in military uniforms pass 
through. Cars from the 1940s in parking lot. American flags displayed prominently.
Rationing posters visible. Sense of wartime urgency and purpose.""",
        
        "guess_keywords": ["ww2", "wwii", "1940s", "america", "home front", "factory",
                          "rosie", "california", "pacific", "internment"],
        
        "key_events": [
            "America is fighting on two fronts: Europe and the Pacific against Japan",
            "Japanese Americans on the West Coast have been forced into internment camps",
            "Women are working in factories in huge numbers - 'Rosie the Riveter'",
            "Everything is rationed: food, gas, rubber, metal",
            "Gold Star families mourn sons lost overseas; everyone knows someone fighting"
        ],
        
        "figures": [
            "Franklin D. Roosevelt - President leading the war effort",
            "Japanese American families - 120,000 people forcibly relocated",
            "Women factory workers - Doing 'men's work' for the first time",
            "Soldiers on leave - Home briefly before shipping out",
            "Local draft board - Deciding who fights and who stays"
        ],
        
        "hard_rules": {
            "Lower": [
                "Rationing hits harder - less money for black market",
                "Factory work is available but dangerous",
                "Military service offers steady pay and benefits"
            ],
            "Middle": [
                "Expected to buy war bonds, support the effort",
                "Gasoline rationing limits mobility",
                "Some jobs are 'essential' - exemption from draft"
            ],
            "Upper": [
                "Wealth doesn't exempt from draft, but connections help",
                "Expected to lead community war efforts",
                "Business opportunities in war production"
            ],
            "Female": [
                "Factory jobs open that were closed before",
                "Pay is lower than men for same work",
                "Expected to return to home after war",
                "Nursing overseas is an option"
            ],
            "Japanese American": [
                "Subject to forced relocation regardless of citizenship",
                "Lost homes, businesses, everything",
                "Can prove loyalty through military service (442nd regiment)",
                "Face racism from fellow Americans"
            ]
        },
        
        "adult_hard_rules": {
            "Japanese American": [
                "Suicide among internees from shame and despair",
                "Shot for approaching camp fences",
                "Families destroyed by stress of imprisonment"
            ],
            "Lower": [
                "Industrial accidents maim and kill workers",
                "War casualties devastate families"
            ],
            "Female": [
                "Sexual harassment in factories common",
                "War brides face abuse from traumatized veterans"
            ]
        },
        
        "adult_events": [
            "Pacific combat is especially brutal - mutilation of enemy dead",
            "Factory accidents crush, burn, maim workers",
            "War neurosis (PTSD) destroys returning soldiers",
            "Atomic bombs will kill 200,000+ in Japan"
        ],
        
        "agency_windows": [
            "Factory skills = steady income and war contribution",
            "Military service: choose branch/role when possible",
            "War bonds and scrap drives = community standing",
            "For Japanese Americans: 442nd regiment offers path to prove loyalty",
            "Nursing or USO work allows women to serve overseas"
        ],
        
        "debrief_facts": [
            "120,000 Japanese Americans were forcibly relocated to internment camps",
            "The 442nd Infantry Regiment (Japanese American) became the most decorated unit in U.S. history",
            "6 million American women entered the workforce during the war",
            "After the war, most women were pushed out of factory jobs to make room for returning men",
            "It took until 1988 for the U.S. government to formally apologize for internment",
            "About 400,000 Americans died in WWII"
        ],
        
        "real_people": [
            {
                "name": "Fred Korematsu (1919-2005)",
                "description": "A Japanese American who refused to go to an internment camp and was arrested. He fought his case to the Supreme Court and lost, but in 1983 his conviction was finally overturned. He received the Presidential Medal of Freedom in 1998."
            },
            {
                "name": "Daniel Inouye (1924-2012)",
                "description": "Joined the 442nd regiment despite his family being in an internment camp. Lost his arm in combat and was awarded the Medal of Honor. Later became a U.S. Senator from Hawaii for 50 years."
            },
            {
                "name": "Rosie the Riveter (symbol)",
                "description": "A cultural icon representing the millions of women who worked in factories during the war. Based on several real women, including Rose Will Monroe. The image became a symbol of women's capability and later of feminism."
            }
        ],
        
        "resources": [
            "📖 'Farewell to Manzanar' by Jeanne Wakatsuki Houston (ages 11+)",
            "📖 'The War That Saved My Life' by Kimberly Brubaker Bradley",
            "🎬 'Come See the Paradise' (1990 film about internment)",
            "🌐 Densho.org - Japanese American WWII history"
        ]
    },
    
    # ═══════════════════════════════════════════════════════════════════
    # ERA 13: INDIAN INDEPENDENCE - PARTITION
    # ═══════════════════════════════════════════════════════════════════
    {
        "id": "indian_partition",
        "name": "Indian Independence - Partition",
        "year": 1947,
        "location": "Punjab (India/Pakistan border)",
        
        "image_description": """A train station in Punjab, August 1947. Crowds of 
people with bundles and children press toward overcrowded trains. Sikh men in 
turbans, Muslim women in burqas, Hindu families in saris all mixed together. 
British soldiers stand uncertain. Hand-painted signs announce 'Pakistan' and 
'Hindustan.' Ox-carts loaded with belongings line the road. Smoke rises from 
distant villages. The atmosphere is tense, fearful. 1940s Indian subcontinent 
aesthetic - no modern vehicles.""",
        
        "guess_keywords": ["india", "pakistan", "partition", "1947", "independence",
                          "gandhi", "british", "punjab", "refugee", "nehru"],
        
        "key_events": [
            "After 200 years, British rule is ending - India will be independent",
            "The country is being partitioned into Hindu-majority India and Muslim-majority Pakistan",
            "Punjab and Bengal are being divided - millions must choose which side to live on",
            "Communal violence is exploding - Hindus, Muslims, and Sikhs are killing each other",
            "The largest mass migration in history is underway - 14 million people displaced"
        ],
        
        "figures": [
            "Mahatma Gandhi - Apostle of nonviolence, fasting to stop the killing",
            "Jawaharlal Nehru - Soon to be India's first Prime Minister",
            "Muhammad Ali Jinnah - Leader of the Muslim League, father of Pakistan",
            "Lord Mountbatten - Last Viceroy, rushing partition with fatal speed",
            "Ordinary families - Trying to survive the chaos"
        ],
        
        "hard_rules": {
            "Lower": [
                "Refugees lose everything - land, homes, possessions",
                "Walking hundreds of miles with nothing",
                "Trains are being attacked - some arrive full of corpses",
                "No one knows where the border will be until it's announced"
            ],
            "Middle": [
                "Property on the 'wrong' side is lost forever",
                "Some have resources to flee early or bribe passage",
                "Business networks can help find safety"
            ],
            "Upper": [
                "More resources to escape but also bigger targets",
                "Political connections may help or hurt",
                "Expected to protect dependents and community"
            ],
            "Female": [
                "Women targeted for abduction and violence",
                "Some families kill daughters rather than let them be captured",
                "'Honor' concerns affect rescue and recovery",
                "Widows left with nothing"
            ]
        },
        
        "adult_hard_rules": {
            "Female": [
                "Mass rape used as weapon by all sides",
                "Women's bodies mutilated with religious symbols",
                "Forced conversion through marriage to captors",
                "Suicide or family murder to prevent 'dishonor'"
            ],
            "Lower": [
                "Train massacres leave thousands dead",
                "Entire villages slaughtered",
                "Refugee camps become death traps"
            ]
        },
        
        "adult_events": [
            "Trains of corpses arrive at stations - entire passenger lists murdered",
            "Women's breasts cut off, religious slogans carved into bodies",
            "Mass rapes - estimates of 75,000-100,000 women abducted",
            "Fathers killing daughters to 'save their honor'",
            "Wells filled with women who jumped in rather than be captured"
        ],
        
        "agency_windows": [
            "Early information about violence = time to flee",
            "Mixed-religion friendships can mean protection",
            "Those who stay calm and plan survive better than panicked flight",
            "Helping others can build networks of mutual aid",
            "Skills (medical, mechanical) are valuable in chaos"
        ],
        
        "debrief_facts": [
            "Partition killed between 200,000 and 2 million people in communal violence",
            "14 million people were displaced - the largest mass migration in history",
            "The border was drawn by a British lawyer who had never been to India",
            "Gandhi was assassinated in January 1948 by a Hindu nationalist angry at his tolerance",
            "Many families were separated and never reunited",
            "India and Pakistan have fought four wars since partition"
        ],
        
        "real_people": [
            {
                "name": "Mahatma Gandhi (1869-1948)",
                "description": "The leader of Indian independence through nonviolent resistance. During partition, he walked through riot-torn areas and fasted to stop the killing. He was assassinated five months after independence by a Hindu extremist."
            },
            {
                "name": "Bhisham Sahni (1915-2003)",
                "description": "A writer who witnessed partition in Punjab. His novel 'Tamas' (Darkness) and short story 'Amritsar Aa Gaya' capture the horror and humanity of those days. He saw neighbors become killers - and protectors."
            },
            {
                "name": "Urvashi Butalia (b. 1952)",
                "description": "A historian whose family was divided by partition. Her book 'The Other Side of Silence' collected oral histories from survivors, including stories of women who were abducted and those who protected people across religious lines."
            }
        ],
        
        "resources": [
            "📖 'The Night Diary' by Veera Hiranandani (ages 10+)",
            "📖 'Tamas' by Bhisham Sahni (for older readers)",
            "🎬 'Partition: 1947' (2017 film)",
            "🎬 'Train to Pakistan' (1998 film)",
            "🌐 1947partitionarchive.org - Oral histories"
        ]
    }
]


def get_era_by_id(era_id):
    """Get a specific era by ID"""
    for era in ERAS:
        if era['id'] == era_id:
            return era
    return None


def get_random_era():
    """Get a random era"""
    import random
    return random.choice(ERAS)


def get_hard_rules_for_persona(era, persona, include_adult=False):
    """
    Get applicable hard rules for a specific persona in an era.
    
    Args:
        era: Era dictionary
        persona: Persona object
        include_adult: Whether to include adult content
    """
    rules = []
    
    # Class-based rules
    class_rules = era['hard_rules'].get(persona.social_class, [])
    rules.extend(class_rules)
    
    # Sex-based rules
    if persona.sex == 'Female':
        female_rules = era['hard_rules'].get('Female', [])
        rules.extend(female_rules)
    
    # Adult content if enabled
    if include_adult and 'adult_hard_rules' in era:
        adult_class_rules = era['adult_hard_rules'].get(persona.social_class, [])
        rules.extend(adult_class_rules)
        
        if persona.sex == 'Female':
            adult_female_rules = era['adult_hard_rules'].get('Female', [])
            rules.extend(adult_female_rules)
    
    return rules


def get_era_events(era, include_adult=False):
    """Get key events for an era, optionally including adult content"""
    events = era['key_events'].copy()
    
    if include_adult and 'adult_events' in era:
        events.extend(era['adult_events'])
    
    return events
