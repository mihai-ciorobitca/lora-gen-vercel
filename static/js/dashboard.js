const sidebar = document.getElementById('mobile-sidebar');
const overlay = document.getElementById('overlay');
const openBtn = document.getElementById('open-sidebar');
const closeBtn = document.getElementById('close-sidebar');

openBtn.addEventListener('click', () => {
    sidebar.classList.remove('-translate-x-full');
    overlay.classList.remove('hidden');
});

closeBtn.addEventListener('click', () => {
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
});

overlay.addEventListener('click', () => {
    sidebar.classList.add('-translate-x-full');
    overlay.classList.add('hidden');
});
const darkToggle = document.querySelectorAll('#dark-toggle, #dark-toggle-mobile');
darkToggle.forEach(btn => {
    btn.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        const icon = btn.querySelector('i');
        if (document.documentElement.classList.contains('dark')) {
            icon.classList.replace('fa-sun', 'fa-moon');
        } else {
            icon.classList.replace('fa-moon', 'fa-sun');
        }
    });
});