import {existsSync} from 'node:fs';
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(16); // previews; render-final.ps1 overrides for its intermediate
Config.setConcurrency(null);

// Use an installed Chrome when present instead of downloading Chrome Headless
// Shell (the download stalls on some networks). Override with REMOTION_BROWSER.
const browserCandidates = [
  process.env.REMOTION_BROWSER,
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
].filter(Boolean) as string[];
const browser = browserCandidates.find((p) => existsSync(p));
if (browser) {
  Config.setBrowserExecutable(browser);
  Config.setChromeMode('chrome-for-testing');
}

// The firmware sketch is imported as text so the video always shows the
// real source (config/episode.ts slices it).
Config.overrideWebpackConfig((current) => ({
  ...current,
  module: {
    ...current.module,
    rules: [...(current.module?.rules ?? []), {test: /\.ino$/, type: 'asset/source'}],
  },
}));
