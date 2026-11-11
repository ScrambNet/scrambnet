# Política de seguridad

ScrambNet es pre-alpha: una especificación y una prueba de concepto, no todavía un sistema con
el que proteger secretos reales. La contribución más valiosa que puedes hacer es una
rotura.

## Qué cuenta como hallazgo

- Un fallo en el **diseño**: una forma de leer el contenido por debajo de `k` partes capturadas; una
  forma de vincular las partes de un mismo mensaje (SP-7); un ataque de eclipse, sybil o
  que derrote la disjunción contra el descubrimiento o la selección de rutas; cualquier cosa que
  viole un invariante (I-1…I-4).
- Un fallo en el código de la **prueba de concepto** bajo `poc/`. Ten en cuenta que la PoC
  usa deliberadamente aritmética de tiempo no constante y construcciones de juguete; eso
  son no-objetivos documentados, no hallazgos. Una desviación de la especificación, o un
  defecto de la especificación que el código revele, sí es un hallazgo.

## Cómo informar

- **Fallos de diseño y problemas de la PoC que no sean sensibles:** abre una issue pública.
  La discusión abierta es el sentido de este repositorio.
- **Cualquier cosa que creas que debe tratarse primero en privado:** escribe a
  `scrambnet@proton.me`. Cifra los informes sensibles con la clave del proyecto (ver
  más abajo). Aspiramos a acusar recibo **en un plazo de 7 días**; si para entonces no
  has recibido respuesta, dalo por perdido en las cañerías seudónimas y vuelve a avisar
  en una issue pública (sin el detalle sensible) para que nos demos cuenta.

Por favor, no incluyas tu identidad legal en un informe a menos que quieras que sea
pública. Los informes seudónimos son bienvenidos y reciben la misma consideración.

## Alcance

En alcance: la especificación en `docs/`, la PoC en `poc/`. Fuera de alcance: la
seguridad del propio dispositivo o cuenta de quien contribuye; la plataforma GitHub en sí; la
denegación de servicio contra este repositorio.

## Clave del proyecto

Una clave PGP para `scrambnet@proton.me` está publicada en el repositorio como
[`scrambnet-pubkey.asc`](../../scrambnet-pubkey.asc). Cifra con ella los informes sensibles.

```
Fingerprint: E5B5 399D 751F 830D 35CB  5F4A 3087 9F3B F93D 44F7
Algorithm:   Ed25519 (sign) + Cv25519 (encrypt)
Created:     2026-11-11   Expires: 2028-11-10
```

Verifica el fingerprint contra este archivo (e, idealmente, contra una segunda copia de
este documento en un mirror distinto) antes de confiar en la clave: el sentido de
publicarla en el propio texto *y* como archivo versionado es que ambas deben coincidir.

Para usarla:

```
gpg --import scrambnet-pubkey.asc
gpg --fingerprint scrambnet@proton.me     # debe coincidir con la línea de arriba
gpg --encrypt --armor -r scrambnet@proton.me your-report.txt
```

**Rotación (por qué la clave caduca, invariante I-3).** La clave caduca dentro de dos
años; deliberadamente no es un singleton inmortal. Antes de que expire, la siguiente
clave se publicará aquí y **firmada por esta** mientras esta siga siendo válida, de modo
que el traspaso sea verificable en lugar de un acto de fe. Si esta clave se pierde o se
ve comprometida alguna vez antes de su caducidad, se publicará aquí un certificado de
revocación (generado y conservado sin conexión en el momento de la creación) y se
enviará a `keys.openpgp.org`, y se anunciará una nueva clave de la misma manera. Ninguna
clave de divulgación individual es un punto de confianza permanente.

## Divulgación

Divulgación coordinada para todo lo que pudiera poner en peligro a los usuarios de un futuro
despliegue; discusión pública inmediata para todo lo que esté en esta etapa pre-alpha,
donde no hay usuarios a quienes poner en peligro y el objetivo es romper el diseño antes de que
alguien dependa de él.
