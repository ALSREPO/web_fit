<!-- Crear el Layout Base -->

<script>
  import '../app.css';
  import BottomNav from '$lib/components/layout/BottomNav.svelte';

  /** @type {{ children?: import('svelte').Snippet }} */
  let { children } = $props();

</script>

<div class="min-h-screen pb-20 bg-slate-900 text-slate-100 flex flex-col">
  <!-- Cabecera Superior Minimalista -->
  <header class="p-4 border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10 flex justify-between items-center">
    <a href="/" class="flex items-center gap-2 group transition-opacity hover:opacity-90">
      <!-- Icono SVG de Barra Olímpica Sólida -->
      <svg class="h-6 w-6 text-blue-500 transition-transform group-hover:scale-110" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M3 10v4m2-5v6m2-7v8m10-8v8m2-7v6m2-5v4M7 12h10" />
      </svg>
      
      <h1 class="font-bold text-lg text-slate-100 group-hover:text-blue-400 transition-colors">
        Diario de Hierro
      </h1>
    </a>

    <span class="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded-full border border-slate-700 font-mono">
      ALS
    </span>
  </header>

  <!-- Contenido Principal -->
  <main class="flex-1 p-4 max-w-md mx-auto w-full">
    {@render children?.()}
  </main>

  <!-- Navegación Inferior -->
  <BottomNav />
</div>