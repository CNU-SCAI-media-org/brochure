/* 브로셔 '의견' 패널 ↔ 노션 '브로셔 의견' DB 중계 (Google Apps Script 웹앱)
 *
 * 브라우저에서 노션 API를 직접 부를 수 없어서(토큰 노출·CORS) 이 스크립트가 중간에서 받아 넘긴다.
 *   GET  ?page=N            → 그 페이지의 의견 목록 {rows:[{text,name,ts,done}]}
 *   POST {page,name,text}   → 노션에 행 추가 {ok:true}
 *
 * 설정: 스크립트 속성에 NOTION_TOKEN(노션 내부 연동 시크릿) 하나. 배포는 feedback/README.md 참고.
 */
const DB = '531bfb4bbca3428f95df9cb3f24e722d'; // 노션 '브로셔 의견' DB

function headers() {
  return {
    Authorization: 'Bearer ' + PropertiesService.getScriptProperties().getProperty('NOTION_TOKEN'),
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json',
  };
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function notion(path, body) {
  const r = UrlFetchApp.fetch('https://api.notion.com/v1' + path, {
    method: 'post', headers: headers(), payload: JSON.stringify(body), muteHttpExceptions: true,
  });
  if (r.getResponseCode() >= 400) throw new Error('Notion ' + r.getResponseCode() + ': ' + r.getContentText().slice(0, 200));
  return JSON.parse(r.getContentText());
}

const text = (arr) => (arr || []).map((t) => t.plain_text).join('');

function doGet(e) {
  const page = Math.round(+((e && e.parameter && e.parameter.page) || 0));
  if (!(page >= 1)) return out({ error: 'page 번호가 필요합니다' });
  try {
    const d = notion('/databases/' + DB + '/query', {
      filter: { property: '페이지', number: { equals: page } },
      sorts: [{ timestamp: 'created_time', direction: 'descending' }],
      page_size: 100,
    });
    return out({ rows: d.results.map((p) => ({
      text: text(p.properties['내용'].title),
      name: text(p.properties['이름'].rich_text),
      ts: p.created_time,
      done: !!p.properties['처리'].checkbox,
    })) });
  } catch (err) { return out({ error: String(err) }); }
}

function doPost(e) {
  let d;
  try { d = JSON.parse(e.postData.contents); } catch (_) { return out({ error: '잘못된 요청' }); }
  const page = Math.round(+d.page);
  const body = String(d.text || '').trim().slice(0, 500);
  const name = String(d.name || '').trim().slice(0, 30);
  if (!(page >= 1 && page <= 500) || !body) return out({ error: '페이지 번호와 내용이 필요합니다' });
  try {
    notion('/pages', {
      parent: { database_id: DB },
      properties: {
        '내용': { title: [{ text: { content: body } }] },
        '페이지': { number: page },
        '이름': { rich_text: name ? [{ text: { content: name } }] : [] },
      },
    });
    return out({ ok: true });
  } catch (err) { return out({ error: String(err) }); }
}
