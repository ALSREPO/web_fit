<!-- frontend/src/lib/components/historico/ExerciseChart.svelte -->
<script lang="ts">
    import { dashboardApi } from '$lib/services';

    interface Props {
        ejercicio: string;
    }

    let { ejercicio }: Props = $props();

    type MetricType = 'total_volume' | 'max_estimated_1rm' | 'max_weight' | 'total_reps' | 'total_distance' | 'total_time_seconds' | 'avg_ritmo_min_km';
    type TimeframeType = '7d' | '30d' | '12m' | 'all';
    type ChartRenderType = 'bar' | 'line';

    let isCardio = $derived.by(() => {
        const name = (ejercicio || '').toLowerCase();
        return name.includes('correr') || name.includes('nataci') || name.includes('ciclismo') || name.includes('running') || name.includes('natacion') || name.includes('trot');
    });

    let timeframe = $state<TimeframeType>('7d');
    let selectedMetric = $state<MetricType>('total_volume');

    $effect(() => {
        if (isCardio) {
            selectedMetric = 'total_distance';
        } else {
            selectedMetric = 'total_volume';
        }
    });

    let loading = $state(true);
    let chartData = $state<any[]>([]);
    let activePointIndex = $state<number | null>(null);

    const fuerzaMetrics: { id: MetricType; label: string; unit: string; chartType: ChartRenderType }[] = [
        { id: 'total_volume', label: 'Volumen', unit: 'kg', chartType: 'bar' },
        { id: 'max_estimated_1rm', label: '1RM Est.', unit: 'kg', chartType: 'line' },
        { id: 'max_weight', label: 'Carga Máx.', unit: 'kg', chartType: 'line' },
        { id: 'total_reps', label: 'Reps', unit: 'reps', chartType: 'bar' }
    ];

    const cardioMetrics: { id: MetricType; label: string; unit: string; chartType: ChartRenderType }[] = [
        { id: 'total_distance', label: 'Distancia', unit: 'm', chartType: 'bar' },
        { id: 'avg_ritmo_min_km', label: 'Ritmo Medio', unit: 'min/km', chartType: 'line' },
        { id: 'total_time_seconds', label: 'Tiempo Total', unit: 's', chartType: 'bar' }
    ];

    let currentMetrics = $derived(isCardio ? cardioMetrics : fuerzaMetrics);

    const timeframes: { id: TimeframeType; label: string }[] = [
        { id: '7d', label: 'Semana' },
        { id: '30d', label: 'Mes' },
        { id: '12m', label: 'Año' },
        { id: 'all', label: 'Histórico' }
    ];

    $effect(() => {
        if (!ejercicio) return;
        loading = true;
        activePointIndex = null;
        dashboardApi.getExerciseChart(ejercicio, timeframe)
            .then((data: any) => { chartData = Array.isArray(data) ? data : []; })
            .catch(() => { chartData = []; })
            .finally(() => { loading = false; });
    });

    let currentMetricObj = $derived(currentMetrics.find(m => m.id === selectedMetric) || currentMetrics[0]);

    // Filtrar solo puntos con valor > 0 para el modo línea
    let validLinePoints = $derived.by(() => {
        if (!chartData.length) return [];
        return chartData
            .map((item, index) => ({ ...item, originalIndex: index }))
            .filter(item => (item[selectedMetric] || 0) > 0);
    });

    let maxVal = $derived.by(() => {
        if (!chartData.length) return 1;
        const targetData = currentMetricObj.chartType === 'line' ? validLinePoints : chartData;
        if (!targetData.length) return 1;
        const max = Math.max(...targetData.map(d => d[selectedMetric] || 0));
        return max > 0 ? max : 1;
    });

    let minVal = $derived.by(() => {
        if (!chartData.length || currentMetricObj.chartType === 'bar') return 0;
        if (!validLinePoints.length) return 0;
        const vals = validLinePoints.map(d => d[selectedMetric] || 0);
        const min = Math.min(...vals);
        return min * 0.95;
    });

    function handlePointClick(event: MouseEvent, index: number) {
        event.stopPropagation();
        activePointIndex = activePointIndex === index ? null : index;
    }

    function handleWindowClick() {
        activePointIndex = null;
    }

    function shouldShowLabel(index: number, total: number, tf: TimeframeType): boolean {
        if (tf !== '30d') return true;
        return index % 5 === 0 || index === total - 1;
    }

    function formatVal(value: number, metricId: MetricType): string {
        if (metricId === 'total_time_seconds') {
            const mins = Math.floor(value / 60);
            const secs = Math.round(value % 60);
            return `${mins}m ${secs}s`;
        }
        return value.toLocaleString('es-ES');
    }

    // Ruta SVG conectando ÚNICAMENTE los puntos con valor > 0
    let svgLinePath = $derived.by(() => {
        if (currentMetricObj.chartType !== 'line' || validLinePoints.length < 2) return '';
        const range = maxVal - minVal || 1;
        const totalItems = chartData.length;

        return validLinePoints.map((item, i) => {
            const val = item[selectedMetric] || 0;
            const x = (item.originalIndex / (totalItems - 1)) * 100;
            const y = 100 - (((val - minVal) / range) * 80 + 10);
            return `${i === 0 ? 'M' : 'L'} ${x} ${y}`;
        }).join(' ');
    });
