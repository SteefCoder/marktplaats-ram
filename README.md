# marktplaats-ram
Een programma om de RAM-prijzen op marktplaats bij te houden.


## Marktplaats API
Marktplaats gebruikt intern een API voor hun website. Daar kunnen we gebruik van maken.
https://www.marktplaats.nl/lrp/api

Deze API is alleen voor gebruik vanaf de website, dus we moeten altijd headers toevoegen om ons voor te doen als website. Ook willen we zo min mogelijk requests gebruiken.
Standaard doen we een delay van 15 seconden tussen iedere request.


## Updatecyclus
Om de laatste stand van zaken op Marktplaats bij te houden vragen we regelmatig de lijst met advertenties op. Er zijn in totaal zo'n 6000-7000 advertenties. Ook is er een limiet van 100 advertenties per pagina (request). Dat betekent dat we om alles op te vragen zo'n 60 tot 70 requests nodig hebben. Al zouden we dat ieder uur willen doen, zitten we zo op de 1400 requests per dag en 43k requests per maand. Dat is niet zo aardig voor de servers van Marktplaats. Daarom limiteren we onze requests zo:

Iedere twee uur - alles sinds gisteren.
Iedere zes uur - alles sinds eergisteren.
Iedere dag - alles sinds afgelopen week.
Iedere twee dagen - alles sinds afgelopen maand.
Iedere vier dagen - alles in het afgelopen jaar.

Dit is vrij relaxed en het kan nog meer of minder. Als laatste stoppen we nog met het maken van de uurlijke requests tussen 10 uur 's avonds en 6 uur 's ochtends, omdat er dan toch niets gebeurt. 

Het doel van de requests is om

1. Alle informatie over de advertenties te krijgen (en geen advertenties te missen).
2. Te weten wanneer een advertentie gepost is (tot op twee uur accuraat dus).
3. Te weten wanneer een advertentie is weggehaald (door een verkoop of andersinds, van twee uur tot op 4 dagen accuraat afhankelijk van de duur).

Dit geeft een inzicht in het vraag en aanbod van werkgeheugen op Marktplaats.


## Informatie verwerken

Uit de titel en beschrijving van een advertentie kan vaak worden opgemaakt om wat voor werkgeheugen het gaat. De volgende informatie wordt gepoogd er uit te halen:

- De generatie (DDR tot DDR5)
- De totale hoeveelheid (in GB)
- Het aantal sticks te koop
- De capaciteit van een stick
- De snelheid (in mt/s)
- De latency

Hier kan dan weer wat gedaan mee worden.