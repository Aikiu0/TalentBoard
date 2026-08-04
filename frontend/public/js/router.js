/* ============================================================
   TalentBoard - Router SPA + lógica de las vistas
   ------------------------------------------------------------
   Toda la lógica de las pantallas vive AQUÍ (no en los .html),
   porque este archivo se ejecuta siempre (está en <script src>).
   Las vistas en views/*.html son SOLO HTML.

   Para agregar una pantalla nueva:
     1. Crea views/miPantalla.html (solo HTML).
     2. Regístrala en "routes".
     3. Si necesita lógica, crea una función init y enlázala
        en "inicializadores".
   ============================================================ */

// IMPORTANTE: el host del backend debe COINCIDIR con el host desde el que
// abres la página, o las cookies de sesión no viajarán.
//   - Si abres el frontend en  http://127.0.0.1:5500  -> usa 127.0.0.1 aquí.
//   - Si abres el frontend en  http://localhost:5500   -> usa localhost aquí.
// (El navegador trata "localhost" y "127.0.0.1" como sitios distintos.)
const API_URL = "http://127.0.0.1:5000";

// Mapa de rutas -> archivo de la vista
const routes = {
    "login":    "views/login.html",
    "register": "views/register.html",
    "dashboard-candidato": "views/dashboard-candidato.html",
    "dashboard-empresa":   "views/dashboard-empresa.html",
};

const RUTA_INICIAL = "login";
const app = document.getElementById("app");

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/* ============================================================
   UTILIDADES
   ============================================================ */
function navegarA(nombre) {
    window.location.hash = nombre;
}

// Conecta TODOS los ojos (toggle-password) que haya en pantalla
function activarTogglePassword() {
    document.querySelectorAll(".toggle-password").forEach(function (icon) {
        // Evita duplicar el listener si ya se enganchó
        if (icon.dataset.bound === "1") return;
        icon.dataset.bound = "1";
        icon.addEventListener("click", function () {
            var input = document.getElementById(this.dataset.target);
            if (!input) return;
            if (input.type === "password") {
                input.type = "text";
                this.classList.remove("fa-eye");
                this.classList.add("fa-eye-slash");
            } else {
                input.type = "password";
                this.classList.remove("fa-eye-slash");
                this.classList.add("fa-eye");
            }
        });
    });
}

/* ============================================================
   LÓGICA DE CADA VISTA
   ============================================================ */

// ---- LOGIN ----
function initLogin() {
    activarTogglePassword();

    var form = document.getElementById("loginForm");
    if (!form) return;
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        var correo    = document.getElementById("login-correo").value.trim();
        var password  = document.getElementById("login-password").value.trim();
        var btnSubmit = this.querySelector(".btn-submit");

        btnSubmit.textContent = "Signing in...";
        btnSubmit.disabled = true;

        fetch(API_URL + "/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "include",
            body: JSON.stringify({ correo: correo, password: password })
        })
        .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, d: d }; }); })
        .then(function (r) {
            if (r.ok) {
                // Redirigir al dashboard según el rol
                if (r.d.rol === "empresa") {
                    navegarA("dashboard-empresa");
                } else if (r.d.rol === "candidato") {
                    navegarA("dashboard-candidato");
                } else {
                    alert("¡Bienvenido! Rol: " + r.d.rol);
                }
            } else {
                alert(r.d.error || "Error al iniciar sesión");
            }
        })
        .catch(function (err) {
            alert("No se pudo conectar con el servidor. ¿Está corriendo Flask?");
            console.error(err);
        })
        .finally(function () {
            btnSubmit.textContent = "Sign in";
            btnSubmit.disabled = false;
        });
    });
}

// ---- REGISTER ----
function mostrarPaso(rol) {
    var r = document.getElementById("step-role");
    var c = document.getElementById("step-candidato");
    var e = document.getElementById("step-empresa");
    if (!r || !c || !e) return;
    if (rol === null) {            // volver a la selección
        c.style.display = "none";
        e.style.display = "none";
        r.style.display = "block";
        return;
    }
    r.style.display = "none";
    c.style.display = (rol === "candidato") ? "block" : "none";
    e.style.display = (rol === "empresa") ? "block" : "none";
}

function enviarRegistro(payload, btnSubmit) {
    btnSubmit.textContent = "Creando cuenta...";
    btnSubmit.disabled = true;
    fetch(API_URL + "/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(payload)
    })
    .then(function (res) { return res.json().then(function (d) { return { ok: res.ok, d: d }; }); })
    .then(function (r) {
        if (r.ok) {
            alert("¡Cuenta creada exitosamente! Ahora puedes iniciar sesión.");
            navegarA("login");
        } else {
            alert(r.d.error || "Error al crear la cuenta.");
        }
    })
    .catch(function (err) {
        alert("No se pudo conectar con el servidor. ¿Está corriendo Flask?");
        console.error(err);
    })
    .finally(function () {
        btnSubmit.textContent = "Crear cuenta";
        btnSubmit.disabled = false;
    });
}

