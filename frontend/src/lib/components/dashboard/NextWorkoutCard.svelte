<!-- 
frontend/src/lib/components/dashboard/NextWorkoutCard.svelte 
Widget Próximo Entrenamiento
-->
<script lang="ts">
	import WorkoutCard from './WorkoutCard.svelte';

	let { data = null }: { data?: any } = $props();

	// Evalúa dinámicamente si es hoy (rojo) o fecha futura/mañana (amarillo)
	let badgeColor = $derived(data?.date_label?.startsWith('Hoy') ? 'red' : 'yellow');
</script>

<WorkoutCard 
	title="Siguiente Entrenamiento" 
	cardData={data} 
	{badgeColor} 
/>