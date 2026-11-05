import React from 'react';
import {useCurrentFrame} from 'remotion';
import {COLORS, RADIUS, TYPE} from '../../../config/design';
import {mono, sans} from '../styles/fonts';
import {enter, rise} from '../styles/motion';

// ------------------------------------------------------------ tokenizer
type Tok = {t: string; c: string};
const KEYWORDS = /^(void|return|if|else|for|while|const)\b/;
const TYPES = /^(float|int|bool|char|DHT|uint8_t)\b/;
const MACROS = /^(DHT11|DHT22|DHT_PIN|DHT_TYPE)\b/;

const tokenize = (line: string): Tok[] => {
  const S = COLORS.syntax;
  const out: Tok[] = [];
  let rest = line;
  if (/^\s*#/.test(rest)) {
    const m = rest.match(/^(\s*#\w+)(.*)$/)!;
    out.push({t: m[1], c: S.preproc});
    rest = m[2];
  }
  while (rest.length) {
    let m: RegExpMatchArray | null;
    if ((m = rest.match(/^\/\/.*/))) out.push({t: m[0], c: S.comment});
    else if ((m = rest.match(/^"[^"]*"|^<[\w.]+>/))) out.push({t: m[0], c: S.string});
    else if ((m = rest.match(/^\d+(\.\d+)?/))) out.push({t: m[0], c: S.number});
    else if ((m = rest.match(KEYWORDS))) out.push({t: m[0], c: S.keyword});
    else if ((m = rest.match(TYPES))) out.push({t: m[0], c: S.type});
    else if ((m = rest.match(MACROS))) out.push({t: m[0], c: S.number});
    else if ((m = rest.match(/^[A-Za-z_]\w*(?=\()/))) out.push({t: m[0], c: S.func});
    else if ((m = rest.match(/^[A-Za-z_]\w*/))) out.push({t: m[0], c: S.plain});
    else out.push({t: (m = [rest[0]])[0], c: COLORS.textMuted});
    rest = rest.slice(m[0].length);
  }
  return out;
};

// ------------------------------------------------------------ layout
const LINE_H = TYPE.code * 1.75;
/** JetBrains Mono advance width is 0.6em, so token x-positions are exact. */
const CH = TYPE.code * 0.6;
const GUTTER = 84; // line-number column, including its right padding
const PAD_R = 34;
/** Space reserved under an annotated line from the start, so lines never shift. */
const NOTE_H = 66;
const NOTE_FONT = TYPE.small;
/** Inter at ~0.55em average advance; used only to keep labels inside the editor. */
const estimateWidth = (text: string) => text.length * NOTE_FONT * 0.55 + 4;

// ------------------------------------------------------------ component
export type EditorSegment = {
  startLine: number;
  code: string;
  annotations: {line: number; token: string; text: string}[];
};

type Props = {
  filename: string;
  segment: EditorSegment;
  /** Frame (local) the segment starts typing. */
  start: number;
  /** Characters revealed per frame. */
  speed?: number;
  width?: number;
};

/**
 * Code panel that types in the real sketch, then points at the exact tokens
 * that matter: an underline on the token, a thin stem, and a label beneath.
 */
export const CodeEditor: React.FC<Props> = ({filename, segment, start, speed = 4, width = 900}) => {
  const frame = useCurrentFrame();
  const lines = segment.code.split('\n');
  const typed = Math.max(0, Math.floor((frame - start) * speed));
  const typingEnd = start + Math.ceil(segment.code.length / speed);
  const maxX = width - PAD_R;

  let consumed = 0;
  return (
    <div style={{width, borderRadius: RADIUS.lg, background: COLORS.surface, border: `1px solid ${COLORS.stroke}`, overflow: 'hidden'}}>
      <div style={{padding: '22px 34px', borderBottom: `1px solid ${COLORS.stroke}`, fontFamily: mono, fontSize: TYPE.small, color: COLORS.textMuted}}>{filename}</div>

      <div style={{padding: '30px 0 34px'}}>
        {lines.map((line, i) => {
          const visible = Math.max(0, Math.min(line.length, typed - consumed));
          const lineStart = consumed;
          consumed += line.length + 1;
          const cursorHere = typed >= lineStart && typed < consumed && frame < typingEnd + 20;
          const blink = Math.floor(frame / 8) % 2 === 0;

          const annIndex = segment.annotations.findIndex((a) => a.line === i + 1);
          const ann = annIndex >= 0 ? segment.annotations[annIndex] : null;
          const at = typingEnd + 6 + annIndex * 12;
          const underline = enter(frame, at, 12);
          const stem = enter(frame, at + 8, 10);
          const label = enter(frame, at + 12, 16);

          let tokenX = 0;
          let tokenW = 0;
          let labelX = 0;
          if (ann) {
            const col = line.indexOf(ann.token);
            tokenX = GUTTER + Math.max(0, col) * CH;
            tokenW = ann.token.length * CH;
            const stemX = tokenX + tokenW / 2;
            labelX = Math.max(GUTTER, Math.min(stemX - 18, maxX - estimateWidth(ann.text)));
          }

          let shown = 0;
          return (
            <React.Fragment key={i}>
              <div style={{position: 'relative', display: 'flex', height: LINE_H, alignItems: 'center', fontFamily: mono, fontSize: TYPE.code, whiteSpace: 'pre'}}>
                <span style={{width: GUTTER, textAlign: 'right', paddingRight: 30, color: COLORS.textDim, fontSize: TYPE.small, flexShrink: 0}}>{segment.startLine + i}</span>
                <span>
                  {tokenize(line).map((tok, k) => {
                    const take = Math.max(0, Math.min(tok.t.length, visible - shown));
                    shown += tok.t.length;
                    return take ? (
                      <span key={k} style={{color: tok.c}}>
                        {tok.t.slice(0, take)}
                      </span>
                    ) : null;
                  })}
                  {cursorHere && blink ? <span style={{display: 'inline-block', width: 3, height: TYPE.code * 1.1, background: COLORS.accent, verticalAlign: 'middle'}} /> : null}
                </span>
                {ann ? (
                  <span
                    style={{
                      position: 'absolute',
                      left: tokenX,
                      bottom: 4,
                      width: tokenW,
                      height: 3,
                      borderRadius: 2,
                      background: COLORS.accent,
                      transform: `scaleX(${underline})`,
                      transformOrigin: 'left center',
                    }}
                  />
                ) : null}
              </div>
              {ann ? (
                <div style={{position: 'relative', height: NOTE_H}}>
                  <span
                    style={{
                      position: 'absolute',
                      left: tokenX + tokenW / 2 - 1,
                      top: 0,
                      width: 2,
                      height: 18 * stem,
                      background: COLORS.accent,
                    }}
                  />
                  <span
                    style={{
                      position: 'absolute',
                      left: labelX,
                      top: 22,
                      ...rise(label, 8),
                      fontFamily: sans,
                      fontSize: NOTE_FONT,
                      fontWeight: 600,
                      whiteSpace: 'nowrap',
                      color: COLORS.accent,
                    }}
                  >
                    {ann.text}
                  </span>
                </div>
              ) : null}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};
