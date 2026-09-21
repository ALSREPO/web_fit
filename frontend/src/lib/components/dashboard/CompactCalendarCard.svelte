<!-- 
frontend/src/lib/components/dashboard/CompactCalendarCard.svelte 
Widget Calendario Compacto
-->
<script>
	import { goto } from '$app/navigation';
	import { dashboardApi } from '$lib/services';

	// Props
	let { data = null, loading = false } = $props();

	// Control de fecha seleccionada
	let currentDate = $state(new Date());
	let selectedYear = $state(currentDate.getFullYear());
	let selectedMonth = $state(currentDate.getMonth() + 1); // 1-12

	let internalData = $state(null);
	let internalLoading = $state(false);

	// Actualizar datos internos cuando viene prop inicial
	$effect(() => {
		if (data && !internalData && !internalLoading) {
			internalData = data;
		}
	});

	// Cargar datos iniciales si no hay prop data al montar
	$effect(() => {
		if (!internalData && !data && !internalLoading && selectedYear && selectedMonth) {
			fetchMonthData(selectedYear, selectedMonth);
		}
	});

	// Array de meses y años para los selecciones
	const months = [
		'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
		'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
	];
	
	const currentYear = new Date().getFullYear();
	const years = Array.from({ length: 5 }, (_, i) => currentYear - 2 + i); // Ejemplo: 2 años atrás y 2 adelante

	// Días de la semana para cabecera
	const weekDays = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'];

	// Mapeo de colores según disciplina/tipo de entrenamiento
	function getDotColorClass(type) {
		if (!type) return 'bg-gray-400';
		const lower = type.toLowerCase();
		
		if (lower.includes('fuerza') || lower.includes('strength') || lower.includes('pesa')) {
			return 'bg-red-500';
		}
		if (lower.includes('nataci') || lower.includes('swim') || lower.includes('agua')) {
			return 'bg-blue-500';
		}
		if (lower.includes('carrera') || lower.includes('run') || lower.includes('correr')) {
			return 'bg-emerald-500';
		}
		if (lower.includes('cicl') || lower.includes('bici') || lower.includes('bike')) {
			return 'bg-orange-500';
		}
		if (lower.includes('mma') || lower.includes('bjj') || lower.includes('jiu') || lower.includes('luta') || lower.includes('boxeo')) {
			return 'bg-purple-500';
		}
		return 'bg-yellow-500';
	}

	async function fetchMonthData(year, month) {
		internalLoading = true;
		try {
			internalData = await dashboardApi.getCompactCalendar(year, month);
		} catch (e) {
			console.error('Error al cargar calendario:', e);
		} finally {
			internalLoading = false;
		}
	}

	function changeMonth(delta) {
		let newMonth = selectedMonth + delta;
		let newYear = selectedYear;

		if (newMonth > 12) {
			newMonth = 1;
			newYear++;
		} else if (newMonth < 1) {
			newMonth = 12;
			newYear--;
		}

		selectedMonth = newMonth;
		selectedYear = newYear;
		fetchMonthData(selectedYear, selectedMonth);
	}

	function onSelectChange() {
		fetchMonthData(selectedYear, selectedMonth);
	}

	function goToDayDetail(dateStr) {
		if (!dateStr) return;
		// Navega a la pantalla del día seleccionado
		goto(`/detalle/${dateStr}`);
	}

	// Matriz de días para construir el grid del calendario
	let calendarGrid = $derived.by(() => {
		const year = selectedYear;
		const month = selectedMonth - 1; // 0-indexed para JavaScript Date

		const firstDayOfMonth = new Date(year, month, 1);
		const lastDayOfMonth = new Date(year, month + 1, 0);

		// Ajustar el primer día de la semana (Lunes = 0, Domingo = 6)
		let startDay = firstDayOfMonth.getDay() - 1;
		if (startDay === -1) startDay = 6;

		const totalDays = lastDayOfMonth.getDate();
		const days = [];

		// Días vacíos del mes anterior
		for (let i = 0; i < startDay; i++) {
			days.push(null);
		}

		// Días del mes actual
		const activeDaysMap = new Map();
		const activeList = (internalData?.days || internalData || []);
		if (Array.isArray(activeList)) {
			activeList.forEach((item) => {
				// Supone que 'item' trae { date: 'YYYY-MM-DD', types: ['fuerza', 'carrera'] } o similar
				const key = item.date || item.day;
				activeDaysMap.set(key, item.types || item.workouts || [item.type]);
			});
		}

		for (let day = 1; day <= totalDays; day++) {
			const formattedMonth = String(selectedMonth).padStart(2, '0');
			const formattedDay = String(day).padStart(2, '0');
			const dateStr = `${year}-${formattedMonth}-${formattedDay}`;

			days.push({
				dayNumber: day,
				dateStr: dateStr,
				workouts: activeDaysMap.get(dateStr) || []
			});
		}

		return days;
	});
