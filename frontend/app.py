import streamlit as st
import requests
from PIL import Image
import io
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from remedy_generator import get_remedy



# ── Config ───────────────────────────────────────────────────────────────────
BACKEND_URL = "http://localhost:8000"

st.set_page_config(
    page_title="PlantAI",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0d0d0d;
    color: #e8e8e8;
  }

  .block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 720px;
  }

  #MainMenu, footer, header { visibility: hidden; }

  .header-wrap {
    text-align: center;
    margin-bottom: 2.5rem;
  }
  .header-wrap .logo {
    font-size: 2.6rem;
    font-weight: 600;
    letter-spacing: -1px;
    color: #f0f0f0;
  }
  .header-wrap .logo span { color: #5bde8a; }
  .header-wrap .tagline {
    font-size: 0.9rem;
    color: #666;
    font-weight: 300;
    margin-top: 0.3rem;
    letter-spacing: 0.5px;
  }

  .upload-zone {
    border: 1.5px dashed #2e2e2e;
    border-radius: 16px;
    padding: 2rem 1.5rem;
    text-align: center;
    background: #141414;
    margin-bottom: 1.5rem;
    transition: border-color 0.2s;
  }
  .upload-zone:hover { border-color: #5bde8a; }

  .card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1rem;
  }
  .card-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.4rem;
  }
  .card-value {
    font-size: 1.55rem;
    font-weight: 600;
    color: #f0f0f0;
    line-height: 1.2;
  }
  .card-value.green  { color: #5bde8a; }
  .card-value.yellow { color: #f5c842; }
  .card-value.red    { color: #f5665d; }
  .card-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #444;
    margin-top: 0.25rem;
  }

  .bar-wrap {
    background: #1e1e1e;
    border-radius: 99px;
    height: 6px;
    margin-top: 0.8rem;
    overflow: hidden;
  }
  .bar-fill {
    height: 6px;
    border-radius: 99px;
    background: linear-gradient(90deg, #5bde8a, #30c96e);
    transition: width 0.6s ease;
  }
  .bar-fill.yellow { background: linear-gradient(90deg, #f5c842, #e0a800); }
  .bar-fill.red    { background: linear-gradient(90deg, #f5665d, #d93b31); }

  .score-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.55rem 0;
    border-bottom: 1px solid #1c1c1c;
  }
  .score-row:last-child { border-bottom: none; }
  .score-name {
    font-size: 0.82rem;
    color: #bbb;
    flex: 1;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    padding-right: 1rem;
  }
  .score-pct {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem;
    color: #5bde8a;
    min-width: 52px;
    text-align: right;
  }
  .score-bar-wrap {
    width: 100px;
    background: #1e1e1e;
    border-radius: 99px;
    height: 4px;
    margin: 0 0.8rem;
    overflow: hidden;
  }
  .score-bar-fill {
    height: 4px;
    border-radius: 99px;
    background: #5bde8a44;
  }

  .divider {
    border: none;
    border-top: 1px solid #1f1f1f;
    margin: 1.5rem 0;
  }

  .pill {
    display: inline-block;
    padding: 0.2rem 0.75rem;
    border-radius: 99px;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.5px;
  }
  .pill.healthy  { background: #1a3d28; color: #5bde8a; }
  .pill.diseased { background: #3d1a1a; color: #f5665d; }

  /* ── Severity pills ── */
  .pill.sev-low    { background: #1a3d28; color: #5bde8a; }
  .pill.sev-medium { background: #3d3217; color: #f5c842; }
  .pill.sev-high   { background: #3d1a1a; color: #f5665d; }

  /* ── Remedy card styles ── */
  .remedy-card {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1rem;
  }
  .remedy-section-title {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.75rem;
  }
  .remedy-overview {
    font-size: 0.88rem;
    color: #aaa;
    line-height: 1.6;
    margin-bottom: 0;
  }
  .remedy-item {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.4rem 0;
    font-size: 0.84rem;
    color: #ccc;
    border-bottom: 1px solid #1c1c1c;
    line-height: 1.4;
  }
  .remedy-item:last-child { border-bottom: none; }
  .remedy-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #5bde8a;
    margin-top: 0.35rem;
    flex-shrink: 0;
  }
  .remedy-dot.yellow { background: #f5c842; }
  .remedy-dot.blue   { background: #5bc8de; }
  .expert-box {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #f5c842;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    font-size: 0.83rem;
    color: #aaa;
    line-height: 1.5;
  }

  /* ── GradCAM section styles ── */
  .gradcam-label {
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #555;
    margin-bottom: 0.5rem;
    text-align: center;
  }
  .gradcam-caption {
    font-size: 0.72rem;
    color: #444;
    text-align: center;
    margin-top: 0.4rem;
  }
  .gradcam-wrap {
    background: #141414;
    border: 1px solid #1f1f1f;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
  }

  div[data-testid="stButton"] > button {
    background: #5bde8a;
    color: #0d0d0d;
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 600;
    padding: 0.65rem 2rem;
    width: 100%;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
    letter-spacing: 0.3px;
  }
  div[data-testid="stButton"] > button:hover {
    background: #4dcc7c;
    transform: translateY(-1px);
  }

  img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def clean_label(raw: str) -> str:
    parts = raw.split("___")
    if len(parts) == 2:
        plant, condition = parts
        plant     = plant.replace("_", " ").replace(",", "").strip()
        condition = condition.replace("_", " ").strip()
        return f"{condition} ({plant})"
    return raw.replace("_", " ")


def confidence_color(conf: float) -> str:
    if conf >= 80:
        return "green"
    elif conf >= 50:
        return "yellow"
    return "red"


def is_healthy(label: str) -> bool:
    return "healthy" in label.lower()


def call_backend(image_bytes: bytes, filename: str) -> dict:
    resp = requests.post(
        f"{BACKEND_URL}/predict",
        files={"file": (filename, image_bytes, "image/jpeg")},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


# ── NEW: GradCAM backend call ─────────────────────────────────────────────────
def call_gradcam(image_bytes: bytes, filename: str) -> Image.Image | None:
    """Call /gradcam endpoint and return heatmap as PIL Image, or None on failure."""
    try:
        resp = requests.post(
            f"{BACKEND_URL}/gradcam",
            files={"file": (filename, image_bytes, "image/jpeg")},
            timeout=30,
        )
        if resp.status_code == 200:
            return Image.open(io.BytesIO(resp.content))
        return None
    except Exception:
        return None


# ── Render remedy card ────────────────────────────────────────────────────────
def render_remedy_card(remedy: dict):
    """Render the LLM-generated remedy guide as a styled card."""

    severity = remedy.get("severity", "Medium")
    sev_class = {"Low": "sev-low", "Medium": "sev-medium", "High": "sev-high"}.get(severity, "sev-medium")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Header row ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:1rem;">
      <div class="card-label" style="margin-bottom:0;">🌿 Health Guide & Remedies</div>
      <span class="pill {sev_class}">⚠ {severity} Severity</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Overview ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="remedy-card">
      <div class="remedy-section-title">Overview</div>
      <div class="remedy-overview">{remedy.get("overview", "No overview available.")}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 3-column grid: Remedies | Dietary Tips | Lifestyle ────────────────────
    col1, col2, col3 = st.columns(3, gap="small")

    with col1:
        items_html = "".join([
            f'<div class="remedy-item"><div class="remedy-dot"></div><div>{item}</div></div>'
            for item in remedy.get("remedies", [])
        ])
        st.markdown(f"""
        <div class="remedy-card" style="height:100%;">
          <div class="remedy-section-title">💊 Remedies</div>
          {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col2:
        items_html = "".join([
            f'<div class="remedy-item"><div class="remedy-dot yellow"></div><div>{item}</div></div>'
            for item in remedy.get("dietary_tips", [])
        ])
        st.markdown(f"""
        <div class="remedy-card" style="height:100%;">
          <div class="remedy-section-title">🌱 Soil & Nutrition</div>
          {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col3:
        items_html = "".join([
            f'<div class="remedy-item"><div class="remedy-dot blue"></div><div>{item}</div></div>'
            for item in remedy.get("lifestyle_steps", [])
        ])
        st.markdown(f"""
        <div class="remedy-card" style="height:100%;">
          <div class="remedy-section-title">🔄 Prevention</div>
          {items_html}
        </div>
        """, unsafe_allow_html=True)

    # ── When to see expert ────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="expert-box">
      <strong style="color:#f5c842;">🩺 When to consult an expert</strong><br>
      {remedy.get("when_to_see_expert", "Consult an agronomist if symptoms worsen.")}
    </div>
    """, unsafe_allow_html=True)


# ── Layout ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="header-wrap">
  <div class="logo">Plant<span>AI</span></div>
  <div class="tagline">Leaf disease detection · EfficientNet-B0 · 38 classes</div>
</div>
""", unsafe_allow_html=True)

uploaded = st.file_uploader(
    label="Drop a leaf image here",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
)

if uploaded:
    col_img, col_btn = st.columns([3, 2], gap="large")

    with col_img:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, use_container_width=True)

    with col_btn:
        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card-label">File</div>
        <div style="font-size:0.85rem;color:#aaa;margin-bottom:1rem;
                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
          {uploaded.name}
        </div>
        <div class="card-label">Size</div>
        <div style="font-size:0.85rem;color:#aaa;margin-bottom:1.2rem;">
          {image.width} × {image.height} px
        </div>
        """, unsafe_allow_html=True)
        analyse = st.button("Analyse Leaf →")

    if analyse:
        with st.spinner("Running diagnosis..."):
            try:
                img_bytes = io.BytesIO()
                image.save(img_bytes, format="JPEG", quality=95)
                img_bytes = img_bytes.getvalue()

                start = time.time()
                result = call_backend(img_bytes, uploaded.name)
                elapsed = round((time.time() - start) * 1000)

                # ── Fetch GradCAM only for diseased plants ────────────────────
                heatmap_img = None
                pred_raw_check = result.get("predicted_class", "")
                if not is_healthy(pred_raw_check):
                    heatmap_img = call_gradcam(img_bytes, uploaded.name)

            except requests.exceptions.ConnectionError:
                st.error("⚠️  Cannot reach the backend. Make sure it's running on port 8000.")
                st.stop()
            except Exception as e:
                st.error(f"Something went wrong: {e}")
                st.stop()

        pred_raw   = result["predicted_class"]
        pred_label = clean_label(pred_raw)
        confidence = result["confidence"]
        all_scores = result["all_scores"]
        conf_color = confidence_color(confidence)
        health_tag = "healthy" if is_healthy(pred_raw) else "diseased"

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("<div class='card-label' style='margin-bottom:0.8rem'>Diagnosis</div>",
                    unsafe_allow_html=True)

        c1, c2 = st.columns([5, 2], gap="small")
        with c1:
            st.markdown(f"""
            <div class="card">
              <div class="card-label">Detected Condition</div>
              <div class="card-value">{pred_label}</div>
              <div class="card-sub">{pred_raw}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="card" style="text-align:center;">
              <div class="card-label">Status</div>
              <div style="margin-top:0.6rem;">
                <span class="pill {health_tag}">
                  {'✓ Healthy' if health_tag == 'healthy' else '✗ Diseased'}
                </span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        c3, c4 = st.columns(2, gap="small")
        with c3:
            bar_w = int(confidence)
            st.markdown(f"""
            <div class="card">
              <div class="card-label">Confidence</div>
              <div class="card-value {conf_color}">{confidence}%</div>
              <div class="bar-wrap">
                <div class="bar-fill {conf_color}" style="width:{bar_w}%"></div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="card">
              <div class="card-label">Inference Time</div>
              <div class="card-value">{elapsed}<span style="font-size:1rem;color:#666"> ms</span></div>
              <div class="card-sub">CPU · EfficientNet-B0</div>
            </div>
            """, unsafe_allow_html=True)

        top5 = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        max_score = top5[0][1] if top5 else 1

        rows_html = ""
        for name, pct in top5:
            bar_pct = int((pct / max_score) * 100) if max_score > 0 else 0
            label = clean_label(name)
            rows_html += (
                f'<div class="score-row">'
                f'<div class="score-name">{label}</div>'
                f'<div class="score-bar-wrap">'
                f'<div class="score-bar-fill" style="width:{bar_pct}%"></div>'
                f'</div>'
                f'<div class="score-pct">{pct}%</div>'
                f'</div>'
            )

        st.markdown(f"""
        <div class="card">
          <div class="card-label" style="margin-bottom:0.6rem">Top 5 Predictions</div>
          {rows_html}
        </div>
        """, unsafe_allow_html=True)

        # ── NEW: GradCAM heatmap (only shown for diseased plants) ────────────
        if heatmap_img is not None:
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("""
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.8rem;">
              <div class="card-label" style="margin-bottom:0;">🔥 GradCAM — Diseased Region Heatmap</div>
            </div>
            """, unsafe_allow_html=True)

            gc1, gc2 = st.columns(2, gap="small")
            with gc1:
                st.markdown('<div class="gradcam-label">Original</div>', unsafe_allow_html=True)
                st.image(image, use_container_width=True)
            with gc2:
                st.markdown('<div class="gradcam-label">Heatmap Overlay</div>', unsafe_allow_html=True)
                st.image(heatmap_img, use_container_width=True)

            st.markdown("""
            <div class="gradcam-caption">
              🔴 Red / yellow regions = areas the model focused on to make this diagnosis
            </div>
            """, unsafe_allow_html=True)

        # ── Remedy card (only for diseased plants) ────────────────────────────
        if not is_healthy(pred_raw):
            with st.spinner("Generating health guide..."):
                remedy = get_remedy(pred_raw)

            if "error" in remedy:
                st.warning(f"⚠️ Could not load remedies: {remedy['error']}")
            else:
                render_remedy_card(remedy)
        else:
            st.markdown("""
            <div class="remedy-card" style="text-align:center; padding: 2rem;">
              <div style="font-size:1.5rem; margin-bottom:0.5rem;">✅</div>
              <div style="color:#5bde8a; font-weight:600; margin-bottom:0.3rem;">Plant looks healthy!</div>
              <div style="font-size:0.83rem; color:#555;">No remedies needed. Keep up the good care.</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="upload-zone">
      <div style="font-size:2rem;margin-bottom:0.5rem">🌿</div>
      <div style="font-size:0.9rem;color:#555;">Upload a leaf image to begin diagnosis</div>
      <div style="font-size:0.75rem;color:#333;margin-top:0.3rem;">JPG · PNG · WEBP</div>
    </div>
    """, unsafe_allow_html=True)