function initRegister() {
    console.log("[register] init OK");
    activarTogglePassword();

    // Tarjetas de rol
    var tarjetas = document.querySelectorAll(".role-card[data-rol]");
    console.log("[register] tarjetas encontradas:", tarjetas.length);
    tarjetas.forEach(function (btn) {
        btn.addEventListener("click", function () {
            console.log("[register] click rol:", this.getAttribute("data-rol"));
            mostrarPaso(this.getAttribute("data-rol"));
        });
    });

    // Botones "Volver"
    document.querySelectorAll(".btn-volver").forEach(function (btn) {
        btn.addEventListener("click", function () { mostrarPaso(null); });
    });

    // Formulario PERSONA
    var formCand = document.getElementById("formCandidato");
    if (formCand) {
        formCand.addEventListener("submit", function (e) {
            e.preventDefault();
            var nombre    = document.getElementById("cand-nombre").value.trim();
            var apellido  = document.getElementById("cand-apellido").value.trim();
            var correo    = document.getElementById("cand-correo").value.trim();
            var password  = document.getElementById("cand-password").value.trim();
            var password2 = document.getElementById("cand-password2").value.trim();
            var terms     = document.getElementById("cand-terms").checked;

            document.getElementById("cand-correo-error").classList.remove("show");
            document.getElementById("cand-pass-error").classList.remove("show");
            document.getElementById("cand-correo").classList.remove("input-error");
            document.getElementById("cand-password2").classList.remove("input-error");

            var valid = true;
            if (!nombre || !apellido) { alert("Ingresa nombre y apellido."); valid = false; }
            if (!emailRegex.test(correo)) {
                document.getElementById("cand-correo-error").classList.add("show");
                document.getElementById("cand-correo").classList.add("input-error");
                valid = false;
            }
            if (password !== password2 || !password) {
                document.getElementById("cand-pass-error").classList.add("show");
                document.getElementById("cand-password2").classList.add("input-error");
                valid = false;
            }
            if (!terms) { alert("Debes aceptar los términos."); valid = false; }
            if (!valid) return;

            enviarRegistro(
                { rol: "candidato", correo: correo, password: password, nombre: nombre, apellido: apellido },
                this.querySelector(".btn-submit")
            );
        });
    }

    // Formulario EMPRESA
    var formEmp = document.getElementById("formEmpresa");
    if (formEmp) {
        formEmp.addEventListener("submit", function (e) {
            e.preventDefault();
            var nombre_empresa = document.getElementById("emp-nombre").value.trim();
            var descripcion    = document.getElementById("emp-descripcion").value.trim();
            var correo         = document.getElementById("emp-correo").value.trim();
            var password       = document.getElementById("emp-password").value.trim();
            var password2      = document.getElementById("emp-password2").value.trim();
            var terms          = document.getElementById("emp-terms").checked;

            document.getElementById("emp-correo-error").classList.remove("show");
            document.getElementById("emp-pass-error").classList.remove("show");
            document.getElementById("emp-correo").classList.remove("input-error");
            document.getElementById("emp-password2").classList.remove("input-error");

            var valid = true;
            if (!nombre_empresa) { alert("Ingresa el nombre de la empresa."); valid = false; }
            if (!emailRegex.test(correo)) {
                document.getElementById("emp-correo-error").classList.add("show");
                document.getElementById("emp-correo").classList.add("input-error");
                valid = false;
            }
            if (password !== password2 || !password) {
                document.getElementById("emp-pass-error").classList.add("show");
                document.getElementById("emp-password2").classList.add("input-error");
                valid = false;
            }
            if (!terms) { alert("Debes aceptar los términos."); valid = false; }
            if (!valid) return;

            enviarRegistro(
                { rol: "empresa", correo: correo, password: password, nombre_empresa: nombre_empresa, descripcion: descripcion },
                this.querySelector(".btn-submit")
            );
        });
    }
}

/* ============================================================
   HELPERS COMPARTIDOS DE DASHBOARD
   ============================================================ */

// Activa/desactiva body.dashboard-mode según la vista
function setDashboardMode(activo) {
    if (activo) document.body.classList.add("dashboard-mode");
    else document.body.classList.remove("dashboard-mode");
}

// Navegación entre secciones internas del dashboard (sidebar)
function activarNavSecciones(prefijoSeccion) {
    var items = document.querySelectorAll(".nav-item[data-seccion]");
    items.forEach(function (item) {
        item.addEventListener("click", function () {
            var sec = this.getAttribute("data-seccion");
            // marcar activo
            items.forEach(function (i) { i.classList.remove("active"); });
            this.classList.add("active");
            // mostrar la sección correspondiente, ocultar las demás
            mostrarSeccion(prefijoSeccion, sec);
        });
    });
}

