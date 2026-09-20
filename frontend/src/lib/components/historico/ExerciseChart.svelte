<!-- frontend/src/lib/components/historico/ExerciseChart.svelte -->
<script>
    import { dashboardApi } from '$lib/services';

    let { ejercicio } = $props();

    let timeframe = $state('30d'); // '7d', '30d', '12m', 'all'
    let selectedMetric = $state('total_volume'); // 'total_volume', 'max_estimated_1rm', 'max_weight', 'total_reps'
    
    let loading = $state(true);
    let chartData = $state([]);

    const metrics = [
        { id: 'total_volume', label: 'Volumen', unit: 'kg' },
        { id: 'max_estimated_1rm', label: '1RM Est.', unit: 'kg' },
        { id: 'max_weight', label: 'Carga Máx.', unit: 'kg' },
        { id: 'total_reps', label: 'Reps Totales', unit: 'reps' }
    ];

    const timeframes = [
        { id: '7d', label: '7D' },
        { id: '30d', label: '30D' },
        { id: '12m', label: '12M' },
        { id: 'all', label: 'Histórico' }
    ];

    $effect(() => {
        if (!ejercicio) return;
        loading = true;
        dashboardApi.getExerciseChart(ejercicio, timeframe)
            .then(data => { chartData = data; })
            .catch(() => { chartData = []; })
            .finally(() => { loading = false; });
    });

    let maxValue = $derived.by(() => {
        if (!chartData.length) return 1;
        const max = Math.max(...chartData.map(d => d[selectedMetric] || 0));
        return max > 0 ? max : 1;
    });

    function getMetricUnit(id) {
        return metrics.find(m => m.id === id)?.unit || '';
    }
</script>

<div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md space-y-4">
    <!-- Selectores de Control -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <!-- Selector de Métrica -->
        <div class="flex flex-wrap gap-1 rounded-xl bg-slate-900/80 p-1">
            {#each metrics as m}
                <button
                    type="button"
                    onclick={() => selectedMetric = m.id}
                    class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-all {selectedMetric === m.id ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'}"
                >
                    {m.label}
                </button>
            {/each}
        </div>

        <!-- Selector de Rango Temporal -->
        <div class="flex rounded-xl bg-slate-900/80 p-1 self-start sm:self-auto">
            {#each timeframes as t}
                <button
                    type="button"
                    onclick={() => timeframe = t.id}
                    class="rounded-lg px-2.5 py-1 text-xs font-semibold transition-all {timeframe === t.id ? 'bg-slate-700 text-white shadow' : 'text-slate-400 hover:text-slate-200'}"
                >
                    {t.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Renderizado del Gráfico de Barras -->
    {#if loading}
        <div class="h-44 w-full animate-pulse rounded-xl bg-slate-900/50"></div>
    {:else if chartData.length === 0}
        <div class="flex h-44 items-center justify-center text-xs text-slate-500">
            Sin datos en este período
        </div>
    {:else}
        <div class="space-y-1">
            <div class="flex h-40 items-end gap-1.5 pt-6 pb-2 px-1">
                {#each chartData as point}
                    {@const val = point[selectedMetric] || 0}
                    {@const heightPercent = Math.max(8, (val / maxValue) * 100)}
                    
                    <div class="group relative flex flex-1 flex-col items-center h-full justify-end">
                        <!-- Tooltip Hover -->
                        <div class="absolute -top-7 hidden group-hover:flex flex-col items-center z-10 whitespace-nowrap rounded bg-slate-950 px-2 py-0.5 text-[10px] font-mono text-slate-200 shadow-lg border border-slate-700">
                            <span>{val.toLocaleString('es-ES')} {getMetricUnit(selectedMetric)}</span>
                        </div>

                        <!-- Barra -->
                        <div 
                            style="height: {heightPercent}%;" 
                            class="w-full max-w-[32px] rounded-t-md bg-blue-500/80 transition-all duration-300 group-hover:bg-blue-400"
                        ></div>
                    </div>
                {/each}
            </div>

            <!-- Labels del Eje X -->
            <div class="flex justify-between border-t border-slate-700/60 pt-1.5 px-1 text-[10px] font-mono text-slate-400">
                <span>{chartData[0]?.period}</span>
                {#if chartData.length > 2}
                    <span>{chartData[Math.floor(chartData.length / 2)]?.period}</span>
                {/if}
                <span>{chartData[chartData.length - 1]?.period}</span>
            </div>
        </div>
    {/if}
</div>