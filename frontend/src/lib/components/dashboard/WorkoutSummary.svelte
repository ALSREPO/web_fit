<!-- frontend/src/lib/components/dashboard/WorkoutSummary.svelte -->
<script lang="ts">
    interface MetricItem {
        label: string;
        volume_kg: number;
        distance_km: number;
        sessions_count: number;
    }

    interface SummaryData {
        period: 'week' | 'month' | 'year' | 'all';
        kpis: {
            days_count: number;
            sessions_count: number;
            total_volume_kg: number;
            total_distance_km: number;
        };
        chart_by_time: MetricItem[];
        chart_by_type: MetricItem[];
    }

    interface Props {
        onPeriodChange?: (period: string) => void;
        summaryData?: SummaryData | null;
        loading?: boolean;
    }

    let { onPeriodChange, summaryData = null, loading = false }: Props = $props();

    const periods = [
        { id: 'week', label: 'Semana' },
        { id: 'month', label: 'Mes' },
        { id: 'year', label: 'Año' },
        { id: 'all', label: 'Histórico' }
    ];

    let activePeriod = $state<string>('week');
    let chartView = $state<'time' | 'type'>('time');
    let selectedMetric = $state<'sessions_count' | 'volume_kg' | 'distance_km'>('sessions_count');

    function selectPeriod(pId: string) {
        activePeriod = pId;
        if (onPeriodChange) {
            onPeriodChange(pId);
        }
    }
    
    // Obtener datos activos filtrando según el tipo de métrica seleccionada
    let activeChartData = $derived.by(() => {
        if (!summaryData) return [];

        const rawData = chartView === 'time'
            ? summaryData.chart_by_time || []
            : summaryData.chart_by_type || [];

        if (chartView === 'time') {
            return rawData;
        }

        return rawData.filter((item) => {
            if (selectedMetric === 'volume_kg') {
                return (item.volume_kg || 0) > 0;
            }
            if (selectedMetric === 'distance_km') {
                return (item.distance_km || 0) > 0;
            }
            return (item.sessions_count || 0) > 0;
        });
    });

    // Calcular valor máximo para escalar la altura de las barras
    let maxVal = $derived.by(() => {
        if (!activeChartData.length) return 1;
        const max = Math.max(...activeChartData.map((d) => d[selectedMetric] || 0));
        return max > 0 ? max : 1;
    });

    const metricUnits = {
        sessions_count: 'sesiones',
        volume_kg: 'kg',
        distance_km: 'km'
    };

    let activeBarIndex = $state<number | null>(null);

    function handleBarSelect(event: Event, index: number) {
        event.stopPropagation();
        activeBarIndex = activeBarIndex === index ? null : index;
    }

    function handleWindowClick() {
        activeBarIndex = null;
    }

    function shouldShowXLabel(index: number, total: number): boolean {
        if (activePeriod !== 'month' || chartView !== 'time') return true;
        return index % 5 === 0 || index === total - 1;
    }

    function formatVal(value: number): string {
        return value.toLocaleString('es-ES');
    }
</script>

<svelte:window onclick={handleWindowClick} />