function mostrarSeccion(prefijo, sec) {
    // Oculta todas las <section id="sec-..."> y muestra la elegida
    document.querySelectorAll('section[id^="sec-"]').forEach(function (s) {
        s.style.display = "none";
    });
    var target = document.getElementById("sec-" + sec);
    if (target) target.style.display = "block";
}

// Cerrar sesión
function activarLogout() {
    var btn = document.getElementById("btnLogout");
    if (!btn) return;
    btn.addEventListener("click", function () {
        fetch(API_URL + "/api/logout", { method: "POST", credentials: "include" })
            .finally(function () { navegarA("login"); });
    });
}

// Escapar texto para evitar romper el HTML al inyectar datos
function esc(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Iniciales para el "logo" de una empresa
function iniciales(nombre) {
    if (!nombre) return "?";
    var partes = nombre.trim().split(/\s+/);
    if (partes.length === 1) return partes[0].charAt(0).toUpperCase();
    return (partes[0].charAt(0) + partes[1].charAt(0)).toUpperCase();
}

function formatoSalario(s) {
    if (s === null || s === undefined) return null;
    return "$" + Number(s).toLocaleString("es-MX");
}

/* ============================================================
   MAPAS — APIs externas consumidas:
     1) Leaflet + tiles de OpenStreetMap  -> dibuja los mapas
     2) Nominatim (OpenStreetMap)         -> geocodificación:
        convierte una dirección escrita en lat/lng vía REST:
        GET https://nominatim.openstreetmap.org/search?format=json&q=...
   ============================================================ */
var mapaCandidato   = null;  // mapa grande del dashboard candidato
var capaMarcadores  = null;  // grupo de pines de vacantes (se limpia y recarga)
var mapaEmpresa     = null;  // mini-mapa del formulario "Crear vacante"
var marcadorEmpresa = null;  // pin de la vacante que se está creando

var CENTRO_MX = [23.6345, -102.5528]; // centro aproximado de México
var ZOOM_MX = 5;

// Crea un mapa Leaflet con los tiles de OpenStreetMap
function crearMapa(idContenedor, centro, zoom) {
    var mapa = L.map(idContenedor).setView(centro, zoom);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(mapa);
    return mapa;
}

/* ---------- MAPA DEL CANDIDATO (vacantes con ubicación) ---------- */
function cargarMapaVacantes() {
    if (!document.getElementById("mapaVacantes")) return;

    // Crear el mapa solo la primera vez que se abre la sección
    if (!mapaCandidato) {
        mapaCandidato = crearMapa("mapaVacantes", CENTRO_MX, ZOOM_MX);
        capaMarcadores = L.layerGroup().addTo(mapaCandidato);

        // El HTML del popup se inyecta dinámicamente: enganchar
        // el botón "Postularme" cada vez que se abre un popup.
        mapaCandidato.on("popupopen", function (e) {
            var btn = e.popup.getElement().querySelector(".btn-postular-mapa");
            if (btn && btn.dataset.bound !== "1") {
                btn.dataset.bound = "1";
                btn.addEventListener("click", function () {
                    postularse(this.getAttribute("data-id"), this);
                });
            }
        });
    }

    // Leaflet calcula mal el tamaño si el contenedor estaba oculto
    // (display:none). La sección ya es visible: recalcular.
    setTimeout(function () { mapaCandidato.invalidateSize(); }, 100);

    var info = document.getElementById("mapa-info");
    if (info) info.textContent = "Cargando vacantes…";

    fetch(API_URL + "/api/vacantes", { credentials: "include" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var vacantes = (data && data.vacantes) || [];
            capaMarcadores.clearLayers();

            var conUbicacion = vacantes.filter(function (v) {
                return v.latitud !== null && v.longitud !== null;
            });

            if (info) {
                info.textContent = conUbicacion.length + " vacante(s) con ubicación en el mapa, de " +
                    vacantes.length + " activa(s) en total.";
            }
            if (conUbicacion.length === 0) return;

            var puntos = [];
            conUbicacion.forEach(function (v) {
                var sal = formatoSalario(v.salario);
                var html = '' +
                    '<div class="popup-vacante">' +
                        '<div class="popup-titulo">' + esc(v.titulo) + '</div>' +
                        '<div class="popup-empresa"><i class="fa-solid fa-building"></i> ' +
                            esc(v.nombre_empresa) + '</div>' +
                        (sal ? '<span class="tag salary">' + sal + '</span>' : '') +
                        '<button class="btn-primary btn-postular-mapa" data-id="' +
                            v.id_vacante + '">Postularme</button>' +
                    '</div>';
                L.marker([v.latitud, v.longitud]).addTo(capaMarcadores).bindPopup(html);
                puntos.push([v.latitud, v.longitud]);
            });

            // Encuadrar el mapa para que se vean todos los pines
            mapaCandidato.fitBounds(L.latLngBounds(puntos), { padding: [40, 40], maxZoom: 14 });
        })
        .catch(function (e) {
            if (info) info.textContent = "No se pudo conectar con el servidor.";
            console.error(e);
        });
}

/* ---------- MINI-MAPA DE LA EMPRESA (crear vacante) ---------- */
function initMapaEmpresa() {
    if (mapaEmpresa || !document.getElementById("mapaEmpresa")) return;
    mapaEmpresa = crearMapa("mapaEmpresa", CENTRO_MX, ZOOM_MX);

    // Clic en el mapa = colocar/ajustar el pin y llenar lat/lng
    mapaEmpresa.on("click", function (e) {
        ponerPinEmpresa(e.latlng.lat, e.latlng.lng);
        var st = document.getElementById("geo-status");
        if (st) { st.textContent = "Ubicación ajustada manualmente en el mapa."; st.className = "geo-status ok"; }
    });
}

function ponerPinEmpresa(lat, lng) {
    var inLat = document.getElementById("vac-lat");
    var inLng = document.getElementById("vac-lng");
    if (inLat) inLat.value = Number(lat).toFixed(7);
    if (inLng) inLng.value = Number(lng).toFixed(7);
    if (marcadorEmpresa) {
        marcadorEmpresa.setLatLng([lat, lng]);
    } else {
        marcadorEmpresa = L.marker([lat, lng]).addTo(mapaEmpresa);
    }
}

// Llama a la API externa Nominatim para convertir dirección -> lat/lng
function geocodificarDireccion() {
    var direccion = document.getElementById("vac-direccion").value.trim();
    var st  = document.getElementById("geo-status");
    var btn = document.getElementById("btnGeocodificar");

    if (!direccion) {
        if (st) { st.textContent = "Escribe una dirección primero."; st.className = "geo-status error"; }
        return;
    }
    btn.disabled = true;
    if (st) { st.textContent = "Buscando dirección…"; st.className = "geo-status"; }

    var url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&accept-language=es&q=" +
              encodeURIComponent(direccion);

    fetch(url)
        .then(function (r) { return r.json(); })
        .then(function (resultados) {
            if (!resultados || resultados.length === 0) {
                if (st) {
                    st.textContent = "No se encontró la dirección. Sé más específico o haz clic directo en el mapa.";
                    st.className = "geo-status error";
                }
                return;
            }
            var lugar = resultados[0];
            var lat = parseFloat(lugar.lat);
            var lng = parseFloat(lugar.lon);
            ponerPinEmpresa(lat, lng);
            mapaEmpresa.setView([lat, lng], 15);
            if (st) { st.textContent = "✓ " + lugar.display_name; st.className = "geo-status ok"; }
        })
        .catch(function (e) {
            if (st) { st.textContent = "Error al consultar el servicio de geocodificación."; st.className = "geo-status error"; }
            console.error(e);
        })
        .finally(function () { btn.disabled = false; });
}

// Deja el mini-mapa listo para la siguiente vacante
function limpiarMapaEmpresa() {
    if (marcadorEmpresa && mapaEmpresa) {
        mapaEmpresa.removeLayer(marcadorEmpresa);
        marcadorEmpresa = null;
    }
    if (mapaEmpresa) mapaEmpresa.setView(CENTRO_MX, ZOOM_MX);
    var st = document.getElementById("geo-status");
    if (st) { st.textContent = ""; st.className = "geo-status"; }
}

/* ============================================================
   DASHBOARD CANDIDATO
   ============================================================ */
function initDashboardCandidato() {
    setDashboardMode(true);
    activarNavSecciones("candidato");
    activarLogout();

    // El SPA reemplaza el DOM al navegar: descartar el mapa anterior
    mapaCandidato = null;
    capaMarcadores = null;

    // Al entrar a "Mapa de vacantes", crear/actualizar el mapa.
    // (Se engancha DESPUÉS de activarNavSecciones para que la sección
    // ya esté visible cuando Leaflet calcule su tamaño.)
    document.querySelectorAll('.nav-item[data-seccion="mapa"]').forEach(function (b) {
        b.addEventListener("click", cargarMapaVacantes);
    });

    // Cargar datos del usuario + perfil
    fetch(API_URL + "/api/me", { credentials: "include" })
        .then(function (res) {
            if (res.status === 401) { navegarA("login"); return null; }
            return res.json();
        })
        .then(function (data) {
            if (!data) return;
            var perfil = data.perfil || {};
            var nombre = perfil.nombre_completo || "";
            var saludo = document.getElementById("saludo-candidato");
            if (saludo) saludo.textContent = "¡Hola" + (nombre ? ", " + nombre.split(" ")[0] : "") + "! 👋";

            // Rellenar formulario de perfil
            var pn = document.getElementById("perfil-nombre");
            var pe = document.getElementById("perfil-especialidad");
            var pc = document.getElementById("perfil-correo");
            if (pn) pn.value = perfil.nombre_completo || "";
            if (pe) pe.value = perfil.especialidad || "";
            if (pc) pc.value = (data.usuario && data.usuario.correo) || "";
        })
        .catch(function (e) { console.error(e); });

    // Cargar lista de vacantes
    cargarVacantesCandidato("");

    // Buscar
    var btnBuscar = document.getElementById("btnBuscar");
    var inputBuscar = document.getElementById("buscarVacante");
    if (btnBuscar) btnBuscar.addEventListener("click", function () {
        cargarVacantesCandidato(inputBuscar ? inputBuscar.value.trim() : "");
    });
    if (inputBuscar) inputBuscar.addEventListener("keydown", function (e) {
        if (e.key === "Enter") cargarVacantesCandidato(this.value.trim());
    });

    // Cuando el usuario entra a "Mis postulaciones", cargarlas
    document.querySelectorAll('.nav-item[data-seccion="postulaciones"]').forEach(function (b) {
        b.addEventListener("click", cargarMisPostulaciones);
    });

    // Guardar perfil
    var formPerfil = document.getElementById("formPerfilCandidato");
    if (formPerfil) {
        formPerfil.addEventListener("submit", function (e) {
            e.preventDefault();
            var payload = {
                nombre_completo: document.getElementById("perfil-nombre").value.trim(),
                especialidad: document.getElementById("perfil-especialidad").value.trim()
            };
            var btn = this.querySelector(".btn-primary");
            btn.disabled = true; btn.textContent = "Guardando…";
            fetch(API_URL + "/api/perfil/candidato", {
                method: "PUT", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (r) { alert(r.ok ? "Perfil actualizado" : (r.d.error || "Error")); })
            .catch(function () { alert("No se pudo conectar con el servidor."); })
            .finally(function () { btn.disabled = false; btn.textContent = "Guardar cambios"; });
        });
    }
}

function cargarVacantesCandidato(q) {
    var cont = document.getElementById("listaVacantes");
    if (!cont) return;
    cont.innerHTML = '<div class="loading">Cargando vacantes…</div>';

    var url = API_URL + "/api/vacantes" + (q ? "?q=" + encodeURIComponent(q) : "");
    fetch(url, { credentials: "include" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var vacantes = (data && data.vacantes) || [];
            if (vacantes.length === 0) {
                cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-folder-open"></i>' +
                    '<p>No se encontraron vacantes' + (q ? ' para "' + esc(q) + '"' : '') + '.</p></div>';
                return;
            }
            cont.innerHTML = vacantes.map(function (v) {
                var sal = formatoSalario(v.salario);
                return '' +
                '<div class="vacancy-card">' +
                    '<div class="vacancy-top">' +
                        '<div class="vacancy-logo">' + esc(iniciales(v.nombre_empresa)) + '</div>' +
                        '<div class="vacancy-headtext">' +
                            '<div class="vacancy-title">' + esc(v.titulo) + '</div>' +
                            '<div class="vacancy-company">' + esc(v.nombre_empresa) + '</div>' +
                        '</div>' +
                    '</div>' +
                    '<div class="vacancy-desc">' + esc(v.descripcion) + '</div>' +
                    '<div class="vacancy-meta">' +
                        (sal ? '<span class="tag salary">' + sal + '</span>' : '') +
                    '</div>' +
                    '<div class="vacancy-actions">' +
                        '<button class="btn-primary btn-postular" data-id="' + v.id_vacante + '">Postularme</button>' +
                    '</div>' +
                '</div>';
            }).join("");

            // Enganchar botones "Postularme"
            cont.querySelectorAll(".btn-postular").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    postularse(this.getAttribute("data-id"), this);
                });
            });
        })
        .catch(function (e) {
            cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i>' +
                '<p>No se pudo conectar con el servidor.</p></div>';
            console.error(e);
        });
}

