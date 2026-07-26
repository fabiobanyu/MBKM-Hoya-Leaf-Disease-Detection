const TABLE_DATA = {
    "diseases": [
        {
            "name_id": "Bercak Mata Katak (Cercospora)",
            "name_en": "Frog-eye Spot (Cercospora)",
            "desc_id": "Terdapat lesi atau bintik kecil berwarna abu-abu pada bagian tengah dengan tepi berwarna cokelat kemerahan atau ungu.",
            "desc_en": "Small gray lesions or spots in the center with reddish-brown or purple margins.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Rendah",
            "severity_text_en": "Low",
            "severity_class": "info"
        },
        {
            "name_id": "Embun Tepung (Powdery Mildew)",
            "name_en": "Powdery Mildew",
            "desc_id": "Bercak putih seperti tepung yang meluas menutupi daun dan batang, daun menggulung, pertumbuhan melambat.",
            "desc_en": "White powdery spots spreading over leaves and stems, leaves curling, stunted growth.",
            "ai_cat_id": "Bercak Putih",
            "ai_cat_en": "White Spots",
            "severity_text_id": "Rendah",
            "severity_text_en": "Low",
            "severity_class": "info"
        },
        {
            "name_id": "Embun Jelaga (Sooty Mold)",
            "name_en": "Sooty Mold",
            "desc_id": "Lapisan hitam seperti jelaga pada daun dan batang, mudah terhapus dengan kain lembap, residu lengket sebelum jelaga muncul.",
            "desc_en": "Black soot-like coating on leaves and stems, easily wiped off with a damp cloth, sticky residue before soot appears.",
            "ai_cat_id": "Bercak Bintik Hitam",
            "ai_cat_en": "Black Spot",
            "severity_text_id": "Rendah",
            "severity_text_en": "Low",
            "severity_class": "info"
        },
        {
            "name_id": "Bercak Daun Jamur/Bakteri (Leaf Spot)",
            "name_en": "Fungal/Bacterial Leaf Spot",
            "desc_id": "Bercak cokelat/hitam bulat pada permukaan daun, kadang disertai halo kuning di sekeliling bercak.",
            "desc_en": "Round brown/black spots on the leaf surface, sometimes with a yellow halo around them.",
            "ai_cat_id": "Bercak Bintik Hitam",
            "ai_cat_en": "Black Spot",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Bercak Cokelat (Brown Spots)",
            "name_en": "Brown Spots",
            "desc_id": "Terdapat bercak-bercak berwarna cokelat pada permukaan daun. Biasanya disebabkan oleh infeksi jamur atau kondisi kelembapan yang terlalu tinggi.",
            "desc_en": "Brown spots on the leaf surface. Usually caused by fungal infection or excessive humidity.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Bercak Putih (White Spots)",
            "name_en": "White Spots",
            "desc_id": "Bercak putih menyerupai tepung atau jamur pada daun. Sering kali disebabkan oleh embun tepung (powdery mildew) atau hama tertentu.",
            "desc_en": "White spots resembling powder or mold on the leaves. Often caused by powdery mildew or certain pests.",
            "ai_cat_id": "Bercak Putih",
            "ai_cat_en": "White Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Bercak Bintik Hitam (Black Spot)",
            "name_en": "Black Spot",
            "desc_id": "Bintik-bintik hitam kecil yang menyebar di permukaan daun. Dapat menyebabkan daun menguning dan gugur secara prematur.",
            "desc_en": "Small black spots spreading on the leaf surface. Can cause leaves to yellow and drop prematurely.",
            "ai_cat_id": "Bercak Bintik Hitam",
            "ai_cat_en": "Black Spot",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Karat Daun (Rust)",
            "name_en": "Leaf Rust",
            "desc_id": "Terdapat pustul atau bintik menonjol berwarna oranye, merah karat, atau cokelat di permukaan bawah atau atas daun.",
            "desc_en": "Raised orange, rust-red, or brown pustules or spots on the lower or upper surface of leaves.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Kutu Putih (Mealybugs)",
            "name_en": "Mealybugs",
            "desc_id": "Bercak putih seperti kapas di sela-sela daun atau batang. Daun terlihat kusam, lengket (embun madu), dan berdebu hitam (jamur jelaga).",
            "desc_en": "Cotton-like white spots between leaves or stems. Leaves look dull, sticky (honeydew), and black dusty (sooty mold).",
            "ai_cat_id": "Bercak Putih",
            "ai_cat_en": "White Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Kutu Daun (Aphids)",
            "name_en": "Aphids",
            "desc_id": "Serangga kecil yang berkumpul di pucuk daun muda. Dapat menyebabkan daun mengeriting dan pertumbuhan tanaman terhambat.",
            "desc_en": "Small insects clustering on young leaf shoots. Can cause leaf curling and stunt plant growth.",
            "ai_cat_id": "Daun Layu",
            "ai_cat_en": "Wilted Leaves",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Tungau Laba-laba (Spider Mites)",
            "name_en": "Spider Mites",
            "desc_id": "Daun terlihat memiliki bintik-bintik kuning kecil dan kusam. Terlihat adanya jaring halus di sekitar pangkal daun jika sudah parah.",
            "desc_en": "Leaves show small yellow spots and look dull. Fine webbing can be seen around the leaf base if severe.",
            "ai_cat_id": "Bercak Bintik Hitam",
            "ai_cat_en": "Black Spot",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Busuk Abu-abu (Botrytis Blight)",
            "name_en": "Botrytis Blight",
            "desc_id": "Bercak abu-abu/cokelat berair pada daun, daun lunak dan membusuk, muncul jamur putih/abu-abu/cokelat gelap, batang dan bunga ikut layu.",
            "desc_en": "Watery gray/brown spots on leaves, leaves become soft and rot, white/gray/dark brown mold appears, stems and flowers also wilt.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Antraknosa (Anthracnose / Leaf Spot)",
            "name_en": "Anthracnose",
            "desc_id": "Bercak kecil yang membesar dan bertambah banyak, berkembang dari kuning menjadi cokelat hingga lesi cekung gelap, kadang disertai halo kuning.",
            "desc_en": "Small spots that enlarge and multiply, developing from yellow to brown to dark sunken lesions, sometimes with a yellow halo.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Sedang",
            "severity_text_en": "Medium",
            "severity_class": "warning"
        },
        {
            "name_id": "Hawar Bakteri (Bacterial Blight)",
            "name_en": "Bacterial Blight",
            "desc_id": "Bercak kecil berair (water-soaked spots) yang membesar menjadi area cokelat nekrotik, muncul cairan lengket (ooze) pada kondisi lembap.",
            "desc_en": "Water-soaked spots that enlarge into necrotic brown areas, sticky ooze appears in humid conditions.",
            "ai_cat_id": "Bercak Cokelat",
            "ai_cat_en": "Brown Spots",
            "severity_text_id": "Tinggi",
            "severity_text_en": "High",
            "severity_class": "danger"
        },
        {
            "name_id": "Busuk Akar (Root Rot)",
            "name_en": "Root Rot",
            "desc_id": "Daun menguning dan layu terasa lunak, batang lembek dekat media tanam, akar berubah abu-abu/cokelat/hitam dan lembek, bau apek/busuk dari media tanam.",
            "desc_en": "Leaves yellow and wilt feeling soft, stems mushy near the soil, roots turn gray/brown/black and mushy, musty/rotten smell from potting mix.",
            "ai_cat_id": "Daun Layu",
            "ai_cat_en": "Wilted Leaves",
            "severity_text_id": "Tinggi",
            "severity_text_en": "High",
            "severity_class": "danger"
        },
        {
            "name_id": "Daun Layu (Wilting Leaves)",
            "name_en": "Wilting Leaves",
            "desc_id": "Daun terlihat kehilangan turgor (kekakuan), keriput, atau menguning. Bisa mengindikasikan masalah pada akar, seperti busuk akar (root rot) atau kekurangan/kelebihan air.",
            "desc_en": "Leaves look to have lost turgor (stiffness), wrinkled, or yellowing. Can indicate root problems like root rot or over/underwatering.",
            "ai_cat_id": "Daun Layu",
            "ai_cat_en": "Wilted Leaves",
            "severity_text_id": "Tinggi",
            "severity_text_en": "High",
            "severity_class": "danger"
        }
    ],
    "species": [
        {
            "no": "1",
            "name": "Hoya Macrophylla",
            "cat_id": "Tanaman Hias",
            "cat_en": "Ornamental Plant",
            "cat_class": "species-hias",
            "desc_id": "Dikenal dengan daun besarnya yang tebal dan berurat indah. Cocok sebagai tanaman gantung dekoratif di dalam ruangan.",
            "desc_en": "Known for its large, thick leaves with beautiful veins. Suitable as a decorative indoor hanging plant."
        },
        {
            "no": "2",
            "name": "Hoya Wayeti",
            "cat_id": "Tanaman Hias",
            "cat_en": "Ornamental Plant",
            "cat_class": "species-hias",
            "desc_id": "Memiliki daun ramping memanjang dan bunga berwarna merah muda keunguan. Mudah dirawat dan populer di kalangan kolektor.",
            "desc_en": "Has elongated slender leaves and purplish-pink flowers. Easy to care for and popular among collectors."
        },
        {
            "no": "3",
            "name": "Hoya australis",
            "cat_id": "Tanaman Hias & Obat",
            "cat_en": "Ornamental & Medicinal",
            "cat_class": "species-hias",
            "desc_id": "Spesies asal Australia yang cepat tumbuh. Selain sebagai tanaman hias, secara tradisional digunakan dalam pengobatan herbal.",
            "desc_en": "A fast-growing Australian species. Besides being an ornamental plant, it is traditionally used in herbal medicine."
        },
        {
            "no": "4",
            "name": "Hoya callistophylla",
            "cat_id": "Tanaman Hias",
            "cat_en": "Ornamental Plant",
            "cat_class": "species-hias",
            "desc_id": "Terkenal karena pola urat daun yang sangat kontras dan artistik menyerupai motif batik. Sangat dicari kolektor.",
            "desc_en": "Famous for its highly contrasting and artistic leaf vein pattern resembling batik. Highly sought by collectors."
        },
        {
            "no": "5",
            "name": "Hoya finlaysonii",
            "cat_id": "Tanaman Hias & Obat",
            "cat_en": "Ornamental & Medicinal",
            "cat_class": "species-hias",
            "desc_id": "Memiliki daun bertekstur unik dengan urat yang menonjol. Digunakan secara tradisional untuk pengobatan di beberapa daerah Asia Tenggara.",
            "desc_en": "Has uniquely textured leaves with prominent veins. Traditionally used for medicine in some Southeast Asian regions."
        },
        {
            "no": "6",
            "name": "Hoya imperialis",
            "cat_id": "Tanaman Hias",
            "cat_en": "Ornamental Plant",
            "cat_class": "species-hias",
            "desc_id": "Spesies Hoya terbesar dengan bunga berdiameter hingga 8 cm dan beraroma harum. Dijuluki \"Ratu Hoya\".",
            "desc_en": "The largest Hoya species with flowers up to 8 cm in diameter and fragrant. Dubbed \"The Queen of Hoyas\"."
        },
        {
            "no": "7",
            "name": "Hoya kerrii",
            "cat_id": "Tanaman Hias & Obat",
            "cat_en": "Ornamental & Medicinal",
            "cat_class": "species-hias",
            "desc_id": "Dikenal sebagai \"Sweetheart Hoya\" karena bentuk daunnya yang menyerupai hati. Populer sebagai hadiah Valentine dan memiliki khasiat obat tradisional.",
            "desc_en": "Known as the \"Sweetheart Hoya\" due to its heart-shaped leaves. Popular as a Valentine gift and has traditional medicinal properties."
        },
        {
            "no": "8",
            "name": "Hoya lacunosa",
            "cat_id": "Tanaman Hias & Obat",
            "cat_en": "Ornamental & Medicinal",
            "cat_class": "species-hias",
            "desc_id": "Spesies kecil yang harum semerbak terutama di malam hari. Getah daunnya digunakan secara tradisional untuk mengobati luka ringan.",
            "desc_en": "A small species that is very fragrant, especially at night. Its leaf sap is traditionally used to treat minor wounds."
        },
        {
            "no": "9",
            "name": "Hoya pubicalyx",
            "cat_id": "Tanaman Hias",
            "cat_en": "Ornamental Plant",
            "cat_class": "species-hias",
            "desc_id": "Salah satu spesies Hoya paling mudah dirawat. Memiliki bunga berwarna merah muda hingga ungu tua berbentuk bintang.",
            "desc_en": "One of the easiest Hoya species to care for. Has star-shaped pink to deep purple flowers."
        },
        {
            "no": "10",
            "name": "Hoya carnosa",
            "cat_id": "Tanaman Hias & Obat",
            "cat_en": "Ornamental & Medicinal",
            "cat_class": "species-hias",
            "desc_id": "Spesies Hoya paling klasik dan populer. Dikenal memiliki daun tebal berlilin dan bunga berbentuk bintang beraroma manis. Digunakan dalam pengobatan tradisional Tiongkok.",
            "desc_en": "The most classic and popular Hoya species. Known for its thick waxy leaves and sweet-smelling star-shaped flowers. Used in traditional Chinese medicine."
        }
    ]
};
