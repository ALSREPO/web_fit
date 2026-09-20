<!-- frontend/src/lib/components/historico/ExerciseChart.svelte -->
<script lang="ts">
    import { dashboardApi } from '$lib/services';

    interface Props {
        ejercicio: string;
    }

    let { ejercicio }: Props = $props();

    type MetricType = 'total_volume' | 'max_estimated_1rm' | 'max_weight' | 'total_reps';
    type TimeframeType = '7d' | '30d' | '12m' | 'all';

    let timeframe = $state<TimeframeType>('7d');
    let selectedMetric = $state<MetricType>('total_volume');
    
    let loading = $state(true);
    let chartData = $state<any[]>([]);
    let activeBarIndex = $state<number | null>(null);

    const metrics: { id: MetricType; label: string; unit: string }[] = [
        { id: 'total_volume', label: 'Volumen', unit: 'kg' },
        { id: 'max_estimated_1rm', label: '1RM Est.', unit: 'kg' },
        { id: 'max_weight', label: 'Carga Máx.', unit: 'kg' },
        { id: 'total_reps', label: 'Reps', unit: 'reps' }
    ];

    const timeframes: { id: TimeframeType; label: string }[] = [
        { id: '7d', label: 'Semana' },
        { id: '30d', label: 'Mes' },
        { id: '12m', label: 'Año' },
        { id: 'all', label: 'Histórico' }
    ];

    $effect(() => {
        if (!ejercicio) return;
        loading = true;
        activeBarIndex = null;
        dashboardApi.getExerciseChart(ejercicio, timeframe)
            .then((data: any) => { chartData = Array.isArray(data) ? data : []; })
            .catch(() => { chartData = []; })
            .finally(() => { loading = false; });
    });

    let currentMetricObj = $derived(metrics.find(m => m.id === selectedMetric)!);

    let maxVal = $derived.by(() => {
        if (!chartData.length) return 1;
        const max = Math.max(...chartData.map(d => d[selectedMetric] || 0));
        return max > 0 ? max : 1;
    });

    function handleBarClick(event: MouseEvent, index: number) {
        event.stopPropagation();
        activeBarIndex = activeBarIndex === index ? null : index;
    }

    function handleWindowClick() {
        activeBarIndex = null;
    }

    // Determina si se debe renderizar la etiqueta del eje X para no saturar 30d
    function shouldShowLabel(index: number, total: number, tf: TimeframeType): boolean {
        if (tf !== '30d') return true;
        // En vista de 30 días, mostrar cada 5 días y la última barra
        return index % 5 === 0 || index === total - 1;
    }
</script>

<svelte:window onclick={handleWindowClick} />

<div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-4">
    <!-- Header con Selectores -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between border-b border-slate-700/60 pb-3">
        <!-- Selector Rango Temporal -->
        <div class="flex gap-1 rounded-xl bg-slate-900/80 p-1 border border-slate-700/40">
            {#each timeframes as t}
                <button
                    type="button"
                    onclick={() => timeframe = t.id}
                    class="rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all {timeframe === t.id ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}"
                >
                    {t.label}
                </button>
            {/each}
        </div>

        <!-- Selector Métrica -->
        <div class="flex flex-wrap gap-2 text-xs font-medium">
            {#each metrics as m}
                <button
                    type="button"
                    onclick={() => { selectedMetric = m.id; activeBarIndex = null; }}
                    class="transition-colors {selectedMetric === m.id ? 'text-blue-400 underline underline-offset-4 font-bold' : 'text-slate-400 hover:text-slate-200'}"
                >
                    {m.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Contenedor del Gráfico de Barras -->
    {#if loading}
        <div class="h-48 w-full animate-pulse rounded-xl bg-slate-900/40"></div>
    {:else if chartData.length === 0}
        <div class="flex h-48 items-center justify-center rounded-xl border border-slate-700/30 bg-slate-900/30 text-xs text-slate-500">
            No hay datos para este período.
        </div>
    {:else}
        <div 
            class="relative flex h-48 items-end rounded-xl border border-slate-700/40 bg-slate-900/40 p-3 pt-8 overflow-hidden {timeframe === '30d' ? 'gap-1' : 'gap-2'}"
        >
            {#each chartData as item, index}
                {@const val = item[selectedMetric] || 0}
                {@const heightPercent = Math.max((val / maxVal) * 100, val > 0 ? 8 : 2)}
                {@const isSelected = activeBarIndex === index}
                {@const showLabel = shouldShowLabel(index, chartData.length, timeframe)}

                <button
                    type="button"
                    onclick={(e) => handleBarClick(e, index)}
                    class="group relative flex h-full flex-1 flex-col items-center justify-end cursor-pointer bg-transparent border-0 p-0 outline-none min-w-0"
                >
                    <!-- Tooltip al pulsar / hover -->
                    <div 
                        class="absolute -top-7 rounded bg-slate-950 px-2 py-0.5 text-[10px] font-mono text-slate-100 shadow-lg border border-slate-700 z-20 whitespace-nowrap pointer-events-none transition-opacity {isSelected ? 'block' : 'hidden group-hover:block'}"
                    >
                        {val.toLocaleString('es-ES')} {currentMetricObj.unit}
                    </div>

                    <!-- Barra -->
                    <div
                        class="w-full rounded-t transition-all duration-200 {val > 0 ? 'bg-blue-500 group-hover:bg-blue-400' : 'bg-slate-800/80'} {isSelected ? 'brightness-125 ring-1 ring-white' : ''}"
                        style="height: {heightPercent}%"
                    ></div>

                    <!-- Etiqueta eje X -->
                    <span class="mt-2 text-[9px] font-medium text-slate-400 truncate w-full text-center">
                        {showLabel ? item.label : ''}
                    </span>
                </button>
            {/each}
        </div>
    {/if}
</div>