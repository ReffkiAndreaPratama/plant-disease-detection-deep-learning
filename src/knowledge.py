"""
knowledge.py
============
Basis pengetahuan 38 kelas daun dari dataset PlantVillage (14 tanaman).

Setiap kelas berisi informasi: nama tanaman, nama penyakit/status, kategori,
gejala umum, faktor penyebab, penanganan, pencegahan, kondisi lingkungan,
tingkat risiko, dan emoji. Digunakan aplikasi untuk menampilkan penjelasan
setelah prediksi dan untuk tab "Basis Pengetahuan".

Persis sama dengan nama folder kelas di PlantVillage.
"""

# =========================================================
# TAMPILAN / UTIL
# =========================================================

KATEGORI_EMOJI = {
    "jamur": "🍄",
    "bakteri": "🦠",
    "virus": "🧬",
    "hama": "🐜",
    "lingkungan": "🌦️",
    "sehat": "🌱",
}

RISIKO_EMOJI = {"rendah": "ℹ️", "sedang": "⚠️", "tinggi": "🔴"}


def cari_kelas(kode_kelas: str) -> dict:
    """Mengembalikan dict info kelas, fallback ke dict kosong jika tidak ada."""
    return PENGETAHUAN.get(kode_kelas, {})


def simpan_dan_penyakit(kode_kelas: str) -> tuple:
    """Mengembalikan (nama_tanaman, nama_penyakit)."""
    info = PENGETAHUAN.get(kode_kelas, {})
    return info.get("tanaman", "Tanaman"), info.get("penyakit", "Tidak diketahui")


# =========================================================
# BASIS PENGETAHUAN
# =========================================================

