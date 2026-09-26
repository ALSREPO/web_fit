import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Carga variables del archivo .env y también del process.env de la máquina/Docker
	const env = { ...process.env, ...loadEnv(mode, process.cwd(), '') };

	// Si DOMAIN_SUFFIX está definido en Compose (ej: '_pre'), lo usa. Si no, usa '_na'.
	const hasSuffix = env.DOMAIN_SUFFIX !== undefined && env.DOMAIN_SUFFIX.trim() !== '';
	const suffix = hasSuffix ? env.DOMAIN_SUFFIX : '';	const nombre_url = env.NOMBRE_URL !== undefined ? env.NOMBRE_URL : 'diariodehierro';
	const nombre_dominio = env.NOMBRE_DOMINIO !== undefined ? env.NOMBRE_DOMINIO : 'alsdev.com';
	const allowedDomain = `${nombre_url}${suffix}.${nombre_dominio}`;

	// LOGS PARA DEPURACIÓN 
	console.log('--------------------------------------------------');
	console.log(`[Vite Config] Mode: ${mode}`);
	console.log(`[Vite Config] DOMAIN_SUFFIX detectado: "${env.DOMAIN_SUFFIX}"`);
	console.log(`[Vite Config] Domain resuelto para allowedHosts: "${allowedDomain}"`);
	console.log('--------------------------------------------------');

	return {
		plugins: [
			tailwindcss(),
			sveltekit({
				compilerOptions: {
					runes: ({ filename }) => filename.split(/[/\\]/).includes('node_modules') ? undefined : true
				}
			})
		],
		server: {
			allowedHosts: [
				allowedDomain,
				'localhost'
			]
		}
	};
});