<script>
	let { sessions = [] } = $props();

	function formatVolume(kg) {
		if (!kg) return null;
		return `${Math.round(kg).toLocaleString('es-ES')} kg`;
	}
</script>

<section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
	<h3 class="mb-3 text-base font-semibold text-white">Ejercicios realizados</h3>

	{#if !sessions || sessions.length === 0}
		<p class="text-sm text-slate-400">No hay ejercicios registrados este día.</p>
	{:else}
		<div class="space-y-5">
			{#each sessions as session}
				<div>
					<div class="mb-2 flex items-baseline justify-between gap-2">
						<p class="text-sm font-semibold text-slate-100">{session.tipo_ejercicio}</p>
						{#if session.total_volume_kg}
							<p class="text-xs text-slate-400">{formatVolume(session.total_volume_kg)}</p>
						{:else if session.total_distance_km}
							<p class="text-xs text-slate-400">{session.total_distance_km} km</p>
						{/if}
					</div>

					<ul class="space-y-3">
						{#each session.exercises as exercise}
							<li class="rounded-xl border border-slate-700/70 bg-slate-900/60 p-3">
								<a
									href="/historico/{encodeURIComponent(exercise.ejercicio)}"
									class="block"
								>
									<div class="flex items-start justify-between gap-2">
										<div>
											<p class="font-medium text-slate-100">{exercise.ejercicio}</p>
											{#if exercise.summary}
												<p class="mt-0.5 font-mono text-xs text-slate-400">{exercise.summary}</p>
											{/if}
										</div>
										<span class="shrink-0 text-xs text-blue-400">Histórico →</span>
									</div>
								</a>

								{#if exercise.sets?.length}
									<ol class="mt-3 space-y-1.5 border-t border-slate-800 pt-2">
										{#each exercise.sets as set}
											<li class="flex items-start justify-between gap-2 text-xs text-slate-300">
												<span class="w-8 shrink-0 font-semibold text-slate-500">S{set.set_number}</span>
												<span class="flex-1 font-mono">{set.detalle}</span>
												{#if set.comment}
													<span class="max-w-[40%] text-right text-slate-500">{set.comment}</span>
												{/if}
											</li>
										{/each}
									</ol>
								{/if}
							</li>
						{/each}
					</ul>
				</div>
			{/each}
		</div>
	{/if}
</section>
