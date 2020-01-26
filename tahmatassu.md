
# Startti viestin etsintää

Etsin mistä löytyy vari.sh tiedosto joka luo ssh yhteyden jälkeen näytettävän tervetuloviestin. Koetin ensin etsiä tiedostoa seuraavalla komennolla.

```
find / -name "vari.sh"
```

Tämä antoi tulostuksen:

```
find: "/proc/17815/task/17856/fdinfo": Lupa evätty
find: "/proc/17815/task/17856/ns": Lupa evätty
find: "/proc/17815/task/17857/fd": Lupa evätty
find: "/proc/17815/task/17857/fdinfo": Lupa evätty
```

Noh.. näistä ei ole paljoa apua, eikä minua kiinnosta virheviestit. En aluksi tajunnut näitten menevän `stderr` streamiin. Joten koitin greppailla outputtia seuraavasti.

```
find / -name "vari.sh" | grep -v 'Lupa evätty'
```

No, ei siitä ollut apua. Minulle selvisi pienen Googlettelun jälkeen,että virhe stream pitää greppailla seuraavasti. Seuraava komento ohjaa `stderr` streamin `stdout` streamiin. Joten nyt grep osaa suodattaakin tulokset oikein. Tämä on tätä magiaa.

```
find / -name "vari.sh"  2>&1 | grep -v 'Lupa evätty'
```

Tämän jälkeen suodatuksen jälkeen tiedostoja löytyi vain yksi kappale ja se oli tiedosto josta en ollut kiinnostunut.. :)

```
/home/teemuki/vari.sh
```

Noh.. mites sitten etsitään tiedostoja joissa esiintyy tietty sananen. Pienen Googlettelun jälkeen päädyin taas komentoon nimeltä `grep`. No ekalla haulla sain tietysti samat 'Lupa evätty' tulvan aikaan. Joten päädyin vähän muokkaamaan komentojani.

```
grep -r "Tassukka toivottaa" /  2>&1 | grep -v 'Lupa' | grep -v 'Laitetta tai osoitetta ei ole' | grep -v 'Laitetta ei ole' | grep -v 'Toiminto ei ole sallittu'
```

Poimin yhden sanan parren jonka tiesin tiedostosta löytyvän. Osalla `2>&1` ohjasin `stderr` streamin `stdout` streamiin jotta putkitetut grep komennot voivat suodattaa ei halutut viestit pois ulostuksesta. Sitten putkitin useamman `grep` komennon putkeen, jotta sain sanan parret suodatettua. Tätä tämä reealielämän terminaalielämä on.. outputtiin tulee kaikkea shaissea. Ehkä olisin voinut jotenkin piilottaa `stderr` streamin kokonaan kun en ollut siitä kiinnostunut. Tai kasata kaikki suodatettavat tekstit yhteen grep komentoon.

Noh.. nähdään vaiva ja luetaan man.. siis tehdään Google haku ja päädytään StackOverflowhun :)

Ensinnäkin voimme ohjata `stderr` tavaran tyhjyyteen `2>/dev/null` komennolla. Jes! Jollon komennossa ei tartteta enää suodatella höpsöyksiä niin paljon.

Pienen Googlettelun jälkeen minulle selkesi että `/dev/null` on erikoislaite Unix käyttöjärjestelmässä. Sitä sopivasti kutsutaan nimellä `null device`, joka on käytännössä bittien mustaaukko.

Ruvetaanpas etsimään taas rekursiivisesta tietodsto puun juuresta mainintoja `Tassukka toivottaa` ja ohjataan `stderr` tyhjyyteen. 

```
grep -r "Tassukka toivottaa" / 2>/dev/null 
```

Ja komento noin suunnilleen tulosti seuraavaa:

```
Binääritiedosto /proc/7342/task/7342/cmdline täsmää hakuun
Binääritiedosto /proc/7342/cmdline täsmää hakuun
/etc/update-motd.d/00-header:Tassukka toivottaa tulijan tervetulleeksi. Ethän tee minulle mitään
/etc/motd.tcl:Tassukka toivottaa tulijan tervetulleeksi. Ethän tee minulle mitään
/etc/motd.tail:Tassukka toivottaa tulijan tervetulleeksi. Ethän tee minulle mitään
```

