<script>
	import { page } from '$app/state';

	let ejercicio = $derived(decodeURIComponent(page.params.ejercicio || ''));
</script>

<div class="space-y-3">
	<button
		type="button"
		onclick={() => history.back()}
		class="text-xs font-medium text-blue-400 hover:text-blue-300"
	>
		← Volver
	</button>
	<h2 class="text-xl font-bold text-white">{ejercicio || 'Histórico'}</h2>
	<p class="rounded-xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-400">
		El histórico de cada ejercicio se implementará en el Módulo 5.
	</p>
</div>
