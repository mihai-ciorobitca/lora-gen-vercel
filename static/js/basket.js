
document.addEventListener('DOMContentLoaded', () => {
    const imageList = document.getElementById('new-image-list');
    const uploadInput = document.getElementById('upload-input');
    const saveBtn = document.getElementById('save-btn');
    const deleteBtn = document.getElementById('delete-btn');

    // Preview selected images
    uploadInput.addEventListener('change', () => {
        imageList.innerHTML = '';
        const files = Array.from(uploadInput.files);
        files.forEach(file => {
            const reader = new FileReader();
            reader.onload = e => {
                const label = document.createElement('label');
                label.className = 'image-label relative cursor-pointer';
                label.innerHTML = `
                            <input type="checkbox" name="delete_images" class="peer hidden">
                            <img src="${e.target.result}" alt="New Image"
                                class="w-full h-48 object-cover rounded-lg border border-gray-300 dark:border-gray-600">
                            <div class="image-overlay absolute inset-0 bg-black/40 opacity-0 peer-checked:opacity-100 transition-all rounded-lg"></div>
                        `;
                imageList.appendChild(label);
            };
            reader.readAsDataURL(file);
        });

        saveBtn.disabled = files.length === 0;
        saveBtn.classList.toggle('opacity-50', files.length === 0);
        saveBtn.classList.toggle('cursor-not-allowed', files.length === 0);
    });

    // Mobile sidebar toggle
    const sidebar = document.getElementById('mobile-sidebar');
    const overlay = document.getElementById('overlay');
    const openBtn = document.getElementById('open-sidebar');
    const closeBtn = document.getElementById('close-sidebar');

    openBtn.addEventListener('click', () => { sidebar.classList.remove('-translate-x-full'); overlay.classList.remove('hidden'); });
    closeBtn.addEventListener('click', () => { sidebar.classList.add('-translate-x-full'); overlay.classList.add('hidden'); });
    overlay.addEventListener('click', () => { sidebar.classList.add('-translate-x-full'); overlay.classList.add('hidden'); });

    // Dark mode toggle
    const darkToggle = document.querySelectorAll('#dark-toggle, #dark-toggle-mobile');
    darkToggle.forEach(btn => {
        btn.addEventListener('click', () => {
            document.documentElement.classList.toggle('dark');
            const icon = btn.querySelector('i');
            if (document.documentElement.classList.contains('dark')) icon.classList.replace('fa-sun', 'fa-moon');
            else icon.classList.replace('fa-moon', 'fa-sun');
        });
    });

    const uploadedImageList = document.getElementById('image-list');
    uploadedImageList.addEventListener('change', () => {
        const checked = uploadedImageList.querySelectorAll('input[type="checkbox"]:checked').length > 0;
        deleteBtn.disabled = !checked;
        deleteBtn.classList.toggle('opacity-50', !checked);
        deleteBtn.classList.toggle('cursor-not-allowed', !checked);
    });

});