<section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-6">
    <!-- Header con Selector de Periodo -->
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-700/60 pb-3">
        <h2 class="text-base font-bold text-slate-200">Resumen</h2>
        <div class="grid w-full flex-1 grid-cols-4 gap-1 rounded-xl border border-slate-700/40 bg-slate-900/80 p-1 min-w-[280px] sm:w-auto sm:flex-none">
            {#each periods as p}
                <button
                    type="button"
                    onclick={() => selectPeriod(p.id)}
                    class="rounded-lg py-1.5 text-center text-xs font-semibold transition-all {activePeriod === p.id
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    {p.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Tarjetas KPI -->
    <div class="grid grid-cols-2 gap-3 sm:grid-cols-2">
        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Días</span>
            <p class="mt-1 text-2xl font-bold text-slate-100">
                {loading ? '...' : summaryData?.kpis?.days_count ?? 0}
            </p>
        </div>

        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Sesiones</span>
            <p class="mt-1 text-2xl font-bold text-blue-400">
                {loading ? '...' : summaryData?.kpis?.sessions_count ?? 0}
            </p>
        </div>

        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Volumen</span>
            <p class="mt-1 text-2xl font-bold text-amber-400">
                {loading ? '...' : formatVal(summaryData?.kpis?.total_volume_kg ?? 0)}
                <span class="text-xs font-normal text-slate-400">kg</span>
            </p>
        </div>

        <div class="rounded-xl border border-slate-700/40 bg-slate-900/50 p-3.5 text-center">
            <span class="text-xs font-medium text-slate-400">Distancia</span>
            <p class="mt-1 text-2xl font-bold text-emerald-400">
                {loading ? '...' : formatVal(summaryData?.kpis?.total_distance_km ?? 0)}
                <span class="text-xs font-normal text-slate-400">km</span>
            </p>
        </div>
    </div>

    <!-- Gráfico y Controles -->
    <div class="space-y-4 pt-2">
        <div class="flex flex-wrap items-center justify-between gap-3">
            <!-- Selector Tipo / Periodo -->
            <div class="flex gap-1 rounded-lg bg-slate-900/60 p-1 border border-slate-700/30">
                <button
                    type="button"
                    onclick={() => { chartView = 'time'; activeBarIndex = null; }}
                    class="rounded px-2.5 py-1 text-xs font-medium transition-all {chartView === 'time'
                        ? 'bg-slate-700 text-slate-100'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    Periodo
                </button>
                <button
                    type="button"
                    onclick={() => { chartView = 'type'; activeBarIndex = null; }}
                    class="rounded px-2.5 py-1 text-xs font-medium transition-all {chartView === 'type'
                        ? 'bg-slate-700 text-slate-100'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    Tipo
                </button>
            </div>

            <!-- Selector de Métrica -->
            <div class="flex gap-3 text-xs font-medium">
                <button
                    type="button"
                    onclick={() => { selectedMetric = 'sessions_count'; activeBarIndex = null; }}
                    class="transition-colors {selectedMetric === 'sessions_count'
                        ? 'text-blue-400 underline underline-offset-4'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    Sesiones
                </button>
                <button
                    type="button"
                    onclick={() => { selectedMetric = 'volume_kg'; activeBarIndex = null; }}
                    class="transition-colors {selectedMetric === 'volume_kg'
                        ? 'text-amber-400 underline underline-offset-4'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    Volumen (kg)
                </button>
                <button
                    type="button"
                    onclick={() => { selectedMetric = 'distance_km'; activeBarIndex = null; }}
                    class="transition-colors {selectedMetric === 'distance_km'
                        ? 'text-emerald-400 underline underline-offset-4'
                        : 'text-slate-400 hover:text-slate-200'}"
                >
                    Distancia (km)
                </button>
            </div>
        </div>

        <!-- Área del Gráfico de Barras -->
        {#if loading}
            <div class="h-52 w-full animate-pulse rounded-xl bg-slate-900/40"></div>
        {:else if activeChartData.length === 0}
            <div class="flex h-52 items-center justify-center rounded-xl border border-slate-700/30 bg-slate-900/30 text-xs text-slate-500">
                No hay datos registrados para este periodo.
            </div>
        {:else}
            <div class="relative h-52 w-full rounded-xl border border-slate-700/40 bg-slate-900/40 p-3 pt-6 pb-8 flex items-end">
                
                <!-- Guías Horizontales de Fondo -->
                <div class="absolute inset-x-3 top-6 bottom-8 flex flex-col justify-between pointer-events-none opacity-15">
                    <div class="border-b border-slate-400 w-full"></div>
                    <div class="border-b border-slate-400 w-full border-dashed"></div>
                    <div class="border-b border-slate-400 w-full"></div>
                </div>

                <!-- Barras -->
                <div class="relative flex h-full w-full items-end justify-between gap-1">
                    {#each activeChartData as item, index}
                        {@const val = item[selectedMetric] || 0}
                        {@const heightPercent = val > 0 ? Math.max((val / maxVal) * 100, 4) : 0}
                        {@const isSelected = activeBarIndex === index}
                        {@const showLabel = shouldShowXLabel(index, activeChartData.length)}

                        <button
                            type="button"
                            onclick={(e) => handleBarSelect(e, index)}
                            class="group relative flex h-full flex-1 flex-col items-center justify-end cursor-pointer bg-transparent border-0 p-0 outline-none min-w-0"
                        >
                            <!-- Tooltip -->
                            <div 
                                class="absolute -top-10 rounded bg-slate-950 px-2 py-1 text-[10px] font-mono text-slate-100 shadow-lg border border-slate-700 z-20 whitespace-nowrap pointer-events-none transition-opacity flex flex-col items-center leading-tight {isSelected ? 'block' : 'hidden group-hover:block'}"
                            >
                                <span class="text-[9px] text-slate-400 font-sans">{item.label}</span>
                                <span class="font-bold text-blue-400">{formatVal(val)} {metricUnits[selectedMetric]}</span>
                            </div>

                            <!-- Columna de grosor uniforme con gap -->
                            <div
                                class="w-full rounded-t-sm transition-all duration-200 {val > 0
                                    ? selectedMetric === 'sessions_count'
                                        ? 'bg-blue-500 group-hover:bg-blue-400'
                                        : selectedMetric === 'volume_kg'
                                        ? 'bg-amber-500 group-hover:bg-amber-400'
                                        : 'bg-emerald-500 group-hover:bg-emerald-400'
                                    : 'bg-slate-800/30'} {isSelected ? 'brightness-125 ring-1 ring-white' : ''}"
                                style="height: {heightPercent}%"
                            ></div>

                            <!-- Etiqueta Eje X -->
                            <span class="absolute -bottom-6 text-[9px] font-medium text-slate-400 truncate w-full text-center">
                                {showLabel ? item.label : ''}
                            </span>
                        </button>
                    {/each}
                </div>
            </div>
        {/if}
    </div>
</section>