function postularse(idVacante, btn) {
    btn.disabled = true; btn.textContent = "Enviando…";
    fetch(API_URL + "/api/postulaciones", {
        method: "POST", credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id_vacante: Number(idVacante) })
    })
    .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, status: r.status, d: d }; }); })
    .then(function (r) {
        if (r.ok) {
            btn.textContent = "✓ Postulado";
            btn.classList.remove("btn-primary");
            btn.classList.add("btn-secondary");
        } else {
            alert(r.d.error || "No se pudo postular");
            btn.disabled = false; btn.textContent = "Postularme";
        }
    })
    .catch(function () {
        alert("No se pudo conectar con el servidor.");
        btn.disabled = false; btn.textContent = "Postularme";
    });
}

function cargarMisPostulaciones() {
    var cont = document.getElementById("listaPostulaciones");
    if (!cont) return;
    cont.innerHTML = '<div class="loading">Cargando…</div>';
    fetch(API_URL + "/api/mis-postulaciones", { credentials: "include" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var posts = (data && data.postulaciones) || [];
            if (posts.length === 0) {
                cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-file-circle-question"></i>' +
                    '<p>Aún no te has postulado a ninguna vacante.</p></div>';
                return;
            }
            cont.innerHTML = posts.map(function (p) {
                var sal = formatoSalario(p.salario);
                return '' +
                '<div class="vacancy-card">' +
                    '<div class="vacancy-top">' +
                        '<div class="vacancy-logo">' + esc(iniciales(p.nombre_empresa)) + '</div>' +
                        '<div class="vacancy-headtext">' +
                            '<div class="vacancy-title">' + esc(p.titulo) + '</div>' +
                            '<div class="vacancy-company">' + esc(p.nombre_empresa) + '</div>' +
                        '</div>' +
                        '<span class="badge ' + esc(p.estado) + '">' + esc(p.estado) + '</span>' +
                    '</div>' +
                    '<div class="vacancy-meta">' +
                        (sal ? '<span class="tag salary">' + sal + '</span>' : '') +
                        '<span class="tag">Postulado el ' + esc(p.fecha_postulacion) + '</span>' +
                    '</div>' +
                '</div>';
            }).join("");
        })
        .catch(function (e) {
            cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i>' +
                '<p>No se pudo conectar con el servidor.</p></div>';
            console.error(e);
        });
}

