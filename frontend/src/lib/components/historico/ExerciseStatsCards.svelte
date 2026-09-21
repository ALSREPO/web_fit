<!-- frontend/src/lib/components/historico/ExerciseStatsCards.svelte -->
<script lang="ts">
    interface CardioProjections {
        pace_label: string;
        best_pace?: number;
        target_1_label: string;
        target_1_time: string;
        target_2_label: string;
        target_2_time: string;
        target_3_label: string;
        target_3_time: string;
        target_4_label: string;
        target_4_time: string;
        target_5_label: string;
        target_5_time: string;
    }

    interface Stats {
        has_recent_data: boolean;
        is_cardio?: boolean;
        cardio_type?: string;
        // Fuerza
        max_weight?: number;
        reps_at_max?: number;
        weight_unit?: string;
        estimated_1rm?: number;
        // Cardio
        cardio_projections?: CardioProjections;
    }

    let { stats = null }: { stats: Stats | null } = $props();

    function estimateWeightForReps(oneRm: number | undefined, reps: number): number | null {
        if (!oneRm) return null;
        return Math.round(oneRm / (1 + reps / 30.0));
    }
</script>

{#if !stats}
    <div class="h-32 w-full animate-pulse rounded-2xl bg-slate-800/80"></div>
{:else if !stats.has_recent_data}
    <div class="rounded-2xl border border-amber-900/50 bg-amber-950/30 p-4 text-amber-200">
        <p class="text-xs font-semibold uppercase tracking-wider text-amber-400">Sin registros recientes</p>
        <p class="mt-1 text-sm text-slate-300">
            No has realizado este ejercicio en los últimos 3 meses.
        </p>
    </div>
{:else if stats.is_cardio && stats.cardio_projections}
    <!-- TARJETAS PARA CARDIO ADAPTADAS POR DISCIPLINA -->
    <div class="space-y-4">
        <!-- Bloque Superior: 2 Cajas -->
        <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Mejor Ritmo (3M)</span>
                <p class="mt-1 font-mono text-xl font-bold text-emerald-400">
                    {stats.cardio_projections.best_pace ?? 'N/A'} <span class="text-xs font-normal text-slate-300">{stats.cardio_projections.pace_label}</span>
                </p>
                <p class="mt-0.5 text-xs text-slate-400">Ritmo Medio</p>
            </div>

            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Estimado {stats.cardio_projections.target_1_label}</span>
                <p class="mt-1 font-mono text-xl font-bold text-blue-400">
                    {stats.cardio_projections.target_1_time}
                </p>
                <p class="mt-0.5 text-xs text-slate-400">Fórmula Riegel</p>
            </div>
        </div>

        <!-- Bloque Inferior: Resto de Distancias Clave -->
        <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md space-y-3">
            <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Estimación por Distancia ({stats.cardio_type === 'swimming' ? 'Natación' : stats.cardio_type === 'cycling' ? 'Ciclismo' : 'Running'})
            </h3>

            <div class="grid grid-cols-2 gap-2">
                <div class="flex flex-col items-center justify-center rounded-xl bg-slate-900/80 p-3 border border-slate-700/40 text-center">
                    <span class="text-xs font-bold text-slate-400 mb-1 truncate w-full">
                        {stats.cardio_projections.target_2_label}
                    </span>
                    <p class="font-mono text-sm font-bold text-slate-100">
                        {stats.cardio_projections.target_2_time}
                    </p>
                </div>

                <div class="flex flex-col items-center justify-center rounded-xl bg-slate-900/80 p-3 border border-slate-700/40 text-center">
                    <span class="text-xs font-bold text-slate-400 mb-1 truncate w-full">
                        {stats.cardio_projections.target_3_label}
                    </span>
                    <p class="font-mono text-sm font-bold text-slate-100">
                        {stats.cardio_projections.target_3_time}
                    </p>
                </div>

                <div class="flex flex-col items-center justify-center rounded-xl bg-slate-900/80 p-3 border border-slate-700/40 text-center">
                    <span class="text-xs font-bold text-slate-400 mb-1 truncate w-full">
                        {stats.cardio_projections.target_4_label}
                    </span>
                    <p class="font-mono text-sm font-bold text-slate-100">
                        {stats.cardio_projections.target_4_time}
                    </p>
                </div>

                <div class="flex flex-col items-center justify-center rounded-xl bg-slate-900/80 p-3 border border-slate-700/40 text-center">
                    <span class="text-xs font-bold text-slate-400 mb-1 truncate w-full">
                        {stats.cardio_projections.target_5_label}
                    </span>
                    <p class="font-mono text-sm font-bold text-slate-100">
                        {stats.cardio_projections.target_5_time}
                    </p>
                </div>
            </div>
        </div>
    </div>
{:else if stats.max_weight || stats.estimated_1rm}
    <!-- TARJETAS PARA FUERZA -->
    <div class="space-y-4">
        <div class="grid grid-cols-2 gap-3">
            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Máximo (3M)</span>
                <p class="mt-1 font-mono text-xl font-bold text-emerald-400">
                    {stats.max_weight} <span class="text-xs font-normal text-slate-300">{stats.weight_unit || 'kg'}</span>
                </p>
                {#if stats.reps_at_max}
                    <p class="mt-0.5 text-xs text-slate-400">{stats.reps_at_max} reps</p>
                {/if}
            </div>

            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 text-center shadow-md">
                <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">1RM Estimado</span>
                <p class="mt-1 font-mono text-xl font-bold text-blue-400">
                    {stats.estimated_1rm} <span class="text-xs font-normal text-slate-300">{stats.weight_unit || 'kg'}</span>
                </p>
                <p class="mt-0.5 text-xs text-slate-400">Fórmula Epley</p>
            </div>
        </div>

        {#if stats.estimated_1rm}
            <div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md space-y-3">
                <h3 class="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Estimación por Repeticiones
                </h3>

                <div class="grid grid-cols-4 gap-2">
                    {#each [2, 3, 4, 5] as reps}
                        {@const est = estimateWeightForReps(stats.estimated_1rm, reps)}
                        <div class="flex flex-col items-center justify-center rounded-xl bg-slate-900/80 p-3 border border-slate-700/40 text-center">
                            <span class="text-xs font-bold text-slate-400 mb-1">
                                {reps}RM
                            </span>
                            <p class="font-mono text-base font-bold text-slate-100">
                                ~{est} <span class="text-[10px] font-normal text-slate-400">{stats.weight_unit || 'kg'}</span>
                            </p>
                        </div>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
{/if}