
import json
from pathlib import Path

import streamlit as st
from ai_agent import generate_post
from image_generator import create_post_image

st.set_page_config(
    page_title="Dream Data Labs Challenge",
    page_icon="🎨"
)

st.title("Social Media Post Generator")
st.write("Dream Data Labs Internship Challenge")

# Projenin ana klasörü
BASE_DIR = Path(__file__).resolve().parent

# Marka isimleri ve JSON dosyaları
brands = {
    "ABA Psikoloji": "aba_psikoloji.json",
    "ABA Eğitim": "aba_egitim.json",
    "Education for Innovation": "e4i.json",
    "Design House Global": "design_house_global.json"
}

# Kullanıcının marka seçimi
selected_brand = st.selectbox(
    "Bir marka seçin:",
    list(brands.keys())
)

# Kullanıcının post konusu
topic = st.text_input(
    "Post konusu:",
    placeholder="Örn: Sınav kaygısıyla başa çıkma"
)

# Seçilen markanın Brand Kit dosyasını oku
brand_path = BASE_DIR / "brand_kits" / brands[selected_brand]

with open(brand_path, encoding="utf-8") as file:
    brand_kit = json.load(file)

brand_id = brand_kit["brand_id"]

# Post Library dosyasını oku
posts_path = BASE_DIR / "post_library" / "posts.json"

with open(posts_path, encoding="utf-8") as file:
    all_posts = json.load(file)

# Yalnızca seçilen markanın postlarını bul
brand_posts = [
    post for post in all_posts
    if post["brand_id"] == brand_kit["brand_id"]
]

# Sonuçları ekranda göster
st.subheader("Seçilen Bilgiler")
st.write(f"Marka: {brand_kit['brand_name']}")

if topic.strip():
    st.write(f"Konu: {topic}")
else:
    st.info("Lütfen bir post konusu girin.")

st.subheader("Brand Kit Bilgileri")

st.write(f"Dil: {brand_kit['language']}")
st.write(f"Ana renk: {brand_kit['colors']['primary']}")
st.write(f"Başlık fontu: {brand_kit['fonts']['heading']}")

st.subheader("Post Library")

st.write(f"Bu markaya ait {len(brand_posts)} örnek post bulundu.")

for post in brand_posts:
    with st.expander(post["headline"]):
        st.write(f"Konu: {post['topic']}")
        st.write(f"Tür: {post['post_type']}")
        st.write(f"İçerik: {post['body']}")
        st.write(f"CTA: {post['cta']}")


# AI ile yeni sosyal medya içeriği üret
st.subheader("AI ile İçerik Üret")

if st.button("✨ İçerik Üret"):
    if not topic.strip():
        st.warning("Lütfen önce bir post konusu girin.")
    else:
        try:
            with st.spinner("Gemini içerik üretiyor..."):
                generated_post = generate_post(brand_id, topic)

            # Üretilen içeriği sonraki ekran yenilemelerinde koru
            st.session_state["generated_post"] = generated_post
            st.session_state.pop("image_path", None)
            st.session_state["generated_brand"] = brand_id
            st.session_state["generated_topic"] = topic

        
        except Exception as error:
            error_message = str(error)

            if "503" in error_message:
                st.warning(
                    "Gemini servisi şu anda yoğun. "
                    "Lütfen biraz bekleyip tekrar deneyin."
                )

            elif "429" in error_message:
                st.warning(
                    "Gemini API kullanım limitine ulaşıldı. "
                    "Lütfen daha sonra tekrar deneyin."
                )

            else:
                st.error(
                    "İçerik oluşturulurken bir hata meydana geldi. "
                    "Lütfen tekrar deneyin."
                )

# Daha önce üretilmiş içerik varsa ekranda göster
if "generated_post" in st.session_state:
    if (
        st.session_state["generated_brand"] == brand_id
        and st.session_state["generated_topic"] == topic
    ):
        post = st.session_state["generated_post"]

        st.success("İçerik başarıyla üretildi!")

        st.markdown("**Başlık**")
        st.write(post["headline"])

        st.markdown("**Görsel Metni**")
        st.write(post["body"])

        st.markdown("**Instagram Açıklaması (Caption)**")
        st.write(post["caption"])

        st.markdown("**CTA**")
        st.write(post["cta"])

        st.markdown("**Hashtag'ler**")
        st.write(" ".join(post["hashtags"]))

# AI tarafından üretilmiş içerik için görsel oluştur
if "generated_post" in st.session_state:
    if (
        st.session_state["generated_brand"] == brand_id
        and st.session_state["generated_topic"] == topic
    ):
        st.subheader("Görsel Post Oluştur")

        if st.button("🎨 Görsel Oluştur"):
            try:
                with st.spinner("Görsel hazırlanıyor..."):
                    image_path = create_post_image(
                        brand_kit=brand_kit,
                        post_data=st.session_state["generated_post"],
                        output_filename=f"{brand_id}_generated.png"
                    )

                st.session_state["image_path"] = str(image_path)

            except Exception as error:
                st.error(f"Görsel oluşturulamadı: {error}")

        # Görsel oluşturulduysa ekranda göster
        if "image_path" in st.session_state:
            image_path = Path(st.session_state["image_path"])

            if image_path.exists():
                st.image(str(image_path), caption="Oluşturulan Instagram Postu")

                with open(image_path, "rb") as file:
                    st.download_button(
                        label="⬇️ Görseli İndir (PNG)",
                        data=file.read(),
                        file_name=image_path.name,
                        mime="image/png"
                    )
