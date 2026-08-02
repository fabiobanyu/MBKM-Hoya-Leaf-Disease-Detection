const translations = {
    id: {
        nav_home: 'Beranda',
        nav_disease: 'Gejala Penyakit',
        nav_species: '10 Spesies',
        upload_title: 'Unggah Daun Hoya',
        upload_desc: 'Tarik & lepas gambar di sini, atau klik untuk memilih',
        upload_btn: 'Pilih File',
        camera_hint: 'Posisikan daun di dalam bingkai dan ambil foto',
        crop_hint: 'Atur pemotong (crop) agar fokus pada area daun utama.',
        about_title: 'Tentang Hoya Vision',
        about_p1: 'Hoya Vision merupakan sistem berbasis kecerdasan buatan (AI) hasil riset kolaboratif antara BRIN (Badan Riset dan Inovasi Nasional) dan ITERA (Institut Teknologi Sumatera). Platform ini dirancang secara khusus untuk mendeteksi berbagai jenis penyakit yang menyerang daun tanaman Hoya, serta mengidentifikasi hingga 10 spesies Hoya yang berbeda secara otomatis hanya melalui sebuah foto.',
        about_p2: 'Sistem ini diintegrasikan dengan Knowledge Graph (KG) yang mampu menyajikan informasi terstruktur dan komprehensif mengenai penanganan penyakit, penyebab, dan langkah preventif, membantu para peneliti maupun pembudidaya tanaman hias menjaga kesehatan tanaman Hoya dengan lebih presisi dan efisien.',
        disease_title: 'Informasi Gejala Penyakit Hoya',
        disease_desc: 'Kenali berbagai jenis penyakit yang menyerang tanaman Hoya beserta ciri-ciri visualnya. Penyakit-penyakit di bawah ini memiliki panduan penanganan lengkap dari Knowledge Graph yang akan muncul otomatis saat Anda scan daun.',
        th_disease_name: 'Jenis Penyakit',
        th_disease_symp: 'Gejala Visual pada Daun',
        th_disease_ai: 'Kategori AI',
        th_disease_sev: 'Keparahan',
        species_title: '10 Spesies Tanaman Hoya',
        species_desc: 'Daftar 10 spesies Hoya yang saat ini dikenali oleh model AI kami beserta karakteristik bentuk daun dan habitat aslinya.',
        th_species_no: 'No',
        th_species_name: 'Nama Spesies',
        th_species_cat: 'Kategori Pemanfaatan',
        th_species_desc: 'Deskripsi Singkat',

        error_title_noise: 'Sistem Keamanan AI',
        error_msg_noise_small: 'Gambar Terdeteksi Bukan Daun Hoya. Ukuran gambar terlalu kecil, harap gunakan foto yang lebih besar.',
        error_msg_noise_blur: 'Gambar Terdeteksi Bukan Daun Hoya. Foto terlalu buram atau tidak fokus, harap foto ulang daun dengan lebih jelas.',
        error_msg_noise_ood: 'Gambar Terdeteksi Bukan Daun Hoya. Sistem mendeteksi objek ini bukan daun Hoya (tanaman/objek lain). Harap pastikan foto memperlihatkan daun Hoya.',
        error_title_conf: 'Peringatan Kepastian Rendah',
        error_msg_conf: 'Sistem kesulitan mengenali daun Hoya ini secara pasti. Hal ini biasa terjadi akibat sudut pengambilan foto, pantulan cahaya, atau fokus crop yang kurang pas. Harap coba foto ulang lebih dekat dan terang.',
        kg_treatment_info: 'Informasi Penanganan',
        btn_remove: 'Hapus',
        btn_analyze: 'Analisis Gambar',
        btn_rotate_left: 'Putar Kiri',
        btn_rotate_right: 'Putar Kanan',
        btn_flip_h: 'Balik Horizontal',
        btn_flip_v: 'Balik Vertikal',
        btn_reset: 'Reset',

        cat_sehat: 'Sehat',
        cat_bercak_cokelat: 'Bercak Cokelat',
        cat_bercak_putih: 'Bercak Putih',
        cat_daun_layu: 'Daun Layu',
        cat_bercak_bintik_hitam: 'Bercak Bintik Hitam'
    },
    en: {
        nav_home: 'Home',
        nav_disease: 'Disease Symptoms',
        nav_species: '10 Species',
        upload_title: 'Upload Hoya Leaf',
        upload_desc: 'Drag & drop your image here, or click to browse',
        upload_btn: 'Browse Files',
        camera_hint: 'Position the leaf in the frame and capture',
        crop_hint: 'Adjust the crop box to focus on the main leaf area.',
        about_title: 'About Hoya Vision',
        about_p1: 'Hoya Vision is an Artificial Intelligence (AI) system resulting from collaborative research between BRIN (National Research and Innovation Agency) and ITERA (Sumatera Institute of Technology). This platform is specifically designed to detect various diseases attacking Hoya plant leaves and automatically identify up to 10 different Hoya species from just a single photo.',
        about_p2: 'The system is integrated with a Knowledge Graph (KG) that provides structured and comprehensive information regarding disease treatments, causes, and preventive measures, helping researchers and ornamental plant cultivators maintain Hoya plant health with greater precision and efficiency.',
        disease_title: 'Hoya Disease Symptoms Information',
        disease_desc: 'Recognize the various types of diseases that attack Hoya plants along with their visual characteristics. The diseases below have complete treatment guidelines from the Knowledge Graph that will appear automatically when you scan a leaf.',
        th_disease_name: 'Disease Type',
        th_disease_symp: 'Visual Symptoms on Leaves',
        th_disease_ai: 'AI Category',
        th_disease_sev: 'Severity',
        species_title: '10 Hoya Plant Species',
        species_desc: 'A list of 10 Hoya species currently recognized by our AI model, along with their leaf shape characteristics and natural habitats.',
        th_species_no: 'No',
        th_species_name: 'Species Name',
        th_species_cat: 'Utilization Category',
        th_species_desc: 'Brief Description',

        error_title_noise: 'AI Security System',
        error_msg_noise_small: 'Image Detected as Non-Hoya Leaf. The image size is too small, please use a larger photo.',
        error_msg_noise_blur: 'Image Detected as Non-Hoya Leaf. The photo is too blurry or out of focus, please retake a clearer photo of the leaf.',
        error_msg_noise_ood: 'Image Detected as Non-Hoya Leaf. The system detected that this object is not a Hoya leaf (another plant/object). Please ensure the photo shows a Hoya leaf.',
        error_title_conf: 'Low Confidence Warning',
        error_msg_conf: 'The system has difficulty recognizing this Hoya leaf definitively. This commonly happens due to the photo angle, light reflections, or poor crop focus. Please try retaking the photo closer and brighter.',
        kg_treatment_info: 'Treatment Information',
        btn_remove: 'Remove',
        btn_analyze: 'Analyze Image',
        btn_rotate_left: 'Rotate Left',
        btn_rotate_right: 'Rotate Right',
        btn_flip_h: 'Flip Horizontal',
        btn_flip_v: 'Flip Vertical',
        btn_reset: 'Reset',

        cat_sehat: 'Healthy',
        cat_bercak_cokelat: 'Brown Spots',
        cat_bercak_putih: 'White Spots',
        cat_daun_layu: 'Wilted Leaves',
        cat_bercak_bintik_hitam: 'Black Spot'
    }
};

