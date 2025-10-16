import fetch from "node-fetch";
import fs from "fs";

const BASE_URL = "https://icons.llama.fi";
const API_URL = "https://api.llama.fi/chains";

async function checkIcons() {
  console.log("🔍 Checking DefiLlama chain icons...\n");

  const res = await fetch(API_URL);
  const chains = await res.json();

  const missing = [];
  let checked = 0;

  for (const chain of chains) {
    const name = chain.name.toLowerCase().replace(/\s+/g, "-");
    const url = `${BASE_URL}/${name}.jpg`;

    try {
      const response = await fetch(url, { method: "HEAD" });
      checked++;
      if (response.status === 404) {
        missing.push(chain.name);
        console.log(`❌ Missing: ${chain.name}`);
      } else {
        console.log(`✅ Found: ${chain.name}`);
      }
    } catch (err) {
      console.log(`⚠️ Error: ${chain.name}`, err.message);
    }
  }

  console.log(`\n✅ Checked ${checked} chains`);
  console.log(`❌ Missing icons: ${missing.length}`);
  fs.writeFileSync("missing-icons.json", JSON.stringify(missing, null, 2));
  console.log("📁 Saved list to missing-icons.json");
}

checkIcons();