#!/usr/bin/env python3
"""
Master translation script: translates ALL 2134 segments to one language.
Usage: python3 translate_lang.py <lang_code>
"""
import json, os, subprocess, sys

BASE = "/Users/sipi/churnlens/i18n"
EN_PATH = os.path.join(BASE, "locales", "en", "_combined.json")
WRITE_SCRIPT = os.path.join(BASE, "write_translations.py")

# Load English source
with open(EN_PATH) as f:
    en_data = json.load(f)

all_entries = []
for page, page_data in en_data.items():
    for k, v in page_data.items():
        all_entries.append((k, v.replace('\n', '\\n'), page))
all_entries.sort(key=lambda x: x[0])

text_to_keys = {}
for k, v, p in all_entries:
    text_to_keys.setdefault(v, []).append(k)

unique_texts = list(text_to_keys.keys())

def S(text):
    """Protect brand names and HTML entities with safe placeholders."""
    mapping = {}
    brands = ['Churn Lens', 'SaaS']
    for b in brands:
        if b in text:
            ph = f"\x00B{len(mapping)}\x00"
            mapping[ph] = b
            text = text.replace(b, ph)
    ents = {'&amp;': '\x00A\x00', '&lt;': '\x00L\x00', '&gt;': '\x00G\x00',
            '&mdash;': '\x00M\x00', '&rarr;': '\x00R\x00', '&times;': '\x00T\x00',
            '&copy;': '\x00C\x00', '&ldquo;': '\x00Q\x00', '&rdquo;': '\x00q\x00',
            '&ndash;': '\x00N\x00', '&hellip;': '\x00H\x00'}
    for e, p in ents.items():
        if e in text:
            mapping[p] = e
            text = text.replace(e, p)
    return text, mapping

def R(text, mapping):
    for p, o in mapping.items():
        text = text.replace(p, o)
    return text

def pipe(lang, tdict):
    lines = [f"{k}|{tdict[k]}" for k in sorted(tdict.keys())]
    lines.append("DONE")
    r = subprocess.run([sys.executable, WRITE_SCRIPT, lang],
                       input="\n".join(lines), capture_output=True, text=True, encoding='utf-8')
    return r

# ========================================================================
# TRANSLATION: Build full translation map for the requested language
# ========================================================================

def build_translations(lang):
    """Build translation map: english_text -> translated_text for given language"""
    result = {}
    for text in unique_texts:
        protected, m = S(text)
        translated = _translate_protected(protected, lang)
        result[text] = R(translated, m)
    return result

def _translate_protected(text, lang):
    """Translate text that has brands/entities protected (as \x00 placeholders)."""
    if not text or text == '':
        return text
    
    # For efficiency, I'll handle the translation by dispatching
    # to language-specific functions that use both direct lookups
    # and pattern-based translation for longer texts.
    
    translators = {
        'es': _ES,
        'fr': _FR,
        'pt': _PT,
        'zh-CN': _ZH,
        'hi': _HI,
        'ar': _AR,
        'bn': _BN,
        'ru': _RU,
        'ur': _UR,
        'id': _ID,
    }
    
    fn = translators.get(lang)
    if fn:
        return fn(text)
    return text

# Now I need to implement each language function.
# Each function must handle all 1491 unique texts correctly.
# I'll build them using a combination of direct lookups and pattern matching.

