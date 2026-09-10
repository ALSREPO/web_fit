<!-- Mapa muscular frontal / trasero. Rojo = principal, amarillo = secundario, gris = no trabajado -->
<script>
	let { muscles = [] } = $props();

	let view = $state('front');

	const ROLE_PRIORITY = { Principal: 2, Asistencial: 1 };

	let colorById = $derived.by(() => {
		const map = {};
		for (const muscle of muscles || []) {
			const role = muscle.role;
			const ids = muscle.svg_ids || [];
			for (const id of ids) {
				if (!map[id] || (ROLE_PRIORITY[role] || 0) > (ROLE_PRIORITY[map[id]] || 0)) {
					map[id] = role;
				}
			}
		}
		return map;
	});

	function fill(id) {
		const role = colorById[id];
		if (role === 'Principal') return '#ef4444';
		if (role === 'Asistencial') return '#eab308';
		return '#475569';
	}

	const idleStroke = '#0f172a';
</script>

<section class="rounded-2xl border border-slate-700/60 bg-slate-800/90 p-4 shadow-md">
	<div class="mb-3 flex items-center justify-between gap-2">
		<h3 class="text-base font-semibold text-white">Mapa muscular</h3>
		<div class="flex rounded-lg border border-slate-700 bg-slate-900 p-0.5 text-xs">
			<button
				type="button"
				onclick={() => (view = 'front')}
				class="rounded-md px-3 py-1.5 font-medium transition {view === 'front'
					? 'bg-blue-600 text-white'
					: 'text-slate-400 hover:text-white'}"
			>
				Frontal
			</button>
			<button
				type="button"
				onclick={() => (view = 'back')}
				class="rounded-md px-3 py-1.5 font-medium transition {view === 'back'
					? 'bg-blue-600 text-white'
					: 'text-slate-400 hover:text-white'}"
			>
				Trasero
			</button>
		</div>
	</div>

	<div class="flex justify-center">
		{#if view === 'front'}
			<svg viewBox="0 0 220 460" class="h-80 w-auto max-w-full" aria-label="Cuerpo vista frontal">
				<!-- Cabeza / cuello -->
				<ellipse cx="110" cy="28" rx="22" ry="26" fill="#64748b" stroke={idleStroke} stroke-width="1.5" />
				<rect x="102" y="52" width="16" height="16" rx="4" fill="#64748b" stroke={idleStroke} stroke-width="1.5" />

				<!-- Trapecio frontal -->
				<path
					id="traps-front"
					d="M78 70 L110 62 L142 70 L132 86 L110 80 L88 86 Z"
					fill={fill('traps-front')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Hombros -->
				<ellipse
					id="shoulders-front"
					cx="62"
					cy="92"
					rx="22"
					ry="16"
					fill={fill('shoulders-front')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<ellipse
					cx="158"
					cy="92"
					rx="22"
					ry="16"
					fill={fill('shoulders-front')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Pectoral superior -->
				<path
					id="chest-upper"
					d="M80 86 L110 80 L140 86 L136 102 L110 96 L84 102 Z"
					fill={fill('chest-upper')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Pectoral -->
				<path
					id="chest"
					d="M84 100 L110 94 L136 100 L140 132 L110 126 L80 132 Z"
					fill={fill('chest')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Bíceps -->
				<ellipse
					id="biceps"
					cx="48"
					cy="138"
					rx="14"
					ry="28"
					fill={fill('biceps')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<ellipse
					cx="172"
					cy="138"
					rx="14"
					ry="28"
					fill={fill('biceps')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Antebrazos -->
				<rect x="36" y="164" width="16" height="46" rx="8" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />
				<rect x="168" y="164" width="16" height="46" rx="8" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />

				<!-- Abdominales -->
				<path
					id="abs"
					d="M88 130 L110 124 L132 130 L128 210 L110 216 L92 210 Z"
					fill={fill('abs')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Oblicuos / cadera -->
				<path d="M80 170 L92 210 L78 230 L62 210 Z" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />
				<path d="M140 170 L128 210 L142 230 L158 210 Z" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />

				<!-- Cuádriceps -->
				<path
					id="quads"
					d="M78 228 L110 220 L96 340 L72 336 Z"
					fill={fill('quads')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M110 220 L142 228 L148 336 L124 340 Z"
					fill={fill('quads')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Gemelos frontales -->
				<path
					id="calves-front"
					d="M74 338 L94 342 L90 420 L70 416 Z"
					fill={fill('calves-front')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M126 342 L146 338 L150 416 L130 420 Z"
					fill={fill('calves-front')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
			</svg>
		{:else}
			<svg viewBox="0 0 220 460" class="h-80 w-auto max-w-full" aria-label="Cuerpo vista trasera">
				<ellipse cx="110" cy="28" rx="22" ry="26" fill="#64748b" stroke={idleStroke} stroke-width="1.5" />
				<rect x="102" y="52" width="16" height="16" rx="4" fill="#64748b" stroke={idleStroke} stroke-width="1.5" />

				<!-- Trapecio trasero -->
				<path
					id="traps-back"
					d="M70 68 L110 58 L150 68 L138 100 L110 92 L82 100 Z"
					fill={fill('traps-back')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Hombros traseros -->
				<ellipse
					id="shoulders-back"
					cx="62"
					cy="96"
					rx="22"
					ry="16"
					fill={fill('shoulders-back')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<ellipse
					cx="158"
					cy="96"
					rx="22"
					ry="16"
					fill={fill('shoulders-back')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Romboides -->
				<path
					id="rhomboids"
					d="M96 96 L110 90 L124 96 L120 128 L110 132 L100 128 Z"
					fill={fill('rhomboids')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Redondo mayor -->
				<path
					id="teres"
					d="M72 100 L96 108 L92 140 L68 128 Z"
					fill={fill('teres')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M148 100 L124 108 L128 140 L152 128 Z"
					fill={fill('teres')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Dorsal ancho -->
				<path
					id="lats"
					d="M68 126 L98 132 L94 200 L62 178 Z"
					fill={fill('lats')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M152 126 L122 132 L126 200 L158 178 Z"
					fill={fill('lats')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Erectores -->
				<path
					id="erectors"
					d="M100 130 L110 126 L120 130 L118 214 L110 218 L102 214 Z"
					fill={fill('erectors')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Tríceps -->
				<ellipse
					id="triceps"
					cx="48"
					cy="140"
					rx="14"
					ry="28"
					fill={fill('triceps')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<ellipse
					cx="172"
					cy="140"
					rx="14"
					ry="28"
					fill={fill('triceps')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<rect x="36" y="166" width="16" height="46" rx="8" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />
				<rect x="168" y="166" width="16" height="46" rx="8" fill="#64748b" stroke={idleStroke} stroke-width="1.2" />

				<!-- Glúteos -->
				<path
					id="glutes"
					d="M74 198 L110 210 L78 258 L62 240 Z"
					fill={fill('glutes')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M110 210 L146 198 L158 240 L142 258 Z"
					fill={fill('glutes')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Isquiotibiales -->
				<path
					id="hamstrings"
					d="M70 252 L108 258 L98 348 L72 340 Z"
					fill={fill('hamstrings')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M112 258 L150 252 L148 340 L122 348 Z"
					fill={fill('hamstrings')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>

				<!-- Gemelos traseros -->
				<path
					id="calves-back"
					d="M74 342 L96 348 L90 420 L70 416 Z"
					fill={fill('calves-back')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
				<path
					d="M124 348 L146 342 L150 416 L130 420 Z"
					fill={fill('calves-back')}
					stroke={idleStroke}
					stroke-width="1.2"
				/>
			</svg>
		{/if}
	</div>

	<div class="mt-4 flex flex-wrap justify-center gap-3 text-xs text-slate-400">
		<span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-red-500"></span> Principal</span>
		<span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-yellow-500"></span> Secundario</span>
		<span class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-full bg-slate-500"></span> No trabajado</span>
	</div>
</section>
