import { Glob } from "bun";
import * as path from 'path';
import { embeddedModel, questions } from "./0-constants";

const similarity = require('compute-cosine-similarity')
import ollama from "ollama";

type Embeddings = { text: string, embed: number[], file: string }[];


async function getFileNames() {
  const fileNames: string[] = []
  const glob = new Glob("embedding*.json");
  for await (const file of glob.scan(".")) {
    fileNames.push(file)
  }
  return fileNames.sort((a, b) => {
    const [la, oa] = extractAndParse(a);
    const [lb, ob] = extractAndParse(b);

    if (la !== lb) {
      return la - lb;
    }
    return oa - ob;
  })
}
function extractAndParse(filename: string): [number, number] {
  const matches = filename.match(/l(\d+)-o(\d+)/);
  if (!matches) {
    throw new Error('Filename format is incorrect');
  }
  return [parseInt(matches[1], 10), parseInt(matches[2], 10)];
}


const allFiles = await getFileNames();
const scores = {};
for await (const q of questions) {
  let success = 0;
  let fail = 0;
  const embedquestion = (await ollama.embeddings({ model: embeddedModel, prompt: q.q })).embedding;
  const bestMatches: { file: string, score: number }[] = [];
  for await (const file of allFiles) {
    const embeddings: Embeddings = await Bun.file(file).json();

    const sortedEmbeddings = embeddings.sort((a, b) => similarity(b.embed, embedquestion) - similarity(a.embed, embedquestion));
    const simscore = similarity(sortedEmbeddings[0].embed, embedquestion)
    if (sortedEmbeddings[0].file === q.a) {
      console.log(simscore);
      success++;

      // console.log(`${file}: Success (${simscore}).`)
      bestMatches.push({ file: file, score: simscore })
    } else {
      fail++;
      //console.log(`${file}: Fail (${simscore}).`)
    }
  }
  // console.log(`Success: ${success} - Fail: ${fail}`);
  // console.log(`Best 5 matches: ${bestMatches.sort((a, b) => b.score - a.score).slice(0, 5).map(m => `${m.file} - ${m.score.toFixed(3)}`).join(', ')}`)
  // console.log(`worst 5 matches: ${bestMatches.sort((a, b) => a.score - b.score).slice(0, 5).map(m => `${m.file} - ${m.score.toFixed(3)}`).join(', ')}`)
  // console.log('---')
  for (const m of bestMatches) {
    if (!scores[m.file]) {
      scores[m.file] = { success: success, fail: fail }
    } else {
      scores[m.file].success += success;
      scores[m.file].fail += fail;
    }
  }
}


console.log('---')
console.log('Best scores:')
let best_scores = Object.keys(scores).sort((a, b) => scores[b].success / (scores[b].success + scores[b].fail) - scores[a].success / (scores[a].success + scores[a].fail)).slice(0, 5);

for (const s of best_scores) {
  console.log(`${s} - ${scores[s].success / (scores[s].success + scores[s].fail)}`)
}