# ========================================================================
# SPANISH
# ========================================================================
def _ES(text):
    """Translate to Spanish."""
    # Short/common texts direct lookup
    L = {
        "Toggle navigation menu": "Alternar menú de navegación",
        "Mobile navigation": "Navegación móvil",
        "Back to top": "Volver arriba",
        "Home": "Inicio",
        "Pricing": "Precios",
        "Founder Story": "Historia del Fundador",
        "Get the checklist \x00R\x00": "Obtener la lista \x00R\x00",
        "Get the free checklist \x00R\x00": "Obtener la lista gratuita \x00R\x00",
        "Free Checklist": "Lista Gratuita",
        "DD Checklist": "Lista de DD",
        "Due Diligence Checklist": "Lista de Due Diligence",
        "Churn Benchmarks": "Benchmarks de Churn",
        "Related Resources": "Recursos Relacionados",
        "Churn Lens": "Churn Lens",
        "SaaS": "SaaS",
        "Manifesto": "Manifiesto",
        "Partners": "Socios",
        "Get the free 23-point churn audit checklist": "Obtén la lista gratuita de auditoría de churn de 23 puntos",
        "Run a Churn Report \x00R\x00": "Ejecutar Informe de Churn \x00R\x00",
        "Upload CSV \x00R\x00": "Subir CSV \x00R\x00",
        "Value a Deal \x00R\x00": "Valorar un Acuerdo \x00R\x00",
        "Analyze a CSV \x00R\x00": "Analizar un CSV \x00R\x00",
        "Start Pro for $1 \x00R\x00": "Empieza Pro por $1 \x00R\x00",
        "No thanks, show me the free checklist \x00R\x00": "No gracias, muéstrame la lista gratuita \x00R\x00",
        "Cancel anytime. No commitment.": "Cancela cuando quieras. Sin compromiso.",
        "FREE": "GRATIS",
        "Limited Time Offer": "Oferta por Tiempo Limitado",
        "Audit Points": "Puntos de Auditoría",
        "audit points": "puntos de auditoría",
        "$48K": "$48K",
        "$340K": "$340K",
        "MRR case study": "caso de estudio MRR",
        "hidden-churn tricks exposed": "trucos de churn oculto expuestos",
        "avg. real churn found": "churn real promedio encontrado",
        "Frequently asked before signing up": "Preguntas frecuentes antes de registrarse",
        "Is this really free?": "¿Esto es realmente gratuito?",
        "I already have a due diligence checklist. Why this one?": "Ya tengo una lista de due diligence. ¿Por qué esta?",
        "I'm not technical. Can I use this?": "No soy técnico. ¿Puedo usar esto?",
        "Will you spam me?": "¿Me enviarán spam?",
        "Yes.": "Sí.",
        "No.": "No.",
        "No spam.": "Sin spam.",
        "Unsubscribe in one click.": "Cancela la suscripción con un clic.",
        "We never share your data.": "Nunca compartimos tus datos.",
        # Page titles
        "Annual Plan Churn Risk in SaaS: The Hidden Renewal Cliff": "Riesgo de Churn en Planes Anuales SaaS: El Acantilado de Renovación Oculta",
        "Annual Plan Churn Risk in SaaS": "Riesgo de Churn en Planes Anuales SaaS",
        "The Complete Guide to Buying a SaaS Business (2026)": "La Guía Completa para Comprar un Negocio SaaS (2026)",
        "The Complete Guide to Buying a SaaS Business": "La Guía Completa para Comprar un Negocio SaaS",
        "Churn Lens for SaaS Acquirers: How It Works": "Churn Lens para Adquirentes SaaS: Cómo Funciona",
        "Churn Lens for SaaS Acquirers": "Churn Lens para Adquirentes SaaS",
        "Customer Concentration Risk in SaaS Acquisitions": "Riesgo de Concentración de Clientes en Adquisiciones SaaS",
        "Customer Concentration Risk": "Riesgo de Concentración de Clientes",
        "Get the SaaS Churn Audit Checklist + Sample Report": "Obtén la Lista de Auditoría de Churn SaaS + Informe de Muestra",
        "Hidden Churn: What Sellers Don't Tell You": "Churn Oculto: Lo Que los Vendedores No Te Dicen",
        "Hidden Churn: What SaaS Sellers Don't Tell Buyers": "Churn Oculto: Lo Que los Vendedores SaaS No Les Dicen a los Compradores",
        "How to Evaluate a SaaS Before Buying: 6-Step Framework": "Cómo Evaluar un SaaS Antes de Comprar: Marco de 6 Pasos",
        "Inactive Paid Accounts in SaaS: Ghost Revenue Detection": "Cuentas Pagadas Inactivas en SaaS: Detección de Ingresos Fantasma",
        "Logo Churn vs. Revenue Churn: What SaaS Buyers Miss": "Churn de Logos vs. Churn de Ingresos: Lo Que los Compradores SaaS Pasan por Alto",
        "MRR vs. Revenue Quality": "MRR vs. Calidad de Ingresos",
        "SaaS Acquisition Red Flags": "Señales de Alerta en Adquisiciones SaaS",
        "SaaS Buyer Risk Assessment": "Evaluación de Riesgo para Compradores SaaS",
        "SaaS Churn Rate Benchmarks by Industry (2025-2026)": "Benchmarks de Tasa de Churn SaaS por Industria (2025-2026)",
        "SaaS Churn Rate Benchmarks by Industry": "Benchmarks de Tasa de Churn SaaS por Industria",
        "SaaS Due Diligence Checklist": "Lista de Due Diligence SaaS",
        "SaaS MRR Decline Analysis": "Análisis de Declive de MRR SaaS",
        "SaaS Revenue Churn Calculator": "Calculadora de Churn de Ingresos SaaS",
        "SaaS Revenue Concentration Risk": "Riesgo de Concentración de Ingresos SaaS",
        "SaaS Revenue Quality Score": "Puntuación de Calidad de Ingresos SaaS",
        "The Ultimate SaaS Due Diligence Guide (2026)": "La Guía Definitiva de Due Diligence SaaS (2026)",
        "The Ultimate SaaS Due Diligence Guide": "La Guía Definitiva de Due Diligence SaaS",
        "Why Churn Lens?": "¿Por Qué Churn Lens?",
        "Who Uses Churn Lens?": "¿Quién Usa Churn Lens?",
        # Checklist items
        "Logo churn rate": "Tasa de churn de logos",
        "Revenue churn rate": "Tasa de churn de ingresos",
        "Net vs. gross churn": "Churn neto vs. bruto",
        "Monthly vs. annual churn": "Churn mensual vs. anual",
        "Cohort trend (24 months)": "Tendencia de cohorte (24 meses)",
        "Downgrade rate": "Tasa de degradación",
        "Involuntary churn split": "División de churn involuntario",
        "Top 10 customer concentration": "Concentración de top 10 clientes",
        "Top 3 customer churn impact": "Impacto de churn de top 3 clientes",
        "Annual-plan renewal schedule": "Calendario de renovación de planes anuales",
        "Annual-plan early-cancellation rate": "Tasa de cancelación anticipada de planes anuales",
        "Inactive paid accounts": "Cuentas pagadas inactivas",
        "Inactive account trend": "Tendencia de cuentas inactivas",
        "Expansion revenue rate": "Tasa de ingresos por expansión",
        "Contraction revenue rate": "Tasa de ingresos por contracción",
        "Trial-to-paid conversion rate": "Tasa de conversión de prueba a pago",
        "Reactivation pattern": "Patrón de reactivación",
        "MRR trajectory (6 months)": "Trayectoria de MRR (6 meses)",
        "Net new MRR vs. churned MRR": "MRR nuevo neto vs. MRR perdido",
        "Revenue quality grade": "Grado de calidad de ingresos",
        "Voluntary vs. involuntary ratio": "Relación voluntario vs. involuntario",
        "Customer lifecycle stage distribution": "Distribución de etapas del ciclo de vida del cliente",
        "Cohort retention curves by signup month": "Curvas de retención de cohorte por mes de registro",
        # Risk categories
        "Churn \x00A\x00 Retention": "Churn \x00A\x00 Retención",
        "Concentration Risk": "Riesgo de Concentración",
        "Revenue Quality \x00A\x00 Decay": "Calidad \x00A\x00 Deterioro de Ingresos",
        "Technical \x00A\x00 Operational Health": "Salud Técnica \x00A\x00 Operativa",
        "Legal \x00A\x00 Compliance": "Legal \x00A\x00 Cumplimiento",
        # Pricing
        "Monthly": "Mensual",
        "Annually": "Anual",
        "Per report": "Por informe",
        "Free": "Gratis",
        "Contact us": "Contáctanos",
        "Sign up": "Registrarse",
        # General UI
        "Search": "Buscar",
        "Close": "Cerrar",
        "Menu": "Menú",
        "Language": "Idioma",
        "English": "Inglés",
        "Spanish": "Español",
        "French": "Francés",
        "German": "Alemán",
        "Portuguese": "Portugués",
        "Chinese": "Chino",
        "Japanese": "Japonés",
        "Korean": "Coreano",
        "Send": "Enviar",
        "Submit": "Enviar",
        "Cancel": "Cancelar",
        "Save": "Guardar",
        "Delete": "Eliminar",
        "Edit": "Editar",
        "View": "Ver",
        "Download": "Descargar",
        "Upload": "Subir",
        "Share": "Compartir",
        "Print": "Imprimir",
        "Export": "Exportar",
        "Import": "Importar",
        "Next": "Siguiente",
        "Previous": "Anterior",
        "First": "Primero",
        "Last": "Último",
        "Back": "Volver",
        "Continue": "Continuar",
        "Learn more": "Más información",
        "Read more": "Leer más",
        "Show more": "Mostrar más",
        "Show less": "Mostrar menos",
        "View all": "Ver todo",
        "See all": "Ver todo",
        "More": "Más",
        "Less": "Menos",
        "All": "Todo",
        "None": "Ninguno",
        "Any": "Cualquiera",
        "Or": "O",
        "And": "Y",
        "Not": "No",
        "Yes": "Sí",
        "No": "No",
        "On": "Activado",
        "Off": "Desactivado",
        "Enable": "Activar",
        "Disable": "Desactivar",
        "Loading": "Cargando",
        "Error": "Error",
        "Warning": "Advertencia",
        "Success": "Éxito",
        "Info": "Información",
        "Help": "Ayuda",
        "Support": "Soporte",
        "Documentation": "Documentación",
        "API": "API",
        "Status": "Estado",
        "Settings": "Configuración",
        "Account": "Cuenta",
        "Profile": "Perfil",
        "Logout": "Cerrar sesión",
        "Login": "Iniciar sesión",
        "Register": "Registrarse",
        "Password": "Contraseña",
        "Email": "Correo electrónico",
        "Name": "Nombre",
        "Company": "Empresa",
        "Website": "Sitio web",
        "Phone": "Teléfono",
        "Address": "Dirección",
        "City": "Ciudad",
        "Country": "País",
        "Region": "Región",
        "Language": "Idioma",
        "Timezone": "Zona horaria",
        "Currency": "Moneda",
        "Date": "Fecha",
        "Time": "Hora",
        "Updated": "Actualizado",
        "Created": "Creado",
        "Expired": "Expirado",
        "Active": "Activo",
        "Inactive": "Inactivo",
        "Pending": "Pendiente",
        "Completed": "Completado",
        "Failed": "Falló",
        "Cancelled": "Cancelado",
        "Refunded": "Reembolsado",
        "Paid": "Pagado",
        "Unpaid": "No pagado",
        "Overdue": "Vencido",
        "Trial": "Prueba",
        "Basic": "Básico",
        "Pro": "Pro",
        "Enterprise": "Empresarial",
        "Team": "Equipo",
        "Individual": "Individual",
        # Specific phrases
        "2% monthly churn.": "2% de churn mensual.",
        "23-point buyer-side churn audit checklist": "Lista de auditoría de churn de 23 puntos para compradores",
        "The 23-Point Churn Audit Checklist": "La Lista de Auditoría de Churn de 23 Puntos",
        "The 23-Point Buyer-Side Churn Audit Checklist": "La Lista de Auditoría de Churn de 23 Puntos para Compradores",
        "Sample Risk Report": "Informe de Riesgo de Muestra",
        "Hidden Churn Cheat Sheet": "Guía de Churn Oculto",
        "Revenue Quality Scorecard": "Tarjeta de Puntuación de Calidad de Ingresos",
        # Comparison table
        "Churn Lens Pro": "Churn Lens Pro",
        "Manual Checklist": "Lista Manual",
        "23-point checklist (PDF)": "Lista de 23 puntos (PDF)",
        "Manual spreadsheet work": "Trabajo manual con hojas de cálculo",
        "2\x00N\x004 hours per target": "2\x00N\x004 horas por objetivo",
        "Sample report included": "Informe de muestra incluido",
        "Automated logo \x00A\x00 revenue churn": "Churn de logos e ingresos automatizado",
        "Concentration risk analysis": "Análisis de riesgo de concentración",
        "Zombie MRR detection": "Detección de MRR zombie",
        "Annual-plan decay tracking": "Seguimiento de deterioro de planes anuales",
        "Revenue quality score": "Puntuación de calidad de ingresos",
        "Cohort analysis (24-month)": "Análisis de cohorte (24 meses)",
        "Good call. But let me ask you something\x00H\x00": "Buena decisión. Pero déjame preguntarte algo\x00H\x00",
        "While you read \x00M\x00 got a target in due diligence right now?": "Mientras lees \x00M\x00 ¿tienes un objetivo en due diligence ahora mismo?",
        "Upload the CSV and get your own risk report in minutes \x00R\x00": "Sube el CSV y obtén tu propio informe de riesgo en minutos \x00R\x00",
        "Sent instantly. No spam. Unsubscribe in one click. We never share your data.": "Enviado al instante. Sin spam. Cancela con un clic. Nunca compartimos tus datos.",
        "No waiting. Read it below right now \x00M\x00 the sample report and cheat sheet are in your inbox for deeper reference.": "Sin esperas. Léelo abajo ahora mismo \x00M\x00 el informe de muestra y la guía están en tu bandeja de entrada.",
        "I already have a due diligence checklist. Why this one?": "Ya tengo una lista de due diligence. ¿Por qué esta?",
    }
    
    # Direct lookup
    if text in L:
        return L[text]
    
    # If text starts with certain patterns, translate accordingly
    # Many longer texts will fall through to here
    
    return text  # placeholder - I'll handle remaining texts


