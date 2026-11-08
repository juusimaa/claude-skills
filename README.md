# suomi-skills

Suomalaisiin palveluihin ja paikkakuntiin liittyviä skillejä [Claude Codelle](https://claude.com/claude-code).

## Skillit

| Skilli | Kuvaus |
|---|---|
| [keikat](skills/keikat/SKILL.md) | Hakee lähiaikojen musiikkikeikat Oulusta (Tiketti, Tarkastamo, Tullisali, Tuba, Songkick ym.) taulukoksi hintoineen ja loppuunmyyntitietoineen. Kutsu: `/keikat` (1 kk) tai esim. `/keikat 3kk` (1–12 kk). |

## Asennus

Kloonaa repo ja linkitä haluamasi skilli Clauden skill-kansioon:

```bash
git clone https://github.com/juusimaa/suomi-skills.git
ln -s "$PWD/suomi-skills/skills/keikat" ~/.claude/skills/keikat
```

Skriptit tarvitsevat vain Python 3:n standardikirjaston.

## Rakenne

Jokainen skilli on omassa kansiossaan `skills/<nimi>/`. Kansion juuressa on `SKILL.md` ja tarvittaessa `scripts/`-kansio apuskripteille.