</script>

<div class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-5 shadow-md space-y-4">
    <!-- Encabezado fijo arriba -->
    <div class="border-b border-slate-700/60 pb-3">
        <h3 class="text-base font-bold text-slate-200">Calendario Mensual</h3>
    </div>

    <!-- Barra de navegación (Mes / Año) -->
    <div class="flex w-full items-center gap-1.5">
        <!-- Botón Mes Anterior -->
        <button
            type="button"
            onclick={() => changeMonth(-1)}
            class="shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white"
            aria-label="Mes anterior"
        >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
        </button>

        <!-- Desplegable Mes -->
        <select
            bind:value={selectedMonth}
            onchange={onSelectChange}
            class="min-w-0 flex-1 truncate rounded-lg border border-slate-700/60 bg-slate-900/50 px-2 py-2 text-center text-xs font-medium text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
            {#each months as monthName, idx}
                <option value={idx + 1} class="bg-slate-800 text-slate-200">{monthName}</option>
            {/each}
        </select>

        <!-- Desplegable Año -->
        <select
            bind:value={selectedYear}
            onchange={onSelectChange}
            class="w-20 shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 px-2 py-2 text-center text-xs font-medium text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
            {#each years as yr}
                <option value={yr} class="bg-slate-800 text-slate-200">{yr}</option>
            {/each}
        </select>

        <!-- Botón Mes Siguiente -->
        <button
            type="button"
            onclick={() => changeMonth(1)}
            class="shrink-0 rounded-lg border border-slate-700/60 bg-slate-900/50 p-2 text-slate-300 transition hover:bg-slate-700 hover:text-white"
            aria-label="Mes siguiente"
        >
            <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
        </button>
    </div>

    <!-- Leyenda de colores -->
    <div class="flex w-full flex-wrap items-center justify-between gap-2 rounded-xl border border-slate-700/40 bg-slate-900/50 p-2.5 text-xs text-slate-400">
        <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-red-500"></span> Fuerza</span>
        <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-emerald-500"></span> Carrera</span>
        <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-orange-500"></span> Ciclismo</span>
        <span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-blue-500"></span> Natación</span>
    </div>

    <!-- Grid del Calendario -->
    {#if loading || internalLoading}
        <div class="flex h-48 items-center justify-center text-xs text-slate-500">
            Cargando calendario...
        </div>
    {:else}
        <div class="grid grid-cols-7 gap-1 text-center">
            <!-- Días de la semana -->
            {#each weekDays as day}
                <div class="py-1 text-xs font-semibold text-slate-400">
                    {day}
                </div>
            {/each}

            <!-- Casillas de los días -->
            {#each calendarGrid as cell}
                {#if cell === null}
                    <div class="h-10 rounded-lg bg-transparent"></div>
                {:else}
                    <button
                        type="button"
                        onclick={() => goToDayDetail(cell.dateStr)}
                        class="group relative flex h-10 flex-col items-center justify-between rounded-lg border border-slate-700/40 bg-slate-900/40 p-1 text-xs text-slate-200 transition hover:border-blue-500/50 hover:bg-slate-700/50"
                    >
                        <span>{cell.dayNumber}</span>

                        <!-- Puntos de disciplinas entrenadas ese día -->
                        <div class="flex items-center justify-center space-x-1">
                            {#each cell.workouts as workoutType}
                                <span class="h-1.5 w-1.5 rounded-full {getDotColorClass(workoutType)}"></span>
                            {/each}
                        </div>
                    </button>
                {/if}
            {/each}
        </div>
    {/if}
</div>