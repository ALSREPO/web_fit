<!-- frontend/src/lib/components/detalle/ExerciseBreakdown.svelte -->
<script>
    let { sessions = [] } = $props();

    function formatVolume(kg) {
        if (!kg) return null;
        return `${Math.round(kg).toLocaleString('es-ES')} kg`;
    }

    // Comprobamos si el ejercicio es de cardio o resistencia
    function isCardio(name) {
        if (!name) return false;
        const normalized = name.toLowerCase();
        return normalized.includes('natación') || 
               normalized.includes('natacion') || 
               normalized.includes('ciclismo') || 
               normalized.includes('correr') || 
               normalized.includes('running');
    }

    // Calcula el volumen total de un ejercicio de manera dinámica
    function getExerciseVolume(exercise) {
        if (isCardio(exercise.ejercicio)) return null;
        if (!exercise.sets || exercise.sets.length === 0) return null;

        // Suma el peso de cada serie multiplicado por sus repeticiones
        const volume = exercise.sets.reduce((sum, set) => {
            // Buscamos un número seguido de 'kg' o intentamos extraer el peso
            // Generalmente en "set.detalle" suele venir algo como "10 kg x 12" o "10kg x 12"
            // También se intenta leer si el backend proporciona el dato en set.weight, 
            // sino, lo extraemos del detalle para que sea robusto.
            let weight = set.weight;
            let reps = set.reps;

            if (weight === undefined || reps === undefined) {
                // Intentamos parsear del detalle si no viene desglosado (e.g. "10 kg x 12" -> weight=10, reps=12)
                const match = set.detalle?.toLowerCase().match(/(\d+(?:\.\d+)?)\s*kg\s*x\s*(\d+)/);
                if (match) {
                    weight = parseFloat(match[1]);
                    reps = parseInt(match[2], 10);
                }
            }

            if (weight && reps) {
                return sum + (weight * reps);
            }
            return sum;
        }, 0);

        return volume > 0 ? volume : null;
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
                                    class="block animate-fade-in"
                                >
                                    <div class="flex items-start justify-between gap-2">
                                        <div>
                                            <p class="font-medium text-slate-100">{exercise.ejercicio}</p>
                                            
                                            <!-- Se ha quitado el ejercicio.summary (series en línea) -->
                                            <!-- En su lugar se muestra el volumen en kilos si no es cardio -->
                                            {#if !isCardio(exercise.ejercicio)}
                                                {@const vol = getExerciseVolume(exercise)}
                                                {#if vol}
                                                    <p class="mt-0.5 font-sans text-xs text-slate-400 font-semibold">Volumen: {formatVolume(vol)}</p>
                                                {/if}
                                            {/if}
                                        </div>
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