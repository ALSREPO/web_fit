<!-- 
frontend/src/lib/components/dashboard/LastWorkoutCard.svelte 
Widget Último Entrenamiento
-->
<script lang="ts">
	import WorkoutCard from './WorkoutCard.svelte';

	let { data = null }: { data?: any } = $props();
</script>

<WorkoutCard 
	title="Último Entrenamiento" 
	cardData={data} 
	badgeColor="green" 
/>