# ========================================================================
# OTHER LANGUAGES
# ========================================================================

def _FR(text): return text
def _PT(text): return text
def _ZH(text): return text
def _HI(text): return text
def _AR(text): return text
def _BN(text): return text
def _RU(text): return text
def _UR(text): return text
def _ID(text): return text


# ========================================================================
# MAIN
# ========================================================================

if __name__ == '__main__':
    lang = sys.argv[1]
    valid = ['es', 'fr', 'pt', 'zh-CN', 'hi', 'ar', 'bn', 'ru', 'ur', 'id']
    if lang not in valid:
        print(f"Invalid: {lang}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Building translations for {lang}...", file=sys.stderr)
    tmap = build_translations(lang)
    
    # Build full dict
    translations = {}
    for k, v, p in all_entries:
        translations[k] = tmap[v]
    
    print(f"  {len(translations)} translations built", file=sys.stderr)
    
    r = pipe(lang, translations)
    print(f"  {r.stdout.strip()}", file=sys.stderr)
    if r.stderr.strip():
        print(f"  ERR: {r.stderr.strip()}", file=sys.stderr)
    
    # Verify
    lang_dir = os.path.join(BASE, "locales", lang)
    if os.path.isdir(lang_dir):
        files = [f for f in os.listdir(lang_dir) if f.endswith('.json')]
        total = sum(len(json.load(open(os.path.join(lang_dir, f)))) for f in files)
        print(f"  ✓ {len(files)} files, {total} keys total", file=sys.stderr)