let currentAppLang = localStorage.getItem('appLang') || 'id';

function applyTranslations(lang) {
    currentAppLang = lang;
    localStorage.setItem('appLang', lang);

    const langToggleBtn = document.getElementById('langToggleBtn');
    const langID = document.getElementById('langID');
    const langEN = document.getElementById('langEN');

    if (langToggleBtn) {

        if (langToggleBtn.type === 'checkbox') {
            langToggleBtn.checked = (lang === 'en');
            if (langID && langEN) {
                if (lang === 'en') {
                    langID.classList.remove('active-id');
                    langEN.classList.add('active-en');
                } else {
                    langID.classList.add('active-id');
                    langEN.classList.remove('active-en');
                }
            }
        } else {

            const langBtnText = document.getElementById('currentLangText');
            if (langBtnText) langBtnText.textContent = lang.toUpperCase();
        }
    }

    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {

            const icon = el.querySelector('i');
            if (icon) {
                el.innerHTML = '';
                el.appendChild(icon);
                el.appendChild(document.createTextNode(' ' + translations[lang][key]));
            } else {
                el.innerHTML = translations[lang][key];
            }
        }
    });

    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (translations[lang] && translations[lang][key]) {
            el.setAttribute('placeholder', translations[lang][key]);
        }
    });

    if (typeof TABLE_DATA !== 'undefined') {
        const diseaseTableBody = document.getElementById('diseaseTableBody');
        const speciesTableBody = document.getElementById('speciesTableBody');

        const tables = [diseaseTableBody, speciesTableBody].filter(Boolean);
        tables.forEach(tbody => tbody.style.opacity = '0.3');

        setTimeout(() => {
            renderDynamicTables(lang);
            tables.forEach(tbody => {
                tbody.style.transition = 'opacity 0.3s ease-in-out';
                tbody.style.opacity = '1';
            });
        }, 150);
    }

    document.dispatchEvent(new CustomEvent('languageChanged', { detail: { lang } }));
}

