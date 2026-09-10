<script>
	import { page } from '$app/state';
	import { dashboardApi } from '$lib/services';
	import MuscleMap from '$lib/components/detalle/MuscleMap.svelte';
	import ExerciseBreakdown from '$lib/components/detalle/ExerciseBreakdown.svelte';

	let loading = $state(true);
	let error = $state(null);
	let detail = $state(null);

	let fecha = $derived(page.params.fecha);

	$effect(() => {
		const currentFecha = fecha;
		if (!currentFecha) return;

		loading = true;
		error = null;

		dashboardApi
			.getDayDetail(currentFecha)
			.then((res) => {
				detail = res;
			})
			.catch((e) => {
				error = e.message || 'No se pudo cargar el detalle del día';
				detail = null;
			})
			.finally(() => {
				loading = false;
			});
	});

	function formatVolume(kg) {
		if (!kg) return '0 kg';
		return `${Math.round(kg).toLocaleString('es-ES')} kg`;
	}
</script>

<div class="space-y-4">
	<a href="/calendario" class="inline-flex items-center text-xs font-medium text-blue-400 hover:text-blue-300">
		← Calendario
	</a>

	{#if loading}
		<div class="space-y-3 animate-pulse">
			<div class="h-8 w-2/3 rounded bg-slate-800"></div>
			<div class="h-20 w-full rounded-2xl bg-slate-800"></div>
			<div class="h-64 w-full rounded-2xl bg-slate-800"></div>
		</div>
	{:else if error}
		<p class="rounded-xl border border-rose-900/60 bg-rose-950/40 p-4 text-sm text-rose-300">{error}</p>
	{:else if detail}
		<header class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
			<p class="text-xs font-medium text-slate-400">Detalle del día</p>
			<h2 class="mt-1 text-xl font-bold text-white">{detail.date_label || fecha}</h2>

			{#if detail.has_workout}
				<div class="mt-4 grid grid-cols-3 gap-2 text-center">
					<div class="rounded-xl bg-slate-900/70 px-2 py-3">
						<p class="text-[10px] uppercase tracking-wide text-slate-500">Duración</p>
						<p class="mt-1 text-sm font-semibold text-slate-100">{detail.duration_label || '—'}</p>
					</div>
					<div class="rounded-xl bg-slate-900/70 px-2 py-3">
						<p class="text-[10px] uppercase tracking-wide text-slate-500">Volumen</p>
						<p class="mt-1 text-sm font-semibold text-slate-100">{formatVolume(detail.total_volume_kg)}</p>
					</div>
					<div class="rounded-xl bg-slate-900/70 px-2 py-3">
						<p class="text-[10px] uppercase tracking-wide text-slate-500">Distancia</p>
						<p class="mt-1 text-sm font-semibold text-slate-100">
							{detail.total_distance_km ? `${detail.total_distance_km} km` : '—'}
						</p>
					</div>
				</div>
			{:else}
				<p class="mt-3 text-sm text-slate-400">Día de descanso. No hay sesión registrada.</p>
			{/if}
		</header>

		{#if detail.has_workout}
			<ExerciseBreakdown sessions={detail.sessions} />
			<MuscleMap muscles={detail.muscles} />
		{/if}
	{/if}
</div>
