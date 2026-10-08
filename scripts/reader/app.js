/* Reader interface code: MIT. Course content has its own rights; see LICENSE. */
(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('reader-data').textContent);
  const repo = 'https://github.com/haloshin/amazon-seller-university-transcripts';
  const main = document.getElementById('main');
  const sidebar = document.getElementById('sidebar');
  const menu = document.getElementById('menu-toggle');
  const byId = new Map(data.courses.map(c => [c.moduleId, c]));
  const titleCounts = new Map();
  for (const c of data.courses) titleCounts.set(c.title,(titleCounts.get(c.title)||0)+1);
  const idLabel = c => titleCounts.get(c.title)>1 ? `<span>${c.moduleId.slice(0,8)}</span>` : '';
  const pageSize = 30;
  let state, english, searchTimer, fontSize = 18;
  const progress = document.createElement('div');
  progress.className = 'read-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const t = (zh, en) => english ? en : zh;
  const title = c => english ? c.title : c.navigationTitleZh;
  const topicTitle = key => data.topics[key][english ? 1 : 0];
  const chosen = (c, locale) => c.variants.find(v => v.locale === locale) || c.variants.find(v => v.locale === 'en_US');
  const initialLocale = c => chosen(c, english ? 'en_US' : 'zh_CN').locale;
  const href = values => '#' + new URLSearchParams({...values, ui: english ? 'en' : 'zh'}).toString();
  const courseHref = (c, locale) => href({view:'course', id:c.moduleId, lang:locale || initialLocale(c)});
  const langs = c => c.variants.some(v => v.locale === 'zh_CN') ? t('中文音轨 · English', 'Chinese audio · English') : t('仅英文', 'English only');
  const countTopic = key => data.courses.filter(c => c.navigationTopic === key).length;
  const highlight = (text, query) => {
    if (!query) return esc(text);
    const pos = text.toLowerCase().indexOf(query.toLowerCase());
    return pos < 0 ? esc(text) : esc(text.slice(0,pos)) + '<mark>' + esc(text.slice(pos,pos+query.length)) + '</mark>' + esc(text.slice(pos+query.length));
  };
  function replaceHash(value) {
    try { history.replaceState(null,'',value); }
    catch { location.hash = value; }
  }
  function closeMenu() { sidebar.classList.remove('is-open'); menu.setAttribute('aria-expanded','false'); }
  function shell() {
    english = state.get('ui') === 'en';
    document.documentElement.lang = english ? 'en' : 'zh-CN';
    document.getElementById('brand').href = href({});
    document.getElementById('brand-name').innerHTML = t('卖家大学<span>SHIN · 课程阅读室</span>','Seller University<span>SHIN · READING ROOM</span>');
    document.getElementById('help-link').textContent = t('使用与来源','About');
    document.getElementById('help-link').href = href({view:'about'});
    document.getElementById('ui-language').textContent = english ? '中文' : 'English';
    menu.textContent = t('目录','Topics');
    const footer = document.getElementById('footer-rights');
    footer.textContent = t('来源与使用条件','Sources and terms'); footer.href = href({view:'about'});
    document.getElementById('footer-version').textContent = 'v' + data.release.version + ' · ' + t('课程归档 ','Course archive ') + data.release.archiveDate;
    let current = state.get('topic');
    if (state.get('view') === 'course') current = byId.get(state.get('id'))?.navigationTopic;
    sidebar.innerHTML = `<p class="sidebar-label">${t('课程目录','COURSE LIBRARY')}</p><nav class="topic-nav" aria-label="${t('按主题选课','Browse by topic')}"><a href="${href({})}" ${!current && !state.get('view') ? 'aria-current="page"' : ''}><span>${t('全部课程','All courses')}</span><span>${data.courses.length}</span></a>${Object.keys(data.topics).map(key => `<a href="${href({topic:key})}" ${current===key ? 'aria-current="page"' : ''}><span>${topicTitle(key)}</span><span>${countTopic(key)}</span></a>`).join('')}</nav><div class="sidebar-bottom">${t('每一门课，沿原文阅读。','Read each course in its original sequence.')}<a href="${repo}/releases/latest">${t('下载离线阅读包 ↓','Download offline edition ↓')}</a><a href="${href({view:'about'})}">${t('使用说明与课程来源','Reading guide and sources')} ↗</a><p>${t('SHIN 整理维护<br>非 Amazon 官方项目','Compiled by SHIN<br>Unofficial project')}</p></div>`;
  }
  function courseDirectory() {
    const c = byId.get(state.get('id'));
    if (state.get('view') !== 'course' || !c) return;
    const locale = chosen(c,state.get('lang') || initialLocale(c)).locale;
    const group = data.courses.filter(item => item.navigationTopic === c.navigationTopic);
    sidebar.classList.add('course-sidebar');
    sidebar.innerHTML = `<a class="sidebar-back" href="${href({})}">${t('← 全部课程与主题','← All courses and topics')}</a><div class="sidebar-course-title">${topicTitle(c.navigationTopic)}</div><p class="sidebar-label">${t('本主题','IN THIS TOPIC')} · ${group.length} ${t('门课程','courses')}</p><nav class="course-nav" aria-label="${t('同主题课程目录','Courses in this topic')}">${group.map((item,i)=>{const v=chosen(item,locale);return `<a href="${courseHref(item,v.locale)}" ${item.moduleId===c.moduleId ? 'aria-current="page"' : ''}><span class="course-number">${String(i+1).padStart(2,'0')}</span><span>${esc(title(item))}${locale==='zh_CN' && v.locale!=='zh_CN' ? '<small>EN</small>' : ''}</span></a>`;}).join('')}</nav><div class="directory-footer"><a href="${href({topic:c.navigationTopic})}">${t('在本主题搜索 ↗','Search this topic ↗')}</a></div>`;
    const active = sidebar.querySelector('[aria-current="page"]');
    const nav = sidebar.querySelector('.course-nav');
    if (active) nav.scrollTop = Math.max(0, active.offsetTop - nav.offsetTop - 150);
  }
  function searchResults() {
    const query = (state.get('q') || '').trim().toLowerCase();
    const topic = state.get('topic');
    const language = state.get('language') || 'all';
    const rows = [];
    for (const c of data.courses) {
      if (topic && c.navigationTopic !== topic) continue;
      const variants = c.variants.filter(v => language === 'all' || v.locale === language);
      if (!variants.length) continue;
      const titleMatch = (c.title + '\n' + c.navigationTitleZh).toLowerCase().includes(query);
      const match = variants.find(v => v.text.toLowerCase().includes(query));
      if (query && !titleMatch && !match) continue;
      const preferred = chosen(c, language === 'all' ? (english ? 'en_US' : 'zh_CN') : language);
      const target = query && !titleMatch ? match : preferred;
      let snippet = '';
      if (query && match) {
        const body = match.text.replace(/^# [^\n]*\n/, '').trim();
        const at = body.toLowerCase().indexOf(query);
        if (at >= 0) {
          const start = Math.max(0,at-48), end = Math.min(body.length,at+query.length+95);
          snippet = (start ? '…' : '') + body.slice(start,end).replace(/\n/g,' ') + (end<body.length ? '…' : '');
        }
      }
      rows.push({c,target,snippet,rank:query && titleMatch ? 0 : 1});
    }
    return rows.sort((a,b) => a.rank-b.rank);
  }
  function results() {
    const rows = searchResults();
    const pages = Math.max(1,Math.ceil(rows.length/pageSize));
    const page = Math.max(1,Math.min(pages,parseInt(state.get('page'),10)||1));
    const query = (state.get('q') || '').trim();
    document.getElementById('result-count').textContent = t(`${rows.length} 门课程`,`${rows.length} courses`) + (query ? t(' · 搜索标题与全文',' · Titles and full text') : '');
    document.getElementById('results').innerHTML = !rows.length ? `<div class="empty-state"><h2>${t('没有找到对应课程','No courses found')}</h2><p class="muted">${t('试试更短的关键词，或切换语言和主题。','Try a shorter keyword, or change the topic or language filter.')}</p><a href="${href({})}">${t('返回全部课程','Back to all courses')}</a></div>` : `<ol class="catalogue-list">${rows.slice((page-1)*pageSize,page*pageSize).map(({c,target,snippet},i) => `<li class="course-row"><a href="${courseHref(c,target.locale)}"><span class="row-index">${String((page-1)*pageSize+i+1).padStart(2,'0')}</span><div><div class="course-name">${highlight(title(c),query)}</div>${!english ? `<div class="course-original">${highlight(c.title,query)}</div>` : ''}<div class="course-meta"><span>${topicTitle(c.navigationTopic)}</span><span>${langs(c)}</span><span>${Math.max(1,Math.round(target.duration/60))} ${t('分钟原课','min video')}</span>${idLabel(c)}</div>${snippet ? `<p class="snippet">${highlight(snippet,query)}</p>` : ''}</div><span class="row-arrow" aria-hidden="true">↗</span></a></li>`).join('')}</ol>${pages>1 ? `<nav class="pagination" aria-label="${t('课程分页','Course pages')}">${page>1 ? `<a href="${href({...Object.fromEntries(state),page:page-1})}">${t('← 上一页','← Previous')}</a>` : ''}<span>${page} / ${pages}</span>${page<pages ? `<a href="${href({...Object.fromEntries(state),page:page+1})}">${t('下一页 →','Next →')}</a>` : ''}</nav>` : ''}`;
  }
  function library() {
    let topic = state.get('topic');
    if (topic && !data.topics[topic]) { errorPage(); return; }
    document.title = (topic ? topicTitle(topic) : t('课程阅读室','Reading room')) + ' · Seller University · SHIN';
    const home = !topic && !state.get('q') && !state.get('language') && !state.get('page');
    const starterNames = english ? ['Get started','Meet Seller Central','Know the rules','Create a listing','Understand FBA'] : ['认识亚马逊开店','熟悉卖家平台','先读销售政策','发布第一件商品','了解 FBA 配送'];
    main.innerHTML = `${home ? `<section class="hero"><div><div class="eyebrow">AMAZON SELLER UNIVERSITY / SHIN</div><h1>${t('亚马逊卖家大学<span>课程阅读室</span>','Amazon Seller University<span>A reading room for sellers</span>')}</h1><p>${t('按主题找课，沿原文阅读。','Find a topic. Read the original transcript.')}</p></div><img src="assets/reader-banner.png" alt="${t('270 门课程，455 份转写稿，8 个主题','270 courses, 455 transcripts, 8 topics')}" width="1774" height="887"></section><div class="stats"><div class="stat"><strong>${data.release.courseCount}</strong><span>${t('门课程','courses')}</span></div><div class="stat"><strong>${data.release.transcriptCount}</strong><span>${t('份音轨转写','transcripts')}</span></div><div class="stat"><strong>${Object.keys(data.topics).length}</strong><span>${t('个学习主题','topics')}</span></div></div><section aria-labelledby="starter-title"><div class="section-head"><h2 id="starter-title">${t('入门先读这五门','Five starting points')}</h2><small>${t('按需选读','Read at your own pace')}</small></div><ol class="starter-list">${data.starters.map((id,i)=>{const c=byId.get(id);return `<li><a href="${courseHref(c)}"><span class="step">0${i+1}</span><span class="step-title">${starterNames[i]}</span><small>${t('阅读','Read')} ↗</small></a></li>`;}).join('')}</ol></section>` : `<div class="eyebrow">COURSE LIBRARY</div><h1 style="margin-top:15px">${topic ? topicTitle(topic) : t('查找课程','Find a course')}</h1><p class="muted">${t('检索课程标题与原文，找到正在处理的问题。','Search course titles and transcripts for the question at hand.')}</p>`}<section aria-labelledby="library-title"><div class="section-head"><h2 id="library-title">${t('查找你需要的课程','Find the course you need')}</h2></div><form id="search-form" class="search-form" role="search"><label class="search-field"><span aria-hidden="true">⌕</span><input id="search" type="search" aria-label="${t('搜索课程标题与全文','Search titles and transcripts')}" placeholder="${t('搜索课程或正文，如 FBA、退货…','Search courses or text, e.g. FBA…')}" value="${esc(state.get('q')||'')}" maxlength="200"></label><button type="submit">${t('搜索','Search')}</button></form><div class="filter-row"><label for="language-filter">${t('音轨语言','Audio language')}</label><select id="language-filter"><option value="all">${t('全部语言','All languages')}</option><option value="zh_CN">${t('有中文音轨','Chinese audio available')}</option><option value="en_US">English</option></select><span id="result-count" class="result-count" aria-live="polite"></span></div><div id="results"></div></section>`;
    if (home) {
      const starter = main.querySelector('[aria-labelledby="starter-title"]');
      const librarySection = main.querySelector('[aria-labelledby="library-title"]');
      librarySection.insertBefore(starter,document.getElementById('results'));
      main.querySelector('.hero > div').append(main.querySelector('.stats'));
    }
    const input = document.getElementById('search');
    const filter = document.getElementById('language-filter');
    filter.value = ['zh_CN','en_US'].includes(state.get('language')) ? state.get('language') : 'all';
    function updateSearch() {
      const q = input.value.trim();
      q ? state.set('q',q) : state.delete('q');
      filter.value === 'all' ? state.delete('language') : state.set('language',filter.value);
      state.delete('page');
      replaceHash(href(Object.fromEntries(state)));
      results();
    }
    document.getElementById('search-form').onsubmit = e => {e.preventDefault();updateSearch();};
    input.oninput = () => {clearTimeout(searchTimer);searchTimer=setTimeout(updateSearch,160);};
    filter.onchange = updateSearch;
    results();
  }
  function transcript(c, v) {
    const lines = v.text.split(/\r?\n/);
    // Suppress only the duplicate source H1 already shown as the page title.
    if (lines[0] === '# ' + c.title) lines.shift();
    return lines.filter(line => line.trim()).map(line => `<p>${esc(line)}</p>`).join('');
  }
  function course() {
    const c = byId.get(state.get('id'));
    if (!c) {errorPage(); return;}
    const requested = state.get('lang') || initialLocale(c);
    const v = chosen(c,requested);
    if (requested !== v.locale) {
      state.set('lang',v.locale);
      replaceHash(href(Object.fromEntries(state)));
    }
    const isChinese = v.locale === 'zh_CN';
    document.title = title(c) + ' · Seller University · SHIN';
    const group = data.courses.filter(item => item.navigationTopic === c.navigationTopic);
    const at = group.indexOf(c);
    const adjacent = [-1,1].map(offset => {
      const neighbor = group[at+offset];
      if (!neighbor) return '';
      const nv = chosen(neighbor,v.locale);
      return `<a href="${courseHref(neighbor,nv.locale)}"><small>${offset<0 ? t('← 同主题上一篇','← Previous in topic') : t('同主题下一篇 →','Next in topic →')}</small>${esc(title(neighbor))}${nv.locale !== v.locale ? `<small>${t('仅英文','English only')}</small>` : ''}</a>`;
    }).join('');
    const notes = v.notes.split(/\r?\n/).filter(line => line.trim() && !line.startsWith('# ')).map(line => `<p>${esc(line.replace(/^- /,''))}</p>`).join('');
    main.innerHTML = `<article class="reading-shell"><nav class="breadcrumb" aria-label="${t('位置导航','Breadcrumb')}"><a href="${href({})}">${t('课程库','Library')}</a><span>/</span><a href="${href({topic:c.navigationTopic})}">${topicTitle(c.navigationTopic)}</a></nav><header class="course-heading"><div class="eyebrow">${t('原课转写 · ','ORIGINAL TRANSCRIPT · ')}${isChinese ? t('中文音轨','CHINESE AUDIO') : 'ENGLISH'}</div><h1>${esc(title(c))}</h1>${!english ? `<div class="original-title">${esc(c.title)}</div>` : ''}<div class="course-facts"><span>${t('原课时长','Video length')} ${Math.floor(v.duration/60)}:${String(Math.floor(v.duration%60)).padStart(2,'0')}</span><span>${t('归档于','Archived')} ${data.release.archiveDate}</span><span>${t('SHIN 整理维护','Compiled by SHIN')}</span>${idLabel(c)}</div></header><div class="reading-toolbar"><nav class="language-tabs" aria-label="${t('转写稿音轨语言','Transcript audio language')}">${c.variants.map(item => `<a href="${courseHref(c,item.locale)}" ${v.locale===item.locale ? 'aria-current="page"' : ''}>${item.locale==='zh_CN' ? '中文音轨' : 'English'}</a>`).join('')}</nav><div class="type-controls"><span>${t('字号','Text size')}</span><button type="button" id="font-smaller" aria-label="${t('缩小字号','Decrease text size')}">A−</button><button type="button" id="font-larger" aria-label="${t('增大字号','Increase text size')}">A+</button></div></div>${c.variants.length===1 ? `<p class="muted" style="font-size:12px">${t('本课程仅有英文音轨转写稿。','Only the English audio transcript is available for this course.')}</p>` : ''}${notes ? `<aside class="reader-note"><strong>${t('阅读说明','Editorial notes (Chinese)')}</strong>${notes}</aside>` : ''}<div id="transcript" class="transcript" lang="${isChinese ? 'zh-CN' : 'en'}">${transcript(c,v)}</div><p class="credit-line">${t('课程来源：Amazon Seller University · SHIN 整理维护。','Source: Amazon Seller University · Compiled by SHIN.')}<br>${t('分享请保留署名与','Please retain credit and the ')}<a href="${repo}">${t('原仓库链接','source repository link')}</a> · <a href="${href({view:'about'})}">${t('使用条件','Terms of use')}</a></p><div class="course-downloads"><a href="${v.path}/transcript.txt" download>TXT ${t('全文','text')} ↓</a><a href="${v.path}/captions.vtt" download>VTT ${t('字幕','captions')} ↓</a><a href="${v.path}/transcript.md" download>Markdown ↓</a><a href="${v.source}">${t('官方学习入口','Official learning portal')} ↗</a></div><p class="source-note">${t('原视频请在官方入口按课程原标题查找，部分课程需登录 Seller Central。本包不含视频。中文稿来自中文音轨，并非逐句翻译；不同音轨的表达可能有差异。费用、政策和界面请核对当前官方页面。','Use the original course title to find the video in the official portal; some courses require Seller Central sign-in. Videos are not included. Chinese transcripts follow Chinese audio and are not line-by-line translations. Check current official pages for fees, policies and interfaces.')}</p><nav class="adjacent" aria-label="${t('继续阅读','Continue reading')}">${adjacent}</nav></article>`;
    const updateSize = () => {
      document.documentElement.style.setProperty('--reader-size',fontSize+'px');
      document.getElementById('font-smaller').disabled = fontSize<=16;
      document.getElementById('font-larger').disabled = fontSize>=24;
    };
    document.getElementById('font-smaller').onclick = () => {fontSize=Math.max(16,fontSize-2);updateSize();};
    document.getElementById('font-larger').onclick = () => {fontSize=Math.min(24,fontSize+2);updateSize();};
    updateSize();
  }
  function about() {
    document.title = t('使用与来源','About and sources') + ' · Seller University · SHIN';
    main.innerHTML = `<article class="about"><div class="eyebrow">ABOUT THIS READING ROOM</div><h1>${t('安心读，也知道从哪里来。','Read with context.<br>Keep the source in sight.')}</h1><p>${t('这里收录亚马逊卖家大学 270 门课程、455 份转写稿：英文 270 份、中文音轨稿 185 份。正文保留课程讲述顺序与案例，中文导航名与主题由 SHIN 编辑整理。','This collection contains 270 Amazon Seller University courses and 455 transcripts: 270 in English and 185 from Chinese audio. Transcripts retain the course sequence and examples. SHIN provides the topic organization and Chinese navigation labels.')}</p><h2>${t('在线读，也能离线带走','Read online or take it offline')}</h2><p>${t('下载完整 ZIP 并解压，双击根目录的 index.html，即可在浏览器中选课、搜索全文与阅读，不需要安装软件或启动服务。离线阅读无需联网；打开 GitHub、官方课程和更新链接时需要网络。请保留完整文件夹，课程下载文件和图片也在其中。','Download and extract the complete ZIP, then open index.html in your browser. Browse, search and read without an installation or a local server. Offline reading needs no network; external GitHub, official-course and update links do. Keep the entire folder together for images and downloadable course files.')}</p><a class="download-link" href="${repo}/releases/latest">${t('下载完整阅读包 ↓','Download the complete edition ↓')}</a><h2>${t('怎样找课与阅读','Finding and reading courses')}</h2><ul><li>${t('按左侧主题选课；手机上点击右上角“目录”。搜索同时覆盖课程标题和全部转写正文。','Choose a topic in the sidebar, or tap Topics on a phone. Search covers titles and all transcript text.')}</li><li>${t('顶栏中英文按钮切换界面语言；课程标题下的语言按钮切换已有音轨转写。没有中文音轨的课程仅提供英文稿。','The header language button changes the interface. Buttons below a course title switch between available audio transcripts. Courses without Chinese audio have English text only.')}</li><li>${t('用 A− / A+ 调整字号，页尾可继续阅读同主题上一篇、下一篇。','Use A− / A+ to adjust the text size; previous and next links continue within the same topic.')}</li><li>${t('每课可下载 Markdown、TXT 全文与 VTT 字幕。VTT 需配合支持外部字幕的播放器和原视频；本项目不提供视频文件。','Each course includes Markdown, TXT and VTT downloads. VTT needs a compatible external-caption player and the original video. This project does not distribute videos.')}</li></ul><h2>${t('来源与署名','Source and attribution')}</h2><p>${t('课程来源于','Courses originate from ')}<a href="https://sell.amazon.com/learn/seller-university">Amazon Seller University</a>${t('。本项目由 SHIN 独立整理维护，非 Amazon 官方发布或背书。原课入口是官方学习总入口，请按原标题查找；不是逐课直达视频链接。','. This independent collection is maintained by SHIN and is not an official Amazon publication or endorsement. The source link is the general official learning portal; find a course by its original title.')}</p><p>${t('分享请保留来源、SHIN 整理署名和','Please keep the course source, SHIN credit and the ')}<a href="${repo}">${t('原仓库链接','original repository link')}</a>${t('。课程内容权利属于 Amazon 或相应权利人，本项目没有重新授权。SHIN 的使用条件仅适用于依法享有著作权的原创编辑内容；正常 Fork、法定使用权利与 MIT 程序代码许可保留。','. Amazon course content remains with its rights holders and is not relicensed here. SHIN’s conditions apply only to copyrightable original editorial material owned by SHIN; statutory rights, normal GitHub forks and MIT code permissions remain intact.')}</p><details><summary>${t('完整来源与权利说明','Full attribution and rights notice')}</summary><pre class="notice">${esc(data.notice)}</pre><pre class="notice">${esc(data.license)}</pre></details><h2>${t('资料范围与反馈','Scope and corrections')}</h2><p>${t('课程归档日期为','Courses were archived on ')} ${data.release.archiveDate}${t('。少量课程附阅读说明，单独展示，不改写原课说法。费用、政策和界面请以当前官方信息为准。发现错字或漏句，可附课程名、语言、时间位置和依据，','; a small number include separate editorial notes. Check current official information for fees, policies and interfaces. To report a correction, include the course, language, timestamp and supporting evidence: ')}<a href="${repo}/issues/new?template=correction.yml">${t('提交纠错','submit a correction')}</a>。</p><h2>${t('接下来的更新','Planned updates')}</h2><p>${t('卖家大学 Skill、课程题库目前均在规划中，尚未发布。可 Star 收藏仓库，或通过 GitHub Watch → Custom → Releases 关注版本更新。','A Seller University Skill and course question bank are planned and have not been released. Star the repository to bookmark it, or use GitHub Watch → Custom → Releases for release notifications.')}</p></article>`;
  }
  function errorPage() {
    document.title = t('未找到课程','Course not found') + ' · Seller University';
    main.innerHTML = `<section class="empty-state"><div class="eyebrow">SELLER UNIVERSITY</div><h1>${t('这个阅读入口不存在','This reading link was not found')}</h1><p class="muted">${t('链接可能不完整，请从课程库重新选择。','The link may be incomplete. Choose a course from the library.')}</p><a href="${href({})}">${t('返回课程库','Return to the library')}</a></section>`;
  }
  function updateProgress() {
    const article = document.getElementById('transcript');
    if (!article) {progress.style.width='0';return;}
    const start = article.getBoundingClientRect().top + window.scrollY - 100;
    const length = Math.max(1,article.offsetHeight - window.innerHeight + 180);
    progress.style.width = Math.min(100,Math.max(0,(window.scrollY-start)/length*100)) + '%';
  }
  function render(focus=false) {
    clearTimeout(searchTimer);
    state = new URLSearchParams(location.hash.slice(1));
    sidebar.classList.remove('course-sidebar');
    shell();
    courseDirectory();
    const view = state.get('view');
    if (view==='course') course();
    else if(view==='about') about();
    else if(view) errorPage();
    else library();
    closeMenu();
    window.scrollTo({top:0,behavior:'instant'});
    if (focus) main.focus({preventScroll:true});
    updateProgress();
  }
  menu.onclick = () => {const open = !sidebar.classList.contains('is-open');sidebar.classList.toggle('is-open',open);menu.setAttribute('aria-expanded',String(open));if(open){const active=sidebar.querySelector('.course-nav [aria-current="page"]');const nav=sidebar.querySelector('.course-nav');if(active)nav.scrollTop=Math.max(0,active.offsetTop-nav.offsetTop-150);}};
  document.addEventListener('keydown',e => {if(e.key==='Escape'){closeMenu();menu.focus();}});
  document.addEventListener('click',e => {if(!sidebar.contains(e.target) && !menu.contains(e.target)) closeMenu();});
  document.getElementById('ui-language').onclick = () => {state.set('ui',english ? 'zh' : 'en');location.hash=state.toString();};
  document.querySelector('.skip-link').onclick = e => {e.preventDefault();main.focus();main.scrollIntoView();};
  window.addEventListener('hashchange',()=>render(true));
  window.addEventListener('scroll',updateProgress,{passive:true});
  render();
})();
