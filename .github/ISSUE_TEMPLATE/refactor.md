---
name: Refactoring
about: Hvis du ser en del af koden der kunne være lavet anderledes
title: "[Refactor]"
labels: refactor
assignees: ''
---

## Hvad skal refactors og hvorfor?

(Slet eksempel og udfyld)

Lige nu ligger alle admin filer i en [stor fil](https://github.com/CodingPirates/forenings_medlemmer/blob/867eed2746085c0eb93ef94583496c805aef98c4/members/admin.py),
det gør den uoverskuelig og svær at vedligeholde. Ved at splitte den op ville
det være nemmere at kode fremadrettet.

## Beskrivelse af det nye design

1. Lav en admin mappe
2. Lav en `admin/__init__.py`
3. Lav en fil til hver admin klasse
4. Registrer den i `admin/__init__.py`
5. Test alle til sidst.
