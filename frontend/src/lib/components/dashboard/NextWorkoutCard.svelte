<!-- 
frontend/src/lib/components/dashboard/NextWorkoutCard.svelte 
Widget Próximo Entrenamiento
-->
<script lang="ts">
	import WorkoutCard from './WorkoutCard.svelte';

	let { data = null, loading = false }: { data?: any; loading?: boolean } = $props();

	let dateColorClass = $derived(
		data?.date_label?.startsWith('Hoy') ? 'text-rose-400' : 'text-amber-400'
	);
</script>

<WorkoutCard 
	title="Próximo entrenamiento" 
	cardData={data} 
	{dateColorClass} 
	{loading} 
/>