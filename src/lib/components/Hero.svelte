<script>
  import { onMount } from 'svelte';
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  let visible = $state(false);
  let scrollY = $state(0);

  onMount(() => {
    visible = true;
    
    const handleScroll = () => {
      scrollY = window.scrollY;
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });
</script>

<section class="relative min-h-screen w-full flex flex-col justify-center items-center overflow-hidden px-4 md:px-12 pt-24 pb-12">
  <!-- Background Parallax Element -->
  <div 
    class="absolute top-0 left-0 w-full h-full opacity-5 pointer-events-none z-0"
    style="transform: translateY({scrollY * 0.2}px)"
  >
    <div class="w-full h-full bg-[url('/placeholder.svg?height=1080&width=1920')] bg-cover bg-center grayscale"></div>
  </div>

  <div class="z-10 w-full max-w-[1800px] mx-auto grid grid-cols-1 md:grid-cols-12 gap-4 md:gap-8 items-center">
    {#if visible}
      <div 
        class="col-span-1 md:col-span-8 md:col-start-2"
        in:fly={{ y: 100, duration: 1500, easing: cubicOut }}
      >
        <h1 class="font-serif text-[12vw] md:text-[10vw] leading-[0.85] tracking-tighter text-primary mix-blend-difference">
          CAPTURING <br />
          <span class="italic font-light ml-[10vw] md:ml-[15vw]">THE SILENCE</span>
        </h1>
      </div>

      <div 
        class="col-span-1 md:col-span-3 md:col-start-9 mt-8 md:mt-0 flex flex-col gap-6"
        in:fly={{ y: 50, duration: 1500, delay: 400, easing: cubicOut }}
      >
        <p class="text-sm md:text-base font-light text-muted-foreground max-w-xs leading-relaxed">
          Photography is the art of freezing time. In the chaos of the natural world, we find a hidden order, a silent rhythm that speaks to the soul.
        </p>
        <div class="h-[1px] w-24 bg-primary/30"></div>
        <p class="text-xs uppercase tracking-widest text-primary/60">
          Est. 2024 — Portfolio
        </p>
      </div>
    {/if}
  </div>

  <!-- Scroll Indicator -->
  <div class="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 opacity-50 animate-pulse">
    <span class="text-[10px] uppercase tracking-widest">Scroll</span>
    <div class="w-[1px] h-12 bg-primary"></div>
  </div>
</section>
