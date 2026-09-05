<!-- Navegación Inferior -->

<script>
  import { page } from '$app/state';

  const navItems = [
    { href: '/', label: 'Inicio', icon: '🏠' },
    { href: '/calendario', label: 'Calendario', icon: '📅' },
    { href: '/historico', label: 'Histórico', icon: '📈' }
  ];
</script>

<nav class="fixed bottom-0 left-0 right-0 bg-slate-900/95 border-t border-slate-800 backdrop-blur z-50">
  <div class="max-w-md mx-auto flex justify-around items-center h-16">
    {#each navItems as item}
      <a 
        href={item.href} 
        class="flex flex-col items-center justify-center w-full h-full text-xs transition-colors {page.url.pathname === item.href ? 'text-blue-500 font-semibold' : 'text-slate-400 hover:text-slate-200'}"
      >
        <span class="text-lg mb-0.5">{item.icon}</span>
        <span>{item.label}</span>
      </a>
    {/each}
  </div>
</nav>