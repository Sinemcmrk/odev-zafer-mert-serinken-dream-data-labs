# Dream Data Labs Challenge

Dream Data Labs staj değerlendirme görevi için geliştirilen Python ve Streamlit tabanlı sosyal medya gönderisi üretme MVP'si.

Kullanıcı bir marka ve konu seçer. Uygulama, markanın kurallarını ve örnek gönderilerini Gemini'ye aktararak başlık, görsel metni, Instagram açıklaması, CTA (eylem çağrısı) ve hashtag üretir. Pillow, başlık, görsel metni ve CTA'yı marka renkleri, logo ve dekoratif çizimlerle birleştirerek indirilebilir **1080×1080 PNG** oluşturur. Açıklama ve hashtag'ler arayüzde ayrıca gösterilir.

## Teknolojiler

| Teknoloji | Kullanım |
| --- | --- |
| Python | Uygulama mantığı ve dosya işlemleri |
| Streamlit | Marka/konu seçimi, sonuç gösterimi ve PNG indirme |
| Google Gen AI SDK (`google-genai`) | Gemini üzerinden yapılandırılmış JSON içerik üretimi |
| Pillow | Yerel, şablon tabanlı PNG oluşturma ve metin yerleşimi |
| python-dotenv | İçerik üretiminde ortam değişkenlerini yükleme |
| JSON | Marka kuralları, örnek gönderiler ve kayıtlı çıktılar |

Görseller yerel olarak Pillow ile çizilir; bir görsel üretim API'si kullanılmaz. Metin üreticisi `ai_agent.py` içinde `gemini-3.8-flash` modelini kullanacak şekilde tanımlıdır.

## Desteklenen markalar

| Marka | Kimlik | Varsayılan dil | İçerik odağı |
| --- | --- | --- | --- |
| ABA Psikoloji | `aba_psikoloji` | Türkçe | Psikolojik farkındalık, öğrenci ve ebeveyn iletişimi |
| ABA Eğitim | `aba_egitim` | Türkçe | Yurt dışı eğitim, sınav hazırlığı ve akademik planlama |
| Education for Innovation | `e4i` | İngilizce | Eğitim, teknoloji, yapay zekâ ve inovasyon |
| Design House Global | `design_house_global` | İngilizce | Sanat ve tasarım eğitimi, yaratıcı süreç ve portfolyo |

E4I ve Design House Global marka kuralları, açıkça istendiğinde Türkçe üretime de izin verir. Arayüzde ayrı bir dil seçici bulunmaz; istek konu alanında belirtilebilir. Dil ve üslup uyumu model çıktısının gözden geçirilmesini gerektirir.

Her marka kitinde hedef kitle, üslup, renkler, font tanımları, logo yolu, tasarım ilkeleri ve içerik kuralları bulunur. Gönderi kütüphanesi marka başına üç, toplam 12 örnek içerir.

### Marka araştırması kaynakları ve tasarım varsayımları

Brand Kit dosyalarında aşağıdaki web sitesi ve Instagram adresleri referans olarak kayıtlıdır:

