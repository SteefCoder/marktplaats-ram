# marktplaats-ram
Een programma om de RAM-prijzen op marktplaats bij te houden.


## Marktplaats API
Marktplaats gebruikt intern een API voor hun website. Daar kunnen we gebruik van maken.
https://www.marktplaats.nl/lrp/api

Deze API is alleen voor gebruik vanaf de website, dus we moeten altijd headers toevoegen om ons voor te doen als website.
```py
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
    "Host": "www.marktplaats.nl",
}
```
Dit kan je natuurlijk ook vervangen door de `User-Agent` tag van je eigen browser. Zonder deze headers zul je een `Not-Allowed` response krijgen.

### /search
Dit is de endpoint die ik gebruik (er zullen ook vast genoeg andere zijn, maar die zijn niet zo interessant hiervoor).
Je hebt een aantal opties voor de url parameters, onder andere:

`query`
(string, optional). Dit is de term waar je op wil zoeken, spreekt voor zich denk ik.

`searchInTitleAndDescription`
(bool, optional). Of je met de query ook in de description wil zoeken (denk ik, weet ik niet zeker).

`attributesByKey[]`
(string, required). Een aantal attributes die je kan instellen, onder andere:
- `"offeredSince: [Vandaag|Gisteren|Deze week|Altijd]"`

`l1CategoryId`
(integer, optional). De ID van de hoofdcategorie waar je op wil zoeken. Voor ons `322` = Computers en Software.

`l2CategoryId`
(integer, optional). De ID van de subcategorie waar je op wil zoeken. Voor ons `331` = RAM geheugen.

`limit`
(integer, required). Maximale aantal resultaten dat gegeven wordt. Is maximaal 150 ofzo geloof ik.

`offset` (integer, required). Moet een meervoud van `limit` zijn.

`viewOptions` (string, optional). Geen idee wat dit doet.
