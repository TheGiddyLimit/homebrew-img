import fs from "fs";
import {lsRecursiveSync} from "5etools-utils/lib/UtilFs.js";

const _TIME_TAG = "\tRun duration";
const _DIRS = [
	"img",
	"pdf",
];
const MB_BYTES = 1024 * 1024;
const _MAX_SIZE = 25 * MB_BYTES;

function main () {
	console.time(_TIME_TAG);

	const badPaths = _DIRS
		.flatMap(dirName => {
			return lsRecursiveSync(dirName)
				.filter(fname => fs.statSync(fname).size > _MAX_SIZE);
		});

	if (!badPaths.length) {
		console.timeEnd(_TIME_TAG);
		return;
	}

	console.error(`File(s) larger than ${_MAX_SIZE / MB_BYTES} MiB:\n${badPaths.map(p => `\t"${p}"`).join("\n")}`)

	console.timeEnd(_TIME_TAG);
	process.exit(1);
}

export default main();