| Marka | Web sitesi | Instagram |
| --- | --- | --- |
| ABA Psikoloji | [abapsikoloji.com](https://abapsikoloji.com/) | [@abapsikoloji](https://www.instagram.com/abapsikoloji/) |
| ABA Eğitim | [abaegitim.com](https://abaegitim.com/) | [@abaegitim](https://www.instagram.com/abaegitim/) |
| Education for Innovation | [educationforinnovation.org](https://www.educationforinnovation.org/) | [@e4i_vakfi](https://www.instagram.com/e4i_vakfi/) |
| Design House Global | [designhouseglobal.com](https://www.designhouseglobal.com/) | [@designhouseglobal](https://www.instagram.com/designhouseglobal/) |

19 Ekim 2026 tarihindeki görsel karşılaştırmada dört web sitesi ve Instagram profillerinde erişilebilen gönderi kapakları incelendi; carousel iç sayfaları ve videolar incelenmedi. Instagram'da ABA Psikoloji için krem/turuncu/bordo/yeşil, ABA Eğitim için lacivert/turuncu, E4I için koyu zemin/neon vurgular, Design House için koyu sıcak tonlar ve dar başlıklar gözlemlendi. Design House web sitesindeki “Istanbul” adı ve açık tasarım ile Instagram'daki “Global” kimliği arasında fark bulunuyor; bu durum kesin bir yeniden markalaşma olarak yorumlanmadı. Resmî kurumsal kimlik kılavuzu doğrulanmadığından renk kodları ve Brand Kit'teki Montserrat/Oswald/Playfair Display tanımları, resmî standart iddiası taşımayan MVP tasarım varsayımlarıdır.

Görsel üretici Brand Kit renklerini korur; font tanımlarını görsel yönelim olarak referans alır. Mevcut macOS ortamında Psikoloji başlıklarında Arial Rounded, Eğitim ve E4I başlıklarında Arial Black, Design House başlıklarında DIN Condensed Bold kullanılır. Bunlar kurulu sistem fontlarıdır; font dosyaları indirilmez veya projeyle dağıtılmaz ve resmî marka fontu oldukları iddia edilmez. Bulunamazlarsa mevcut Arial, DejaVu veya boyutlandırılabilen Pillow varsayılan fontuna dönülür. Kütüphanedeki örnek metinler kaynak gönderi bağlantıları içermediğinden markaların gerçek paylaşımlarından birebir alıntı olarak sunulmaz.

## Kurulum

Mevcut geliştirme ortamı macOS ve Python **3.13.16** kullanır. `requirements.txt` doğrudan bağımlılıkları bu ortamda kurulu sürümlere sabitler; tüm dolaylı bağımlılıkları kapsayan bir kilit dosyası değildir. Font seçimi kurulu fontlara bağlı olduğundan diğer işletim sistemlerinde görünüm ve Türkçe karakterler ayrıca kontrol edilmelidir.

Terminali proje kökünde açın. Yeni bir ortam oluşturmak için:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Mevcut bir `.venv` varsa yeniden oluşturmak yerine onu etkinleştirin. Windows PowerShell üzerinde ortam oluşturma ve etkinleştirme komutları:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### API yapılandırması

Yeni metin üretmek için internet bağlantısı ve kullanılabilir bir Gemini API anahtarı gerekir. Anahtar `GEMINI_API_KEY` ortam değişkeninden alınır. `.env.example`, yalnızca değişken adını gösteren boş bir şablondur.

Yeni kurulumda `.env` yoksa `.env.example` dosyasının bir kopyasını `.env` adıyla oluşturup kendi anahtarınızı yerel olarak ekleyin. Mevcut `.env` dosyasının üzerine yazmayın. Anahtarı kaynak koda, README'ye veya teslim paketine eklemeyin. `.env` dosyası mevcut `.gitignore` tarafından dışlanır; ZIP hazırlarken ayrıca hariç tutulmalıdır.

API erişimi, model kullanılabilirliği ve kota hesabınıza bağlıdır; ücretsiz kullanım garantisi verilmez. Kayıtlı örnekleri görüntülemek veya aşağıdaki yerel yöntemle PNG üretmek için API anahtarı gerekmez.

## Kullanım

Etkin sanal ortamda, proje kökünde:

```bash
python -m streamlit run app.py
```

Terminalde gösterilen yerel adresi tarayıcıda açın.

1. Dört markadan birini seçin ve marka bilgileri ile örnek gönderileri inceleyin.
2. Gönderi konusunu yazın. Örnek: `Sınav kaygısıyla başa çıkma`.
3. **İçerik Üret** düğmesine basın. Bu adım Gemini API'ye istek gönderir.
4. Üretilen başlık, görsel metni, açıklama, CTA ve hashtag'leri inceleyin.
5. **Görsel Oluştur** düğmesine basın; bu adım yerel Pillow işlemi yapar.
6. Önizlemeyi kontrol edip **Görseli İndir (PNG)** düğmesiyle dosyayı indirin.

İçerik Streamlit oturumunda saklanır. Marka veya konu değiştiğinde eski sonuç, yeni seçimin sonucu olarak gösterilmez. Arayüzden üretilen görseller `generated_posts/<brand_id>_generated.png` yoluna yazılır.

### Marka tasarımları ve isteğe bağlı yerel fotoğraf

- **ABA Psikoloji:** Yuvarlak başlık, turuncu/bordo sözcük vurguları, açık metin paneli ve yaprak çizimi.
- **ABA Eğitim:** Geniş akademik başlık, turuncu sayı/anahtar kelime vurguları, iki sütun ve üniversite çizimi.
- **E4I:** Kalın başlık, sınırlı yeşil/mor/siyan vurgular, koyu içerik paneli ve bağlantı ağı.
- **Design House Global:** Dar, büyük harfli editoryal başlık, altın tonlu vurgular, ince çizgiler ve portfolyo dekoru. Büyük harf dönüşümü yalnızca görseldedir; JSON metni korunur.

Dört tasarım da mevcut logoyu, 1080×1080 boyutu ve küçük CTA alanını korur. Vurgular yerel bir anahtar kelime/sayı listesiyle belirlenir; ek AI çağrısı yapılmaz. Her başlıkta mutlaka renkli kelime bulunması garanti edilmez.

`create_post_image` işlevi isteğe bağlı `photo_path` parametresi kabul eder. Aşağıdaki örnek, önceden yüklenen `brand_kit` ve `post` sözlükleriyle kullanılabilir:

```python
create_post_image(
    brand_kit,
    post,
    output_filename="yerel_fotografli_post.png",
    photo_path="assets/photos/kendi_fotografim.jpg",
)
```

Fotoğrafı kullanıcı sağlamalı ve kullanım hakkına sahip olmalıdır; uygulama internetten görsel indirmez. Göreli yollar proje köküne göre çözülür. PNG, JPEG, WebP, BMP ve TIFF desteklenir. Fotoğraf medya alanına ortalanarak kırpılır; mevcut dekor küçük bir köşe öğesi olarak korunur. Parametre verilmezse veya belirtilen görsel dosyası yoksa mevcut çizim kullanılır. Mevcut fakat bozuk ya da desteklenmeyen dosya için anlaşılır hata verilir; çıktı dosyasının üzerine yazılmaz. Streamlit'e yeni fotoğraf yükleme alanı eklenmemiştir; mevcut düğme akışı fotoğrafsız çalışır.

## Kayıtlı örnekler ve API kullanmadan görsel üretimi

`examples/` klasöründe her marka için bir JSON ve aynı isimli PNG bulunur. JSON dosyaları konu, marka kimliği ve üretilmiş metin alanlarını içerir. PNG dosyaları bu kayıtlı metinlerden oluşturulmuştur.

| Marka | Metin | Görsel |
| --- | --- | --- |
| ABA Psikoloji | [JSON](examples/aba_psikoloji.json) | [PNG](examples/aba_psikoloji.png) |
| ABA Eğitim | [JSON](examples/aba_egitim.json) | [PNG](examples/aba_egitim.png) |
| Education for Innovation | [JSON](examples/e4i.json) | [PNG](examples/e4i.png) |
| Design House Global | [JSON](examples/design_house_global.json) | [PNG](examples/design_house_global.png) |

Aşağıdaki kodu proje kökünde, etkin sanal ortamın Python yorumlayıcısında çalıştırmak dört PNG'yi güncel tasarımla yeniden üretir. **Yalnızca `examples/` içindeki dört PNG'nin üzerine yazar; JSON metinlerini değiştirmez, `.env` dosyasını yüklemez ve API çağırmaz.**

```python
import json
from pathlib import Path
from image_generator import create_post_image

root = Path.cwd()
brand_ids = ("aba_psikoloji", "aba_egitim", "e4i", "design_house_global")

for brand_id in brand_ids:
    brand = json.loads(
        (root / "brand_kits" / f"{brand_id}.json").read_text(encoding="utf-8")
    )
    post = json.loads(
        (root / "examples" / f"{brand_id}.json").read_text(encoding="utf-8")
    )
    output = root / "examples" / f"{brand_id}.png"
    create_post_image(brand, post, output_filename=str(output))
    print(output.name)
```

`generate_examples.py` farklı bir işlem yapar: Gemini'den **yeni metin** üretir, örnek JSON ve PNG dosyalarının üzerine yazar. Mevcut metinleri koruyarak yalnızca görselleri yenilemek için bu betiği kullanmayın.

## Klasör yapısı

```text
dream-data-labs-challenge/
├── app.py                  # Streamlit arayüzü ve oturum akışı
├── ai_agent.py             # Marka bağlamıyla Gemini içerik üretimi
├── image_generator.py      # Pillow ile marka tasarımları ve PNG üretimi
├── brand_kits/             # Dört markanın JSON yapılandırmaları
├── post_library/
│   └── posts.json          # Toplam 12 referans gönderi
├── assets/
│   └── logos/              # Dört markanın logoları
├── examples/               # Marka başına bir JSON ve bir teslim PNG'si
├── generated_posts/        # Uygulama ve manuel deneme çıktıları
├── generate_examples.py    # API ile yeni örnek metin ve görsel üretimi
├── test_*.py               # Manuel API ve görsel deneme betikleri
├── tests/                  # API gerektirmeyen görsel regresyon testleri
├── requirements.txt        # Sabitlenmiş doğrudan bağımlılıklar
├── .env.example            # Anahtar içermeyen ortam değişkeni şablonu
├── .gitignore
└── README.md
```

## Doğrulama durumu

Teslim hazırlığında dört kayıtlı JSON korunarak PNG'ler güncel `image_generator.py` ile yeniden oluşturuldu. Yerel kontrollerde dört dosyanın da PNG biçiminde, RGB ve **1080×1080** olduğu doğrulandı. Başlık, gövde ve CTA'nın hesaplanan genişlik/yükseklik sınırları; çizilen metinlerin güvenli alanlarda kalması ve metin kutularının birbiriyle çakışmaması kontrol edildi. Dört görsel ayrıca açılarak görsel olarak incelendi.

Çevrimdışı regresyon testleri dört örneğe ek olarak kütüphanedeki 12 gönderiyi, çizilen metin sınırlarını, metin/medya/logo alanlarının ayrılığını, logo piksel bütünlüğünü, yerel fotoğrafı, eksik fotoğrafta çizime dönüşü, uzun kelimeleri ve sığmayan metinde kontrollü hatayı kapsar. Şu komut yalnızca yeni çevrimdışı testleri çalıştırır:

```bash
python -B -m unittest discover -s tests -v
```

Streamlit AppTest ortamında dört marka için içerik gösterimi, gerçek Pillow görsel üretimi, önizleme ve indirme kontrolünün görünmesi doğrulandı. Metin üretimi kayıtlı örneklerle taklit edildi; `.env` okunmadı ve Gemini çağrılmadı. Bu kontroller macOS ortamında yapıldı; temiz kurulum, gerçek tarayıcıda dosya indirme, canlı Gemini veya diğer işletim sistemleri test edilmedi.

`test_*.py` dosyaları otomatik birim testi paketi değildir. Bazıları modül yüklenirken API çağrısı, kullanıcı girdisi veya dosya yazımı yapar. Özellikle `test_gemini.py`, `test_brand_agent.py` ve `test_all_brands.py` API kullanır; topluca test toplama/çalıştırma işlemi çevrimdışı kontrol olarak değerlendirilmemelidir.

## Sınırlamalar ve sonraki adımlar

- Brand Kit'teki font isimleri birebir yüklenmez; kurulu sistem fontlarından uygun görsel alternatifler kullanılır. macOS, yaygın Linux ve Windows font yolları denenir; sistemler arasında aynı görünüm garanti edilmez.
- Görsel düzenleri marka başına sabittir. Gönderi kütüphanesindeki `template` açıklamaları ayrı tasarım şablonları olarak uygulanmaz; tüm marka tasarım yönergeleri otomatik olarak karşılanmaz.
- Metin küçültülür, uzun kelimeler gerektiğinde bölünür ve çizim sınırları doğrulanır. En küçük boyutta da sığmayan metin sessizce kırpılmak yerine hata verir; kullanıcı daha kısa içerik üretmelidir.
- Modelden JSON şemasıyla yanıt istenir; uygulama tarafında kapsamlı alan, uzunluk ve içerik doğrulaması bulunmaz. Eksik/bozuk yerel JSON dosyaları başlangıçta uygulamayı durdurabilir.
- API için 429 ve 503 durumlarında kullanıcı mesajları bulunur. Uygulama düzeyinde özel yeniden deneme akışı yoktur; model adı kodda sabittir.
- Aynı marka için arayüzden üretilen PNG'nin üzerine yazılır. Eşzamanlı kullanıcılar için dosya ayrımı ve kalıcı içerik geçmişi bulunmaz.
- Arayüzde kayıtlı JSON yükleme, içerik düzenleme veya JSON/metin indirme özelliği yoktur. Hazır örneklerle API'siz görsel üretimi yukarıdaki Python koduyla yapılabilir.
- Üretilen içerikler yayımlanmadan önce marka dili ve doğruluk açısından gözden geçirilmelidir. Uygulama sosyal medya hesabına doğrudan paylaşım yapmaz.

Fontların platformlar arasında tutarlılığı, ek içerik doğrulamaları ve benzersiz çıktı adları sonraki geliştirme adımlarıdır. Tasarım iyileştirmesi görsel üreticiyle sınırlıdır; mevcut Streamlit ve Gemini akışı değiştirilmemiştir.