/* ============================================================
   DASHBOARD EMPRESA
   ============================================================ */
function initDashboardEmpresa() {
    setDashboardMode(true);
    activarNavSecciones("empresa");
    activarLogout();

    // El SPA reemplaza el DOM al navegar: descartar el mapa anterior
    mapaEmpresa = null;
    marcadorEmpresa = null;

    // Al entrar a "Crear vacante", inicializar el mini-mapa
    document.querySelectorAll('.nav-item[data-seccion="crear"]').forEach(function (b) {
        b.addEventListener("click", function () {
            initMapaEmpresa();
            setTimeout(function () { if (mapaEmpresa) mapaEmpresa.invalidateSize(); }, 100);
        });
    });

    // Botón "Buscar ubicación" (API Nominatim) + Enter en el campo dirección
    var btnGeo = document.getElementById("btnGeocodificar");
    if (btnGeo) btnGeo.addEventListener("click", geocodificarDireccion);
    var inpDir = document.getElementById("vac-direccion");
    if (inpDir) inpDir.addEventListener("keydown", function (e) {
        if (e.key === "Enter") { e.preventDefault(); geocodificarDireccion(); }
    });

    // Cargar datos + stats
    fetch(API_URL + "/api/me", { credentials: "include" })
        .then(function (res) {
            if (res.status === 401) { navegarA("login"); return null; }
            return res.json();
        })
        .then(function (data) {
            if (!data) return;
            var perfil = data.perfil || {};
            var stats = data.stats || {};
            var saludo = document.getElementById("saludo-empresa");
            if (saludo) saludo.textContent = "Hola, " + (perfil.nombre_empresa || "empresa") + " 👋";

            var sv = document.getElementById("stat-vacantes");
            var sp = document.getElementById("stat-postulaciones");
            var spe = document.getElementById("stat-pendientes");
            if (sv) sv.textContent = stats.vacantes_activas || 0;
            if (sp) sp.textContent = stats.postulaciones_totales || 0;
            if (spe) spe.textContent = stats.postulaciones_pendientes || 0;

            // Rellenar formulario de empresa
            var en = document.getElementById("emp-perfil-nombre");
            var ed = document.getElementById("emp-perfil-descripcion");
            var ec = document.getElementById("emp-perfil-correo");
            if (en) en.value = perfil.nombre_empresa || "";
            if (ed) ed.value = perfil.descripcion || "";
            if (ec) ec.value = (data.usuario && data.usuario.correo) || "";
        })
        .catch(function (e) { console.error(e); });

    // Cargar vacantes recientes (en inicio) y la lista completa
    cargarMisVacantes("vacantesRecientes");

    // Al entrar a "Mis vacantes", recargar la lista completa
    document.querySelectorAll('.nav-item[data-seccion="vacantes"]').forEach(function (b) {
        b.addEventListener("click", function () { cargarMisVacantes("listaMisVacantes"); });
    });

    // Crear vacante
    var formCrear = document.getElementById("formCrearVacante");
    if (formCrear) {
        formCrear.addEventListener("submit", function (e) {
            e.preventDefault();
            var payload = {
                titulo: document.getElementById("vac-titulo").value.trim(),
                descripcion: document.getElementById("vac-descripcion").value.trim(),
                salario: document.getElementById("vac-salario").value.trim(),
                latitud: document.getElementById("vac-lat").value.trim(),
                longitud: document.getElementById("vac-lng").value.trim()
            };
            if (!payload.titulo || !payload.descripcion) {
                alert("Título y descripción son obligatorios.");
                return;
            }
            var btn = this.querySelector(".btn-primary");
            btn.disabled = true; btn.textContent = "Publicando…";
            fetch(API_URL + "/api/vacantes", {
                method: "POST", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (r) {
                if (r.ok) {
                    alert("¡Vacante publicada!");
                    formCrear.reset();
                    limpiarMapaEmpresa();
                    cargarMisVacantes("listaMisVacantes");
                    cargarMisVacantes("vacantesRecientes");
                } else {
                    alert(r.d.error || "Error al crear la vacante");
                }
            })
            .catch(function () { alert("No se pudo conectar con el servidor."); })
            .finally(function () { btn.disabled = false; btn.textContent = "Publicar vacante"; });
        });
    }

    // Guardar perfil empresa
    var formEmp = document.getElementById("formPerfilEmpresa");
    if (formEmp) {
        formEmp.addEventListener("submit", function (e) {
            e.preventDefault();
            var payload = {
                nombre_empresa: document.getElementById("emp-perfil-nombre").value.trim(),
                descripcion: document.getElementById("emp-perfil-descripcion").value.trim()
            };
            var btn = this.querySelector(".btn-primary");
            btn.disabled = true; btn.textContent = "Guardando…";
            fetch(API_URL + "/api/perfil/empresa", {
                method: "PUT", credentials: "include",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            })
            .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
            .then(function (r) { alert(r.ok ? "Perfil actualizado" : (r.d.error || "Error")); })
            .catch(function () { alert("No se pudo conectar con el servidor."); })
            .finally(function () { btn.disabled = false; btn.textContent = "Guardar cambios"; });
        });
    }

    // Botón volver desde candidatos
    var btnVolver = document.getElementById("btnVolverVacantes");
    if (btnVolver) {
        btnVolver.addEventListener("click", function () {
            // volver a la sección de vacantes
            document.querySelectorAll(".nav-item[data-seccion]").forEach(function (i) { i.classList.remove("active"); });
            var navVac = document.querySelector('.nav-item[data-seccion="vacantes"]');
            if (navVac) navVac.classList.add("active");
            mostrarSeccion("empresa", "vacantes");
            cargarMisVacantes("listaMisVacantes");
        });
    }
}

function cargarMisVacantes(contenedorId) {
    var cont = document.getElementById(contenedorId);
    if (!cont) return;
    cont.innerHTML = '<div class="loading">Cargando…</div>';
    fetch(API_URL + "/api/mis-vacantes", { credentials: "include" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var vacantes = (data && data.vacantes) || [];
            if (vacantes.length === 0) {
                cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-briefcase"></i>' +
                    '<p>Aún no has publicado vacantes. Ve a "Crear vacante" para empezar.</p></div>';
                return;
            }
            cont.innerHTML = vacantes.map(function (v) {
                var sal = formatoSalario(v.salario);
                return '' +
                '<div class="vacancy-card">' +
                    '<div class="vacancy-top">' +
                        '<div class="vacancy-headtext">' +
                            '<div class="vacancy-title">' + esc(v.titulo) + '</div>' +
                            '<div class="vacancy-company">' +
                                (v.activa ? 'Activa' : 'Inactiva') + ' · ' +
                                v.num_postulaciones + ' postulación(es)' +
                            '</div>' +
                        '</div>' +
                        (sal ? '<span class="tag salary">' + sal + '</span>' : '') +
                    '</div>' +
                    '<div class="vacancy-desc">' + esc(v.descripcion) + '</div>' +
                    '<div class="vacancy-actions">' +
                        '<button class="btn-secondary btn-ver-candidatos" data-id="' + v.id_vacante +
                            '" data-titulo="' + esc(v.titulo) + '">Ver candidatos</button>' +
                    '</div>' +
                '</div>';
            }).join("");

            cont.querySelectorAll(".btn-ver-candidatos").forEach(function (btn) {
                btn.addEventListener("click", function () {
                    verCandidatos(this.getAttribute("data-id"), this.getAttribute("data-titulo"));
                });
            });
        })
        .catch(function (e) {
            cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i>' +
                '<p>No se pudo conectar con el servidor.</p></div>';
            console.error(e);
        });
}

function verCandidatos(idVacante, titulo) {
    // Cambiar a la sección de candidatos
    document.querySelectorAll(".nav-item[data-seccion]").forEach(function (i) { i.classList.remove("active"); });
    mostrarSeccion("empresa", "candidatos");

    var tit = document.getElementById("candidatos-titulo");
    if (tit) tit.textContent = "Candidatos · " + titulo;

    var cont = document.getElementById("listaCandidatos");
    cont.innerHTML = '<div class="loading">Cargando…</div>';

    fetch(API_URL + "/api/vacantes/" + idVacante + "/postulaciones", { credentials: "include" })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            var posts = (data && data.postulaciones) || [];
            if (posts.length === 0) {
                cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-user-slash"></i>' +
                    '<p>Aún no hay candidatos para esta vacante.</p></div>';
                return;
            }
            var filas = posts.map(function (p) {
                return '<tr>' +
                    '<td>' + esc(p.nombre_completo) + '</td>' +
                    '<td>' + esc(p.especialidad || "—") + '</td>' +
                    '<td>' + esc(p.correo) + '</td>' +
                    '<td><span class="badge ' + esc(p.estado) + '">' + esc(p.estado) + '</span></td>' +
                    '<td>' +
                        '<select class="sel-estado" data-id="' + p.id_postulacion + '" style="padding:6px 10px;border-radius:8px;border:1px solid #e0ddd8;font-family:Poppins,sans-serif;font-size:0.8rem;">' +
                            ['pendiente','revisado','aceptado','rechazado'].map(function (e) {
                                return '<option value="' + e + '"' + (e === p.estado ? ' selected' : '') + '>' + e + '</option>';
                            }).join('') +
                        '</select>' +
                    '</td>' +
                '</tr>';
            }).join("");
            cont.innerHTML = '<table class="simple-table"><thead><tr>' +
                '<th>Nombre</th><th>Especialidad</th><th>Correo</th><th>Estado</th><th>Cambiar estado</th>' +
                '</tr></thead><tbody>' + filas + '</tbody></table>';

            // Cambiar estado
            cont.querySelectorAll(".sel-estado").forEach(function (sel) {
                sel.addEventListener("change", function () {
                    var id = this.getAttribute("data-id");
                    var estado = this.value;
                    fetch(API_URL + "/api/postulaciones/" + id + "/estado", {
                        method: "PUT", credentials: "include",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ estado: estado })
                    })
                    .then(function (r) { return r.json().then(function (d) { return { ok: r.ok, d: d }; }); })
                    .then(function (r) {
                        if (!r.ok) alert(r.d.error || "Error al cambiar estado");
                        else {
                            // actualizar el badge de la fila
                            var fila = sel.closest("tr");
                            var badge = fila.querySelector(".badge");
                            if (badge) { badge.className = "badge " + estado; badge.textContent = estado; }
                        }
                    })
                    .catch(function () { alert("No se pudo conectar con el servidor."); });
                });
            });
        })
        .catch(function (e) {
            cont.innerHTML = '<div class="empty-state"><i class="fa-solid fa-triangle-exclamation"></i>' +
                '<p>No se pudo conectar con el servidor.</p></div>';
            console.error(e);
        });
}

