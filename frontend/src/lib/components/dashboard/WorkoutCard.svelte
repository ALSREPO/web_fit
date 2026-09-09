<!-- frontend/src/lib/components/dashboard/WorkoutCard.svelte 
    contiene la estructura base para los widgets de Próximo Entrenamiento y Último Entrenamiento
-->
<!-- frontend/src/lib/components/dashboard/WorkoutCard.svelte -->
<script lang="ts">
	interface WorkoutCardData {
		has_workout: boolean;
		fecha?: string;
		date_label?: string;
		sessions: Array<{
			tipo_ejercicio: string;
			ejercicios: Array<{
				ejercicio: string;
				detalle: string;
			}>;
		}>;
	}

	interface Props {
		title?: string;
		cardData?: WorkoutCardData | null;
		badgeColor?: 'green' | 'red' | 'yellow';
	}

	let { title = '', cardData = null, badgeColor = 'green' }: Props = $props();

	const colorClasses = {
		green: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
		red: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
		yellow: 'bg-amber-500/15 text-amber-400 border-amber-500/30'
	};
</script>

<div class="rounded-xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-sm">
	<div class="mb-4 flex items-center justify-between border-b border-slate-800/80 pb-3">
		<h3 class="text-sm font-medium uppercase tracking-wider text-slate-400">{title}</h3>
		{#if cardData?.has_workout && cardData?.date_label}
			<span
				class="rounded-full border px-2.5 py-1 text-xs font-semibold shadow-xs transition-colors {colorClasses[badgeColor]}"
			>
				{cardData.date_label}
			</span>
		{/if}
	</div>

	{#if !cardData || !cardData.has_workout}
		<div class="py-6 text-center text-sm text-slate-500">
			No hay datos de entrenamiento disponibles.
		</div>
	{:else}
		<div class="space-y-4">
			{#each cardData.sessions as session}
				<div class="rounded-lg border border-slate-800/40 bg-slate-950/40 p-3.5">
					<div class="mb-2 flex items-center gap-2">
						<span class="h-2 w-2 rounded-full bg-slate-400"></span>
						<h4 class="text-xs font-bold uppercase tracking-wide text-slate-300">
							{session.tipo_ejercicio}
						</h4>
					</div>

					<ul class="space-y-1.5 pl-4 text-sm">
						{#each session.ejercicios as item}
							<li class="flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-0.5 sm:gap-2">
								<span class="font-medium text-slate-200">{item.ejercicio}:</span>
								<span class="font-mono text-xs text-slate-400">{item.detalle}</span>
							</li>
						{/each}
					</ul>
				</div>
			{/each}
		</div>
	{/if}
</div>