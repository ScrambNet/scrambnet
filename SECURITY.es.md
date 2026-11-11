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
  más abajo). Aspiramos a acusar recibo en un plazo razonable; ten en cuenta que es un
  proyecto seudónimo y al ritmo del voluntariado.

Por favor, no incluyas tu identidad legal en un informe a menos que quieras que sea
pública. Los informes seudónimos son bienvenidos y reciben la misma consideración.

## Alcance

En alcance: la especificación en `docs/`, la PoC en `poc/`. Fuera de alcance: la
seguridad del propio dispositivo o cuenta de quien contribuye; la plataforma GitHub en sí; la
denegación de servicio contra este repositorio.

## Clave del proyecto

Una clave PGP para `scrambnet@proton.me` para los informes cifrados se publicará
aquí y en el repositorio. Hasta que una clave firmada aparezca en este archivo, trata
el correo como confidencial-pero-no-autenticado y guarda los detalles más sensibles
para un canal que puedas verificar.

## Divulgación

Divulgación coordinada para todo lo que pudiera poner en peligro a los usuarios de un futuro
despliegue; discusión pública inmediata para todo lo que esté en esta etapa pre-alpha,
donde no hay usuarios a quienes poner en peligro y el objetivo es romper el diseño antes de que
alguien dependa de él.
