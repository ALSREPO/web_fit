<!-- frontend/src/lib/components/dashboard/WorkoutCard.svelte 
    contiene la estructura base para los widgets de Próximo Entrenamiento y Último Entrenamiento
-->
<script lang="ts">
	interface ExerciseItem {
		ejercicio: string;
		detalle: string;
	}

	interface SessionItem {
		tipo_ejercicio: string;
		ejercicios: ExerciseItem[];
	}

	interface WorkoutCardData {
		has_workout: boolean;
		fecha?: string;
		date_label?: string;
		sessions: SessionItem[];
	}

	interface Props {
		title?: string;
		cardData?: WorkoutCardData | null;
		dateColorClass?: string;
		loading?: boolean;
	}

	let {
		title = '',
		cardData = null,
		dateColorClass = 'text-emerald-400',
		loading = false
	}: Props = $props();
</script>

<section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md">
	<p class="mb-1 text-xs font-medium text-slate-400">{title}</p>

	{#if loading}
		<div class="mt-2 space-y-3 animate-pulse">
			<div class="h-5 w-1/2 rounded bg-slate-700"></div>
			<div class="h-6 w-3/4 rounded bg-slate-700"></div>
			<div class="h-16 w-full rounded bg-slate-700"></div>
		</div>
	{:else if cardData && cardData.has_workout}
		{#if cardData.fecha}
			<a href="/detalle/{cardData.fecha}" class="block">
				<h3 class="text-lg font-bold {dateColorClass}">{cardData.date_label}</h3>
			</a>
		{:else}
			<h3 class="text-lg font-bold {dateColorClass}">{cardData.date_label}</h3>
		{/if}

		<div class="mt-3 space-y-4">
			{#each cardData.sessions as session}
				<div>
					<p class="text-base font-semibold text-slate-100">{session.tipo_ejercicio}</p>

					{#if session.ejercicios && session.ejercicios.length > 0}
						<ul class="mt-2 space-y-2.5 pl-2 text-sm text-slate-300">
							{#each session.ejercicios as item}
								<li class="flex items-start gap-2.5">
									<span class="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500"></span>
									<div class="flex flex-col">
										<a
											href="/historico/{encodeURIComponent(item.ejercicio)}"
											class="font-medium text-slate-200 hover:text-blue-300"
										>
											{item.ejercicio}
										</a>
										<span class="font-mono text-xs text-slate-400">{item.detalle}</span>
									</div>
								</li>
							{/each}
						</ul>
					{/if}
				</div>
			{/each}
		</div>

		{#if cardData.fecha}
			<div class="mt-4 text-right">
				<a href="/detalle/{cardData.fecha}" class="text-xs font-medium text-blue-400 hover:text-blue-300">
					Ver detalle →
				</a>
			</div>
		{/if}
	{:else}
		<p class="mt-2 text-sm text-slate-400">No hay nada programado</p>
	{/if}
</section>