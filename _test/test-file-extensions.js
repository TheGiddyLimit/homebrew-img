import {lsRecursiveSync} from "5etools-utils/lib/UtilFs.js";

const _TIME_TAG = "\tRun duration";
const _ALLOWED_EXTENSIONS = {
	"font": new Set([
		"otf",
		"ttf",
		"woff",
		"woff2",
	]),
	"img": new Set([
		"gif",
		"jpeg",
		"jpg",
		"png",
		"svg",
		"webp",
	]),
	"pdf": new Set([
		"pdf",
	]),
}

function main () {
	console.time(_TIME_TAG);

	const badPaths = Object.entries(_ALLOWED_EXTENSIONS)
		.flatMap(([dirName, allowedExts]) => {
			return lsRecursiveSync(dirName)
				.filter(fname => {
					const ext = fname.split(".").at(-1).toLowerCase();
					return !allowedExts.has(ext);
				});
		});

	if (!badPaths.length) {
		console.timeEnd(_TIME_TAG);
		return;
	}

	console.error(`File extensions were not on allowlist:\n${badPaths.map(p => `\t${p}`).join("\n")}`)

	console.timeEnd(_TIME_TAG);
	process.exit(1);
}

export default main();
