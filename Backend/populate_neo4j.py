from neo4j import GraphDatabase

# Configuration
# ==========================================
# UBAH KREDENSIAL INI SESUAI DENGAN NEO4J ANDA
URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "12345678" 
# ==========================================

class HoyaKnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            # Drop all existing data to start fresh
            session.run("MATCH (n) DETACH DELETE n")
            
            # Create uniqueness constraints based on EN name (as primary identifier)
            constraints = [
                "CREATE CONSTRAINT IF NOT EXISTS FOR (s:HoyaSpecies) REQUIRE s.name_en IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.name_en IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (sym:Symptom) REQUIRE sym.name_en IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (c:CausalFactor) REQUIRE c.name_en IS UNIQUE",
                "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Treatment) REQUIRE t.name_en IS UNIQUE"
            ]
            for query in constraints:
                session.run(query)
            print("Constraints created.")

    def populate(self):
        # 1. Data Spesies (Sesuai dengan dataset AI)
        species_list = [
            "Hoya Macrophylla", "Hoya Wayeti", "Hoya australis", 
            "Hoya callistophylla", "Hoya finlaysonii", "Hoya imperialis", 
            "Hoya kerrii", "Hoya lacunosa", "Hoya pubicalyx", "hoya carnosa"
        ]

        # 2. Data Penyakit & Kategori Gejala Dataset (Jembatan ke Machine Learning)
        diseases = [
            {"en": "Botrytis Blight", "id": "Busuk Abu-abu", "category": "Bercak Cokelat"},
            {"en": "Anthracnose / Leaf Spot Disease", "id": "Antraknosa / Penyakit Bercak Daun", "category": "Bercak Cokelat"},
            {"en": "Bacterial Blight", "id": "Hawar Bakteri", "category": "Bercak Cokelat"},
            {"en": "Powdery Mildew", "id": "Embun Tepung", "category": "Bercak Putih"},
            {"en": "Sooty Mold", "id": "Embun Jelaga", "category": "Bercak Bintik Hitam"},
            {"en": "Unspecified Fungal/Bacterial Leaf Spot", "id": "Bercak Daun Jamur/Bakteri Tidak Spesifik", "category": "Bercak Bintik Hitam"},
            {"en": "Root Rot", "id": "Busuk Akar", "category": "Daun Layu"}
        ]

        # 3. Struktur Pengetahuan Relasional Bilingual
        knowledge = {
            "Botrytis Blight": {
                "symptoms": [
                    {"id": "Bercak abu-abu/cokelat berair pada daun", "en": "Water-soaked gray/brown spots on leaves"},
                    {"id": "Daun lunak dan membusuk", "en": "Leaves become soft and rot"},
                    {"id": "Muncul jamur putih/abu-abu/cokelat gelap", "en": "Appearance of white/gray/dark brown mold"},
                    {"id": "Batang dan bunga ikut layu", "en": "Stems and flowers wilt"}
                ],
                "causes": [
                    {"id": "Kelembapan tinggi", "en": "High humidity"},
                    {"id": "Suhu dingin", "en": "Cold temperatures"},
                    {"id": "Sirkulasi udara buruk", "en": "Poor air circulation"},
                    {"id": "Sisa bunga/daun mati yang menempel di tanaman", "en": "Dead flowers/leaves clinging to the plant"}
                ],
                "treatments": [
                    {"id": "Isolasi tanaman", "en": "Isolate the plant"},
                    {"id": "Buang seluruh bagian terinfeksi", "en": "Remove all infected parts"},
                    {"id": "Tingkatkan sirkulasi udara", "en": "Improve air circulation"},
                    {"id": "Aplikasikan fungisida (umum)", "en": "Apply general fungicide"}
                ]
            },
            "Anthracnose / Leaf Spot Disease": {
                "symptoms": [
                    {"id": "Bercak kecil yang membesar dan bertambah banyak", "en": "Small spots that enlarge and multiply"},
                    {"id": "Berkembang dari kuning menjadi cokelat hingga lesi cekung gelap", "en": "Develops from yellow to brown to dark sunken lesions"},
                    {"id": "Kadang disertai halo kuning", "en": "Sometimes accompanied by a yellow halo"}
                ],
                "causes": [
                    {"id": "Air menggenang di daun", "en": "Water pooling on leaves"},
                    {"id": "Percikan tanah saat penyiraman", "en": "Soil splashing during watering"},
                    {"id": "Alat pangkas terkontaminasi", "en": "Contaminated pruning tools"},
                    {"id": "Sirkulasi udara buruk", "en": "Poor air circulation"}
                ],
                "treatments": [
                    {"id": "Buang daun terinfeksi", "en": "Remove infected leaves"},
                    {"id": "Siram ke media, bukan ke daun", "en": "Water the soil, not the leaves"},
                    {"id": "Tingkatkan sirkulasi udara", "en": "Improve air circulation"},
                    {"id": "Aplikasikan fungisida tembaga", "en": "Apply copper fungicide"}
                ]
            },
            "Bacterial Blight": {
                "symptoms": [
                    {"id": "Bercak kecil berair (water-soaked spots)", "en": "Small water-soaked spots"},
                    {"id": "Membesar menjadi area cokelat nekrotik", "en": "Enlarges into brown necrotic areas"},
                    {"id": "Muncul cairan lengket (ooze) pada kondisi lembap", "en": "Sticky ooze appears in humid conditions"}
                ],
                "causes": [
                    {"id": "Kelembapan tinggi", "en": "High humidity"},
                    {"id": "Penyiraman dari atas", "en": "Overhead watering"},
                    {"id": "Luka pada jaringan daun", "en": "Wounds on leaf tissue"}
                ],
                "treatments": [
                    {"id": "Isolasi tanaman", "en": "Isolate the plant"},
                    {"id": "Pangkas dengan alat steril", "en": "Prune with sterile tools"},
                    {"id": "Hindari penyiraman dari atas", "en": "Avoid overhead watering"},
                    {"id": "Perbaiki pencahayaan dan sirkulasi udara", "en": "Improve lighting and air circulation"}
                ]
            },
            "Powdery Mildew": {
                "symptoms": [
                    {"id": "Bercak putih seperti tepung", "en": "White powdery spots"},
                    {"id": "Meluas menutupi daun dan batang", "en": "Spreads to cover leaves and stems"},
                    {"id": "Daun menggulung", "en": "Curling leaves"},
                    {"id": "Pertumbuhan melambat", "en": "Stunted growth"}
                ],
                "causes": [
                    {"id": "Sirkulasi udara buruk", "en": "Poor air circulation"},
                    {"id": "Tanaman terlalu rapat", "en": "Overcrowded plants"},
                    {"id": "Ruang tertutup", "en": "Enclosed space"}
                ],
                "treatments": [
                    {"id": "Isolasi tanaman", "en": "Isolate the plant"},
                    {"id": "Buang daun terserang berat", "en": "Remove heavily infected leaves"},
                    {"id": "Tingkatkan sirkulasi udara", "en": "Improve air circulation"},
                    {"id": "Aplikasikan fungisida khusus", "en": "Apply specific fungicide"}
                ]
            },
            "Sooty Mold": {
                "symptoms": [
                    {"id": "Lapisan hitam seperti jelaga pada daun dan batang", "en": "Soot-like black layer on leaves and stems"},
                    {"id": "Mudah terhapus dengan kain lembap", "en": "Easily wiped off with a damp cloth"},
                    {"id": "Residu lengket sebelum jelaga muncul", "en": "Sticky residue before mold appears"}
                ],
                "causes": [
                    {"id": "Hama pengisap getah penghasil honeydew", "en": "Sap-sucking pests producing honeydew"}
                ],
                "treatments": [
                    {"id": "Kendalikan hama (sabun insektisida/neem oil)", "en": "Control pests (insecticidal soap/neem oil)"},
                    {"id": "Bersihkan jelaga dengan kain lembap", "en": "Clean mold with a damp cloth"}
                ]
            },
            "Unspecified Fungal/Bacterial Leaf Spot": {
                "symptoms": [
                    {"id": "Bercak cokelat/hitam bulat", "en": "Round brown/black spots"},
                    {"id": "Kadang disertai halo kuning", "en": "Sometimes accompanied by a yellow halo"}
                ],
                "causes": [
                    {"id": "Daun basah berkepanjangan", "en": "Prolonged leaf wetness"},
                    {"id": "Sirkulasi udara buruk", "en": "Poor air circulation"},
                    {"id": "Alat pangkas terkontaminasi", "en": "Contaminated pruning tools"}
                ],
                "treatments": [
                    {"id": "Buang daun terinfeksi", "en": "Remove infected leaves"},
                    {"id": "Tingkatkan sirkulasi udara", "en": "Improve air circulation"},
                    {"id": "Aplikasikan fungisida tembaga", "en": "Apply copper fungicide"}
                ]
            },
            "Root Rot": {
                "symptoms": [
                    {"id": "Daun menguning dan layu, terasa lunak", "en": "Yellowing and wilting leaves, feeling soft"},
                    {"id": "Batang lembek dekat media tanam", "en": "Soft stems near the potting mix"},
                    {"id": "Akar berubah abu-abu/cokelat/hitam dan lembek", "en": "Roots turn gray/brown/black and soft"},
                    {"id": "Bau apek/busuk dari media tanam", "en": "Musty/foul odor from the potting mix"}
                ],
                "causes": [
                    {"id": "Penyiraman berlebih dalam waktu lama", "en": "Prolonged overwatering"},
                    {"id": "Media tanam padat atau drainase buruk", "en": "Compacted potting mix or poor drainage"}
                ],
                "treatments": [
                    {"id": "Keluarkan tanaman dari pot", "en": "Remove the plant from its pot"},
                    {"id": "Potong akar yang busuk", "en": "Trim rotted roots"},
                    {"id": "Tanam ulang di media porous dengan drainase baik", "en": "Repot in porous mix with good drainage"},
                    {"id": "Siram hanya saat media benar-benar kering", "en": "Water only when the mix is completely dry"}
                ]
            }
        }

        with self.driver.session() as session:
            # 1. Create Species Nodes
            print("Creating Species Nodes...")
            for sp in species_list:
                session.run(
                    "MERGE (s:HoyaSpecies {name_en: $name}) "
                    "SET s.name_id = $name",
                    name=sp
                )
            
            # 2. Create Disease Nodes
            print("Creating Disease Nodes...")
            for d in diseases:
                session.run(
                    "MERGE (dis:Disease {name_en: $en}) "
                    "SET dis.name_id = $id, dis.category = $cat",
                    en=d["en"], id=d["id"], cat=d["category"]
                )

            # 3. Create Symptoms, CausalFactors, Treatments, and Relationships
            print("Creating Bilingual Symptoms, Causes, Treatments and their Relationships...")
            for disease_en, data in knowledge.items():
                
                # Relasi hasSymptom
                for sym in data["symptoms"]:
                    session.run(
                        """
                        MATCH (d:Disease {name_en: $d_name})
                        MERGE (s:Symptom {name_en: $s_en})
                        SET s.name_id = $s_id
                        MERGE (d)-[:HAS_SYMPTOM]->(s)
                        """,
                        d_name=disease_en, s_en=sym["en"], s_id=sym["id"]
                    )
                
                # Relasi favoredBy (Faktor Pemicu)
                for cause in data["causes"]:
                    session.run(
                        """
                        MATCH (d:Disease {name_en: $d_name})
                        MERGE (c:CausalFactor {name_en: $c_en})
                        SET c.name_id = $c_id
                        MERGE (d)-[:FAVORED_BY]->(c)
                        """,
                        d_name=disease_en, c_en=cause["en"], c_id=cause["id"]
                    )
                
                # Relasi treatedWith (Penanganan)
                for treatment in data["treatments"]:
                    session.run(
                        """
                        MATCH (d:Disease {name_en: $d_name})
                        MERGE (t:Treatment {name_en: $t_en})
                        SET t.name_id = $t_id
                        MERGE (d)-[:TREATED_WITH]->(t)
                        """,
                        d_name=disease_en, t_en=treatment["en"], t_id=treatment["id"]
                    )
            
            print("Bilingual Knowledge Graph successfully populated!")

if __name__ == "__main__":
    try:
        kg = HoyaKnowledgeGraph(URI, USERNAME, PASSWORD)
        kg.create_constraints()
        kg.populate()
        kg.close()
        print("\nSelesai! Database sekarang memiliki properti dwibahasa (name_id dan name_en).")
    except Exception as e:
        print(f"\nError: {e}")
        print("Pastikan Neo4j sudah berjalan dan kredensial (URI, Username, Password) di skrip sudah benar!")
