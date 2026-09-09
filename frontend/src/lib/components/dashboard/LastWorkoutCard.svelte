<!-- 
frontend/src/lib/components/dashboard/LastWorkoutCard.svelte 
Widget Último Entrenamiento
-->
<script lang="ts">
	import WorkoutCard from './WorkoutCard.svelte';

	let { data = null, loading = false }: { data?: any; loading?: boolean } = $props();
</script>

<WorkoutCard 
	title="Entrenamiento anterior" 
	cardData={data} 
	dateColorClass="text-emerald-400" 
	{loading} 
/>