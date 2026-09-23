# TapeBackup.org translation rules and glossary

Read this in full before translating. It applies to German (de), French (fr), Italian (it), Spanish (es), Dutch (nl) and Polish (pl). The reader is an IT professional buying or running LTO tape backup: sysadmins, storage engineers, IT managers, procurement. Write the way that reader writes and searches, not the way a marketing agency would.

## The format you are translating

Each segment is one piece of page text with its markup and numbers replaced by tokens:

- `<a1>`, `</a1>`, `<b2>`, `</b2>`, `<s3>`, `</s3>`, `<i4>`, `<br5/>`, `<in6/>` ... are inline tags (a = link, b = bold, s = span, i = italic, br = line break, in = form input). Keep every token exactly once, spelled exactly as in the source. You may move a pair (opening and closing together) to wherever the translated words sit, but never drop, duplicate, rename or unbalance one.
- `{0}`, `{1}`, ... are numbers, prices, dates, part numbers or product generations (e.g. `{0}` might be "LTO-9", "$92.45", "18" or "2026"). Keep every one exactly once. Reorder freely to fit your grammar. Never write digits yourself and never add a currency symbol or unit next to a placeholder unless the English has one; the page fills in local number formats (92,45 €) automatically.
- `{gen}`, `{n}`, `{tb}`, `{media}`, `{drive}`, `{total}`, `{v}` are script variables in the calculator and software finder. Same rule: keep each exactly once.
- `&amp;` is an ampersand. Keep it as `&amp;`.
- The `example` field shows the English with real values filled in, so you can see what `{0}` stands for. Translate the `key`, not the example.

Return a JSON object mapping each segment `id` to its translated `key`.

## Register and tone

| | Address | Notes |
|---|---|---|
| de | Sie | Formal, direct. Prefer German word order over English calques. |
| fr | vous | Formal. Use "To", "Go", "Mo/s" for TB, GB, MB/s (French units). Non-breaking spaces are added automatically; don't type them. |
| it | impersonal or voi | Avoid "Lei". Use impersonal constructions ("si consiglia") or plural "voi" in instructions. |
| es | usted | Formal, Spain Spanish (not Latin American). |
| nl | u | Formal but plain. Dutch IT readers accept English tech terms; don't force Dutch words nobody uses. |
| pl | impersonal or Państwo | Prefer impersonal forms ("warto", "należy") over direct address. |

- Keep sentences as short and plain as the English. No marketing filler, no exclamation marks, no rhetorical questions that are not in the source.
- Do not use em dashes or en dashes as punctuation. Use a comma, colon, semicolon or a new sentence.
- Headings stay headings: short, no full stop.
- Keep British/American neutrality: translate meaning, not idiom.

## Length limits

- Segments with context `title`, `meta og:title`, `meta twitter:title`: the final text (with values filled in) must be 60 characters or fewer, including the " | TapeBackup" or " | TapeBackup.org" suffix if present. Shorten by dropping words, not by abbreviating into nonsense. Keep the product term (e.g. "LTO-9") and the year.
- Segments with context `meta description`, `meta og:description`, `meta twitter:description`: 155 characters or fewer.
- The same English text appears as a title, an og:title and a twitter:title; it is one segment, translate it once.

## Never translate

- Brand and site names: TapeBackup, TapeBackup.org, LTO Tape Info.
- Product and company names: LTO, Ultrium, LTFS, WORM (the acronym), HPE, IBM, Dell, Quantum, Fujifilm, Sony, MagStor, Symply, Overland, Tandberg, Qualstar, Catalogic DPX, Veeam (Veeam Backup & Replication, Veeam for Microsoft 365), Commvault, Nakivo, Acronis, CloudCasa, Bacula, AWS, Amazon S3, S3 Glacier Deep Archive, S3 Glacier Flexible Retrieval, Azure Blob Storage, Google Cloud Storage, Backblaze B2, Wasabi, StoreEver, PowerVault, Microsoft 365, NDMP, SAS, HBA, Fibre Channel, Thunderbolt, NAS, SSD, HDD, RAID, AES-256, NVMe, API, CPU.
- Seller names (Tape4Backup, LTO World, BackupWorks, TapeandMedia, Alternate, LDLC, Senetic, ...) and part numbers.
- "LTO Program" is the name of the consortium; keep it in English.
- Acronyms RTO, RPO, TCO, SLA stay as they are; you may expand once in brackets if the English does.

