<!-- frontend/src/lib/components/dashboard/SummarySection.svelte -->
<script lang="ts">
	import { onMount } from 'svelte';
	import WorkoutSummary from './WorkoutSummary.svelte';

	let summaryData = $state<any>(null);
	let loading = $state<boolean>(true);
	let currentPeriod = $state<string>('week');

	async function fetchSummary(period: string) {
		loading = true;
		try {
			const res = await fetch(`/api/v1/dashboard/summary?period=${period}`);
			if (res.ok) {
				summaryData = await res.json();
			} else {
				console.error('Error al cargar resumen:', res.statusText);
			}
		} catch (err) {
			console.error('Error de red al cargar resumen:', err);
		} finally {
			loading = false;
		}
	}

	function handlePeriodChange(newPeriod: string) {
		currentPeriod = newPeriod;
		fetchSummary(newPeriod);
	}

	onMount(() => {
		fetchSummary(currentPeriod);
	});
</script>

<WorkoutSummary
	{summaryData}
	{loading}
	onPeriodChange={handlePeriodChange}
/>