</script>

<svelte:window onclick={handleWindowClick} />

<div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-4">
    <!-- Header con Selectores en 2 Filas Completas -->
    <div class="flex flex-col gap-3 border-b border-slate-700/60 pb-3">
        <!-- Fila 1: Selector Rango Temporal (Ancho Completo) -->
        <div class="grid grid-cols-4 gap-1 rounded-xl bg-slate-900/80 p-1 border border-slate-700/40 w-full">
            {#each timeframes as t}
                <button
                    type="button"
                    onclick={() => timeframe = t.id}
                    class="rounded-lg py-1.5 text-center text-xs font-semibold transition-all w-full {timeframe === t.id ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'}"
                >
                    {t.label}
                </button>
            {/each}
        </div>

        <!-- Fila 2: Selector Métrica (Ancho Completo / Distribuido) -->
        <div class="flex w-full items-center justify-around gap-2 rounded-xl bg-slate-900/40 px-2 py-1.5 border border-slate-700/30 text-xs font-medium">
            {#each currentMetrics as m}
                <button
                    type="button"
                    onclick={() => { selectedMetric = m.id; activePointIndex = null; }}
                    class="transition-colors flex items-center justify-center gap-1.5 py-1 px-2 rounded-lg text-center flex-1 {selectedMetric === m.id ? 'text-blue-400 bg-blue-500/10 font-bold border border-blue-500/30' : 'text-slate-400 hover:text-slate-200'}"
                >
                    <span class="text-[10px]">{m.chartType === 'line' ? '📈' : '📊'}</span>
                    <span>{m.label}</span>
                </button>
            {/each}
        </div>
    </div>

    <!-- Contenedor del Gráfico -->
    {#if loading}
        <div class="h-48 w-full animate-pulse rounded-xl bg-slate-900/40"></div>
    {:else if chartData.length === 0}
        <div class="flex h-48 items-center justify-center rounded-xl border border-slate-700/30 bg-slate-900/30 text-xs text-slate-500">
            No hay datos para este período.
        </div>
    {:else}
        <div class="relative h-52 w-full rounded-xl border border-slate-700/40 bg-slate-900/40 p-3 pt-6 flex items-end">
            
            <!-- Líneas de Guía Horizontales de Fondo -->
            <div class="absolute inset-x-3 inset-y-6 flex flex-col justify-between pointer-events-none opacity-15">
                <div class="border-b border-slate-400 w-full"></div>
                <div class="border-b border-slate-400 w-full border-dashed"></div>
                <div class="border-b border-slate-400 w-full"></div>
            </div>

            <!-- Área Principal del Gráfico -->
            <div class="relative w-full h-full">

                {#if currentMetricObj.chartType === 'line'}
                    <!-- RENDERIZADO MODO LÍNEA -->
                    <svg class="w-full h-full overflow-visible" viewBox="0 0 100 100" preserveAspectRatio="none">
                        <path
                            d={svgLinePath}
                            fill="none"
                            stroke="#3b82f6"
                            stroke-width="1.5"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            class="transition-all duration-300"
                        />
                    </svg>

                    <!-- Puntos Interactivos -->
                    <div class="absolute inset-0 pointer-events-none">
                        {#each validLinePoints as item}
                            {@const val = item[selectedMetric] || 0}
                            {@const range = maxVal - minVal || 1}
                            {@const topPercent = 100 - (((val - minVal) / range) * 80 + 10)}
                            {@const leftPercent = (item.originalIndex / (chartData.length - 1)) * 100}
                            {@const isSelected = activePointIndex === item.originalIndex}

                            <button
                                type="button"
                                onclick={(e) => handlePointClick(e, item.originalIndex)}
                                class="group absolute flex flex-col items-center cursor-pointer bg-transparent border-0 p-0 outline-none -translate-x-1/2 -translate-y-1/2 z-10 pointer-events-auto"
                                style="left: {leftPercent}%; top: {topPercent}%;"
                            >
                                <!-- Tooltip con Fecha + Valor -->
                                <div 
                                    class="absolute -top-10 rounded bg-slate-950 px-2 py-1 text-[10px] font-mono text-slate-100 shadow-lg border border-slate-700 z-20 whitespace-nowrap pointer-events-none transition-opacity flex flex-col items-center leading-tight {isSelected ? 'block' : 'hidden group-hover:block'}"
                                >
                                    <span class="text-[9px] text-slate-400 font-sans">{item.label}</span>
                                    <span class="font-bold text-blue-400">{formatVal(val, selectedMetric)} {currentMetricObj.unit}</span>
                                </div>

                                <!-- Punto interactivo (w-2 h-2) -->
                                <div class="w-2 h-2 rounded-full bg-blue-500 border border-slate-900 shadow transition-transform group-hover:scale-150 {isSelected ? 'scale-150 bg-emerald-400 ring-2 ring-white' : ''}"></div>
                            </button>
                        {/each}

                        <!-- Etiquetas del Eje X -->
                        <div class="absolute bottom-0 inset-x-0 flex justify-between translate-y-6 pointer-events-none">
                            {#each chartData as item, index}
                                {@const showLabel = shouldShowLabel(index, chartData.length, timeframe)}
                                <span class="text-[9px] font-medium text-slate-400 truncate text-center flex-1">
                                    {showLabel ? item.label : ''}
                                </span>
                            {/each}
                        </div>
                    </div>

                {:else}
                    <!-- RENDERIZADO MODO COLUMNAS -->
                    <div class="relative flex h-full w-full items-end justify-between">
                        {#each chartData as item, index}
                            {@const val = item[selectedMetric] || 0}
                            {@const heightPercent = Math.max((val / maxVal) * 100, val > 0 ? 6 : 2)}
                            {@const isSelected = activePointIndex === index}
                            {@const showLabel = shouldShowLabel(index, chartData.length, timeframe)}

                            <button
                                type="button"
                                onclick={(e) => handlePointClick(e, index)}
                                class="group relative flex h-full flex-1 flex-col items-center justify-end cursor-pointer bg-transparent border-0 p-0 outline-none min-w-0"
                            >
                                <!-- Tooltip con Fecha + Valor -->
                                <div 
                                    class="absolute -top-10 rounded bg-slate-950 px-2 py-1 text-[10px] font-mono text-slate-100 shadow-lg border border-slate-700 z-20 whitespace-nowrap pointer-events-none transition-opacity flex flex-col items-center leading-tight {isSelected ? 'block' : 'hidden group-hover:block'}"
                                >
                                    <span class="text-[9px] text-slate-400 font-sans">{item.label}</span>
                                    <span class="font-bold text-blue-400">{formatVal(val, selectedMetric)} {currentMetricObj.unit}</span>
                                </div>

                                <!-- Columna Fina -->
                                <div
                                    class="w-full max-w-[8px] sm:max-w-[12px] rounded-t-sm transition-all duration-200 {val > 0 ? 'bg-blue-500 group-hover:bg-blue-400' : 'bg-slate-800/60'} {isSelected ? 'brightness-125 ring-1 ring-white' : ''}"
                                    style="height: {heightPercent}%"
                                ></div>

                                <!-- Etiqueta Eje X -->
                                <span class="absolute -bottom-6 text-[9px] font-medium text-slate-400 truncate w-full text-center">
                                    {showLabel ? item.label : ''}
                                </span>
                            </button>
                        {/each}
                    </div>
                {/if}

            </div>
        </div>
    {/if}
</div>