# ADR-0005: `nexus.secrets.bundle`, cifrado en navegador, import a vault local, OAuth/device flow y prohibición de secretos en prompts cowork

- **Estado:** Aceptada (contrato `v1alpha1`)
- **Fecha:** 2026-07-19
- **Versión de arquitectura:** `v1alpha1`
- **Relacionadas:** [ADR-0002](0002-signing-and-verification.md); esquema [`secrets-bundle-manifest`](../schemas/v1alpha1/secrets-bundle-manifest.schema.json)

## Contexto

Un artefacto de API keys en texto plano (`.env`) es el punto de fuga más probable del sistema: se
copia, se sube por error a un repo, se pega en un chat de soporte o queda en el historial de un
asistente cowork. El sistema gestionado necesita transferir secretos a la instancia **sin** que el
Hub, el tránsito o un asistente vean el valor en claro.

## Decisión

Separar el problema en artefactos con distinto nivel de exposición:

1. **`SETUP.md`** (humanos y cowork): instrucciones paso a paso **sin ningún valor de secreto**.
2. **`setup.plan.yaml`** (máquina): plan parseable, **sin secretos embebidos**.
3. **`nexus.secrets.bundle`** (paquete cifrado de un solo uso):
   - El usuario pega sus claves en un formulario del Hub que las **cifra en el navegador** contra la
     **clave pública de la instancia** (`age`/`hpke`/`jwe`). El Hub **nunca** almacena la clave en claro.
   - Se transfiere al Operator o se descarga **una sola vez**.
   - El Runtime lo importa a su **vault local** (secreto en reposo, cifrado, dentro de la instancia).
   - Tras importación exitosa, el bundle se **invalida y elimina**; no queda copia reutilizable.
   - El **manifiesto público** (`secrets-bundle-manifest.schema.json`) describe **solo metadatos**:
     `bundle_id`, destinatario, esquema de cifrado, `entries` (nombre de referencia + servicio +
     método de obtención), `expires_at`, `single_use`. El esquema **prohíbe** por construcción campos
     `value`/`secret`/`plaintext`/`ciphertext` en cada entrada.
4. **OAuth / device authorization primero:** antes de pedir una API key manual, el flujo intenta
   OAuth/device flow contra el proveedor, o referencias a un vault externo (AWS/GCP/HashiCorp). La API
   key en texto es **último recurso**.

## Regla no negociable para asistentes cowork

**Ningún asistente cowork (OpenClaw u otro) recibe jamás un secreto en texto plano en su prompt o
contexto.** El asistente trabaja contra `SETUP.md` y `setup.plan.yaml`, ejecuta conexiones OAuth
cuando es posible, y en el peor caso indica al humano dónde pegar el secreto en un formulario cifrado,
nunca a través del propio asistente. El rol cowork es acotado ("setup executor"), no hereda todos los
permisos del usuario.

## Consecuencias

- El valor de secreto solo existe en claro en el navegador del usuario y en el vault de la instancia.
- Caducidad corta + un solo uso limitan la ventana de exposición.
- Coste: implementar cifrado en navegador y gestión del ciclo de vida del bundle.

## Alternativas consideradas

- **`.env` en texto plano como artefacto por defecto:** rechazada explícitamente.
- **Hub almacena las claves cifradas a su propia clave:** rechazada; concentra el secreto en el Hub.
