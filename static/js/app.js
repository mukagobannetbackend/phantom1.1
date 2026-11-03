const root=document.documentElement;const toggle=document.getElementById('theme-toggle');if(toggle){toggle.addEventListener('click',async()=>{const next=root.dataset.theme==='light'?'dark':'light';root.dataset.theme=next;try{await fetch('/settings/theme',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:`theme=${next}`})}catch(e){}})}document.querySelectorAll('input[type=file]').forEach(i=>i.addEventListener('change',()=>{if(i.files[0]&&i.files[0].size>12*1024*1024){alert('Image is larger than the 12 MB upload limit.')}}));
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("/static/service-worker.js")
            .catch((error) => {
                console.error("PhantomVault service worker registration failed:", error);
            });
    });
}