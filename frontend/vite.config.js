import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Carga las variables de entorno inyectadas por Docker Compose / Portainer
	const env = loadEnv(mode, process.cwd(), '');

	// Construye el subdominio dinámicamente según DOMAIN_SUFFIX (_dev, _pre, o vacío)
	const suffix = env.DOMAIN_SUFFIX !== undefined ? env.DOMAIN_SUFFIX : '_dev';
	const allowedDomain = `diariodehierro${suffix}.alsdev.com`;

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