// Tabla: qué función inicializa cada vista
const inicializadores = {
    "login":    initLogin,
    "register": initRegister,
    "dashboard-candidato": initDashboardCandidato,
    "dashboard-empresa":   initDashboardEmpresa,
};

/* ============================================================
   ROUTER
   ============================================================ */
async function cargarVista(nombre) {
    const archivo = routes[nombre];

    if (!archivo) {
        app.innerHTML = '<div style="text-align:center;padding:40px;color:#888">' +
            'Pantalla "<b>' + nombre + '</b>" no encontrada.</div>';
        return;
    }

    try {
        const res = await fetch(archivo);
        if (!res.ok) throw new Error("No se pudo cargar " + archivo);
        const html = await res.text();

        // Si la vista NO es un dashboard, quitar el modo dashboard del body
        if (nombre.indexOf("dashboard") === -1) {
            document.body.classList.remove("dashboard-mode");
        }

        app.innerHTML = html;

        // Llama al inicializador de la vista (la lógica está en este archivo)
        const initFn = inicializadores[nombre];
        if (typeof initFn === "function") initFn();

    } catch (err) {
        app.innerHTML = '<div style="text-align:center;padding:40px;color:#c0504f">' +
            'Error cargando la pantalla.</div>';
        console.error(err);
    }
}

function manejarRuta() {
    const nombre = window.location.hash.replace("#", "") || RUTA_INICIAL;
    cargarVista(nombre);
}

window.addEventListener("hashchange", manejarRuta);
window.addEventListener("DOMContentLoaded", manejarRuta);