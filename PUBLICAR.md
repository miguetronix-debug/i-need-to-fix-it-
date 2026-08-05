# Cómo publicarlo

## ✅ Publicado el 5 de agosto de 2026

| Dirección | Estado |
|---|---|
| **https://ineedtofixit.vercel.app** | **La buena.** Conectada al repositorio: cada `git push` la republica sola. |
| https://i-need-to-fix-it.vercel.app | Alias del mismo despliegue. |
| https://ineedtofixit.netlify.app | El primer intento, subido a mano. **Se queda congelado** hasta que vuelvas a arrastrar la carpeta. |

Repositorio: `github.com/miguetronix-debug/i-need-to-fix-it-` (con el guion final, que se coló al crearlo).

**El ajuste que hace que todo funcione** está en Vercel, en *Settings → **Build and Deployment** → Root Directory → `sitio`*. Ojo: **no está en General**, que es donde la documentación vieja lo sitúa. Sin ese ajuste, Vercel sirve la raíz del repositorio y el app queda colgando de `/sitio/` con la portada vacía.

Un `vercel.json` en la raíz con `outputDirectory` **no sustituye a ese ajuste**: en proyectos estáticos sin compilación, Vercel lo ignora. Se probó y no funciona.

Verificado en las tres: el HTML llega entero, el *service worker* y el icono responden, y las figuras cargan. En Vercel además el manifest llega con su tipo correcto, que es lo que permite instalar la app.

**Para publicar un cambio de aquí en adelante:**

```bash
cd "/Users/drkush/Documents/Claude/Projects/libro de ortopedia/app-10-pasos"
python3 tools/build_prototipo.py && python3 tools/publicar.py
git add -A && git commit -m "lo que hayas cambiado" && git push
```

Y ya está: Vercel lo detecta y republica en menos de un minuto. **La de Netlify no**: esa hay que actualizarla a mano entrando al sitio → pestaña *Deploys* → arrastrar ahí la carpeta `sitio`. Ojo: si vuelves a arrastrarla en `app.netlify.com/drop` se crea un sitio **nuevo** con otra dirección. Lo más simple es quedarse con la de Vercel y olvidar la otra.

---

## Lo que queda por comprobar en un móvil

Tres cosas que **no se pueden verificar desde aquí** y que en tu teléfono llevan dos minutos. Usa la dirección de Vercel:

1. **Que se instale.** Abre https://ineedtofixit.vercel.app y busca «Añadir a pantalla de inicio». Debe aparecer con su icono y abrirse sin barra de navegador.
2. **Que funcione sin conexión.** Ábrela, navega dos o tres pasos, pon el móvil en modo avión y recarga. Si sigue funcionando, el *service worker* quedó bien.
3. **Que los enlaces de caso viajen.** Rellena medio caso, copia la URL de la barra y ábrela en otro dispositivo: tienen que aparecer las mismas decisiones marcadas.

Si el modo sin conexión falla, la consola del navegador dirá exactamente qué recurso no se pudo cachear: el *service worker* avisa en lugar de callarse.

---

<details>
<summary>Cómo se llegó hasta aquí (por si hay que repetirlo)</summary>

## Por qué no pude publicarlo yo

Para subirlo a GitHub o a Vercel hay que autenticarse, y **yo no manejo contraseñas ni tokens**: no me los pegues en el chat. La forma correcta de darme acceso a GitHub no es pasarme una credencial sino **autorizar el conector desde tus ajustes de Claude**, con lo que el permiso lo das tú y yo nunca veo la clave. Aun así, en esta sesión ese flujo no se puede completar, y para Vercel directamente no existe conector.

Así que la división queda así: el repositorio está creado, con todo confirmado; el sitio está armado y probado; y lo único que falta es que entres tú con tu cuenta.

---

## Opción A · La más rápida, sin GitHub · dos minutos

