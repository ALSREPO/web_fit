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
		if (role === 'Principal') return '#dc2626';
		if (role === 'Asistencial') return '#f59e0b';
		return '#475569';
	}

	function stroke(id) {
		const role = colorById[id];
		if (role === 'Principal') return '#7f1d1d';
		if (role === 'Asistencial') return '#92400e';
		return '#1e293b';
	}

	const idleStroke = '#0f172a';
	const idleStrokeWidth = '0.8';

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
			<svg viewBox="0 0 200 500" class="h-96 w-auto max-w-full" aria-label="Cuerpo vista frontal">
				<defs>
					<filter id="shadow">
						<feDropShadow dx="0.5" dy="0.5" stdDeviation="1" flood-opacity="0.3" />
					</filter>
				</defs>

				<!-- Cabeza -->
				<circle cx="100" cy="30" r="18" fill="#64748b" stroke={idleStroke} stroke-width="1" />

				<!-- Cuello -->
				<rect x="94" y="46" width="12" height="14" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />

				<!-- Trapecio -->
				<path
					id="traps-front"
					d="M 75 58 L 100 52 L 125 58 L 118 75 L 100 70 L 82 75 Z"
					fill={fill('traps-front')}
					stroke={stroke('traps-front')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Hombros/Deltoides -->
				<ellipse
					id="shoulders-front"
					cx="60"
					cy="78"
					rx="18"
					ry="22"
					fill={fill('shoulders-front')}
					stroke={stroke('shoulders-front')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>
				<ellipse
					cx="140"
					cy="78"
					rx="18"
					ry="22"
					fill={fill('shoulders-front')}
					stroke={stroke('shoulders-front')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Pectoral -->
				<path
					id="chest"
					d="M 75 80 Q 100 70 125 80 L 128 140 Q 100 135 72 140 Z"
					fill={fill('chest')}
					stroke={stroke('chest')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Pectoral Superior -->
				<path
					id="chest-upper"
					d="M 80 75 Q 100 65 120 75 L 120 95 Q 100 90 80 95 Z"
					fill={fill('chest-upper')}
					stroke={stroke('chest-upper')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Bíceps izquierdo -->
				<ellipse
					id="biceps"
					cx="46"
					cy="110"
					rx="12"
					ry="35"
					fill={fill('biceps')}
					stroke={stroke('biceps')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Bíceps derecho -->
				<ellipse
					cx="154"
					cy="110"
					rx="12"
					ry="35"
					fill={fill('biceps')}
					stroke={stroke('biceps')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Antebrazos -->
				<rect x="38" y="142" width="10" height="40" rx="5" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />
				<rect x="152" y="142" width="10" height="40" rx="5" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />

				<!-- Abdominales -->
				<path
					id="abs"
					d="M 82 138 Q 100 133 118 138 L 115 220 Q 100 225 85 220 Z"
					fill={fill('abs')}
					stroke={stroke('abs')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Oblicuos izquierdo -->
				<path
					d="M 70 160 L 85 200 L 78 240 L 62 220 Z"
					fill="#64748b"
					stroke={idleStroke}
					stroke-width="0.8"
				/>

				<!-- Oblicuos derecho -->
				<path
					d="M 130 160 L 115 200 L 122 240 L 138 220 Z"
					fill="#64748b"
					stroke={idleStroke}
					stroke-width="0.8"
				/>

				<!-- Cuádriceps izquierdo -->
				<path
					id="quads"
					d="M 72 238 Q 85 235 95 242 L 92 380 Q 80 382 65 378 Z"
					fill={fill('quads')}
					stroke={stroke('quads')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Cuádriceps derecho -->
				<path
					d="M 128 238 Q 115 235 105 242 L 108 380 Q 120 382 135 378 Z"
					fill={fill('quads')}
					stroke={stroke('quads')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Gemelos izquierdos -->
				<path
					id="calves-front"
					d="M 70 382 Q 80 385 85 388 L 82 460 Q 70 458 65 450 Z"
					fill={fill('calves-front')}
					stroke={stroke('calves-front')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Gemelos derechos -->
				<path
					d="M 130 382 Q 120 385 115 388 L 118 460 Q 130 458 135 450 Z"
					fill={fill('calves-front')}
					stroke={stroke('calves-front')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>
			</svg>
		{:else}
			<svg viewBox="0 0 200 500" class="h-96 w-auto max-w-full" aria-label="Cuerpo vista trasera">
				<defs>
					<filter id="shadow">
						<feDropShadow dx="0.5" dy="0.5" stdDeviation="1" flood-opacity="0.3" />
					</filter>
				</defs>

				<!-- Cabeza -->
				<circle cx="100" cy="30" r="18" fill="#64748b" stroke={idleStroke} stroke-width="1" />

				<!-- Cuello -->
				<rect x="94" y="46" width="12" height="14" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />

				<!-- Trapecio -->
				<path
					id="traps-back"
					d="M 70 60 L 100 50 L 130 60 L 122 80 L 100 75 L 78 80 Z"
					fill={fill('traps-back')}
					stroke={stroke('traps-back')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Hombros/Deltoides traseros -->
				<ellipse
					id="shoulders-back"
					cx="60"
					cy="82"
					rx="18"
					ry="22"
					fill={fill('shoulders-back')}
					stroke={stroke('shoulders-back')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>
				<ellipse
					cx="140"
					cy="82"
					rx="18"
					ry="22"
					fill={fill('shoulders-back')}
					stroke={stroke('shoulders-back')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Romboides -->
				<path
					id="rhomboids"
					d="M 88 82 L 100 76 L 112 82 L 110 115 L 100 120 L 90 115 Z"
					fill={fill('rhomboids')}
					stroke={stroke('rhomboids')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Redondo mayor izquierdo -->
				<path
					id="teres"
					d="M 68 90 L 88 100 L 85 130 L 62 115 Z"
					fill={fill('teres')}
					stroke={stroke('teres')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Redondo mayor derecho -->
				<path
					d="M 132 90 L 112 100 L 115 130 L 138 115 Z"
					fill={fill('teres')}
					stroke={stroke('teres')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Dorsal ancho izquierdo -->
				<path
					id="lats"
					d="M 60 120 L 88 130 L 85 200 L 58 160 Z"
					fill={fill('lats')}
					stroke={stroke('lats')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Dorsal ancho derecho -->
				<path
					d="M 140 120 L 112 130 L 115 200 L 142 160 Z"
					fill={fill('lats')}
					stroke={stroke('lats')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Erectores espinales -->
				<path
					id="erectors"
					d="M 96 115 L 104 115 L 102 220 L 98 220 Z"
					fill={fill('erectors')}
					stroke={stroke('erectors')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Tríceps izquierdo -->
				<ellipse
					id="triceps"
					cx="46"
					cy="112"
					rx="12"
					ry="35"
					fill={fill('triceps')}
					stroke={stroke('triceps')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Tríceps derecho -->
				<ellipse
					cx="154"
					cy="112"
					rx="12"
					ry="35"
					fill={fill('triceps')}
					stroke={stroke('triceps')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Antebrazos -->
				<rect x="38" y="144" width="10" height="40" rx="5" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />
				<rect x="152" y="144" width="10" height="40" rx="5" fill="#64748b" stroke={idleStroke} stroke-width="0.8" />

				<!-- Glúteos -->
				<path
					id="glutes"
					d="M 70 205 L 100 215 L 75 265 L 62 248 Z"
					fill={fill('glutes')}
					stroke={stroke('glutes')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<path
					d="M 130 205 L 100 215 L 125 265 L 138 248 Z"
					fill={fill('glutes')}
					stroke={stroke('glutes')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Isquiotibiales izquierdos -->
				<path
					id="hamstrings"
					d="M 68 262 L 100 270 L 95 380 L 65 372 Z"
					fill={fill('hamstrings')}
					stroke={stroke('hamstrings')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Isquiotibiales derechos -->
				<path
					d="M 132 262 L 100 270 L 105 380 L 135 372 Z"
					fill={fill('hamstrings')}
					stroke={stroke('hamstrings')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Gemelos traseros izquierdos -->
				<path
					id="calves-back"
					d="M 68 378 Q 80 382 85 385 L 82 460 Q 70 458 65 450 Z"
					fill={fill('calves-back')}
					stroke={stroke('calves-back')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
				/>

				<!-- Gemelos traseros derechos -->
				<path
					d="M 132 378 Q 120 382 115 385 L 118 460 Q 130 458 135 450 Z"
					fill={fill('calves-back')}
					stroke={stroke('calves-back')}
					stroke-width={idleStrokeWidth}
					filter="url(#shadow)"
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
