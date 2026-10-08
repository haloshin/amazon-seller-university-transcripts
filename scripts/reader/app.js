/* Reader interface code: MIT. Course content has its own rights; see LICENSE. */
(() => {
  'use strict';
  const bundle = JSON.parse(document.getElementById('reader-data').textContent);
  let platform, data, byId, titleCounts, topicDescriptions;
  const repo = 'https://github.com/haloshin/seller-university';
  const main = document.getElementById('main');
  const sidebar = document.getElementById('sidebar');
  const menu = document.getElementById('menu-toggle');
  const idLabel = c => titleCounts.get(c.title)>1 ? `<span>${c.moduleId.slice(0,8)}</span>` : '';
  const pageSize = 30;
  const isLibrary = () => state.get('view') === 'library' || (!state.get('view') && ['topic','q','language','page'].some(key => state.has(key)));
  let state, english, searchTimer, fontSize = 16;
  const progress = document.createElement('div');
  progress.className = 'read-progress';
  progress.setAttribute('aria-hidden', 'true');
  document.body.append(progress);
  const esc = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const t = (zh, en) => english ? en : zh;
  const title = c => english ? c.title : c.navigationTitleZh;
  const topicTitle = key => data.topics[key][english ? 1 : 0];
  const isChineseText = v => v.locale.startsWith('zh_CN');
  const variantLabel = v => v.kind === 'translation' ? t('中文译文','Chinese translation') : v.locale === 'zh_CN' ? t('中文音轨','Chinese audio') : 'English';
  const chosen = (c, locale) => c.variants.find(v => v.locale === locale) || (locale.startsWith('zh_CN') && c.variants.find(isChineseText)) || c.variants.find(v => v.locale === 'en_US') || c.variants[0];
  const initialLocale = c => chosen(c, english ? 'en_US' : 'zh_CN').locale;
  const href = values => '#' + new URLSearchParams({platform, ...values, ui: english ? 'en' : 'zh'}).toString();
  const courseHref = (c, locale) => href({view:'course', id:c.moduleId, lang:locale || initialLocale(c)});
  const langs = c => c.variants.some(v => v.locale === 'zh_CN') ? t('中文音轨 · English', 'Chinese audio · English') : c.variants.some(v => v.kind === 'translation') ? t('中文译文 · English', 'Chinese translation · English') : t('仅英文', 'English only');
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
  function closeMenu() { sidebar.classList.remove('is-open'); menu.setAttribute('aria-expanded','false'); document.getElementById('menu-scrim').hidden=true; document.body.classList.remove('menu-open'); }
  function revealCurrentCourse() {
    const active = sidebar.querySelector('.course-nav [aria-current="page"]');
    const nav = sidebar.querySelector('.course-nav');
    if (active && nav.clientHeight) nav.scrollTop = Math.max(0,active.offsetTop-nav.offsetTop-150);
  }
  function shell() {
    english = state.get('ui') === 'en';
    document.documentElement.lang = english ? 'en' : 'zh-CN';
    document.getElementById('brand').href = href({});
    document.getElementById('brand-name').innerHTML = `Seller University<span>${esc(data.config.name[english?1:0])} ${t('专区 · SHIN 整理维护','COLLECTION · BY SHIN')}</span>`;
    const selector = document.getElementById('platform-select');
    selector.hidden = Object.keys(bundle.platforms).length < 2;
    selector.innerHTML = Object.entries(bundle.platforms).map(([id, collection]) => `<option value="${esc(id)}">${esc(collection.config.name[english?1:0])}</option>`).join('');
    selector.value = platform;
    selector.onchange = () => {location.hash = href({platform:selector.value});};
    document.getElementById('help-link').textContent = t('使用与来源','About');
    document.getElementById('help-link').href = href({view:'about'});
    document.getElementById('ui-language').textContent = english ? '中文' : 'English';
    const homeView = !state.get('view') && !isLibrary();
    document.body.dataset.view = homeView ? 'home' : isLibrary() ? 'library' : state.get('view');
    for (const [id, label, url, active] of [
      ['nav-home', t('首页','Home'), href({}), homeView],
      ['nav-library', t('课程库','Library'), href({view:'library'}), isLibrary() || state.get('view') === 'course']
    ]) { const link=document.getElementById(id); link.textContent=label; link.href=url; if(active)link.setAttribute('aria-current','page');else link.removeAttribute('aria-current'); }
    const hasDirectory = isLibrary() || state.get('view') === 'course';
    sidebar.hidden = !hasDirectory;
    menu.hidden = !hasDirectory;
    menu.textContent = t('目录','Topics');
    const footer = document.getElementById('footer-rights');
    footer.textContent = t('来源与使用条件','Sources and terms'); footer.href = href({view:'about'});
    document.getElementById('footer-version').textContent = 'v' + data.release.version + ' · ' + t('课程归档 ','Course archive ') + data.release.archiveDate;
    let current = state.get('topic');
    if (state.get('view') === 'course') current = byId.get(state.get('id'))?.navigationTopic;
    sidebar.innerHTML = `<p class="sidebar-label">${t('课程目录','COURSE LIBRARY')}</p><nav class="topic-nav" aria-label="${t('按主题选课','Browse by topic')}"><a href="${href({view:'library'})}" ${!current && isLibrary() ? 'aria-current="page"' : ''}><span>${t('全部课程','All courses')}</span><span>${data.courses.length}</span></a>${Object.keys(data.topics).map(key => `<a href="${href({topic:key})}" ${current===key ? 'aria-current="page"' : ''}><span>${topicTitle(key)}</span><span>${countTopic(key)}</span></a>`).join('')}</nav><div class="sidebar-bottom">${t('每一门课，沿原文阅读。','Read each course in its original sequence.')}<a href="${repo}/releases/latest">${t('下载离线阅读包 ↓','Download offline edition ↓')}</a><a href="${href({view:'about'})}">${t('使用说明与课程来源','Reading guide and sources')} ↗</a><p>${t('SHIN 整理维护<br>非官方项目','Compiled by SHIN<br>Unofficial project')}</p></div>`;
  }
  function courseDirectory() {
    const c = byId.get(state.get('id'));
    if (state.get('view') !== 'course' || !c) return;
    const locale = chosen(c,state.get('lang') || initialLocale(c)).locale;
    const group = data.courses.filter(item => item.navigationTopic === c.navigationTopic);
    sidebar.classList.add('course-sidebar');
    sidebar.innerHTML = `<a class="sidebar-back" href="${href({view:'library'})}">${t('← 全部课程与主题','← All courses and topics')}</a><div class="sidebar-course-title">${topicTitle(c.navigationTopic)}</div><p class="sidebar-label">${t('本主题','IN THIS TOPIC')} · ${group.length} ${t('门课程','courses')}</p><nav class="course-nav" aria-label="${t('同主题课程目录','Courses in this topic')}">${group.map((item,i)=>{const v=chosen(item,locale);return `<a href="${courseHref(item,v.locale)}" ${item.moduleId===c.moduleId ? 'aria-current="page"' : ''}><span class="course-number">${String(i+1).padStart(2,'0')}</span><span>${esc(title(item))}${locale.startsWith('zh_CN') && !isChineseText(v) ? '<small>EN</small>' : ''}</span></a>`;}).join('')}</nav><div class="directory-footer"><a href="${href({topic:c.navigationTopic})}">${t('在本主题搜索 ↗','Search this topic ↗')}</a></div>`;
    revealCurrentCourse();
  }
  function searchResults() {
    const query = (state.get('q') || '').trim().toLowerCase();
    const topic = state.get('topic');
    const language = state.get('language') || 'all';
    const rows = [];
    for (const c of data.courses) {
      if (topic && c.navigationTopic !== topic) continue;
      const variants = c.variants.filter(v => language === 'all' || v.locale === language || (language === 'chinese' && isChineseText(v)));
      if (!variants.length) continue;
      const titleMatch = (c.title + '\n' + c.navigationTitleZh + '\n' + variants.map(v => v.title || '').join('\n')).toLowerCase().includes(query);
      const match = variants.find(v => v.text.toLowerCase().includes(query));
      if (query && !titleMatch && !match) continue;
      const preferred = chosen(c, language === 'all' ? (english ? 'en_US' : 'zh_CN') : language === 'chinese' ? 'zh_CN' : language);
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
    document.getElementById('results').innerHTML = !rows.length ? `<div class="empty-state"><h2>${t('没有找到对应课程','No courses found')}</h2><p class="muted">${t('试试更短的关键词，或切换语言和主题。','Try a shorter keyword, or change the topic or language filter.')}</p><a href="${href({view:'library'})}">${t('返回全部课程','Back to all courses')}</a></div>` : `<ol class="catalogue-list">${rows.slice((page-1)*pageSize,page*pageSize).map(({c,target,snippet},i) => `<li class="course-row"><a href="${courseHref(c,target.locale)}"><span class="row-index">${String((page-1)*pageSize+i+1).padStart(2,'0')}</span><div><div class="course-name">${highlight(title(c),query)}</div>${!english ? `<div class="course-original">${highlight(c.title,query)}</div>` : ''}<div class="course-meta"><span>${topicTitle(c.navigationTopic)}</span><span>${langs(c)}</span><span>${Math.max(1,Math.round(target.duration/60))} ${t('分钟原课','min video')}</span>${idLabel(c)}</div>${snippet ? `<p class="snippet">${highlight(snippet,query)}</p>` : ''}</div><span class="row-arrow" aria-hidden="true">↗</span></a></li>`).join('')}</ol>${pages>1 ? `<nav class="pagination" aria-label="${t('课程分页','Course pages')}">${page>1 ? `<a href="${href({...Object.fromEntries(state),page:page-1})}">${t('← 上一页','← Previous')}</a>` : ''}<span>${page} / ${pages}</span>${page<pages ? `<a href="${href({...Object.fromEntries(state),page:page+1})}">${t('下一页 →','Next →')}</a>` : ''}</nav>` : ''}`;
  }
  function searchForm() {
    return `<form id="search-form" class="search-form" role="search"><label class="search-field"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="search" type="search" aria-label="${t('搜索课程标题与全文','Search titles and transcripts')}" placeholder="${t('搜索课程标题、术语或问题…','Search course titles, terms or questions…')}" value="${esc(state.get('q')||'')}" maxlength="200"></label><button type="submit">${t('搜索','Search')} <span aria-hidden="true">→</span></button></form>`;
  }
  function home() {
    document.title='Seller University · '+data.config.name[english?1:0]+t(' 课程阅读',' courses');
    const starterNames=data.config.starterNames[english?1:0];
    const starterDescriptions=data.config.starterDescriptions[english?1:0];
    main.innerHTML=`<div class="home-content">
      <section class="home-hero"><div class="hero-copy"><div class="eyebrow">SELLER UNIVERSITY / ${esc(data.config.name[1])}</div><h1>${esc(data.config.heroTitle[english?1:0])}<br><span>${esc(data.config.heroSubtitle[english?1:0])}</span></h1><p class="hero-description">${esc(data.config.heroDescription[english?1:0])}</p><p class="home-stats"><strong>${data.stats.courses}</strong> ${t('门课程','courses')}<span> / </span><strong>${data.stats.transcripts}</strong> ${t('份转写稿','transcripts')}<span> / </span><strong>${Object.keys(data.topics).length}</strong> ${t('个主题','topics')}</p><p class="home-language-note">${t(`${data.stats.chineseReadable} 门可中文阅读`,`${data.stats.chineseReadable} courses readable in Chinese`)} · <a href="${href({view:'library',language:'zh_CN_translation'})}">${t(`${data.stats.translations} 份中文译文`,`${data.stats.translations} Chinese translations`)} ↗</a></p>${searchForm()}<div class="hero-links"><span>${t('搜索标题与全文','Search titles and full text')}</span><a href="${href({view:'library'})}">${t('浏览全部课程','Browse all courses')} →</a></div></div><img class="hero-art" src="assets/reader-banner.png" alt="" width="1536" height="1024"></section>
      <section class="home-section start-section" aria-labelledby="starter-title"><div class="section-intro"><div class="eyebrow">01 / ${t('从这里开始','START HERE')}</div><h2 id="starter-title">${t(`第一次来，先读这 ${data.starters.length} 门。`,'A starting point for new sellers.')}</h2><p>${t('沿着推荐顺序，逐步了解这个平台。','Follow the recommended courses in order.')}</p></div><ol class="starter-list">${data.starters.map((id,i)=>`<li><a href="${courseHref(byId.get(id))}"><span class="step">0${i+1}</span><h3>${starterNames[i]}</h3><p>${starterDescriptions[i]}</p><span class="step-link">${t('阅读课程','Read course')} <span aria-hidden="true">↗</span></span></a></li>`).join('')}</ol></section>
      <section class="home-section topics-section" aria-labelledby="topics-title"><div class="section-intro"><div class="eyebrow">02 / ${t('按主题选读','EXPLORE BY TOPIC')}</div><h2 id="topics-title">${t('从你正在处理的问题出发。','Find the topic you need today.')}</h2><p>${t('入门、商品、配送与经营，按需进入对应课程。','Setup, listings, fulfillment and growth. Choose where to go next.')}</p></div><div class="topic-index">${Object.keys(data.topics).map((key,i)=>`<a href="${href({topic:key})}"><span class="topic-number">0${i+1}</span><div><h3>${topicTitle(key)}</h3><p>${topicDescriptions[key][english?1:0]}</p></div><span class="topic-count">${countTopic(key)} ${t('门','courses')} <span aria-hidden="true">↗</span></span></a>`).join('')}</div><a class="text-link" href="${href({view:'library'})}">${t(`查看全部 ${data.stats.courses} 门课程`,`Browse all ${data.stats.courses} courses`)} →</a></section>
      <section class="home-section take-section" aria-labelledby="take-title"><div><div class="eyebrow">03 / ${t('带走阅读','TAKE IT WITH YOU')}</div><h2 id="take-title">${t('在线读，也可以离线带走。','Your reading room. Online or offline.')}</h2><p>${t('下载完整资料包，解压后打开 index.html。<br>每门课程同时提供 Markdown、TXT 全文和 VTT 字幕。','Download the complete edition and open index.html.<br>Every course also includes Markdown, TXT and VTT captions.')}</p><a class="primary-link" href="${repo}/releases/latest">${t('下载完整阅读包','Download the complete edition')} ↓</a><a class="text-link" href="${href({view:'about'})}">${t('查看使用说明','Reading guide')} →</a></div><div class="download-note"><span class="note-label">${t('关于这份资料','ABOUT THE COLLECTION')}</span><p>${collectionSummary()}</p><p>${t('SHIN 整理维护，非官方项目。<br>分享请保留课程来源、整理署名与原仓库链接。','Compiled by SHIN. An unofficial project.<br>Please retain the source, editor’s credit and repository link.')}</p></div></section>
      <section class="updates-section" aria-labelledby="updates-title"><div><div class="eyebrow">${t('接下来的更新','PLANNED UPDATES')}</div><h2 id="updates-title">${t('更多平台，更多学习方式。','More platforms. More ways to learn.')}</h2><p>${plannedUpdates()}</p></div><a class="text-link" href="${repo}">${t('在 GitHub 关注','Follow on GitHub')} ↗</a></section>
    </div>`;
    document.getElementById('search-form').onsubmit=e=>{e.preventDefault();const q=document.getElementById('search').value.trim();location.hash=href({view:'library',...(q ? {q} : {})});};
  }
  function library() {
    const topic=state.get('topic');
    if(topic && !data.topics[topic]) { errorPage(); return; }
    document.title=(topic ? topicTitle(topic) : t('课程库','Course library'))+' · Seller University · SHIN';
    main.innerHTML=`<div class="library-content"><header class="library-header"><div class="eyebrow">${t('课程库','COURSE LIBRARY')}</div><h1>${topic ? topicTitle(topic) : t('找到你需要的那门课。','Find your next course.')}</h1><p>${topic ? topicDescriptions[topic][english?1:0] : t(`${data.stats.courses} 门课程，按主题浏览，或直接检索课程原文。`,`${data.stats.courses} courses. Browse by topic or search the original transcripts.`)}</p></header>${searchForm()}<div class="filter-row"><label for="language-filter">${t('阅读语言','Reading language')}</label><select id="language-filter"><option value="all">${t('全部语言','All languages')}</option><option value="chinese">${t('中文（含译文）','Chinese (including translations)')}</option><option value="zh_CN_translation">${t('中文译文','Chinese translations')}</option><option value="zh_CN">${t('有中文音轨','Chinese audio available')}</option><option value="en_US">English</option></select><span id="result-count" class="result-count" aria-live="polite"></span></div><div id="results"></div></div>`;
    const input=document.getElementById('search'),filter=document.getElementById('language-filter');
    filter.value=['zh_CN','en_US','chinese','zh_CN_translation'].includes(state.get('language')) ? state.get('language') : 'all';
    function updateSearch() {
      const q=input.value.trim();q ? state.set('q',q) : state.delete('q');
      state.set('view','library');
      filter.value==='all' ? state.delete('language') : state.set('language',filter.value);
      state.delete('page');replaceHash(href(Object.fromEntries(state)));results();
    }
    document.getElementById('search-form').onsubmit=e=>{e.preventDefault();clearTimeout(searchTimer);updateSearch();};
    input.oninput=()=>{clearTimeout(searchTimer);searchTimer=setTimeout(updateSearch,160);};
    filter.onchange=updateSearch;
    results();
  }
  function transcript(c, v) {
    // Paragraph layout is compiled separately from the unchanged source text.
    return v.paragraphs.map(paragraph => {
      const listItem = /^(?:[-*•]\s+|\d+[.)、]\s*|[一二三四五六七八九十]+[、．])/.test(paragraph);
      return `<p${listItem ? ' class="transcript-list-item"' : ''}>${esc(paragraph)}</p>`;
    }).join('');
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
    const isChinese = isChineseText(v);
    const isTranslation = v.kind === 'translation';
    const downloads = isTranslation
      ? `<a href="${v.path}/translation.txt" download>TXT ${t('译文','translation')}</a><a href="${v.path}/translation.md" download>Markdown</a>`
      : `<a href="${v.path}/transcript.txt" download>TXT ${t('全文','text')}</a><a href="${v.path}/captions.vtt" download>VTT ${t('字幕','captions')}</a><a href="${v.path}/transcript.md" download>Markdown</a>`;
    document.title = title(c) + ' · Seller University · SHIN';
    const group = data.courses.filter(item => item.navigationTopic === c.navigationTopic);
    const at = group.indexOf(c);
    const adjacent = [-1,1].map(offset => {
      const neighbor = group[at+offset];
      if (!neighbor) return '';
      const nv = chosen(neighbor,v.locale);
      return `<a href="${courseHref(neighbor,nv.locale)}"><small>${offset<0 ? t('← 同主题上一篇','← Previous in topic') : t('同主题下一篇 →','Next in topic →')}</small>${esc(title(neighbor))}${nv.locale !== v.locale ? `<small>${variantLabel(nv)}</small>` : ''}</a>`;
    }).join('');
    const notes = v.notes.split(/\r?\n/).filter(line => line.trim() && !line.startsWith('# ')).map(line => `<p>${esc(line.replace(/^- /,''))}</p>`).join('');
    main.innerHTML = `<article class="reading-shell"><nav class="breadcrumb" aria-label="${t('位置导航','Breadcrumb')}"><a href="${href({view:'library'})}">${t('课程库','Library')}</a><span>/</span><a href="${href({topic:c.navigationTopic})}">${topicTitle(c.navigationTopic)}</a></nav><header class="course-heading"><div class="eyebrow">${isTranslation ? t('中文译文 · 英文原稿翻译','CHINESE TRANSLATION · FROM ENGLISH') : t('原课转写 · ','ORIGINAL TRANSCRIPT · ') + (isChinese ? t('中文音轨','CHINESE AUDIO') : 'ENGLISH')}</div><h1>${esc(title(c))}</h1>${!english ? `<div class="original-title">${esc(c.title)}</div>` : ''}<div class="course-facts"><span>${t('原课时长','Video length')} ${Math.floor(v.duration/60)}:${String(Math.floor(v.duration%60)).padStart(2,'0')}</span><span>${t('归档于','Archived')} ${data.release.archiveDate}</span><span>${t('SHIN 整理维护','Compiled by SHIN')}</span>${idLabel(c)}</div></header><div class="reading-toolbar"><nav class="language-tabs" aria-label="${t('正文语言与来源','Text language and source')}">${c.variants.map(item => `<a href="${courseHref(c,item.locale)}" ${v.locale===item.locale ? 'aria-current="page"' : ''}>${variantLabel(item)}</a>`).join('')}</nav><div class="reading-actions"><div class="type-controls"><span>${t('字号','Text size')}</span><button type="button" id="font-smaller" aria-label="${t('缩小字号','Decrease text size')}">A−</button><button type="button" id="font-larger" aria-label="${t('增大字号','Increase text size')}">A+</button></div><details class="download-menu"><summary>${t('下载','Download')} ↓</summary><div>${downloads}</div></details></div></div>${isTranslation ? `<p class="translation-note">${t('依据英文转写稿，经 AI 辅助翻译与校对；非官方中文音轨。可切换 English 对照原文。','AI-assisted translation reviewed against the English transcript; not an official Chinese audio track. Switch to English to compare.')}</p>` : ''}${c.variants.length===1 ? `<p class="muted" style="font-size:12px">${t('本课程仅有英文音轨转写稿。','Only the English audio transcript is available for this course.')}</p>` : ''}${notes ? `<aside class="reader-note"><strong>${t('阅读说明','Editorial notes (Chinese)')}</strong>${notes}</aside>` : ''}<div id="transcript" class="transcript" lang="${isChinese ? 'zh-CN' : 'en'}">${transcript(c,v)}</div><p class="credit-line">${t(`课程来源：${esc(data.config.sourceName)} · SHIN 整理维护。`,`Source: ${esc(data.config.sourceName)} · Compiled by SHIN.`)}<br>${t('分享请保留署名与','Please retain credit and the ')}<a href="${repo}">${t('原仓库链接','source repository link')}</a> · <a href="${href({view:'about'})}">${t('使用条件','Terms of use')}</a></p><div class="course-downloads"><a href="${v.source}">${v.sourceStatus === 'archive_match' ? t('观看本课原视频','Watch this official course') : v.sourceStatus === 'current_version_changed' ? t('查看本课当前官方版本','View the current official version') : t('官方学习总入口','Official learning portal')} ↗</a></div><p class="source-note">${sourceNote(v)} ${t('本包不含视频。音轨稿和译文分别标明；费用、政策和界面请核对当前官方信息。','Videos are not included. Audio transcripts and translations are labeled separately. Check current official information for fees, policies and interfaces.')}</p><nav class="adjacent" aria-label="${t('继续阅读','Continue reading')}">${adjacent}</nav></article>`;
    const updateSize = () => {
      document.documentElement.style.setProperty('--reader-size',fontSize+'px');
      document.getElementById('font-smaller').disabled = fontSize<=14;
      document.getElementById('font-larger').disabled = fontSize>=22;
    };
    document.getElementById('font-smaller').onclick = () => {fontSize=Math.max(14,fontSize-2);updateSize();};
    document.getElementById('font-larger').onclick = () => {fontSize=Math.min(22,fontSize+2);updateSize();};
    updateSize();
  }
  function plannedUpdates() {
    const active=Object.values(bundle.platforms).map(c=>c.config.name[1]);
    const future=(bundle.plannedPlatforms || []).filter(name=>!active.includes(name));
    return (future.length ? esc(future.join(' / '))+t('，以及','; plus ') : '')+t('知识卡、题库和 Skill 均在规划中，尚未发布。通过 GitHub Releases 关注更新。','knowledge cards, quizzes and a Skill are planned, not yet released. Follow GitHub Releases for updates.');
  }
  function collectionSummary() {
    const s=data.stats;
    return t(`${s.courses} 门课程 · ${s.transcripts} 份转写稿。英文 ${s.englishAudio} 份，中文音轨 ${s.chineseAudio} 份，另附中文译文 ${s.translations} 份。`,`${s.courses} courses · ${s.transcripts} transcripts. ${s.englishAudio} English, ${s.chineseAudio} Chinese audio transcripts, plus ${s.translations} Chinese translations.`);
  }
  function sourceNote(v) {
    if(v.sourceStatus==='archive_match') return t('已核对官方课程 ID、音轨及归档版本；链接直接打开本课。官方播放器加载或登录要求可能变化。','The official course ID, audio language and archived version were matched. This link opens the course; player access requirements may change.');
    if(v.sourceStatus==='current_version_changed') return t('官方同一课程已有新版本，可能与本转写稿不同；本稿保留归档原文。','The official course has changed since this archive; the transcript retains its archived wording.');
    if(v.sourceStatus==='official_module_unavailable') return t('官方公开接口暂未找到本课（404）；此处仅提供总入口，可按原标题查找。','The official public endpoint returned 404 for this course. This is a general portal link; search by the original title.');
    return t('尚未确认对应音轨的有效逐课入口，请在官方站按原标题查找。','The matching audio link is not yet confirmed. Search the official site by the original title.');
  }
  function about() {
    document.title = t('使用与来源','About and sources') + ' · Seller University · SHIN';
    main.innerHTML = `<article class="about"><div class="eyebrow">ABOUT THIS READING ROOM</div><h1>${t('安心读，也知道从哪里来。','Read with context.<br>Keep the source in sight.')}</h1><p>${collectionSummary()} ${t('正文保留课程讲述顺序与案例，导航由 SHIN 整理。','The course sequence and examples are retained; SHIN provides editorial navigation.')}</p><h2>${t('在线读，也能离线带走','Read online or take it offline')}</h2><p>${t('下载完整 ZIP 并解压，双击根目录的 index.html，即可在浏览器中选课、搜索全文与阅读，不需要安装软件或启动服务。离线阅读无需联网；打开 GitHub、官方课程和更新链接时需要网络。请保留完整文件夹，课程下载文件和图片也在其中。','Download and extract the complete ZIP, then open index.html in your browser. Browse, search and read without an installation or a local server. Offline reading needs no network; external GitHub, official-course and update links do. Keep the entire folder together for images and downloadable course files.')}</p><a class="download-link" href="${repo}/releases/latest">${t('下载完整阅读包 ↓','Download the complete edition ↓')}</a><h2>${t('怎样找课与阅读','Finding and reading courses')}</h2><ul><li>${t('首页可搜索或沿入门路线阅读；进入课程库后，按左侧主题选课，手机上点击“目录”。搜索覆盖课程标题、全部转写正文和中文译文。','Search or follow the starter path on the home page. In the library, choose a sidebar topic or tap Topics on a phone. Search covers titles, transcripts and Chinese translations.')}</li><li>${t('顶栏按钮切换界面语言；课程标题下的按钮切换音轨转写与中文译文。','The header button changes the interface language. Course buttons switch between audio transcripts and Chinese translations.')}</li><li>${t('用 A− / A+ 调整字号，页尾可继续阅读同主题上一篇、下一篇。','Use A− / A+ to adjust the text size; previous and next links continue within the same topic.')}</li><li>${t('音轨稿可下载 Markdown、TXT 全文与 VTT 字幕；中文译文提供 Markdown 和 TXT。VTT 需配合支持外部字幕的播放器和原视频；本项目不提供视频文件。','Audio transcripts include Markdown, TXT and VTT; Chinese translations include Markdown and TXT. VTT needs a compatible external-caption player and the original video. This project does not distribute videos.')}</li></ul><h2>${t('来源与署名','Source and attribution')}</h2><p>${t('课程来源于','Courses originate from ')}<a href="${esc(data.config.officialHome)}">${esc(data.config.sourceName)}</a>${t('。本项目由 SHIN 独立整理维护，非官方发布或背书。课程页提供逐课官方入口，并区分版本匹配、已换版与未确认；链接可能随官方调整。','. This independent collection is maintained by SHIN without official endorsement. Course pages distinguish verified original versions, changed versions and unverified links. Official links may change.')}</p><p>${t('分享请保留来源、SHIN 整理署名和','Please keep the course source, SHIN credit and the ')}<a href="${repo}">${t('原仓库链接','original repository link')}</a>${t('。课程内容权利属于相应权利人，本项目没有重新授权。SHIN 的使用条件仅适用于依法享有著作权的原创编辑内容；正常 Fork、法定使用权利与 MIT 程序代码许可保留。','. Course content remains with its rights holders and is not relicensed here. SHIN’s conditions apply only to copyrightable original editorial material owned by SHIN; statutory rights, normal GitHub forks and MIT code permissions remain intact.')}</p><details><summary>${t('完整来源与权利说明','Full attribution and rights notice')}</summary><pre class="notice">${esc(data.notice)}</pre><pre class="notice">${esc(data.license)}</pre></details><h2>${t('资料范围与反馈','Scope and corrections')}</h2><p>${t('课程归档日期为','Courses were archived on ')} ${data.release.archiveDate}${t('。少量课程附阅读说明，单独展示，不改写原课说法。费用、政策和界面请以当前官方信息为准。发现错字或漏句，可附课程名、语言、时间位置和依据，','; a small number include separate editorial notes. Check current official information for fees, policies and interfaces. To report a correction, include the course, language, timestamp and supporting evidence: ')}<a href="${repo}/issues/new?template=correction.yml">${t('提交纠错','submit a correction')}</a>。</p><h2>${t('接下来的更新','Planned updates')}</h2><p>${t('当前上线：','Available today: ')}${Object.values(bundle.platforms).map(c=>esc(c.config.name[english?1:0])).join(' / ')}。${plannedUpdates()}</p></article>`;
  }
  function errorPage() {
    document.title = t('未找到课程','Course not found') + ' · Seller University';
    main.innerHTML = `<section class="empty-state"><div class="eyebrow">SELLER UNIVERSITY</div><h1>${t('这个阅读入口不存在','This reading link was not found')}</h1><p class="muted">${t('链接可能不完整，请从课程库重新选择。','The link may be incomplete. Choose a course from the library.')}</p><a href="${href({view:'library'})}">${t('返回课程库','Return to the library')}</a></section>`;
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
    platform = state.get('platform') || bundle.defaultPlatform;
    const validPlatform = Object.hasOwn(bundle.platforms, platform);
    if(!validPlatform) platform=bundle.defaultPlatform;
    data = bundle.platforms[platform];
    byId = new Map(data.courses.map(c=>[c.moduleId,c]));
    titleCounts = new Map();
    for(const c of data.courses) titleCounts.set(c.title,(titleCounts.get(c.title)||0)+1);
    topicDescriptions = data.config.topicDescriptions;
    sidebar.classList.remove('course-sidebar');
    shell();
    if(!validPlatform) { platform=bundle.defaultPlatform; errorPage(); closeMenu(); return; }
    courseDirectory();
    const view = state.get('view');
    if (view==='course') course();
    else if(view==='about') about();
    else if(isLibrary()) library();
    else if(view) errorPage();
    else home();
    closeMenu();
    window.scrollTo({top:0,behavior:'instant'});
    if (focus) main.focus({preventScroll:true});
    updateProgress();
  }
  menu.onclick = () => {const open = !sidebar.classList.contains('is-open');sidebar.classList.toggle('is-open',open);menu.setAttribute('aria-expanded',String(open));document.getElementById('menu-scrim').hidden=!open;document.body.classList.toggle('menu-open',open);if(open)revealCurrentCourse();};
  document.getElementById('menu-scrim').onclick = () => {closeMenu();menu.focus();};
  window.addEventListener('resize',()=>{if(window.innerWidth>760){closeMenu();requestAnimationFrame(revealCurrentCourse);}});
  document.addEventListener('keydown',e => {
    if(!sidebar.classList.contains('is-open')) return;
    if(e.key==='Escape'){closeMenu();menu.focus();}
    if(e.key==='Tab'){
      const items=[menu,...sidebar.querySelectorAll('a[href],button')];
      const at=items.indexOf(document.activeElement);
      if(e.shiftKey && at<=0){e.preventDefault();items.at(-1).focus();}
      else if(!e.shiftKey && (at===items.length-1 || at<0)){e.preventDefault();menu.focus();}
    }
  });
  document.addEventListener('click',e => {if(!sidebar.contains(e.target) && !menu.contains(e.target)) closeMenu();});
  document.getElementById('ui-language').onclick = () => {state.set('ui',english ? 'zh' : 'en');location.hash=state.toString();};
  document.querySelector('.skip-link').onclick = e => {e.preventDefault();main.focus();main.scrollIntoView();};
  window.addEventListener('hashchange',()=>render(true));
  window.addEventListener('scroll',updateProgress,{passive:true});
  render();
})();
