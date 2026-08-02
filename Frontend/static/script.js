document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');

    const uploadPanel = document.getElementById('uploadPanel');
    const previewArea = document.getElementById('previewArea');
    const imagePreview = document.getElementById('imagePreview');
    const removeBtn = document.getElementById('removeBtn');
    const analyzeBtn = document.getElementById('analyzeBtn');

    const errorBanner = document.getElementById('errorBanner');
    const errorMessage = document.getElementById('errorMessage');
    const closeErrorBtn = document.getElementById('closeErrorBtn');

    const logoHome = document.getElementById('logoHome');

    const navHomeBtn = document.getElementById('navHomeBtn');
    const navDiseaseBtn = document.getElementById('navDiseaseBtn');
    const homePage = document.getElementById('homePage');
    const diseaseInfoPage = document.getElementById('diseaseInfoPage');

    const fabCameraToggleBtn = document.getElementById('fabCameraToggleBtn');
    let isCameraMode = false;
    const cameraZone = document.getElementById('cameraZone');
    const cameraStream = document.getElementById('cameraStream');
    const cameraCanvas = document.getElementById('cameraCanvas');
    const captureBtn = document.getElementById('captureBtn');
    const brightnessSlider = document.getElementById('brightnessSlider');

    const hamburgerBtn = document.getElementById('hamburgerBtn');
    const navMenu = document.getElementById('navMenu');
    if (hamburgerBtn && navMenu) {
        hamburgerBtn.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
        
        // Close menu when clicking a nav button (use getElementById to avoid referencing undeclared const)
        ['navHomeBtn', 'navDiseaseBtn', 'navSpeciesBtn'].forEach(id => {
            const btn = document.getElementById(id);
            if (btn) btn.addEventListener('click', () => navMenu.classList.remove('active'));
        });
    }

    let cameraMediaStream = null;

    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');

    const btnOriginal = document.getElementById('btnOriginal');
    const btnGradCam = document.getElementById('btnGradCam');
    const resultImageOriginal = document.getElementById('resultImageOriginal');
    const resultImageGradcam = document.getElementById('resultImageGradcam');
    const newAnalysisBtn = document.getElementById('newAnalysisBtn');
    const retryCropBtn = document.getElementById('retryCropBtn');

    const langToggle = document.getElementById('langToggle');
    const knowledgeSection = document.getElementById('knowledgeSection');
    const knowledgeContainer = document.getElementById('knowledgeContainer');
    const knowledgeTitleText = document.getElementById('knowledgeTitleText');

    const historySection = document.getElementById('historySection');
    const historyContainer = document.getElementById('historyContainer');

    let currentFile = null;
    let cropper = null;
    let currentKnowledge = [];

    function hideErrorBanner() {
        if (!errorBanner || errorBanner.classList.contains('hidden') || errorBanner.classList.contains('collapsing-out')) return;
        errorBanner.classList.add('collapsing-out');
        setTimeout(() => {
            errorBanner.classList.add('hidden');
            errorBanner.classList.remove('collapsing-out');
        }, 300);
    }

    function showErrorBanner(msg, errorType) {
        if (!errorBanner || !errorMessage) return;

        if (typeof translations !== 'undefined' && currentAppLang) {
            if (errorType === 'confidence') {
                msg = translations[currentAppLang].error_msg_conf;
            } else if (msg.includes('terlalu kecil')) {
                msg = translations[currentAppLang].error_msg_noise_small;
            } else if (msg.includes('buram')) {
                msg = translations[currentAppLang].error_msg_noise_blur;
            } else {
                msg = translations[currentAppLang].error_msg_noise_ood;
            }
        }

        errorMessage.textContent = msg;
        const errorIconWrapper = document.getElementById('errorIconWrapper');
        const errorIcon = document.getElementById('errorIcon');
        const errorTitle = document.getElementById('errorTitle');

        if (errorType === 'confidence') {
            if (errorTitle) {
                errorTitle.textContent = (typeof translations !== 'undefined') ? translations[currentAppLang].error_title_conf : 'Sistem Keamanan AI';
            }
            errorBanner.style.background = 'rgba(245, 158, 11, 0.15)';
            errorBanner.style.border = '1px solid rgba(245, 158, 11, 0.3)';
            errorBanner.style.borderLeft = '5px solid #f59e0b';
            errorBanner.style.boxShadow = '0 10px 25px rgba(245, 158, 11, 0.15)';

            if (errorIconWrapper) {
                errorIconWrapper.style.background = 'rgba(245, 158, 11, 0.2)';
                errorIconWrapper.style.boxShadow = '0 0 15px rgba(245, 158, 11, 0.3)';
            }
            if (errorIcon) errorIcon.style.color = '#fcd34d';
            if (errorTitle) errorTitle.style.color = '#fcd34d';
        } else {
            if (errorTitle) {
                errorTitle.textContent = (typeof translations !== 'undefined') ? translations[currentAppLang].error_title_noise : 'Sistem Keamanan AI';
            }
            errorBanner.style.background = 'rgba(239, 68, 68, 0.15)';
            errorBanner.style.border = '1px solid rgba(239, 68, 68, 0.3)';
            errorBanner.style.borderLeft = '5px solid #ef4444';
            errorBanner.style.boxShadow = '0 10px 25px rgba(239, 68, 68, 0.15)';

            if (errorIconWrapper) {
                errorIconWrapper.style.background = 'rgba(239, 68, 68, 0.2)';
                errorIconWrapper.style.boxShadow = '0 0 15px rgba(239, 68, 68, 0.3)';
            }
            if (errorIcon) errorIcon.style.color = '#fca5a5';
            if (errorTitle) errorTitle.style.color = '#fca5a5';
        }

        errorBanner.classList.remove('hidden');
        errorBanner.classList.remove('collapsing-out');
        errorBanner.style.animation = 'fadeInDown 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards';
    }

    function transitionTo(hideElements, showElements, keepError = false) {
        const toHide = Array.isArray(hideElements) ? hideElements : [hideElements];
        const toShow = Array.isArray(showElements) ? showElements : [showElements];

        if (!keepError) {
            hideErrorBanner();
        }

        toHide.forEach(el => {
            if (el && !el.classList.contains('hidden')) {
                el.style.animation = 'fadeOutScale 0.25s ease-in forwards';
            }
        });

        setTimeout(() => {
            toHide.forEach(el => {
                if (el) {
                    el.classList.add('hidden');
                    el.style.animation = '';
                }
            });

            toShow.forEach(el => {
                if (el) {
                    el.classList.remove('hidden');
                    el.style.animation = 'fadeInScale 0.35s ease-out forwards';
                }
            });
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }, 240);
    }

    function renderKnowledge() {
        if (!knowledgeSection || !knowledgeContainer) return;

        if (!currentKnowledge || currentKnowledge.length === 0) {
            knowledgeSection.classList.remove('hidden');
            const offlineMsgId = `
                <div class="kg-offline-msg" style="text-align: center; padding: 30px; color: var(--text-muted);">
                    <i class="fa-solid fa-database" style="font-size: 2rem; opacity: 0.5; margin-bottom: 10px; display: block;"></i>
                    <p>Database Knowledge Graph (Neo4j) saat ini sedang offline atau tidak dapat diakses.</p>
                    <p style="font-size: 0.85rem; opacity: 0.7;">(Tidak ada informasi penanganan yang dapat ditampilkan)</p>
                </div>`;
            const offlineMsgEn = `
                <div class="kg-offline-msg" style="text-align: center; padding: 30px; color: var(--text-muted);">
                    <i class="fa-solid fa-database" style="font-size: 2rem; opacity: 0.5; margin-bottom: 10px; display: block;"></i>
                    <p>The Knowledge Graph Database (Neo4j) is currently offline or unreachable.</p>
                    <p style="font-size: 0.85rem; opacity: 0.7;">(No treatment information can be displayed)</p>
                </div>`;
            knowledgeContainer.innerHTML = currentAppLang === 'en' ? offlineMsgEn : offlineMsgId;
            return;
        }

        knowledgeSection.classList.remove('hidden');
        knowledgeContainer.innerHTML = '';

        currentKnowledge.forEach(disease => {

            const title = currentAppLang === 'en' ? disease.disease_en : (disease.disease_id || disease.disease_en);
            const typeIcon = disease.type === 'Pest' ? 'fa-bug' : 'fa-virus';

            let html = `
            <div class="knowledge-item">
                <h3><i class="fa-solid ${typeIcon}"></i> ${title}</h3>
                <div class="kg-grid">
            `;

            if (disease.symptoms && disease.symptoms.length > 0) {
                html += `
                <div class="kg-card">
                    <h4><i class="fa-solid fa-microscope text-gradient"></i> ${currentAppLang === 'en' ? 'Symptoms' : 'Gejala'}</h4>
                    <ul>
                        ${disease.symptoms.map(s => `<li>${s[currentAppLang] || s.en}</li>`).join('')}
                    </ul>
                </div>`;
            }

            if (disease.causes && disease.causes.length > 0) {
                html += `
                <div class="kg-card">
                    <h4><i class="fa-solid fa-temperature-half text-gradient"></i> ${currentAppLang === 'en' ? 'Causes' : 'Pemicu'}</h4>
                    <ul>
                        ${disease.causes.map(c => `<li>${c[currentAppLang] || c.en}</li>`).join('')}
                    </ul>
                </div>`;
            }

            if (disease.treatments && disease.treatments.length > 0) {
                html += `
                <div class="kg-card">
                    <h4><i class="fa-solid fa-kit-medical text-gradient"></i> ${currentAppLang === 'en' ? 'Treatment' : 'Penanganan'}</h4>
                    <ul>
                        ${disease.treatments.map(t => `<li>${t[currentAppLang] || t.en}</li>`).join('')}
                    </ul>
                </div>`;
            }

            html += `</div></div>`;
            knowledgeContainer.innerHTML += html;
        });
    }

    function saveHistory(data) {
        const historyItem = {
            id: Date.now(),
            image: data.images.original,
            species: data.species.name,
            disease: data.disease.name,
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
        };

        let history = [];
        try {
            const stored = localStorage.getItem('hoyaHistory');
            if (stored) history = JSON.parse(stored);
        } catch (e) {
            console.error("Local storage error", e);
        }

        history.unshift(historyItem);

        if (history.length > 5) {
            history = history.slice(0, 5);
        }

        try {
            localStorage.setItem('hoyaHistory', JSON.stringify(history));
        } catch (e) {
            console.error("Failed to save history", e);
        }

        renderHistory();
    }

    function renderHistory() {
        if (!historySection || !historyContainer) return;

        let history = [];
        try {
            const stored = localStorage.getItem('hoyaHistory');
            if (stored) history = JSON.parse(stored);
        } catch (e) { return; }

        if (history.length === 0) {
            historySection.classList.add('hidden');
            return;
        }

        historySection.classList.remove('hidden');
        historyContainer.innerHTML = '';

        history.forEach(item => {
            const card = document.createElement('div');
            card.className = 'history-card';
            card.innerHTML = `
                <img src="${item.image}" alt="History item">
                <div class="history-info">
                    <span class="h-species">${item.species}</span>
                    <span class="h-disease" style="color: ${item.disease.toLowerCase() === 'sehat' ? 'var(--primary-color)' : 'var(--secondary-color)'}">${item.disease}</span>
                    <span class="h-time"><i class="fa-regular fa-clock"></i> ${item.time}</span>
                </div>
            `;
            historyContainer.appendChild(card);
        });
    }

    renderHistory();

    browseBtn.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');

        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });

    if (fabCameraToggleBtn) {
        fabCameraToggleBtn.addEventListener('click', () => {
            if (isCameraMode) {
                // Switch to Upload Mode
                isCameraMode = false;
                fabCameraToggleBtn.innerHTML = '<i class="fa-solid fa-camera"></i>';
                transitionTo(cameraZone, dropZone);
                stopCamera();
            } else {
                // Switch to Camera Mode
                isCameraMode = true;
                fabCameraToggleBtn.innerHTML = '<i class="fa-solid fa-cloud-arrow-up"></i>';
                transitionTo(dropZone, cameraZone);
                startCamera();
            }
        });
    }

    async function startCamera() {
        try {
            cameraMediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' }
            });
            cameraStream.srcObject = cameraMediaStream;

            if (brightnessSlider) {
                brightnessSlider.value = 1;
                cameraStream.style.filter = 'brightness(1)';
            }
        } catch (err) {
            console.error("Error accessing camera:", err);
            alert("Unable to access camera. Please make sure permissions are granted.");
            if (isCameraMode) fabCameraToggleBtn.click();
        }
    }

    function stopCamera() {
        if (cameraMediaStream) {
            cameraMediaStream.getTracks().forEach(track => track.stop());
            cameraMediaStream = null;
        }
    }

    captureBtn.addEventListener('click', () => {
        if (!cameraMediaStream) return;

        cameraCanvas.width = cameraStream.videoWidth;
        cameraCanvas.height = cameraStream.videoHeight;

        const ctx = cameraCanvas.getContext('2d');

        ctx.drawImage(cameraStream, 0, 0, cameraCanvas.width, cameraCanvas.height);

        const brightness = brightnessSlider ? parseFloat(brightnessSlider.value) : 1;
        if (brightness !== 1) {
            const imageData = ctx.getImageData(0, 0, cameraCanvas.width, cameraCanvas.height);
            const data = imageData.data;
            for (let i = 0; i < data.length; i += 4) {
                data[i]     = Math.min(255, data[i] * brightness);
                data[i + 1] = Math.min(255, data[i + 1] * brightness);
                data[i + 2] = Math.min(255, data[i + 2] * brightness);
            }
            ctx.putImageData(imageData, 0, 0);
        }

        cameraCanvas.toBlob((blob) => {
            if (!blob) return;
            const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
            stopCamera();
            cameraZone.classList.add('hidden');
            handleFile(file);
        }, 'image/jpeg', 0.95);
    });

    if (brightnessSlider) {
        brightnessSlider.addEventListener('input', (e) => {
            if (cameraStream) {
                cameraStream.style.filter = `brightness(${e.target.value})`;
            }
        });
    }

    function handleFile(file) {
        hideErrorBanner();
        if (!file.type.match('image.*')) {
            showErrorBanner('Harap unggah file gambar yang valid (JPEG/PNG).', 'noise');
            return;
        }

        const MAX_FILE_SIZE = 16 * 1024 * 1024;
        if (file.size > MAX_FILE_SIZE) {
            const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
            showErrorBanner(`Ukuran foto terlalu besar (${sizeMB} MB). Maksimal ukuran file adalah 16 MB. Harap gunakan foto dengan ukuran yang lebih kecil.`, 'noise');
            return;
        }

        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {

            imagePreview.onload = () => {
                if (cropper) {
                    try { cropper.destroy(); } catch (err) {}
                }
                cropper = new Cropper(imagePreview, {
                    viewMode: 1,
                    dragMode: 'move',
                    autoCropArea: 0.8,
                    background: false,
                    responsive: true,
                    guides: true,
                    center: true,
                    highlight: true,
                    zoomable: true,
                    minContainerHeight: 300,
                    ready() {
                        attachTopRotateHandle(this.cropper);
                    },
                    crop() {
                        attachTopRotateHandle(this.cropper);
                    }
                });
            };

            imagePreview.src = e.target.result;

            const toHide = dropZone.classList.contains('hidden') ? cameraZone : dropZone;
            if (fabCameraToggleBtn) fabCameraToggleBtn.classList.add('hidden');
            transitionTo(toHide, previewArea);
        };
        reader.readAsDataURL(file);
    }

    function attachTopRotateHandle(cropperInstance) {
        if (!cropperInstance || !cropperInstance.cropBox) return;
        const cropBox = cropperInstance.cropBox;
        if (cropBox.querySelector('.cropper-top-rotate-wrapper')) return;

        const wrapper = document.createElement('div');
        wrapper.className = 'cropper-top-rotate-wrapper';
        wrapper.setAttribute('title', 'Rotasi Foto (Klik untuk +15°, atau Drag untuk Memutar)');
        wrapper.innerHTML = `
            <div class="cropper-top-rotate-handle">
                <i class="fa-solid fa-arrow-rotate-right"></i>
            </div>
            <div class="cropper-top-rotate-line"></div>
        `;

        let isDragging = false;
        let startAngle = 0;
        let hasDragged = false;

        wrapper.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            e.preventDefault();
            isDragging = true;
            hasDragged = false;

            const rect = cropBox.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            startAngle = Math.atan2(e.clientY - centerY, e.clientX - centerX) * (180 / Math.PI);

            const onMouseMove = (moveEvt) => {
                if (!isDragging) return;
                hasDragged = true;
                const currentRect = cropBox.getBoundingClientRect();
                const cX = currentRect.left + currentRect.width / 2;
                const cY = currentRect.top + currentRect.height / 2;
                const currentAngle = Math.atan2(moveEvt.clientY - cY, moveEvt.clientX - cX) * (180 / Math.PI);
                let diff = currentAngle - startAngle;

                if (Math.abs(diff) >= 3) {
                    cropperInstance.rotate(Math.round(diff));
                    startAngle = currentAngle;
                }
            };

            const onMouseUp = () => {
                isDragging = false;
                document.removeEventListener('mousemove', onMouseMove);
                document.removeEventListener('mouseup', onMouseUp);
            };

            document.addEventListener('mousemove', onMouseMove);
            document.addEventListener('mouseup', onMouseUp);
        });

        wrapper.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();
            if (!hasDragged) {
                cropperInstance.rotate(15);
            }
        });

        wrapper.addEventListener('touchstart', (e) => {
            e.stopPropagation();
            if (e.touches.length !== 1) return;
            isDragging = true;
            hasDragged = false;
            const touch = e.touches[0];
            const rect = cropBox.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            startAngle = Math.atan2(touch.clientY - centerY, touch.clientX - centerX) * (180 / Math.PI);

            const onTouchMove = (moveEvt) => {
                if (!isDragging || moveEvt.touches.length !== 1) return;
                hasDragged = true;
                const t = moveEvt.touches[0];
                const currentRect = cropBox.getBoundingClientRect();
                const cX = currentRect.left + currentRect.width / 2;
                const cY = currentRect.top + currentRect.height / 2;
                const currentAngle = Math.atan2(t.clientY - cY, t.clientX - cX) * (180 / Math.PI);
                let diff = currentAngle - startAngle;

                if (Math.abs(diff) >= 3) {
                    cropperInstance.rotate(Math.round(diff));
                    startAngle = currentAngle;
                }
            };

            const onTouchEnd = () => {
                isDragging = false;
                document.removeEventListener('touchmove', onTouchMove);
                document.removeEventListener('touchend', onTouchEnd);
            };

            document.addEventListener('touchmove', onTouchMove, { passive: false });
            document.addEventListener('touchend', onTouchEnd);
        }, { passive: false });

        cropBox.appendChild(wrapper);
    }

    if (closeErrorBtn) {
        closeErrorBtn.addEventListener('click', hideErrorBanner);
    }

    const rotateLeftBtn = document.getElementById('rotateLeftBtn');
    const rotateRightBtn = document.getElementById('rotateRightBtn');
    const flipHBtn = document.getElementById('flipHBtn');
    const flipVBtn = document.getElementById('flipVBtn');
    const resetCropBtn = document.getElementById('resetCropBtn');

    let flipHState = 1;
    let flipVState = 1;

    if (rotateLeftBtn) {
        rotateLeftBtn.addEventListener('click', () => {
            if (cropper) {
                const icon = rotateLeftBtn.querySelector('i');
                if (icon) {
                    icon.style.transition = 'transform 0.35s ease';
                    icon.style.transform = 'rotate(-90deg)';
                    setTimeout(() => { icon.style.transform = ''; }, 350);
                }
                cropper.rotate(-90);
            }
        });
    }
    if (rotateRightBtn) {
        rotateRightBtn.addEventListener('click', () => {
            if (cropper) {
                const icon = rotateRightBtn.querySelector('i');
                if (icon) {
                    icon.style.transition = 'transform 0.35s ease';
                    icon.style.transform = 'rotate(90deg)';
                    setTimeout(() => { icon.style.transform = ''; }, 350);
                }
                cropper.rotate(90);
            }
        });
    }
    if (flipHBtn) {
        flipHBtn.addEventListener('click', () => {
            if (cropper) {
                flipHState = -flipHState;
                cropper.scaleX(flipHState);
            }
        });
    }
    if (flipVBtn) {
        flipVBtn.addEventListener('click', () => {
            if (cropper) {
                flipVState = -flipVState;
                cropper.scaleY(flipVState);
            }
        });
    }
    if (resetCropBtn) {
        resetCropBtn.addEventListener('click', () => {
            if (cropper) {
                flipHState = 1;
                flipVState = 1;
                cropper.reset();
            }
        });
    }

    removeBtn.addEventListener('click', () => {
        hideErrorBanner();
        currentFile = null;
        fileInput.value = '';

        if (fabCameraToggleBtn) fabCameraToggleBtn.classList.remove('hidden');

        const toShow = isCameraMode ? cameraZone : dropZone;
        transitionTo(previewArea, toShow);

        const cropperToDestroy = cropper;
        cropper = null;
        setTimeout(() => {
            if (cropperToDestroy) {
                try { cropperToDestroy.destroy(); } catch (e) {}
            }
            if (imagePreview) imagePreview.src = '';
        }, 280);

        if (isCameraMode) {
            startCamera();
        }
    });

    analyzeBtn.addEventListener('click', () => {
        if (!currentFile || !cropper) return;

        if (errorBanner) errorBanner.classList.add('hidden');

        const mainInfoSection = document.getElementById('mainInfoSection');
        const institutionLogos = document.getElementById('institutionLogos');
        transitionTo([uploadPanel, mainInfoSection], loadingSection);

        cropper.getCroppedCanvas({
            maxWidth: 1024,
            maxHeight: 1024
        }).toBlob(async (blob) => {
            const formData = new FormData();

            formData.append('file', blob, currentFile.name);

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Server error: ${response.status}`);
                }

            const data = await response.json();

            if (data.error) {
                transitionTo(loadingSection, [uploadPanel, previewArea], true);
                showErrorBanner(data.error, data.error_type);
                return;
            }

            populateResults(data);

            transitionTo(loadingSection, resultsSection);
            } catch (error) {
                console.error(error);
                alert("Error analyzing image: " + error.message);
                transitionTo(loadingSection, uploadPanel);
            }
        }, 'image/jpeg', 0.95);
    });

    function populateResults(data) {

        resultImageOriginal.src = data.images.original;
        resultImageGradcam.src = data.images.gradcam;

        const diseaseName = document.getElementById('diseaseName');
        const diseaseConfidence = document.getElementById('diseaseConfidence');
        const diseaseConfidenceBar = document.getElementById('diseaseConfidenceBar');
        const statusBanner = document.getElementById('statusBanner');
        const statusIcon = document.getElementById('statusIcon');

        const t = (typeof translations !== 'undefined') ? translations[currentAppLang] : null;
        const diseaseCatKey = 'cat_' + data.disease.name.toLowerCase().replace(/ /g, '_');
        const translatedDiseaseName = t && t[diseaseCatKey] ? t[diseaseCatKey] : data.disease.name;

        diseaseName.textContent = translatedDiseaseName;
        diseaseConfidence.textContent = `${data.disease.confidence}% Confidence`;

        setTimeout(() => {
            diseaseConfidenceBar.style.width = `${data.disease.confidence}%`;
        }, 100);

        if (data.disease.status === 'sakit') {
            statusBanner.classList.add('sakit');
            statusIcon.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        } else {
            statusBanner.classList.remove('sakit');
            statusIcon.innerHTML = '<i class="fa-solid fa-check-circle"></i>';
        }

        const topPredictions = document.getElementById('topPredictions');
        topPredictions.innerHTML = '';
        data.disease.top3.forEach((pred, index) => {
            if (index === 0) return;

            const predCatKey = 'cat_' + pred.nama.toLowerCase().replace(/ /g, '_');
            const translatedPredName = t && t[predCatKey] ? t[predCatKey] : pred.nama;

            const div = document.createElement('div');
            div.className = 'prediction-item';
            div.innerHTML = `<span class="pred-name">${translatedPredName}</span><span class="pred-conf">${pred.confidence}%</span>`;
            topPredictions.appendChild(div);
        });

        document.getElementById('speciesName').textContent = data.species.name;
        document.getElementById('speciesConfidence').textContent = `${data.species.confidence}% Match`;

        if (data.knowledge && data.knowledge.length > 0) {
            currentKnowledge = data.knowledge;
        } else {
            currentKnowledge = [];
        }
        if (knowledgeTitleText) {
            knowledgeTitleText.textContent = t ? t.kg_treatment_info : 'Informasi Penanganan';
        }
        renderKnowledge();

        btnOriginal.click();

        saveHistory(data);
    }

    btnOriginal.addEventListener('click', () => {
        btnOriginal.classList.add('active');
        btnGradCam.classList.remove('active');
        resultImageOriginal.classList.add('active');
        resultImageGradcam.classList.remove('active');
    });

    btnGradCam.addEventListener('click', () => {
        btnGradCam.classList.add('active');
        btnOriginal.classList.remove('active');
        resultImageGradcam.classList.add('active');
        resultImageOriginal.classList.remove('active');
    });

    function resetToHome(instant = false) {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
        currentFile = null;
        fileInput.value = '';

        if (fabCameraToggleBtn) fabCameraToggleBtn.classList.remove('hidden');

        const toShow = isCameraMode ? cameraZone : dropZone;
        const mainInfoSection = document.getElementById('mainInfoSection');

        if (instant) {
            [previewArea, resultsSection, knowledgeSection].forEach(el => {
                if(el) { el.classList.add('hidden'); el.style.animation = ''; }
            });
            [uploadPanel, toShow, mainInfoSection].forEach(el => {
                if(el) { el.classList.remove('hidden'); el.style.animation = ''; }
            });
        } else {
            transitionTo([previewArea, resultsSection, knowledgeSection], [uploadPanel, toShow, mainInfoSection]);
        }

        const diseaseConfidenceBar = document.getElementById('diseaseConfidenceBar');
        if (diseaseConfidenceBar) diseaseConfidenceBar.style.width = '0%';

        renderHistory();

        if (isCameraMode) {
            startCamera();
        }
    }

    newAnalysisBtn.addEventListener('click', () => resetToHome(false));

    if (retryCropBtn) {
        retryCropBtn.addEventListener('click', () => {
            if (fabCameraToggleBtn) fabCameraToggleBtn.classList.add('hidden');
            transitionTo(resultsSection, [uploadPanel, previewArea]);
        });
    }

    if (logoHome) {
        logoHome.addEventListener('click', () => {

            if (!homePage.classList.contains('active-page')) {
                navHomeBtn.click();
            }
            resetToHome();
        });
    }

    const navSpeciesBtn = document.getElementById('navSpeciesBtn');
    const speciesInfoPage = document.getElementById('speciesInfoPage');
    const allNavBtns = [navHomeBtn, navDiseaseBtn, navSpeciesBtn];
    const allPages = [homePage, diseaseInfoPage, speciesInfoPage];

    function switchToPage(activeBtn, activePage) {

        allNavBtns.forEach(btn => { if(btn) btn.classList.remove('active'); });
        if(activeBtn) activeBtn.classList.add('active');

        if (activePage !== homePage) stopCamera();

        if (activePage === homePage) {
            resetToHome(true);
            if (fabCameraToggleBtn) fabCameraToggleBtn.classList.remove('hidden');
        } else {
            if (fabCameraToggleBtn) fabCameraToggleBtn.classList.add('hidden');
            transitionTo([uploadPanel, previewArea, loadingSection, resultsSection, knowledgeSection, historySection], []);
        }

        allPages.forEach(page => {
            if (page) {
                page.classList.add('hidden');
                page.classList.remove('active-page');
            }
        });

        if (activePage) {
            activePage.classList.remove('hidden');
            setTimeout(() => activePage.classList.add('active-page'), 10);
        }
    }

    if (navHomeBtn) {
        navHomeBtn.addEventListener('click', () => switchToPage(navHomeBtn, homePage));
    }
    if (navDiseaseBtn) {
        navDiseaseBtn.addEventListener('click', () => switchToPage(navDiseaseBtn, diseaseInfoPage));
    }
    if (navSpeciesBtn) {
        navSpeciesBtn.addEventListener('click', () => switchToPage(navSpeciesBtn, speciesInfoPage));
    }

    document.addEventListener('languageChanged', (e) => {

        if (currentKnowledge && currentKnowledge.length > 0) {
            renderKnowledge();
        }

        if (errorBanner && !errorBanner.classList.contains('hidden')) {
            const currentTitle = errorTitle ? errorTitle.textContent : '';
            const t = translations[e.detail.lang];

            if (currentTitle.includes('AI') || currentTitle.includes('Keamanan') || currentTitle.includes('Security')) {

                const currentMsg = errorMessage.textContent;
                if (currentMsg.includes('kecil') || currentMsg.includes('small')) {
                    errorMessage.textContent = t.error_msg_noise_small;
                } else if (currentMsg.includes('buram') || currentMsg.includes('blur')) {
                    errorMessage.textContent = t.error_msg_noise_blur;
                } else {
                    errorMessage.textContent = t.error_msg_noise_ood;
                }
                if (errorTitle) errorTitle.textContent = t.error_title_noise;
            } else {

                errorMessage.textContent = t.error_msg_conf;
                if (errorTitle) errorTitle.textContent = t.error_title_conf;
            }
        }

        const diseaseNameEl = document.getElementById('diseaseName');
        if (diseaseNameEl && diseaseNameEl.textContent) {
            const rawName = diseaseNameEl.textContent;

        }
    });

});
