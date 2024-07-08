import fs from "fs";
import {DIRS, TIME_TAG} from "./consts.js";
import {UtilSource} from "5etools-utils";

function main () {
	console.time(TIME_TAG);

	const badPaths = DIRS
		.flatMap(dirName => {
			return fs.readdirSync(dirName)
				.filter(subDirName => !UtilSource.isValidHomebrewSorce(subDirName))
		});

	if (!badPaths.length) {
		console.timeEnd(TIME_TAG);
		return;
	}

	console.error(`Invalid homebrew source(s) found in directory name(s):\n${badPaths.map(p => `\t"${p}"`).join("\n")}`)

	console.timeEnd(TIME_TAG);
	process.exit(1);
}

export default main();
