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
    <h1 class="font-bold text-lg text-blue-500">🏋️ FitNotes Analytics</h1>
    <span class="text-xs bg-slate-800 text-slate-400 px-2 py-1 rounded-full border border-slate-700">PWA</span>
  </header>

  <!-- Contenido Principal -->
  <main class="flex-1 p-4 max-w-md mx-auto w-full">
    {@render children?.()}
  </main>

  <!-- Navegación Inferior -->
  <BottomNav />
</div>