1. Entra en **[app.netlify.com/drop](https://app.netlify.com/drop)**
2. Arrastra la carpeta **`sitio/`** a la ventana
3. Ya está publicado, con https y certificado

Sirve para enseñárselo a alguien hoy mismo. La pega es que para actualizarlo hay que volver a arrastrar.

---

## Opción B · GitHub y Vercel · la buena para mantenerlo

El repositorio está inicializado, en la rama `main`, con cuatro commits y **nada pendiente de confirmar**. Pesa 29 MB y el archivo más grande son 1,2 MB, muy por debajo del límite de 100 MB por archivo de GitHub. Solo falta conectarlo.

### Primero: la cuenta

Si aún no la tienes, en **[github.com/signup](https://github.com/signup)**. Correo, contraseña, nombre de usuario. Gratis, y los repositorios privados también son gratis, así que puedes tenerlo oculto mientras lo pruebas.

Ahora elige ruta. **La primera no usa el terminal y no exige tokens: es la que recomiendo.**

---

### Ruta 1 · GitHub Desktop · sin terminal *(recomendada)*

1. Descarga **[desktop.github.com](https://desktop.github.com)** e instálalo.

2. Ábrelo y entra con tu cuenta: *File → Options → Accounts → Sign in*. Se autentica por el navegador, así que **no tienes que crear ni pegar ningún token**. Este es el motivo principal para preferir esta ruta.

3. **File → Add Local Repository…**, y elige la carpeta:

   `/Users/drkush/Documents/Claude/Projects/libro de ortopedia/app-10-pasos`

   La reconocerá como repositorio de git —ya lo es— y no te pedirá inicializar nada.

4. Verás un botón **Publish repository**. Al pulsarlo te pregunta el nombre (`i-need-to-fix-it`) y si quieres mantenerlo privado. **Deja marcado *Keep this code private* de momento**; se puede hacer público después con un clic.

5. **Publish repository**. Sube los 29 MB en un par de minutos.

A partir de ahí, cada vez que cambies algo: el programa te lista lo que cambió, escribes una frase abajo a la izquierda, pulsas **Commit to main** y luego **Push origin**. Eso es todo.

---

### Ruta 2 · Terminal

Funciona igual, pero **hay una trampa**: desde 2021 GitHub **no acepta la contraseña de tu cuenta** para subir código. Si te pide contraseña y escribes la tuya, falla siempre y el mensaje de error no lo explica bien. Hay que darle un *token* en su lugar.

**Antes**, crea el repositorio vacío en **[github.com/new](https://github.com/new)** con el nombre `i-need-to-fix-it`, y **sin marcar** README, .gitignore ni licencia —si marcas alguno, el repositorio nace con un commit y el `push` es rechazado por historiales divergentes—.

La forma más limpia de resolver la autenticación es instalar la herramienta oficial de GitHub, que también entra por el navegador y deja las credenciales guardadas:

```bash
brew install gh          # si no tienes Homebrew: brew.sh
gh auth login            # elige GitHub.com → HTTPS → sí → Login with a web browser
```

Y ya:

```bash
cd "/Users/drkush/Documents/Claude/Projects/libro de ortopedia/app-10-pasos"
git remote add origin https://github.com/TU_USUARIO/i-need-to-fix-it.git
git push -u origin main
```

*(Si prefieres no instalar nada: **github.com → foto de perfil → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token**, marca el permiso `repo`, cópialo, y cuando el `git push` pida la contraseña **pega el token ahí**. Cópialo bien: GitHub no vuelve a enseñártelo.)

### Y después, en Vercel, clic a clic

Vercel no sube archivos: **importa desde GitHub**, así que el `git push` de arriba tiene que estar hecho antes.

1. Entra en **[vercel.com](https://vercel.com)** y pulsa **Continue with GitHub**. Iniciar sesión con la cuenta de GitHub evita tener que conectarlas después.

2. En el panel, arriba a la derecha: **Add New…** → **Project**.

3. Aparece *Import Git Repository*. La primera vez no verás ningún repositorio: hay que darle acceso. Pulsa **Adjust GitHub App Permissions** —o *Install*— y autoriza, o bien todos tus repositorios o bien solo `i-need-to-fix-it`. Al volver ya aparece en la lista.

4. Pulsa **Import** en la fila del repositorio.

5. Se abre *Configure Project*. Aquí solo hay que tocar una cosa:

   - **Framework Preset:** `Other`
   - **Root Directory:** pulsa **Edit**, elige la carpeta **`sitio`** y confirma. ← *esto es lo único imprescindible*
   - **Build Command**, **Output Directory** e **Install Command**: déjalos vacíos y sin activar *Override*. No hay nada que compilar: son archivos estáticos.

6. **Deploy**. Tarda menos de un minuto.

7. Te da una URL del tipo `i-need-to-fix-it.vercel.app`. Ábrela en el móvil.

**Si te equivocas en el Root Directory** —que es el fallo típico— verás el listado de archivos del repositorio en vez del app. Se arregla sin volver a desplegar: *Settings → General → Root Directory → `sitio` → Save*, y luego *Deployments → … → Redeploy*.

A partir de ahí, cada `git push` republica solo. Para actualizar el contenido:

```bash
python3 tools/build_prototipo.py && python3 tools/publicar.py
git add -A && git commit -m "lo que hayas cambiado" && git push
```

</details>

---

## Antes de enseñárselo a nadie

**El nombre y el dominio siguen sin verificar.** «I Need To Fix It» nunca se comprobó como marca ni como dominio disponible. Vercel y Netlify te dan un subdominio gratuito, así que para probarlo con residentes basta; para algo estable conviene mirarlo antes de que la URL empiece a circular.

**La licencia AO.** La OTA y la AO permiten reproducir la clasificación y sus figuras con fines de investigación, docencia o uso médico sin pedir permiso; **el uso comercial requiere autorización del editor**. Mientras siga siendo gratuito, encaja. El día que se plantee cobrar, hay que pedir permiso primero.
