# Contribuir a ScrambNet

El proyecto está en la fase de pre-especificación. Las contribuciones más valiosas en este
momento, por orden:

1. **Ataca el modelo de amenazas.** Abre una issue contra cualquier afirmación de
   [docs/threat-model.md](threat-model.md), especialmente la lista de problemas abiertos.
2. **Propón texto de especificación.** PR contra `docs/` — al estilo RFC, un mecanismo por PR.
3. **Traduce.** Los README existen en seis idiomas; `docs/` está por ahora solo en inglés.
   Las traducciones y correcciones de hablantes nativos son contribuciones de primera clase.
4. **Señala trabajos previos.** Si algo aquí reinventa la rueda, nombra la rueda. La filosofía
   de diseño es componer trabajo publicado y atacado, nunca inventar donde basta una cita.

## Cómo trabajamos

- Un tema por issue. Los debates de diseño viven en las issues, las decisiones quedan
  registradas en `docs/`.
- El inglés es la lengua canónica de `docs/`; si editas un README en un idioma, o actualizas
  los demás o dices en la PR que ahora están desactualizados.
- Nada de código hasta que el modelo de amenazas y la especificación del protocolo se
  estabilicen. Cuando empiece el código: un único cliente de referencia pequeño, aburrido y
  mobile-first.

## Política de seudonimia

No se exigen nombres reales y nunca se exigirán. Las contribuciones seudónimas y anónimas son
de primera clase. No hay CLA; al contribuir liberas tu contribución a la documentación bajo
[CC0 1.0](LICENSE).

Si tu propio modelo de amenazas lo requiere, protégete:

- Usa la dirección noreply de tu forge en los commits:
  `git config user.email "USERNAME@users.noreply.github.com"`
- Haz los commits en UTC para que tu zona horaria no se filtre:
  `git config alias.ci '!TZ=UTC git commit'`
- No firmes los commits con una clave ligada a tu identidad legal; si firmas, usa una clave
  creada solo para este seudónimo.
- No reutilices apodos de otros lugares, y recuerda que el estilo de la prosa es una huella.

## Neutralidad

Esta red transporta paquetes, no opiniones. Protege a los disidentes y a sus adversarios con
la misma matemática; los adversarios políticos no son enemigos. Las propuestas que harían que
la red favoreciera o perjudicara puntos de vista, orígenes o destinos concretos serán
rechazadas al margen del punto de vista — esa neutralidad es el argumento de seguridad del
proyecto tanto como su ética.
