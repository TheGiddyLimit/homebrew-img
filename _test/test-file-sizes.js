import fs from "fs";
import {lsRecursiveSync} from "5etools-utils/lib/UtilFs.js";
import {DIRS, TIME_TAG} from "./consts.js";

const MB_BYTES = 1024 * 1024;
const _MAX_SIZE = 25 * MB_BYTES;

function main () {
	console.time(TIME_TAG);

	const badPaths = DIRS
		.flatMap(dirName => {
			return lsRecursiveSync(dirName)
				.filter(fname => fs.statSync(fname).size > _MAX_SIZE);
		});

	if (!badPaths.length) {
		console.timeEnd(TIME_TAG);
		return;
	}

	console.error(`File(s) larger than ${_MAX_SIZE / MB_BYTES} MiB:\n${badPaths.map(p => `\t"${p}"`).join("\n")}`)

	console.timeEnd(TIME_TAG);
	process.exit(1);
}

export default main();