## Glossary

Use these renderings consistently. Where two are given, the first is preferred in running text.

| English | de | fr | it | es | nl | pl |
|---|---|---|---|---|---|---|
| tape (the medium) | Band, Tape | bande | nastro | cinta | tape | taśma |
| LTO tape (product) | LTO-Band | bande LTO | nastro LTO | cinta LTO | LTO-tape | taśma LTO |
| cartridge | Kassette, LTO-Kassette | cartouche | cartuccia | cartucho | cartridge | kaseta |
| data cartridge | Datenkassette | cartouche de données | cartuccia dati | cartucho de datos | datacartridge | kaseta z danymi |
| WORM cartridge | WORM-Kassette | cartouche WORM | cartuccia WORM | cartucho WORM | WORM-cartridge | kaseta WORM |
| tape drive | Bandlaufwerk | lecteur de bandes | unità a nastro | unidad de cinta | tapedrive | napęd taśmowy |
| internal drive | internes Laufwerk | lecteur interne | unità interna | unidad interna | interne drive | napęd wewnętrzny |
| external / desktop drive | externes Laufwerk, Desktop-Laufwerk | lecteur externe | unità esterna | unidad externa | externe drive | napęd zewnętrzny |
| half-height | Half-Height (HH) | demi-hauteur | mezza altezza | media altura | half-height | połówkowej wysokości (HH) |
| full-height | Full-Height (FH) | pleine hauteur | altezza piena | altura completa | full-height | pełnej wysokości (FH) |
| tape library | Bandbibliothek, Tape-Library | bibliothèque de bandes | libreria a nastro | biblioteca de cintas | tapebibliotheek | biblioteka taśmowa |
| autoloader | Autoloader | chargeur automatique | autoloader | autocargador | autoloader | autoloader |
| generation (LTO-9 etc.) | Generation | génération | generazione | generación | generatie | generacja |
| native capacity | native Kapazität | capacité native | capacità nativa | capacidad nativa | native capaciteit | pojemność natywna |
| compressed | komprimiert | compressé | compressa | comprimida | gecomprimeerd | skompresowana |
| cost per TB | Kosten pro TB | coût par To | costo per TB | coste por TB | kosten per TB | koszt za TB |
| per native TB | pro nativem TB | par To natif | per TB nativo | por TB nativo | per native TB | za natywny TB |
| price tracker | Preis-Tracker | suivi des prix | monitoraggio dei prezzi | seguimiento de precios | prijstracker | monitor cen |
| price history | Preisverlauf | historique des prix | storico dei prezzi | historial de precios | prijsgeschiedenis | historia cen |
| price guide | Preisübersicht | guide des prix | guida ai prezzi | guía de precios | prijsgids | przewodnik cenowy |
| snapshot (price edition) | Stand, Ausgabe | relevé | rilevazione | edición | momentopname | zestawienie |
| seller | Händler | vendeur | rivenditore | vendedor | verkoper | sprzedawca |
| listing | Angebot | offre | offerta | oferta | aanbieding | oferta |
| listed at | angeboten für | proposé à | offerto a | a la venta por | aangeboden voor | oferowane za |
| part number | Teilenummer | référence | codice articolo | referencia | onderdeelnummer | numer katalogowy |
| multipack / 5-pack | Mehrfachpack, 5er-Pack | lot, lot de 5 | confezione, confezione da 5 | pack, pack de 5 | multipack, 5-pack | pakiet, pakiet 5 szt. |
| pricebook | Preisliste | grille tarifaire | listino prezzi | lista de precios | prijslijst | cennik |
| backup (noun) | Backup | sauvegarde | backup | copia de seguridad | back-up | kopia zapasowa |
| back up (verb) | sichern | sauvegarder | eseguire il backup | hacer copias de seguridad | back-uppen | tworzyć kopie zapasowe |
| archive | Archiv | archive | archivio | archivo | archief | archiwum |
| cold archive / cold data | Cold Archive, selten genutzte Daten | archivage froid, données froides | archivio a freddo, dati freddi | archivo en frío, datos fríos | koude archivering, koude data | archiwum zimne, zimne dane |
| air gap / air-gapped | Air Gap, physisch getrennt | air gap, isolé physiquement | air gap, isolato fisicamente | air gap, aislado físicamente | air gap, fysiek gescheiden | air gap, fizycznie odizolowany |
| offline copy | Offline-Kopie | copie hors ligne | copia offline | copia sin conexión | offline kopie | kopia offline |
| ransomware | Ransomware | ransomware | ransomware | ransomware | ransomware | ransomware |
| restore (noun) | Wiederherstellung | restauration | ripristino | restauración | herstel | przywracanie |
| retrieval (cloud) | Abruf | récupération | recupero | recuperación | ophalen | pobieranie |
| egress (cloud) | Egress, ausgehender Datenverkehr | sortie de données (egress) | traffico in uscita (egress) | salida de datos (egress) | uitgaand verkeer (egress) | transfer wychodzący (egress) |
| cloud archive tier | Cloud-Archivklasse | niveau d'archivage cloud | livello di archiviazione cloud | nivel de archivo en la nube | cloud-archiefklasse | klasa archiwalna w chmurze |
| drive (hard disk) | Festplatte | disque dur | disco rigido | disco duro | harde schijf | dysk twardy |
| disk (storage) | Festplatten, Disk | disque | disco | disco | disk | dysk |
| migration (tape) | Migration | migration | migrazione | migración | migratie | migracja |
| read back / verify | zurücklesen, verifizieren | relire, vérifier | rileggere, verificare | releer, verificar | teruglezen, verifiëren | odczytać ponownie, zweryfikować |
| VAT | MwSt. | TVA | IVA | IVA | btw | VAT |
| including VAT | inkl. MwSt. | TTC | IVA inclusa | IVA incluido | incl. btw | z VAT (brutto) |
| net price | Nettopreis | prix HT | prezzo netto (IVA esclusa) | precio sin IVA | prijs excl. btw | cena netto |
| sales tax (US) | Sales Tax (US-Umsatzsteuer) | taxe de vente américaine | imposta sulle vendite USA | impuesto sobre las ventas (EE. UU.) | Amerikaanse sales tax | amerykański podatek od sprzedaży |
| US sellers | US-Händler | vendeurs américains | rivenditori statunitensi | vendedores de EE. UU. | Amerikaanse verkopers | sprzedawcy z USA |
| Tape Q&A (site section) | Tape-Q&amp;A | Q&amp;R bandes | Domande e risposte | Preguntas y respuestas | Tape-vragen | Pytania i odpowiedzi |
| Blog | Blog | Blog | Blog | Blog | Blog | Blog |
| Get Pricebook (button) | Preisliste anfordern | Obtenir la grille tarifaire | Richiedi il listino | Solicitar lista de precios | Prijslijst opvragen | Pobierz cennik |

## Country and month names

Translate country names ("Germany", "the United States", "US") and month names normally. "September {0}" becomes "September {0}" (de), "septembre {0}" (fr), "settembre {0}" (it), "septiembre de {0}" (es), "september {0}" (nl), "wrzesień {0}" (pl, nominative) or "{0} września {1}" style when a day precedes the month (pl genitive). Dates like "{0} September {1}" become "{0}. September {1}" (de), "{0} septembre {1}" (fr), "{0} settembre {1}" (it), "{0} de septiembre de {1}" (es), "{0} september {1}" (nl), "{0} września {1}" (pl).

## Things that look translatable but are not

- Table cells that hold only a seller name or part number.
- `LTFS · WORM READY` and `ULTRIUM` (decorative cartridge label).
- Button values and ids inside tokens.
