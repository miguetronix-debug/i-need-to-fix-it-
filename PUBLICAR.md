# Cómo publicarlo

Está todo listo. Falta el paso que solo puedes dar tú, porque exige entrar con tus credenciales.

---

## Por qué no puedo publicarlo yo

Para subirlo a GitHub o a Vercel hay que autenticarse, y **yo no manejo contraseñas ni tokens**: no me los pegues en el chat. La forma correcta de darme acceso a GitHub no es pasarme una credencial sino **autorizar el conector desde tus ajustes de Claude**, con lo que el permiso lo das tú y yo nunca veo la clave. Aun así, en esta sesión ese flujo no se puede completar, y para Vercel directamente no existe conector.

Así que la división queda así: el repositorio está creado y con su primer commit hecho, el sitio está armado y probado, y lo único que falta son dos comandos y un clic.

---

## Opción A · La más rápida, sin GitHub · dos minutos

1. Entra en **[app.netlify.com/drop](https://app.netlify.com/drop)**
2. Arrastra la carpeta **`sitio/`** a la ventana
3. Ya está publicado, con https y certificado

Sirve para enseñárselo a alguien hoy mismo. La pega es que para actualizarlo hay que volver a arrastrar.

---

## Opción B · GitHub y Vercel · la buena para mantenerlo

El repositorio ya está inicializado y con el primer commit hecho, con los 1 270 archivos dentro. Quedan seis cambios sin confirmar —este documento y el arreglo del *service worker*— porque desde mi entorno no puedo borrar un fichero de bloqueo dentro de tu carpeta. Se resuelve con la primera línea:

```bash
cd "/Users/drkush/Documents/Claude/Projects/libro de ortopedia/app-10-pasos"

# 0 · quitar el bloqueo que quedó suelto y cerrar el último commit
rm -f .git/index.lock
git add -A && git commit -m "Sitio listo para publicar"

# 1 · crea el repositorio vacío en github.com/new  (por ejemplo: i-need-to-fix-it)
#     sin README, sin .gitignore, sin licencia

# 2 · conéctalo y sube
git remote add origin https://github.com/TU_USUARIO/i-need-to-fix-it.git
git branch -M main
git push -u origin main
```

Después, en **vercel.com**:

1. *Add New… → Project* e importa el repositorio
2. Framework Preset: **Other**
3. **Root Directory: `sitio`** ← lo único que hay que cambiar
4. *Deploy*

A partir de ahí, cada `git push` republica solo.

Para actualizar el contenido:

```bash
python3 tools/build_prototipo.py && python3 tools/publicar.py
git add -A && git commit -m "lo que hayas cambiado" && git push
```

---

## Lo que hay que comprobar en cuanto esté en línea

Tres cosas que **no he podido verificar aquí** porque el navegador del entorno de pruebas no soporta *service workers*, y que en cambio se comprueban en dos minutos en tu móvil:

1. **Que se instale.** Abre la URL en el móvil y busca «Añadir a pantalla de inicio». Debería aparecer con su icono y abrirse sin barra de navegador.
2. **Que funcione sin conexión.** Ábrela, navega un par de pasos, pon el móvil en modo avión y recárgala. Debería seguir funcionando.
3. **Que los enlaces de caso funcionen.** Copia la URL con un caso a medias y ábrela en otro dispositivo: tiene que aparecer con las mismas decisiones puestas.

Si el modo sin conexión falla, la consola del navegador dirá exactamente qué recurso no se pudo cachear: el *service worker* ahora avisa en lugar de callarse.

---

## Antes de enseñárselo a nadie

**El nombre y el dominio siguen sin verificar.** «I Need To Fix It» nunca se comprobó como marca ni como dominio disponible. Vercel y Netlify te dan un subdominio gratuito, así que para probarlo con residentes basta; para algo estable conviene mirarlo antes de que la URL empiece a circular.

**La licencia AO.** La OTA y la AO permiten reproducir la clasificación y sus figuras con fines de investigación, docencia o uso médico sin pedir permiso; **el uso comercial requiere autorización del editor**. Mientras siga siendo gratuito, encaja. El día que se plantee cobrar, hay que pedir permiso primero.
