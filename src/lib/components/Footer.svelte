<script>
  const year = new Date().getFullYear();

  function scrollToTop(event) {
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
</script>

<footer class="w-full px-4 md:px-12 py-12 border-t border-border bg-background">
  <div class="grid grid-cols-1 md:grid-cols-12 gap-8">
    <div class="col-span-1 md:col-span-4">
      <h2 class="font-serif text-4xl mb-4">Let's Create</h2>
      <p class="text-muted-foreground max-w-xs">
        Available for commissions worldwide. Specializing in landscape, architectural, and fine art photography.
      </p>
    </div>
    
    <div class="col-span-1 md:col-span-4 md:col-start-6 flex flex-col gap-2">
      <span class="text-xs uppercase tracking-widest text-muted-foreground mb-2">Contact</span>
      <a href="mailto:hello@example.com" class="text-lg hover:italic transition-all">hello@example.com</a>
      <a href="tel:+1234567890" class="text-lg hover:italic transition-all">+1 (555) 000-0000</a>
    </div>
    
    <div class="col-span-1 md:col-span-2 md:col-start-11 flex flex-col gap-2">
      <span class="text-xs uppercase tracking-widest text-muted-foreground mb-2">Social</span>
      <a href="https://www.instagram.com" class="hover:underline">Instagram</a>
      <a href="https://www.twitter.com" class="hover:underline">Twitter</a>
      <a href="https://www.behance.net" class="hover:underline">Behance</a>
    </div>
  </div>
  
  <div class="mt-24 flex justify-between items-end">
    <span class="text-[10vw] font-serif leading-none opacity-5 select-none pointer-events-none">STUDIO</span>
    <div class="flex flex-col items-end gap-4">
      <button 
        onclick={scrollToTop}
        class="text-xs uppercase tracking-widest hover:text-primary transition-colors cursor-pointer"
        type="button"
      >
        Back to Top ↑
      </button>
      <p class="text-xs text-muted-foreground">© {year} All rights reserved.</p>
    </div>
  </div>
</footer>
