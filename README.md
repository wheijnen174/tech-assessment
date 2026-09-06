# Tech Assessment

*Vanwege privacy-gevoelige data is de bijbehorende data niet geüpload.*

## Vereisten

- Python 3.12 of hoger
- uv

## Installatie

Pak het ZIP-bestand uit.

Installeer vervolgens de benodigde dependencies: ``uv sync``

## Uitvoeren

Start de applicatie vanuit de hoofdmap van het project: ``uv run src/main.py``

De applicatie leest de CSV-bestanden uit de ``data/`` map en schrijft de gegenereerde resultaten naar de ``output/`` map.

## Aannames

- Scores zonder ingevulde waarde worden buiten beschouwing gelaten.
- Scores die niet gekoppeld kunnen worden aan een student+groep worden buiten beschouwing gelaten.
   - Dit betreft 35,8% van de scores uit ``bron_2``, doordat deze scoreWs afkomstig zijn van datums die buiten de groepsindeling in ``bron_1`` vallen.