function renderDynamicTables(lang) {
    if (typeof TABLE_DATA === 'undefined') return;

    const diseaseTableBody = document.getElementById('diseaseTableBody');
    if (diseaseTableBody) {
        diseaseTableBody.innerHTML = TABLE_DATA.diseases.map(d => {
            let typeBadge = '';
            if (d.type === 'pest') {
                typeBadge = `<br><span class="badge-type badge-type-pest"><i class="fa-solid fa-bug"></i> ${lang === 'en' ? 'Pest' : 'Hama'}</span>`;
            } else if (d.type === 'category') {
                typeBadge = `<br><span class="badge-type badge-type-category"><i class="fa-solid fa-layer-group"></i> ${lang === 'en' ? 'General Category' : 'Kategori Umum'}</span>`;
            } else {
                typeBadge = `<br><span class="badge-type badge-type-disease"><i class="fa-solid fa-virus"></i> ${lang === 'en' ? 'Disease' : 'Penyakit'}</span>`;
            }

            return `
            <tr>
                <td><strong>${lang === 'en' ? d.name_en : d.name_id}</strong>${typeBadge}</td>
                <td>${lang === 'en' ? d.desc_en : d.desc_id}</td>
                <td><span class="badge category-badge">${lang === 'en' ? d.ai_cat_en : d.ai_cat_id}</span></td>
                <td><span class="badge ${d.severity_class}">${lang === 'en' ? d.severity_text_en : d.severity_text_id}</span></td>
            </tr>
        `;
        }).join('');
    }

    const speciesTableBody = document.getElementById('speciesTableBody');
    if (speciesTableBody) {
        speciesTableBody.innerHTML = TABLE_DATA.species.map(s => `
            <tr>
                <td>${s.no}</td>
                <td><strong>${s.name}</strong></td>
                <td><span class="badge ${s.cat_class}">${lang === 'en' ? s.cat_en : s.cat_id}</span></td>
                <td>${lang === 'en' ? s.desc_en : s.desc_id}</td>
            </tr>
        `).join('');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    applyTranslations(currentAppLang);

    const toggleBtn = document.getElementById('langToggleBtn');
    const toggleBtnMobile = document.getElementById('langToggleBtnMobile');

    // Sync mobile toggle initial state
    if (toggleBtnMobile) {
        toggleBtnMobile.checked = (currentAppLang === 'en');
    }

    if (toggleBtn) {
        if (toggleBtn.type === 'checkbox') {
            toggleBtn.addEventListener('change', () => {
                const newLang = toggleBtn.checked ? 'en' : 'id';
                if (toggleBtnMobile) toggleBtnMobile.checked = toggleBtn.checked;
                applyTranslations(newLang);
            });
        } else {
            toggleBtn.addEventListener('click', () => {
                const newLang = currentAppLang === 'id' ? 'en' : 'id';
                applyTranslations(newLang);
            });
        }
    }

    // Mobile toggle listener
    if (toggleBtnMobile) {
        toggleBtnMobile.addEventListener('change', () => {
            const newLang = toggleBtnMobile.checked ? 'en' : 'id';
            if (toggleBtn) toggleBtn.checked = toggleBtnMobile.checked;
            applyTranslations(newLang);
        });
    }
});
