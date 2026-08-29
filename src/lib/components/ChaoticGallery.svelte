<script>
  import { onMount } from 'svelte';
  
  // Generate chaotic grid items with pre-calculated heights
  let items = [
    { id: 1, span: 'col-span-12 md:col-span-6 lg:col-span-4', heightClass: 'h-[400px]', heightVal: 400, src: '/images/misty-forest.jpg', title: 'Morning Mist', delay: 0 },
    { id: 2, span: 'col-span-12 md:col-span-6 lg:col-span-8', heightClass: 'h-[400px]', heightVal: 400, src: '/images/mountain-peak.jpg', title: 'High Altitude', delay: 100 },
    { id: 3, span: 'col-span-12 md:col-span-4 lg:col-span-3', heightClass: 'h-[600px]', heightVal: 600, src: '/images/lake-reflection.jpg', title: 'Mirror', delay: 200 },
    { id: 4, span: 'col-span-12 md:col-span-8 lg:col-span-6', heightClass: 'h-[600px]', heightVal: 600, src: '/images/rock-texture.jpg', title: 'Stone Skin', delay: 300 },
    { id: 5, span: 'col-span-12 md:col-span-12 lg:col-span-3', heightClass: 'h-[300px] lg:h-[600px]', heightVal: 600, src: '/images/fern-leaf.jpg', title: 'Details', delay: 400 },
    { id: 6, span: 'col-span-12 md:col-span-6 lg:col-span-5', heightClass: 'h-[500px]', heightVal: 500, src: '/images/stormy-ocean.jpg', title: 'Turbulence', delay: 150 },
    { id: 7, span: 'col-span-12 md:col-span-6 lg:col-span-7', heightClass: 'h-[500px]', heightVal: 500, src: '/images/sand-dunes.jpg', title: 'Golden Hour', delay: 250 },
    { id: 8, span: 'col-span-12 md:col-span-12 lg:col-span-12', heightClass: 'h-[700px]', heightVal: 700, src: '/images/starry-night.jpg', title: 'Cosmos', delay: 350 },
  ];

  // Intersection Observer Action
  function viewport(element) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          element.classList.add('is-visible');
          observer.unobserve(element);
        }
      });
    }, { threshold: 0.1 });

    observer.observe(element);

    return {
      destroy() {
        observer.disconnect();
      }
    };
  }
</script>

<section class="w-full px-4 md:px-12 py-24">
  <div class="grid grid-cols-12 gap-0 border-t border-l border-border">
    {#each items as item}
      <div 
        class="{item.span} relative group border-r border-b border-border overflow-hidden bg-secondary/10 transition-colors hover:bg-secondary/30"
        use:viewport
      >
        <div class="opacity-0 translate-y-8 transition-all duration-1000 ease-out group-[.is-visible]:opacity-100 group-[.is-visible]:translate-y-0 w-full h-full p-4 md:p-8 flex flex-col">
          
          <!-- Image Container -->
          <div class="relative w-full {item.heightClass} overflow-hidden mb-4">
            <img 
              src={item.src || "/placeholder.svg"}
              alt={item.title}
              class="w-full h-full object-cover transition-transform duration-[1.5s] ease-in-out group-hover:scale-105 grayscale hover:grayscale-0"
            />
            
            <!-- Overlay Lines -->
            <div class="absolute inset-0 border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"></div>
          </div>

          <!-- Content -->
          <div class="mt-auto flex justify-between items-end">
            <div>
              <span class="text-[10px] uppercase tracking-widest text-muted-foreground block mb-1">0{item.id}</span>
              <h3 class="font-serif text-2xl md:text-3xl italic">{item.title}</h3>
            </div>
            <div class="w-8 h-[1px] bg-primary/50 group-hover:w-16 transition-all duration-300"></div>
          </div>
          
        </div>
      </div>
    {/each}
  </div>
  
  <!-- "Chaotic" decorative lines -->
  <div class="relative w-full h-24 mt-12 overflow-hidden">
    <div class="absolute top-1/2 left-0 w-full h-[1px] bg-border"></div>
    <div class="absolute top-0 left-1/4 w-[1px] h-full bg-border rotate-12 origin-top"></div>
    <div class="absolute top-0 right-1/3 w-[1px] h-full bg-border -rotate-6 origin-bottom"></div>
  </div>
</section>

<style>
  /* Custom utility for the viewport action */
  :global(.is-visible) {
    /* This class is added by the action */
  }
</style>