PENGETAHUAN = {
    # ------------------------------------------------------------------ APPLE
    "Apple___Apple_scab": {
        "tanaman": "Apel",
        "penyakit": "Kudis Apel (Apple Scab)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak cokelat kehitaman pada daun, kadang tampak seperti beludru.",
            "Daun muda dapat berkerut dan mengeriting.",
            "Bercak menyebar ke buah membentuk bintik hitam kasar.",
        ],
        "penyebab": "Jamur Venturia inaequalis yang berkembang pada cuaca basah dan dingin (faktor lingkungan juga disebutkan di atas).",
        "penanganan": [
            "Rontokkan dan buang daun terinfeksi; jangan dijadikan kompos.",
            "Semprot fungisida berbahan dasar sulfur atau tembaga sesuai dosis.",
            "Pangkas cabang yang terserang parah agar sirkulasi udara baik.",
        ],
        "pencegahan": [
            "Pilih varietas apel yang tahan kudis.",
            "Hindari penyiraman dari atas sehingga daun tidak basah terlalu lama.",
            "Jaga jarak tanam agar aliran udara lancar.",
        ],
        "lingkungan": "Berkembang di suhu 15-25°C dengan kelembapan daun basah 9 jam atau lebih.",
    },
    "Apple___Black_rot": {
        "tanaman": "Apel",
        "penyakit": "Busuk Hitam (Black Rot)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak ungu-cokelat yang menyebar dari tepi daun.",
            "Bagian tengah bercak berubah menjadi cokelat terang dengan tepi gelap.",
            "Buah membusuk membentuk lingkaran cokelat yang mengeras.",
        ],
        "penyebab": "Jamur Botryosphaeria obtusa, umum pada pohon yang stres atau luka terbuka.",
        "penanganan": [
            "Buang ranting, daun, dan buah mati yang menjadi sumber inokulum.",
            "Semprot fungisida protektif sebelum musim hujan.",
            "Perkuat pohon dengan pemupukan seimbang.",
        ],
        "pencegahan": [
            "Perbaiki drainase dan hindari genangan di sekitar akar.",
            "Lindungi luka bekas pangkasan dengan fungisida.",
            "Jaga kebersihan kebun dari sisa tanaman yang membusuk.",
        ],
        "lingkungan": "Infeksi meningkat pada musim hujan yang panjang dan suhu hangat 20-28°C.",
    },
    "Apple___Cedar_apple_rust": {
        "tanaman": "Apel",
        "penyakit": "Karat Cedar-Apel (Cedar Apple Rust)",
        "kategori": "jamur",
        "risiko": "rendah",
        "gejala": [
            "Bercak oranye terang dengan titik-titik hitam di tengah pada permukaan daun.",
            "Pada musim semi tampak tonjolan berwarna oranye seperti tanduk.",
            "Daun menguning dan gugur lebih awal bila serangan berat.",
        ],
        "penyebab": "Jamur Gymnosporangium juniperi-virginianae yang membutuhkan dua inang (cedar/juniper dan apel).",
        "penanganan": [
            "Buang bagian cedar/juniper di sekitar kebun bila memungkinkan sebagai inang perantara.",
            "Semprot fungisida saat tunas baru muncul hingga buah kecil.",
            "Rontokkan daun terinfeksi berat.",
        ],
        "pencegahan": [
            "Tanam varietas apel yang tahan karat.",
            "Hindari menanam apel dekat pohon cedar yang terinfeksi.",
            "Penyemprotan rutin saat cuaca lembap dan hangat.",
        ],
        "lingkungan": "Membutuhkan cuaca hangat-lembap 18-24°C dan hujan musim semi.",
    },
    "Apple___healthy": {
        "tanaman": "Apel",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau normal, permukaan rata dan tidak ada bercak.", "Pertumbuhan daun seragam dan kokoh."],
        "penyebab": "-",
        "penanganan": ["Tidak perlu perlakuan khusus.", "Lanjutkan perawatan rutin dan pemantauan mingguan."],
        "pencegahan": [
            "Pemupukan seimbang dan penyiraman teratur.",
            "Jaga kebersihan kebun dari gulma dan sisa tanaman.",
        ],
        "lingkungan": "Tanaman sehat didukung sinar matahari penuh dan drainase baik.",
    },
    # -------------------------------------------------------------- BLUEBERRY
    "Blueberry___healthy": {
        "tanaman": "Blueberry",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau mengilap dengan tekstur halus.", "Tidak ada bercak, keriting, atau perubahan warna."],
        "penyebab": "-",
        "penanganan": ["Tidak ada tindakan khusus, hanya perawatan rutin."],
        "pencegahan": [
            "Tanam di tanah asam (pH 4,5-5,5) dan beririgasi teratur.",
            "Periksa hama secara berkala.",
        ],
        "lingkungan": "Menyukai tanah asam, sinar matahari penuh, dan drainase baik.",
    },
    # ---------------------------------------------------------------- CHERRY
    "Cherry_(including_sour)___Powdery_mildew": {
        "tanaman": "Ceri",
        "penyakit": "Embun Tepung (Powdery Mildew)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Lapisan tepung putih tipis pada permukaan daun muda.",
            "Daun mengerut dan pertumbuhannya terhambat.",
            "Serangan berat membuat daun menguning dan gugur.",
        ],
        "penyebab": "Jamur Podosphaera clandestina yang menyukai udara lembap tetapi permukaan daun kering.",
        "penanganan": [
            "Semprot fungisida sulfur atau kalium bikarbonat.",
            "Buang pucuk dan daun yang terinfeksi berat.",
            "Lakukan pemangkasan untuk membuka tajuk.",
        ],
        "pencegahan": [
            "Hindari pemupukan nitrogen berlebihan yang memicu tunas lembut.",
            "Jaga sirkulasi udara antar pohon.",
            "Siram di pangkal, bukan menyiram daun.",
        ],
        "lingkungan": "Optimal pada kelembapan relatif tinggi tetapi daun kering, suhu 15-27°C.",
    },
    "Cherry_(including_sour)___healthy": {
        "tanaman": "Ceri",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau segar dan bersih tanpa lapisan tepung atau bercak."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin; tidak perlu pengendalian hama atau penyakit."],
        "pencegahan": ["Pangkas rutin agar tajuk terbuka dan amati kondisi daun tiap minggu."],
        "lingkungan": "Ceri sehat tumbuh baik di iklim sedang dengan drainase baik.",
    },
    # --------------------------------------------------------------- CORN
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "tanaman": "Jagung",
        "penyakit": "Bercak Daun Abu-abu (Gray Leaf Spot)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak sempit persegi panjang berwarna abu-abu kecokelatan sejajar urat daun.",
            "Bercak meluas dan menyatu, daun tampak hangus.",
            "Menurunkan areal fotosintesis sehingga tongkol kecil.",
        ],
        "penyebab": "Jamur Cercospora zeae-maydis yang berkembang saat kelembapan tinggi dan sisa tanaman di permukaan tanah.",
        "penanganan": [
            "Aplikasi fungisida berbahan aktif triazol atau strobilurin pada gejala awal.",
            "Bajak/benamkan sisa tanaman jagung setelah panen.",
            "Pilih hibrida tahan pada musim berikutnya.",
        ],
        "pencegahan": [
            "Rotasi tanaman untuk memutus siklus jamur.",
            "Tanam dengan kepadatan sesuai anjuran agar aliran udara baik.",
            "Perbaiki drainase lahan.",
        ],
        "lingkungan": "Puncak pada kelembapan daun berkepanjangan dan suhu 22-30°C.",
    },
    "Corn_(maize)___Common_rust_": {
        "tanaman": "Jagung",
        "penyakit": "Karat Biasa (Common Rust)",
        "kategori": "jamur",
        "risiko": "rendah",
        "gejala": [
            "Pustula (tonjolan) kecil berwarna cokelat-oranye tersebar di kedua permukaan daun.",
            "Pustula pecah mengeluarkan bubuk spora oranye.",
            "Serangan awal dapat menurunkan hasil panen.",
        ],
        "penyebab": "Jamur Puccinia sorghi; spora menyebar lewat angin.",
        "penanganan": [
            "Semprot fungisida pada gejala awal bila tekanan penyakit tinggi.",
            "Tingkatkan ketahanan tanaman dengan pemupukan seimbang.",
        ],
        "pencegahan": [
            "Gunakan varietas jagung yang tahan karat.",
            "Hindari pemupukan nitrogen berlebihan.",
            "Tanam pada waktu yang seragam antar petak.",
        ],
        "lingkungan": "Sporulasi maksimal pada suhu 16-25°C dan kelembapan tinggi.",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "tanaman": "Jagung",
        "penyakit": "Hawar Daun Utara (Northern Leaf Blight)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Lesi besar berbentuk perahu/cerutu berwarna cokelat abu-abu di daun.",
            "Lesi dimulai dari daun bawah dan menyebar ke atas.",
            "Daun layu dan mengering dalam serangan berat.",
        ],
        "penyebab": "Jamur Exserohilum turcicum, menyebar cepat pada cuaca basah.",
        "penanganan": [
            "Semprot fungisida protektif saat gejala muncul di daun ke-6 hingga ke-8.",
            "Pisahkan lahan terinfeksi agar spora tidak menyebar.",
        ],
        "pencegahan": [
            "Tanam hibrida tahan hawar daun.",
            "Rotasi tanaman dan pembenaman sisa tanaman.",
            "Hindari tanam rapat yang menaikkan kelembapan tajuk.",
        ],
        "lingkungan": "Infeksi cepat pada suhu 18-27°C dengan hujan atau embun berkepanjangan.",
    },
    "Corn_(maize)___healthy": {
        "tanaman": "Jagung",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau segar, rata, tanpa lesi, karat, atau bercak abu-abu."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin; pantau populasi hama."],
        "pencegahan": ["Pemupukan sesuai anjuran dan pengaturan jarak tanam yang tepat."],
        "lingkungan": "Jagung sehat tumbuh optimal di tanah subur berdrainase baik dan sinar penuh.",
    },
    # ------------------------------------------------------------------ GRAPE
    "Grape___Black_rot": {
        "tanaman": "Anggur",
        "penyakit": "Busuk Hitam (Black Rot)",
        "kategori": "jamur",
        "risiko": "tinggi",
        "gejala": [
            "Bercak cokelat muda dengan tepi gelap pada daun.",
            "Titik hitam kecil (piknidia) di dalam bercak.",
            "Buah mengecil, hangus, dan mengeras seperti mumi.",
        ],
        "penyebab": "Jamur Guignardia bidwellii, sangat cepat berkembang pada musim hujan.",
        "penanganan": [
            "Semprot fungisida protektif (mancozeb, myclobutanil) sejak mulai berdaun.",
            "Buang tandan dan daun terinfeksi; kumpulkan mumi buah.",
            "Pangkas untuk membuka tajuk.",
        ],
        "pencegahan": [
            "Bersihkan sisa tanaman anggur setelah pemangkasan.",
            "Pantau cuaca dan lakukan penyemprotan sebelum hujan.",
        ],
        "lingkungan": "Berkembang pesat pada hujan mendung, suhu 18-27°C.",
    },
    "Grape___Esca_(Black_Measles)": {
        "tanaman": "Anggur",
        "penyakit": "Esca / Measles Hitam",
        "kategori": "jamur",
        "risiko": "tinggi",
        "gejala": [
            "Daun menunjukkan pola bintik cokelat-kemerahan di antara urat daun (tiger stripe).",
            "Daun layu mendadak dan buah bernoda hitam kecil.",
            "Serangan bertahun-tahun menyebabkan batang membusuk dari dalam.",
        ],
        "penyebab": "Sekumpulan jamur kayu (Phaeomoniella, Phaeoacremonium, dll) masuk lewat luka pangkas.",
        "penanganan": [
            "Pangkas cabang yang menunjukkan garis hitam gelap pada penampang.",
            "Hindari pemangkasan saat hujan; tutup luka besar dengan pasta.",
            "Perkuat tanaman dengan kalium dan kurangi stres air.",
        ],
        "pencegahan": [
            "Gunakan kayu mata tempel yang sehat/bebas penyakit.",
            "Disinfeksi peralatan pangkas.",
            "Hindari pemangkasan berat di pangkal batang.",
        ],
        "lingkungan": "Makin parah pada tanaman tua dan kebun yang sering terluka pangkasan.",
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "tanaman": "Anggur",
        "penyakit": "Hawar Daun (Isariopsis Leaf Spot)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak cokelat muda bersudut pada daun, sering bertepi gelap.",
            "Bercak menyatu membentuk area nekrosis besar.",
            "Daun gugur sebelum waktunya pada serangan berat.",
        ],
        "penyebab": "Jamur Pseudocercospora vitis (Isariopsis) pada tajuk yang lembap dan rimbun.",
        "penanganan": [
            "Semprot fungisida berbahan aktif tembaga pada awal gejala.",
            "Pangkas tanaman agar sirkulasi udara dan cahaya masuk.",
        ],
        "pencegahan": [
            "Jaga kebersihan kebun dari sisa daun terinfeksi.",
            "Hindari penyiraman berlebih dan irigasi tajuk.",
        ],
        "lingkungan": "Membutuhkan kelembapan tinggi dan tajuk yang rimbun; sering muncul akhir musim.",
    },
    "Grape___healthy": {
        "tanaman": "Anggur",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun anggur hijau normal, lobus rata, tanpa bercak atau mumi."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin, pemangkasan dan pemupukan terjadwal."],
        "pencegahan": ["Pantau kelembapan tajuk dan bersihkan gulma."],
        "lingkungan": "Anggur sehat ideal pada iklim hangat-kering dengan irigasi terkontrol.",
    },
    # ----------------------------------------------------------------- ORANGE
    "Orange___Haunglongbing_(Citrus_greening)": {
        "tanaman": "Jeruk",
        "penyakit": "Citrus Greening (HLB)",
        "kategori": "bakteri",
        "risiko": "tinggi",
        "gejala": [
            "Pola bercak kuning tidak merata / blotchy mottle pada daun.",
            "Daun mengeras, tebal, dan urat daun menonjol menguning.",
            "Buah kecil, asimetris, hijau karena tidak matang sempurna.",
        ],
        "penyebab": "Bakteri Candidatus Liberibacter yang ditularkan kutu loncat jeruk (Diaphorina citri).",
        "penanganan": [
            "Cabut dan musnahkan pohon yang terinfeksi berat (tidak bisa disembuhkan).",
            "Kendalikan kutu loncat dengan insektisida dan musuh alami.",
            "Pakai bibit jeruk bersertifikat bebas penyakit.",
        ],
        "pencegahan": [
            "Pasang perangkap kuning untuk memantau kutu loncat.",
            "Karantina bibit dari daerah terserang.",
            "Jaga nutrisi pohon agar daya tahan meningkat.",
        ],
        "lingkungan": "Menyebar cepat di kebun jeruk yang dekat dengan sumber inokulum dan kutu vektor aktif.",
    },
    # ------------------------------------------------------------------ PEACH
    "Peach___Bacterial_spot": {
        "tanaman": "Persik",
        "penyakit": "Bercak Bakteri (Bacterial Spot)",
        "kategori": "bakteri",
        "risiko": "sedang",
        "gejala": [
            "Bercak kecil ungu-cokelat dengan area kuning di sekelilingnya.",
            "Dapat berlubang (shot hole) pada daun.",
            "Bercak cekung gelap pada buah.",
        ],
        "penyebab": "Bakteri Xanthomonas arboricola pv. pruni, menyebar lewat hujan dan angin.",
        "penanganan": [
            "Semprot bakterisida berbasis tembaga pada awal musim.",
            "Buang daun dan buah terinfeksi serta jaga kebersihan kebun.",
            "Pangkas untuk mempercepat daun cepat kering.",
        ],
        "pencegahan": [
            "Pilih varietas/varietas tahan bercak bakteri.",
            "Kurangi pancuran air di tajuk (gunakan irigasi tetes).",
            "Berikan kalium yang cukup agar daun lebih tebal.",
        ],
        "lingkungan": "Puncak saat angin kencang + hujan, suhu 18-25°C.",
    },
    "Peach___healthy": {
        "tanaman": "Persik",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau bersih, tanpa bercak ungu atau lubang (shot hole)."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin; monitoring mingguan."],
        "pencegahan": ["Pohon sehat didukung pemangkasan teratur dan pemupukan seimbang."],
        "lingkungan": "Persik sehat tumbuh baik di tanah gembur berdrainase baik dan sinar penuh.",
    },
    # ------------------------------------------------------------------ PEPPER
    "Pepper,_bell___Bacterial_spot": {
        "tanaman": "Paprika / Cabai",
        "penyakit": "Bercak Bakteri (Bacterial Spot)",
        "kategori": "bakteri",
        "risiko": "sedang",
        "gejala": [
            "Bercak kecil kecokelatan berkilau pada daun.",
            "Tepi bercak bersudut dan dikelilingi halo kuning.",
            "Bercak meluas, daun menguning dan gugur.",
        ],
        "penyebab": "Bakteri Xanthomonas campestris pv. vesicatoria yang terbawa biji dan percikan air.",
        "penanganan": [
            "Semprot bakterisida tembaga segera setelah bercak pertama terlihat.",
            "Buang bagian tanaman terinfeksi ke luar lahan.",
            "Gunakan benih bebas patogen / diperlakukan panas.",
        ],
        "pencegahan": [
            "Rotasi tanaman (jangan paprika/cabai berturut-turut).",
            "Hindari irigasi pancuran di atas tajuk.",
            "Pilih varietas tahan bercak bakteri.",
        ],
        "lingkungan": "Aktif pada cuaca hujan-berangin dan suhu 24-32°C.",
    },
    "Pepper,_bell___healthy": {
        "tanaman": "Paprika / Cabai",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun hijau rata, tanpa bercak bersudut atau halo kuning."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin."],
        "pencegahan": ["Amati menyeluruh saat pagi hari; berikan nutrisi berimbang."],
        "lingkungan": "Paprika sehat tumbuh optimal di suhu 21-30°C dengan tanah lembap merata.",
    },
    # ------------------------------------------------------------------ POTATO
    "Potato___Early_blight": {
        "tanaman": "Kentang",
        "penyakit": "Hawar Awal (Early Blight)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak cokelat konsentris seperti cincin burung sasaran (target ring).",
            "Bercak dimulai dari daun bawah dan menguning di sekitarnya.",
            "Daun kering dan gugur lebih awal.",
        ],
        "penyebab": "Jamur Alternaria solani, menyerang tanaman stres / kekurangan nutrisi.",
        "penanganan": [
            "Semprot fungisida pada gejala awal (azol/strobilurin).",
            "Buang dan kubur daun tua yang sakit.",
            "Lakukan pemupukan kalium untuk memperkuat daun.",
        ],
        "pencegahan": [
            "Rotasi tanaman 2-3 tahun.",
            "Jaga kelembapan tanah stabil, hindari stres air.",
            "Gunakan umbi bibit sehat.",
        ],
        "lingkungan": "Cepat terjadi pada suhu 20-30°C dengan daun basah bergantian siang-malam.",
    },
    "Potato___Late_blight": {
        "tanaman": "Kentang",
        "penyakit": "Hawar Daun (Late Blight)",
        "kategori": "jamur",
        "risiko": "tinggi",
        "gejala": [
            "Bercak besar berwarna hijau gelap seperti basah, dengan tepi tidak jelas.",
            "Di bawah daun tampak jamur putih halus saat lembap.",
            "Seluruh tanaman bisa membusuk dalam beberapa hari.",
        ],
        "penyebab": "Oomycota Phytophthora infestans, penyebab gagal panen kentang Eropa abad 19.",
        "penanganan": [
            "Semprot fungisida sistemik segera; ulangi 7-10 hari saat cuaca cocok.",
            "Matahari: buang dedaunan terinfeksi dan hentikan irigasi kabut.",
            "Panen lebih awal bila infeksi menyebar cepat.",
        ],
        "pencegahan": [
            "Gunakan umbi bibit bersertifikat bebas penyakit.",
            "Pantau ramalan cuaca lembap; lakukan aplikasi protektif sebelum hujan.",
            "Rotasi dan hindari tumpukan sisa tanaman terinfeksi.",
        ],
        "lingkungan": "Epidemi saat suhu 10-22°C disertai hujan/embun tebal berkepanjangan.",
    },
    "Potato___healthy": {
        "tanaman": "Kentang",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun kentang hijau segar tanpa bercak cincin atau basah-basah."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin; buang gulma."],
        "pencegahan": ["Berikan pupuk berimbang dan tanam umbi sehat pada tanah gembur."],
        "lingkungan": "Kentang sehat tumbuh baik di suhu sejuk 15-20°C.",
    },
    # -------------------------------------------------------------- RASPBERRY
    "Raspberry___healthy": {
        "tanaman": "Raspberry",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun raspberry hijau dengan tepi bergerigi rata dan bersih."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin."],
        "pencegahan": ["Pangkas cabang mati dan lindungi dari sengatan sinar sore ekstrem."],
        "lingkungan": "Raspberry sehat menyukai tanah subur agak asam dengan sinar pagi penuh.",
    },
    # ----------------------------------------------------------------- SOYBEAN
    "Soybean___healthy": {
        "tanaman": "Kedelai",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun kedelai hijau trifoliat yang rata tanpa bercak atau kuning."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin."],
        "pencegahan": ["Amankan jarak tanam dan kecukupan fosfor/nitrogen."],
        "lingkungan": "Kedelai sehat tumbuh baik di tanah lempung berdrainase baik.",
    },
    # ----------------------------------------------------------------- SQUASH
    "Squash___Powdery_mildew": {
        "tanaman": "Labu (Squash)",
        "penyakit": "Embun Tepung (Powdery Mildew)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bubuk putih seperti tepung pada permukaan daun labu.",
            "Daun menguning, mengering, dan pertumbuhan terhambat.",
        ],
        "penyebab": "Jamur Podosphaera xanthii yang aktif saat siang hangat dan malam lembap.",
        "penanganan": [
            "Semprot sulfur atau kalium bikarbonat (hindari sulfur saat >30°C).",
            "Buang daun bertepung berat.",
            "Kurangi naungan yang membuat udara pengap.",
        ],
        "pencegahan": [
            "Berikan jarak tanam lebar.",
            "Siram di pangkal tanaman.",
            "Tanam varietas labu tahan embun tepung.",
        ],
        "lingkungan": "Mudah muncul pada cuaca kering-desau hangat dengan kelembapan malam tinggi.",
    },
    # -------------------------------------------------------------- STRAWBERRY
    "Strawberry___Leaf_scorch": {
        "tanaman": "Stroberi",
        "penyakit": "Layu Daun / Leaf Scorch",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Tepi dan permukaan daun berubah ungu-cokelat seperti terbakar.",
            "Daun melengkung dan tampak hangus dari tepi.",
            "Bercak menyebar ke seluruh daun pada serangan berat.",
        ],
        "penyebab": "Jamur Diplocarpon earlianum yang hidup pada daun tua dan lembap.",
        "penanganan": [
            "Potong dan buang daun terinfeksi.",
            "Semprot fungisida pada awal musim tanam.",
            "Kurangi kepadatan tanaman.",
        ],
        "pencegahan": [
            "Jaga bedengan bersih dari daun mati.",
            "Irigasi di pagi hari agar daun cepat kering.",
            "Pilih kultivar tahan scorch.",
        ],
        "lingkungan": "Parah pada kelembapan tinggi dan tajuk stroberi yang rapat.",
    },
    "Strawberry___healthy": {
        "tanaman": "Stroberi",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun stroberi hijau mengilap dengan tepi bergerigi, tanpa hangus."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin."],
        "pencegahan": ["Bersihkan daun tua dan beri mulsa agar buah tidak kotor."],
        "lingkungan": "Stroberi sehat tumbuh baik di tanah gembur dengan sinar pagi.",
    },
    # ------------------------------------------------------------------ TOMATO
    "Tomato___Bacterial_spot": {
        "tanaman": "Tomat",
        "penyakit": "Bercak Bakteri (Bacterial Spot)",
        "kategori": "bakteri",
        "risiko": "sedang",
        "gejala": [
            "Bercak kecil cokelat berkilau dengan halo kuning pada daun tomat.",
            "Bercak bersudut dan seperti berserak merata.",
            "Daun menguning dan gugur; buah bernoda kecil.",
        ],
        "penyebab": "Bakteri Xanthomonas gardneri / euvesicatoria yang terbawa benih dan air.",
        "penanganan": [
            "Semprot bakterisida tembaga saat bercak pertama muncul.",
            "Buang daun sakit; jangan gunakan untuk kompos dalam lahan.",
            "Sterilkan benih dengan air panas 50°C / desinfektan.",
        ],
        "pencegahan": [
            "Gunakan benih bersertifikat bebas patogen.",
            "Rotasi dengan tanaman bukan tomat selama 2-3 tahun.",
            "Hindari irigasi atas tajuk.",
        ],
        "lingkungan": "Aktif pada hujan-berangin dan suhu 24-32°C.",
    },
    "Tomato___Early_blight": {
        "tanaman": "Tomat",
        "penyakit": "Hawar Awal (Early Blight)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak cokelat berbentuk cincin konsentris (target spot) pada daun tua.",
            "Halo kuning mengelilingi bercak.",
            "Daun bawah gugur lebih dulu hingga tanaman tampak 'tinggi botak'.",
        ],
        "penyebab": "Jamur Alternaria solani, makin parah pada tanaman stres dan cuaca lembap-bergantian.",
        "penanganan": [
            "Aplikasi fungisida (terutama pada daun bawah) di awal gejala.",
            "Kurangi daun bawah yang terserang.",
            "Mulsa tanah untuk mencegah percikan spora.",
        ],
        "pencegahan": [
            "Rotasi tanaman 2 tahun.",
            "Irigasi pagi, hindari basah berkepanjangan pada daun.",
            "Jaga nutrisi kalium & nitrogen seimbang.",
        ],
        "lingkungan": "Optimal 22-29°C dengan dedaunan basah bergantian kering-basah.",
    },
    "Tomato___Late_blight": {
        "tanaman": "Tomat",
        "penyakit": "Hawar Daun (Late Blight)",
        "kategori": "jamur",
        "risiko": "tinggi",
        "gejala": [
            "Bercak besar gelap seperti tergenang, tepi tidak jelas pada daun dan batang.",
            "Lapisan putih halus di bawah daun saat lembap.",
            "Buah membusuk cepat dengan area cokelat keras.",
        ],
        "penyebab": "Oomiseta Phytophthora infestans (sama dengan kentang) - sangat destruktif.",
        "penanganan": [
            "Aplikasi fungisida sistemik segera dan ulangi sesuai jadwal.",
            "Buang dan musnahkan tanaman terinfeksi agar tidak menular.",
            "Turunkan kelembapan: jangan irigasi kabut dan buka rumah tanam.",
        ],
        "pencegahan": [
            "Tanam varietas tomat tahan late blight.",
            "Pisahkan lahan dengan sumber spora (tumpukan kentang).",
            "Pantau cuaca lembap dan lakukan protektif sebelum hujan.",
        ],
        "lingkungan": "Epidemi saat suhu 10-22°C dan kelembapan tinggi berkepanjangan (>90%).",
    },
    "Tomato___Leaf_Mold": {
        "tanaman": "Tomat",
        "penyakit": "Jamur Daun (Leaf Mold)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak kuning pucat di atas daun; di bawahnya tumbuh jamur cokelat zaitun.",
            "Daun menggulung, mengering, dan gugur dari bawah.",
            "Sering muncul pada rumah tanam dengan sirkulasi buruk.",
        ],
        "penyebab": "Jamur Passalora (Cladosporium) fulva di rumah kaca lembap dan pengap.",
        "penanganan": [
            "Buka ventilasi dan turunkan kelembapan.",
            "Buang daun terinfeksi.",
            "Semprot fungisida bila serangan berat.",
        ],
        "pencegahan": [
            "Jaga jarak antar tanaman.",
            "Siram pagi, perbaiki sirkulasi udara.",
            "Gunakan varietas tahan jamur daun.",
        ],
        "lingkungan": "Muncul pada kelembapan relatif >85% dan suhu malam 15-23°C.",
    },
    "Tomato___Septoria_leaf_spot": {
        "tanaman": "Tomat",
        "penyakit": "Bercak Daun Septoria",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak kecil bulat abu-abu (jumlah sangat banyak) dengan tepi cokelat gelap.",
            "Titik hitam kecil (piknidia) di tengah bercak.",
            "Daun bawah menguning dan gugur secara massal.",
        ],
        "penyebab": "Jamur Septoria lycopersici, menyebar cepat lewat percikan air dan tangan.",
        "penanganan": [
            "Buang daun bawah yang sakit secara rutin.",
            "Semprot fungisida protektif (tembaga/mancozeb).",
            "Jangan menyiram menjelang malam.",
        ],
        "pencegahan": [
            "Rotasi di luar kelompok tomat selama 2 tahun.",
            "Pangkas daun tua agar aliran udara baik.",
            "Mulsa untuk menghalangi percikan spora.",
        ],
        "lingkungan": "Cepat menular pada cuaca hangat-lembap dengan hujan/embun.",
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "tanaman": "Tomat",
        "penyakit": "Tungau Laba-laba (Spider Mites)",
        "kategori": "hama",
        "risiko": "sedang",
        "gejala": [
            "Bintik-bintik kecil kuning/putih (stippling) di permukaan daun.",
            "Daun tampak kecokelatan seperti terbakar dan jaringan halus/sarang (webbing).",
            "Populasi tinggi membuat daun gugur.",
        ],
        "penyebab": "Tungau Tetranychus urticae, meledak pada cuaca panas dan kering.",
        "penanganan": [
            "Semprot air kuat untuk mengurangi populasi tungau.",
            "Gunakan akarisida atau sabun insektisida.",
            "Lepas predator alami seperti Phytoseiulus persimilis.",
        ],
        "pencegahan": [
            "Jaga kelembapan tanah dan udara, hindari ukuran daun memanas berlebihan.",
            "Periksa bagian bawah daun secara rutin.",
            "Hindari pemupukan nitrogen berlebihan.",
        ],
        "lingkungan": "Puncak pada suhu >30°C, kering, dan berdebu.",
    },
    "Tomato___Target_Spot": {
        "tanaman": "Tomat",
        "penyakit": "Bercak Sasaran (Target Spot)",
        "kategori": "jamur",
        "risiko": "sedang",
        "gejala": [
            "Bercak besar dengan cincin konsentris jelas seperti sasaran tembak.",
            "Cincin tengah kering dan pecah (shot hole).",
            "Berbeda dengan early blight, bercak merata sampai daun muda.",
        ],
        "penyebab": "Jamur Corynespora cassiicola pada cuaca hangat dan lembap serta tajuk rapat.",
        "penanganan": [
            "Semprot fungisida (banyak yang sama dengan early blight).",
            "Kurangi kepadatan tanaman dan buang daun terinfeksi.",
        ],
        "pencegahan": [
            "Jaga sirkulasi udara.",
            "Rotasi tanaman non-solanaceae.",
            "Pilih varietas tahan target spot.",
        ],
        "lingkungan": "Optimal pada 24-32°C dan dedaunan basah.",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "tanaman": "Tomat",
        "penyakit": "Virus Kuning Keriting Daun (TYLCV)",
        "kategori": "virus",
        "risiko": "tinggi",
        "gejala": [
            "Daun muda menguning di tepi dan melengkung ke atas (cupping).",
            "Tanaman kerdil, ruas pendek, bunga gugur.",
            "Buah sedikit dan kecil.",
        ],
        "penyebab": "Tomato yellow leaf curl virus yang ditularkan kutu kebul (Bemisia tabaci).",
        "penanganan": [
            "Cabut tanaman terinfeksi berat (tidak ada obat untuk virus).",
            "Kendalikan kutu kebul dengan insektisida selektif dan perangkap kuning.",
            "Gunakan bibit bebas vektor.",
        ],
        "pencegahan": [
            "Tanam varietas tomat tahan TYLCV.",
            "Pasang kelambu/net di rumah tanam.",
            "Buang gulma inang kutu kebul di sekitar lahan.",
        ],
        "lingkungan": "Penyebaran meningkat saat populasi kutu kebul tinggi (cuaca panas dan kering).",
    },
    "Tomato___Tomato_mosaic_virus": {
        "tanaman": "Tomat",
        "penyakit": "Virus Mosaik Tomat (ToMV)",
        "kategori": "virus",
        "risiko": "sedang",
        "gejala": [
            "Pola mozaik hijau terang-gelap tidak beraturan pada daun.",
            "Daun muda menyempit (fern leaf) dan keriput.",
            "Buah berbintik cokelat dan memanjang-lonjong (fern leaf fruit).",
        ],
        "penyebab": "Tomato mosaic virus yang sangat mudah menular lewat tangan, alat, dan biji.",
        "penanganan": [
            "Cuci tangan dan desinfeksi alat (larutan susu/desinfektan) sebelum bekerja.",
            "Cabut tanaman terinfeksi.",
            "Jangan merokok/seksan yang membawa TMV lalu menyentuh tomat.",
        ],
        "pencegahan": [
            "Celup benih ke air panas 50°C dan campuran trisodium fosfat.",
            "Gunakan bibit bebas virus.",
            "Pisahkan area kerja yang bersentuhan dengan tomat.",
        ],
        "lingkungan": "Menular secara mekanik; tidak tergantung cuaca, lebih pada kebersihan kebun.",
    },
    "Tomato___healthy": {
        "tanaman": "Tomat",
        "penyakit": "Sehat",
        "kategori": "sehat",
        "risiko": "rendah",
        "gejala": ["Daun tomat hijau segar, rata, tanpa bercak, keriting, atau mozaik."],
        "penyebab": "-",
        "penanganan": ["Perawatan rutin; tidak ada tindakan pengendalian."],
        "pencegahan": [
            "Penyiraman teratur dan pemupukan berimbang.",
            "Pangkas tunas liar agar tajuk tidak rimbun.",
        ],
        "lingkungan": "Tomat sehat tumbuh optimal di 18-28°C dan tanah gembur subur.",
    },
}

# Nama-nama kelas yang dipakai sebagai label (sesuai PlantVillage)
KELAS = list(PENGETAHUAN.keys())